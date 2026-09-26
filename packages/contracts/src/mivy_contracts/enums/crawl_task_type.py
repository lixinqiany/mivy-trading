from enum import StrEnum


class CrawlTaskType(StrEnum):
    """抓取任务的业务类型；各类型的参数结构按 params_version 分别定义。"""

    SECURITY_INFO = "security_info"  # 标的基本信息。
    LATEST_QUOTE = "latest_quote"  # 最新行情快照。
    DAILY_BAR = "daily_bar"  # 日线行情。
