from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class BackendMeResponse(BaseModel):
    found: bool
    id: Optional[int] = None
    access_level: int
    refs_count: int = 0
    notify_platform: Optional[str]
    tg_id: Optional[int] = None
    vk_id: Optional[int] = None
    site_url: str
    subscription_expires: Optional[datetime] = None
    notify_extra_slots: int = 0
    forum_extra_slots: int = 0


class NotificationSubscriptionEntry(BaseModel):
    id: int
    server_id: int
    event_type: str
    target_value: str
    created_at: datetime


class MarketAlertSetItemEntry(BaseModel):
    id: int
    item_id: int
    item_name: str = ""
    mod_level: Optional[int] = None
    max_sell_price: Optional[int] = None
    min_profit: Optional[int] = None
    min_price_gap: Optional[int] = None
    min_margin_pct: Optional[int] = None
    note: Optional[str] = None
    enabled: bool
    created_at: datetime
    updated_at: datetime


class MarketAlertSetEntry(BaseModel):
    id: int
    subscription_id: int
    server_id: int
    name: str
    is_active: bool
    include_modded: bool
    allow_vc_routes: bool
    min_profit: int
    min_price_gap: int
    min_margin_pct: int
    items_count: int
    items: List[MarketAlertSetItemEntry] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class MarketAlertSubscriptionEntry(BaseModel):
    subscription_id: int
    server_id: int
    sets_count: int
    items_count: int
    sets: List[MarketAlertSetEntry]


class BroadcastAudienceResponse(BaseModel):
    user_ids: List[int]


class PromoActivationResponse(BaseModel):
    code: str
    reward_type: str
    reward_value: int
    duration_seconds: int
    expires_at: datetime
    description: str
    activation_id: int


class PromoCodeEntry(BaseModel):
    id: int
    code: str
    title: Optional[str] = None
    reward_type: str
    reward_value: int
    duration_seconds: int
    max_activations: Optional[int] = None
    per_user_limit: int
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    allowed_platforms: List[str] = Field(default_factory=list)
    allowed_user_ids: List[int] = Field(default_factory=list)
    require_site_account: bool
    is_active: bool


class TelegramStarsPaymentResponse(BaseModel):
    payment_id: str
    amount: int
    months: int
    description: str


class TelegramStarsConfirmResponse(BaseModel):
    paid: bool


class TelegramStarsPreCheckoutResponse(BaseModel):
    ok: bool
    error_message: Optional[str] = None


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


class ForumThreadEntry(BaseModel):
    id: int
    thread_name: Optional[str] = None
    thread_path: Optional[str] = None
    nickname: Optional[str] = None
    created_at: datetime


class AddForumThreadRequest(BaseModel):
    platform: Literal['tg', 'vk']
    platform_user_id: int
    subscription_platform_user_id: Optional[int] = None
    raw_input: str
