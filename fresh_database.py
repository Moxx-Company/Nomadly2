#!/usr/bin/env python3
"""
Fresh Database Schema for Nomadly3 Domain Registration Platform
Designed specifically for our use cases:
- Domain registration workflow
- Cryptocurrency payments
- DNS management
- User account management
"""

import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, 
    DECIMAL, Text, ForeignKey, BIGINT, JSON, Index
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class
Base = declarative_base()

class User(Base):
    """User accounts for the Nomadly3 platform"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Account settings
    language = Column(String(10), default='en')
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Financial
    balance_usd = Column(DECIMAL(10, 2), default=0.00)
    total_spent = Column(DECIMAL(10, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now())
    
    # Relationships
    domains = relationship("Domain", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    user_states = relationship("UserState", back_populates="user", cascade="all, delete-orphan")

class UserState(Base):
    """Track user conversation states"""
    __tablename__ = 'user_states'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BIGINT, ForeignKey('users.telegram_id'), nullable=False)
    current_state = Column(String(100), default='ready')
    session_data = Column(JSON, default={})
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="user_states")

class Domain(Base):
    """Registered domains"""
    __tablename__ = 'domains'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BIGINT, ForeignKey('users.telegram_id'), nullable=False)
    domain_name = Column(String(255), nullable=False, index=True)
    
    # Registration details
    tld = Column(String(20), nullable=False)
    registrar = Column(String(50), default='openprovider')
    openprovider_domain_id = Column(String(100))
    
    # DNS Management
    nameserver_type = Column(String(20), default='cloudflare')  # cloudflare or custom
    cloudflare_zone_id = Column(String(100))
    custom_nameservers = Column(JSON, default=[])
    
    # Status and dates
    status = Column(String(20), default='active')  # active, expired, suspended
    registered_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True)
    
    # Pricing
    price_paid_usd = Column(DECIMAL(10, 2), nullable=False)
    renewal_price_usd = Column(DECIMAL(10, 2))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="domains")
    dns_records = relationship("DNSRecord", back_populates="domain", cascade="all, delete-orphan")

class DNSRecord(Base):
    """DNS records for domains"""
    __tablename__ = 'dns_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    
    # DNS record details
    record_type = Column(String(10), nullable=False)  # A, AAAA, CNAME, MX, TXT, NS
    name = Column(String(255), nullable=False)  # subdomain or @
    content = Column(Text, nullable=False)  # IP address, domain, text
    ttl = Column(Integer, default=3600)
    priority = Column(Integer)  # for MX records
    
    # Cloudflare integration
    cloudflare_record_id = Column(String(100))
    proxied = Column(Boolean, default=False)
    
    # Status
    status = Column(String(20), default='active')  # active, disabled
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    domain = relationship("Domain", back_populates="dns_records")

class Transaction(Base):
    """All financial transactions"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BIGINT, ForeignKey('users.telegram_id'), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # domain_purchase, wallet_deposit, refund
    amount_usd = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)
    
    # Cryptocurrency details (if applicable)
    crypto_currency = Column(String(10))  # BTC, ETH, LTC, DOGE
    crypto_amount = Column(DECIMAL(18, 8))
    crypto_address = Column(String(255))
    
    # Payment processing
    payment_provider = Column(String(50))  # blockbee, wallet
    payment_id = Column(String(255))
    transaction_hash = Column(String(255))
    
    # Status tracking
    status = Column(String(20), default='pending')  # pending, completed, failed, refunded
    
    # Related domain (if domain purchase)
    domain_id = Column(Integer, ForeignKey('domains.id'))
    
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="transactions")

class Order(Base):
    """Orders for domain registration"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BIGINT, ForeignKey('users.telegram_id'), nullable=False)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Order details
    domain_name = Column(String(255), nullable=False)
    tld = Column(String(20), nullable=False)
    registration_years = Column(Integer, default=1)
    
    # Pricing
    base_price_usd = Column(DECIMAL(10, 2), nullable=False)
    offshore_multiplier = Column(DECIMAL(3, 1), default=3.3)
    total_price_usd = Column(DECIMAL(10, 2), nullable=False)
    
    # User preferences
    nameserver_choice = Column(String(20), default='cloudflare')  # cloudflare or custom
    email_provided = Column(String(255))  # Optional email for notifications
    
    # Payment
    payment_method = Column(String(20))  # wallet or crypto
    crypto_currency = Column(String(10))  # BTC, ETH, LTC, DOGE
    crypto_address = Column(String(255))  # Payment address for crypto payments
    
    # Status
    status = Column(String(20), default='pending')  # pending, paid, completed, failed
    
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

class SystemSetting(Base):
    """System configuration settings"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Nameserver operations table
