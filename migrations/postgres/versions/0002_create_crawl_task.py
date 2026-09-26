"""create crawl task

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-26 01:53:12.268853

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "crawl_task",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
            comment="任务主键，由调用方显式生成 UUID v7 后插入；无数据库或 ORM 生成默认值。",
        ),
        sa.Column(
            "idempotency_key",
            sa.Uuid(),
            nullable=False,
            comment="提交方在首次请求前生成的 UUID v4；同一次提交重试复用，主动新建任务更换。唯一约束防止重复创建；同键不同 type、params_version 或 params 由业务层拒绝。此键不代替 Kafka 重复消息按任务 id 进行的执行去重。",
        ),
        sa.Column(
            "type",
            sa.String(),
            nullable=False,
            comment="业务类型：security_info 标的基本信息、latest_quote 最新行情快照、daily_bar 日线行情；由应用枚举校验，数据库不固定可选值，便于新增业务。",
        ),
        sa.Column(
            "params_version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
            comment="该任务类型的参数格式版本，正整数，初始为 1；与 type 共同确定参数校验模型。参数格式发生不兼容变化时增加版本，旧记录仍按原版本解释，不是重试次数。",
        ),
        sa.Column(
            "params",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
            comment="任务业务参数，必须为 JSON 对象，创建后不修改。具体字段随业务开发定义，后续按 type 和 params_version 用有类型的参数模型校验、生成说明并序列化。JSONB 和 ORM 类型注解不会自动验证证券范围、日期等业务规则。",
        ),
        sa.Column(
            "status",
            sa.String(length=10),
            server_default="pending",
            nullable=False,
            comment="pending 尚未记录派发确认；dispatched 已确认发送；running 实际执行中；completed 全部成功完成；failed 已终止且失败。临时派发失败待补发时仍为 pending。更新须检查旧状态，迟到的派发确认不能覆盖 running 或终态；数据库约束不实现状态转换。",
        ),
        sa.Column(
            "last_error",
            sa.Text(),
            nullable=True,
            comment="最近的派发或执行错误说明；可空，只保留最近一次，完整历史由日志记录。",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="本系统任务记录创建时间，数据库默认当前事务时间；不是 UUID 生成或执行开始时间。",
        ),
        sa.Column(
            "dispatched_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="本系统收到 Kafka 写入确认的时间，未确认时为空，不是任务开始时间。执行端可能先开始处理，故允许该时间晚于 started_at，不能据此回退任务状态。",
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="执行端实际开始处理的时间，尚未开始时为空；派发阶段终止的任务也可为空。",
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="任务成功或失败结束的时间，与 completed／failed 状态一起写入；非终态时为空。派发阶段最终失败也填写，此时 started_at 可以为空。",
        ),
        sa.CheckConstraint(
            "(status IN ('completed', 'failed')) = (finished_at IS NOT NULL)",
            name=op.f("ck_crawl_task_finished_at_matches_status"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(params) = 'object'", name=op.f("ck_crawl_task_params_object")
        ),
        sa.CheckConstraint(
            "status != 'dispatched' OR dispatched_at IS NOT NULL",
            name=op.f("ck_crawl_task_dispatched_at_required"),
        ),
        sa.CheckConstraint(
            "status NOT IN ('running', 'completed') OR started_at IS NOT NULL",
            name=op.f("ck_crawl_task_started_at_required"),
        ),
        sa.CheckConstraint(
            "params_version > 0", name=op.f("ck_crawl_task_params_version_positive")
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'dispatched', 'running', 'completed', 'failed')",
            name=op.f("ck_crawl_task_crawl_task_status"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_crawl_task")),
        sa.UniqueConstraint(
            "idempotency_key", name=op.f("uq_crawl_task_idempotency_key")
        ),
        comment="抓取任务主表；一行表示一次独立提交，统一记录派发与执行生命周期。",
    )
    op.create_index(
        "ix_crawl_task_created_at_id", "crawl_task", ["created_at", "id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_crawl_task_created_at_id", table_name="crawl_task")
    op.drop_table("crawl_task")
