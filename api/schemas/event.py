from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from decimal import Decimal

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: Optional[datetime] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    price_tier: str = "free"
    price_amount: Optional[Decimal] = None
    image_url: Optional[str] = None
    source_url: str
    source_type: str
    category: Optional[str] = None
    fid_hash: str
    status: str = "draft"

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    price_tier: Optional[str] = None
    price_amount: Optional[Decimal] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_at: datetime
    end_at: Optional[datetime]
    venue: Optional[str]
    address: Optional[str]
    city: Optional[str]
    price_tier: str
    price_amount: Optional[Decimal]
    image_url: Optional[str]
    source_url: str
    source_type: str
    category: Optional[str]
    fid_hash: str
    status: str
    wp_post_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EventFilter(BaseModel):
    status: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    price_tier: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0
