"""
Nameserver Management System for Nomadly2 Bot
Handles nameserver operations and domain delegation
"""

import logging
from typing import Dict, List, Optional, Any
from api_services import get_api_manager
from database import get_db_manager

logger = logging.getLogger(__name__)


class NameserverManager:
    """Manages nameserver operations and domain delegation"""

    # Dynamic Cloudflare nameservers (no hardcoding)
    @staticmethod
    async def get_real_cloudflare_nameservers(domain: str = None) -> List[str]:
        """Get real Cloudflare nameservers for domain or defaults"""
        try:
            if domain:
                from apis.production_cloudflare import CloudflareAPI
                cf_api = CloudflareAPI()
                cloudflare_zone_id = cf_api._get_zone_id(domain)
                if cloudflare_zone_id:
                    import requests
                    headers = {
                        'Authorization': f'Bearer {cf_api.api_token}',
                        'Content-Type': 'application/json'
                    }
                    url = f"https://api.cloudflare.com/client/v4/zones/{cloudflare_zone_id}"
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        zone_data = response.json()
                        if zone_data.get('success'):
                            real_ns = zone_data['result'].get('name_servers', [])
                            if real_ns:
                                return real_ns
            # Fallback only if API fails
            return [await get_real_cloudflare_nameservers(domain_name)]
        except Exception as e:
            logger.error(f"Error getting real Cloudflare nameservers: {e}")
            return [await get_real_cloudflare_nameservers(domain_name)]

    # OpenProvider default nameservers
    OPENPROVIDER_NS = [
        "ns1.openprovider.nl",
        "ns2.openprovider.be",
        "ns3.openprovider.eu",
    ]

    def __init__(self):
        self.api_manager = get_api_manager()
        self.db = get_db_manager()

    async def get_domain_nameservers(self, domain: str) -> Dict[str, Any]:
        """Get current nameserver configuration for a domain"""
        try:
            # First, try to get nameservers from database
            # Try different user IDs to find the domain
            domain_record = None
            for user_id in [0, 5590563715]:  # Try common user IDs
                try:
                    domains = self.db.get_user_domains(user_id)
                    for d in domains:
                        if d.domain_name == domain:
                            domain_record = d
                            break
                    if domain_record:
                        break
                except Exception as e:
                    logger.error(f"Error getting domains for user {user_id}: {e}")
                    continue

            if domain_record and domain_record.nameservers:
                # Parse nameservers from database
                try:
                    import json

                    nameservers_raw = domain_record.nameservers
                    logger.info(f"Raw nameservers data for {domain}: {nameservers_raw}")

                    # Handle different JSON formats and corrupted data
                    if nameservers_raw.startswith("["):
                        nameservers = json.loads(nameservers_raw.replace("'", '"'))
                    elif nameservers_raw.startswith('"['):
                        # Double-encoded JSON
                        nameservers = json.loads(json.loads(nameservers_raw))
                    elif nameservers_raw.startswith('"') and "," in nameservers_raw:
                        # Handle corrupted format: '"ns1.cloudflare.com,ns2.cloudflare.com"'
                        clean_data = nameservers_raw.strip('"')
                        nameservers = [ns.strip() for ns in clean_data.split(",")]
                    else:
                        nameservers = [nameservers_raw]

                    # Determine mode based on nameservers
                    if any("cloudflare.com" in ns for ns in nameservers):
                        mode = "cloudflare"
                        mode_display = "Cloudflare DNS"
                    elif any("openprovider" in ns.lower() for ns in nameservers):
                        mode = "openprovider"
                        mode_display = "Registrar Default"
                    else:
                        mode = "custom"
                        mode_display = "Custom DNS"

                    logger.info(
                        f"Retrieved nameservers from database for {domain}: {nameservers}"
                    )

                    return {
                        "domain": domain,
                        "nameservers": nameservers,
                        "mode": mode,
                        "mode_display": mode_display,
                    }

                except Exception as parse_error:
                    logger.error(f"Error parsing nameservers: {parse_error}")

            # Skip API fallback for now - database should have the data
            logger.info(f"No nameserver data found in database for {domain}")

            # Final fallback
            return {
                "domain": domain,
                "nameservers": [],
                "mode": "unknown",
                "mode_display": "Unknown",
            }

        except Exception as e:
            logger.error(f"Error getting nameservers for {domain}: {e}")
            return {
                "domain": domain,
                "nameservers": [],
                "mode": "unknown",
                "mode_display": "Unknown",
            }

    async def set_nameserver_mode(
        self, domain: str, mode: str, custom_ns: Optional[List[str]] = None
    ) -> bool:
        """Set nameserver mode for a domain with smart Cloudflare zone detection"""
        try:
            if mode == "cloudflare":
                # Smart Cloudflare setup: Check if zone exists first
                logger.info(f"🔍 Checking if Cloudflare zone exists for {domain}")
                cloudflare_zone_id = await self._get_or_create_cloudflare_zone(domain)
                if cloudflare_zone_id:
                    cf_ns = await self.api_manager.cloudflare.get_nameservers(cloudflare_zone_id)
                    if cf_ns:
                        # Update OpenProvider nameservers
                        success = await self._update_openprovider_nameservers(domain, cf_ns)
                        if success:
                            # Update database
                            await self._update_database_nameservers(domain, cf_ns, "cloudflare")
                            logger.info(f"✅ Successfully switched {domain} to Cloudflare DNS")
                            return True
                else:
                    logger.error(f"❌ Failed to create/get Cloudflare zone for {domain}")
                    return False
            elif mode == "custom" and custom_ns:
                # Validate custom nameservers
                if not self._validate_nameservers(custom_ns):
                    logger.error(f"❌ Invalid custom nameservers: {custom_ns}")
                    return False
                
                # Update OpenProvider nameservers
                success = await self._update_openprovider_nameservers(domain, custom_ns)
                if success:
                    # Update database
                    await self._update_database_nameservers(domain, custom_ns, "custom")
                    logger.info(f"✅ Successfully switched {domain} to custom nameservers: {custom_ns}")
                    return True
            else:
                logger.error(f"❌ Invalid nameserver mode: {mode} or missing custom nameservers")
                return False

        except Exception as e:
            logger.error(f"❌ Error setting nameserver mode for {domain}: {e}")
            return False

    async def update_custom_nameservers(
        self, domain: str, nameservers: List[str]
    ) -> bool:
        """Update custom nameservers for a domain"""
        try:
            # Validate nameservers
            if not self._validate_nameservers(nameservers):
                return False

            # Update at registrar
            success = self.api_manager.openprovider.update_nameservers(
                domain, nameservers
            )

            if success:
                # Update database
                await self._update_domain_nameservers(domain, nameservers, "custom")

            return success

        except Exception as e:
            logger.error(f"Error updating custom nameservers for {domain}: {e}")
            return False

    async def _get_or_create_cloudflare_zone(self, domain: str) -> Optional[str]:
        """Check if Cloudflare zone exists, create if not"""
        try:
            from apis.production_cloudflare import CloudflareAPI
            import os
            
            cloudflare = CloudflareAPI(
                email=os.getenv("CLOUDFLARE_EMAIL"),
                api_key=os.getenv("CLOUDFLARE_GLOBAL_API_KEY"),
                api_token=os.getenv("CLOUDFLARE_API_TOKEN"),
            )
            
            # Check if zone already exists
            existing_zone_id = cloudflare.get_zone_by_domain(domain)
            if existing_zone_id:
                logger.info(f"✅ Found existing Cloudflare zone for {domain}: {existing_zone_id}")
                return existing_zone_id
            
            # Zone doesn't exist, create new one
            logger.info(f"🌐 Creating new Cloudflare zone for {domain}")
            success, cloudflare_zone_id, nameservers = cloudflare.create_zone(domain)
            if success and cloudflare_zone_id:
                logger.info(f"✅ Created new Cloudflare zone: {cloudflare_zone_id}")
                
                # Add default A record pointing to our server
                server_ip = os.getenv("SERVER_PUBLIC_IP", "89.117.27.176")
                a_record_data = {
                    "type": "A",
                    "name": domain,
                    "content": server_ip,
                    "ttl": 300
                }
                await cloudflare.create_dns_record(cloudflare_zone_id=cloudflare_zone_id, record_data=a_record_data)
                logger.info(f"✅ Added A record for {domain} → {server_ip}")
                
                return cloudflare_zone_id
            else:
                logger.error(f"❌ Failed to create Cloudflare zone for {domain}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error managing Cloudflare zone for {domain}: {e}")
            return None

    async def _update_openprovider_nameservers(self, domain: str, nameservers: List[str]) -> bool:
        """Update nameservers in OpenProvider"""
        try:
            from apis.production_openprovider import OpenProviderAPI
            from database import get_db_manager
            
            # Get OpenProvider domain ID from database
            db_manager = get_db_manager()
            domain_record = None
            
            # Try different user IDs to find the domain
            for user_id in [0, 5590563715]:
                try:
                    domains = db_manager.get_user_domains(user_id)
                    for d in domains:
                        if d.domain_name == domain:
                            domain_record = d
                            break
                    if domain_record:
                        break
                except Exception as e:
                    logger.error(f"Error getting domains for user {user_id}: {e}")
                    continue
            
            if not domain_record or not domain_record.openprovider_domain_id:
                logger.error(f"❌ No OpenProvider domain ID found for {domain}")
                return False
            
            # Update nameservers via OpenProvider API
            api = OpenProviderAPI()
            success = api.update_domain_nameservers(
                domain_id=domain_record.openprovider_domain_id,
                nameservers=nameservers
            )
            
            if success:
                logger.info(f"✅ Updated OpenProvider nameservers for {domain}")
                return True
            else:
                logger.error(f"❌ Failed to update OpenProvider nameservers for {domain}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating OpenProvider nameservers: {e}")
            return False

    async def _update_database_nameservers(self, domain: str, nameservers: List[str], mode: str) -> bool:
        """Update nameserver information in database"""
        try:
            import json
            from database import get_db_manager
            
            db_manager = get_db_manager()
            
            # Find domain record
            domain_record = None
            for user_id in [0, 5590563715]:
                try:
                    domains = db_manager.get_user_domains(user_id)
                    for d in domains:
                        if d.domain_name == domain:
                            domain_record = d
                            break
                    if domain_record:
                        break
                except Exception as e:
                    continue
            
            if not domain_record:
                logger.error(f"❌ Domain record not found for {domain}")
                return False
            
            # Update nameserver information
            nameservers_json = json.dumps(nameservers)
            
            # Update the database record
            session = db_manager.get_session()
            try:
                from database import RegisteredDomain
                
                # Update the record
                session.query(RegisteredDomain).filter_by(
                    id=domain_record.id
                ).update({
                    'nameservers': nameservers_json,
                    'nameserver_mode': mode
                })
                session.commit()
                
                logger.info(f"✅ Updated database nameservers for {domain}: {mode}")
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ Error updating database nameservers: {e}")
            return False

    def _validate_nameservers(self, nameservers: List[str]) -> bool:
        """Validate custom nameservers format"""
        try:
            if not nameservers or len(nameservers) < 2:
                logger.error("❌ At least 2 nameservers required")
                return False
            
            if len(nameservers) > 4:
                logger.error("❌ Maximum 4 nameservers allowed")
                return False
            
            import re
            hostname_pattern = re.compile(
                r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            )
            
            for ns in nameservers:
                if not ns or not hostname_pattern.match(ns.strip()):
                    logger.error(f"❌ Invalid nameserver format: {ns}")
                    return False
                
                if len(ns.strip()) > 253:
                    logger.error(f"❌ Nameserver too long: {ns}")
                    return False
            
            logger.info(f"✅ Nameservers validated: {nameservers}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating nameservers: {e}")
            return False

    async def revert_to_cloudflare(self, domain: str) -> bool:
        """Revert domain to Cloudflare nameservers"""
        return await self.set_nameserver_mode(domain, "cloudflare")

    async def get_nameserver_options(self) -> Dict[str, Any]:
        """Get available nameserver options"""
        return {
            "cloudflare": {
                "name": "Cloudflare Nameservers",
                "description": "Use Cloudflare for DNS management (Recommended)",
                "nameservers": await self.get_real_cloudflare_nameservers(domain),
                "benefits": [
                    "Full DNS management through bot",
                    "Fast global propagation",
                    "DDoS protection included",
                    "Free SSL certificates",
                ],
            },
            "custom": {
                "name": "Custom Nameservers",
                "description": "Use your own nameserver configuration",
                "nameservers": [],
                "benefits": [
                    "Full control over DNS",
                    "Use existing DNS provider",
                    "Custom DNS configurations",
                ],
            },
        }

    def _determine_ns_mode(self, nameservers: List[str]) -> str:
        """Determine nameserver mode based on current nameservers"""
        if not nameservers:
            return "unknown"

        # Check if Cloudflare nameservers
        cf_domains = ["cloudflare.com"]
        if any(any(cf_domain in ns for cf_domain in cf_domains) for ns in nameservers):
            return "cloudflare"

        # Check if OpenProvider nameservers
        op_domains = ["openprovider.nl", "openprovider.be", "openprovider.eu"]
        if any(any(op_domain in ns for op_domain in op_domains) for ns in nameservers):
            return "openprovider"

        # Otherwise custom
        return "custom"

    def _get_mode_display(self, mode: str) -> str:
        """Get display name for nameserver mode"""
        modes = {
            "cloudflare": "☁️ Cloudflare DNS",
            "custom": "🛠️ Custom Nameservers",
            "unknown": "❓ Unknown",
        }
        return modes.get(mode, "Unknown")

    def _validate_nameservers(self, nameservers: List[str]) -> bool:
        """Validate nameserver format"""
        if not nameservers or len(nameservers) < 1 or len(nameservers) > 4:
            return False

        for ns in nameservers:
            # Basic domain validation
            if not ns or "." not in ns or len(ns) < 4:
                return False

        return True

    async def _setup_registrar_default_cloudflare(self, domain: str) -> List[str]:
        """Setup Cloudflare zone for registrar default option"""
        try:
            from apis.production_cloudflare import CloudflareAPI

            cloudflare = CloudflareAPI()

            # Check if domain already exists in Cloudflare
            zone_result = cloudflare.get_zone_by_domain(domain)

            if zone_result and zone_result.get("success"):
                # Domain exists - get existing nameservers
                zone_data = zone_result.get("zone", {})
                nameservers = zone_data.get("name_servers", [])
                logger.info(
                    f"Domain {domain} found in Cloudflare with nameservers: {nameservers}"
                )
                return nameservers
            else:
                # Domain doesn't exist - create zone and A record
                logger.info(f"Creating Cloudflare zone for {domain}")

                # Create zone
                create_result = cloudflare.create_zone(domain)
                if not create_result.get("success"):
                    logger.error(f"Failed to create Cloudflare zone for {domain}")
                    return await self.get_real_cloudflare_nameservers(domain)  # Fallback

                zone_data = create_result.get("zone", {})
                nameservers = zone_data.get("name_servers", [])
                cloudflare_zone_id = zone_data.get("id")

                # Add A record pointing to default IP
                if cloudflare_zone_id:
                    a_record_result = cloudflare.create_dns_record(
                        cloudflare_zone_id=cloudflare_zone_id,
                        record_type="A",
                        name="@",
                        content="93.184.216.34",  # Example.com IP for parking
                        ttl=3600,
                    )

                    if a_record_result.get("success"):
                        logger.info(f"Added A record for {domain}")
                    else:
                        logger.warning(f"Failed to add A record for {domain}")

                logger.info(
                    f"Created Cloudflare zone for {domain} with nameservers: {nameservers}"
                )
                return nameservers

        except Exception as e:
            logger.error(
                f"Error setting up Cloudflare for registrar default {domain}: {e}"
            )
            return await self.get_real_cloudflare_nameservers(domain)  # Fallback to default Cloudflare nameservers

    async def _update_domain_nameservers(
        self, domain: str, nameservers: List[str], mode: str
    ):
        """Update domain nameserver info in database"""
        try:
            # Update domain record using the database manager
            self.db.update_domain_nameservers(domain, nameservers, mode)

        except Exception as e:
            logger.error(f"Error updating domain nameservers in database: {e}")


# Global nameserver manager instance
_nameserver_manager = None


def get_nameserver_manager() -> NameserverManager:
    """Get global nameserver manager instance"""
    global _nameserver_manager
    if _nameserver_manager is None:
        _nameserver_manager = NameserverManager()
    return _nameserver_manager
