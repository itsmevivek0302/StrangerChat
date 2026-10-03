from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import RegisterIn, LoginIn, TokenOut
from auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    username = data.username
    email = data.email
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(409, "Username or email already exists")
    user = User(username=username, email=email, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username or email already exists")
    db.refresh(user)
    return {"access_token": create_token(user.id), "user": user}

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(user.id), "user": user}
