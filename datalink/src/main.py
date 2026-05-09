from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from datalink.src.db.core import get_session, init_db
from datalink.src.db.models import ChannelMessage, MessageQuery
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

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "datalink"}
