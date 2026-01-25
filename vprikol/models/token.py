import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TokenResponse(BaseModel):
    id: int
    project_label: str
    token: Optional[str]
    activated: bool
    disabled_logs: bool
    service: bool
    allowed_ips: List[str]
    subscription_until: Optional[datetime.datetime]
    created_at: datetime.datetime
    modified_at: datetime.datetime


class RequestLogEntry(BaseModel):
    id: int
    request_id: Optional[str] = None
    api_method: Optional[str]
    http_method: str
    params: Dict[str, Any]
    ip_address: str
    created_at: datetime.datetime


class RequestLogResponse(BaseModel):
    data: List[RequestLogEntry]
    next_request_start_id: Optional[int]


class RequestStatsResponse(BaseModel):
    total_count: int
    methods: Dict[str, int]
