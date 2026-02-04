import datetime
from typing import List, Optional
from pydantic import BaseModel

class ItemEntry(BaseModel):
    item_id: int
    name: str
    icon: str
    acs_slot: Optional[int]
    type: int
    active: int
    skin_id: Optional[int]
    updated_at: datetime.datetime


class ItemsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ItemEntry]


class ItemHistoryEntry(BaseModel):
    item_id: int
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime.datetime


class ItemsHistoryResponse(BaseModel):
    total: int
    changes: List[ItemHistoryEntry]
