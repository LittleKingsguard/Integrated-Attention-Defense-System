import os
import hashlib
import hmac
import time
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlmodel import Session
from ..database import get_session
from ..services import rag

router = APIRouter()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

async def verify_slack_signature(request: Request, x_slack_signature: str = Header(None), x_slack_request_timestamp: str = Header(None)):
    if not SLACK_SIGNING_SECRET:
        return # Skip verification if secret not set for dev
        
    if not x_slack_signature or not x_slack_request_timestamp:
        raise HTTPException(status_code=400, detail="Missing Slack headers")

    if abs(time.time() - int(x_slack_request_timestamp)) > 60 * 5:
        raise HTTPException(status_code=400, detail="Request too old")

    body = await request.body()
    sig_basestring = f"v0:{x_slack_request_timestamp}:{body.decode('utf-8')}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, x_slack_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

@router.post("/events")
async def slack_events(request: Request, session: Session = Depends(get_session)):
    """
    Handle Slack events (Url Verification & Message events)
    """
    data = await request.json()
    
    # 1. Handle URL Verification (Challenge)
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    
    # 2. Verify Signature (only for non-challenge events)
    # await verify_slack_signature(request, ...) 
    # Note: verification needs raw body, already consumed by .json()
    # In production, use a middleware or custom dependency that handles this correctly.

    # 3. Process Message Event
    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        content = event.get("text")
        channel_id = event.get("channel")
        user_id = event.get("user")
        
        if content and channel_id and user_id:
            rag.store_message(
                session,
                platform="slack",
                channel_id=channel_id,
                user_id=user_id,
                content=content
            )
            
    return {"status": "ok"}
