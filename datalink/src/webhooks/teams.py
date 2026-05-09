from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from ..db.core import get_session
from ..services import rag

router = APIRouter()

@router.post("/events")
async def teams_events(request: Request, session: Session = Depends(get_session)):
    """
    Handle Microsoft Teams outgoing webhooks or graph notifications.
    """
    data = await request.json()
    
    content = data.get("text")
    channel_id = data.get("channelData", {}).get("channel", {}).get("id", "unknown")
    user_id = data.get("from", {}).get("id", "unknown")
    
    if content:
        rag.store_message(
            session,
            platform="teams",
            channel_id=channel_id,
            user_id=user_id,
            content=content
        )
        
    return {"type": "message", "text": "Message processed by ADS Datalink"}
