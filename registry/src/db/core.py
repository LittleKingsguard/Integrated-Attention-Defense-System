import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

load_dotenv()

# Following the ADS pattern for environment variable naming and fallback
DATABASE_URL = os.getenv("REGISTRY_DATABASE_URL", "postgresql://ads_user:ads_password@localhost:5432/ads_registry")

engine = create_engine(DATABASE_URL)

def init_db():
    # In ADS, init_db uses raw SQL. We'll use SQLModel but keep the function name.
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
