"""
Support Service for Nomadly3 - Customer Support Business Logic
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SupportService:
    """Service for managing customer support operations"""
    
    def __init__(self, db_session, support_repo=None):
        """Initialize support service with dependencies"""
        self.db = db_session
        self.support_repo = support_repo
        
        # FAQ categories and common questions
        self.faq_data = {
            "domain": [
                {
                    "question": "How do I register a domain?",
                    "answer": "Use the 'Search Domain' button in the main menu to check availability and register domains.",
                    "category": "domain"
                },
                {
                    "question": "What TLDs do you support?",
                    "answer": "We support .com, .net, .org, .info, .biz, .me, .co, .io and many country TLDs.",
                    "category": "domain"
                }
            ],
            "payment": [
                {
                    "question": "What payment methods do you accept?",
                    "answer": "We accept Bitcoin (BTC), Ethereum (ETH), Litecoin (LTC), and Dogecoin (DOGE).",
                    "category": "payment"
                },
                {
                    "question": "How long do payment confirmations take?",
                    "answer": "BTC: 1 confirmation, ETH: 12 confirmations, LTC: 6 confirmations, DOGE: 20 confirmations.",
                    "category": "payment"
                }
            ],
            "dns": [
                {
                    "question": "How do I manage DNS records?",
                    "answer": "Use the 'Manage DNS' button from your domain list to add, edit, or delete DNS records.",
                    "category": "dns"
                },
                {
                    "question": "What DNS record types are supported?",
                    "answer": "We support A, AAAA, CNAME, MX, TXT, NS, and SRV records.",
                    "category": "dns"
                }
            ]
        }
    
    async def get_faq_by_category(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get FAQ entries by category"""
        try:
            if category and category in self.faq_data:
                return self.faq_data[category]
            else:
                # Return all FAQs if no category specified
                all_faqs = []
                for cat_faqs in self.faq_data.values():
                    all_faqs.extend(cat_faqs)
                return all_faqs
                
        except Exception as e:
            logger.error(f"Error getting FAQs: {e}")
            return []
    
    async def create_support_ticket(self, telegram_id: int, subject: str, 
                                  message: str, category: str = "general") -> Dict[str, Any]:
        """Create a new support ticket"""
        try:
            ticket = {
                "id": f"ticket_{uuid.uuid4().hex[:8]}",
                "telegram_id": telegram_id,
                "subject": subject,
                "message": message,
                "category": category,
                "status": "open",
                "priority": "normal",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Here you would normally save to database via repository
            logger.info(f"Created support ticket: {ticket['id']} for user {telegram_id}")
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            raise Exception(f"Could not create support ticket: {str(e)}")
    
    async def get_support_tickets(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get support tickets for user"""
        try:
            # Placeholder - would normally query database
            return []
            
        except Exception as e:
            logger.error(f"Error getting support tickets: {e}")
            return []
    
    async def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Update support ticket status"""
        try:
            # Placeholder - would normally update database
            logger.info(f"Updated ticket {ticket_id} status to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            return False
    
    def get_contact_info(self) -> Dict[str, Any]:
        """Get contact information"""
        return {
            "telegram_support": "@nomadly_support",
            "email_support": "support@nomadly.offshore",
            "response_time": "24 hours",
            "available_languages": ["English", "French"],
            "business_hours": "24/7 offshore operations"
        }