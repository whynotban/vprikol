import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

MarketplaceSource = Literal["external", "user"]
MarketplaceObjectType = Literal["item", "vehicle", "house", "business", "sim_card", "guard", "service", "other"]
MarketplaceDealType = Literal["sell", "buy", "rent_out", "rent_in", "exchange", "service_offer", "service_search"]
MarketplacePromotionTargetType = Literal["external", "user"]
MarketplacePromotionKind = Literal["free_subscriber", "paid", "manual"]
MarketplaceRarity = Literal["common", "rare", "unique", "legendary"]
MarketplaceRentDurationUnit = Literal["hours", "days"]


class MarketplaceAuthorContext(BaseModel):
    platform: Literal["site", "tg", "vk", "ds"]
    platform_user_id: int
    site_user_id: Optional[int] = None
    display_name: str = ""
    is_subscriber: bool = False
    access_level: int = 0


class MarketplaceAuthorRequest(BaseModel):
    author: MarketplaceAuthorContext


class MarketplaceContactInput(BaseModel):
    telegram: Optional[str] = None
    vk: Optional[str] = None
    game_phone: Optional[str] = None
    game_phone_nickname: Optional[str] = None
    site_enabled: bool = False


class MarketplaceContact(BaseModel):
    telegram: Optional[str] = None
    telegram_url: Optional[str] = None
    vk: Optional[str] = None
    vk_url: Optional[str] = None
    game_phone: Optional[str] = None
    game_phone_nickname: Optional[str] = None
    game_phone_checked_at: Optional[datetime.datetime] = None
    site_enabled: bool = False


class MarketplaceUserItemInput(BaseModel):
    item_id: Optional[int] = None
    title: Optional[str] = None
    quantity: int = 1
    enchanted: int = 0
    color_id: int = 0
    quality: int = 0


class MarketplaceListingDetails(BaseModel):
    rarity: Optional[MarketplaceRarity] = None
    legendary_quality: Optional[int] = None
    tuning: Optional[str] = None
    plate_number: Optional[str] = None
    mileage: Optional[int] = None
    weekly_finance: Optional[int] = None
    patch: Optional[str] = None
    sim_number: Optional[str] = None
    guard_buffs: list[str] = Field(default_factory=list)
    rent_duration_value: Optional[int] = None
    rent_duration_unit: Optional[MarketplaceRentDurationUnit] = None
    garage_places: Optional[int] = None
    has_ventilated_basement: Optional[bool] = None
    has_basement: Optional[bool] = None


class MarketplaceUserListingCreateRequest(BaseModel):
    author: MarketplaceAuthorContext
    server_id: int
    object_type: MarketplaceObjectType = "item"
    deal_type: MarketplaceDealType = "sell"
    title: str
    description: str = ""
    price: Optional[int] = None
    price_is_negotiable: bool = False
    category_id: Optional[int] = None
    placement_days: int = 14
    contacts: MarketplaceContactInput = Field(default_factory=MarketplaceContactInput)
    items: list[MarketplaceUserItemInput] = Field(default_factory=list, max_length=12)
    details: MarketplaceListingDetails = Field(default_factory=MarketplaceListingDetails)
    image_urls: list[str] = Field(default_factory=list)


