from pydantic import BaseModel
from typing import List, Dict, Any

class StatsResponse(BaseModel):
    total_events: int
    events_this_week: int
    total_extractions: int
    active_sources: int
    failed_tasks: int
    extraction_success_rate: float
    top_sources: List[Dict[str, Any]]
    events_by_status: Dict[str, int]
    events_by_city: List[Dict[str, Any]]
    recent_errors: List[Dict[str, Any]]
