"""create security tables

Revision ID: 0001
Revises:
Create Date: 2026-09-22 17:27:30.031004

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "security",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            nullable=False,
            comment="内部标的主键。",
        ),
        sa.Column(
            "symbol",
            sa.Text(),
            nullable=False,
            comment="标的代码，保留前导零，不包含供应商专有市场前缀。",
        ),
        sa.Column("name", sa.Text(), nullable=False, comment="当前标的简称。"),
        sa.Column(
            "security_type",
            sa.String(length=3),
            nullable=False,
            comment="CS：普通股；ETF：交易所交易基金；LOF：上市开放式基金（非 FIX 值）。",
        ),
        sa.Column(
            "exchange",
            sa.String(length=4),
            nullable=False,
            comment="上市交易所 MIC：XSHG 上交所、XSHE 深交所、BJSE 北交所。",
        ),
        sa.Column(
            "listing_board",
            sa.String(length=7),
            nullable=True,
            comment="MAIN 主板、STAR 科创板、CHINEXT 创业板；空值为不适用或尚未确认。",
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            comment="ISO 4217 计价币种，如 CNY 人民币；无默认值。",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="本系统记录创建时间。",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="本系统记录最后写入时间；直接 SQL 和 upsert 需显式维护。",
        ),
        sa.CheckConstraint(
            "security_type IN ('CS', 'ETF', 'LOF')",
            name=op.f("ck_security_security_type"),
        ),
        sa.CheckConstraint(
            "exchange IN ('XSHG', 'XSHE', 'BJSE')", name=op.f("ck_security_exchange")
        ),
        sa.CheckConstraint(
            "listing_board IN ('MAIN', 'STAR', 'CHINEXT')",
            name=op.f("ck_security_listing_board"),
        ),
        sa.CheckConstraint(
            "listing_board IS NULL OR (security_type = 'CS' AND ((listing_board = 'MAIN' AND exchange IN ('XSHG', 'XSHE')) OR (listing_board = 'STAR' AND exchange = 'XSHG') OR (listing_board = 'CHINEXT' AND exchange = 'XSHE')))",
            name=op.f("ck_security_listing_board_exchange"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_security")),
        sa.UniqueConstraint(
            "exchange", "symbol", name=op.f("uq_security_exchange_symbol")
        ),
        comment="交易标的基础信息；每行表示一个具体交易标的，不表示发行公司。",
    )
    op.create_table(
        "security_quote_latest",
        sa.Column(
            "security_id",
            sa.BigInteger(),
            autoincrement=False,
            nullable=False,
            comment="关联 security.id，同时作为快照主键。",
        ),
        sa.Column(
            "trading_date",
            sa.Date(),
            nullable=True,
            comment="行情所属交易日，由数据源或市场规则确定；无法确认时为空。",
        ),
        sa.Column(
            "quote_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="数据源标注的行情更新时间；无法确认时为空，不使用抓取时间代替。",
        ),
        sa.Column(
            "last_price",
            sa.Numeric(precision=24, scale=8),
            nullable=True,
            comment="最新成交价。",
        ),
        sa.Column(
            "prev_close",
            sa.Numeric(precision=24, scale=8),
            nullable=True,
            comment="数据源提供的上一交易日收盘价，不表示昨结算价。",
        ),
        sa.Column(
            "open_price",
            sa.Numeric(precision=24, scale=8),
            nullable=True,
            comment="所属交易日开盘价。",
        ),
        sa.Column(
            "high_price",
            sa.Numeric(precision=24, scale=8),
            nullable=True,
            comment="所属交易日截至行情时间的最高价。",
        ),
        sa.Column(
            "low_price",
            sa.Numeric(precision=24, scale=8),
            nullable=True,
            comment="所属交易日截至行情时间的最低价。",
        ),
        sa.Column(
            "price_change",
            sa.Numeric(precision=24, scale=8),
            nullable=True,
            comment="数据源提供的涨跌额。",
        ),
        sa.Column(
            "price_change_pct",
            sa.Numeric(precision=18, scale=8),
            nullable=True,
            comment="数据源提供的涨跌幅，1.25 表示 1.25%。",
        ),
        sa.Column(
            "volume",
            sa.Numeric(precision=28, scale=8),
            nullable=True,
            comment="所属交易日累计成交量；股票按股、基金按份，不按手。",
        ),
        sa.Column(
            "turnover",
            sa.Numeric(precision=28, scale=8),
            nullable=True,
            comment="所属交易日累计成交额，使用标的计价币种的基本单位，如人民币元。",
        ),
        sa.ForeignKeyConstraint(
            ["security_id"],
            ["security.id"],
            name=op.f("fk_security_quote_latest_security_id_security"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("security_id", name=op.f("pk_security_quote_latest")),
        comment="标的最新行情快照；每个标的最多一行。",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("security_quote_latest")
    op.drop_table("security")
