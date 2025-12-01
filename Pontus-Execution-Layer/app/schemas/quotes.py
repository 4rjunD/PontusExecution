from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime


class FXQuote(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    provider: str
    timestamp: datetime


class CryptoQuote(BaseModel):
    from_asset: str
    to_asset: str
    from_network: Optional[str]
    to_network: Optional[str]
    rate: float
    provider: str
    timestamp: datetime


class GasQuote(BaseModel):
    network: str
    gas_price_gwei: float
    provider: str
    timestamp: datetime


class QuoteResponse(BaseModel):
    quotes: List[Union[FXQuote, CryptoQuote, GasQuote]]
    count: int

