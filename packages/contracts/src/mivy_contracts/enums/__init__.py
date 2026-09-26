"""标的分类、市场代码与抓取任务约定。"""

from mivy_contracts.enums.crawl_task_status import CrawlTaskStatus
from mivy_contracts.enums.crawl_task_type import CrawlTaskType
from mivy_contracts.enums.exchange import Exchange
from mivy_contracts.enums.listing_board import ListingBoard
from mivy_contracts.enums.security_type import SecurityType

__all__ = [
    "CrawlTaskStatus",
    "CrawlTaskType",
    "Exchange",
    "ListingBoard",
    "SecurityType",
]
