from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class SourceType(str, enum.Enum):
    EVENTBRITE = "eventbrite"
    EVENTBRITE_BULK = "eventbrite_bulk"
    INSTAGRAM = "instagram"
    WEBPAGE = "webpage"
    ICS = "ics"
    RSS = "rss"
    MANUAL = "manual"

class PriceTier(str, enum.Enum):
    FREE = "free"
    PAID = "paid"
    DONATION = "donation"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at = Column(DateTime(timezone=True))
    venue = Column(String)
    address = Column(String)
    city = Column(String, index=True)
    price_tier = Column(Enum(PriceTier), default=PriceTier.FREE)
    price_amount = Column(Numeric(10, 2))
    image_url = Column(String)
    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    category = Column(String, index=True)
    fid_hash = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="DRAFT", nullable=False, index=True)
    wp_post_id = Column(Integer)
    
    # Featured events fields
    is_featured = Column(Boolean, default=False, index=True)
    featured_tier = Column(String(20))
    featured_until = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
