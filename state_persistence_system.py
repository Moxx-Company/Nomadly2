#!/usr/bin/env python3
"""
State Persistence System
Enhanced user state management and session handling
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class UserState(Enum):
    """User state types"""
    IDLE = "idle"
    DOMAIN_SEARCH = "domain_search"
    DOMAIN_REGISTRATION = "domain_registration" 
    DNS_CONFIGURATION = "dns_configuration"
    PAYMENT_PROCESSING = "payment_processing"
    WALLET_OPERATIONS = "wallet_operations"
    NAMESERVER_SETUP = "nameserver_setup"
    AWAITING_INPUT = "awaiting_input"

@dataclass
class UserSession:
    """User session data"""
    user_id: int
    state: UserState = UserState.IDLE
    data: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    expiry_date: datetime = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.expiry_date is None:
            self.expiry_date = datetime.now() + timedelta(hours=24)
    
    def update_state(self, new_state: UserState, data: Optional[Dict[str, Any]] = None):
        """Update user state and data"""
        self.state = new_state
        self.updated_at = datetime.now()
        if data:
            self.data.update(data)
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expiry_date
    
    def extend_session(self, hours: int = 24):
        """Extend session expiration"""
        self.expiry_date = datetime.now() + timedelta(hours=hours)
        self.updated_at = datetime.now()

class StatePersistenceManager:
    """Manages user state persistence and session handling"""
    
    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}
        self.state_validators = {
            UserState.DOMAIN_SEARCH: self._validate_domain_search_data,
            UserState.DOMAIN_REGISTRATION: self._validate_domain_registration_data,
            UserState.DNS_CONFIGURATION: self._validate_dns_configuration_data,
            UserState.PAYMENT_PROCESSING: self._validate_payment_processing_data,
            UserState.WALLET_OPERATIONS: self._validate_wallet_operations_data,
            UserState.NAMESERVER_SETUP: self._validate_nameserver_setup_data,
        }
    
    def get_user_session(self, user_id: int) -> UserSession:
        """Get or create user session"""
        if user_id not in self.sessions or self.sessions[user_id].is_expired():
            self.sessions[user_id] = UserSession(user_id=user_id)
        
        return self.sessions[user_id]
    
    def update_user_state(self, user_id: int, state: UserState, data: Optional[Dict[str, Any]] = None) -> bool:
        """Update user state with validation"""
        session = self.get_user_session(user_id)
        
        # Validate state data if validator exists
        if state in self.state_validators and data:
            validation_result = self.state_validators[state](data)
            if not validation_result['valid']:
                logger.warning(f"Invalid state data for user {user_id}, state {state}: {validation_result['errors']}")
                return False
        
        # Update session
        session.update_state(state, data)
        logger.info(f"Updated user {user_id} state to {state.value}")
        return True
    
    def get_user_state(self, user_id: int) -> UserState:
        """Get current user state"""
        session = self.get_user_session(user_id)
        return session.state
    
    def get_user_data(self, user_id: int, key: Optional[str] = None) -> Any:
        """Get user session data"""
        session = self.get_user_session(user_id)
        
        if key:
            return session.data.get(key)
        return session.data
    
    def clear_user_state(self, user_id: int):
        """Clear user state and return to idle"""
        session = self.get_user_session(user_id)
        session.update_state(UserState.IDLE, {})
        logger.info(f"Cleared state for user {user_id}")
    
    def is_user_in_state(self, user_id: int, state: UserState) -> bool:
        """Check if user is in specific state"""
        return self.get_user_state(user_id) == state
    
    def validate_state_transition(self, user_id: int, from_state: UserState, to_state: UserState) -> bool:
        """Validate state transition is allowed"""
        current_state = self.get_user_state(user_id)
        
        if current_state != from_state:
            logger.warning(f"Invalid state transition for user {user_id}: expected {from_state}, got {current_state}")
            return False
        
        # Define allowed transitions
        allowed_transitions = {
            UserState.IDLE: [UserState.DOMAIN_SEARCH, UserState.WALLET_OPERATIONS],
            UserState.DOMAIN_SEARCH: [UserState.DOMAIN_REGISTRATION, UserState.IDLE],
            UserState.DOMAIN_REGISTRATION: [UserState.DNS_CONFIGURATION, UserState.PAYMENT_PROCESSING, UserState.IDLE],
            UserState.DNS_CONFIGURATION: [UserState.NAMESERVER_SETUP, UserState.IDLE],
            UserState.PAYMENT_PROCESSING: [UserState.IDLE, UserState.DOMAIN_REGISTRATION],
            UserState.WALLET_OPERATIONS: [UserState.IDLE, UserState.PAYMENT_PROCESSING],
            UserState.NAMESERVER_SETUP: [UserState.IDLE, UserState.DNS_CONFIGURATION],
            UserState.AWAITING_INPUT: [UserState.IDLE]  # Can transition to any state
        }
        
        return to_state in allowed_transitions.get(current_state, [])
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for user_id in expired_users:
            del self.sessions[user_id]
        
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired sessions")
    
    # Validation methods for different state types
    def _validate_domain_search_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate domain search state data"""
        required_fields = []  # Domain search can start without specific data
        errors = []
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_domain_registration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate domain registration state data"""
        required_fields = ['domain_name']
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if 'domain_name' in data and not isinstance(data['domain_name'], str):
            errors.append("domain_name must be a string")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_dns_configuration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate DNS configuration state data"""
        required_fields = ['domain_name', 'nameserver_mode']
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        valid_nameserver_modes = ['cloudflare', 'custom', 'registrar']
        if 'nameserver_mode' in data and data['nameserver_mode'] not in valid_nameserver_modes:
            errors.append(f"Invalid nameserver_mode, must be one of: {valid_nameserver_modes}")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_payment_processing_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment processing state data"""
        required_fields = ['amount', 'currency']
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if 'amount' in data and not isinstance(data['amount'], (int, float)):
            errors.append("amount must be a number")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_wallet_operations_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate wallet operations state data"""
        errors = []  # Wallet operations have flexible data requirements
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _validate_nameserver_setup_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate nameserver setup state data"""
        required_fields = ['domain_name', 'nameservers']
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if 'nameservers' in data and not isinstance(data['nameservers'], list):
            errors.append("nameservers must be a list")
        
        return {'valid': len(errors) == 0, 'errors': errors}

# Global state manager instance
state_manager = StatePersistenceManager()

# Convenience functions
def get_user_state(user_id: int) -> UserState:
    """Get user's current state"""
    return state_manager.get_user_state(user_id)

