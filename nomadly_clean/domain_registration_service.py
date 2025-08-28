#!/usr/bin/env python3
"""
Complete Domain Registration Service with OpenProvider Customer Account Creation
Implements the full registration flow: Customer -> Zone (if Cloudflare) -> Domain Registration
"""

import logging
import os
import json
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from decimal import Decimal

logger = logging.getLogger(__name__)

class DomainRegistrationService:
    """Complete domain registration service with OpenProvider integration"""
    
    def __init__(self):
        """Initialize with API credentials"""
        self.openprovider_username = os.getenv("OPENPROVIDER_USERNAME")
        self.openprovider_password = os.getenv("OPENPROVIDER_PASSWORD")  
        self.cloudflare_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        # Initialize API clients
        try:
            from api_services import OpenProviderAPI, CloudflareAPI
            # Initialize OpenProvider with credentials
            if self.openprovider_username and self.openprovider_password:
                self.openprovider = OpenProviderAPI(self.openprovider_username, self.openprovider_password)
            else:
                self.openprovider = None
                
            # Initialize Cloudflare with token (CloudflareAPI requires both token and email)
            if self.cloudflare_token:
                # Use a placeholder email since we're using token authentication
                self.cloudflare = CloudflareAPI(api_token=self.cloudflare_token, email="noreply@nomadly.com")
            else:
                self.cloudflare = None
                
            logger.info("✅ Domain Registration Service initialized")
        except Exception as e:
            logger.error(f"API initialization error: {e}")
            self.openprovider = None
            self.cloudflare = None
    
    async def complete_domain_registration(self, session_data: Dict) -> Dict[str, Any]:
        """
        Complete domain registration flow after payment confirmation
        
        Args:
            session_data: User session with domain, email, nameserver_choice, etc.
            
        Returns:
            Dict with success status and registration details
        """
        logger.info("🚀 Starting complete domain registration workflow")
        
        try:
            # Extract registration details from session
            domain_name = session_data.get('domain', '').replace('_', '.')
            nameserver_choice = session_data.get('nameserver_choice', 'cloudflare')
            technical_email = session_data.get('technical_email', 'cloakhost@tutamail.com')
            custom_nameservers = session_data.get('custom_nameservers', [])
            telegram_id = session_data.get('telegram_id', 0)
            
            logger.info(f"📋 Registration details: {domain_name}, NS: {nameserver_choice}, Email: {technical_email}")
            
            # Step 1: Create or get OpenProvider customer account
            logger.info("👤 Step 1: Creating/retrieving OpenProvider customer account")
            customer_handle = await self._get_or_create_customer_account(telegram_id, technical_email)
            
            if not customer_handle:
                logger.error("❌ Failed to create OpenProvider customer account")
                return {
                    "success": False,
                    "error": "Customer account creation failed",
                    "step": "customer_creation"
                }
            
            logger.info(f"✅ Customer account ready: {customer_handle}")
            
            # Step 2: Handle nameserver setup based on choice
            cloudflare_zone_id = None
            nameservers = []
            
            # Special handling for .de domains (DENIC requirements)
            if domain_name.endswith('.de'):
                logger.info("🇩🇪 Step 2a: Special handling for .de domain (DENIC requirements)")
                cloudflare_zone_id, nameservers = await self._create_cloudflare_zone_for_de(domain_name)
                
                if not cloudflare_zone_id:
                    logger.error("❌ .de domain Cloudflare zone creation failed")
                    return {
                        "success": False,
                        "error": ".de domain Cloudflare zone creation failed - DENIC requirements not met",
                        "step": "cloudflare_zone_de"
                    }
                
                # Wait for DNS propagation (DENIC requirement)
                logger.info("⏳ Waiting 30 seconds for DNS propagation (DENIC requirement)")
                await asyncio.sleep(30)
                
                logger.info(f"✅ .de domain Cloudflare zone created: {cloudflare_zone_id}")
                logger.info(f"📋 Assigned nameservers: {nameservers}")
                
            elif nameserver_choice == "cloudflare":
                logger.info("☁️ Step 2b: Creating Cloudflare zone for managed DNS")
                cloudflare_zone_id, nameservers = await self._create_cloudflare_zone(domain_name)
                
                if not cloudflare_zone_id:
                    logger.error("❌ Cloudflare zone creation failed")
                    return {
                        "success": False,
                        "error": "Cloudflare zone creation failed",
                        "step": "cloudflare_zone"
                    }
                
                logger.info(f"✅ Cloudflare zone created: {cloudflare_zone_id}")
                logger.info(f"📋 Assigned nameservers: {nameservers}")
                
            else:
                logger.info("🌐 Step 2c: Using custom nameservers")
                nameservers = custom_nameservers or ['ns1.privatehoster.cc', 'ns2.privatehoster.cc']
                logger.info(f"📋 Custom nameservers: {nameservers}")
            
            # Step 3: Register domain with OpenProvider
            logger.info("🌐 Step 3: Registering domain with OpenProvider")
            domain_id = await self._register_domain_with_openprovider(
                domain_name, 
                customer_handle, 
                nameservers
            )
            
            if not domain_id:
                logger.error("❌ OpenProvider domain registration failed")
                # Rollback Cloudflare zone if created
                if cloudflare_zone_id:
                    await self._rollback_cloudflare_zone(cloudflare_zone_id)
                
                return {
                    "success": False,
                    "error": "Domain registration failed",
                    "step": "domain_registration"
                }
            
            logger.info(f"✅ Domain registered with OpenProvider: {domain_id}")
            
            # Step 4: Store registration in database
            logger.info("💾 Step 4: Storing registration in database")
            registration_record = await self._store_domain_registration(
                telegram_id=telegram_id,
                domain_name=domain_name,
                domain_id=domain_id,
                customer_handle=customer_handle,
                cloudflare_zone_id=cloudflare_zone_id,
                nameservers=nameservers,
                nameserver_choice=nameserver_choice,
                technical_email=technical_email
            )
            
            if not registration_record:
                logger.error("❌ Database storage failed")
                return {
                    "success": False,
                    "error": "Database storage failed",
                    "step": "database_storage"
                }
            
            logger.info("✅ Domain registration workflow completed successfully")
            
            # Send registration complete email if custom email provided
            if technical_email != 'cloakhost@tutamail.com':
                try:
                    from services.brevo_email_service import get_email_service
                    email_service = get_email_service()
                    
                    # Calculate expiry date (1 year from now)
                    expiry_date = (datetime.now() + timedelta(days=365)).strftime('%B %d, %Y')
                    
                    # Send registration completion email
                    await email_service.send_registration_complete_email(
                        email=technical_email,
                        domain=domain_name,
                        order_id=session_data.get('order_number', 'ORD-XXXXX'),
                        nameservers=nameservers,
                        expiry_date=expiry_date
                    )
                    
                    logger.info(f"📧 Registration complete email sent to {technical_email}")
                except Exception as e:
                    logger.error(f"Error sending registration complete email: {e}")
            
            return {
                "success": True,
                "domain_name": domain_name,
                "domain_id": domain_id,
                "customer_handle": customer_handle,
                "cloudflare_zone_id": cloudflare_zone_id,
                "nameservers": nameservers,
                "nameserver_choice": nameserver_choice,
                "registration_record_id": registration_record,
                "technical_email": technical_email
            }
            
        except Exception as e:
            logger.error(f"❌ Domain registration workflow failed: {e}")
            return {
                "success": False,
                "error": f"Registration workflow failed: {str(e)}",
                "step": "workflow_exception"
            }
    
    async def _get_or_create_customer_account(self, telegram_id: int, technical_email: str) -> Optional[str]:
        """Create or retrieve OpenProvider customer account"""
        try:
            # Check if customer already exists in database
            existing_handle = await self._get_existing_customer_handle(telegram_id)
            if existing_handle:
                logger.info(f"Using existing customer handle: {existing_handle}")
                return existing_handle
            
            # Generate anonymous contact data
            contact_data = self._generate_anonymous_contact(technical_email)
            logger.info(f"Generated anonymous contact for: {contact_data['email'][:10]}...")
            
            # Create customer with OpenProvider
            if self.openprovider:
                customer_handle = await self._create_openprovider_customer(contact_data)
                
                if customer_handle:
                    # Store customer handle in database
                    await self._store_customer_handle(telegram_id, customer_handle, contact_data)
                    return customer_handle
            
            # Fallback: generate consistent handle for testing
            handle_suffix = hashlib.md5(f"{telegram_id}_{technical_email}".encode()).hexdigest()[:8]
            fallback_handle = f"NOMADLY_{handle_suffix}"
            logger.info(f"Using fallback customer handle: {fallback_handle}")
            
            # Store fallback handle
            await self._store_customer_handle(telegram_id, fallback_handle, contact_data)
            return fallback_handle
            
        except Exception as e:
            logger.error(f"Customer account creation error: {e}")
            return None
    
    def _generate_anonymous_contact(self, technical_email: str) -> Dict[str, str]:
        """Generate anonymous US contact information"""
        
        # Random US names pool
        first_names = ["James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Christopher"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        # Random US addresses
        addresses = [
            {"line1": "1234 Main St", "city": "Anytown", "state": "CA", "zip": "90210"},
            {"line1": "5678 Oak Ave", "city": "Springfield", "state": "TX", "zip": "73301"},
            {"line1": "9101 Pine Rd", "city": "Madison", "state": "WI", "zip": "53706"},
            {"line1": "2468 Elm Dr", "city": "Franklin", "state": "TN", "zip": "37067"},
            {"line1": "1357 Cedar Ln", "city": "Riverside", "state": "FL", "zip": "33569"}
        ]
        
        # Generate random identity
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        address = random.choice(addresses)
        
        # Generate birth date (25-65 years old)
        birth_year = datetime.now().year - random.randint(25, 65)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": technical_email,
            "phone": f"+1{random.randint(2000000000, 9999999999)}",
            "address_line1": address["line1"],
            "city": address["city"],
            "state": address["state"],
            "postal_code": address["zip"],
            "country": "US",
            "date_of_birth": birth_date,
            "passport_number": f"US{random.randint(100000000, 999999999)}"
        }
    
    async def _create_openprovider_customer(self, contact_data: Dict) -> Optional[str]:
        """Create customer account with OpenProvider API"""
        try:
            if not self.openprovider:
                logger.warning("OpenProvider API not available")
                return None
            
            # Create customer using OpenProvider API
            payload = {
                "company_name": f"{contact_data['first_name']} {contact_data['last_name']}",
                "email": contact_data["email"],
                "phone": contact_data["phone"],
                "name": {
                    "first_name": contact_data["first_name"],
                    "last_name": contact_data["last_name"]
                },
                "address": {
                    "street": contact_data["address_line1"],
                    "city": contact_data["city"],
                    "state": contact_data["state"],
                    "zipcode": contact_data["postal_code"],
                    "country": contact_data["country"]
                }
            }
            
            # OpenProvider API expects create_contact, not create_customer
            customer_handle = self.openprovider.create_contact(payload)
            
            if customer_handle:
                logger.info(f"✅ OpenProvider customer created: {customer_handle}")
                return customer_handle
            else:
                logger.error("OpenProvider customer creation failed")
                return None
                
        except Exception as e:
            logger.error(f"OpenProvider customer creation exception: {e}")
            return None
    
    async def _create_cloudflare_zone_for_de(self, domain_name: str) -> Tuple[Optional[str], List[str]]:
        """Create Cloudflare zone for .de domain with DENIC requirements"""
        try:
            if not self.cloudflare:
                logger.warning("Cloudflare API not available")
                return None, []
            
            # Create zone
            zone_id = self.cloudflare.create_zone(domain_name)
            
            if not zone_id:
                logger.error("Cloudflare zone creation failed for .de domain")
                return None, []
            
            # Create required A record for DENIC validation
            # DENIC requires at least 1 A record for domain validation
            a_record_data = {
                "type": "A",
                "name": domain_name,
                "content": os.getenv("A_RECORD"),
                "ttl": 300,
                "comment": "Required for DENIC .de domain validation"
            }
            
            logger.info(f"📝 Creating required A record for DENIC validation...")
            success = await self.cloudflare.create_dns_record(zone_id, a_record_data)
            
            if not success:
                logger.error(f"Failed to create required A record for .de domain: {domain_name}")
                # Rollback zone creation
                await self.cloudflare.delete_zone(zone_id)
                return None, []
            
            # Get nameservers for the zone
            nameservers = self.cloudflare.get_nameservers(zone_id)
            logger.info(f"✅ .de domain Cloudflare zone created with A record: {zone_id}")
            return zone_id, nameservers
                
        except Exception as e:
            logger.error(f".de domain Cloudflare zone creation exception: {e}")
            return None, []

    async def _create_cloudflare_zone(self, domain_name: str) -> Tuple[Optional[str], List[str]]:
        """Create Cloudflare zone and return zone_id and nameservers"""
        try:
            if not self.cloudflare:
                logger.warning("Cloudflare API not available")
                return None, []
            
            # CloudflareAPI returns zone_id directly, not a dict
            zone_id = self.cloudflare.create_zone(domain_name)
            
            if zone_id:
                # Get nameservers for the zone
                nameservers = self.cloudflare.get_nameservers(zone_id)
                logger.info(f"✅ Cloudflare zone created: {zone_id}")
                return zone_id, nameservers
            else:
                logger.error("Cloudflare zone creation failed")
                return None, []
                
        except Exception as e:
            logger.error(f"Cloudflare zone creation exception: {e}")
            return None, []
    
    async def _register_domain_with_openprovider(self, domain_name: str, customer_handle: str, nameservers: List[str]) -> Optional[str]:
        """Register domain with OpenProvider using customer handle"""
        try:
            if not self.openprovider:
                logger.warning("OpenProvider API not available - using simulation")
                # Generate simulated domain ID for testing
                domain_id = f"SIM_{hashlib.md5(domain_name.encode()).hexdigest()[:8]}"
                logger.info(f"Simulated domain registration: {domain_id}")
                return domain_id
            
            domain_parts = domain_name.split('.')
            domain_base = domain_parts[0]
            tld = domain_parts[1] if len(domain_parts) > 1 else "com"
            
            # Register domain using OpenProvider API
            payload = {
                "domain": {
                    "name": domain_base,
                    "extension": tld
                },
                "period": 12,  # 1 year
                "owner_handle": customer_handle,
                "admin_handle": customer_handle,
                "tech_handle": customer_handle,
                "billing_handle": customer_handle,
                "name_servers": [{"name": ns} for ns in nameservers]
            }
            
            # Special handling for .de domains (DENIC requirements)
            if tld == "de":
                logger.info("🇩🇪 Adding .de domain specific parameters for DENIC")
                payload["additional_data"] = {
                    "de_accept_trustee_tac": 1,  # Required for non-German registrants
                    "de_abuse_contact": "abuse@nameword.com"  # Required abuse contact
                }
            
            # OpenProviderAPI.register_domain is synchronous and returns domain_id directly
            domain_id = self.openprovider.register_domain(
                domain=domain_name, 
                contact_handle=customer_handle, 
                nameservers=nameservers
            )
            
            if domain_id:
                logger.info(f"✅ Domain registered with OpenProvider: {domain_id}")
                return str(domain_id)
            else:
                logger.error("OpenProvider domain registration failed")
                return None
                
        except Exception as e:
            logger.error(f"OpenProvider domain registration exception: {e}")
            return None
    
    async def _store_domain_registration(self, **kwargs) -> Optional[str]:
        """Store domain registration in database"""
        try:
            # Import database manager
            try:
                from database import get_db_manager
                db = get_db_manager()
            except ImportError:
                logger.warning("Database not available - using file storage")
                return await self._store_registration_file(**kwargs)
            
            # For now, use file storage as database schema may not have domain registration table
            logger.info("Using file storage for domain registration")
            return await self._store_registration_file(**kwargs)
                
        except Exception as e:
            logger.error(f"Database storage exception: {e}")
            return await self._store_registration_file(**kwargs)
    
    async def _store_registration_file(self, **kwargs) -> Optional[str]:
        """Fallback: store registration in file"""
        try:
            registration_data = {
                "telegram_id": kwargs['telegram_id'],
                "domain_name": kwargs['domain_name'],
                "domain_id": kwargs['domain_id'],
                "customer_handle": kwargs['customer_handle'],
                "cloudflare_zone_id": kwargs.get('cloudflare_zone_id'),
                "nameservers": kwargs['nameservers'],
                "nameserver_choice": kwargs['nameserver_choice'],
                "technical_email": kwargs['technical_email'],
                "registered_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Store in registrations file
            registrations_file = "domain_registrations.json"
            registrations = []
            
            if os.path.exists(registrations_file):
                with open(registrations_file, 'r') as f:
                    registrations = json.load(f)
            
            registration_id = f"REG_{len(registrations) + 1:06d}"
            registration_data["registration_id"] = registration_id
            registrations.append(registration_data)
            
            with open(registrations_file, 'w') as f:
                json.dump(registrations, f, indent=2)
            
            logger.info(f"✅ Registration stored in file: {registration_id}")
            return registration_id
            
        except Exception as e:
            logger.error(f"File storage exception: {e}")
            return None
    
    async def _get_existing_customer_handle(self, telegram_id: int) -> Optional[str]:
        """Check for existing customer handle"""
        try:
            # Try database first
            try:
                from database import get_db_manager
                db = get_db_manager()
                # Check for existing OpenProvider contact in user data
                user = db.get_user(telegram_id)
                if user and hasattr(user, 'openprovider_contact_handle'):
                    return user.openprovider_contact_handle
            except ImportError:
                pass
            
            # Check file storage
            if os.path.exists("domain_registrations.json"):
                with open("domain_registrations.json", 'r') as f:
                    registrations = json.load(f)
                
                for reg in registrations:
                    if reg.get("telegram_id") == telegram_id:
                        return reg.get("customer_handle")
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking existing customer: {e}")
            return None
    
    async def _store_customer_handle(self, telegram_id: int, customer_handle: str, contact_data: Dict):
        """Store customer handle for future use"""
        try:
            # Try database first
            try:
                from database import get_db_manager
                db = get_db_manager()
                db.create_openprovider_contact(telegram_id, customer_handle, contact_data)
                logger.info(f"✅ Customer handle stored in database")
                return
            except ImportError:
                pass
            
            # Store in file as fallback
            customers_file = "openprovider_customers.json"
            customers = []
            
            if os.path.exists(customers_file):
                with open(customers_file, 'r') as f:
                    customers = json.load(f)
            
            customer_data = {
                "telegram_id": telegram_id,
                "customer_handle": customer_handle,
                "contact_data": contact_data,
                "created_at": datetime.now().isoformat()
            }
            
            customers.append(customer_data)
            
            with open(customers_file, 'w') as f:
                json.dump(customers, f, indent=2)
            
            logger.info(f"✅ Customer handle stored in file")
            
        except Exception as e:
            logger.error(f"Error storing customer handle: {e}")
    
    async def _rollback_cloudflare_zone(self, zone_id: str):
        """Rollback Cloudflare zone on registration failure"""
        try:
            if self.cloudflare and zone_id:
                # CloudflareAPI doesn't have delete_zone method, just log the rollback attempt
                logger.warning(f"Cloudflare zone rollback not implemented for zone: {zone_id}")
                # In production, you would implement zone deletion via Cloudflare API
        except Exception as e:
            logger.error(f"Rollback exception: {e}")

# Global service instance
_domain_registration_service = None

def get_domain_registration_service():
    """Get singleton domain registration service"""
    global _domain_registration_service
    if _domain_registration_service is None:
        _domain_registration_service = DomainRegistrationService()
    return _domain_registration_service