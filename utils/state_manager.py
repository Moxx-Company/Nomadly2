"""
Advanced State Management System
Handles complex user workflows and session persistence
Based on Complete URL Management Mystery architecture
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StateManager:
    """Manages user state and workflow persistence"""

    def __init__(self, database_manager):
        self.db_manager = database_manager

    def set_state(
        self, telegram_id: int, state: str, temp_data: Dict[str, Any] = None
    ) -> bool:
        """Set user state with optional temporary data"""
        try:
            return self.db_manager.update_user_state(telegram_id, state, temp_data)
        except Exception as e:
            logger.error(f"Error setting state for {telegram_id}: {e}")
            return False

    def get_state(self, telegram_id: int) -> Tuple[Optional[str], Dict[str, Any]]:
        """Get user state and temporary data"""
        try:
            return self.db_manager.get_user_state(telegram_id)
        except Exception as e:
            logger.error(f"Error getting state for {telegram_id}: {e}")
            return None, {}

    def clear_state(self, telegram_id: int) -> bool:
        """Clear user state"""
        try:
            return self.db_manager.clear_user_state(telegram_id)
        except Exception as e:
            logger.error(f"Error clearing state for {telegram_id}: {e}")
            return False

    def update_temp_data(self, telegram_id: int, key: str, value: Any) -> bool:
        """Update specific key in temporary data"""
        try:
            state, temp_data = self.get_state(telegram_id)
            if temp_data is None:
                temp_data = {}

            temp_data[key] = value
            return self.set_state(telegram_id, state, temp_data)
        except Exception as e:
            logger.error(f"Error updating temp data for {telegram_id}: {e}")
            return False

    def get_temp_data(self, telegram_id: int, key: str, default=None) -> Any:
        """Get specific value from temporary data"""
        try:
            _, temp_data = self.get_state(telegram_id)
            return temp_data.get(key, default) if temp_data else default
        except Exception as e:
            logger.error(f"Error getting temp data for {telegram_id}: {e}")
            return default

    def is_valid_session(self, telegram_id: int, max_age_minutes: int = 30) -> bool:
        """Check if user session is still valid"""
        try:
            state, temp_data = self.get_state(telegram_id)
            if not state:
                return False

            # Check session timestamp if available
            session_start = temp_data.get("session_start") if temp_data else None
            if session_start:
                start_time = datetime.fromisoformat(session_start)
                if datetime.now() - start_time > timedelta(minutes=max_age_minutes):
                    # Clear expired session
                    self.clear_state(telegram_id)
                    return False

            return True
        except Exception as e:
            logger.error(f"Error checking session validity for {telegram_id}: {e}")
            return False

    def start_workflow(
        self, telegram_id: int, workflow_name: str, initial_data: Dict[str, Any] = None
    ) -> bool:
        """Start a new workflow with initial data"""
        try:
            workflow_data = {
                "workflow": workflow_name,
                "session_start": datetime.now().isoformat(),
                "step": 1,
            }

            if initial_data:
                workflow_data.update(initial_data)

            return self.set_state(
                telegram_id, f"workflow_{workflow_name}", workflow_data
            )
        except Exception as e:
            logger.error(
                f"Error starting workflow {workflow_name} for {telegram_id}: {e}"
            )
            return False

    def advance_workflow(
        self, telegram_id: int, next_step_data: Dict[str, Any] = None
    ) -> bool:
        """Advance to next step in current workflow"""
        try:
            state, temp_data = self.get_state(telegram_id)
            if not state or not temp_data:
                return False

            # Increment step
            current_step = temp_data.get("step", 1)
            temp_data["step"] = current_step + 1

            # Update with new step data
            if next_step_data:
                temp_data.update(next_step_data)

            return self.set_state(telegram_id, state, temp_data)
        except Exception as e:
            logger.error(f"Error advancing workflow for {telegram_id}: {e}")
            return False

    def get_workflow_step(self, telegram_id: int) -> int:
        """Get current workflow step"""
        try:
            _, temp_data = self.get_state(telegram_id)
            return temp_data.get("step", 1) if temp_data else 1
        except Exception as e:
            logger.error(f"Error getting workflow step for {telegram_id}: {e}")
            return 1

    def is_in_workflow(self, telegram_id: int, workflow_name: str) -> bool:
        """Check if user is in specific workflow"""
        try:
            state, temp_data = self.get_state(telegram_id)
            if not state or not temp_data:
                return False

            return temp_data.get("workflow") == workflow_name
        except Exception as e:
            logger.error(f"Error checking workflow for {telegram_id}: {e}")
            return False

    # Specific workflow states for URL Management Mystery compatibility
    def set_url_edit_state(
        self, telegram_id: int, url_id: int, current_url: str
    ) -> bool:
        """Set state for URL editing workflow"""
        return self.set_state(
            telegram_id,
            f"awaiting_url_edit_{url_id}",
            {
                "url_id": url_id,
                "current_url": current_url,
                "session_start": datetime.now().isoformat(),
            },
        )

    def set_domain_selection_state(
        self, telegram_id: int, service_type: str, service_data: Dict[str, Any]
    ) -> bool:
        """Set state for domain selection workflow"""
        return self.set_state(
            telegram_id,
            f"awaiting_domain_selection_{service_type}",
            {
                "service_type": service_type,
                "service_data": service_data,
                "session_start": datetime.now().isoformat(),
            },
        )

    def set_payment_state(self, telegram_id: int, payment_data: Dict[str, Any]) -> bool:
        """Set state for payment processing"""
        return self.set_state(
            telegram_id,
            "awaiting_payment_confirmation",
            {"payment_data": payment_data, "session_start": datetime.now().isoformat()},
        )

    def set_input_state(
        self, telegram_id: int, input_type: str, context_data: Dict[str, Any] = None
    ) -> bool:
        """Set state for awaiting user input"""
        temp_data = {
            "input_type": input_type,
            "session_start": datetime.now().isoformat(),
        }

        if context_data:
            temp_data.update(context_data)

        return self.set_state(telegram_id, f"awaiting_{input_type}", temp_data)

    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired user sessions"""
        # This would be implemented in database_manager for bulk cleanup
        # For now, just log the request
        logger.info(
            f"Session cleanup requested for sessions older than {max_age_hours} hours"
        )
        return 0
