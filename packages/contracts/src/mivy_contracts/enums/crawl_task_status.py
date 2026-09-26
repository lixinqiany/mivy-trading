from enum import StrEnum


class CrawlTaskStatus(StrEnum):
    """任务的当前阶段；派发和执行共用一条生命周期。

    常规路径为 pending → dispatched → running → completed。
    执行端可能在派发确认落库前收到消息，因此也允许 pending → running。
    业务层更新时必须检查旧状态，不能用迟到的派发确认覆盖 running 或终态。
    本枚举只定义状态值，不实现状态推进、补发或重复消费处理。
    """

    PENDING = "pending"  # 尚未记录派发确认；可能未发送，也可能发送结果不确定。
    DISPATCHED = "dispatched"  # 已记录 Kafka 写入确认，不表示开始执行。
    RUNNING = "running"  # 执行端已实际开始处理任务。
    COMPLETED = "completed"  # 抓取、解析及约定的数据处理全部成功完成。
    FAILED = "failed"  # 任务已终止且未成功；可发生于派发或执行阶段。
