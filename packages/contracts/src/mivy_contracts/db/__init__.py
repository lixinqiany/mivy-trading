"""PostgreSQL 模型；导入后 Base.metadata 已注册所有表。"""

from mivy_contracts.db.base import Base
from mivy_contracts.db.models import CrawlTask, Security, SecurityQuoteLatest

__all__ = ["Base", "CrawlTask", "Security", "SecurityQuoteLatest"]
