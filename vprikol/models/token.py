import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    id: int
    project_label: str
    token: Optional[str] = None
    activated: bool
    disabled_logs: bool
    service: bool
    bypass_antifloods: bool = False
    allowed_ips: List[str]
    allowed_methods: List[str] = Field(default_factory=list)
    rate_limits: Dict[str, Any] = Field(default_factory=dict)
    daily_limit: Optional[int] = None
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
    status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: datetime.datetime


class RequestLogResponse(BaseModel):
    data: List[RequestLogEntry]
    next_request_start_id: Optional[int]


class RequestStatsResponse(BaseModel):
    total_count: int
    methods: Dict[str, int]


class RateLimitStatusResponse(BaseModel):
    daily_used: Optional[int] = None
    daily_limit: Optional[int] = None
    find_used: int = 0
    find_limit: int = 15
    bypass_antifloods: bool = False
    per_method: Dict[str, Any] = Field(default_factory=dict)


class TokenUsageEntry(BaseModel):
    day: datetime.date
    token_id: int
    project_label: str
    method: str
    requests: int


class TokensUsageResponse(BaseModel):
    entries: List[TokenUsageEntry]


RequestJournalKind = Literal["all", "errors", "client_errors", "slow"]


class RequestJournalEntry(BaseModel):
    id: int
    request_id: Optional[str] = None
    token_id: int
    project_label: str = ""
    api_method: Optional[str] = None
    http_method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    ip_address: str
    status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: datetime.datetime


class RequestJournalResponse(BaseModel):
    entries: List[RequestJournalEntry]
    next_before_id: Optional[int] = None


class RequestsTimelinePoint(BaseModel):
    bucket: datetime.datetime
    total: int
    errors: int
    client_errors: int
    p95_ms: Optional[int] = None


class RequestsMethodSummary(BaseModel):
    api_method: str
    total: int
    errors: int
    client_errors: int
    avg_ms: Optional[int] = None
    p95_ms: Optional[int] = None


class RequestsTokenSummary(BaseModel):
    token_id: int
    project_label: str
    total: int
    errors: int
    client_errors: int


class RequestsOverviewResponse(BaseModel):
    hours: int
    total: int
    errors: int
    client_errors: int
    slow: int
    slow_threshold_ms: int
    p50_ms: Optional[int] = None
    p95_ms: Optional[int] = None
    timeline: List[RequestsTimelinePoint]
    methods: List[RequestsMethodSummary]
    tokens: List[RequestsTokenSummary]
