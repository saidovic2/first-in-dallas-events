from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class SourceType(str, enum.Enum):
    FACEBOOK = "facebook"
    FACEBOOK_BULK = "facebook_bulk"
    EVENTBRITE = "eventbrite"
    EVENTBRITE_BULK = "eventbrite_bulk"
    INSTAGRAM = "instagram"
    WEBPAGE = "webpage"
    ICS = "ics"
    RSS = "rss"
    MANUAL = "manual"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    status = Column(String, default="queued", nullable=False, index=True)
    logs = Column(Text)
    error_message = Column(Text)
    events_extracted = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
