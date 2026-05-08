from typing import List, Optional, Dict, Any
from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlmodel import SQLModel, Field, Column
# pyrefly: ignore [missing-import]
from pgvector.sqlalchemy import Vector

class ChannelMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str # slack, teams
    channel_id: str
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Vector column for semantic search
    # embeddinggemma typically uses 768 or 1024 dimensions. 
    # Based on Gemma 2, it's often 1024 or 3584. 
    # I'll use 1024 as a common default for modern small-medium models, 
    # but the extension handles dynamic sizing if we don't specify, 
    # though it's better to be explicit.
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(768))) 

class MessageQuery(SQLModel):
    query: str
    top_k: int = 5
    platform: Optional[str] = None
