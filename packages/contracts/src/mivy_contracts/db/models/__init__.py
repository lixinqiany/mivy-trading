"""数据库表模型。"""

from mivy_contracts.db.models.crawl_task import CrawlTask
from mivy_contracts.db.models.security import Security
from mivy_contracts.db.models.security_quote_latest import SecurityQuoteLatest

__all__ = ["CrawlTask", "Security", "SecurityQuoteLatest"]
