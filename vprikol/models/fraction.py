import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel

class MembersPlayer(BaseModel):
    account_id: Optional[int]
    nickname: str
    is_online: bool
    is_leader: bool
    rank_number: int
    rank_label: Optional[str]
    ingame_id: Optional[int]
    nickname_color: Optional[int]


class MembersRecord(BaseModel):
    online_players: int
    leader_nickname: Optional[str]
    modified_at: Optional[datetime.datetime]
    modified_by: Literal["system", "admin"]


class MembersResponse(BaseModel):
    server_id: int
    fraction_id: int
    server_label: str
    fraction_label: str
    total_players: int
    total_online: int
    leader_nickname: Optional[str]
    is_leader_online: bool
    online_updated_at: datetime.datetime
    members_updated_at: datetime.datetime
    online_record: MembersRecord
    players: List[MembersPlayer]


class LeaderEntry(BaseModel):
    fraction_id: int
    fraction_label: str
    nickname: str
    ingame_id: int
    phone_number: Optional[int]
    afk: Optional[int]


class LeadersResponse(BaseModel):
    data: List[LeaderEntry]
    server_id: int
    server_label: str
    updated_at: datetime.datetime


class InterviewEntry(BaseModel):
    fraction_id: int
    fraction_label: str
    place: Optional[str]
    time: Optional[str]


class InterviewsResponse(BaseModel):
    server_id: int
    server_label: str
    data: List[InterviewEntry]
    updated_at: datetime.datetime


class PlayerEntry(BaseModel):
    color: int
    ping: int
    id: int
    lvl: int
    nickname: str


class PlayersResponse(BaseModel):
    server_id: int
    server_label: str
    players: List[PlayerEntry]
    updated_at: datetime.datetime
