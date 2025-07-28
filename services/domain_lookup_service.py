"""
Domain Lookup Service
Provides compatibility layer for domain registration functionality
"""

import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


class DomainLookupService:
    """Domain lookup service using existing APIs"""

    def __init__(self):
        # Import the existing domain services
        try:
            from apis.domain_service import get_domain_service

            self.domain_service = get_domain_service()
            logger.info("✅ Domain lookup service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize domain service: {e}")
            # Import direct DomainService as fallback
            try:
                from apis.domain_service import DomainService

                self.domain_service = DomainService()
                logger.info("✅ Fallback domain service initialized")
            except Exception as e2:
                logger.error(f"❌ Fallback also failed: {e2}")
                self.domain_service = None

    def check_domain_availability(self, domain: str) -> dict:
        """Check domain availability using existing domain service"""
        try:
            if self.domain_service:
                return self.domain_service.check_domain_availability(domain)
            else:
                logger.error("Domain service not available")
                return {
                    "available": False,
                    "error": "Domain service not initialized",
                    "price": 0,
                }
        except Exception as e:
            logger.error(f"Error checking domain availability: {e}")
            return {"available": False, "error": str(e), "price": 0}

    def get_domain_info(self, domain: str) -> dict:
        """Get domain information"""
        try:
            if self.domain_service:
                return self.domain_service.get_domain_info(domain)
            else:
                return {
                    "domain": domain,
                    "available": False,
                    "price": 2.99,  # Default SBS price
                    "error": "Service unavailable",
                }
        except Exception as e:
            logger.error(f"Error getting domain info: {e}")
            return {
                "domain": domain,
                "available": True,  # Default to available for fallback
                "price": 2.99,
                "error": str(e),
            }


# Compatibility function
def get_domain_lookup_service():
    """Get domain lookup service instance"""
    return DomainLookupService()
