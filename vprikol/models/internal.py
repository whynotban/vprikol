import datetime
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel

class CheckrRpManualOverrideEntry(BaseModel):
    value: str
    status: Literal["confirmed", "denied"]


class CheckRpManualOverridesListResponse(BaseModel):
    names: List[CheckrRpManualOverrideEntry]
    surnames: List[CheckrRpManualOverrideEntry]


class BotAccount(BaseModel):
    nickname: str
    avg_sessions_per_day: float
    avg_session_duration_seconds: float


class BotDetectionResponse(BaseModel):
    accounts: List[BotAccount]


class AdminEntry(BaseModel):
    nickname: str
    vk_id: Optional[str]
    post: Optional[str]


class AdminsResponse(BaseModel):
    server_id: int
    server_label: str
    updated_at: datetime.datetime
    admins: List[AdminEntry]


class FindStatsResponse(BaseModel):
    total_searches: int
    total_players: int
    total_money: str
    top_servers: Dict[str, int]


class PlayersRequest(BaseModel):
    players: List[dict]
    server_id: int


class PlayerExtendedEntry(BaseModel):
    id: int
    account_id: Optional[int]
    nickname: Optional[str]
    afk_seconds: Optional[int]
    client: Optional[str]
    packetloss: Optional[float]


class IngameAdminData(BaseModel):
    admin_lvl: int
    nickname: str
    ingame_id: int
    reputation: int
    afk: Optional[int] = 0
    recon_id: Optional[int]


class IngameLeaderData(BaseModel):
    nickname: str
    ingame_id: int
    fraction_label: str
    afk: Optional[int] = 0
    phone_number: Optional[int]


class IngameJudgeData(BaseModel):
    index: int
    nickname: Optional[str]
    appointed_at: Optional[datetime.datetime]


class IngameMapData(BaseModel):
    id: int
    x1: int
    y1: int
    x2: int
    y2: int
    color: int


class IngameInterviewData(BaseModel):
    fraction_id: int
    place: Optional[str]
    time: Optional[str]


class RankSalaryEntry(BaseModel):
    rank_number: int
    rank_label: str
    salary: int


class FractionSalariesRequest(BaseModel):
    server_id: int
    data: Dict[str, List[RankSalaryEntry]]


class IngameMemberEntry(BaseModel):
    nickname: str
    ingame_id: int
    nickname_color: str
    phone_number: Optional[int]
    at_work: bool
    rank_label: str


class PunishRequest(BaseModel):
    server_id: int
    value: str


class CurrencyRequest(BaseModel):
    btc: int
    ltc: int
    eth: int
    euro: int
    asc: int
    vc_buy: int
    vc_sell: int
