#!/usr/bin/env python3
"""
Simple Integration Test for Nomadly3 - Resolving Dependency Injection Issues
Tests critical layer connectivity without complex context managers
"""

import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_integration():
    """Test database layer with proper session handling"""
    try:
        from fresh_database import get_db_session, User, Domain, Transaction
        
        db = get_db_session()
        user_count = db.query(User).count()
        domain_count = db.query(Domain).count()
        transaction_count = db.query(Transaction).count()
        db.close()
        
        logger.info(f"✅ Database Layer: {user_count} users, {domain_count} domains, {transaction_count} transactions")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database Layer Failed: {e}")
        return False

def test_repository_integration():
    """Test repository layer with dependency injection fixes"""
    try:
        from fresh_database import get_db_session
        from app.repositories.domain_repo import DomainRepository
        from app.repositories.user_repo import UserRepository
        from app.repositories.wallet_repo import WalletRepository
        
        db = get_db_session()
        
        # Test repository initialization
        domain_repo = DomainRepository(db)
        user_repo = UserRepository(db)
        wallet_repo = WalletRepository(db)
        
        # Test repository methods
        all_domains = domain_repo.get_all_domains()
        all_users = user_repo.get_all_users()
        
        db.close()
        
        logger.info(f"✅ Repository Layer: DomainRepository ({len(all_domains)} domains), UserRepository ({len(all_users)} users), WalletRepository")
        return True
        
    except Exception as e:
        logger.error(f"❌ Repository Layer Failed: {e}")
        return False

def test_service_integration():
    """Test service layer with fixed dependency injection"""
    try:
        from fresh_database import get_db_session
        from app.services.user_service import UserService
        from app.services.domain_service import DomainService
        from app.services.wallet_service import WalletService
        
        db = get_db_session()
        
        # Test service initialization with dependency injection
        user_service = UserService(db)
        domain_service = DomainService(db)
        wallet_service = WalletService(db)
        
        db.close()
        
        logger.info(f"✅ Service Layer: UserService, DomainService, WalletService (all initialized with dependency injection)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service Layer Failed: {e}")
        return False

def test_api_integration():
    """Test API layer imports"""
    try:
        from app.core.openprovider import OpenProviderAPI
        from app.core.cloudflare import CloudflareAPI
        
        # Test API initialization
        openprovider_api = OpenProviderAPI()
        cloudflare_api = CloudflareAPI()
        
        logger.info(f"✅ API Layer: OpenProviderAPI, CloudflareAPI (both initialized)")
        return True
        
    except Exception as e:
        logger.error(f"❌ API Layer Failed: {e}")
        return False

def main():
    """Run comprehensive integration test"""
    logger.info("🚀 NOMADLY3 INTEGRATION TEST - DEPENDENCY INJECTION FIXES")
    logger.info("=" * 70)
    
    results = []
    
    # Test each layer
    results.append(("Database Layer", test_database_integration()))
    results.append(("Repository Layer", test_repository_integration()))
    results.append(("Service Layer", test_service_integration()))
    results.append(("API Layer", test_api_integration()))
    
    # Calculate success rate
    successful = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (successful / total) * 100
    
    logger.info("=" * 70)
    logger.info(f"🎯 INTEGRATION TEST RESULTS:")
    logger.info(f"   Success Rate: {success_rate:.1f}% ({successful}/{total})")
    
    for layer_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"   {layer_name}: {status}")
    
    if success_rate == 100:
        logger.info("🎉 ALL LAYERS OPERATIONAL - INTEGRATION SUCCESS!")
        return 0
    else:
        logger.info("⚠️  INTEGRATION ISSUES DETECTED - Some layers need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())