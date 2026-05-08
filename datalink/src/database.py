import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from sqlmodel import create_engine, Session, SQLModel

load_dotenv()

# Default to the same DB but could be different
DATABASE_URL = os.getenv("DATALINK_DATABASE_URL", "postgresql://ads_user:ads_password@localhost:5432/ads_registry")

engine = create_engine(DATABASE_URL)

def init_db():
    # Ensure pgvector extension is enabled
    with Session(engine) as session:
        session.execute("CREATE EXTENSION IF NOT EXISTS vector")
        session.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
