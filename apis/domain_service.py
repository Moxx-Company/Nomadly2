import logging
from typing import Optional, Dict, Any
from .openprovider import OpenProviderAPI
from .connectreseller import ConnectResellerAPI

logger = logging.getLogger(__name__)


class DomainService:
    """Unified domain service that manages multiple providers"""

    def __init__(
        self,
        openprovider_username: str = None,
        openprovider_password: str = None,
        connectreseller_user: str = None,
        connectreseller_api_key: str = None,
    ):

        # Initialize providers
        self.openprovider = None
        self.connectreseller = None

        if openprovider_username and openprovider_password:
            self.openprovider = OpenProviderAPI(
                openprovider_username, openprovider_password
            )
            logger.info("OpenProvider initialized as primary domain provider")

        if connectreseller_user and connectreseller_api_key:
            self.connectreseller = ConnectResellerAPI(
                connectreseller_user, connectreseller_api_key
            )
            logger.info("ConnectReseller initialized as fallback domain provider")

    def check_domain_availability(self, domain: str) -> Optional[Dict[str, Any]]:
        """Check domain availability using primary provider with fallback"""

        # Try OpenProvider first (primary)
        if self.openprovider:
            try:
                result = self.openprovider.check_domain_availability(domain)
                if result:
                    logger.info(
                        f"Domain availability checked via OpenProvider for {domain}"
                    )
                    return result
            except Exception as e:
                logger.warning(
                    f"OpenProvider availability check failed for {domain}: {e}"
                )

        # Fallback to ConnectReseller
        if self.connectreseller:
            try:
                result = self.connectreseller.check_domain_availability(domain)
                if result:
                    logger.info(
                        f"Domain availability checked via ConnectReseller fallback for {domain}"
                    )
                    return result
            except Exception as e:
                logger.warning(
                    f"ConnectReseller availability check failed for {domain}: {e}"
                )

        # If both fail, return None
        logger.error(f"All domain providers failed for availability check: {domain}")
        return None

    def get_domain_price(self, domain: str) -> Optional[float]:
        """Get domain price using primary provider with fallback"""

        # Try OpenProvider first (primary)
        if self.openprovider:
            try:
                price = self.openprovider.get_domain_price(domain)
                if price is not None:
                    logger.info(
                        f"Domain price retrieved via OpenProvider for {domain}: ${price}"
                    )
                    return price
            except Exception as e:
                logger.warning(f"OpenProvider pricing failed for {domain}: {e}")

        # Fallback to ConnectReseller
        if self.connectreseller:
            try:
                price = self.connectreseller.get_domain_price(domain)
                if price is not None:
                    logger.info(
                        f"Domain price retrieved via ConnectReseller fallback for {domain}: ${price}"
                    )
                    return price
            except Exception as e:
                logger.warning(f"ConnectReseller pricing failed for {domain}: {e}")

        # If both fail, return None
        logger.error(f"All domain providers failed for pricing: {domain}")
        return None

    def get_active_provider(self) -> str:
        """Get the name of the currently active primary provider"""
        if self.openprovider:
            return "OpenProvider"
        elif self.connectreseller:
            return "ConnectReseller"
        else:
            return "No providers available"

    async def list_dns_records(self, domain_name: str) -> Dict[str, Any]:
        """List DNS records for a domain - delegate to DomainRegistrationService"""
        try:
            from apis.domain_registration import DomainRegistrationService

            dns_service = DomainRegistrationService()
            return await dns_service.list_dns_records(domain_name)
        except Exception as e:
            logger.error(f"Error listing DNS records via DomainService: {e}")
            return {"success": False, "error": str(e)}

    def update_dns_record(
        self,
        domain_name: str,
        record_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 300,
    ) -> Dict[str, Any]:
        """Update a DNS record - delegate to DomainRegistrationService"""
        try:
            from apis.domain_registration import DomainRegistrationService

            dns_service = DomainRegistrationService()
            # Note: update_dns_record is not async in DomainRegistrationService
            return dns_service.update_dns_record(
                domain_name, record_id, record_type, name, content, ttl
            )
        except Exception as e:
            logger.error(f"Error updating DNS record via DomainService: {e}")
            return {"success": False, "error": str(e)}

    async def delete_dns_record(
        self, domain_name: str, record_id: str
    ) -> Dict[str, Any]:
        """Delete a DNS record - delegate to DomainRegistrationService"""
        try:
            from apis.domain_registration import DomainRegistrationService

            dns_service = DomainRegistrationService()
            # Note: delete_dns_record is not async in DomainRegistrationService
            return dns_service.delete_dns_record(domain_name, record_id)
        except Exception as e:
            logger.error(f"Error deleting DNS record via DomainService: {e}")
            return {"success": False, "error": str(e)}


# Factory function for service instantiation
def get_domain_service():
    """Create and return domain service instance with credentials from environment"""
    import os

    openprovider_username = os.getenv("OPENPROVIDER_USERNAME")
    openprovider_password = os.getenv("OPENPROVIDER_PASSWORD")
    connectreseller_user = os.getenv("CONNECTRESELLER_USER")
    connectreseller_api_key = os.getenv("CONNECTRESELLER_API_KEY")

    return DomainService(
        openprovider_username=openprovider_username,
        openprovider_password=openprovider_password,
        connectreseller_user=connectreseller_user,
        connectreseller_api_key=connectreseller_api_key,
    )
