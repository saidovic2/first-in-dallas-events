from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class SourceStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"

class SourceType(str, enum.Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WEBPAGE = "webpage"
    ICS = "ics"
    RSS = "rss"
    MANUAL = "manual"

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    last_fetched_at = Column(DateTime(timezone=True))
    status = Column(Enum(SourceStatus), default=SourceStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
