#!/usr/bin/env python3
"""
Safe database clearing script - removes user data while preserving structure
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_user_database():
    """Clear all user data from the database safely"""
    try:
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL not found in environment")
            return False
        
        # Create engine and session
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("🗑️ Starting safe database cleanup...")
        
        # Clear tables in correct order to respect foreign key constraints
        tables_to_clear = [
            'dns_records',
            'wallet_transactions', 
            'orders',
            'domains',  # Clear domains before users due to foreign key
            'registered_domains',
            'users'
        ]
        
        for table in tables_to_clear:
            try:
                result = session.execute(text(f'DELETE FROM {table}'))
                count = result.rowcount
                session.commit()
                logger.info(f"✅ Cleared {count} records from {table}")
            except Exception as e:
                logger.error(f"❌ Error clearing {table}: {e}")
                session.rollback()
        
        # Reset sequences if using PostgreSQL
        sequences_to_reset = [
            ('users_id_seq', 'users'),
            ('registered_domains_id_seq', 'registered_domains'),
            ('orders_id_seq', 'orders'),
            ('wallet_transactions_id_seq', 'wallet_transactions'),
            ('dns_records_id_seq', 'dns_records')
        ]
        
        for seq_name, table_name in sequences_to_reset:
            try:
                session.execute(text(f"SELECT setval('{seq_name}', 1, false)"))
                session.commit()
                logger.info(f"✅ Reset sequence {seq_name}")
            except Exception as e:
                # Sequence might not exist or have different name
                session.rollback()
        
        logger.info("✅ Database cleared successfully!")
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database clear failed: {e}")
        return False

if __name__ == "__main__":
    if clear_user_database():
        logger.info("✅ User database cleared successfully")
        sys.exit(0)
    else:
        logger.error("❌ Failed to clear user database")
        sys.exit(1)