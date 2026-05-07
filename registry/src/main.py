from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlmodel import Session
from .database import get_session, init_db
from .schemas import UserCreate, UserRead
from . import crud
from .models import RegistryUser

app = FastAPI(title="ADS Discovery Registry", version="1.0.0")

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/api/v1/registry/", response_model=UserRead)
def register_user(user: UserCreate, response: Response, session: Session = Depends(get_session)):
    existing_user = crud.get_user(session, user.user_id)
    db_user = crud.create_or_update_user(session, user)
    
    if existing_user:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_201_CREATED
    
    return db_user

@app.get("/api/v1/registry/{user_id}", response_model=UserRead)
def lookup_user(user_id: str, session: Session = Depends(get_session)):
    db_user = crud.get_user(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/health")
def health_check():
    return {"status": "ok"}
