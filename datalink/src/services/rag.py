import os
import httpx
from typing import List, Optional, Sequence
from sqlmodel import Session, select
from datalink.src.db.embeddings import get_embeddings
from datalink.src.db.models import ChannelMessage

embeddings = get_embeddings()

def search_messages(session: Session, query: str, top_k: int = 5, platform: Optional[str] = None) -> Sequence[ChannelMessage]:
    # 1. Generate embedding for the query
    query_vector = embeddings.embed_query(query)
    
    # 2. Perform similarity search using PGVector
    statement = select(ChannelMessage).order_by(
        ChannelMessage.embedding.cosine_distance(query_vector) # type: ignore
    ).limit(top_k)
    
    if platform:
        statement = statement.where(ChannelMessage.platform == platform)
        
    results = session.exec(statement).all()
    return results

def store_message(session: Session, platform: str, channel_id: str, user_id: str, content: str):
    # 1. Generate embedding for the message content
    embedding = embeddings.embed_query(content)
    
    # 2. Create and store the message
    message = ChannelMessage(
        platform=platform,
        channel_id=channel_id,
        user_id=user_id,
        content=content,
        embedding=embedding
    )
    
    session.add(message)
    session.commit()
    session.refresh(message)

    # Notify Radar service (fire and forget / async)
    radar_url = os.getenv("RADAR_URL", "http://localhost:8002")
    if radar_url:
        try:
            # Note: In a production app, this would be a background task or message queue
            # For now, we'll do a quick async POST using httpx
            import threading
            def notify_radar_sync():
                try:
                    httpx.post(f"{radar_url}/api/v1/radar/process", json={
                        "user_id": user_id,
                        "content": content,
                        "source": f"datalink_{platform}"
                    }, timeout=2.0)
                except Exception as e:
                    print(f"Failed to notify Radar: {e}")
            
            threading.Thread(target=notify_radar_sync).start()
        except Exception:
            pass

    return message
