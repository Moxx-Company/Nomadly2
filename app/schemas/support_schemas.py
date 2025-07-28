"""
Support Pydantic schemas for Nomadly3 API
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class SupportTicketBase(BaseModel):
    """Base support ticket schema"""
    subject: str
    message: str
    category: str
    priority: str = "medium"
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [
            'Domain Registration', 'Payment & Billing', 'DNS Management',
            'Technical Support', 'Account Issues', 'Feature Request', 'Other'
        ]
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if v.lower() not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v.lower()

class SupportTicketCreate(SupportTicketBase):
    """Schema for creating support ticket"""
    telegram_id: int

class SupportTicketResponse(SupportTicketBase):
    """Schema for support ticket responses"""
    ticket_id: str
    telegram_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FAQResponse(BaseModel):
    """Schema for FAQ responses"""
    id: int
    category: str
    question: str
    answer: str
    priority: int
    
    class Config:
        from_attributes = True

class ContactInfoResponse(BaseModel):
    """Schema for contact information"""
    telegram_support: str
    email_support: str
    website: str
    business_hours: str
    timezone: str
    response_time: str