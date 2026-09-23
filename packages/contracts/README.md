# Mivy Contracts

`mivy_contracts.enums` 导出 `SecurityType`、`Exchange`、`ListingBoard`；
`mivy_contracts.db` 导出 `Base`、`Security`、`SecurityQuoteLatest`，导入后 metadata 已注册模型。
导入不加载配置或连接数据库。数据库结构通过 Alembic 管理。

`db/base.py` 管理 metadata 和约束命名，`db/models` 放具体表模型，
`db/shared` 放共享映射定义。`Security` 继承 `TimestampMixin` 复用时间字段；
Mixin 本身不建表，其他模型可以按需使用。

## 标的基础表

`security` 每行表示一个具体交易标的，不表示发行公司。

| 字段 | 数据库类型 | 含义 |
|---|---|---|
| `id` | BIGINT IDENTITY | 内部主键，自动生成 |
| `symbol` | TEXT | 代码，保留前导零，不带供应商专有前缀 |
| `name` | TEXT | 当前简称 |
| `security_type` | VARCHAR(3) | CS 普通股、ETF 交易所交易基金、LOF 上市开放式基金 |
| `exchange` | VARCHAR(4) | XSHG 上交所、XSHE 深交所、BJSE 北交所 |
| `listing_board` | VARCHAR(7)，可空 | MAIN 主板、STAR 科创板、CHINEXT 创业板 |
| `currency` | VARCHAR(3) | ISO 4217 计价币种，如 CNY 人民币，无默认值 |
| `created_at` | TIMESTAMPTZ | 本系统记录创建时间，默认数据库当前时间 |
| `updated_at` | TIMESTAMPTZ | 本系统记录最后写入时间，默认数据库当前时间 |

除 `listing_board` 外均不允许 NULL；`(exchange, symbol)` 唯一。
普通股板块可暂缺；非空板块必须与沪深交易所匹配，ETF、LOF 和北交所板块为空。
数据库不检查代码、名称是否为空字符串，也不检查币种格式；币种最多三个字符。

## 最新行情快照

`security_quote_latest` 每个标的最多一行，后续采集覆盖最新快照，不保存历史。
日线数据独立管理，不要求先下载日线才能展示快照。

| 字段 | 数据库类型 | 含义 |
|---|---|---|
| `security_id` | BIGINT | 主键兼外键，关联 `security.id`，不自动生成 |
| `trading_date` | DATE | 行情所属交易日，如 `2026-09-23` |
| `quote_at` | TIMESTAMPTZ | 数据源标注的行情更新时间，不是抓取时间 |
| `last_price` | NUMERIC(24,8) | 最新成交价 |
| `prev_close` | NUMERIC(24,8) | 数据源提供的昨收价，不表示昨结算价 |
| `open_price` | NUMERIC(24,8) | 所属交易日开盘价 |
| `high_price` / `low_price` | NUMERIC(24,8) | 所属交易日截至行情时间的最高／最低价 |
| `price_change` | NUMERIC(24,8) | 数据源提供的涨跌额 |
| `price_change_pct` | NUMERIC(18,8) | 数据源提供的涨跌幅，1.25 表示 1.25% |
| `volume` | NUMERIC(28,8) | 所属交易日累计成交量，股票按股、基金按份 |
| `turnover` | NUMERIC(28,8) | 所属交易日累计成交额，按计价币种基本单位，如人民币元 |

数值映射为 Python `Decimal`；以上精度是本项目的存储选择。
除 `security_id` 外均允许 NULL，无默认值；未知值不填零，没有有效行情时不创建占位行。
无 `source`、`received_at`、`created_at`、`updated_at`，不使用 `TimestampMixin`。
没有快照的标的可通过 LEFT JOIN 展示；删除标的时外键 `ON DELETE CASCADE` 一并删除快照，
单独删除快照时保留标的。

ORM 双向关联为 `Security.latest_quote`（可为空）和 `SecurityQuoteLatest.security`。
两侧使用 `lazy="raise"`，查询时通过 `joinedload` 或 `selectinload` 显式加载，
避免属性访问隐式查库。关联加载需使用 ORM Session，当前 SDK 仍提供原生 Connection。
`Security.latest_quote` 使用 `save-update, merge, delete, delete-orphan` 级联，
删除标的或设置 `latest_quote = None` 时删除快照；反向关联不配置删除级联。
`passive_deletes=True` 将未加载快照的删除交给数据库，原生 SQL 删除同样生效。
更新快照时修改已有对象的字段，或使用 upsert。

交易日优先使用源字段；当前 A 股、ETF、LOF 可从已确认属于该行情的北京时间取日期。
只有时分秒时不能拼接抓取当天；不能确认交易日或完整时间时留空或补查。
未来期货需按交易所日历和交易时段确定交易日，不直接取自然日或简单加一天。
这些规则在后续采集适配层实现，模型不推算日期；TIMESTAMPTZ 保存时间点，按会话时区显示。

后续写入需把同一份快照整体更新，避免将新旧字段拼接；已确认更旧的行情不覆盖当前快照。
数据源的手／股／份、元／万元等单位也在适配层转换，本阶段只交付表结构。

## 代码来源

- CS、ETF 使用 [FIX SecurityType](https://fiximate.fixtrading.org/en/FIX.Latest/cds167.html)。
- LOF 使用[深交所官方简称](https://www.szse.cn/www/investor/knowledge/fund/lof/t20161123_538832.html)，不是 FIX 标准枚举。
- 交易所使用 [ISO 10383 operating MIC](https://www.iso20022.org/market-identifier-codes)。
- 板块采用交易所官方名称的统一大写写法，不是国际标准代码；名称来源见枚举注释。

Python 使用语义明确的成员名，如 `Exchange.SHANGHAI`、`SecurityType.COMMON_STOCK`；
数据库存储其值 `XSHG`、`CS`，通过 VARCHAR + CHECK 约束，不创建原生 ENUM。

## 写入约定

`Security` 模型 UPDATE 通过 `onupdate=func.now()` 更新 `updated_at`。
直接 SQL、`ON CONFLICT DO UPDATE` 等路径需显式设置该字段，没有数据库更新触发器。
时间戳不表示上市日期、行情时间或数据源业务生效时间。

目前仅支持 A 股普通股和沪深 ETF、LOF；未包含上市状态、上市／退市日期。
后续接入期货时增加类型和一对一合约扩展表，业务关联继续引用 `security.id`。
