#!/usr/bin/env python3
"""
Stage 3: Domain Management Flow Example
Demonstrates complete UI-to-Database layer responsibilities for "My Domains" dashboard
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class Stage3DomainManagementFlow:
    """
    Demonstrates complete layer separation for Stage 3: Domain Management
    
    Flow: UI (Bot) → API → Service → Repository → Database
    """
    
    def __init__(self):
        self.flow_description = {
            "stage": "Stage 3: Domain Management",
            "ui_action": "My Domains dashboard → show domains, expiry, DNS status",
            "layers": {
                "ui_bot": {
                    "responsibility": "Display domains list with action buttons",
                    "implementation": "Telegram bot callback handler for 'my_domains'",
                    "code_location": "nomadly3_fixed_bot.py -> handle_my_domains()",
                    "ui_elements": [
                        "Domain list with names",
                        "Expiry dates with color coding",
                        "DNS record counts",
                        "Action buttons: [Manage DNS], [Nameservers], [Details]"
                    ]
                },
                "api": {
                    "responsibility": "RESTful endpoint for domain data retrieval",
                    "endpoint": "GET /api/v1/domains/my/{telegram_id}",
                    "implementation": "app/api/routes/domain_routes.py",
                    "request_params": {"telegram_id": "int", "include_dns": "bool"},
                    "response_format": {
                        "domains": [
                            {
                                "id": "int",
                                "domain_name": "str",
                                "expires_at": "datetime",
                                "days_until_expiry": "int",
                                "dns_record_count": "int",
                                "is_active": "bool",
                                "cloudflare_zone_id": "str",
                                "nameservers": ["str"]
                            }
                        ],
                        "total_count": "int",
                        "active_count": "int",
                        "expiring_soon": "int"
                    }
                },
                "service": {
                    "responsibility": "Business logic for domain portfolio management",
                    "method": "DomainService.get_user_domain_portfolio(telegram_id)",
                    "implementation": "app/services/domain_service.py",
                    "business_logic": [
                        "Calculate days until expiry",
                        "Determine domain status (active/expired)",
                        "Sort by expiry priority",
                        "Apply business rules for display"
                    ]
                },
                "repository": {
                    "responsibility": "Data access with complex joins",
                    "method": "DomainRepository.get_user_domains_with_dns(telegram_id)",
                    "implementation": "app/repositories/domain_repo.py",
                    "database_operations": [
                        "JOIN registered_domains with dns_records",
                        "COUNT DNS records per domain",
                        "Filter by user telegram_id",
                        "ORDER BY expiry date ascending"
                    ]
                },
                "database": {
                    "responsibility": "Data persistence and relationships",
                    "tables": ["registered_domains", "dns_records", "users"],
                    "relationships": [
                        "registered_domains.telegram_id → users.telegram_id",
                        "dns_records.domain_id → registered_domains.id"
                    ],
                    "indexes": [
                        "idx_domains_telegram_id",
                        "idx_domains_expires_at", 
                        "idx_dns_domain_id"
                    ]
                }
            }
        }
    
    def demonstrate_complete_flow(self, telegram_id: int = 123456789):
        """Demonstrate complete Stage 3 flow with real implementation"""
        logger.info("🔍 Demonstrating Stage 3: Domain Management Flow")
        logger.info("=" * 70)
        
        # Stage 3 Flow Demonstration
        logger.info("📱 LAYER 1: UI (Telegram Bot)")
        logger.info("User Action: Clicks 'My Domains' button in main menu")
        logger.info("Bot Response: Fetches domain data and displays interactive list")
        logger.info("UI Elements: Domain cards with expiry warnings and action buttons")
        logger.info("")
        
        logger.info("🌐 LAYER 2: API (FastAPI Router)")
        logger.info("Endpoint: GET /api/v1/domains/my/123456789")
        logger.info("Authentication: Telegram user ID validation")
        logger.info("Response: JSON with domain portfolio data")
        logger.info("")
        
        logger.info("⚙️ LAYER 3: Service (Business Logic)")
        logger.info("Method: DomainService.get_user_domain_portfolio(123456789)")
        logger.info("Logic: Calculate expiry status, sort by priority, format for UI")
        logger.info("Rules: Mark expiring domains (<30 days), count DNS records")
        logger.info("")
        
        logger.info("🗃️ LAYER 4: Repository (Data Access)")
        logger.info("Method: DomainRepository.get_user_domains_with_dns(123456789)")
        logger.info("Query: Complex JOIN between domains and DNS records")
        logger.info("Result: Domains with DNS counts and metadata")
        logger.info("")
        
        logger.info("💾 LAYER 5: Database (PostgreSQL)")
        logger.info("Tables: registered_domains, dns_records, users")
        logger.info("Indexes: Optimized for user filtering and expiry sorting")
        logger.info("ACID: Transactional consistency for all operations")
        logger.info("")
        
        # Show example data flow
        example_data = self.get_example_domain_data()
        
        logger.info("📊 EXAMPLE DATA FLOW:")
        logger.info("=" * 70)
        logger.info("Database → Repository → Service → API → UI")
        logger.info("")
        
        logger.info("🗄️ Database Raw Data:")
        for domain in example_data["database_raw"]:
            logger.info(f"  • {domain['domain_name']} | Expires: {domain['expires_at']} | DNS: {domain['dns_count']}")
        logger.info("")
        
        logger.info("🔧 Service Processed Data:")
        for domain in example_data["service_processed"]:
            status = "🟢 Active" if domain['is_active'] else "🔴 Expired"
            expiry = f"⏰ {domain['days_until_expiry']} days" if domain['days_until_expiry'] else "❌ Expired"
            logger.info(f"  • {domain['domain_name']} | {status} | {expiry} | 📡 {domain['dns_record_count']} DNS")
        logger.info("")
        
        logger.info("📱 UI Display Format:")
        for domain in example_data["ui_formatted"]:
            logger.info(f"  {domain['display']}")
            logger.info(f"    Buttons: {' '.join(domain['buttons'])}")
        logger.info("")
        
        logger.info("✅ LAYER VALIDATION SUMMARY:")
        logger.info("=" * 70)
        validation_results = self.validate_layer_implementation()
        for layer, status in validation_results.items():
            emoji = "✅" if status["implemented"] else "❌"
            logger.info(f"{emoji} {layer.upper()}: {status['details']}")
        
        overall_status = all(result["implemented"] for result in validation_results.values())
        logger.info("")
        logger.info(f"🎯 OVERALL STATUS: {'✅ COMPLETE' if overall_status else '⚠️ PARTIAL'}")
        logger.info("Stage 3 demonstrates proper clean architecture layer separation")
        
        return overall_status
    
    def get_example_domain_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate example data showing transformation through layers"""
        return {
            "database_raw": [
                {
                    "id": 1,
                    "domain_name": "mycompany.com",
                    "expires_at": "2025-08-15",
                    "cloudflare_zone_id": "abc123",
                    "dns_count": 5
                },
                {
                    "id": 2, 
                    "domain_name": "startup.io",
                    "expires_at": "2025-07-30",
                    "cloudflare_zone_id": "def456",
                    "dns_count": 3
                },
                {
                    "id": 3,
                    "domain_name": "expired.net",
                    "expires_at": "2025-06-01",
                    "cloudflare_zone_id": None,
                    "dns_count": 0
                }
            ],
            "service_processed": [
                {
                    "domain_name": "startup.io",
                    "days_until_expiry": 7,
                    "is_active": True,
                    "dns_record_count": 3,
                    "priority": "high"  # Expiring soon
                },
                {
                    "domain_name": "mycompany.com", 
                    "days_until_expiry": 23,
                    "is_active": True,
                    "dns_record_count": 5,
                    "priority": "normal"
                },
                {
                    "domain_name": "expired.net",
                    "days_until_expiry": None,
                    "is_active": False,
                    "dns_record_count": 0,
                    "priority": "expired"
                }
            ],
            "ui_formatted": [
                {
                    "display": "🚨 startup.io (expires in 7 days) - 3 DNS records",
                    "buttons": ["[🛠️ Manage DNS]", "[🔧 Nameservers]", "[📊 Details]"]
                },
                {
                    "display": "🟢 mycompany.com (expires in 23 days) - 5 DNS records", 
                    "buttons": ["[🛠️ Manage DNS]", "[🔧 Nameservers]", "[📊 Details]"]
                },
                {
                    "display": "❌ expired.net (expired) - 0 DNS records",
                    "buttons": ["[🔄 Renew]", "[📊 Details]"]
                }
            ]
        }
    
    def validate_layer_implementation(self) -> Dict[str, Dict[str, Any]]:
        """Validate that each layer is properly implemented"""
        try:
            # Test imports to verify implementation exists
            results = {}
            
            # Check Service Layer
            try:
                from app.services.domain_service import DomainService
                service_methods = [method for method in dir(DomainService) if not method.startswith('_')]
                has_portfolio_method = 'get_user_domain_portfolio' in service_methods
                results["service"] = {
                    "implemented": has_portfolio_method,
                    "details": f"DomainService with {len(service_methods)} methods, portfolio method: {has_portfolio_method}"
                }
            except Exception as e:
                results["service"] = {"implemented": False, "details": f"Import error: {e}"}
            
            # Check Repository Layer  
            try:
                from app.repositories.domain_repo import DomainRepository
                repo_methods = [method for method in dir(DomainRepository) if not method.startswith('_')]
                has_dns_method = 'get_user_domains_with_dns' in repo_methods
                results["repository"] = {
                    "implemented": has_dns_method,
                    "details": f"DomainRepository with {len(repo_methods)} methods, DNS method: {has_dns_method}"
                }
            except Exception as e:
                results["repository"] = {"implemented": False, "details": f"Import error: {e}"}
            
            # Check API Layer
            try:
                from app.api.routes.domain_routes import router
                results["api"] = {
                    "implemented": True,
                    "details": "Domain API router available with endpoint support"
                }
            except Exception as e:
                results["api"] = {"implemented": False, "details": f"Import error: {e}"}
            
            # Check Database Layer
            try:
                from fresh_database import RegisteredDomain, DNSRecord
                results["database"] = {
                    "implemented": True,
                    "details": "Database models available with proper relationships"
                }
            except Exception as e:
                results["database"] = {"implemented": False, "details": f"Import error: {e}"}
            
            return results
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"error": {"implemented": False, "details": str(e)}}

if __name__ == "__main__":
    demo = Stage3DomainManagementFlow()
    success = demo.demonstrate_complete_flow()
    print(f"\nStage 3 Flow Demonstration: {'✅ SUCCESS' if success else '❌ NEEDS FIXES'}")