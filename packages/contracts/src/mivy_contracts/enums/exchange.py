from enum import StrEnum


class Exchange(StrEnum):
    """上市交易所，采用 ISO 10383 operating MIC。

    来源：https://www.iso20022.org/market-identifier-codes
    """

    SHANGHAI = "XSHG"  # 上海证券交易所，常用简称 SSE。
    SHENZHEN = "XSHE"  # 深圳证券交易所，常用简称 SZSE。
    BEIJING = "BJSE"  # 北京证券交易所，常用简称 BSE。
