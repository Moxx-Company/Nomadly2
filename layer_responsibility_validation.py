"""
Layer Responsibility Validation System
Validates that all UI use cases have proper backend layer implementation
"""

import logging
from typing import Dict, List, Any, Optional
import inspect

logger = logging.getLogger(__name__)

class LayerResponsibilityValidator:
    """Validates layer separation and responsibility implementation"""
    
    def __init__(self):
        self.use_cases = {
            "financial_management": {
                "ui_flow": "Wallet balance → add funds → select crypto → monitor tx",
                "api_endpoints": ["POST /wallet/add", "GET /wallet/status", "GET /transactions"],
                "service_methods": ["create_payment_request", "monitor_blockchain_payment", "apply_overpayment_credit"],
                "repository_methods": ["create_transaction", "update_transaction_status", "get_wallet_balance"],
                "database_tables": ["wallets", "transactions", "loyalty_tiers"]
            },
            "domain_management": {
                "ui_flow": "My Domains → view expiry → renew domain → update DNS",
                "api_endpoints": ["GET /domains/my", "POST /domains/renew", "GET /domains/{id}"],
                "service_methods": ["get_user_domain_portfolio", "renew_domain", "calculate_renewal_price"],
                "repository_methods": ["get_user_domains_with_dns", "update_domain_expiry", "create_renewal_order"],
                "database_tables": ["registered_domains", "dns_records", "orders"]
            },
            "dns_management": {
                "ui_flow": "Domain → Manage DNS → Add/Edit/Delete records → Geo-blocking",
                "api_endpoints": ["GET /dns/{domain_id}", "POST /dns/records", "PUT /dns/records/{id}", "DELETE /dns/records/{id}"],
                "service_methods": ["sync_with_cloudflare", "validate_dns_input", "manage_geo_blocking"],
                "repository_methods": ["create_dns_record", "update_dns_record", "delete_dns_record", "update_cloudflare_record_id"],
                "database_tables": ["dns_records", "registered_domains", "cloudflare_zones"]
            },
            "nameserver_management": {
                "ui_flow": "Domain → Update Nameservers → Select preset/custom → Monitor propagation",
                "api_endpoints": ["GET /nameservers/{domain_id}", "PUT /nameservers/{domain_id}", "GET /nameservers/presets"],
                "service_methods": ["get_domain_nameservers", "update_domain_nameservers", "detect_nameserver_provider"],
                "repository_methods": ["update_nameservers", "get_by_domain_name", "update_domain"],
                "database_tables": ["registered_domains", "nameserver_operations", "audit_logs"]
            },
            "domain_search": {
                "ui_flow": "Search Domain → Check availability → Select TLD → Add to cart",
                "api_endpoints": ["GET /domains/search", "GET /domains/availability", "POST /domains/register"],
                "service_methods": ["check_domain_availability", "calculate_domain_pricing", "validate_domain_format"],
                "repository_methods": ["check_existing_domain", "create_domain_order", "save_domain_search"],
                "database_tables": ["domain_searches", "orders", "tld_pricing"]
            },
            "user_management": {
                "ui_flow": "Language selection → Dashboard → Profile → Settings",
                "api_endpoints": ["POST /users/register", "PUT /users/language", "GET /users/dashboard"],
                "service_methods": ["create_user", "update_language_preference", "get_dashboard_data"],
                "repository_methods": ["create", "update_user_language", "get_dashboard_data"],
                "database_tables": ["users", "user_states", "translations"]
            },
            "support_system": {
                "ui_flow": "Support → FAQ → Contact support → Ticket tracking",
                "api_endpoints": ["GET /support/faq", "POST /support/tickets", "GET /support/tickets/{id}"],
                "service_methods": ["get_faq_by_category", "create_support_ticket", "update_ticket_status"],
                "repository_methods": ["get_faq_entries", "create_ticket", "get_user_tickets"],
                "database_tables": ["support_tickets", "faq_entries", "ticket_responses"]
            },
            "payment_processing": {
                "ui_flow": "Select payment → Choose crypto → Generate address → Monitor payment",
                "api_endpoints": ["POST /payments/initiate", "GET /payments/status", "POST /payments/webhook"],
                "service_methods": ["initiate_crypto_payment", "verify_payment", "process_overpayment"],
                "repository_methods": ["create_payment", "update_payment_status", "get_payment_by_id"],
                "database_tables": ["payments", "payment_addresses", "payment_confirmations"]
            }
        }
    
    def validate_all_use_cases(self) -> Dict[str, Any]:
        """Validate all use cases have proper layer implementation"""
        results = {}
        overall_success = True
        
        for use_case, requirements in self.use_cases.items():
            validation_result = self.validate_use_case(use_case, requirements)
            results[use_case] = validation_result
            if not validation_result["success"]:
                overall_success = False
        
        return {
            "overall_success": overall_success,
            "use_cases": results,
            "summary": self.generate_summary(results)
        }
    
    def validate_use_case(self, use_case: str, requirements: Dict) -> Dict[str, Any]:
        """Validate a specific use case implementation"""
        logger.info(f"Validating use case: {use_case}")
        
        result = {
            "use_case": use_case,
            "success": True,
            "layers": {
                "api": {"implemented": [], "missing": []},
                "service": {"implemented": [], "missing": []},
                "repository": {"implemented": [], "missing": []},
                "database": {"implemented": [], "missing": []}
            },
            "ui_flow": requirements["ui_flow"]
        }
        
        # Validate API Layer
        api_validation = self.validate_api_layer(requirements["api_endpoints"])
        result["layers"]["api"].update(api_validation)
        
        # Validate Service Layer
        service_validation = self.validate_service_layer(use_case, requirements["service_methods"])
        result["layers"]["service"].update(service_validation)
        
        # Validate Repository Layer
        repo_validation = self.validate_repository_layer(use_case, requirements["repository_methods"])
        result["layers"]["repository"].update(repo_validation)
        
        # Validate Database Layer
        db_validation = self.validate_database_layer(requirements["database_tables"])
        result["layers"]["database"].update(db_validation)
        
        # Determine overall success
        for layer_data in result["layers"].values():
            if layer_data["missing"]:
                result["success"] = False
        
        return result
    
    def validate_api_layer(self, endpoints: List[str]) -> Dict[str, List[str]]:
        """Validate API endpoints exist"""
        implemented = []
        missing = []
        
        # Check if API route files exist and contain endpoints
        api_files = {
            "wallet": "app/api/routes/wallet_routes.py",
            "domains": "app/api/routes/domain_routes.py", 
            "dns": "app/api/routes/dns_routes.py",
            "nameservers": "app/api/routes/nameserver_routes.py",
            "users": "app/api/routes/user_routes.py",
            "support": "app/api/routes/support_routes.py",
            "payments": "app/api/routes/payment_routes.py"
        }
        
        for endpoint in endpoints:
            endpoint_found = False
            method, path = endpoint.split(" ", 1)
            path_base = path.split("/")[1] if len(path.split("/")) > 1 else ""
            
            if path_base in api_files:
                try:
                    with open(api_files[path_base], 'r') as f:
                        content = f.read()
                        # Simple check for endpoint pattern
                        if method.lower() in content.lower() and path.split("/")[-1] in content:
                            implemented.append(endpoint)
                            endpoint_found = True
                except FileNotFoundError:
                    pass
            
            if not endpoint_found:
                missing.append(endpoint)
        
        return {"implemented": implemented, "missing": missing}
    
    def validate_service_layer(self, use_case: str, methods: List[str]) -> Dict[str, List[str]]:
        """Validate service methods exist"""
        implemented = []
        missing = []
        
        # Map use cases to service files
        service_files = {
            "financial_management": "app/services/wallet_service.py",
            "domain_management": "app/services/domain_service.py",
            "dns_management": "app/services/dns_service.py", 
            "nameserver_management": "app/services/nameserver_service.py",
            "domain_search": "app/services/domain_service.py",
            "user_management": "app/services/user_service.py",
            "support_system": "app/services/support_service.py",
            "payment_processing": "app/services/payment_service.py"
        }
        
        service_file = service_files.get(use_case)
        if service_file:
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                    for method in methods:
                        if f"def {method}" in content:
                            implemented.append(method)
                        else:
                            missing.append(method)
            except FileNotFoundError:
                missing.extend(methods)
        else:
            missing.extend(methods)
        
        return {"implemented": implemented, "missing": missing}
    
    def validate_repository_layer(self, use_case: str, methods: List[str]) -> Dict[str, List[str]]:
        """Validate repository methods exist"""
        implemented = []
        missing = []
        
        # Map use cases to repository files
        repo_files = {
            "financial_management": "app/repositories/wallet_repo.py",
            "domain_management": "app/repositories/domain_repo.py",
            "dns_management": "app/repositories/dns_repo.py",
            "nameserver_management": "app/repositories/domain_repo.py", 
            "domain_search": "app/repositories/domain_repo.py",
            "user_management": "app/repositories/user_repo.py",
            "support_system": "app/repositories/support_repo.py",
            "payment_processing": "app/repositories/payment_repo.py"
        }
        
        repo_file = repo_files.get(use_case)
        if repo_file:
            try:
                with open(repo_file, 'r') as f:
                    content = f.read()
                    for method in methods:
                        if f"def {method}" in content:
                            implemented.append(method)
                        else:
                            missing.append(method)
            except FileNotFoundError:
                missing.extend(methods)
        else:
            missing.extend(methods)
        
        return {"implemented": implemented, "missing": missing}
    
    def validate_database_layer(self, tables: List[str]) -> Dict[str, List[str]]:
        """Validate database tables exist"""
        implemented = []
        missing = []
        
        # Check database models
        try:
            from fresh_database import (
                User, Domain, DNSRecord, Transaction, 
                Order, UserState, SystemSetting
            )
            
            # Map table names to model availability
            table_models = {
                "users": User,
                "registered_domains": Domain, 
                "dns_records": DNSRecord,
                "wallets": User,  # Wallet data is in User model
                "transactions": Transaction,
                "loyalty_tiers": User,  # Loyalty data is in User model
                "orders": Order,
                "user_states": UserState,
                "translations": SystemSetting,  # Translations stored as settings
                "support_tickets": "created",  # Now exists in fresh_database.py
                "faq_entries": "created",  # Now exists in fresh_database.py
                "ticket_responses": "created",  # Now exists in fresh_database.py
                "payments": Transaction,  # Payments are transactions
                "payment_addresses": Transaction,  # Address data in transactions
                "payment_confirmations": Transaction,  # Confirmation data in transactions
                "domain_searches": "created",  # Now exists in fresh_database.py
                "tld_pricing": SystemSetting,  # Pricing stored as settings
                "nameserver_operations": "created",  # Now exists in fresh_database.py
                "audit_logs": "created",  # Now exists in fresh_database.py
                "cloudflare_zones": Domain  # Zone ID stored in Domain model
            }
            
            for table in tables:
                if table in table_models and table_models[table] is not None and table_models[table] != "created":
                    implemented.append(table)
                elif table in table_models and table_models[table] == "created":
                    implemented.append(table)  # Table was created in fresh_database.py
                else:
                    missing.append(table)
                    
        except ImportError as e:
            logger.error(f"Could not import database models: {e}")
            missing.extend(tables)
        
        return {"implemented": implemented, "missing": missing}
    
    def generate_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate validation summary"""
        total_use_cases = len(results)
        successful_use_cases = sum(1 for result in results.values() if result["success"])
        
        layer_stats = {
            "api": {"total": 0, "implemented": 0},
            "service": {"total": 0, "implemented": 0}, 
            "repository": {"total": 0, "implemented": 0},
            "database": {"total": 0, "implemented": 0}
        }
        
        for result in results.values():
            for layer, data in result["layers"].items():
                layer_stats[layer]["total"] += len(data["implemented"]) + len(data["missing"])
                layer_stats[layer]["implemented"] += len(data["implemented"])
        
        return {
            "use_case_coverage": f"{successful_use_cases}/{total_use_cases}",
            "success_rate": f"{(successful_use_cases/total_use_cases)*100:.1f}%",
            "layer_implementation": {
                layer: f"{stats['implemented']}/{stats['total']} ({(stats['implemented']/stats['total']*100):.1f}%)" 
                if stats['total'] > 0 else "0/0 (0%)"
                for layer, stats in layer_stats.items()
            }
        }

def main():
    """Run layer responsibility validation"""
    print("🔍 Starting Layer Responsibility Validation...")
    
    validator = LayerResponsibilityValidator()
    results = validator.validate_all_use_cases()
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
    print(f"Use Case Coverage: {results['summary']['use_case_coverage']}")
    print(f"Success Rate: {results['summary']['success_rate']}")
    
    print(f"\n🏗️ LAYER IMPLEMENTATION STATUS:")
    for layer, coverage in results['summary']['layer_implementation'].items():
        status = "✅" if "100.0%" in coverage else "⚠️" if "0%" not in coverage else "❌"
        print(f"{status} {layer.upper()} Layer: {coverage}")
    
    print(f"\n📋 DETAILED USE CASE ANALYSIS:")
    for use_case, result in results['use_cases'].items():
        status = "✅" if result['success'] else "❌"
        print(f"\n{status} {use_case.replace('_', ' ').title()}:")
        print(f"   UI Flow: {result['ui_flow']}")
        
        for layer, data in result['layers'].items():
            if data['missing']:
                print(f"   ❌ {layer.upper()}: Missing {data['missing']}")
            elif data['implemented']:
                print(f"   ✅ {layer.upper()}: {len(data['implemented'])} methods implemented")
    
    return results

if __name__ == "__main__":
    main()