from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON

class RegistryUser(SQLModel, table=True):
    user_id: str = Field(primary_key=True)
    address: str
    public_key: Optional[str] = None
    protocols: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    interaction_skills: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
