from enum import StrEnum


class ListingBoard(StrEnum):
    """上市板块，按交易所官方英文名称统一大写，不是国际标准代码。

    来源：https://english.sse.com.cn/markets/equities/overview/
    https://investor.szse.cn/English/listings/faq/index.html
    """

    MAIN = "MAIN"  # Main Board，沪深主板。
    STAR = "STAR"  # STAR Market，上交所科创板。
    CHINEXT = "CHINEXT"  # ChiNext，深交所创业板。
