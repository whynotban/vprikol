import datetime
from typing import List, Optional, Literal
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
