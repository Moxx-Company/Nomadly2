import os
import logging
from typing import Dict, Any, Optional
from apis.cloudflare import CloudflareAPI
from apis.openprovider import OpenProviderAPI

logger = logging.getLogger(__name__)


class DomainRegistrationService:
    """Complete domain registration service with DNS management"""

    def __init__(self):
        self.cloudflare = CloudflareAPI()
        self.openprovider = None
        self.server_ip = os.getenv("SERVER_PUBLIC_IP")

        # Initialize OpenProvider with credentials
        try:
            openprovider_user = os.getenv("OPENPROVIDER_USERNAME")
            openprovider_pass = os.getenv("OPENPROVIDER_PASSWORD")
            if openprovider_user and openprovider_pass:
                self.openprovider = OpenProviderAPI(
                    openprovider_user, openprovider_pass
                )
            else:
                logger.error("OpenProvider credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize OpenProvider: {e}")

    def register_complete_domain(
        self, domain_name: str, telegram_user_id: int, telegram_username: str
    ) -> Dict[str, Any]:
        """
        Complete domain registration workflow as specified:
        1. Create Cloudflare DNS zone first and get target nameservers
        2. Add A record pointing to server IP
        3. Get or create OpenProvider customer
        4. Register domain with OpenProvider using OpenProvider default nameservers initially
        5. Update domain nameservers to Cloudflare nameservers after registration
        """
        try:
            logger.info(f"Starting complete domain registration for {domain_name}")

            # Step 1: Create Cloudflare DNS zone first to get target nameservers
            logger.info(f"Step 1: Creating Cloudflare DNS zone for {domain_name}")
            zone_result = self.cloudflare.create_zone(domain_name)

            if not zone_result["success"]:
                return {
                    "success": False,
                    "step": "cloudflare_zone_creation",
                    "error": f"Failed to create Cloudflare zone: {zone_result['error']}",
                }

            cloudflare_zone_id = zone_result["zone_id"]
            cloudflare_nameservers = zone_result["name_servers"]
            logger.info(f"Cloudflare zone created successfully: {cloudflare_zone_id}")
            logger.info(f"Target nameservers: {cloudflare_nameservers}")

            # Step 2: Add A record pointing to server IP and enable HTTPS
            logger.info(
                f"Step 2: Adding A record for {domain_name} -> {self.server_ip}"
            )
            a_record_result = self.cloudflare.add_a_record(
                cloudflare_zone_id, domain_name, self.server_ip
            )

            if not a_record_result["success"]:
                logger.warning(f"Failed to add A record: {a_record_result['error']}")
                # Continue with registration - A record can be added later
                https_enabled = False
            else:
                logger.info(f"A record added successfully")

                # Step 2b: Enable HTTPS/SSL for the domain
                logger.info(f"Step 2b: Enabling HTTPS/SSL for {domain_name}")
                https_result = self.cloudflare.enable_ssl_tls(cloudflare_zone_id)

                if https_result["success"]:
                    logger.info(f"HTTPS/SSL enabled successfully for {domain_name}")
                    https_enabled = True
                else:
                    logger.warning(
                        f"Failed to enable HTTPS/SSL: {https_result.get('error', 'Unknown error')}"
                    )
                    https_enabled = False

            # Step 3: Get or create OpenProvider customer
            logger.info(
                f"Step 3: Getting/creating OpenProvider customer for user {telegram_user_id}"
            )
            customer_result = self._get_or_create_customer(
                telegram_user_id, telegram_username
            )

            if not customer_result["success"]:
                return {
                    "success": False,
                    "step": "openprovider_customer",
                    "error": customer_result["error"],
                }

            customer_id = customer_result["customer_id"]
            logger.info(f"Customer ready: {customer_id}")

            # Step 4: Register domain with OpenProvider using default nameservers initially
            logger.info(
                f"Step 4: Registering domain {domain_name} with OpenProvider (default nameservers)"
            )
            domain_result = self.openprovider.register_domain(
                domain_name,
                customer_id,
                name_servers=None,  # Use OpenProvider defaults initially - critical for registration
                period=1,
            )

            if not domain_result["success"]:
                return {
                    "success": False,
                    "step": "domain_registration",
                    "error": domain_result["error"],
                }

            logger.info(
                f"Domain {domain_name} registered successfully with OpenProvider"
            )

            # Step 5: Now update nameservers to Cloudflare using domain ID from registration
            logger.info(f"Step 5: Updating {domain_name} nameservers to Cloudflare")
            nameserver_update_success = False

            try:
                # Use domain ID from registration instead of domain name lookup
                domain_id = domain_result.get("domain_id")
                if domain_id:
                    logger.info(f"Using domain ID {domain_id} for nameserver update")
                    ns_update_result = (
                        self.openprovider.update_domain_nameservers_by_id(
                            domain_id, cloudflare_nameservers
                        )
                    )

                    if ns_update_result["success"]:
                        nameserver_update_success = True
                        final_nameservers = cloudflare_nameservers
                        logger.info(
                            f"Nameservers updated to Cloudflare successfully: {cloudflare_nameservers}"
                        )
                    else:
                        logger.error(
                            f"Failed to update nameservers to Cloudflare: {ns_update_result['error']}"
                        )
                        final_nameservers = [
                            "ns1.openprovider.nl",
                            "ns2.openprovider.be",
                            "ns3.openprovider.eu",
                        ]
                else:
                    logger.error("No domain ID available for nameserver update")
                    final_nameservers = [
                        "ns1.openprovider.nl",
                        "ns2.openprovider.be",
                        "ns3.openprovider.eu",
                    ]

            except Exception as ns_error:
                logger.error(
                    f"Exception updating nameservers to Cloudflare: {ns_error}"
                )
                final_nameservers = [
                    "ns1.openprovider.nl",
                    "ns2.openprovider.be",
                    "ns3.openprovider.eu",
                ]

            return {
                "success": True,
                "domain_name": domain_name,
                "zone_id": cloudflare_zone_id,
                "nameservers": final_nameservers,
                "customer_id": customer_id,
                "domain_id": domain_result["domain_id"],
                "cloudflare_zone_created": True,
                "nameserver_update_success": nameserver_update_success,
                "a_record_added": a_record_result["success"],
                "https_enabled": https_enabled,
                "steps_completed": [
                    "cloudflare_zone_created",
                    "a_record_added",
                    "https_enabled" if https_enabled else "https_failed",
                    "customer_created",
                    "domain_registered",
                    (
                        "nameservers_updated"
                        if nameserver_update_success
                        else "nameservers_failed"
                    ),
                ],
            }

        except Exception as e:
            logger.error(f"Exception in complete domain registration: {e}")
            return {"success": False, "step": "exception", "error": str(e)}

    def _get_or_create_customer(
        self, telegram_user_id: int, telegram_username: str
    ) -> Dict[str, Any]:
        """Get existing customer or create new one"""
        try:
            # First try to find existing customer
            existing_customer = self.openprovider.get_customer_by_telegram_id(
                telegram_user_id
            )

            if existing_customer["success"]:
                logger.info(
                    f"Found existing OpenProvider customer for user {telegram_user_id}"
                )
                return existing_customer

            # Create new customer
            logger.info(
                f"Creating new OpenProvider customer for user {telegram_user_id}"
            )
            return self.openprovider.create_customer(
                telegram_user_id, telegram_username
            )

        except Exception as e:
            logger.error(f"Exception getting/creating customer: {e}")
            return {"success": False, "error": str(e)}

    def add_dns_record(
        self,
        domain_name: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 300,
    ) -> Dict[str, Any]:
        """Add a DNS record to a domain's Cloudflare zone with validation"""
        try:
            # Validate record type
            valid_types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV"]
            if record_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid record type {record_type}. Supported types: {', '.join(valid_types)}",
                }

            # Validate record content based on type
            validation_result = self._validate_dns_record(record_type, content)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid {record_type} record content: {validation_result['error']}",
                }

            # First try to get zone ID from database for more reliable operations
            cloudflare_zone_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.cloudflare_zone_id:
                        cloudflare_zone_id = domain_record.cloudflare_zone_id
                        logger.info(
                            f"Found zone ID {cloudflare_zone_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get zone ID from database: {db_error}")

            # Fall back to zone lookup if database method failed
            if not cloudflare_zone_id:
                zone_info = self.cloudflare.get_zone_info(domain_name)

                if not zone_info["success"]:
                    return {
                        "success": False,
                        "error": f"Zone not found for domain {domain_name}",
                    }

                cloudflare_zone_id = zone_info["zone_id"]

            # Add the DNS record
            result = self.cloudflare.add_dns_record(
                cloudflare_zone_id, record_type, name, content, ttl
            )

            # If this is the first A record for the domain, enable HTTPS
            if (
                result["success"]
                and record_type == "A"
                and (name == domain_name or name.endswith(f".{domain_name}"))
            ):
                try:
                    https_result = self.cloudflare.enable_ssl_tls(cloudflare_zone_id)
                    if https_result["success"]:
                        logger.info(f"Automatically enabled HTTPS for {domain_name}")
                        result["https_enabled"] = True
                    else:
                        logger.warning(
                            f"Failed to enable HTTPS for {domain_name}: {https_result.get('error', 'Unknown error')}"
                        )
                        result["https_enabled"] = False
                except Exception as https_error:
                    logger.error(
                        f"Error enabling HTTPS for {domain_name}: {https_error}"
                    )
                    result["https_enabled"] = False

            return result

        except Exception as e:
            logger.error(f"Exception adding DNS record: {e}")
            return {"success": False, "error": str(e)}

    async def list_dns_records(self, domain_name: str) -> Dict[str, Any]:
        """List all DNS records for a domain"""
        try:
            # First try to get zone ID from database for more reliable operations
            cloudflare_zone_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.cloudflare_zone_id:
                        cloudflare_zone_id = domain_record.cloudflare_zone_id
                        logger.info(
                            f"Found zone ID {cloudflare_zone_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get zone ID from database: {db_error}")

            # Fall back to zone lookup if database method failed
            if not cloudflare_zone_id:
                zone_info = self.cloudflare.get_zone_info(domain_name)

                if not zone_info["success"]:
                    return {
                        "success": False,
                        "error": f"Zone not found for domain {domain_name}",
                    }

                cloudflare_zone_id = zone_info["zone_id"]

            # List DNS records
            cloudflare_result = await self.cloudflare.list_dns_records(cloudflare_zone_id)

            if cloudflare_result and cloudflare_result.get("success"):
                return {"success": True, "records": cloudflare_result.get("result", [])}
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch DNS records from Cloudflare",
                }

        except Exception as e:
            logger.error(f"Exception listing DNS records: {e}")
            return {"success": False, "error": str(e)}

    def delete_dns_record(self, domain_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a DNS record from a domain's zone"""
        try:
            # First try to get zone ID from database for more reliable operations
            cloudflare_zone_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.cloudflare_zone_id:
                        cloudflare_zone_id = domain_record.cloudflare_zone_id
                        logger.info(
                            f"Found zone ID {cloudflare_zone_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get zone ID from database: {db_error}")

            # Fall back to zone lookup if database method failed
            if not cloudflare_zone_id:
                zone_info = self.cloudflare.get_zone_info(domain_name)

                if not zone_info["success"]:
                    return {
                        "success": False,
                        "error": f"Zone not found for domain {domain_name}",
                    }

                cloudflare_zone_id = zone_info["zone_id"]

            # Delete the DNS record
            return self.cloudflare.delete_dns_record(cloudflare_zone_id, record_id)

        except Exception as e:
            logger.error(f"Exception deleting DNS record: {e}")
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
        """Update a DNS record with validation"""
        try:
            # Validate record content based on type
            validation_result = self._validate_dns_record(record_type, content)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid {record_type} record content: {validation_result['error']}",
                }

            # First try to get zone ID from database for more reliable operations
            cloudflare_zone_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.cloudflare_zone_id:
                        cloudflare_zone_id = domain_record.cloudflare_zone_id
                        logger.info(
                            f"Found zone ID {cloudflare_zone_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get zone ID from database: {db_error}")

            # Fall back to zone lookup if database method failed
            if not cloudflare_zone_id:
                zone_info = self.cloudflare.get_zone_info(domain_name)

                if not zone_info["success"]:
                    return {
                        "success": False,
                        "error": f"Zone not found for domain {domain_name}",
                    }

                cloudflare_zone_id = zone_info["zone_id"]

            # Update the DNS record
            return self.cloudflare.update_dns_record(
                cloudflare_zone_id, record_id, record_type, name, content, ttl
            )

        except Exception as e:
            logger.error(f"Exception updating DNS record: {e}")
            return {"success": False, "error": str(e)}

    def check_domain_status(self, domain_name: str) -> Dict[str, Any]:
        """Check the status of a domain (DNS zone and registration)"""
        try:
            result = {
                "domain_name": domain_name,
                "cloudflare_zone": False,
                "registration_status": "unknown",
                "openprovider_status": None,
                "openprovider_info": None,
            }

            # Check Cloudflare zone - first try database zone ID
            cloudflare_zone_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.cloudflare_zone_id:
                        cloudflare_zone_id = domain_record.cloudflare_zone_id
                        result["cloudflare_zone"] = True
                        result["zone_id"] = cloudflare_zone_id
                        logger.info(
                            f"Found zone ID {cloudflare_zone_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get zone ID from database: {db_error}")

            # Fall back to zone lookup if database method failed
            if not cloudflare_zone_id:
                zone_info = self.cloudflare.get_zone_info(domain_name)
                if zone_info["success"]:
                    result["cloudflare_zone"] = True
                    result["zone_id"] = zone_info["zone_id"]
                    result["nameservers"] = zone_info["name_servers"]

            # Check OpenProvider domain status and information
            if self.openprovider:
                # First check if domain is in our registered_domains table using environment-based SQL
                try:
                    import psycopg2
                    import os

                    # Use PostgreSQL credentials from environment
                    conn = psycopg2.connect(
                        host=os.getenv("PGHOST"),
                        port=os.getenv("PGPORT"),
                        database=os.getenv("PGDATABASE"),
                        user=os.getenv("PGUSER"),
                        password=os.getenv("PGPASSWORD"),
                    )
                    cursor = conn.cursor()

                    # Query for the domain in our registered_domains table
                    cursor.execute(
                        "SELECT openprovider_domain_id, registration_status FROM registered_domains WHERE domain_name = %s",
                        (domain_name,),
                    )
                    domain_rows = cursor.fetchall()

                    if domain_rows and len(domain_rows) > 0:
                        openprovider_domain_id = domain_rows[0][0]
                        db_registration_status = domain_rows[0][1]

                        if openprovider_domain_id:
                            # Domain is in our system, get status from OpenProvider by ID
                            try:
                                domain_id = int(openprovider_domain_id)
                                domain_info = self.openprovider.get_domain_info_by_id(
                                    domain_id
                                )

                                if domain_info["success"]:
                                    result["registration_status"] = "registered_with_us"
                                    result["openprovider_status"] = domain_info.get(
                                        "status", "unknown"
                                    )

                                    # Extract comprehensive domain information
                                    domain_data = domain_info.get("domain_data", {})
                                    result["openprovider_info"] = {
                                        "domain_id": domain_id,
                                        "creation_date": domain_data.get(
                                            "creation_date"
                                        ),
                                        "expiry_date": domain_data.get(
                                            "expiration_date"
                                        ),
                                        "renewal_date": domain_data.get("renewal_date"),
                                        "auto_renew": domain_data.get(
                                            "autorenew", "default"
                                        )
                                        != "off",
                                        "customer_handle": domain_data.get(
                                            "owner_handle"
                                        ),
                                        "nameservers": domain_info.get(
                                            "nameservers", []
                                        ),
                                        "is_locked": domain_data.get(
                                            "is_locked", False
                                        ),
                                        "dnssec_enabled": domain_data.get(
                                            "is_dnssec_enabled", False
                                        ),
                                        "registry_status": domain_data.get("status"),
                                        "can_renew": domain_data.get(
                                            "can_renew", False
                                        ),
                                    }
                                else:
                                    # Domain ID exists but couldn't get info (might be transferred or deleted)
                                    result["registration_status"] = "registered_with_us"
                                    result["openprovider_status"] = "status_unavailable"
                                    result["openprovider_info"] = {
                                        "domain_id": domain_id,
                                        "error": "Could not retrieve domain information",
                                    }
                            except (ValueError, TypeError) as e:
                                logger.error(
                                    f"Invalid domain ID in database for {domain_name}: {e}"
                                )
                                result["registration_status"] = "database_error"
                                result["openprovider_status"] = "invalid_domain_id"
                    else:
                        # Domain not in our system, check if it's available for registration
                        availability = self.openprovider.check_domain_availability(
                            domain_name
                        )
                        if availability and "Available" in availability:
                            if availability["Available"]:
                                result["registration_status"] = "available"
                                result["openprovider_status"] = "available"
                            else:
                                result["registration_status"] = "registered_elsewhere"
                                result["openprovider_status"] = "registered_elsewhere"

                    # Clean up database connection
                    cursor.close()
                    conn.close()

                except Exception as db_error:
                    logger.error(
                        f"Database error checking domain {domain_name}: {db_error}"
                    )
                    # Fallback to availability check only
                    availability = self.openprovider.check_domain_availability(
                        domain_name
                    )
                    if availability and "Available" in availability:
                        if availability["Available"]:
                            result["registration_status"] = "available"
                            result["openprovider_status"] = "available"
                        else:
                            result["registration_status"] = "registered_elsewhere"
                            result["openprovider_status"] = "registered_elsewhere"

            return {"success": True, "status": result}

        except Exception as e:
            logger.error(f"Exception checking domain status: {e}")
            return {"success": False, "error": str(e)}

    def _validate_dns_record(self, record_type: str, content: str) -> Dict[str, Any]:
        """Validate DNS record content based on record type"""
        import re

        # Clean and validate the content
        content = content.strip()
        logger.debug(
            f"Validating {record_type} record with content: '{content}' (length: {len(content)})"
        )

        if record_type == "A":
            # Validate IPv4 address
            ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
            if re.match(ipv4_pattern, content):
                try:
                    parts = content.split(".")
                    if len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts):
                        logger.debug(f"IPv4 validation passed for: {content}")
                        return {"valid": True}
                    else:
                        logger.debug(
                            f"IPv4 validation failed - invalid octet values: {parts}"
                        )
                except ValueError as e:
                    logger.debug(f"IPv4 validation failed - non-numeric octets: {e}")
            else:
                logger.debug(
                    f"IPv4 validation failed - pattern mismatch for: '{content}'"
                )
            return {
                "valid": False,
                "error": "Must be a valid IPv4 address (e.g., 192.168.1.1)",
            }

        elif record_type == "AAAA":
            # Validate IPv6 address
            ipv6_pattern = r"^[0-9a-fA-F:]+$"
            if re.match(ipv6_pattern, content) and (
                "::" in content or content.count(":") >= 2
            ):
                return {"valid": True}
            return {"valid": False, "error": "Must be a valid IPv6 address"}

        elif record_type == "CNAME":
            # Validate domain name
            domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if (
                re.match(domain_pattern, content)
                and not content.startswith(".")
                and not content.endswith(".")
            ):
                return {"valid": True}
            return {
                "valid": False,
                "error": "Must be a valid domain name (e.g., example.com)",
            }

        elif record_type == "MX":
            # Validate MX record format: priority hostname
            mx_pattern = r"^\d+\s+[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if re.match(mx_pattern, content):
                parts = content.split()
                priority = int(parts[0])
                if 0 <= priority <= 65535:
                    return {"valid": True}
            return {
                "valid": False,
                "error": 'Must be in format "priority hostname" (e.g., "10 mail.example.com")',
            }

        elif record_type == "TXT":
            # TXT records can contain almost any text, but should be reasonable length
            if len(content) <= 255:
                return {"valid": True}
            return {
                "valid": False,
                "error": "TXT record content must be 255 characters or less",
            }

        elif record_type == "NS":
            # Validate nameserver
            domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if re.match(domain_pattern, content):
                return {"valid": True}
            return {
                "valid": False,
                "error": "Must be a valid nameserver (e.g., ns1.example.com)",
            }

        elif record_type == "SRV":
            # Validate SRV record format: priority weight port target
            srv_pattern = r"^\d+\s+\d+\s+\d+\s+[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if re.match(srv_pattern, content):
                return {"valid": True}
            return {
                "valid": False,
                "error": 'Must be in format "priority weight port target"',
            }

        return {"valid": True}  # Default to valid for unknown types

    def enable_https_for_domain(self, domain_name: str) -> Dict[str, Any]:
        """Enable HTTPS/SSL for a domain"""
        try:
            # First try to get zone ID from database for more reliable operations
            cloudflare_zone_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.cloudflare_zone_id:
                        cloudflare_zone_id = domain_record.cloudflare_zone_id
                        logger.info(
                            f"Found zone ID {cloudflare_zone_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get zone ID from database: {db_error}")

            # Fall back to zone lookup if database method failed
            if not cloudflare_zone_id:
                zone_info = self.cloudflare.get_zone_info(domain_name)

                if not zone_info["success"]:
                    return {
                        "success": False,
                        "error": f"Zone not found for domain {domain_name}",
                    }

                cloudflare_zone_id = zone_info["zone_id"]

            # Enable SSL/TLS and HTTPS
            return self.cloudflare.enable_ssl_tls(cloudflare_zone_id)

        except Exception as e:
            logger.error(f"Exception enabling HTTPS for domain: {e}")
            return {"success": False, "error": str(e)}

    async def update_domain_nameservers(
        self, domain_name: str, nameservers: list
    ) -> Dict[str, Any]:
        """Update nameservers for a domain via OpenProvider registrar"""
        try:
            if not self.openprovider:
                return {"success": False, "error": "OpenProvider not configured"}

            logger.info(f"Updating nameservers for {domain_name} to: {nameservers}")

            # First try to get domain ID from our database
            domain_id = None
            try:
                from models import DatabaseManager

                db_manager = DatabaseManager()
                session = db_manager.get_session()

                try:
                    from models import RegisteredDomain

                    domain_record = (
                        session.query(RegisteredDomain)
                        .filter_by(domain_name=domain_name)
                        .first()
                    )
                    if domain_record and domain_record.openprovider_domain_id:
                        domain_id = domain_record.openprovider_domain_id
                        logger.info(
                            f"Found domain ID {domain_id} for {domain_name} in database"
                        )
                finally:
                    session.close()
            except Exception as db_error:
                logger.warning(f"Failed to get domain ID from database: {db_error}")

            # Use domain ID method if available, otherwise fall back to domain name method
            if domain_id:
                result = self.openprovider.update_domain_nameservers_by_id(
                    domain_id, nameservers
                )
            else:
                result = self.openprovider.update_domain_nameservers(
                    domain_name, nameservers
                )

            if result["success"]:
                logger.info(f"Successfully updated nameservers for {domain_name}")

                # Update database record if available
                try:
                    from database import Database

                    db = Database()

                    # Update nameserver provider in database
                    if any("cloudflare.com" in ns for ns in nameservers):
                        provider = "cloudflare"
                    elif any("openprovider" in ns for ns in nameservers):
                        provider = "openprovider"
                    else:
                        provider = "custom"

                    db.update_domain_nameserver_provider(domain_name, provider)
                    logger.info(
                        f"Updated nameserver provider to {provider} in database"
                    )

                except Exception as db_error:
                    logger.warning(
                        f"Failed to update database nameserver provider: {db_error}"
                    )
                    # Don't fail the whole operation for database update issues

                return result
            else:
                logger.error(
                    f"Failed to update nameservers: {result.get('error', 'Unknown error')}"
                )
                return result

        except Exception as e:
            logger.error(f"Exception updating nameservers: {e}")
            return {"success": False, "error": str(e)}
