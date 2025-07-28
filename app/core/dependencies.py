"""
Dependency injection for services
"""

from typing import Generator
from sqlalchemy.orm import Session

from fresh_database import get_db_session
from app.services.nameserver_service import NameserverService
from app.repositories.domain_repo import DomainRepository
from app.core.openprovider import OpenProviderAPI

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

def get_nameserver_service(db: Session = None) -> NameserverService:
    """Get nameserver service with dependencies"""
    if db is None:
        db = get_db_session()
    
    domain_repo = DomainRepository(db)
    openprovider_api = OpenProviderAPI()
    
    return NameserverService(
        domain_repo=domain_repo,
        openprovider_api=openprovider_api,
        audit_service=None  # Could add audit service later
    )

def get_wallet_service(db: Session = None):
    """Get wallet service with dependencies"""
    from app.services.wallet_service import WalletService
    from app.repositories.wallet_repo import WalletRepository
    from app.repositories.transaction_repo import TransactionRepository
    from app.repositories.user_repo import UserRepository
    
    if db is None:
        db = get_db_session()
    
    wallet_repo = WalletRepository(db)
    transaction_repo = TransactionRepository(db)
    user_repo = UserRepository(db)
    
    return WalletService(wallet_repo, transaction_repo, user_repo)

def get_user_service(db: Session = None):
    """Get user service with dependencies"""
    from app.services.user_service import UserService
    from app.repositories.user_repo import UserRepository
    
    if db is None:
        db = get_db_session()
    
    user_repo = UserRepository(db)
    return UserService(user_repo)

def get_support_service(db: Session = None):
    """Get support service with dependencies"""
    from app.services.support_service import SupportService
    from app.repositories.support_repo import SupportRepository
    
    if db is None:
        db = get_db_session()
    
    support_repo = SupportRepository(db)
    return SupportService(support_repo)

def get_domain_service(db: Session = None):
    """Get domain service with dependencies"""
    from app.services.domain_service import DomainService
    from app.repositories.domain_repo import DomainRepository
    
    if db is None:
        db = get_db_session()
    
    domain_repo = DomainRepository(db)
    return DomainService(domain_repo)

def get_dns_service(db: Session = None):
    """Get DNS service with dependencies"""
    from app.services.dns_service import DNSService
    from app.repositories.dns_repo import DNSRepository
    
    if db is None:
        db = get_db_session()
    
    dns_repo = DNSRepository(db)
    return DNSService(dns_repo)