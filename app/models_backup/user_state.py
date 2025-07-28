"""
User State model for Nomadly3 Domain Registration Bot
Manages conversation state and temporary data
"""

from sqlalchemy import Column, Integer, String, DateTime, BIGINT, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from ..core.database import Base

class UserState(Base):
    """User conversation state management"""

    __tablename__ = "user_states"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    state = Column(String(100), nullable=False)
    data = Column(JSONB, default={})
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_states")

    def __repr__(self):
        return f"<UserState(telegram_id={self.telegram_id}, state={self.state})>"

    @property
    def is_expired(self) -> bool:
        """Check if state has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def set_data(self, key: str, value: Any) -> None:
        """Set a value in the state data"""
        if not self.data:
            self.data = {}
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get a value from the state data"""
        if not self.data:
            return default
        return self.data.get(key, default)

    def clear_data(self) -> None:
        """Clear all state data"""
        self.data = {}

    def extend_expiry(self, hours: int = 24) -> None:
        """Extend state expiry by specified hours"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)

    def is_in_states(self, *states: str) -> bool:
        """Check if current state is in given list of states"""
        return self.state in states