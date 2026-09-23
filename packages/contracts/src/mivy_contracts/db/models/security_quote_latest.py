from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mivy_contracts.db.base import Base

if TYPE_CHECKING:
    from mivy_contracts.db.models.security import Security


class SecurityQuoteLatest(Base):
    __tablename__ = "security_quote_latest"
    __table_args__ = {"comment": "标的最新行情快照；每个标的最多一行。"}

    security_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("security.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
        comment="关联 security.id，同时作为快照主键。",
    )
    trading_date: Mapped[date | None] = mapped_column(
        Date, comment="行情所属交易日，由数据源或市场规则确定；无法确认时为空。"
    )
    quote_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment="数据源标注的行情更新时间；无法确认时为空，不使用抓取时间代替。",
    )
    last_price: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8), comment="最新成交价。"
    )
    prev_close: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8), comment="数据源提供的上一交易日收盘价，不表示昨结算价。"
    )
    open_price: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8), comment="所属交易日开盘价。"
    )
    high_price: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8), comment="所属交易日截至行情时间的最高价。"
    )
    low_price: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8), comment="所属交易日截至行情时间的最低价。"
    )
    price_change: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8), comment="数据源提供的涨跌额。"
    )
    price_change_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 8), comment="数据源提供的涨跌幅，1.25 表示 1.25%。"
    )
    volume: Mapped[Decimal | None] = mapped_column(
        Numeric(28, 8), comment="所属交易日累计成交量；股票按股、基金按份，不按手。"
    )
    turnover: Mapped[Decimal | None] = mapped_column(
        Numeric(28, 8),
        comment="所属交易日累计成交额，使用标的计价币种的基本单位，如人民币元。",
    )

    security: Mapped[Security] = relationship(
        back_populates="latest_quote", lazy="raise"
    )