class MarketplaceUserListingPatchRequest(BaseModel):
    author: MarketplaceAuthorContext
    object_type: Optional[MarketplaceObjectType] = None
    deal_type: Optional[MarketplaceDealType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    price_is_negotiable: Optional[bool] = None
    category_id: Optional[int] = None
    placement_days: Optional[int] = None
    contacts: Optional[MarketplaceContactInput] = None
    items: Optional[list[MarketplaceUserItemInput]] = Field(None, max_length=12)
    details: Optional[MarketplaceListingDetails] = None
    image_urls: Optional[list[str]] = None


class MarketplaceListingActionRequest(BaseModel):
    author: MarketplaceAuthorContext
    status: Literal["paused", "sold", "rented", "archived", "active"]
    placement_days: Optional[int] = None


class MarketplaceModerationRequest(BaseModel):
    moderator: MarketplaceAuthorContext
    action: Literal["approve", "reject", "return_to_moderation"]
    comment: Optional[str] = None
    placement_days: int = 14


class MarketplaceListingDeleteRequest(BaseModel):
    actor: MarketplaceAuthorContext
    reason: Optional[str] = None


class MarketplacePromoteRequest(BaseModel):
    author: MarketplaceAuthorContext
    target_type: MarketplacePromotionTargetType
    target_key: str
    server_id: int
    kind: MarketplacePromotionKind = "free_subscriber"


class MarketplaceFavoriteRequest(BaseModel):
    author: MarketplaceAuthorContext
    target_type: MarketplacePromotionTargetType
    target_key: str
    favorite: bool = True


class MarketplaceListRequest(BaseModel):
    author: Optional[MarketplaceAuthorContext] = None
    server_id: Optional[int] = None
    source: Optional[MarketplaceSource] = None
    q: Optional[str] = None
    object_type: Optional[MarketplaceObjectType] = None
    deal_type: Optional[MarketplaceDealType] = None
    category_id: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort: Literal["smart", "new", "price", "price_desc", "bumped"] = "smart"
    limit: int = 50
    offset: int = 0


class MarketplaceContactClickRequest(BaseModel):
    author: Optional[MarketplaceAuthorContext] = None
    target_type: MarketplacePromotionTargetType
    target_key: str
    contact_type: Literal["telegram", "vk", "game_phone", "site"]


class MarketplaceCategory(BaseModel):
    id: int
    name: str
    color: Optional[dict] = None


class MarketplaceItemReference(BaseModel):
    field: str
    id: int
    kind: str
    name: Optional[str] = None
    icon: Optional[str] = None


class MarketplaceItem(BaseModel):
    slot_id: int
    item_id: int
    name: str
    icon: Optional[str] = None
    item_type: Optional[int] = None
    acs_slot: Optional[int] = None
    stack_count: int = 1
    is_tradeable: bool = False
    custom_type: Optional[str] = None
    inventory_slot_id: Optional[int] = None
    inventory_slot_name: Optional[str] = None
    enchanted: int
    unic_id: int
    unic_id2: int
    unic_id3: int
    color_id: int
    color_name: Optional[str] = None
    strength: int
    quality: int
    quality_name: Optional[str] = None
    wear: int
    transfer: int
    background: int
    background_color: dict
    references: list[MarketplaceItemReference] = Field(default_factory=list)


class MarketplaceExternalPlayer(BaseModel):
    model_config = ConfigDict(extra="allow")

    uid: int
    nickname: Optional[str] = None
    player_id: Optional[int] = None
    online: bool = False


class MarketplaceExternalListing(BaseModel):
    model_config = ConfigDict(extra="allow")

    rented: bool = False
    rent_end_unix: int = 0
    rent_end_at: Optional[datetime.datetime] = None
    owner: Optional[MarketplaceExternalPlayer] = None
    renter: Optional[MarketplaceExternalPlayer] = None


class MarketplaceListing(BaseModel):
    source: MarketplaceSource
    target_type: MarketplacePromotionTargetType
    target_key: str
    server_id: int
    server_label: str
    user_listing_id: Optional[int] = None
    external_list_uid: Optional[int] = None
    object_type: MarketplaceObjectType
    object_type_label: str
    deal_type: MarketplaceDealType
    deal_type_label: str
    title: str
    description: str
    price: Optional[int] = None
    price_label: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_color: Optional[dict] = None
    status: str
    status_label: str
    author_platform: Optional[str] = None
    author_id: Optional[int] = None
    author_site_user_id: Optional[int] = None
    author_display_name: Optional[str] = None
    owner_nickname: Optional[str] = None
    is_subscriber: bool = False
    contacts: Optional[MarketplaceContact] = None
    contact_available: bool = False
    items: list[MarketplaceItem] = Field(default_factory=list)
    details: MarketplaceListingDetails = Field(default_factory=MarketplaceListingDetails)
    image_urls: list[str] = Field(default_factory=list)
    external: Optional[MarketplaceExternalListing] = None
    rented: bool = False
    rent_end_unix: int = 0
    rent_end_at: Optional[datetime.datetime] = None
    views_count: int = 0
    contact_clicks_count: int = 0
    favorites_count: int = 0
    is_favorite: bool = False
    is_promoted: bool = False
    promoted_at: Optional[datetime.datetime] = None
    bumped_at: Optional[datetime.datetime] = None
    published_at: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class MarketplaceExternalOwner(BaseModel):
    nickname: Optional[str] = None


class MarketplaceExternalSimilarListing(BaseModel):
    uid: int
    label: Optional[str] = None
    category_name: Optional[str] = None
    cost_per_hour: Optional[int] = None
    items: list[MarketplaceItem] = Field(default_factory=list)
    owner: Optional[MarketplaceExternalOwner] = None


class MarketplaceListingsResponse(BaseModel):
    server_id: Optional[int] = None
    server_label: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    total: int
    limit: int
    offset: int
    categories: list[MarketplaceCategory]
    listings: list[MarketplaceListing]


class MarketplaceMyListingsResponse(BaseModel):
    total: int
    active_limit: int
    free_bump_available_at: Optional[datetime.datetime] = None
    listings: list[MarketplaceListing]


class MarketplaceListingResponse(BaseModel):
    listing: MarketplaceListing


class MarketplaceModerationListResponse(BaseModel):
    total: int
    listings: list[MarketplaceListing]


class MarketplacePromoteResponse(BaseModel):
    promoted_at: datetime.datetime
    next_free_bump_at: Optional[datetime.datetime] = None


class MarketplaceSimilarResponse(BaseModel):
    listings: list[MarketplaceExternalSimilarListing]
