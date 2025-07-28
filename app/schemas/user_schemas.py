"""
User Pydantic schemas for Nomadly3 API
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: str = "en"
    technical_email: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    telegram_id: int
    
    @field_validator('telegram_id')
    @classmethod
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError('Telegram ID must be positive')
        return v

class UserUpdate(UserBase):
    """Schema for updating user information"""
    pass

class UserResponse(UserBase):
    """Schema for user API responses"""
    telegram_id: int
    balance_usd: Decimal
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BalanceUpdate(BaseModel):
    """Schema for balance operations"""
    operation: str  # "add", "deduct", "set"
    amount: Decimal
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v):
        if v not in ['add', 'deduct', 'set']:
            raise ValueError('Operation must be add, deduct, or set')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class UserRegistrationRequest(BaseModel):
    """Schema for user registration requests"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = "en"  # Fix: Added missing language field
    initial_balance: Optional[Decimal] = None  # Fix: Added missing initial_balance field
    
    @field_validator('telegram_id')
    @classmethod
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError('Telegram ID must be positive')
        return v
        
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        valid_languages = ['en', 'fr', 'hi', 'zh', 'es']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v
        return v

class UserLoginRequest(BaseModel):
    """Schema for user login requests"""
    telegram_id: int
    
    @field_validator('telegram_id')
    @classmethod
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError('Telegram ID must be positive')
        return v

class TokenResponse(BaseModel):
    """Schema for authentication token responses"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserStateResponse(BaseModel):
    """Schema for user state responses"""
    telegram_id: int
    current_state: str
    state_data: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserStateUpdate(BaseModel):
    """Schema for updating user state"""
    state: str
    data: Optional[dict] = None