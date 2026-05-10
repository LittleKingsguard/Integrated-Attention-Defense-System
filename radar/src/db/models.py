from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class UserTopicLink(SQLModel, table=True):
    user_id: str = Field(primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    is_subscribed: bool = Field(default=False)
    last_touched: datetime = Field(default_factory=datetime.utcnow)

class Topic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    category: str = Field(index=True) # e.g., "Project", "Ticket", "Office", "Working Group", "Individual"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RadarEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str # e.g., "datalink", "agent"
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
