from simple_connection_pool import get_pooled_connection

"""
Nomadly2 - Database Models v1.4
Fresh implementation for Domain Registration Bot
"""

import os
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from decimal import Decimal

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    DECIMAL,
    ForeignKey,
    BIGINT,
    Index,
    Date,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.sql import func

Base = declarative_base()

import logging
logger = logging.getLogger(__name__)

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

    # Relationships
    domains = relationship(
        "RegisteredDomain", back_populates="user", cascade="all, delete-orphan"
    )
    wallet_transactions = relationship(
        "WalletTransaction", back_populates="user", cascade="all, delete-orphan"
    )
    openprovider_contacts = relationship(
        "OpenProviderContact", back_populates="user", cascade="all, delete-orphan"
    )
    user_states = relationship(
        "UserState", back_populates="user", cascade="all, delete-orphan"
    )


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

    user = relationship("User", back_populates="user_states")


class RegisteredDomain(Base):
    """Domain registrations with DNS and nameserver management"""

    __tablename__ = "registered_domains"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    domain_name = Column(String(255), nullable=False, index=True)

    # OpenProvider integration
    openprovider_domain_id = Column(String(100))
    openprovider_contact_handle = Column(String(100))

    # Cloudflare integration
    cloudflare_zone_id = Column(String(100))
    nameservers = Column(JSONB, default=[])
    nameserver_mode = Column(String(50), default="cloudflare")

    # Registration details
    registration_date = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    status = Column(String(50), default="active")

    # Payment information
    price_paid = Column(DECIMAL(10, 2))
    payment_method = Column(String(50))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="domains")
    dns_records = relationship(
        "DNSRecord", back_populates="domain", cascade="all, delete-orphan"
    )


class DNSRecord(Base):
    """DNS records management with Cloudflare integration"""

    __tablename__ = "dns_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("registered_domains.id"), nullable=False)
    cloudflare_record_id = Column(String(100), index=True)

    record_type = Column(String(10), nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    ttl = Column(Integer, default=3600)
    priority = Column(Integer)
    proxied = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    domain = relationship("RegisteredDomain", back_populates="dns_records")


class WalletTransaction(Base):
    """Wallet and cryptocurrency transaction history"""

    __tablename__ = "wallet_transactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )

    transaction_type = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="USD")

    # Cryptocurrency details
    crypto_currency = Column(String(20))
    crypto_amount = Column(DECIMAL(18, 8))
    blockbee_payment_id = Column(String(100), index=True)
    payment_address = Column(Text)
    transaction_hash = Column(String(255))

    status = Column(String(50), default="pending")
    description = Column(Text)
    transaction_metadata = Column(JSONB, default={})

    created_at = Column(DateTime, default=func.now())
    confirmed_at = Column(DateTime)

    user = relationship("User", back_populates="wallet_transactions")


class OpenProviderContact(Base):
    """Privacy-focused random contact information"""

    __tablename__ = "openprovider_contacts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )

    contact_handle = Column(String(100), unique=True, nullable=False, index=True)
    generated_identity = Column(JSONB, nullable=False)

    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))

    address_line1 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country_code = Column(String(2), default="US")

    date_of_birth = Column(Date)
    passport_number = Column(String(50))

    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="openprovider_contacts")


class AdminNotification(Base):
    """Admin notifications and system events"""

    __tablename__ = "admin_notifications"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=True, index=True
    )

    notification_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_metadata = Column(JSONB, default={})

    severity = Column(String(20), default="info")
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())


class Translation(Base):
    """Bilingual translation system"""

    __tablename__ = "translations"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, index=True)
    language_code = Column(String(10), nullable=False, index=True)
    translation_text = Column(Text, nullable=False)
    context = Column(String(255))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_translation_key_lang", "key", "language_code", unique=True),
    )


