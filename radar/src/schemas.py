from typing import List, Optional
from pydantic import BaseModel

class TopicBase(BaseModel):
    name: str
    category: str

class ExtractedTopics(BaseModel):
    topics: List[TopicBase]

class TopicRead(TopicBase):
    id: int

class ProcessRequest(BaseModel):
    user_id: str
    content: str
    source: str = "unknown"

class SubscribeRequest(BaseModel):
    user_id: str
    topic_name: str
    is_subscribed: bool = True

class ProcessResponse(BaseModel):
    topics: List[TopicRead]
    notifications_sent: int
