from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class BackendMeResponse(BaseModel):
    found: bool
    id: Optional[int] = None
    access_level: int
    ref_level: int = 0
    refs_count: int = 0
    notify_platform: Optional[str]
    tg_id: Optional[int] = None
    vk_id: Optional[int] = None
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


class DndSettings(BaseModel):
    dnd_start_hour: Optional[int] = None
    dnd_end_hour: Optional[int] = None


class ForumThreadEntry(BaseModel):
    id: int
    thread_name: Optional[str] = None
    thread_path: Optional[str] = None
    nickname: Optional[str] = None
    created_at: datetime


class AddForumThreadRequest(BaseModel):
    platform: Literal['tg', 'vk']
    platform_user_id: int
    raw_input: str
