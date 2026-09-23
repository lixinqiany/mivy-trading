from enum import StrEnum


class SecurityType(StrEnum):
    """证券业务类型，采用 FIX 代码及交易所官方简称。

    FIX：https://fiximate.fixtrading.org/en/FIX.Latest/cds167.html
    LOF：https://www.szse.cn/www/investor/knowledge/fund/lof/t20161123_538832.html
    """

    COMMON_STOCK = "CS"  # Common Stock，普通股；FIX SecurityType。
    ETF = "ETF"  # Exchange Traded Fund，交易所交易基金；FIX SecurityType。
    LOF = "LOF"  # Listed Open-ended Fund，上市开放式基金；交易所简称，非 FIX 值。
