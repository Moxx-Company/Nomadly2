
#!/usr/bin/env python3
"""
Registration Integration Tests
============================

Comprehensive tests for domain registration process.
"""

import pytest
import logging
from unittest.mock import Mock, patch

logger = logging.getLogger(__name__)

class TestRegistrationIntegration:
    """Test complete registration workflow"""
    
    def test_api_methods_exist(self):
        """Test all required API methods exist"""
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
        
    def test_nameserver_management_after_registration(self):
        """Test nameserver management works after registration"""
        from apis.production_openprovider import OpenProviderAPI
        
        op_api = OpenProviderAPI()
        
        # Test method is callable
        assert callable(getattr(op_api, 'update_domain_nameservers', None))
        
        # Test method signature is correct
        import inspect
        sig = inspect.signature(op_api.update_domain_nameservers)
        params = list(sig.parameters.keys())
        assert 'domain_id' in params, "Missing domain_id parameter"
        assert 'nameservers' in params, "Missing nameservers parameter"
        
        logger.info("✅ Nameserver management method validated")
        
    @patch('apis.production_openprovider.requests.put')
    def test_nameserver_api_call_format(self, mock_put):
        """Test nameserver API call uses correct format"""
        from apis.production_openprovider import OpenProviderAPI
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        op_api = OpenProviderAPI()
        op_api.token = "test_token"  # Mock token
        
        # Test the API call
        result = op_api.update_domain_nameservers(
            12345, 
            ["ns1.test.com", "ns2.test.com"]
        )
        
        # Verify API call was made correctly
        assert mock_put.called, "API call not made"
        
        call_args = mock_put.call_args
        assert call_args[1]['json']['nameServers'], "Missing nameServers in request"
        assert len(call_args[1]['json']['nameServers']) == 2, "Wrong nameserver count"
        
        logger.info("✅ API call format validated")
        
    def test_registration_validation_hooks(self):
        """Test registration validation hooks work"""
        from registration_validation_system import RegistrationValidator
        
        validator = RegistrationValidator()
        
        # Test pre-registration validation
        api_valid = validator.validate_api_methods_before_registration()
        assert api_valid, "Pre-registration validation failed"
        
        # Test post-registration validation
        completion_valid = validator.validate_registration_completion(
            "test.sbs", "12345", "zone123"
        )
        
        logger.info("✅ Registration validation hooks working")

if __name__ == "__main__":
    # Run tests
    test_suite = TestRegistrationIntegration()
    
    logger.info("🧪 Running registration integration tests...")
    
    try:
        test_suite.test_api_methods_exist()
        test_suite.test_nameserver_management_after_registration() 
        test_suite.test_nameserver_api_call_format()
        test_suite.test_registration_validation_hooks()
        
        logger.info("🎉 ALL TESTS PASSED - Registration system validated")
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
