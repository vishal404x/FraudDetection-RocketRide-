from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, models
from app.db.session import get_db
from app.core.config import settings
from datetime import timedelta, datetime
from jose import jwt
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginPayload(BaseModel):
    email: str
    password: str

@router.post('/register', response_model=dict)
def register(payload: dict, db: Session = Depends(get_db)):
    email = payload.get('email')
    password = payload.get('password')
    org_name = payload.get('organization_name')
    if not email or not password:
        raise HTTPException(status_code=400, detail='email and password required')
    existing = crud.get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    # Create org
    if org_name:
        org = crud.create_organization(db, org_name)
    else:
        org = crud.create_organization(db, 'Default Organization')
    user = crud.create_user(db, email, password, org.id, full_name=payload.get('full_name'))
    return {'id': user.id, 'email': user.email}

@router.post('/login')
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not crud.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password')
    to_encode = {"sub": str(user.id), "org": str(user.organization_id)}
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
