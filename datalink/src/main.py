from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from datalink.src.db.core import get_session, init_db
from datalink.src.db.models import ChannelMessage, MessageQuery, MessageIngest
from datalink.src.services import rag
from datalink.src.webhooks import slack, teams

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    yield
    # Shutdown logic (none needed yet)

app = FastAPI(title="Datalink RAG Service", version="1.0.0", lifespan=lifespan)

# Include webhook routers
app.include_router(slack.router, prefix="/webhooks/slack", tags=["Slack"])
app.include_router(teams.router, prefix="/webhooks/teams", tags=["Teams"])

@app.post("/query", response_model=list[ChannelMessage])
def query_context(query_data: MessageQuery, session: Session = Depends(get_session)):
    """
    Semantic search across stored channel messages.
    Used by ADS agents to gather information.
    """
    try:
        results = rag.search_messages(
            session, 
            query=query_data.query, 
            top_k=query_data.top_k, 
            platform=query_data.platform
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest", response_model=ChannelMessage)
def ingest_message(message_data: MessageIngest, session: Session = Depends(get_session)):
    """
    Push new messages into the Datalink store.
    Used by ADS agents for Email/A2A updates.
    """
    try:
        message = rag.store_message(
            session,
            platform=message_data.platform,
            channel_id=message_data.channel_id,
            user_id=message_data.user_id,
            content=message_data.content
        )
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "datalink"}
