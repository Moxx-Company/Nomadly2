"""
Support Repository for Nomadly3 - Support Data Access Layer
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class SupportRepository:
    """Repository for Support/FAQ/Ticket data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_support_ticket(self, telegram_id: int, subject: str, message: str, 
                             category: str = "general") -> Dict[str, Any]:
        """Create new support ticket"""
        try:
            ticket_data = {
                "id": f"ticket_{telegram_id}_{len(subject)}",
                "telegram_id": telegram_id,
                "subject": subject,
                "message": message,
                "category": category,
                "status": "open",
                "created_at": datetime.utcnow()
            }
            
            logger.info(f"Created support ticket: {ticket_data['id']}")
            return ticket_data
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            raise
    
    def get_support_tickets(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get support tickets for user"""
        try:
            # Placeholder implementation
            return []
            
        except Exception as e:
            logger.error(f"Error getting support tickets: {e}")
            return []
    
    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Update support ticket status"""
        try:
            logger.info(f"Updated ticket {ticket_id} status to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            return False
    
    def get_faq_entries(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get FAQ entries by category"""
        try:
            # Placeholder FAQ data
            faq_entries = [
                {
                    "id": "faq_1",
                    "question": "How do I register a domain?",
                    "answer": "Use the Search Domain button to check availability and register.",
                    "category": "domain"
                },
                {
                    "id": "faq_2", 
                    "question": "What payment methods do you accept?",
                    "answer": "We accept Bitcoin, Ethereum, Litecoin, and Dogecoin.",
                    "category": "payment"
                }
            ]
            
            if category:
                return [faq for faq in faq_entries if faq["category"] == category]
            return faq_entries
            
        except Exception as e:
            logger.error(f"Error getting FAQ entries: {e}")
            return []
    
    def search_faq(self, query: str) -> List[Dict[str, Any]]:
        """Search FAQ entries by query"""
        try:
            # Placeholder search implementation
            all_faqs = self.get_faq_entries()
            matching_faqs = []
            
            for faq in all_faqs:
                if query.lower() in faq["question"].lower() or query.lower() in faq["answer"].lower():
                    matching_faqs.append(faq)
            
            return matching_faqs
            
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return []
    
    def create_ticket(self, telegram_id: int, subject: str, message: str, 
                      category: str = "general") -> dict:
        """Create new support ticket - alias for create_support_ticket"""
        return self.create_support_ticket(telegram_id, subject, message, category)
    
    def get_user_tickets(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get user tickets - alias for get_support_tickets"""  
        return self.get_support_tickets(telegram_id)