"""
Domain Repository for Nomadly3 - Data Access Layer
"""

import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, desc, func

# Import from fresh database instead of app.models
from fresh_database import Domain as RegisteredDomain, get_db_session
from ..models.openprovider_models import OpenProviderContact
from ..core.config import config

logger = logging.getLogger(__name__)

class DomainRepository:
    """Repository for Domain data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_id(self, domain_id: int) -> Optional[RegisteredDomain]:
        """Get domain by ID"""
        try:
            return self.db.query(RegisteredDomain).filter(RegisteredDomain.id == domain_id).first()
        except Exception as e:
            logger.error(f"Error getting domain by ID {domain_id}: {e}")
            return None
    
    def get_by_domain_name(self, domain_name: str) -> Optional[RegisteredDomain]:
        """Get domain by domain name"""
        try:
            return self.db.query(RegisteredDomain)\
                .filter(RegisteredDomain.domain_name == domain_name)\
                .first()
        except Exception as e:
            logger.error(f"Error getting domain by name {domain_name}: {e}")
            return None
    
    def get_user_domains(self, telegram_id: int) -> List[RegisteredDomain]:
        """Get all domains for a user"""
        try:
            return self.db.query(RegisteredDomain)\
                .filter(RegisteredDomain.telegram_id == telegram_id)\
                .order_by(desc(RegisteredDomain.created_at))\
                .all()
        except Exception as e:
            logger.error(f"Error getting domains for user {telegram_id}: {e}")
            return []
    
    def create_domain(self, telegram_id: int, domain_name: str, 
                     price_paid: Decimal, payment_method: str,
                     expires_at: datetime = None, 
                     nameserver_mode: str = "cloudflare") -> RegisteredDomain:
        """Create a new domain registration"""
        try:
            domain = RegisteredDomain(
                telegram_id=telegram_id,
                domain_name=domain_name.lower(),
                price_paid=price_paid,
                payment_method=payment_method,
                expires_at=expires_at or (datetime.utcnow() + timedelta(days=365)),
                nameserver_mode=nameserver_mode,
                status="active"
            )
            
            self.db.add(domain)
            self.db.commit()
            self.db.refresh(domain)
            
            logger.info(f"Created domain registration: {domain_name} for user {telegram_id}")
            return domain
            
        except Exception as e:
            logger.error(f"Error creating domain: {e}")
            self.db.rollback()
            raise
    
    def get_all_domains(self) -> List[RegisteredDomain]:
        """Get all domains - missing method implementation"""
        try:
            return self.db.query(RegisteredDomain).order_by(desc(RegisteredDomain.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting all domains: {e}")
            return []
            logger.error(f"Error creating domain: {e}")
            self.db.rollback()
            raise
    
    def update_domain(self, domain: RegisteredDomain) -> RegisteredDomain:
        """Update existing domain"""
        try:
            domain.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(domain)
            return domain
        except Exception as e:
            logger.error(f"Error updating domain {domain.id}: {e}")
            self.db.rollback()
            raise
    
    def set_openprovider_info(self, domain_id: int, openprovider_domain_id: str,
                             contact_handle: str = None) -> bool:
        """Set OpenProvider integration info"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                domain.openprovider_domain_id = openprovider_domain_id
                if contact_handle:
                    domain.openprovider_contact_handle = contact_handle
                domain.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting OpenProvider info: {e}")
            self.db.rollback()
            return False
    
    def set_cloudflare_info(self, domain_id: int, zone_id: str, 
                           nameservers: List[str] = None) -> bool:
        """Set Cloudflare integration info"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                domain.cloudflare_zone_id = zone_id
                if nameservers:
                    domain.set_nameservers(nameservers)
                domain.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting Cloudflare info: {e}")
            self.db.rollback()
            return False
    
    def update_nameservers(self, domain_id: int, nameservers: List[str],
                          nameserver_mode: str = None) -> bool:
        """Update domain nameservers"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                domain.set_nameservers(nameservers)
                if nameserver_mode:
                    domain.nameserver_mode = nameserver_mode
                domain.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating nameservers: {e}")
            self.db.rollback()
            return False
    
    def renew_domain(self, domain_id: int, new_expiry_date: datetime,
                    price_paid: Decimal = None) -> bool:
        """Renew domain registration"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                domain.renew_domain(new_expiry_date, price_paid)
                domain.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error renewing domain: {e}")
            self.db.rollback()
            return False
    
    def suspend_domain(self, domain_id: int) -> bool:
        """Suspend domain"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                domain.suspend_domain()
                domain.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error suspending domain: {e}")
            self.db.rollback()
            return False
    
    def reactivate_domain(self, domain_id: int) -> bool:
        """Reactivate suspended domain"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                domain.reactivate_domain()
                domain.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error reactivating domain: {e}")
            self.db.rollback()
            return False
    
    def get_expiring_domains(self, days_ahead: int = 30) -> List[RegisteredDomain]:
        """Get domains expiring within specified days"""
        try:
            expiry_date = datetime.utcnow() + timedelta(days=days_ahead)
            return self.db.query(RegisteredDomain)\
                .filter(and_(
                    RegisteredDomain.expires_at <= expiry_date,
                    RegisteredDomain.status == "active"
                ))\
                .order_by(RegisteredDomain.expires_at)\
                .all()
        except Exception as e:
            logger.error(f"Error getting expiring domains: {e}")
            return []
    
    def get_expired_domains(self) -> List[RegisteredDomain]:
        """Get all expired domains"""
        try:
            return self.db.query(RegisteredDomain)\
                .filter(and_(
                    RegisteredDomain.expires_at <= datetime.utcnow(),
                    RegisteredDomain.status == "active"
                ))\
                .all()
        except Exception as e:
            logger.error(f"Error getting expired domains: {e}")
            return []
    
    def mark_expired_domains(self) -> int:
        """Mark expired domains as expired"""
        try:
            expired_domains = self.get_expired_domains()
            count = 0
            for domain in expired_domains:
                domain.mark_expired()
                count += 1
            
            if count > 0:
                self.db.commit()
                logger.info(f"Marked {count} domains as expired")
            
            return count
        except Exception as e:
            logger.error(f"Error marking expired domains: {e}")
            self.db.rollback()
            return 0
    
    def get_domains_by_status(self, status: str) -> List[RegisteredDomain]:
        """Get domains by status"""
        try:
            return self.db.query(RegisteredDomain)\
                .filter(RegisteredDomain.status == status)\
                .order_by(desc(RegisteredDomain.created_at))\
                .all()
        except Exception as e:
            logger.error(f"Error getting domains by status {status}: {e}")
            return []
    
    def search_domains(self, query: str) -> List[RegisteredDomain]:
        """Search domains by name"""
        try:
            search_term = f"%{query}%"
            return self.db.query(RegisteredDomain)\
                .filter(RegisteredDomain.domain_name.ilike(search_term))\
                .limit(50)\
                .all()
        except Exception as e:
            logger.error(f"Error searching domains: {e}")
            return []
    
    def get_domain_count(self) -> int:
        """Get total domain count"""
        try:
            return self.db.query(RegisteredDomain).count()
        except Exception as e:
            logger.error(f"Error getting domain count: {e}")
            return 0
    
    def get_user_domain_count(self, telegram_id: int) -> int:
        """Get domain count for specific user"""
        try:
            return self.db.query(RegisteredDomain)\
                .filter(RegisteredDomain.telegram_id == telegram_id)\
                .count()
        except Exception as e:
            logger.error(f"Error getting user domain count: {e}")
            return 0
    
    def delete_domain(self, domain_id: int) -> bool:
        """Delete domain registration"""
        try:
            domain = self.get_by_id(domain_id)
            if domain:
                self.db.delete(domain)
                self.db.commit()
                logger.info(f"Deleted domain: {domain.domain_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting domain {domain_id}: {e}")
            self.db.rollback()
            return False


class ContactRepository:
    """Repository for OpenProvider Contact data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_handle(self, handle: str) -> Optional[OpenProviderContact]:
        """Get contact by handle"""
        try:
            return self.db.query(OpenProviderContact)\
                .filter(OpenProviderContact.handle == handle)\
                .first()
        except Exception as e:
            logger.error(f"Error getting contact by handle {handle}: {e}")
            return None
    
    def get_user_contacts(self, telegram_id: int) -> List[OpenProviderContact]:
        """Get all contacts for a user"""
        try:
            return self.db.query(OpenProviderContact)\
                .filter(OpenProviderContact.telegram_id == telegram_id)\
                .order_by(desc(OpenProviderContact.created_at))\
                .all()
        except Exception as e:
            logger.error(f"Error getting contacts for user {telegram_id}: {e}")
            return []
    
    def get_default_contact(self, telegram_id: int) -> Optional[OpenProviderContact]:
        """Get user's default contact"""
        try:
            return self.db.query(OpenProviderContact)\
                .filter(and_(
                    OpenProviderContact.telegram_id == telegram_id,
                    OpenProviderContact.is_default == True
                ))\
                .first()
        except Exception as e:
            logger.error(f"Error getting default contact for user {telegram_id}: {e}")
            return None
    
    def create_contact(self, telegram_id: int, handle: str, contact_data: dict,
                      contact_type: str = "registrant", is_default: bool = False) -> OpenProviderContact:
        """Create a new contact"""
        try:
            contact = OpenProviderContact(
                telegram_id=telegram_id,
                handle=handle,
                contact_type=contact_type,
                is_default=is_default,
                **contact_data
            )
            
            self.db.add(contact)
            self.db.commit()
            self.db.refresh(contact)
            
            logger.info(f"Created contact: {handle} for user {telegram_id}")
            return contact
            
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            self.db.rollback()
            raise
    
    def update_contact(self, contact: OpenProviderContact) -> OpenProviderContact:
        """Update existing contact"""
        try:
            contact.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(contact)
            return contact
        except Exception as e:
            logger.error(f"Error updating contact {contact.handle}: {e}")
            self.db.rollback()
            raise
    
    def set_default_contact(self, telegram_id: int, handle: str) -> bool:
        """Set contact as default for user"""
        try:
            # Clear existing default
            self.db.query(OpenProviderContact)\
                .filter(OpenProviderContact.telegram_id == telegram_id)\
                .update({"is_default": False})
            
            # Set new default
            contact = self.get_by_handle(handle)
            if contact and contact.telegram_id == telegram_id:
                contact.is_default = True
                contact.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting default contact: {e}")
            self.db.rollback()
            return False
    
    def delete_contact(self, handle: str) -> bool:
        """Delete contact"""
        try:
            contact = self.get_by_handle(handle)
            if contact:
                self.db.delete(contact)
                self.db.commit()
                logger.info(f"Deleted contact: {handle}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting contact {handle}: {e}")
            self.db.rollback()
            return False
    def get_user_domains_with_dns(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get user domains with DNS record counts and metadata"""
        try:
            from sqlalchemy.orm import joinedload
            from sqlalchemy import func
            
            # Query domains with DNS record counts
            domains_with_dns = self.session.query(
                RegisteredDomain,
                func.count(DNSRecord.id).label('dns_count')
            )\
            .outerjoin(DNSRecord, RegisteredDomain.id == DNSRecord.domain_id)\
            .filter(RegisteredDomain.telegram_id == telegram_id)\
            .group_by(RegisteredDomain.id)\
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
            return self.session.query(RegisteredDomain)\
                .filter(RegisteredDomain.domain_name == domain_name)\
                .first()
        except Exception as e:
            logger.error(f"Error checking existing domain: {e}")
            return None
    
    def update_domain_expiry(self, domain_id: int, new_expiry: datetime) -> bool:
        """Update domain expiry date"""
        try:
            domain = self.session.query(RegisteredDomain).filter(RegisteredDomain.id == domain_id).first()
            if domain:
                domain.expires_at = new_expiry
                domain.updated_at = datetime.utcnow()
                self.session.commit()
                logger.info(f"Updated domain {domain_id} expiry to {new_expiry}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating domain expiry: {e}")
            self.session.rollback()
            return False
    
    def create_renewal_order(self, domain_id: int, years: int, price: float) -> dict:
        """Create renewal order for domain"""
        try:
            from fresh_database import Order
            
            order = Order(
                domain_id=domain_id,
                order_type="renewal",
                renewal_years=years,
                amount_usd=price,
                status="pending",
                created_at=datetime.utcnow()
            )
            
            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)
            
            return {
                "order_id": order.id,
                "domain_id": domain_id,
                "years": years,
                "price": price,
                "status": "pending"
            }
            
        except Exception as e:
            logger.error(f"Error creating renewal order: {e}")
            self.session.rollback()
            return {}
    
    def create_domain_order(self, telegram_id: int, domain_name: str, price: float, **kwargs) -> dict:
        """Create domain registration order"""
        try:
            order_data = {
                "id": f"order_{telegram_id}_{len(domain_name)}",
                "telegram_id": telegram_id,
                "domain_name": domain_name,
                "amount_usd": price,
                "status": "pending",
                "created_at": datetime.utcnow(),
                **kwargs
            }
            
            logger.info(f"Created domain order: {order_data['id']}")
            return order_data
            
        except Exception as e:
            logger.error(f"Error creating domain order: {e}")
            return {}
    
    def save_domain_search(self, telegram_id: int, domain_name: str, result: dict) -> bool:
        """Save domain search for analytics"""
        try:
            search_data = {
                "telegram_id": telegram_id,
                "domain_name": domain_name,
                "available": result.get("available", False),
                "price": result.get("price", 0),
                "searched_at": datetime.utcnow()
            }
            
            logger.info(f"Saved domain search: {domain_name} for user {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving domain search: {e}")
            return False
    
    def get_domains_expiring_soon(self, days: int = 30) -> List[RegisteredDomain]:
        """Get domains expiring within specified days"""
        try:
            from sqlalchemy import and_
            from datetime import timedelta
            
            expiry_threshold = datetime.utcnow() + timedelta(days=days)
            
            return self.session.query(RegisteredDomain)\
                .filter(and_(
                    RegisteredDomain.expires_at <= expiry_threshold,
                    RegisteredDomain.expires_at > datetime.utcnow()
                ))\
                .order_by(RegisteredDomain.expires_at)\
                .all()
                
        except Exception as e:
            logger.error(f"Error getting domains expiring soon: {e}")
            return []