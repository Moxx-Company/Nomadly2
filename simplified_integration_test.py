#!/usr/bin/env python3
"""
Simplified Integration Test - Works without FastAPI
Tests core components only
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connectivity():
    """Test database connection"""
    try:
        from database import get_db_manager
        db_manager = get_db_manager()
        connection = db_manager.create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        logger.info(f"✅ Database: {user_count} users found")
        return True
    except Exception as e:
        logger.error(f"❌ Database: {e}")
        return False

def test_openprovider_model():
    """Test OpenProviderContact model"""
    try:
        from app.models.openprovider_models import OpenProviderContact
        contact = OpenProviderContact.create_privacy_contact()
        logger.info(f"✅ OpenProviderContact: {contact.email}")
        return True
    except Exception as e:
        logger.error(f"❌ OpenProviderContact: {e}")
        return False

def test_external_apis():
    """Test external API configuration"""
    try:
        from app.core.cloudflare import CloudflareAPI
        from app.core.openprovider import OpenProviderAPI
        
        cf_api = CloudflareAPI()
        op_api = OpenProviderAPI()
        
        logger.info("✅ External APIs: Configured")
        return True
    except Exception as e:
        logger.error(f"❌ External APIs: {e}")
        return False

def main():
    """Run simplified integration test"""
    logger.info("🔍 Running Simplified Integration Test")
    
    tests = [
        ("Database Connectivity", test_database_connectivity),
        ("OpenProvider Models", test_openprovider_model),
        ("External APIs", test_external_apis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    success_rate = (passed / total) * 100
    logger.info(f"\n🎯 Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        logger.info("✅ Core integration working!")
        return True
    else:
        logger.error("❌ Core integration issues detected")
        return False

if __name__ == "__main__":
    main()
