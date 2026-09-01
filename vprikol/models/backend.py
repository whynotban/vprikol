from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SlotPackPeriod(BaseModel):
    tariff_id: int
    months: int
    amount: int
    stars_amount: int
    monthly_amount: int
    monthly_per_slot: int


class SlotPackOffer(BaseModel):
    pack_id: int
    slots: int
    title: str
    periods: List[SlotPackPeriod]


class NotifySlotPackEntry(BaseModel):
    id: int
    slots: int
    months: int
    expires_at: datetime


class NotifySlotsState(BaseModel):
    base: int
    bonus: int
    purchased: int
    total: int
    used: int
    free: int
    subscription_active: bool
    subscription_expires: Optional[datetime] = None
    packs: List[NotifySlotPackEntry] = []
    offers: List[SlotPackOffer] = []


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
    ds_id: Optional[int] = None
    notify_slots: Optional[NotifySlotsState] = None


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
    raw_amount: Optional[int] = None
    months: int
    tariff_discount_percent: int = 0
    referral_discount_percent: int = 0
    promo_code: Optional[str] = None
    promo_title: Optional[str] = None
    promo_discount_percent: int = 0
    total_discount_percent: int = 0
    description: str
    product: str = "subscription"
    slots: Optional[int] = None


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
    platform: Literal['vk', 'tg', 'ds']
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
    platform: Literal['tg', 'vk', 'ds']
    platform_user_id: int
    subscription_platform_user_id: Optional[int] = None
    raw_input: str


class AnalyticsEventEntry(BaseModel):
    feature: str
    action: Literal['use', 'view', 'paywall', 'checkout', 'paid', 'signup', 'error'] = 'use'
    executor_id: Optional[int] = None
    server_id: Optional[int] = None
    has_subscription: bool = False
    occurred_at: Optional[datetime] = None
    details: dict = {}
