import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from .base import RatingType, EstateHistoryType

class ServerStatusResponse(BaseModel):
    server_id: int
    server_ip: str
    server_port: int
    server_label: str
    online_players: int
    queue_players: int
    max_players: int
    is_closed: bool
    payday_boost: int
    multiplier_donate: int
    server_vk: Optional[str] = None
    server_discord: Optional[str] = None
    main_admin_vk: Optional[str] = None
    deputy_main_admin_vk: Optional[str] = None
    updated_at: datetime.datetime


class ServerStatusBriefResponse(BaseModel):
    server_id: int
    server_label: str
    server_ip: str
    server_port: int
    online_players: int
    queue_players: int
    max_players: int
    is_closed: bool
    payday_boost: int
    multiplier_donate: int
    updated_at: datetime.datetime


class AllServersStatusResponse(BaseModel):
    data: List[ServerStatusBriefResponse]


class RatingPlayer(BaseModel):
    position: int
    nickname: str
    value: Any
    server_id: Optional[int] = None
    server_label: Optional[str] = None
    additional_value: Optional[Any] = None
    az_coins: Optional[int] = None
    family: Optional[str] = None


class RatingResponse(BaseModel):
    server_id: int
    server_label: str
    rating_type: RatingType
    updated_at: datetime.datetime
    players: List[RatingPlayer]


class AuctionInfo(BaseModel):
    active: bool
    minimal_bet: int
    time_end: Optional[datetime.datetime]
    start_price: int


class Coordinates(BaseModel):
    x: float
    y: float


class HouseEntry(BaseModel):
    id: int
    owner: Optional[str]
    name: Optional[str]
    auction: AuctionInfo
    coordinates: Coordinates


class BusinessEntry(BaseModel):
    id: int
    owner: Optional[str]
    name: str
    auction: AuctionInfo
    coordinates: Coordinates


class EstateResponse(BaseModel):
    server_id: int
    server_label: str
    updated_at: datetime.datetime
    houses: List[HouseEntry]
    businesses: List[BusinessEntry]


class EstateHistoryEntry(BaseModel):
    previous_owner: Optional[str]
    new_owner: Optional[str]
    estate_name: Optional[str]
    action_at: datetime.datetime


class EstateHistoryResponse(BaseModel):
    server_id: int
    server_label: str
    estate_type: EstateHistoryType
    estate_id: int
    estate_name: Optional[str]
    total: int
    limit: int
    offset: int
    data: List[EstateHistoryEntry]


class TerritoriesCount(BaseModel):
    grove: int = 0
    ballas: int = 0
    vagos: int = 0
    rifa: int = 0
    aztec: int = 0
    nw: int = 0


class MapResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    server_id: int
    server_label: str
    updated_at: datetime.datetime
    image: str = Field(..., alias="image")
    territories_count: TerritoriesCount


class GraphPoint(BaseModel):
    time: datetime.datetime
    online: int
    queue: int
    project_avg: int


class ServerOnlineHistoryResponse(BaseModel):
    server_id: int
    data: List[GraphPoint]


class EXPCalcResponse(BaseModel):
    current_lvl: int
    target_lvl: int
    exp_needed: int
    total_exp_needed: int


class MapZone(BaseModel):
    id: int
    x1: int
    y1: int
    x2: int
    y2: int
    color: int
    type: str
    money: Optional[int] = None
    respects: Optional[int] = None
    drugden: Optional[bool] = None
    respawn_fraction_id: Optional[int] = None
    family_id: Optional[int] = None
    family_name: Optional[str] = None
    family_color: Optional[int] = None
    family_flag: Optional[int] = None
    family_logo: Optional[int] = None
    zone_coin_count: Optional[int] = None
    zone_money_amount: Optional[int] = None


class FamilyTerritoryCountEntry(BaseModel):
    family_db_id: int
    family_name: str
    territory_count: int


class MapZonesResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    server_id: int
    server_label: str
    data: List[MapZone]
    updated_at: datetime.datetime
    ghetto_territories_count: TerritoriesCount
    fam_ghetto_territories_count: List[FamilyTerritoryCountEntry]


class CurrencyResponse(BaseModel):
    server_id: int
    server_label: str
    btc: int
    ltc: int
    eth: int
    euro: int
    asc: int
    vc_buy: int
    vc_sell: int
    updated_at: datetime.datetime


class GhettoRatingEntry(BaseModel):
    fraction_id: int
    fraction_label: str
    territory_count: int


class GhettoRatingResponse(BaseModel):
    server_id: int
    server_label: str
    data: List[GhettoRatingEntry]
    updated_at: datetime.datetime


class GhettoCaptureEntry(BaseModel):
    zone_id: int
    defender_fraction_id: int
    defender_fraction_label: str
    attacker_fraction_id: int
    attacker_fraction_label: str
    captured_at: datetime.datetime


class GhettoCapturesResponse(BaseModel):
    server_id: int
    server_label: str
    data: List[GhettoCaptureEntry]
    updated_at: datetime.datetime


class FamilyTopEntry(BaseModel):
    family_id: int
    family_name: str
    family_color: int
    family_flag: int
    territory_count: int


class FamilyTopResponse(BaseModel):
    server_id: int
    server_label: str
    data: List[FamilyTopEntry]
    updated_at: datetime.datetime


class FamilyCaptureEntry(BaseModel):
    zone_id: int
    defender_family_id: int
    defender_family_name: str
    defender_family_color: int
    defender_family_flag: int
    attacker_family_id: int
    attacker_family_name: str
    attacker_family_color: int
    attacker_family_flag: int
    attack_date: datetime.datetime
    capture_date: datetime.datetime
    zone_coin_count: int
    zone_money_amount: int


class FamilyCapturesResponse(BaseModel):
    server_id: int
    server_label: str
    data: List[FamilyCaptureEntry]
    updated_at: datetime.datetime
