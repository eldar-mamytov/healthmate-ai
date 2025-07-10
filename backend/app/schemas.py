from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, Literal, List

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

# --- Token Schemas (Existing) ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None

# --- ChatMessage Schemas (Existing) ---
class ChatMessageBase(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    extracted_symptoms: Optional[Dict[str, Any]] = {}
    recommendations: Optional[Dict[str, Any]] = {}

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    model_choice: Literal["openai", "flan-t5", "embedding"]
    message: str

class EmbedRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]