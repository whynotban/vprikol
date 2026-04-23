from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class BackendMeResponse(BaseModel):
    found: bool
    id: Optional[int] = None
    access_level: int
    ref_level: int = 0
    refs_count: int = 0
    notify_platform: Optional[str]
    tg_id: Optional[int] = None
    vk_id: Optional[int] = None
    site_url: str


class NotificationSubscriptionEntry(BaseModel):
    id: int
    server_id: int
    event_type: str
    target_value: str
    created_at: datetime


class TgAuthConfirmResponse(BaseModel):
    success: bool
    redirect_uri: str
    site_url: str


class PrivacyToggleRequest(BaseModel):
    platform: Literal['vk', 'tg']
    user_id: int
    server_id: int
    nickname: str
    is_superadmin: bool = False


class DndSettings(BaseModel):
    dnd_start_hour: Optional[int] = None
    dnd_end_hour: Optional[int] = None


class MarketDealEntry(BaseModel):
    item_id: int
    item_name: str
    mod_level: int = 0

    sell_shop_id: int
    sell_nickname: Optional[str] = None
    sell_price: int
    sell_count: int

    buy_shop_id: int
    buy_nickname: Optional[str] = None
    buy_price: int
    buy_count: int

    flip_count: int
    profit: int
    discount_pct: int


class MarketDealsResponse(BaseModel):
    server_id: int
    total: int
    total_profit: int
    limit: int
    offset: int
    deals: List[MarketDealEntry]
