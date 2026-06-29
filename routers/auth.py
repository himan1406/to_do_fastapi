from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
import crud
from schemas import UserCreate, UserResponse, UserLogin, ForgotPasswordRequest, Token
from auth_utils import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=201, response_model=UserResponse)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    existing_user_email = crud.get_user_by_email(db, body.email)
    if existing_user_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    
    existing_user_phone = crud.get_user_by_phone(db, body.phone)
    if existing_user_phone is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is already registered"
        )
    
    return crud.create_user(db, body)

@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Check if phone number matches the user
    if user.phone != body.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect details. Reset failed."
        )
    
    # Update password
    hashed_pwd = hash_password(body.new_password)
    crud.update_user_password(db, user, hashed_pwd)
    
    return {"message": "Password updated successfully"}
