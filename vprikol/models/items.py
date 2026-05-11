import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MarketHistoryPoint(BaseModel):
    date: datetime.date
    price: int
    count: int


class MarketItemStats(BaseModel):
    min_price: int
    max_price: int
    total_count: int
    listings_count: int
    avg_sell_price: Optional[int] = None
    avg_buy_price: Optional[int] = None


class ItemEntry(BaseModel):
    item_id: int
    name: str
    icon: str
    acs_slot: Optional[int]
    type: int
    active: int
    skin_id: Optional[int]
    updated_at: datetime.datetime
    market_stats: Optional[MarketItemStats] = None


class ItemsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ItemEntry]


class ItemHistoryEntry(BaseModel):
    item_id: int
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime.datetime


class ItemsHistoryResponse(BaseModel):
    total: int
    changes: List[ItemHistoryEntry]


class ShopItem(BaseModel):
    item_id: int
    name: str
    price: int
    count: int
    mod_level: int
    icon: Optional[str] = None
    acs_slot: Optional[int] = None
    item_type: Optional[int] = None


class ShopEntry(BaseModel):
    server_id: int
    server_label: str
    shop_id: int
    nickname: str
    updated_at: datetime.datetime
    items_sell: List[ShopItem]
    items_buy: List[ShopItem]


class ShopsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    shops: List[ShopEntry]


class ItemMarketStatsResponse(BaseModel):
    item_id: int
    name: str
    history_sell: List[MarketHistoryPoint]
    history_buy: List[MarketHistoryPoint]
    shops: List[ShopEntry]
    min_sell_price: Optional[int]
    max_buy_price: Optional[int]


class MarketDealRoute(BaseModel):
    type: str
    label: str
    buy_server_id: int
    buy_server_label: Optional[str] = None
    sell_server_id: int
    sell_server_label: Optional[str] = None
    exchange_server_id: Optional[int] = None
    vc_rate: Optional[int] = None
    vc_bank_rate: Optional[int] = None


class MarketDealOrder(BaseModel):
    shop_id: Optional[int] = None
    nickname: Optional[str] = None
    shop_updated_at: Optional[datetime.datetime] = None
    price: int
    count: int
    server_id: int
    server_label: Optional[str] = None


class MarketDealEntry(BaseModel):
    item_id: int
    item_name: str
    mod_level: int = 0

    sell_shop_id: int
    sell_nickname: Optional[str] = None
    sell_shop_updated_at: Optional[datetime.datetime] = None
    sell_price: int
    sell_count: int

    buy_shop_id: int
    buy_nickname: Optional[str] = None
    buy_shop_updated_at: Optional[datetime.datetime] = None
    buy_price: int
    buy_count: int

    flip_count: int
    profit: int
    net_profit: Optional[int] = None
    bank_net_profit: Optional[int] = None
    discount_pct: int
    sell_orders: List[MarketDealOrder] = Field(default_factory=list)
    buy_orders: List[MarketDealOrder] = Field(default_factory=list)
    route: Optional[MarketDealRoute] = None


class MarketDealsResponse(BaseModel):
    server_id: int
    total: int
    total_profit: int
    limit: int
    offset: int
    deals: List[MarketDealEntry]
