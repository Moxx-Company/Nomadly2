"""
User model for Nomadly3 Domain Registration Bot
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, BIGINT
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal

from ..core.database import Base

# Import for relationships - forward declarations resolve at runtime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .domain import RegisteredDomain
    from .wallet import WalletTransaction

class User(Base):
    """User accounts with language preference and wallet balance"""

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    telegram_id = Column(BIGINT, primary_key=True, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10), default="en")  # en, fr
    balance_usd = Column(DECIMAL(10, 2), default=0.00)
    technical_email = Column(
        String(255), nullable=True
    )  # Store user's technical email once
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships - using string references to avoid circular imports
    domains = relationship(
        "RegisteredDomain", back_populates="user", cascade="all, delete-orphan",
        lazy="select"  # Explicit lazy loading for performance
    )
    wallet_transactions = relationship(
        "WalletTransaction", back_populates="user", cascade="all, delete-orphan",
        lazy="select"
    )
    user_states = relationship(
        "UserState", back_populates="user", cascade="all, delete-orphan",
        lazy="select"
    )
    
    # External service integrations
    email_integrations = relationship(
        "BrevoIntegration", back_populates="user", cascade="all, delete-orphan",
        lazy="select"
    )
    telegram_integrations = relationship(
        "TelegramIntegration", back_populates="user", cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

    @property 
    def display_name(self) -> str:
        """Get user's display name"""
        if self.username:
            return f"@{self.username}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return f"User {self.telegram_id}"

    def has_sufficient_balance(self, amount: Decimal) -> bool:
        """Check if user has sufficient balance for a transaction"""
        return self.balance_usd >= amount

    def add_balance(self, amount: Decimal) -> None:
        """Add amount to user's balance"""
        self.balance_usd += amount

    def deduct_balance(self, amount: Decimal) -> bool:
        """Deduct amount from user's balance if sufficient funds available"""
        if self.has_sufficient_balance(amount):
            self.balance_usd -= amount
            return True
        return False
    
    def get_active_domains_count(self) -> int:
        """Get count of active domains for this user"""
        return len([d for d in self.domains if d.is_active]) if self.domains else 0
    
    def get_total_spent(self) -> Decimal:
        """Calculate total amount spent by user"""
        if not self.domains:
            return Decimal("0.00")
        return sum(d.price_paid for d in self.domains if d.price_paid) or Decimal("0.00")
    
    def is_premium_user(self) -> bool:
        """Check if user qualifies as premium (3+ domains or $100+ spent)"""
        return self.get_active_domains_count() >= 3 or self.get_total_spent() >= Decimal("100.00")


class UserState(Base):
    """User conversation state management"""

    __tablename__ = "user_states"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, index=True)
    current_state = Column(String(100), default="ready")
    state_data = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_states")

    def __repr__(self):
        return f"<UserState(telegram_id={self.telegram_id}, state={self.current_state})>"

    def set_state(self, state: str, data: dict = None) -> None:
        """Set user's current state with optional data"""
        self.current_state = state
        if data:
            self.state_data = data

    def get_state_data(self, key: str, default=None):
        """Get specific data from state_data"""
        return self.state_data.get(key, default) if self.state_data else default

    def update_state_data(self, key: str, value) -> None:
        """Update specific key in state_data"""
        if not self.state_data:
            self.state_data = {}
        self.state_data[key] = value