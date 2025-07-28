#!/usr/bin/env python3
"""
Missing Methods Implementation for Complete UI-Backend Flow Coverage
Implements all missing repository methods identified in the validation
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MissingMethodsImplementation:
    """Implements missing methods for complete UI-backend coverage"""
    
    def __init__(self):
        self.fixes_applied = []
    
    def add_user_repository_methods(self):
        """Add missing methods to UserRepository"""
        user_repo_additions = '''
    def update_user_language(self, telegram_id: int, language_code: str) -> bool:
        """Update user's language preference"""
        try:
            user = self.session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.language_code = language_code
                user.updated_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            self.session.rollback()
            return False
    
    def get_dashboard_data(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user"""
        try:
            from sqlalchemy.orm import joinedload
            from sqlalchemy import func
            
            # Get user with related data pre-loaded
            user = self.session.query(User)\\
                .options(joinedload(User.domains))\\
                .filter(User.telegram_id == telegram_id)\\
                .first()
            
            if not user:
                return {}
            
            # Get domain statistics
            total_domains = self.session.query(func.count(RegisteredDomain.id))\\
                .filter(RegisteredDomain.telegram_id == telegram_id)\\
                .scalar() or 0
            
            active_domains = self.session.query(func.count(RegisteredDomain.id))\\
                .filter(
                    RegisteredDomain.telegram_id == telegram_id,
                    RegisteredDomain.expires_at > datetime.utcnow()
                )\\
                .scalar() or 0
            
            # Get recent transactions
            recent_transactions = self.session.query(WalletTransaction)\\
                .filter(WalletTransaction.telegram_id == telegram_id)\\
                .order_by(WalletTransaction.created_at.desc())\\
                .limit(5)\\
                .all()
            
            return {
                "user": user,
                "total_domains": total_domains,
                "active_domains": active_domains,
                "expiring_soon": active_domains - total_domains if active_domains > total_domains else 0,
                "wallet_balance": float(user.balance_usd) if user.balance_usd else 0.0,
                "recent_transactions": recent_transactions,
                "last_activity": user.updated_at or user.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}'''
        
        return user_repo_additions
    
    def add_domain_repository_methods(self):
        """Add missing methods to DomainRepository"""
        domain_repo_additions = '''
    def get_user_domains_with_dns(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get user domains with DNS record counts and metadata"""
        try:
            from sqlalchemy.orm import joinedload
            from sqlalchemy import func
            
            # Query domains with DNS record counts
            domains_with_dns = self.session.query(
                RegisteredDomain,
                func.count(DNSRecord.id).label('dns_count')
            )\\
            .outerjoin(DNSRecord, RegisteredDomain.id == DNSRecord.domain_id)\\
            .filter(RegisteredDomain.telegram_id == telegram_id)\\
            .group_by(RegisteredDomain.id)\\
            .all()
            
            result = []
            for domain, dns_count in domains_with_dns:
                # Calculate days until expiry
                days_until_expiry = None
                if domain.expires_at:
                    delta = domain.expires_at - datetime.utcnow()
                    days_until_expiry = delta.days if delta.days > 0 else 0
                
                domain_data = {
                    "domain": domain,
                    "dns_record_count": dns_count or 0,
                    "days_until_expiry": days_until_expiry,
                    "is_active": domain.expires_at > datetime.utcnow() if domain.expires_at else False,
                    "cloudflare_zone_id": domain.cloudflare_zone_id,
                    "openprovider_domain_id": domain.openprovider_domain_id,
                    "nameservers": domain.nameservers
                }
                result.append(domain_data)
            
            # Sort by expiry date (soonest first) then by domain name
            result.sort(key=lambda x: (
                x["days_until_expiry"] if x["days_until_expiry"] is not None else 9999,
                x["domain"].domain_name
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user domains with DNS: {e}")
            return []
    
    def check_existing_domain(self, domain_name: str) -> Optional[RegisteredDomain]:
        """Check if domain already exists in our database"""
        try:
            return self.session.query(RegisteredDomain)\\
                .filter(RegisteredDomain.domain_name == domain_name)\\
                .first()
        except Exception as e:
            logger.error(f"Error checking existing domain: {e}")
            return None
    
    def get_domains_expiring_soon(self, days: int = 30) -> List[RegisteredDomain]:
        """Get domains expiring within specified days"""
        try:
            from sqlalchemy import and_
            from datetime import timedelta
            
            expiry_threshold = datetime.utcnow() + timedelta(days=days)
            
            return self.session.query(RegisteredDomain)\\
                .filter(and_(
                    RegisteredDomain.expires_at <= expiry_threshold,
                    RegisteredDomain.expires_at > datetime.utcnow()
                ))\\
                .order_by(RegisteredDomain.expires_at)\\
                .all()
                
        except Exception as e:
            logger.error(f"Error getting domains expiring soon: {e}")
            return []'''
        
        return domain_repo_additions
    
    def create_support_repository(self):
        """Create missing SupportRepository class"""
        support_repo_code = '''"""
Support Repository for ticket and FAQ management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime
import logging

from ..fresh_database import SupportTicket, User

logger = logging.getLogger(__name__)

class SupportRepository:
    """Repository for support ticket management"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_ticket(self, telegram_id: int, subject: str, message: str, priority: str = "medium") -> Optional[SupportTicket]:
        """Create a new support ticket"""
        try:
            ticket = SupportTicket(
                telegram_id=telegram_id,
                subject=subject,
                message=message,
                priority=priority,
                status="open",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(ticket)
            self.session.commit()
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            self.session.rollback()
            return None
    
    def get_user_tickets(self, telegram_id: int, limit: int = 10) -> List[SupportTicket]:
        """Get user's support tickets"""
        try:
            return self.session.query(SupportTicket)\\
                .filter(SupportTicket.telegram_id == telegram_id)\\
                .order_by(desc(SupportTicket.updated_at))\\
                .limit(limit)\\
                .all()
        except Exception as e:
            logger.error(f"Error getting user tickets: {e}")
            return []
    
    def update_ticket_status(self, ticket_id: int, status: str, admin_response: str = None) -> bool:
        """Update ticket status and add admin response"""
        try:
            ticket = self.session.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
            if ticket:
                ticket.status = status
                ticket.updated_at = datetime.utcnow()
                if admin_response:
                    ticket.admin_response = admin_response
                self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating ticket status: {e}")
            self.session.rollback()
            return False
    
    def get_open_tickets(self) -> List[SupportTicket]:
        """Get all open support tickets for admin"""
        try:
            return self.session.query(SupportTicket)\\
                .filter(SupportTicket.status.in_(["open", "in_progress"]))\\
                .order_by(desc(SupportTicket.created_at))\\
                .all()
        except Exception as e:
            logger.error(f"Error getting open tickets: {e}")
            return []'''
        
        return support_repo_code
    
    def create_support_service(self):
        """Create missing SupportService class"""
        support_service_code = '''"""
Support Service for business logic around tickets and FAQs
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..repositories.support_repo import SupportRepository
from ..repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

class SupportService:
    """Business logic for support system"""
    
    def __init__(self, support_repo: SupportRepository, user_repo: UserRepository):
        self.support_repo = support_repo
        self.user_repo = user_repo
    
    def create_support_ticket(self, telegram_id: int, subject: str, message: str, priority: str = "medium") -> Dict[str, Any]:
        """Create support ticket with validation and notifications"""
        try:
            # Validate user exists
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Validate input
            if not subject or len(subject.strip()) < 5:
                return {"success": False, "error": "Subject must be at least 5 characters"}
            
            if not message or len(message.strip()) < 10:
                return {"success": False, "error": "Message must be at least 10 characters"}
            
            # Create ticket
            ticket = self.support_repo.create_ticket(telegram_id, subject.strip(), message.strip(), priority)
            
            if ticket:
                # TODO: Send notification email to support team
                # TODO: Send confirmation to user
                
                return {
                    "success": True,
                    "ticket_id": ticket.id,
                    "ticket_number": f"SUPP-{ticket.id:06d}",
                    "estimated_response": "24 hours"
                }
            else:
                return {"success": False, "error": "Failed to create ticket"}
                
        except Exception as e:
            logger.error(f"Error in create_support_ticket: {e}")
            return {"success": False, "error": "Internal error occurred"}
    
    def get_user_support_history(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's support ticket history with statistics"""
        try:
            tickets = self.support_repo.get_user_tickets(telegram_id)
            
            # Calculate statistics
            total_tickets = len(tickets)
            open_tickets = len([t for t in tickets if t.status in ["open", "in_progress"]])
            closed_tickets = len([t for t in tickets if t.status == "closed"])
            
            return {
                "tickets": tickets,
                "statistics": {
                    "total": total_tickets,
                    "open": open_tickets,
                    "closed": closed_tickets
                },
                "has_open_tickets": open_tickets > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user support history: {e}")
            return {"tickets": [], "statistics": {"total": 0, "open": 0, "closed": 0}, "has_open_tickets": False}
    
    def get_faq_responses(self, query: str = None) -> List[Dict[str, str]]:
        """Get FAQ responses (static for now, could be database-driven later)"""
        faqs = [
            {
                "question": "How do I register a domain?",
                "answer": "Use the 'Search Domain' button in the main menu. Enter your desired domain name, select DNS options, and complete payment with cryptocurrency.",
                "category": "domains"
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept Bitcoin (BTC), Ethereum (ETH), Litecoin (LTC), and Dogecoin (DOGE). All payments are processed securely through our cryptocurrency gateway.",
                "category": "payments"
            },
            {
                "question": "How do I manage DNS records?",
                "answer": "Go to 'My Domains', select your domain, then 'Manage DNS'. You can add, edit, or delete A, AAAA, CNAME, MX, and TXT records.",
                "category": "dns"
            },
            {
                "question": "What is the refund policy?",
                "answer": "Domain registrations are non-refundable once processed. However, overpayments are automatically credited to your wallet balance.",
                "category": "billing"
            },
            {
                "question": "How do I change nameservers?",
                "answer": "In 'My Domains', select your domain and click 'Update Nameservers'. You can switch between Cloudflare managed DNS and custom nameservers.",
                "category": "dns"
            }
        ]
        
        if query:
            # Simple search in questions and answers
            query_lower = query.lower()
            faqs = [faq for faq in faqs if query_lower in faq["question"].lower() or query_lower in faq["answer"].lower()]
        
        return faqs'''
        
        return support_service_code
    
    def apply_all_fixes(self):
        """Apply all missing method implementations"""
        logger.info("🔧 Applying missing methods for complete UI-backend coverage...")
        
        # 1. Add methods to UserRepository
        try:
            with open("app/repositories/user_repo.py", "r") as f:
                content = f.read()
            
            # Add methods before the final class closing
            if "def update_user_language" not in content:
                # Find the last method and add our methods
                user_additions = self.add_user_repository_methods()
                # Insert before the last closing of the class
                if content.strip().endswith('"""'):
                    # Find the last method and add our methods before docstring
                    insert_pos = content.rfind('"""')
                    content = content[:insert_pos] + user_additions + "\n\n" + content[insert_pos:]
                else:
                    content += user_additions
                
                with open("app/repositories/user_repo.py", "w") as f:
                    f.write(content)
                
                self.fixes_applied.append("UserRepository methods added")
                logger.info("✅ Added missing UserRepository methods")
        except Exception as e:
            logger.error(f"Error adding UserRepository methods: {e}")
        
        # 2. Add methods to DomainRepository
        try:
            with open("app/repositories/domain_repo.py", "r") as f:
                content = f.read()
            
            if "def get_user_domains_with_dns" not in content:
                domain_additions = self.add_domain_repository_methods()
                content += domain_additions
                
                with open("app/repositories/domain_repo.py", "w") as f:
                    f.write(content)
                
                self.fixes_applied.append("DomainRepository methods added")
                logger.info("✅ Added missing DomainRepository methods")
        except Exception as e:
            logger.error(f"Error adding DomainRepository methods: {e}")
        
        # 3. Create SupportRepository
        try:
            support_repo_content = self.create_support_repository()
            with open("app/repositories/support_repo.py", "w") as f:
                f.write(support_repo_content)
            
            self.fixes_applied.append("SupportRepository created")
            logger.info("✅ Created SupportRepository class")
        except Exception as e:
            logger.error(f"Error creating SupportRepository: {e}")
        
        # 4. Create SupportService
        try:
            support_service_content = self.create_support_service()
            with open("app/services/support_service.py", "w") as f:
                f.write(support_service_content)
            
            self.fixes_applied.append("SupportService created")
            logger.info("✅ Created SupportService class")
        except Exception as e:
            logger.error(f"Error creating SupportService: {e}")
        
        logger.info(f"🎯 Applied {len(self.fixes_applied)} fixes for complete UI-backend coverage")
        return self.fixes_applied

if __name__ == "__main__":
    fixer = MissingMethodsImplementation()
    fixes = fixer.apply_all_fixes()
    print(f"Applied fixes: {fixes}")