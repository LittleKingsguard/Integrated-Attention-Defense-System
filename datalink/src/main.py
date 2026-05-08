# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlmodel import Session
from .database import get_session, init_db
from .models import ChannelMessage, MessageQuery
from .services import rag
from .webhooks import slack, teams

app = FastAPI(title="Datalink RAG Service", version="1.0.0")

# Include webhook routers (to be implemented)
app.include_router(slack.router, prefix="/webhooks/slack", tags=["Slack"])
app.include_router(teams.router, prefix="/webhooks/teams", tags=["Teams"])

@app.on_event("startup")
def on_startup():
    init_db()

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
