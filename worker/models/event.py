from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
import enum

Base = declarative_base()

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
    FREE = "FREE"
    PAID = "PAID"
    DONATION = "DONATION"

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
    price_tier = Column(ENUM('FREE', 'PAID', 'DONATION', name='pricetier', create_type=True), default="FREE")
    price_amount = Column(Numeric(10, 2))
    image_url = Column(String)
    source_url = Column(String, nullable=False)
    source_type = Column(ENUM('FACEBOOK', 'FACEBOOK_BULK', 'EVENTBRITE', 'EVENTBRITE_BULK', 'INSTAGRAM', 'WEBPAGE', 'ICS', 'RSS', 'MANUAL', 'facebook_bulk', 'eventbrite', 'eventbrite_bulk', name='sourcetype', create_type=True), nullable=False)
    category = Column(String, index=True)
    fid_hash = Column(String, unique=True, index=True, nullable=False)
    status = Column(ENUM('DRAFT', 'PUBLISHED', name='eventstatus', create_type=True), default="DRAFT", nullable=False, index=True)
    wp_post_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
