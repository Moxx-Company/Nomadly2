#!/usr/bin/env python3
"""
Complete database reset for fresh start with correct technical email
"""

import logging
from database import get_db_manager
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def complete_database_reset():
    """Complete database reset with foreign key handling"""
    try:
        print("🔄 Complete Database Reset")
        print("=" * 50)

        db_manager = get_db_manager()
        session = db_manager.get_session()

        try:
            # Disable foreign key constraints temporarily
            session.execute(text("SET session_replication_role = replica"))

            # Truncate all tables in correct order
            tables = [
                "admin_notifications",
                "email_notifications",
                "api_usage_logs",
                "balance_transactions",
                "wallet_transactions",
                "dns_records",
                "registered_domains",
                "orders",
                "openprovider_contacts",
                "user_states",
                "users",
            ]

            for table in tables:
                try:
                    session.execute(
                        text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                    )
                    print(f"  ✅ Reset {table}")
                except Exception as e:
                    print(f"  ⚠️ {table}: {e}")

            # Re-enable foreign key constraints
            session.execute(text("SET session_replication_role = DEFAULT"))

            session.commit()

            # Verify completely clean state
            print(f"\n🔍 Final Verification:")
            for table in ["users", "registered_domains", "orders"]:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  {table}: {count} records")

            return True

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Reset error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = complete_database_reset()

    print(f"\n{'='*50}")
    if success:
        print("✅ DATABASE COMPLETELY RESET")
        print("🎯 Ready for fresh registration with correct email")
        print("📱 Send /start to bot for clean experience")
    else:
        print("❌ Reset failed")
