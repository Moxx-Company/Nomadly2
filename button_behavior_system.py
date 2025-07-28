#!/usr/bin/env python3
"""
Button Behavior System
Enhanced button responsiveness and interaction handling
"""

import asyncio
import time
import logging
from typing import Dict, Any, Set, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ButtonBehaviorManager:
    """Manages button behavior and responsiveness"""
    
    def __init__(self):
        self.click_history: Dict[str, datetime] = {}
        self.processing_states: Set[str] = set()
        self.duplicate_click_threshold = 2.0  # seconds
    
    def prevent_duplicate_clicks(self, user_id: int, callback_data: str) -> bool:
        """Prevent duplicate button clicks within threshold"""
        click_key = f"{user_id}_{callback_data}"
        now = datetime.now()
        
        if click_key in self.click_history:
            last_click = self.click_history[click_key]
            time_diff = (now - last_click).total_seconds()
            
            if time_diff < self.duplicate_click_threshold:
                logger.warning(f"Duplicate click prevented for {click_key}")
                return False  # Prevent duplicate
        
        self.click_history[click_key] = now
        return True  # Allow click
    
    def is_processing(self, user_id: int, operation: str) -> bool:
        """Check if user operation is currently processing"""
        key = f"{user_id}_{operation}"
        return key in self.processing_states
    
    def start_processing(self, user_id: int, operation: str):
        """Mark operation as processing"""
        key = f"{user_id}_{operation}"
        self.processing_states.add(key)
        logger.info(f"Started processing: {key}")
    
    def finish_processing(self, user_id: int, operation: str):
        """Mark operation as complete"""
        key = f"{user_id}_{operation}"
        self.processing_states.discard(key)
        logger.info(f"Finished processing: {key}")
    
    def get_button_state_validation(self, user_id: int, callback_data: str) -> Dict[str, Any]:
        """Validate button state and provide feedback"""
        operation_type = self._extract_operation_type(callback_data)
        
        # Check for duplicate clicks
        if not self.prevent_duplicate_clicks(user_id, callback_data):
            return {
                'valid': False,
                'reason': 'duplicate_click',
                'message': 'Please wait, your request is being processed...',
                'retry_after': self.duplicate_click_threshold
            }
        
        # Check for ongoing operations
        if self.is_processing(user_id, operation_type):
            return {
                'valid': False,
                'reason': 'operation_in_progress',
                'message': f'Your {operation_type} request is already being processed...',
                'retry_after': 5.0
            }
        
        return {
            'valid': True,
            'reason': 'ready',
            'message': 'Processing your request...',
            'operation_type': operation_type
        }
    
    def _extract_operation_type(self, callback_data: str) -> str:
        """Extract operation type from callback data"""
        if callback_data.startswith('pay_'):
            return 'payment'
        elif callback_data.startswith('dns_'):
            return 'dns'
        elif callback_data.startswith('register_'):
            return 'registration'
        elif callback_data.startswith('wallet'):
            return 'wallet'
        elif callback_data.startswith('crypto_'):
            return 'crypto'
        else:
            return 'general'
    
    def cleanup_old_entries(self, max_age_minutes: int = 10):
        """Clean up old click history entries"""
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
        old_keys = [
            key for key, timestamp in self.click_history.items() 
            if timestamp < cutoff
        ]
        
        for key in old_keys:
            del self.click_history[key]
        
        if old_keys:
            logger.info(f"Cleaned up {len(old_keys)} old click history entries")

# Global button behavior manager instance
button_manager = ButtonBehaviorManager()

async def validate_button_interaction(user_id: int, callback_data: str) -> Dict[str, Any]:
    """Validate button interaction before processing"""
    return button_manager.get_button_state_validation(user_id, callback_data)

def mark_operation_start(user_id: int, operation: str):
    """Mark operation as started"""
    button_manager.start_processing(user_id, operation)

def mark_operation_complete(user_id: int, operation: str):
    """Mark operation as completed"""
    button_manager.finish_processing(user_id, operation)

# Cleanup task
async def periodic_cleanup():
    """Periodic cleanup of old entries"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        button_manager.cleanup_old_entries()

# Test function
async def test_button_behavior():
    """Test button behavior system"""
    print("🔘 TESTING BUTTON BEHAVIOR SYSTEM")
    print("=" * 40)
    
    # Test duplicate click prevention
    user_id = 12345
    callback = "pay_crypto_eth_example.com"
    
    # First click should be valid
    result1 = await validate_button_interaction(user_id, callback)
    print(f"First click: {result1['valid']} - {result1['reason']}")
    
    # Immediate second click should be blocked
    result2 = await validate_button_interaction(user_id, callback)
    print(f"Duplicate click: {result2['valid']} - {result2['reason']}")
    
    # Test operation tracking
    mark_operation_start(user_id, 'payment')
    is_processing = button_manager.is_processing(user_id, 'payment')
    print(f"Operation tracking: {'✅' if is_processing else '❌'}")
    
    mark_operation_complete(user_id, 'payment')
    is_complete = not button_manager.is_processing(user_id, 'payment')
    print(f"Operation completion: {'✅' if is_complete else '❌'}")
    
    # Test operation type extraction
    operation_type = button_manager._extract_operation_type("dns_create_a_example.com")
    print(f"Operation type extraction: {'✅' if operation_type == 'dns' else '❌'}")
    
    print("\n✅ Button behavior system tests completed")

if __name__ == "__main__":
    asyncio.run(test_button_behavior())