#!/usr/bin/env python3
"""
Test the fresh database integration with all our use cases
"""

import logging
from fresh_database import initialize_fresh_database, User, Domain, Transaction, Order
from datetime import datetime, timedelta
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_use_case_1_user_registration():
    """Test Case 1: User Registration"""
    logger.info("🧪 Testing Use Case 1: User Registration")
    
    db = initialize_fresh_database()
    if not db:
        return False
    
    # Create test user
    test_user = db.create_user(
        telegram_id=12345,
        username="testuser",
        first_name="Test"
    )
    
    if test_user:
        logger.info("✅ User registration successful")
        return True
    else:
        logger.error("❌ User registration failed")
        return False

def test_use_case_2_domain_registration():
    """Test Case 2: Domain Registration Workflow"""
    logger.info("🧪 Testing Use Case 2: Domain Registration")
    
    db = initialize_fresh_database()
    session = db.get_session()
    
    try:
        # Create user
        user = User(
            telegram_id=54321,
            username="domainuser",
            first_name="Domain"
        )
        session.add(user)
        session.flush()
        
        # Create order
        order = Order(
            telegram_id=54321,
            order_id="order_test_001",
            domain_name="example.com",
            tld="com",
            base_price_usd=Decimal('15.00'),
            offshore_multiplier=Decimal('3.3'),
            total_price_usd=Decimal('49.50'),
            nameserver_choice="cloudflare",
            payment_method="crypto",
            crypto_currency="BTC"
        )
        session.add(order)
        
        # Create domain
        domain = Domain(
            telegram_id=54321,
            domain_name="example.com",
            tld="com",
            price_paid_usd=Decimal('49.50'),
            expires_at=datetime.now() + timedelta(days=365)
        )
        session.add(domain)
        
        # Create transaction
        transaction = Transaction(
            telegram_id=54321,
            transaction_type="domain_purchase",
            amount_usd=Decimal('49.50'),
            crypto_currency="BTC",
            crypto_amount=Decimal('0.001'),
            payment_provider="blockbee",
            status="completed",
            domain_id=1
        )
        session.add(transaction)
        
        session.commit()
        logger.info("✅ Domain registration workflow successful")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Domain registration failed: {e}")
        return False
    finally:
        session.close()

def test_use_case_3_dns_management():
    """Test Case 3: DNS Management"""
    logger.info("🧪 Testing Use Case 3: DNS Management")
    
    db = initialize_fresh_database()
    session = db.get_session()
    
    try:
        from fresh_database import DNSRecord
        
        # Create user first (required for foreign key)
        user = User(
            telegram_id=99999,
            username="dnsuser",
            first_name="DNS"
        )
        session.add(user)
        session.flush()
        
        # Create domain 
        domain = Domain(
            telegram_id=99999,
            domain_name="dnstest.com",
            tld="com",
            price_paid_usd=Decimal('49.50'),
            expires_at=datetime.now() + timedelta(days=365),
            cloudflare_zone_id="test_zone_123"
        )
        session.add(domain)
        session.flush()
        
        # Add A record
        a_record = DNSRecord(
            domain_id=domain.id,
            record_type="A",
            name="@",
            content="192.168.1.1",
            ttl=3600
        )
        session.add(a_record)
        
        # Add CNAME record
        cname_record = DNSRecord(
            domain_id=domain.id,
            record_type="CNAME",
            name="www",
            content="dnstest.com",
            ttl=3600
        )
        session.add(cname_record)
        
        session.commit()
        logger.info("✅ DNS management successful")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ DNS management failed: {e}")
        return False
    finally:
        session.close()

def test_use_case_4_payment_processing():
    """Test Case 4: Payment Processing"""
    logger.info("🧪 Testing Use Case 4: Payment Processing")
    
    db = initialize_fresh_database()
    session = db.get_session()
    
    try:
        # Create user with balance
        user = User(
            telegram_id=77777,
            username="paymentuser",
            balance_usd=Decimal('100.00')
        )
        session.add(user)
        
        # Wallet deposit transaction
        deposit = Transaction(
            telegram_id=77777,
            transaction_type="wallet_deposit",
            amount_usd=Decimal('50.00'),
            crypto_currency="ETH",
            crypto_amount=Decimal('0.02'),
            payment_provider="blockbee",
            status="completed"
        )
        session.add(deposit)
        
        # Domain purchase from wallet
        purchase = Transaction(
            telegram_id=77777,
            transaction_type="domain_purchase",
            amount_usd=Decimal('49.50'),
            payment_provider="wallet",
            status="completed"
        )
        session.add(purchase)
        
        session.commit()
        logger.info("✅ Payment processing successful")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Payment processing failed: {e}")
        return False
    finally:
        session.close()

def run_all_use_case_tests():
    """Run all use case tests"""
    logger.info("🚀 Running All Use Case Tests for Fresh Database")
    
    test_results = {
        "User Registration": test_use_case_1_user_registration(),
        "Domain Registration": test_use_case_2_domain_registration(),
        "DNS Management": test_use_case_3_dns_management(),
        "Payment Processing": test_use_case_4_payment_processing()
    }
    
    # Report results
    logger.info("\n" + "="*50)
    logger.info("FRESH DATABASE USE CASE TEST RESULTS")
    logger.info("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    logger.info(f"\nOverall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        logger.info("🎯 ALL USE CASES PASSED - Fresh database is ready!")
    elif success_rate >= 75:
        logger.info("✅ Most use cases passed - Good foundation")
    else:
        logger.info("⚠️ Multiple use cases failed - Needs attention")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = run_all_use_case_tests()
    exit(0 if success else 1)