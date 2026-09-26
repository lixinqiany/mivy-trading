from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from mivy_contracts.db.base import Base
from mivy_contracts.enums import CrawlTaskStatus, CrawlTaskType

type JsonValue = (
    str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
)


class CrawlTask(Base):
    """一次独立提交的抓取任务，所有抓取业务共用本表。

    type、params_version、params 描述创建时的请求，业务层应保持它们不变。
    相同幂等键只能对应相同请求；唯一约束防止重复创建，参数比较由业务层完成。
    params 的 JSON 类型注解只约束可存储的数据形状，不代替具体业务参数校验。
    后续在 API／执行端按 (type, params_version) 选择参数模型，校验后转为 JSON
    写入，读回时按原版本还原；本阶段不预设三种任务的参数字段。

    pending 记录可供发送程序扫描补发；本模型不实现补发、执行或状态转换。
    不继承 TimestampMixin：本表仅记录明确的生命周期时间，没有 updated_at。
    """

    __tablename__ = "crawl_task"
    __table_args__ = (
        UniqueConstraint("idempotency_key"),
        CheckConstraint("params_version > 0", name="params_version_positive"),
        CheckConstraint("jsonb_typeof(params) = 'object'", name="params_object"),
        CheckConstraint(
            "status != 'dispatched' OR dispatched_at IS NOT NULL",
            name="dispatched_at_required",
        ),
        CheckConstraint(
            "status NOT IN ('running', 'completed') OR started_at IS NOT NULL",
            name="started_at_required",
        ),
        CheckConstraint(
            "(status IN ('completed', 'failed')) = (finished_at IS NOT NULL)",
            name="finished_at_matches_status",
        ),
        Index("ix_crawl_task_created_at_id", "created_at", "id"),
        {"comment": "抓取任务主表；一行表示一次独立提交，统一记录派发与执行生命周期。"},
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        comment="任务主键，由调用方显式生成 UUID v7 后插入；无数据库或 ORM 生成默认值。",
    )
    idempotency_key: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        comment=(
            "提交方在首次请求前生成的 UUID v4；同一次提交重试复用，主动新建任务更换。"
            "唯一约束防止重复创建；同键不同 type、params_version 或 params 由业务层拒绝。"
            "此键不代替 Kafka 重复消息按任务 id 进行的执行去重。"
        ),
    )
    type: Mapped[CrawlTaskType] = mapped_column(
        Enum(
            CrawlTaskType,
            name="crawl_task_type",
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda members: [member.value for member in members],
            length=None,
        ),
        # 使用无长度上限的 VARCHAR，不把业务类型列表固化为数据库 CHECK。
        # 新增类型时扩展枚举和参数模型即可；ORM 仍检查当前应用支持的类型。
        comment=(
            "业务类型：security_info 标的基本信息、latest_quote 最新行情快照、"
            "daily_bar 日线行情；由应用枚举校验，数据库不固定可选值，便于新增业务。"
        ),
    )
    params_version: Mapped[int] = mapped_column(
        Integer,
        server_default=text("1"),
        comment=(
            "该任务类型的参数格式版本，正整数，初始为 1；与 type 共同确定参数校验模型。"
            "参数格式发生不兼容变化时增加版本，旧记录仍按原版本解释，不是重试次数。"
        ),
    )
    params: Mapped[dict[str, JsonValue]] = mapped_column(
        JSONB(none_as_null=True),
        comment=(
            "任务业务参数，必须为 JSON 对象，创建后不修改。具体字段随业务开发定义，"
            "后续按 type 和 params_version 用有类型的参数模型校验、生成说明并序列化。"
            "JSONB 和 ORM 类型注解不会自动验证证券范围、日期等业务规则。"
        ),
    )
    status: Mapped[CrawlTaskStatus] = mapped_column(
        Enum(
            CrawlTaskStatus,
            name="crawl_task_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda members: [member.value for member in members],
            length=10,
        ),
        server_default=CrawlTaskStatus.PENDING.value,
        comment=(
            "pending 尚未记录派发确认；dispatched 已确认发送；running 实际执行中；"
            "completed 全部成功完成；failed 已终止且失败。临时派发失败待补发时仍为 pending。"
            "更新须检查旧状态，迟到的派发确认不能覆盖 running 或终态；数据库约束不实现状态转换。"
        ),
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        comment="最近的派发或执行错误说明；可空，只保留最近一次，完整历史由日志记录。",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="本系统任务记录创建时间，数据库默认当前事务时间；不是 UUID 生成或执行开始时间。",
    )
    dispatched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment=(
            "本系统收到 Kafka 写入确认的时间，未确认时为空，不是任务开始时间。"
            "执行端可能先开始处理，故允许该时间晚于 started_at，不能据此回退任务状态。"
        ),
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment="执行端实际开始处理的时间，尚未开始时为空；派发阶段终止的任务也可为空。",
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment=(
            "任务成功或失败结束的时间，与 completed／failed 状态一起写入；非终态时为空。"
            "派发阶段最终失败也填写，此时 started_at 可以为空。"
        ),
    )
