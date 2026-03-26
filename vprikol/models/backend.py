from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class BackendMeResponse(BaseModel):
    found: bool
    access_level: int
    ref_level: int = 0
    notify_platform: Optional[str]
    site_url: str


class NotificationSubscriptionEntry(BaseModel):
    id: int
    server_id: int
    event_type: str
    target_value: str
    created_at: datetime


class TgAuthConfirmResponse(BaseModel):
    success: bool
    redirect_uri: str
    site_url: str


class PrivacyToggleRequest(BaseModel):
    platform: Literal['vk', 'tg']
    user_id: int
    server_id: int
    nickname: str
    is_superadmin: bool = False
