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
