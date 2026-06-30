from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import os

from database import get_db
import crud
from schemas import UserCreate, UserResponse, UserLogin, ForgotPasswordRequest
from auth_utils import verify_password, generate_session_token, hash_password
from routers.deps import SESSION_COOKIE, get_current_user
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_DURATION_DAYS = 7
COOKIE_SECURE = os.environ.get("ENV") == "production"  # True only over HTTPS in prod


@router.post("/signup", status_code=201, response_model=UserResponse)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    if crud.get_user_by_phone(db, body.phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is already registered")
    return crud.create_user(db, body)


@router.post("/login", response_model=UserResponse)
def login(body: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    crud.delete_expired_sessions(db)

    token = generate_session_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DURATION_DAYS)
    user_agent = request.headers.get("user-agent")

    crud.create_session(db, user_id=user.id, token=token, expires_at=expires_at, user_agent=user_agent)

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )

    return user


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        crud.delete_session(db, token)

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    if user.phone != body.phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect details. Reset failed.")

    hashed_pwd = hash_password(body.new_password)
    crud.update_user_password(db, user, hashed_pwd)
    return {"message": "Password updated successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user