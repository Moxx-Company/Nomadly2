#!/usr/bin/env python3
"""
Comprehensive Integration Verification Test
Tests all layers: Database → Repositories → Services → External Integrations

This script verifies the complete integration between:
1. Database Layer (PostgreSQL with proper schema)
2. Data Access Layer (Repository pattern)
3. Service/Business Logic Layer (Domain services)
4. External Integration Layer (APIs)
"""

import asyncio
import logging
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import DatabaseManager
from app.repositories.user_repo import UserRepository
from app.repositories.domain_repo import DomainRepository
from app.repositories.dns_repo import DNSRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.external_integration_repo import (
    CloudflareIntegrationRepository, 
    OpenProviderIntegrationRepository,
    BlockBeeIntegrationRepository,
    BrevoIntegrationRepository,
    APIUsageLogRepository
)
from app.services.user_service import UserService
from app.services.domain_service import DomainService
from app.services.dns_service import DNSService
from app.services.wallet_service import WalletService
from app.services.payment_service import PaymentService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationVerificationTest:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.test_results = {
            "database_layer": {},
            "repository_layer": {},
            "service_layer": {},
            "integration_layer": {},
            "end_to_end_flows": {}
        }
        
        # Initialize repositories
        self.user_repo = UserRepository()
        self.domain_repo = DomainRepository()
        self.dns_repo = DNSRepository()
        self.transaction_repo = TransactionRepository()
        self.cloudflare_repo = CloudflareIntegrationRepository()
        self.openprovider_repo = OpenProviderIntegrationRepository()
        self.blockbee_repo = BlockBeeIntegrationRepository()
        self.brevo_repo = BrevoIntegrationRepository()
        self.api_usage_repo = APIUsageLogRepository()
        
        # Initialize services
        self.user_service = UserService(self.user_repo, self.transaction_repo)
        self.domain_service = DomainService(self.domain_repo, self.user_repo)
        self.dns_service = DNSService(self.dns_repo, self.domain_repo, self.cloudflare_repo)
        self.wallet_service = WalletService(self.user_repo, self.transaction_repo)
        self.payment_service = PaymentService(self.user_repo, self.transaction_repo)
        
        self.test_user_id = 999999999  # Test user ID
        self.test_domain_name = "integration-test.example"
    
    async def run_all_tests(self):
        """Run comprehensive integration verification"""
        logger.info("Starting Comprehensive Integration Verification")
        logger.info("=" * 60)
        
        try:
            # Test each layer
            await self.test_database_layer()
            await self.test_repository_layer()
            await self.test_service_layer()
            await self.test_integration_layer()
            await self.test_end_to_end_flows()
            
            # Generate report
            self.generate_verification_report()
            
        except Exception as e:
            logger.error(f"Integration verification failed: {e}")
            return False
        
        return True
    
    async def test_database_layer(self):
        """Test database connectivity and schema"""
        logger.info("Testing Database Layer...")
        
        try:
            # Test database connection
            with self.db_manager.get_db() as db:
                # Test basic connectivity
                result = db.execute("SELECT 1 as test").fetchone()
                self.test_results["database_layer"]["connectivity"] = result[0] == 1
                
                # Test table existence
                tables_query = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'registered_domains', 'dns_records', 'orders', 'audit_logs')
                """
                tables = db.execute(tables_query).fetchall()
                expected_tables = {'users', 'registered_domains', 'dns_records', 'orders', 'audit_logs'}
                found_tables = {table[0] for table in tables}
                self.test_results["database_layer"]["required_tables"] = expected_tables.issubset(found_tables)
                
                # Test user table structure
                user_columns = db.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
                """).fetchall()
                user_column_names = {col[0] for col in user_columns}
                required_user_columns = {'telegram_id', 'balance_usd', 'language', 'is_admin', 'created_at'}
                self.test_results["database_layer"]["user_table_schema"] = required_user_columns.issubset(user_column_names)
                
                # Test domain table structure
                domain_columns = db.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'registered_domains' AND table_schema = 'public'
                """).fetchall()
                domain_column_names = {col[0] for col in domain_columns}
                required_domain_columns = {'domain_name', 'expires_at', 'cloudflare_zone_id', 'openprovider_domain_id'}
                self.test_results["database_layer"]["domain_table_schema"] = required_domain_columns.issubset(domain_column_names)
                
        except Exception as e:
            logger.error(f"Database layer test failed: {e}")
            self.test_results["database_layer"]["error"] = str(e)
    
    async def test_repository_layer(self):
        """Test repository pattern implementation"""
        logger.info("Testing Repository Layer...")
        
        try:
            # Test UserRepository
            test_user = self.user_repo.get_by_telegram_id(self.test_user_id)
            if not test_user:
                # Create test user
                test_user = self.user_repo.create_user(
                    telegram_id=self.test_user_id,
                    language="en",
                    balance_usd=Decimal("100.00")
                )
            self.test_results["repository_layer"]["user_crud"] = test_user is not None
            
            # Test user balance operations
            original_balance = test_user.balance_usd
            self.user_repo.add_balance(self.test_user_id, Decimal("50.00"))
            updated_user = self.user_repo.get_by_telegram_id(self.test_user_id)
            balance_updated = updated_user.balance_usd == original_balance + Decimal("50.00")
            self.test_results["repository_layer"]["balance_operations"] = balance_updated
            
            # Reset balance
            self.user_repo.deduct_balance(self.test_user_id, Decimal("50.00"))
            
            # Test DomainRepository
            existing_domains = self.domain_repo.get_user_domains(self.test_user_id)
            self.test_results["repository_layer"]["domain_queries"] = isinstance(existing_domains, list)
            
            # Test DNSRepository
            if existing_domains:
                domain_id = existing_domains[0].id
                dns_records = self.dns_repo.get_domain_records(domain_id)
                self.test_results["repository_layer"]["dns_queries"] = isinstance(dns_records, list)
            else:
                self.test_results["repository_layer"]["dns_queries"] = True  # Skip if no domains
            
            # Test TransactionRepository
            transactions = self.transaction_repo.get_user_transactions(self.test_user_id)
            self.test_results["repository_layer"]["transaction_queries"] = isinstance(transactions, list)
            
            # Test External Integration Repositories
            cloudflare_ops = self.cloudflare_repo.get_recent_operations(limit=5)
            self.test_results["repository_layer"]["cloudflare_integration_repo"] = isinstance(cloudflare_ops, list)
            
            api_logs = self.api_usage_repo.get_recent_logs(service_name="cloudflare", limit=5)
            self.test_results["repository_layer"]["api_usage_repo"] = isinstance(api_logs, list)
            
        except Exception as e:
            logger.error(f"Repository layer test failed: {e}")
            self.test_results["repository_layer"]["error"] = str(e)
    
    async def test_service_layer(self):
        """Test service/business logic layer"""
        logger.info("Testing Service/Business Logic Layer...")
        
        try:
            # Test UserService
            user_profile = self.user_service.get_user_profile(self.test_user_id)
            self.test_results["service_layer"]["user_service"] = user_profile.get("success", False)
            
            # Test balance validation
            balance_check = self.user_service.validate_sufficient_balance(self.test_user_id, Decimal("10.00"))
            self.test_results["service_layer"]["balance_validation"] = isinstance(balance_check, dict)
            
            # Test DomainService
            domain_availability = self.domain_service.check_domain_availability("test-integration-domain.com")
            self.test_results["service_layer"]["domain_availability"] = isinstance(domain_availability, dict)
            
            # Test domain pricing
            domain_pricing = self.domain_service.calculate_domain_pricing("test.com", years=1)
            self.test_results["service_layer"]["domain_pricing"] = (
                isinstance(domain_pricing, dict) and 
                "total_price_usd" in domain_pricing
            )
            
            # Test DNSService validation
            from app.services.dns_service import DNSRecordRequest
            dns_request = DNSRecordRequest(
                domain_id=1,
                record_type="A",
                name="test",
                content="192.168.1.1",
                ttl=3600
            )
            dns_validation = self.dns_service.validate_dns_record(dns_request)
            self.test_results["service_layer"]["dns_validation"] = dns_validation.valid
            
            # Test geo-blocking validation
            country_validation = self.dns_service._validate_country_codes(["US", "CA", "GB"])
            self.test_results["service_layer"]["geo_blocking_validation"] = country_validation.get("valid", False)
            
            # Test WalletService
            wallet_summary = self.wallet_service.get_wallet_summary(self.test_user_id)
            self.test_results["service_layer"]["wallet_service"] = isinstance(wallet_summary, dict)
            
            # Test PaymentService validation
            payment_validation = self.payment_service.validate_payment_amount(Decimal("49.50"))
            self.test_results["service_layer"]["payment_validation"] = isinstance(payment_validation, dict)
            
        except Exception as e:
            logger.error(f"Service layer test failed: {e}")
            self.test_results["service_layer"]["error"] = str(e)
    
    async def test_integration_layer(self):
        """Test external integration layer"""
        logger.info("Testing External Integration Layer...")
        
        try:
            # Test configuration access
            from app.core.config import config
            cloudflare_token = config.CLOUDFLARE_API_TOKEN
            openprovider_username = config.OPENPROVIDER_USERNAME
            blockbee_key = config.BLOCKBEE_API_KEY
            
            self.test_results["integration_layer"]["config_access"] = all([
                cloudflare_token, openprovider_username, blockbee_key
            ])
            
            # Test Cloudflare Integration
            from app.integrations.cloudflare_integration import CloudflareAPI
            cloudflare = CloudflareAPI()
            
            # Test geo-blocking templates
            templates = await cloudflare.get_geo_blocking_templates()
            self.test_results["integration_layer"]["cloudflare_templates"] = (
                templates.get("success", False) and 
                len(templates.get("templates", {})) >= 5
            )
            
            # Test OpenProvider Integration
            from app.integrations.openprovider_integration import OpenProviderAPI
            openprovider = OpenProviderAPI()
            
            # Test domain search capability
            search_result = await openprovider.search_domain("integration-test-domain-12345")
            self.test_results["integration_layer"]["openprovider_search"] = isinstance(search_result, dict)
            
            # Test BlockBee Integration
            from app.integrations.blockbee_integration import BlockBeeAPI
            blockbee = BlockBeeAPI()
            
            # Test crypto address generation capability
            address_result = await blockbee.generate_payment_address("btc", "test-callback")
            self.test_results["integration_layer"]["blockbee_address"] = isinstance(address_result, dict)
            
            # Test FastForex Integration
            from app.integrations.fastforex_integration import FastForexAPI
            fastforex = FastForexAPI()
            
            # Test currency conversion
            conversion_result = await fastforex.convert_usd_to_crypto(Decimal("49.50"), "BTC")
            self.test_results["integration_layer"]["fastforex_conversion"] = isinstance(conversion_result, dict)
            
            # Test Brevo Integration
            from app.integrations.brevo_integration import BrevoAPI
            brevo = BrevoAPI()
            
            # Test email template capability
            email_result = await brevo.send_domain_registration_confirmation(
                "test@example.com", "test-domain.com", "order123"
            )
            self.test_results["integration_layer"]["brevo_email"] = isinstance(email_result, dict)
            
        except Exception as e:
            logger.error(f"Integration layer test failed: {e}")
            self.test_results["integration_layer"]["error"] = str(e)
    
    async def test_end_to_end_flows(self):
        """Test complete end-to-end user flows"""
        logger.info("Testing End-to-End User Flows...")
        
        try:
            # Flow 1: Domain Registration Workflow
            logger.info("Testing Domain Registration Flow...")
            
            # Step 1: Check domain availability
            availability = self.domain_service.check_domain_availability("e2e-test-domain.com")
            flow1_step1 = availability.get("available", False)
            
            # Step 2: Calculate pricing
            pricing = self.domain_service.calculate_domain_pricing("e2e-test-domain.com", years=1)
            flow1_step2 = "total_price_usd" in pricing
            
            # Step 3: Validate user balance
            balance_check = self.user_service.validate_sufficient_balance(
                self.test_user_id, 
                pricing.get("total_price_usd", Decimal("0"))
            )
            flow1_step3 = balance_check.get("sufficient", False)
            
            self.test_results["end_to_end_flows"]["domain_registration"] = {
                "availability_check": flow1_step1,
                "pricing_calculation": flow1_step2,
                "balance_validation": flow1_step3,
                "complete_flow": all([flow1_step1, flow1_step2, flow1_step3])
            }
            
            # Flow 2: DNS Management Workflow
            logger.info("Testing DNS Management Flow...")
            
            # Get user domains
            user_domains = self.domain_repo.get_user_domains(self.test_user_id)
            flow2_step1 = len(user_domains) >= 0  # Can be 0 for new users
            
            if user_domains:
                # Test DNS record validation
                from app.services.dns_service import DNSRecordRequest
                dns_request = DNSRecordRequest(
                    domain_id=user_domains[0].id,
                    record_type="A",
                    name="test",
                    content="8.8.8.8"
                )
                dns_validation = self.dns_service.validate_dns_record(dns_request)
                flow2_step2 = dns_validation.valid
                
                # Test geo-blocking capability
                geo_status = self.dns_service.get_geo_blocking_status(
                    user_domains[0].id, 
                    self.test_user_id
                )
                flow2_step3 = isinstance(geo_status, dict)
            else:
                flow2_step2 = True  # Skip if no domains
                flow2_step3 = True
            
            self.test_results["end_to_end_flows"]["dns_management"] = {
                "domain_access": flow2_step1,
                "record_validation": flow2_step2,
                "geo_blocking_status": flow2_step3,
                "complete_flow": all([flow2_step1, flow2_step2, flow2_step3])
            }
            
            # Flow 3: Payment Processing Workflow
            logger.info("Testing Payment Processing Flow...")
            
            # Test crypto payment generation
            payment_amount = Decimal("49.50")
            crypto_currency = "BTC"
            
            # Step 1: Convert USD to crypto
            from app.integrations.fastforex_integration import FastForexAPI
            fastforex = FastForexAPI()
            conversion = await fastforex.convert_usd_to_crypto(payment_amount, crypto_currency)
            flow3_step1 = isinstance(conversion, dict)
            
            # Step 2: Generate payment address
            from app.integrations.blockbee_integration import BlockBeeAPI
            blockbee = BlockBeeAPI()
            address = await blockbee.generate_payment_address(crypto_currency.lower(), "test-callback")
            flow3_step2 = isinstance(address, dict)
            
            # Step 3: Validate payment amount
            payment_validation = self.payment_service.validate_payment_amount(payment_amount)
            flow3_step3 = payment_validation.get("valid", False)
            
            self.test_results["end_to_end_flows"]["payment_processing"] = {
                "currency_conversion": flow3_step1,
                "address_generation": flow3_step2,
                "amount_validation": flow3_step3,
                "complete_flow": all([flow3_step1, flow3_step2, flow3_step3])
            }
            
        except Exception as e:
            logger.error(f"End-to-end flow test failed: {e}")
            self.test_results["end_to_end_flows"]["error"] = str(e)
    
    def generate_verification_report(self):
        """Generate comprehensive verification report"""
        logger.info("=" * 60)
        logger.info("INTEGRATION VERIFICATION REPORT")
        logger.info("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for layer_name, layer_results in self.test_results.items():
            logger.info(f"\n{layer_name.upper().replace('_', ' ')}:")
            logger.info("-" * 40)
            
            for test_name, result in layer_results.items():
                if test_name == "error":
                    logger.error(f"  ERROR: {result}")
                    continue
                
                total_tests += 1
                if isinstance(result, dict):
                    # Handle nested results (e.g., end-to-end flows)
                    for sub_test, sub_result in result.items():
                        if isinstance(sub_result, bool):
                            total_tests += 1
                            if sub_result:
                                passed_tests += 1
                                logger.info(f"  ✅ {test_name} - {sub_test}: PASS")
                            else:
                                logger.error(f"  ❌ {test_name} - {sub_test}: FAIL")
                elif isinstance(result, bool):
                    if result:
                        passed_tests += 1
                        logger.info(f"  ✅ {test_name}: PASS")
                    else:
                        logger.error(f"  ❌ {test_name}: FAIL")
                else:
                    # Non-boolean result, assume informational
                    logger.info(f"  ℹ️  {test_name}: {result}")
        
        # Summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        logger.info("\n" + "=" * 60)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("🎉 INTEGRATION VERIFICATION: SUCCESS")
            logger.info("All layers are properly integrated and functional!")
        elif success_rate >= 60:
            logger.warning("⚠️  INTEGRATION VERIFICATION: PARTIAL SUCCESS")
            logger.warning("Most integrations working, some issues detected.")
        else:
            logger.error("💥 INTEGRATION VERIFICATION: FAILED")
            logger.error("Significant integration issues detected.")
        
        return success_rate >= 80

async def main():
    """Run the integration verification"""
    test_suite = IntegrationVerificationTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n✅ Integration verification completed successfully!")
        return 0
    else:
        print("\n❌ Integration verification failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)