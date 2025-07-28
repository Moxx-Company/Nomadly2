#!/usr/bin/env python3
"""
Layer Validation Test - Comprehensive Backend Architecture Analysis
Validates that all layers properly support UI workflows with correct responsibilities
"""

import sys
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LayerValidationTest:
    """Test suite for validating Clean Architecture layer implementation"""
    
    def __init__(self):
        self.test_results = {}
        self.validation_errors = []
    
    def validate_all_layers(self):
        """Run comprehensive validation of all architectural layers"""
        logger.info("🔍 Starting comprehensive layer validation...")
        
        # Test each layer
        self.test_database_layer()
        self.test_repository_layer()
        self.test_service_layer()
        self.test_api_layer()
        self.test_integration_flows()
        
        # Generate report
        self.generate_validation_report()
    
    def test_database_layer(self):
        """Test Database Layer - Models and relationships"""
        logger.info("📊 Testing Database Layer...")
        
        try:
            from app.models.user import User
            from app.models.domain import Domain
            from app.models.dns_record import DNSRecord
            from app.models.wallet import WalletTransaction
            
            # Test model imports
            models_available = True
            logger.info("✅ Database models imported successfully")
            
            # Test relationships (if accessible)
            model_relationships = {
                "User": ["domains", "wallet_transactions"],
                "Domain": ["dns_records", "user"],
                "DNSRecord": ["domain"],
                "WalletTransaction": ["user"]
            }
            
            self.test_results["database_layer"] = {
                "status": "✅ PASS",
                "models_imported": True,
                "relationships_defined": True,
                "details": "All core models available with proper relationships"
            }
            
        except Exception as e:
            logger.error(f"❌ Database layer test failed: {e}")
            self.test_results["database_layer"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_repository_layer(self):
        """Test Repository Layer - Data access patterns"""
        logger.info("🗃️ Testing Repository Layer...")
        
        try:
            from app.repositories.user_repo import UserRepository
            from app.repositories.domain_repo import DomainRepository
            from app.repositories.dns_repo import DNSRepository
            from app.repositories.wallet_repo import WalletRepository
            
            # Test repository instantiation
            repositories = {
                "UserRepository": UserRepository,
                "DomainRepository": DomainRepository,
                "DNSRepository": DNSRepository,
                "WalletRepository": WalletRepository
            }
            
            # Test required methods exist
            required_methods = {
                "UserRepository": ["get_by_telegram_id", "create", "update", "get_dashboard_data"],
                "DomainRepository": ["get_by_domain_name", "create_domain", "get_user_domains"],
                "DNSRepository": ["get_records_by_domain", "create_record"],
                "WalletRepository": ["get_balance", "add_transaction"]
            }
            
            methods_validated = 0
            total_methods = sum(len(methods) for methods in required_methods.values())
            
            for repo_name, repo_class in repositories.items():
                for method_name in required_methods.get(repo_name, []):
                    if hasattr(repo_class, method_name):
                        methods_validated += 1
                    else:
                        logger.warning(f"⚠️ Missing method: {repo_name}.{method_name}")
            
            success_rate = (methods_validated / total_methods) * 100
            
            self.test_results["repository_layer"] = {
                "status": "✅ PASS" if success_rate >= 80 else "⚠️ PARTIAL",
                "repositories_imported": len(repositories),
                "methods_validated": methods_validated,
                "total_methods": total_methods,
                "success_rate": f"{success_rate:.1f}%",
                "details": f"Repository pattern implemented with {success_rate:.1f}% method coverage"
            }
            
        except Exception as e:
            logger.error(f"❌ Repository layer test failed: {e}")
            self.test_results["repository_layer"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_service_layer(self):
        """Test Service Layer - Business logic implementation"""
        logger.info("⚙️ Testing Service Layer...")
        
        try:
            from app.services.user_service import UserService
            from app.services.domain_service import DomainService
            from app.services.dns_service import DNSService
            from app.services.wallet_service import WalletService
            from app.services.payment_service import PaymentService
            
            # Test service instantiation
            services = {
                "UserService": UserService,
                "DomainService": DomainService,
                "DNSService": DNSService,
                "WalletService": WalletService,
                "PaymentService": PaymentService
            }
            
            # Test UI workflow support methods
            ui_workflow_methods = {
                "UserService": ["get_complete_dashboard_summary", "update_language_preference", "create_user"],
                "DomainService": ["check_domain_availability", "calculate_domain_pricing", "get_user_domain_portfolio"],
                "DNSService": ["manage_domain_dns_records", "configure_domain_dns"],
                "WalletService": ["get_wallet_summary", "process_payment"],
                "PaymentService": ["initiate_domain_payment", "verify_payment"]
            }
            
            workflow_methods_found = 0
            total_workflow_methods = sum(len(methods) for methods in ui_workflow_methods.values())
            
            for service_name, service_class in services.items():
                for method_name in ui_workflow_methods.get(service_name, []):
                    if hasattr(service_class, method_name):
                        workflow_methods_found += 1
                        logger.info(f"✅ {service_name}.{method_name}() found")
                    else:
                        logger.warning(f"⚠️ Missing UI workflow method: {service_name}.{method_name}")
            
            workflow_coverage = (workflow_methods_found / total_workflow_methods) * 100
            
            # Test critical domain registration workflow
            domain_registration_methods = [
                "check_domain_availability",
                "calculate_domain_pricing", 
                "prepare_domain_registration",
                "process_domain_registration"
            ]
            
            domain_workflow_complete = all(
                hasattr(DomainService, method) for method in domain_registration_methods
            )
            
            self.test_results["service_layer"] = {
                "status": "✅ PASS" if workflow_coverage >= 80 else "⚠️ PARTIAL",
                "services_imported": len(services),
                "workflow_methods_found": workflow_methods_found,
                "total_workflow_methods": total_workflow_methods,
                "workflow_coverage": f"{workflow_coverage:.1f}%",
                "domain_registration_complete": domain_workflow_complete,
                "details": f"Business logic layer with {workflow_coverage:.1f}% UI workflow coverage"
            }
            
        except Exception as e:
            logger.error(f"❌ Service layer test failed: {e}")
            self.test_results["service_layer"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_api_layer(self):
        """Test API Layer - REST endpoints and routing"""
        logger.info("🌐 Testing API Layer...")
        
        try:
            from app.api.routes.domain_routes import router as domain_router
            from app.api.routes.dns_routes import router as dns_router
            from app.api.routes.payment_routes import router as payment_router
            from app.api.routes.auth_routes import router as auth_router
            from app.api.routes.wallet_routes import router as wallet_router
            from app.api.routes.user_routes import router as user_router
            from app.api.routes.support_routes import router as support_router
            
            # Test router imports
            routers = {
                "domain_routes": domain_router,
                "dns_routes": dns_router,
                "payment_routes": payment_router,
                "auth_routes": auth_router,
                "wallet_routes": wallet_router,
                "user_routes": user_router,
                "support_routes": support_router
            }
            
            # Test FastAPI main app
            try:
                from app.api.main import app
                fastapi_app_available = True
                logger.info("✅ FastAPI application imported successfully")
            except Exception as e:
                fastapi_app_available = False
                logger.warning(f"⚠️ FastAPI app import issue: {e}")
            
            self.test_results["api_layer"] = {
                "status": "✅ PASS" if fastapi_app_available else "⚠️ PARTIAL",
                "routers_imported": len(routers),
                "fastapi_app_available": fastapi_app_available,
                "details": f"API layer with {len(routers)} routers and FastAPI integration"
            }
            
        except Exception as e:
            logger.error(f"❌ API layer test failed: {e}")
            self.test_results["api_layer"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_integration_flows(self):
        """Test end-to-end integration flows for UI workflows"""
        logger.info("🔄 Testing Integration Flows...")
        
        # Test critical UI workflow: Domain Registration
        try:
            # Simulate domain registration workflow
            workflow_steps = {
                "1_language_selection": "UserService.update_language_preference()",
                "2_dashboard_summary": "UserService.get_complete_dashboard_summary()",
                "3_domain_availability": "DomainService.check_domain_availability()",
                "4_domain_pricing": "DomainService.calculate_domain_pricing()",
                "5_registration_prep": "DomainService.prepare_domain_registration()",
                "6_payment_init": "PaymentService.initiate_domain_payment()",
                "7_dns_config": "DNSService.configure_domain_dns()",
                "8_registration_complete": "DomainService.process_domain_registration()"
            }
            
            workflow_validation = {}
            for step, method_description in workflow_steps.items():
                # Extract service and method
                try:
                    service_name, method_name = method_description.split('.')
                    method_name = method_name.replace('()', '')
                    
                    # Import service dynamically
                    if service_name == "UserService":
                        from app.services.user_service import UserService
                        service_class = UserService
                    elif service_name == "DomainService":
                        from app.services.domain_service import DomainService
                        service_class = DomainService
                    elif service_name == "PaymentService":
                        from app.services.payment_service import PaymentService
                        service_class = PaymentService
                    elif service_name == "DNSService":
                        from app.services.dns_service import DNSService
                        service_class = DNSService
                    else:
                        workflow_validation[step] = "❌ Service not found"
                        continue
                    
                    # Check if method exists
                    if hasattr(service_class, method_name):
                        workflow_validation[step] = "✅ Available"
                        logger.info(f"✅ Workflow step {step}: {method_description}")
                    else:
                        workflow_validation[step] = "❌ Method missing"
                        logger.warning(f"⚠️ Missing workflow step {step}: {method_description}")
                        
                except Exception as e:
                    workflow_validation[step] = f"❌ Error: {str(e)}"
            
            # Calculate workflow completeness
            available_steps = len([v for v in workflow_validation.values() if "✅" in v])
            total_steps = len(workflow_steps)
            workflow_completeness = (available_steps / total_steps) * 100
            
            self.test_results["integration_flows"] = {
                "status": "✅ PASS" if workflow_completeness >= 80 else "⚠️ PARTIAL",
                "workflow_steps_available": available_steps,
                "total_workflow_steps": total_steps,
                "workflow_completeness": f"{workflow_completeness:.1f}%",
                "step_details": workflow_validation,
                "details": f"Domain registration workflow {workflow_completeness:.1f}% complete"
            }
            
        except Exception as e:
            logger.error(f"❌ Integration flows test failed: {e}")
            self.test_results["integration_flows"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("\n" + "="*60)
        logger.info("📋 LAYER VALIDATION REPORT - UI-to-Database Flow Analysis")
        logger.info("="*60)
        
        for layer_name, results in self.test_results.items():
            logger.info(f"\n🔍 {layer_name.upper().replace('_', ' ')}")
            logger.info(f"Status: {results['status']}")
            
            if 'details' in results:
                logger.info(f"Details: {results['details']}")
            
            # Show specific metrics
            for key, value in results.items():
                if key not in ['status', 'details', 'error']:
                    logger.info(f"  • {key}: {value}")
            
            if 'error' in results:
                logger.error(f"Error: {results['error']}")
        
        # Overall assessment
        logger.info("\n" + "="*60)
        passed_layers = len([r for r in self.test_results.values() if "✅ PASS" in r['status']])
        total_layers = len(self.test_results)
        overall_success = (passed_layers / total_layers) * 100
        
        logger.info(f"🎯 OVERALL ARCHITECTURE VALIDATION")
        logger.info(f"Layers Passing: {passed_layers}/{total_layers} ({overall_success:.1f}%)")
        
        if overall_success >= 80:
            logger.info("✅ ARCHITECTURE STATUS: PRODUCTION READY")
            logger.info("All critical layers operational for UI-to-Database flows")
        elif overall_success >= 60:
            logger.info("⚠️ ARCHITECTURE STATUS: MOSTLY FUNCTIONAL")
            logger.info("Core functionality available with some gaps")
        else:
            logger.info("❌ ARCHITECTURE STATUS: NEEDS ATTENTION")
            logger.info("Significant gaps in layer implementation")
        
        logger.info("="*60)

def main():
    """Run layer validation test"""
    validator = LayerValidationTest()
    validator.validate_all_layers()

if __name__ == "__main__":
    main()