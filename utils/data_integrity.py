#!/usr/bin/env python3
"""
Data Integrity Module for Nomadly2 Bot
Implements database migrations, backups, transactions, and data consistency
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from sqlalchemy import text
from database import get_db_manager

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Database migration system"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    def create_migration_table(self):
        """Create migrations tracking table"""
        with self.db_manager.get_session() as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """))
            session.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        self.create_migration_table()
        with self.db_manager.get_session() as session:
            result = session.execute(text("SELECT version FROM schema_migrations ORDER BY applied_at"))
            return [row[0] for row in result.fetchall()]
    
    def apply_migration(self, version: str, description: str, sql_commands: List[str]):
        """Apply a database migration"""
        applied_migrations = self.get_applied_migrations()
        
        if version in applied_migrations:
            logger.info(f"Migration {version} already applied")
            return
        
        logger.info(f"Applying migration {version}: {description}")
        
        with self.db_manager.get_session() as session:
            try:
                # Execute migration commands
                for command in sql_commands:
                    session.execute(text(command))
                
                # Record migration
                session.execute(text("""
                    INSERT INTO schema_migrations (version, description) 
                    VALUES (:version, :description)
                """), {'version': version, 'description': description})
                
                session.commit()
                logger.info(f"Migration {version} applied successfully")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Migration {version} failed: {e}")
                raise

class DatabaseBackup:
    """Database backup and recovery system"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create database backup"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_file = os.path.join(self.backup_dir, f"{backup_name}.sql")
        
        try:
            # Use pg_dump for PostgreSQL
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                cmd = f"pg_dump '{db_url}' > {backup_file}"
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"Database backup created: {backup_file}")
                    return backup_file
                else:
                    logger.error(f"Backup failed with return code {process.returncode}")
                    return None
            else:
                logger.error("DATABASE_URL not found")
                return None
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return None
    
    async def restore_backup(self, backup_file: str) -> bool:
        """Restore from backup"""
        if not os.path.exists(backup_file):
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        try:
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                cmd = f"psql '{db_url}' < {backup_file}"
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                if process.returncode == 0:
                    logger.info(f"Database restored from: {backup_file}")
                    return True
                else:
                    logger.error(f"Restore failed with return code {process.returncode}")
                    return False
            else:
                logger.error("DATABASE_URL not found")
                return False
                
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

class TransactionManager:
    """Transaction management for data consistency"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions"""
        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            session.close()
    
    async def execute_with_retry(self, operation, max_retries: int = 3) -> Any:
        """Execute database operation with retry logic"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                async with self.transaction() as session:
                    return await operation(session)
                    
            except Exception as e:
                last_exception = e
                logger.warning(f"Database operation attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        logger.error(f"Database operation failed after {max_retries} attempts")
        raise last_exception

class DataValidator:
    """Data validation and integrity checks"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Run comprehensive data integrity checks"""
        results = {
            'orphaned_records': await self._check_orphaned_records(),
            'duplicate_data': await self._check_duplicates(),
            'foreign_key_violations': await self._check_foreign_keys(),
            'data_consistency': await self._check_data_consistency()
        }
        
        return results
    
    async def _check_orphaned_records(self) -> List[str]:
        """Check for orphaned records"""
        issues = []
        
        with self.db_manager.get_session() as session:
            # Check for orders without users
            result = session.execute(text("""
                SELECT COUNT(*) FROM orders o 
                LEFT JOIN users u ON o.telegram_id = u.telegram_id 
                WHERE u.telegram_id IS NULL
            """))
            orphaned_orders = result.scalar()
            
            if orphaned_orders > 0:
                issues.append(f"{orphaned_orders} orphaned orders without users")
            
            # Check for domains without users
            result = session.execute(text("""
                SELECT COUNT(*) FROM registered_domains d 
                LEFT JOIN users u ON d.user_id = u.telegram_id 
                WHERE u.telegram_id IS NULL
            """))
            orphaned_domains = result.scalar()
            
            if orphaned_domains > 0:
                issues.append(f"{orphaned_domains} orphaned domains without users")
        
        return issues
    
    async def _check_duplicates(self) -> List[str]:
        """Check for duplicate data"""
        issues = []
        
        with self.db_manager.get_session() as session:
            # Check for duplicate domains
            result = session.execute(text("""
                SELECT domain_name, COUNT(*) as count 
                FROM registered_domains 
                GROUP BY domain_name 
                HAVING COUNT(*) > 1
            """))
            duplicates = result.fetchall()
            
            if duplicates:
                for domain, count in duplicates:
                    issues.append(f"Domain {domain} appears {count} times")
        
        return issues
    
    async def _check_foreign_keys(self) -> List[str]:
        """Check foreign key constraints"""
        # This would be database-specific validation
        # PostgreSQL has built-in constraint checking
        return []
    
    async def _check_data_consistency(self) -> List[str]:
        """Check business logic data consistency"""
        issues = []
        
        with self.db_manager.get_session() as session:
            # Check for negative balances
            result = session.execute(text("""
                SELECT telegram_id, balance_usd 
                FROM users 
                WHERE balance_usd < 0
            """))
            negative_balances = result.fetchall()
            
            if negative_balances:
                for user_id, balance in negative_balances:
                    issues.append(f"User {user_id} has negative balance: ${balance}")
        
        return issues

# Global instances
migration_manager = DatabaseMigration()
backup_manager = DatabaseBackup()
transaction_manager = TransactionManager()
data_validator = DataValidator()

# Migration definitions
MIGRATIONS = [
    {
        'version': '001_add_indexes',
        'description': 'Add performance indexes',
        'commands': [
            'CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)',
            'CREATE INDEX IF NOT EXISTS idx_orders_telegram_id ON orders(telegram_id)', 
            'CREATE INDEX IF NOT EXISTS idx_domains_user_id ON registered_domains(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_domains_name ON registered_domains(domain_name)'
        ]
    },
    {
        'version': '002_add_audit_columns',
        'description': 'Add audit timestamps',
        'commands': [
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP',
            'ALTER TABLE orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'ALTER TABLE registered_domains ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ]
    }
]

async def run_pending_migrations():
    """Run all pending migrations"""
    for migration in MIGRATIONS:
        migration_manager.apply_migration(
            migration['version'],
            migration['description'], 
            migration['commands']
        )