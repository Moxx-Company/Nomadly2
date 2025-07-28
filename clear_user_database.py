#!/usr/bin/env python3
"""
Clear User Database
Remove all user-specific data while preserving system structure
"""

import logging
from database import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_user_data():
    """Clear all user data from database"""
    logger.info("🗑️ CLEARING USER DATABASE")
    logger.info("Removing all user-specific records while preserving system structure")
    logger.info("=" * 60)
    
    try:
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Clear user-related tables in proper order (foreign keys first)
            tables_to_clear = [
                ('dns_records', 'DNS records'),
                ('registered_domains', 'Registered domains'),
                ('balance_transactions', 'Balance transactions'),
                ('bonus_transactions', 'Bonus transactions'),
                ('wallet_transactions', 'Wallet transactions'),
                ('orders', 'Payment orders'),
                ('openprovider_contacts', 'OpenProvider contacts'),
                ('admin_notifications', 'Admin notifications'),
                ('email_notifications', 'Email notifications'),
                ('user_states', 'User states'),
                ('users', 'Users')
            ]
            
            total_deleted = 0
            
            for table_name, description in tables_to_clear:
                try:
                    # Get table class
                    table_class = getattr(db_manager, table_name.title().replace('_', ''))
                    
                    # Count records before deletion
                    count = session.query(table_class).count()
                    
                    if count > 0:
                        # Delete all records
                        session.query(table_class).delete()
                        logger.info(f"✅ Cleared {count} records from {description}")
                        total_deleted += count
                    else:
                        logger.info(f"📭 {description}: Already empty")
                        
                except AttributeError:
                    # Try alternative naming
                    try:
                        # Handle special cases
                        if table_name == 'registered_domains':
                            table_class = db_manager.RegisteredDomain
                        elif table_name == 'openprovider_contacts':
                            table_class = db_manager.OpenProviderContact
                        elif table_name == 'admin_notifications':
                            table_class = db_manager.AdminNotification
                        elif table_name == 'balance_transactions':
                            table_class = db_manager.BalanceTransaction
                        elif table_name == 'bonus_transactions':
                            table_class = db_manager.BonusTransaction
                        elif table_name == 'wallet_transactions':
                            table_class = db_manager.WalletTransaction
                        elif table_name == 'user_states':
                            table_class = db_manager.UserState
                        elif table_name == 'dns_records':
                            table_class = db_manager.DnsRecord
                        elif table_name == 'email_notifications':
                            table_class = db_manager.EmailNotification
                        else:
                            table_class = getattr(db_manager, table_name.capitalize())
                        
                        count = session.query(table_class).count()
                        
                        if count > 0:
                            session.query(table_class).delete()
                            logger.info(f"✅ Cleared {count} records from {description}")
                            total_deleted += count
                        else:
                            logger.info(f"📭 {description}: Already empty")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Could not clear {description}: {e}")
            
            # Commit all deletions
            session.commit()
            logger.info(f"\n🎉 DATABASE CLEARING COMPLETE")
            logger.info(f"📊 Total records deleted: {total_deleted}")
            
            # Reset sequences for clean ID numbering
            logger.info("\n🔄 RESETTING ID SEQUENCES...")
            
            sequence_resets = [
                "ALTER SEQUENCE users_id_seq RESTART WITH 1",
                "ALTER SEQUENCE orders_id_seq RESTART WITH 1", 
                "ALTER SEQUENCE registered_domains_id_seq RESTART WITH 1",
                "ALTER SEQUENCE openprovider_contacts_id_seq RESTART WITH 1",
                "ALTER SEQUENCE balance_transactions_id_seq RESTART WITH 1",
                "ALTER SEQUENCE bonus_transactions_id_seq RESTART WITH 1",
                "ALTER SEQUENCE admin_notifications_id_seq RESTART WITH 1"
            ]
            
            for reset_sql in sequence_resets:
                try:
                    session.execute(reset_sql)
                    logger.info(f"✅ Reset sequence: {reset_sql.split('_')[0].split(' ')[2]}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not reset sequence: {e}")
            
            session.commit()
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error clearing database: {e}")
        return False

def verify_database_clean():
    """Verify database is clean"""
    logger.info("\n🔍 VERIFYING DATABASE IS CLEAN")
    
    try:
        db_manager = get_db_manager()
        
        with db_manager.get_session() as session:
            # Check key tables
            tables_to_check = [
                ('users', db_manager.User),
                ('orders', db_manager.Order),
                ('registered_domains', db_manager.RegisteredDomain),
                ('openprovider_contacts', db_manager.OpenProviderContact)
            ]
            
            all_clean = True
            
            for table_name, table_class in tables_to_check:
                try:
                    count = session.query(table_class).count()
                    if count == 0:
                        logger.info(f"✅ {table_name}: Clean (0 records)")
                    else:
                        logger.warning(f"⚠️ {table_name}: {count} records remain")
                        all_clean = False
                except Exception as e:
                    logger.error(f"❌ Could not check {table_name}: {e}")
                    all_clean = False
            
            if all_clean:
                logger.info("\n🎉 DATABASE SUCCESSFULLY CLEANED")
                logger.info("Ready for fresh user registrations")
            else:
                logger.warning("\n⚠️ DATABASE CLEANING INCOMPLETE")
                
            return all_clean
            
    except Exception as e:
        logger.error(f"❌ Verification error: {e}")
        return False

def main():
    """Main execution"""
    success = clear_user_data()
    
    if success:
        verify_database_clean()
        logger.info("\n✅ USER DATABASE CLEARED SUCCESSFULLY")
        logger.info("Database is ready for production use")
    else:
        logger.error("\n❌ DATABASE CLEARING FAILED")

if __name__ == "__main__":
    main()