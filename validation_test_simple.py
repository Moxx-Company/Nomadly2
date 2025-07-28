#!/usr/bin/env python3
"""
Simple Validation Test - No External Dependencies
=================================================

Test registration validation system without pytest.
"""

import sys
import logging

# Add project root to path
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_methods_exist():
    """Test all required API methods exist"""
    logger.info("🧪 Testing API methods exist...")
    
    try:
        from apis.production_openprovider import OpenProviderAPI
        from apis.production_cloudflare import CloudflareAPI
        
        # Test OpenProvider methods
        op_api = OpenProviderAPI()
        assert hasattr(op_api, 'update_domain_nameservers'), "Missing update_domain_nameservers"
        assert hasattr(op_api, 'update_nameservers'), "Missing update_nameservers"
        assert hasattr(op_api, '_authenticate'), "Missing authentication"
        
        # Test Cloudflare methods
        cf_api = CloudflareAPI()
        assert hasattr(cf_api, 'create_zone'), "Missing create_zone"
        assert hasattr(cf_api, 'get_nameservers'), "Missing get_nameservers"
        
        logger.info("✅ All API methods exist")
        return True
        
    except Exception as e:
        logger.error(f"❌ API methods test failed: {e}")
        return False

def test_nameserver_method_signature():
    """Test nameserver management method has correct signature"""
    logger.info("🧪 Testing nameserver method signature...")
    
    try:
        from apis.production_openprovider import OpenProviderAPI
        import inspect
        
        op_api = OpenProviderAPI()
        
        # Test method is callable
        assert callable(getattr(op_api, 'update_domain_nameservers', None))
        
        # Test method signature is correct
        sig = inspect.signature(op_api.update_domain_nameservers)
        params = list(sig.parameters.keys())
        assert 'domain_id' in params, "Missing domain_id parameter"
        assert 'nameservers' in params, "Missing nameservers parameter"
        
        logger.info("✅ Nameserver method signature correct")
        return True
        
    except Exception as e:
        logger.error(f"❌ Method signature test failed: {e}")
        return False

def test_registration_validation():
    """Test registration validation system"""
    logger.info("🧪 Testing registration validation system...")
    
    try:
        from registration_validation_system import RegistrationValidator
        
        validator = RegistrationValidator()
        
        # Test pre-registration validation
        api_valid = validator.validate_api_methods_before_registration()
        assert api_valid, "Pre-registration validation failed"
        
        logger.info("✅ Registration validation system working")
        return True
        
    except Exception as e:
        logger.error(f"❌ Registration validation test failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    logger.info("🧪 RUNNING ALL VALIDATION TESTS")
    logger.info("=" * 50)
    
    tests = [
        ("API Methods Exist", test_api_methods_exist),
        ("Nameserver Method Signature", test_nameserver_method_signature),
        ("Registration Validation", test_registration_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"Running: {test_name}")
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ PASSED: {test_name}")
            else:
                failed += 1
                logger.error(f"❌ FAILED: {test_name}")
        except Exception as e:
            failed += 1
            logger.error(f"❌ ERROR in {test_name}: {e}")
        
        logger.info("")
    
    # Final summary
    total = passed + failed
    logger.info("🎯 TEST SUMMARY")
    logger.info("=" * 30)
    logger.info(f"Total tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED - System validated!")
        return True
    else:
        logger.error("⚠️ Some tests failed - Check logs above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)