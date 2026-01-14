import datetime
from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from .base import RatingType

class CheckRpNameData(BaseModel):
    value: Optional[str]
    is_existing: bool
    is_confirmed: bool
    nationalities_chart: Optional[str]


class CheckRpResponse(BaseModel):
    first_name: CheckRpNameData
    last_name: CheckRpNameData
    nickname: str


class RpNickResponse(BaseModel):
    name: str
    surname: str
    nickname: str


class ServerInfo(BaseModel):
    server_id: int
    server_label: str


class PlayerGeneral(BaseModel):
    account_id: int
    skin_id: int
    nickname: str
    gender: str
    played_hours: int
    phone_number: Optional[int]
    health: int
    hunger: int
    max_hunger: int
    drug_addict_lvl: int
    marriage: Optional[str]
    job_label: Optional[str]


class PlayerFraction(BaseModel):
    fraction_id: Optional[int]
    fraction_label: Optional[str]
    rank_number: Optional[int]
    rank_label: Optional[str]


class IndividualAccounts(BaseModel):
    account_1: Optional[int] = Field(None, alias="1")
    account_2: Optional[int] = Field(None, alias="2")
    account_3: Optional[int] = Field(None, alias="3")
    account_4: Optional[int] = Field(None, alias="4")
    account_5: Optional[int] = Field(None, alias="5")
    account_6: Optional[int] = Field(None, alias="6")


class PlayerMoney(BaseModel):
    az_coins: int
    total_money: int
    cash: int
    bank_balance: int
    deposit: int
    have_bank_card: bool
    charity_money: int
    phone_balance: Optional[int]
    individual_accounts: IndividualAccounts


class PlayerLvl(BaseModel):
    lvl: int
    current_xp: int
    max_xp: int


class PlayerPunishes(BaseModel):
    law_count: int
    wanted_lvl: int
    warns_count: int


class PlayerVIP(BaseModel):
    vip_lvl: Optional[int]
    vip_label: Optional[str]
    vip_expiration_date: Optional[datetime.datetime]
    have_addition_vip: bool
    addition_vip_expiration_date: Optional[datetime.datetime]


class PlayerRatingEntry(BaseModel):
    rating_type: RatingType
    position: int
    value: Any


class AdminInfo(BaseModel):
    is_admin: Optional[bool]
    post: Optional[str]
    vk_tag: Optional[str]


class FindPlayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    server: ServerInfo
    general: PlayerGeneral
    admin_info: AdminInfo
    fraction: PlayerFraction
    money: PlayerMoney
    lvl: PlayerLvl
    punishes: PlayerPunishes
    vip_info: PlayerVIP
    ratings: List[PlayerRatingEntry] = []
    views_today: int = 0
    views_total: int = 0
    is_premium: bool = False
    is_cached: bool = False
    is_hidden: bool = False
    updated_at: datetime.datetime


class OnlineEntry(BaseModel):
    date: datetime.date
    hours: int
    minutes: int
    seconds: int


class OnlineResponse(BaseModel):
    online: List[OnlineEntry]
    have_active_session: bool
    active_session_login_at: Optional[datetime.datetime]
    last_login_at: Optional[datetime.datetime]
    last_logout_at: Optional[datetime.datetime]


class PlayerSessionEntry(BaseModel):
    login_at: datetime.datetime
    logout_at: Optional[datetime.datetime]


class PlayerSessionsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    sessions: List[PlayerSessionEntry]


class CalendarDayEntry(BaseModel):
    date: datetime.date
    count: int
    durations: List[int]
    total_played_minutes: int


class PlayerCalendarResponse(BaseModel):
    server_id: int
    nickname: str
    year: int
    month: int
    days: List[CalendarDayEntry]


class NicknameHistoryEntry(BaseModel):
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime.datetime


class MoneyHistoryEntry(BaseModel):
    date: datetime.date
    value: int


class PlayerViewEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    platform: Optional[str]
    executor_id: Optional[int]
    created_at: datetime.datetime


class PlayerViewsResponse(BaseModel):
    views: List[PlayerViewEntry]


class PrivacyToggleRequest(BaseModel):
    platform: Literal['vk', 'tg']
    user_id: int
    server_id: int
    nickname: str
    is_superadmin: bool = False
