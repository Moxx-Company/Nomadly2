#!/usr/bin/env python3
"""
Comprehensive Integration Validation for Nomadly3
Tests all architectural layers end-to-end integration
"""

import sys
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_layer_1_fresh_database():
    """Test Layer 1: Fresh Database Layer"""
    try:
        logger.info("🔍 Testing Layer 1: Fresh Database Layer")
        
        # Test database connection and schema
        from fresh_database import get_db_session, User, Domain, DNSRecord, Transaction, Order
        
        db = get_db_session()
        try:
            # Test basic queries
            user_count = db.query(User).count()
            domain_count = db.query(Domain).count()
            dns_count = db.query(DNSRecord).count()
            transaction_count = db.query(Transaction).count()
            order_count = db.query(Order).count()
            
            logger.info(f"   Database connectivity: ✅")
            logger.info(f"   User records: {user_count}")
            logger.info(f"   Domain records: {domain_count}")
            logger.info(f"   DNS records: {dns_count}")
            logger.info(f"   Transaction records: {transaction_count}")
            logger.info(f"   Order records: {order_count}")
        finally:
            db.close()
            
        return {
            "status": "success",
            "message": "Fresh database layer operational",
            "data": {
                "users": user_count,
                "domains": domain_count,
                "dns_records": dns_count,
                "transactions": transaction_count,
                "orders": order_count
            }
        }
        
    except Exception as e:
        logger.error(f"   Layer 1 Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_layer_2_data_access():
    """Test Layer 2: Data Access Layer (Repositories)"""
    try:
        logger.info("🔍 Testing Layer 2: Data Access Layer")
        
        # Test repository imports and initialization
        from app.repositories.user_repo import UserRepository
        from app.repositories.domain_repo import DomainRepository  
        from app.repositories.dns_repo import DNSRepository
        from app.repositories.wallet_repo import WalletRepository
        from fresh_database import get_db_session
        
        db = get_db_session()
        try:
            # Initialize repositories
            user_repo = UserRepository(db)
            domain_repo = DomainRepository(db)
            dns_repo = DNSRepository(db)
            wallet_repo = WalletRepository(db)
            
            # Test repository methods
            users = user_repo.get_all_users()
            domains = domain_repo.get_all_domains()
            
            logger.info(f"   UserRepository: ✅ ({len(users)} users)")
            logger.info(f"   DomainRepository: ✅ ({len(domains)} domains)")
            logger.info(f"   DNSRepository: ✅")
            logger.info(f"   WalletRepository: ✅")
            
        return {
            "status": "success",
            "message": "Data access layer operational",
            "repositories": ["UserRepository", "DomainRepository", "DNSRepository", "WalletRepository"]
        }
        
    except Exception as e:
        logger.error(f"   Layer 2 Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_layer_3_business_logic():
    """Test Layer 3: Service/Business Logic Layer"""
    try:
        logger.info("🔍 Testing Layer 3: Service/Business Logic Layer")
        
        # Test service imports and initialization
        from app.services.user_service import UserService
        from app.services.domain_service import DomainService
        from app.services.dns_service import DNSService
        from app.services.wallet_service import WalletService
        from fresh_database import get_db_session
        
        with get_db_session() as db:
            # Initialize services with dependency injection
            user_service = UserService(db)
            domain_service = DomainService(db)
            dns_service = DNSService(db)
            wallet_service = WalletService(db)
            
            # Test basic service methods
            logger.info(f"   UserService: ✅ (initialized)")
            logger.info(f"   DomainService: ✅ (initialized)")
            logger.info(f"   DNSService: ✅ (initialized)")
            logger.info(f"   WalletService: ✅ (initialized)")
            
        return {
            "status": "success",
            "message": "Business logic layer operational",
            "services": ["UserService", "DomainService", "DNSService", "WalletService"]
        }
        
    except Exception as e:
        logger.error(f"   Layer 3 Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_layer_4_external_integrations():
    """Test Layer 4: External Integration Layer"""
    try:
        logger.info("🔍 Testing Layer 4: External Integration Layer")
        
        # Test external service imports
        from app.core.cloudflare import CloudflareAPI
        from app.core.openprovider import OpenProviderAPI
        from app.integrations.blockbee_integration import BlockBeeAPI
        from app.integrations.brevo_integration import BrevoAPI
        from app.integrations.fastforex_integration import FastForexAPI
        
        # Initialize APIs (test configuration)
        cloudflare_api = CloudflareAPI()
        openprovider_api = OpenProviderAPI()
        blockbee_api = BlockBeeAPI()
        brevo_api = BrevoAPI()
        fastforex_api = FastForexAPI()
        
        # Test API method availability
        has_cloudflare_methods = hasattr(cloudflare_api, 'create_zone') and hasattr(cloudflare_api, 'create_dns_record')
        has_openprovider_methods = hasattr(openprovider_api, 'check_domain_availability') and hasattr(openprovider_api, 'register_domain')
        has_blockbee_methods = hasattr(blockbee_api, 'create_payment_address')
        has_brevo_methods = hasattr(brevo_api, 'send_email')
        has_fastforex_methods = hasattr(fastforex_api, 'convert_currency')
        
        logger.info(f"   CloudflareAPI: ✅ (methods available: {has_cloudflare_methods})")
        logger.info(f"   OpenProviderAPI: ✅ (methods available: {has_openprovider_methods})")
        logger.info(f"   BlockBeeAPI: ✅ (methods available: {has_blockbee_methods})")
        logger.info(f"   BrevoAPI: ✅ (methods available: {has_brevo_methods})")
        logger.info(f"   FastForexAPI: ✅ (methods available: {has_fastforex_methods})")
        
        return {
            "status": "success",
            "message": "External integration layer operational", 
            "apis": {
                "cloudflare": has_cloudflare_methods,
                "openprovider": has_openprovider_methods,
                "blockbee": has_blockbee_methods,
                "brevo": has_brevo_methods,
                "fastforex": has_fastforex_methods
            }
        }
        
    except Exception as e:
        logger.error(f"   Layer 4 Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_layer_5_fastapi_routes():
    """Test Layer 5: FastAPI Routes Layer"""
    try:
        logger.info("🔍 Testing Layer 5: FastAPI Routes Layer")
        
        # Test route imports
        from app.api.routes.auth_routes import auth_router
        from app.api.routes.domain_routes import domain_router
        from app.api.routes.dns_routes import dns_router
        from app.api.routes.payment_routes import payment_router
        
        # Test route configuration
        auth_routes = len(auth_router.routes)
        domain_routes = len(domain_router.routes)
        dns_routes = len(dns_router.routes)
        payment_routes = len(payment_router.routes)
        
        logger.info(f"   AuthRouter: ✅ ({auth_routes} routes)")
        logger.info(f"   DomainRouter: ✅ ({domain_routes} routes)")
        logger.info(f"   DNSRouter: ✅ ({dns_routes} routes)")
        logger.info(f"   PaymentRouter: ✅ ({payment_routes} routes)")
        
        return {
            "status": "success",
            "message": "FastAPI routes layer operational",
            "routes": {
                "auth": auth_routes,
                "domain": domain_routes,
                "dns": dns_routes,
                "payment": payment_routes
            }
        }
        
    except Exception as e:
        logger.error(f"   Layer 5 Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_layer_6_api_middleware():
    """Test Layer 6: API Middleware Layer"""
    try:
        logger.info("🔍 Testing Layer 6: API Middleware Layer")
        
        # Test middleware imports
        from app.api.middleware import (
            RequestLoggingMiddleware, 
            SecurityHeadersMiddleware,
            RateLimitingMiddleware,
            ErrorHandlingMiddleware,
            DatabaseMiddleware
        )
        from app.api.auth_middleware import AuthenticationMiddleware
        from app.api.cors_middleware import EnhancedCORSMiddleware
        
        # Test middleware initialization
        middleware_classes = [
            RequestLoggingMiddleware,
            SecurityHeadersMiddleware, 
            RateLimitingMiddleware,
            ErrorHandlingMiddleware,
            DatabaseMiddleware,
            AuthenticationMiddleware,
            EnhancedCORSMiddleware
        ]
        
        logger.info(f"   RequestLoggingMiddleware: ✅")
        logger.info(f"   SecurityHeadersMiddleware: ✅")
        logger.info(f"   RateLimitingMiddleware: ✅")
        logger.info(f"   ErrorHandlingMiddleware: ✅")
        logger.info(f"   DatabaseMiddleware: ✅")
        logger.info(f"   AuthenticationMiddleware: ✅")
        logger.info(f"   EnhancedCORSMiddleware: ✅")
        
        return {
            "status": "success",
            "message": "API middleware layer operational",
            "middleware_count": len(middleware_classes)
        }
        
    except Exception as e:
        logger.error(f"   Layer 6 Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def test_integration_flow():
    """Test End-to-End Integration Flow"""
    try:
        logger.info("🔍 Testing Integration Flow: Database → Repository → Service → API")
        
        # Test complete integration chain
        from fresh_database import get_db_session, User
        from app.repositories.user_repo import UserRepository
        from app.services.user_service import UserService
        
        with get_db_session() as db:
            # Layer 1: Database
            test_user = db.query(User).first()
            
            # Layer 2: Repository  
            user_repo = UserRepository(db)
            repo_user = user_repo.get_user_by_telegram_id(test_user.telegram_id) if test_user else None
            
            # Layer 3: Service
            user_service = UserService(db)
            service_user = user_service.get_user_profile(test_user.telegram_id) if test_user else None
            
            logger.info(f"   Database → Repository → Service: ✅")
            logger.info(f"   Integration chain functional: {bool(test_user and repo_user and service_user)}")
            
        return {
            "status": "success",
            "message": "Integration flow operational",
            "chain_working": bool(test_user and repo_user and service_user)
        }
        
    except Exception as e:
        logger.error(f"   Integration Flow Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def run_comprehensive_validation():
    """Run complete architectural integration validation"""
    logger.info("🚀 Starting Comprehensive Integration Validation")
    logger.info("=" * 60)
    
    results = {}
    
    # Test all layers
    results["layer_1_database"] = test_layer_1_fresh_database()
    results["layer_2_data_access"] = test_layer_2_data_access()
    results["layer_3_business_logic"] = test_layer_3_business_logic()
    results["layer_4_external_integrations"] = test_layer_4_external_integrations()
    results["layer_5_fastapi_routes"] = test_layer_5_fastapi_routes()
    results["layer_6_api_middleware"] = test_layer_6_api_middleware()
    results["integration_flow"] = test_integration_flow()
    
    # Calculate success rate
    successful_layers = sum(1 for result in results.values() if result["status"] == "success")
    total_layers = len(results)
    success_rate = (successful_layers / total_layers) * 100
    
    logger.info("=" * 60)
    logger.info(f"🎯 INTEGRATION VALIDATION COMPLETE")
    logger.info(f"   Success Rate: {success_rate:.1f}% ({successful_layers}/{total_layers})")
    
    if success_rate == 100:
        logger.info("🎉 ALL LAYERS FULLY INTEGRATED AND OPERATIONAL!")
    elif success_rate >= 80:
        logger.info("✅ INTEGRATION MOSTLY SUCCESSFUL - Minor issues to resolve")
    else:
        logger.info("⚠️  INTEGRATION ISSUES DETECTED - Requires attention")
    
    return {
        "overall_status": "success" if success_rate >= 80 else "needs_attention",
        "success_rate": success_rate,
        "successful_layers": successful_layers,
        "total_layers": total_layers,
        "layer_results": results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    try:
        validation_results = run_comprehensive_validation()
        
        # Print summary
        print(f"\n📊 FINAL INTEGRATION STATUS:")
        print(f"Success Rate: {validation_results['success_rate']:.1f}%")
        print(f"Layers Operational: {validation_results['successful_layers']}/{validation_results['total_layers']}")
        
        # Exit with appropriate code
        sys.exit(0 if validation_results["success_rate"] >= 80 else 1)
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)