class BalanceTransaction(Base):
    """Balance transaction tracking for wallet operations"""

    __tablename__ = "balance_transactions"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    transaction_type = Column(String(50), nullable=False)  # deposit, withdrawal, payment, bonus
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(500))
    order_id = Column(String(100))
    created_at = Column(DateTime, default=func.now())


class BonusTransaction(Base):
    """Bonus system for referrals and promotions"""

    __tablename__ = "bonus_transactions"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    bonus_type = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    trigger_event = Column(String(100))
    referrer_id = Column(BIGINT)
    promotion_code = Column(String(50))
    created_at = Column(DateTime, default=func.now())


class SystemSetting(Base):
    """System configuration and settings"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text)
    data_type = Column(String(50), default="string")
    description = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class APIUsageLog(Base):
    """API usage tracking and monitoring"""

    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True)
    service = Column(String(100), nullable=False)
    endpoint = Column(String(255))
    method = Column(String(20))
    status_code = Column(Integer)
    response_time = Column(DECIMAL(8, 3))
    telegram_id = Column(BIGINT, index=True)
    error_message = Column(Text)
    request_data = Column(JSONB)
    response_data = Column(JSONB)
    created_at = Column(DateTime, default=func.now())


class EmailNotification(Base):
    """Email notification system"""

    __tablename__ = "email_notifications"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    email_type = Column(String(100), nullable=False)
    recipient_email = Column(String(255))
    subject = Column(String(255))
    body = Column(Text)
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class Order(Base):
    """Order processing for all services"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    telegram_id = Column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False, index=True
    )
    service_type = Column(String(100), nullable=False)
    service_details = Column(JSONB, default={})
    amount_usd = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="pending")
    payment_address = Column(String(255))
    payment_txid = Column(String(255))
    crypto_currency = Column(String(10))
    crypto_amount = Column(DECIMAL(18, 8))
    blockbee_payment_id = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)


