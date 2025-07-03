from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

# --- User Schemas (Existing) ---
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

# --- Token Schemas (NEW) ---
# Schema for the JWT token itself (what the API returns upon successful login)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" # Standard token type for JWTs

# Schema for the data contained within the JWT payload (e.g., user identifier)
class TokenData(BaseModel):
    username: str | None = None # Using username as the subject ('sub') in the token

# ChatMessage Schemas
class ChatMessageBase(BaseModel):
    """
    Base schema for a chat message, defining common attributes.
    """
    role: str # e.g., 'user', 'assistant'
    content: str
    
    # Optional fields for AI-extracted data
    extracted_symptoms: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None

class ChatMessageCreate(ChatMessageBase):
    """
    Schema for creating a new chat message.
    User ID will be added by the backend based on the authenticated user.
    """
    pass # No new fields beyond ChatMessageBase for creation

class ChatMessageResponse(ChatMessageBase):
    """
    Schema for returning a chat message, including database-generated fields.
    """
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True # Was orm_mode = True in older Pydantic versions