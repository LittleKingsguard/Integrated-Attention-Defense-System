from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr

class InteractionSkills(BaseModel):
    relationship_type: Optional[str] = None
    tone_preference: Optional[str] = None
    rules: Optional[List[str]] = []
    permissions: Optional[Dict[str, Any]] = {}

class UserBase(BaseModel):
    user_id: str
    address: str
    public_key: Optional[str] = None
    protocols: Optional[List[str]] = []
    interaction_skills: InteractionSkills

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    pass
