from typing import Optional
from sqlmodel import Session, select
from .models import RegistryUser
from .schemas import UserCreate

def get_user(session: Session, user_id: str) -> Optional[RegistryUser]:
    statement = select(RegistryUser).where(RegistryUser.user_id == user_id)
    return session.exec(statement).first()

def create_or_update_user(session: Session, user_data: UserCreate) -> RegistryUser:
    db_user = get_user(session, user_data.user_id)
    
    if db_user:
        # Update existing user
        db_user.address = user_data.address
        db_user.public_key = user_data.public_key
        db_user.protocols = user_data.protocols
        db_user.interaction_skills = user_data.interaction_skills.model_dump()
    else:
        # Create new user
        db_user = RegistryUser(
            user_id=user_data.user_id,
            address=user_data.address,
            public_key=user_data.public_key,
            protocols=user_data.protocols,
            interaction_skills=user_data.interaction_skills.model_dump()
        )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
