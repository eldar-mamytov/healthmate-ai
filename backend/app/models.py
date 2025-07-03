from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Boolean # ADDED Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from .database import Base # Correctly import Base from database.py

class User(Base):
    __tablename__ = "users" # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True) # Primary key, auto-increments
    username = Column(String, unique=True, index=True, nullable=False) # Unique username, cannot be null
    email = Column(String, unique=True, index=True, nullable=False) # Unique email, cannot be null
    hashed_password = Column(String, nullable=False) # Stores the hashed password, cannot be null
    is_active = Column(Boolean, default=True) # User account status, default to active
    is_admin = Column(Boolean, default=False) # Admin flag, default to false
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Timestamp of creation
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) # Timestamp of last update
    chat_messages = relationship("ChatMessage", back_populates="user")

    # This method is for representation when you print a User object
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class ChatMessage(Base):
    """
    Represents a single message within a chat session.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Store the role (e.g., 'user', 'assistant')
    role = Column(String, nullable=False) 
    
    # Store the actual message content
    content = Column(Text, nullable=False) 
    
    # Store extracted symptoms (as JSON, allowing for flexibility)
    extracted_symptoms = Column(JSON, default={}) 
    
    # Store recommended actions (as JSON)
    recommendations = Column(JSON, default={}) 
    
    # Timestamp for when the message was created
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to the User model
    user = relationship("User", back_populates="chat_messages")