def set_user_state(user_id: int, state: UserState, data: Optional[Dict[str, Any]] = None) -> bool:
    """Set user's state with optional data"""
    return state_manager.update_user_state(user_id, state, data)

def get_user_data(user_id: int, key: Optional[str] = None) -> Any:
    """Get user's session data"""
    return state_manager.get_user_data(user_id, key)

def clear_user_state(user_id: int):
    """Clear user's state"""
    state_manager.clear_user_state(user_id)

def is_user_in_state(user_id: int, state: UserState) -> bool:
    """Check if user is in specific state"""
    return state_manager.is_user_in_state(user_id, state)

# Test function
async def test_state_persistence():
    """Test state persistence system"""
    print("💾 TESTING STATE PERSISTENCE SYSTEM")
    print("=" * 40)
    
    user_id = 12345
    
    # Test initial state
    initial_state = get_user_state(user_id)
    print(f"Initial state: {initial_state.value} {'✅' if initial_state == UserState.IDLE else '❌'}")
    
    # Test state update
    success = set_user_state(user_id, UserState.DOMAIN_SEARCH, {'query': 'example.com'})
    print(f"State update: {'✅' if success else '❌'}")
    
    # Test state retrieval
    current_state = get_user_state(user_id)
    print(f"State retrieval: {'✅' if current_state == UserState.DOMAIN_SEARCH else '❌'}")
    
    # Test data retrieval
    query_data = get_user_data(user_id, 'query')
    print(f"Data retrieval: {'✅' if query_data == 'example.com' else '❌'}")
    
    # Test validation
    validation_success = set_user_state(user_id, UserState.DOMAIN_REGISTRATION, {'domain_name': 'test.com'})
    print(f"Validation success: {'✅' if validation_success else '❌'}")
    
    validation_failure = set_user_state(user_id, UserState.DOMAIN_REGISTRATION, {'invalid': 'data'})
    print(f"Validation failure: {'✅' if not validation_failure else '❌'}")
    
    # Test state clearing
    clear_user_state(user_id)
    final_state = get_user_state(user_id)
    print(f"State clearing: {'✅' if final_state == UserState.IDLE else '❌'}")
    
    print("\n✅ State persistence system tests completed")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_state_persistence())