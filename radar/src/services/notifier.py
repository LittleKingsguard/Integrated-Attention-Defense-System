import os
import httpx
from typing import List, Optional
from radar.src.db.models import Topic

REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:8000")

async def get_user_address(user_id: str) -> Optional[str]:
    """Fetch user agent address from the Registry."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{REGISTRY_URL}/api/v1/registry/{user_id}")
            if response.status_code == 200:
                return response.json().get("address")
        except Exception as e:
            print(f"Error looking up user {user_id} in registry: {e}")
    return None

async def notify_agent(address: str, topic: Topic):
    """Send notification to the ADS agent."""
    if not address:
        return
    
    # We assume the agent has an endpoint /api/v1/notify
    url = f"{address.rstrip('/')}/api/v1/notify"
    payload = {
        "topic": topic.name,
        "category": topic.category,
        "action": "query_datalink",
        "message": f"New activity detected on topic: {topic.name}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"Failed to notify agent at {url}: {e}")

async def notify_interested_users(topic: Topic, user_ids: List[str]):
    """Notify all users interested in a specific topic."""
    for user_id in user_ids:
        address = await get_user_address(user_id)
        if address:
            await notify_agent(address, topic)
