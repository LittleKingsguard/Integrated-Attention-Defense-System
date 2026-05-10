from typing import List, cast
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from datetime import datetime
from radar.src.db.core import get_session, init_db
from radar.src.db.models import Topic, UserTopicLink, RadarEvent
from radar.src.schemas import ProcessRequest, ProcessResponse, SubscribeRequest, TopicRead
from radar.src.services.extractor import extractor
from radar.src.services.notifier import notify_interested_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Radar Topic Tracking Service", version="1.0.0", lifespan=lifespan)

@app.post("/api/v1/radar/process", response_model=ProcessResponse)
async def process_content(
    request: ProcessRequest, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # 1. Log event
    event = RadarEvent(source=request.source, user_id=request.user_id, content=request.content)
    session.add(event)
    
    # 2. Extract topics
    extracted_topics = await extractor.extract_keywords(request.content)
    
    result_topics = []
    notifications_count = 0
    
    for ext in extracted_topics:
        # 3. Find or create topic
        statement = select(Topic).where(Topic.name == ext.name)
        topic = session.exec(statement).first()
        if not topic:
            topic = Topic(name=ext.name, category=ext.category)
            session.add(topic)
            session.commit()
            session.refresh(topic)
        
        result_topics.append(TopicRead(id=cast(int, topic.id), name=topic.name, category=topic.category))
        
        # 4. Link user to topic (touch)
        link_statement = select(UserTopicLink).where(
            UserTopicLink.user_id == request.user_id,
            UserTopicLink.topic_id == topic.id
        )
        link = session.exec(link_statement).first()
        if not link:
            link = UserTopicLink(user_id=request.user_id, topic_id=cast(int, topic.id))
            session.add(link)
        else:
            link.last_touched = datetime.utcnow()
        
        # 5. Find other interested users (subscribed or touched)
        sub_statement = select(UserTopicLink.user_id).where(
            UserTopicLink.topic_id == topic.id,
            UserTopicLink.user_id != request.user_id # Don't notify the sender
        )
        interested_users = session.exec(sub_statement).all()
        
        # 6. Trigger notifications in background
        if interested_users:
            background_tasks.add_task(notify_interested_users, topic, list(interested_users))
            notifications_count += len(interested_users)
            
    session.commit()
    return ProcessResponse(topics=result_topics, notifications_sent=notifications_count)

@app.post("/api/v1/radar/subscribe")
async def subscribe_topic(request: SubscribeRequest, session: Session = Depends(get_session)):
    statement = select(Topic).where(Topic.name == request.topic_name)
    topic = session.exec(statement).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    link_statement = select(UserTopicLink).where(
        UserTopicLink.user_id == request.user_id,
        UserTopicLink.topic_id == topic.id
    )
    link = session.exec(link_statement).first()
    if not link:
        link = UserTopicLink(user_id=request.user_id, topic_id=cast(int, topic.id), is_subscribed=request.is_subscribed)
        session.add(link)
    else:
        link.is_subscribed = request.is_subscribed
        
    session.commit()
    return {"status": "ok", "subscribed": request.is_subscribed}

@app.get("/api/v1/radar/topics", response_model=List[TopicRead])
async def list_topics(session: Session = Depends(get_session)):
    return session.exec(select(Topic)).all()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "radar"}
