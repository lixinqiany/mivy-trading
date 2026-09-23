from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Enum,
    Identity,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mivy_contracts.db.base import Base
from mivy_contracts.db.shared import TimestampMixin
from mivy_contracts.enums import Exchange, ListingBoard, SecurityType

if TYPE_CHECKING:
    from mivy_contracts.db.models.security_quote_latest import SecurityQuoteLatest


class Security(TimestampMixin, Base):
    __tablename__ = "security"
    __table_args__ = (
        UniqueConstraint("exchange", "symbol"),
        CheckConstraint(
            "listing_board IS NULL OR (security_type = 'CS' AND ("
            "(listing_board = 'MAIN' AND exchange IN ('XSHG', 'XSHE')) OR "
            "(listing_board = 'STAR' AND exchange = 'XSHG') OR "
            "(listing_board = 'CHINEXT' AND exchange = 'XSHE')))",
            name="listing_board_exchange",
        ),
        {"comment": "交易标的基础信息；每行表示一个具体交易标的，不表示发行公司。"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True, comment="内部标的主键。"
    )
    symbol: Mapped[str] = mapped_column(
        Text, comment="标的代码，保留前导零，不包含供应商专有市场前缀。"
    )
    name: Mapped[str] = mapped_column(Text, comment="当前标的简称。")
    security_type: Mapped[SecurityType] = mapped_column(
        Enum(
            SecurityType,
            name="security_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda members: [member.value for member in members],
            length=3,
        ),
        comment="CS：普通股；ETF：交易所交易基金；LOF：上市开放式基金（非 FIX 值）。",
    )
    exchange: Mapped[Exchange] = mapped_column(
        Enum(
            Exchange,
            name="exchange",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda members: [member.value for member in members],
            length=4,
        ),
        comment="上市交易所 MIC：XSHG 上交所、XSHE 深交所、BJSE 北交所。",
    )
    listing_board: Mapped[ListingBoard | None] = mapped_column(
        Enum(
            ListingBoard,
            name="listing_board",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda members: [member.value for member in members],
            length=7,
        ),
        comment="MAIN 主板、STAR 科创板、CHINEXT 创业板；空值为不适用或尚未确认。",
    )
    currency: Mapped[str] = mapped_column(
        String(3), comment="ISO 4217 计价币种，如 CNY 人民币；无默认值。"
    )

    latest_quote: Mapped[SecurityQuoteLatest | None] = relationship(
        back_populates="security",
        lazy="raise",
        # add/merge 标的时连带处理快照；删除标的或解除关联时删除快照。
        cascade="save-update, merge, delete, delete-orphan",
        # 删除标的时不额外查询未加载的快照，交给数据库 ON DELETE CASCADE 清理。
        passive_deletes=True,
    )