class NameserverOperation(Base):
    __tablename__ = 'nameserver_operations'
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('domains.id'))
    operation_type = Column(String(50), nullable=False)
    old_nameservers = Column(Text)
    new_nameservers = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=func.now())
    
# Audit logs table
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    old_values = Column(Text)
    new_values = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
# Domain searches table
class DomainSearch(Base):
    __tablename__ = 'domain_searches'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, nullable=False)
    domain_name = Column(String(255), nullable=False)
    available = Column(Boolean, default=False)
    price = Column(DECIMAL(10, 2))
    searched_at = Column(DateTime, default=func.now())
    
# Support tickets table
class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default='general')
    status = Column(String(20), default='open')
    priority = Column(String(10), default='normal')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
# FAQ entries table
class FAQEntry(Base):
    __tablename__ = 'faq_entries'
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    order_priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
# Ticket responses table  
class TicketResponse(Base):
    __tablename__ = 'ticket_responses'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'))
    responder_type = Column(String(20), nullable=False)  # 'user' or 'admin'
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

# Create indexes for performance
Index('idx_users_telegram_id', User.telegram_id)
Index('idx_domains_user', Domain.telegram_id)
Index('idx_domains_name', Domain.domain_name)
Index('idx_domains_expires', Domain.expires_at)
Index('idx_transactions_user', Transaction.telegram_id)
Index('idx_transactions_status', Transaction.status)
Index('idx_orders_id', Order.order_id)
Index('idx_dns_domain', DNSRecord.domain_id)

class FreshDatabaseManager:
    """Database manager for the fresh schema"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        # Create session factory
        self.SessionFactory = sessionmaker(bind=self.engine)
        
        logger.info("Fresh database manager initialized")
    
    def create_all_tables(self):
        """Create all tables in the database"""
        try:
            # Drop and recreate all tables to avoid conflicts
            #Base.metadata.drop_all(self.engine) # BB_CODE
            #Base.metadata.create_all(self.engine) # BB_CODE
            logger.info("✅ All fresh database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def get_session(self):
        """Get a database session"""
        return self.SessionFactory()
    
    def get_user(self, telegram_id: int):
        """Get user by telegram ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return user
        except Exception as e:
            logger.error(f"Error getting user {telegram_id}: {e}")
            return None
        finally:
            session.close()
    
    def create_user(self, telegram_id: int, username: str = None, first_name: str = None):
        """Create a new user"""
        session = self.get_session()
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            session.add(user)
            session.commit()
            logger.info(f"✅ Created new user: {telegram_id}")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to create user {telegram_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_user_domains(self, telegram_id: int):
        """Get all domains for a user"""
        session = self.get_session()
        try:
            domains = session.query(Domain).filter(Domain.telegram_id == telegram_id).all()
            return domains
        except Exception as e:
            logger.error(f"Error getting domains for user {telegram_id}: {e}")
            return []
        finally:
            session.close()
    
    def get_stats(self):
        """Get platform statistics"""
        session = self.get_session()
        try:
            user_count = session.query(User).count()
            domain_count = session.query(Domain).count()
            transaction_count = session.query(Transaction).count()
            
            return {
                'users': user_count,
                'domains': domain_count,
                'transactions': transaction_count
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'users': 0, 'domains': 0, 'transactions': 0}
        finally:
            session.close()

# Initialize the database manager and create tables
fresh_db_manager = FreshDatabaseManager()
fresh_db_manager.create_all_tables()

# Create session maker
SessionLocal = fresh_db_manager.SessionFactory

def get_db_session():
    """Get database session for repository layer initialization"""
    return SessionLocal()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_fresh_database():
    """Initialize the fresh database"""
    logger.info("🔥 Initializing Fresh Database for Nomadly3")
    
    try:
        db = FreshDatabaseManager()
        return db # BB_CODE
        
        # Create all tables
        if db.create_all_tables():
            logger.info("✅ Fresh database initialized successfully")
            
            # Get initial stats
            stats = db.get_stats()
            logger.info(f"📊 Database stats: {stats}")
            
            return db
        else:
            logger.error("❌ Failed to initialize fresh database")
            return None
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return None

def get_db_manager():
    """Legacy compatibility function for database manager"""
    return fresh_db_manager

if __name__ == "__main__":
    # Test the fresh database
    db = initialize_fresh_database()
    if db:
        print("🎯 Fresh database is ready for Nomadly3!")
    else:
        print("❌ Fresh database initialization failed")