import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import create_engine, Session, SQLModel

load_dotenv()

DATABASE_URL = os.getenv("DATALINK_DATABASE_URL", "postgresql://datalink_user:datalink_password@localhost:5433/ads_datalink")

engine = create_engine(DATABASE_URL)

def init_db():
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector")) # type: ignore
        session.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
