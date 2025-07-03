from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # For handling form data for login
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware 

from .database import create_db_tables, get_db
from . import models, schemas # Ensure schemas is imported
from . import auth # Import our new auth module

app = FastAPI(title="HealthMate-AI Backend")

# NEW BLOCK: CORS Configuration
origins = [
    "http://localhost:3000",  # Your React frontend's address
    "http://127.0.0.1:3000",  # Another common address for localhost
    # Add other origins if your frontend is deployed elsewhere (e.g., "https://yourfrontend.com")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies/authentication headers
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],     # Allow all headers (e.g., Authorization header for JWT)
)

# --- Password Hashing Setup (MOVED TO AUTH.PY - REMOVE FROM HERE) ---
# pwd_context is now defined in auth.py and imported if needed, or used directly there.
# You no longer need verify_password or get_password_hash functions here,
# as auth.py will handle password logic using pwd_context.
# --------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    create_db_tables()

@app.get("/")
async def read_root():
    return {"message": "Welcome to HealthMate-AI Backend"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is healthy and running."}

# --- User Registration Endpoint (Existing) ---
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
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
    if db_user_by_username:
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

# --- User Login Endpoint (NEW) ---
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and provide an access token.

    - **username**: The user's username or email.
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

# --- Protected Endpoint Example (NEW) ---
@app.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Get information about the current authenticated user.
    Requires a valid access token in the Authorization: Bearer header.
    """
    return current_user

# --- Chat Endpoint (NEW) ---
@app.post("/chat/", response_model=schemas.ChatMessageResponse)
async def chat_with_bot(
    message: schemas.ChatMessageCreate, # The incoming message from the user
    current_user: models.User = Depends(auth.get_current_user), # Ensures user is authenticated
    db: Session = Depends(get_db)
):
    """
    Handles chat messages from the user, stores them, and provides a bot response.
    Eventually integrates with an AI model.
    """
    # 1. Store the user's message in the database
    db_user_message = models.ChatMessage(
        user_id=current_user.id,
        role="user", # This is a user's message
        content=message.content,
        # extracted_symptoms and recommendations can be empty for now, filled by AI later
        extracted_symptoms={},
        recommendations={}
    )
    db.add(db_user_message)
    db.commit()
    db.refresh(db_user_message)

    # 2. Simulate a bot response (will be replaced by AI later)
    bot_response_content = f"Hello {current_user.username}! I received your message: '{message.content}'. I'm still learning to be a health assistant, but I'll get back to you soon!"
    
    # 3. Store the bot's response in the database
    db_bot_message = models.ChatMessage(
        user_id=current_user.id,
        role="assistant", # This is the assistant's message
        content=bot_response_content,
        extracted_symptoms={},
        recommendations={}
    )
    db.add(db_bot_message)
    db.commit()
    db.refresh(db_bot_message)

    # Return the bot's message as the response
    return db_bot_message

# --- Get Chat History Endpoint (NEW) ---
@app.get("/chat/history/", response_model=list[schemas.ChatMessageResponse])
async def get_chat_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the chat history for the current authenticated user.
    """
    chat_history = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == current_user.id).order_by(models.ChatMessage.timestamp).all()
    return chat_history
