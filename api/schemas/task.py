from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskCreate(BaseModel):
    urls: List[str]

class TaskResponse(BaseModel):
    id: int
    url: str
    source_type: str
    status: str
    logs: Optional[str]
    error_message: Optional[str]
    events_extracted: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
