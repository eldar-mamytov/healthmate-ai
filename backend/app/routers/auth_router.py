from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models, auth # Relative imports to access modules in parent directory
from ..database import get_db

# Initialize APIRouter
router = APIRouter(
    prefix="/auth", # This prefix will be prepended to all paths in this router (e.g., /auth/register)
    tags=["Authentication & Users"], # Tag for FastAPI interactive docs
)

# --- User Registration Endpoint ---
@router.post("/register/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    - **username**: Unique username for the user.
    - **email**: Unique email address for the user.
    - **password**: The user's chosen password (will be hashed).
    """
    db_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username: # Corrected variable name from db_user_by_code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Use get_password_hash from auth.py
    hashed_password = auth.get_password_hash(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# --- User Login Endpoint ---
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and provide an access token.

    - **username**: The user's username (or email, if your authenticate_user supports it).
    - **password**: The user's password.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with 'sub' (subject) being the username (or user ID)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Get Current User Endpoint ---
@router.get("/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Get information about the current authenticated user.
    Requires a valid access token in the Authorization: Bearer header.
    """
    return current_user

# --- Optional: Get all users (for admin/testing, remove later if not needed) ---
@router.get("/users/", response_model=List[schemas.UserResponse])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
                   current_user: models.User = Depends(auth.get_current_user)): # Protected
    """
    Retrieve a list of all registered users. For demonstration/admin purposes.
    Requires authentication.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/test-auth/", tags=["Testing"])
async def test_authentication(current_user: models.User = Depends(auth.get_current_user)):
    """
    A simple test endpoint to check if authentication is working.
    Requires a valid access token.
    """
    return {"message": f"Authentication successful for user: {current_user.username}"}