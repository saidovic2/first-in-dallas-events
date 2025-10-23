import redis
import json
from config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def queue_extraction_task(task_id: int, url: str, source_type: str):
    """Queue a task for the worker to process"""
    task_data = {
        "task_id": task_id,
        "url": url,
        "source_type": source_type
    }
    redis_client.lpush("extraction_queue", json.dumps(task_data))
    return True

def get_next_task():
    """Get the next task from the queue (used by worker)"""
    task_json = redis_client.rpop("extraction_queue")
    if task_json:
        return json.loads(task_json)
    return None