class AuditLog(Base):
    """Comprehensive audit trail for all system operations"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    
    # User and session information
    telegram_id = Column(BIGINT, index=True)  # Nullable for system operations
    username = Column(String(100))
    
    # Operation details
    action_type = Column(String(100), nullable=False, index=True)  # domain_register, payment_process, dns_create, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # domain, user, payment, dns_record
    resource_id = Column(String(100), index=True)  # domain_name, order_id, record_id, etc.
    
    # Action description and context
    action_description = Column(Text, nullable=False)
    old_values = Column(JSONB)  # Previous state before change
    new_values = Column(JSONB)  # New state after change
    
    # Technical details
    ip_address = Column(String(45))  # IPv4/IPv6 support
    user_agent = Column(Text)
    api_endpoint = Column(String(255))
    http_method = Column(String(10))
    
    # Result and metadata
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)  # Performance tracking
    audit_metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_audit_user_action', 'telegram_id', 'action_type'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_timestamp', 'created_at'),
        Index('idx_audit_action_success', 'action_type', 'success'),
    )


class DatabaseManager:
    def get_connection(self):
        """Get database connection for direct SQL queries"""
        return self.create_connection()
    
    def create_connection(self):
        """Create new database connection"""
        import psycopg2
        return psycopg2.connect(self.database_url)

    """Database connection and session management"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        self.engine = create_engine(
            self.database_url, pool_pre_ping=True, pool_recycle=300, echo=False
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self._tables_created = False

    def ensure_tables(self):
        """Create tables if they don't exist (lazy initialization)"""
        if not self._tables_created:
            Base.metadata.create_all(bind=self.engine)
            self._tables_created = True

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        self._tables_created = True

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def get_or_create_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
    ) -> User:
        """Get existing user or create new one"""
        self.ensure_tables()  # Lazy table creation
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    def update_user_language(self, telegram_id: int, language_code: str):
        """Update user's language preference"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.language_code = language_code
                user.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
        finally:
            session.close()

    def update_user_technical_email(self, telegram_id: int, email: str) -> bool:
        """Store user's technical email (once per user)"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.technical_email = email
                user.updated_at = datetime.utcnow()
                session.commit()
                print(f"✅ Technical email stored for user {telegram_id}: {email}")
                return True
            return False
        except Exception as e:
            print(f"Error updating user technical email: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_user_technical_email(self, telegram_id: int) -> Optional[str]:
        """Get user's stored technical email"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return user.technical_email
            return None
        except Exception as e:
            print(f"Error getting user technical email: {e}")
            return None
        finally:
            session.close()

    def get_user_balance(self, telegram_id: int) -> float:
        """Get user's wallet balance"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return float(user.balance_usd) if user else 0.0
        finally:
            session.close()

    def update_user_balance(
        self, telegram_id: int, amount: float, transaction_type: str = "admin_credit"
    ):
        """Update user balance and create transaction record"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.balance_usd = float(user.balance_usd) + amount
                user.updated_at = datetime.utcnow()

                # Create transaction record
                transaction = WalletTransaction(
                    telegram_id=telegram_id,
                    transaction_type=transaction_type,
                    amount=amount,
                    status="confirmed",
                    description=f"Balance {transaction_type}: ${amount}",
                )
                session.add(transaction)
                session.commit()
        finally:
            session.close()

    def get_user_domains(self, telegram_id: int) -> List[RegisteredDomain]:
        """Get all domains for a user"""
        session = self.get_session()
        try:
            domains = (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.telegram_id == telegram_id)
                .order_by(RegisteredDomain.registration_date.desc())
                .all()
            )
            return domains
        finally:
            session.close()
    
    def update_domain_zone_id(self, domain_name: str, cloudflare_zone_id: str):
        """Update cloudflare_zone_id for a domain"""
        session = self.get_session()
        try:
            domain = (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.domain_name == domain_name)
                .first()
            )
            if domain:
                domain.cloudflare_zone_id = cloudflare_zone_id
                session.commit()
                logger.info(f"Updated cloudflare_zone_id for {domain_name}: {cloudflare_zone_id}")
            else:
                logger.warning(f"Domain {domain_name} not found for cloudflare_zone_id update")
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating cloudflare_zone_id for {domain_name}: {e}")
            raise
        finally:
            session.close()

    def update_user_state(self, telegram_id: int, state: str, state_data: dict = None):
        """Update user state"""
        session = self.get_session()
        try:
            # Delete existing state
            session.query(UserState).filter(
                UserState.telegram_id == telegram_id
            ).delete()

            # Create new state
            user_state = UserState(
                telegram_id=telegram_id, state=state, data=state_data or {}
            )
            session.add(user_state)
            session.commit()
        finally:
            session.close()

    def get_user_state(self, telegram_id: int) -> Optional[UserState]:
        """Get user's current state"""
        session = self.get_session()
        try:
            return (
                session.query(UserState)
                .filter(UserState.telegram_id == telegram_id)
                .first()
            )
        finally:
            session.close()

    def clear_user_state(self, telegram_id: int):
        """Clear user state"""
        session = self.get_session()
        try:
            session.query(UserState).filter(
                UserState.telegram_id == telegram_id
            ).delete()
            session.commit()
        finally:
            session.close()

    def get_domain_by_id(self, domain_id: int) -> Optional[RegisteredDomain]:
        """Get domain by ID"""
        session = self.get_session()
        try:
            return (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.id == domain_id)
                .first()
            )
        finally:
            session.close()

    def get_domain_by_name(self, domain_name: str, telegram_id: int = None) -> Optional[RegisteredDomain]:
        """Get domain by name, optionally filtered by user"""
        session = self.get_session()
        try:
            query = session.query(RegisteredDomain).filter(RegisteredDomain.domain_name == domain_name)
            if telegram_id:
                query = query.filter(RegisteredDomain.telegram_id == telegram_id)
            return query.first()
        finally:
            session.close()

    def create_registered_domain(
        self,
        telegram_id: int,
        domain_name: str,
        registrar: str = "openprovider",
        expiry_date: datetime = None,
        openprovider_contact_handle: str = None,
        openprovider_domain_id: str = None,
        cloudflare_zone_id: str = None,
        nameservers: str = None,
    ) -> RegisteredDomain:
        """Create registered domain record"""
        session = self.get_session()
        try:
            # Convert comma-separated nameservers to list for JSONB field
            nameserver_list = []
            if nameservers:
                if isinstance(nameservers, str):
                    nameserver_list = [ns.strip() for ns in nameservers.split(',') if ns.strip()]
                elif isinstance(nameservers, list):
                    nameserver_list = nameservers
                    
            domain = RegisteredDomain(
                telegram_id=telegram_id,
                domain_name=domain_name,
                openprovider_contact_handle=openprovider_contact_handle,
                openprovider_domain_id=openprovider_domain_id,
                cloudflare_zone_id=cloudflare_zone_id,
                nameservers=nameserver_list,
                registration_date=datetime.now(),
                expires_at=expiry_date if expiry_date else datetime.now() + timedelta(days=365),
                status='active',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(domain)
            session.commit()
            session.refresh(domain)
            return domain
        finally:
            session.close()

    def update_domain_cloudflare_zone(self, domain_id: int, cloudflare_zone_id: str):
        """Update domain with Cloudflare zone ID"""
        session = self.get_session()
        try:
            domain = (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.id == domain_id)
                .first()
            )
            if domain:
                domain.cloudflare_zone_id = cloudflare_zone_id
                session.commit()
        finally:
            session.close()

    def create_admin_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        telegram_id: int = None,
        notification_metadata: Dict = None,
    ):
        """Create admin notification"""
        session = self.get_session()
        try:
            notification = AdminNotification(
                telegram_id=telegram_id,
                notification_type=notification_type,
                title=title,
                message=message,
                notification_metadata=notification_metadata or {},
            )
            session.add(notification)
            session.commit()
        finally:
            session.close()

    def create_domain_registration(
        self,
        telegram_id: int,
        domain_name: str,
        openprovider_domain_id: str = None,
        openprovider_contact_handle: str = None,
        cloudflare_zone_id: str = None,
        price_paid: float = None,
        payment_method: str = None,
    ) -> RegisteredDomain:
        """Create new domain registration record"""
        session = self.get_session()
        try:
            domain = RegisteredDomain(
                telegram_id=telegram_id,
                domain_name=domain_name,
                openprovider_domain_id=openprovider_domain_id,
                openprovider_contact_handle=openprovider_contact_handle,
                cloudflare_zone_id=cloudflare_zone_id,
                price_paid=price_paid,
                payment_method=payment_method,
            )
            session.add(domain)
            session.commit()
            session.refresh(domain)
            return domain
        finally:
            session.close()

    def create_openprovider_contact(
        self, telegram_id: int, contact_handle: str, generated_identity: Dict
    ) -> OpenProviderContact:
        """Create OpenProvider contact with random identity"""
        session = self.get_session()
        try:
            contact = OpenProviderContact(
                telegram_id=telegram_id,
                contact_handle=contact_handle,
                generated_identity=generated_identity,
                first_name=generated_identity.get("first_name"),
                last_name=generated_identity.get("last_name"),
                email=generated_identity.get("email"),
                phone=generated_identity.get("phone"),
                address_line1=generated_identity.get("address_line1"),
                city=generated_identity.get("city"),
                state=generated_identity.get("state"),
                postal_code=generated_identity.get("postal_code"),
                date_of_birth=datetime.strptime(
                    generated_identity.get("date_of_birth"), "%Y-%m-%d"
                ).date(),
                passport_number=generated_identity.get("passport_number"),
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return contact
        finally:
            session.close()

    def get_user_contact(self, telegram_id: int) -> OpenProviderContact:
        """Get existing contact for user"""
        session = self.get_session()
        try:
            return (
                session.query(OpenProviderContact)
                .filter(
                    OpenProviderContact.telegram_id == telegram_id,
                    OpenProviderContact.is_active == True,
                )
                .first()
            )
        finally:
            session.close()

    def get_domain_by_telegram_id(self, telegram_id: int) -> RegisteredDomain:
        """Get registered domain by telegram_id (for compatibility)"""
        session = self.get_session()
        try:
            return (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.telegram_id == telegram_id)
                .first()
            )
        finally:
            session.close()

    def get_latest_domain_by_telegram_id(self, telegram_id: int) -> RegisteredDomain:
        """Get latest registered domain by telegram_id"""
        session = self.get_session()
        try:
            return (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.telegram_id == telegram_id)
                .order_by(RegisteredDomain.id.desc())
                .first()
            )
        finally:
            session.close()

    def create_dns_record(
        self,
        domain_id: int,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 3600,
        cloudflare_record_id: str = None,
    ) -> DNSRecord:
        """Create DNS record"""
        session = self.get_session()
        try:
            dns_record = DNSRecord(
                domain_id=domain_id,
                record_type=record_type,
                name=name,
                content=content,
                ttl=ttl,
                cloudflare_record_id=cloudflare_record_id,
            )
            session.add(dns_record)
            session.commit()
            session.refresh(dns_record)
            return dns_record
        finally:
            session.close()

    def get_domain_dns_records(self, domain_id: int) -> List[DNSRecord]:
        """Get all DNS records for a domain"""
        session = self.get_session()
        try:
            return (
                session.query(DNSRecord).filter(DNSRecord.domain_id == domain_id).all()
            )
        finally:
            session.close()

    def update_domain_nameservers(
        self, domain_name: str, nameservers: List[str], mode: str
    ):
        """Update domain nameserver configuration"""
        session = self.get_session()
        try:
            domain = (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.domain_name == domain_name)
                .first()
            )
            if domain:
                domain.nameservers = ",".join(nameservers)
                domain.nameserver_mode = mode
                session.commit()
        finally:
            session.close()

    def get_order(self, order_id: str):
        """Get order by ID using actual database schema"""
        from sqlalchemy import text
        
        session = self.get_session()
        try:
            result = session.execute(text("""
                SELECT id, telegram_id, order_id, domain_name, tld, 
                       registration_years, base_price_usd, offshore_multiplier,
                       total_price_usd, nameserver_choice, email_provided,
                       payment_method, crypto_currency, status, created_at, completed_at,crypto_address,service_type, transaction_id,service_details
                FROM orders 
                WHERE order_id = :order_id
            """), {'order_id': order_id})
            
            row = result.fetchone()
            if row:
                # Create a simple order object with the actual data
                class SimpleOrder:
                    def __init__(self, row_data):
                        self.id = row_data[0]
                        self.telegram_id = row_data[1] 
                        self.order_id = row_data[2]
                        self.domain_name = row_data[3]
                        self.tld = row_data[4]                        
                        self.registration_years = row_data[5]
                        self.base_price_usd = row_data[6]
                        self.offshore_multiplier = row_data[7]
                        self.total_price_usd = row_data[8]
                        self.nameserver_choice = row_data[9]
                        self.email_provided = row_data[10]
                        self.payment_method = row_data[11]
                        self.crypto_currency = row_data[12]
                        self.status = row_data[13]
                        self.created_at = row_data[14]
                        self.completed_at = row_data[15]
                        self.crypto_address = row_data[16]
                        self.service_type = row_data[17]
                        self.transaction_id = row_data[18]
                        self.service_details = row_data[19]
                        
                return SimpleOrder(row)
            return None
        finally:
            session.close()

    def get_user_orders(self, telegram_id: int) -> List:
        """Get all orders for a user"""
        session = self.get_session()
        try:
            return (
                session.query(Order)
                .filter(Order.telegram_id == telegram_id)
                .order_by(Order.created_at.desc())
                .all()
            )
        finally:
            session.close()

    def create_transaction(
        self,
        telegram_id: int,
        transaction_type: str,
        amount: float,
        description: str = None,
        order_id: str = None,
    ):
        """Create transaction record"""
        session = self.get_session()
        try:
            transaction = Transaction(
                telegram_id=telegram_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                order_id=order_id,
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        finally:
            session.close()

    def get_user_transactions(self, telegram_id: int) -> List:
        """Get user transaction history"""
        session = self.get_session()
        try:
            return (
                session.query(Transaction)
                .filter(Transaction.telegram_id == telegram_id)
                .order_by(Transaction.created_at.desc())
                .limit(20)
                .all()
            )
        finally:
            session.close()

    def update_user_balance(self, telegram_id: int, amount_change: float):
        """Update user balance (can be positive or negative)"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.balance_usd = float(user.balance_usd or 0.0) + amount_change
                if user.balance_usd < 0:
                    user.balance_usd = 0.0  # Prevent negative balance
                session.commit()
        finally:
            session.close()

    def set_user_balance(self, telegram_id: int, amount_change: float):
        """Update user balance (can be positive or negative)"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.balance_usd = amount_change
                if user.balance_usd < 0:
                    user.balance_usd = 0.0  # Prevent negative balance
                session.commit()
        finally:
            session.close()

    def create_order(
        self,
        telegram_id: int,
        service_type: str,
        service_details: Dict,
        amount: float,
        payment_method: str = None,
        email_provided: str = None
    ) -> Order:
        """Create new order using raw SQL to match actual database schema"""
        import uuid
        from decimal import Decimal
        from sqlalchemy import text

        session = self.get_session()
        try:
            # Extract domain info from service_details 
            domain_name = service_details.get('domain_name', 'unknown.com')
            tld = service_details.get('tld', '.com')
            nameserver_choice = service_details.get('nameserver_choice', 'cloudflare')
            order_id = str(uuid.uuid4())
            
            # Use raw SQL to insert with exact column names from actual schema
            result = session.execute(text("""
                INSERT INTO orders (
                    telegram_id, order_id, domain_name, tld, service_type, registration_years,
                    base_price_usd, offshore_multiplier, total_price_usd,
                    nameserver_choice, payment_method, status, created_at
                ) VALUES (
                    :telegram_id, :order_id, :domain_name, :tld, :service_type, :registration_years,
                    :base_price_usd, :offshore_multiplier, :total_price_usd,
                    :nameserver_choice, :payment_method, :status, now(),:service_details,:email_provided
                ) RETURNING id
            """), {
                'telegram_id': telegram_id,
                'order_id': order_id,
                'domain_name': domain_name,
                'tld': tld,
                'service_type':service_type,
                'registration_years': 1,
                'base_price_usd': float(Decimal(str(amount)) / Decimal('3.3')),
                'offshore_multiplier': 3.3,
                'total_price_usd': float(amount),
                'nameserver_choice': nameserver_choice,
                'payment_method': payment_method,
                'status': 'pending',
                'service_details':json.dumps(service_details),
                'email_provided': email_provided
            })
            
            order_db_id = result.fetchone()[0]
            session.commit()
            
            # Create a simple order object to return
            class SimpleOrder:
                def __init__(self, order_id, db_id):
                    self.order_id = order_id
                    self.id = db_id
                    
            return SimpleOrder(order_id, order_db_id)
            
        finally:
            session.close()

    def update_order_payment(
        self,
        order_id: str,
        payment_status: str = None,
        payment_address: str = None,
        crypto_currency: str = None,
        crypto_amount: str = None,
        blockbee_payment_id: str = None,
    ):
        """Update order payment information using actual database schema"""
        from sqlalchemy import text
        
        session = self.get_session()
        try:
            # Build dynamic update query based on provided parameters
            update_parts = []
            params = {'order_id': order_id}
            
            if payment_status:
                update_parts.append("status = :status")
                params['status'] = payment_status
            if crypto_currency:
                update_parts.append("crypto_currency = :crypto_currency")
                params['crypto_currency'] = crypto_currency
            if payment_status == "completed":
                update_parts.append("completed_at = now()")
                
            if update_parts:
                update_sql = f"""
                    UPDATE orders 
                    SET {', '.join(update_parts)}
                    WHERE order_id = :order_id
                """
                session.execute(text(update_sql), params)
                session.commit()
                
        finally:
            session.close()

    def get_pending_orders(self, telegram_id: int = None) -> List[Order]:
        """Get pending orders"""
        session = self.get_session()
        try:
            query = session.query(Order).filter(Order.payment_status == "pending")
            if telegram_id:
                query = query.filter(Order.telegram_id == telegram_id)
            return query.all()
        finally:
            session.close()

    def create_wallet_transaction(
        self,
        telegram_id: int,
        transaction_type: str,
        amount: float,
        description: str = None,
        crypto_currency: str = None,
        payment_address: str = None,
        blockbee_payment_id: str = None,
    ) -> WalletTransaction:
        """Create wallet transaction record"""
        session = self.get_session()
        try:
            transaction = WalletTransaction(
                telegram_id=telegram_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                crypto_currency=crypto_currency,
                payment_address=payment_address,
                blockbee_payment_id=blockbee_payment_id,
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        finally:
            session.close()

    def get_user_transactions(
        self, telegram_id: int, limit: int = 50
    ) -> List[WalletTransaction]:
        """Get user transaction history"""
        session = self.get_session()
        try:
            return (
                session.query(WalletTransaction)
                .filter(WalletTransaction.telegram_id == telegram_id)
                .order_by(WalletTransaction.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def get_system_statistics(self) -> Dict:
        """Get system statistics for admin dashboard"""
        session = self.get_session()
        try:
            stats = {}
            stats["total_users"] = session.query(User).count()
            stats["total_domains"] = session.query(RegisteredDomain).count()
            stats["total_transactions"] = session.query(WalletTransaction).count()
            stats["pending_orders"] = (
                session.query(Order).filter(Order.payment_status == "pending").count()
            )
            stats["total_revenue"] = (
                session.query(func.sum(WalletTransaction.amount))
                .filter(WalletTransaction.transaction_type == "payment")
                .scalar()
                or 0
            )
            return stats
        finally:
            session.close()

    def get_state_data(self, telegram_id: int, state: str) -> Dict:
        """Get user state data"""
        session = self.get_session()
        try:
            user_state = (
                session.query(UserState)
                .filter(UserState.telegram_id == telegram_id, UserState.state == state)
                .first()
            )
            return user_state.data if user_state else {}
        finally:
            session.close()

    def clear_user_state(self, telegram_id: int):
        """Clear all user states"""
        session = self.get_session()
        try:
            session.query(UserState).filter(
                UserState.telegram_id == telegram_id
            ).delete()
            session.commit()
        finally:
            session.close()

    def set_user_state(self, telegram_id: int, state: str, data: Dict = None):
        """Set user state with data"""
        session = self.get_session()
        try:
            # Remove existing states
            session.query(UserState).filter(
                UserState.telegram_id == telegram_id
            ).delete()

            # Add new state
            user_state = UserState(
                telegram_id=telegram_id, state=state, data=data or {}
            )
            session.add(user_state)
            session.commit()
        finally:
            session.close()

    def get_total_orders(self) -> int:
        """Get total number of orders in system"""
        session = self.get_session()
        try:
            return session.query(Order).count()
        finally:
            session.close()

    def get_pending_orders_count(self) -> int:
        """Get count of pending orders"""
        session = self.get_session()
        try:
            return session.query(Order).filter(Order.status == "pending").count()
        finally:
            session.close()

    def update_order_status(self, order_id: str, status: str):
        """Update order status"""
        session = self.get_session()
        try:
            order = session.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.status = status
                session.commit()
        finally:
            session.close()




# Global database manager
db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_db_session():
    """Get database session for bot operations"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not configured")
            
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None
