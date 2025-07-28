"""
Database Migration Manager for Nomadly2
Handles versioned database schema migrations with rollback support
"""

import os
import logging
import psycopg2
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database schema migrations with version control"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent.parent / "database_migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)
    
    def ensure_migration_table(self):
        """Ensure migration history table exists"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS migration_history (
                        id SERIAL PRIMARY KEY,
                        migration_name VARCHAR(255) UNIQUE NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        rollback_sql TEXT
                    )
                """)
                conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations"""
        self.ensure_migration_table()
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT migration_name FROM migration_history 
                    ORDER BY applied_at
                """)
                return [row[0] for row in cur.fetchall()]
    
    def get_pending_migrations(self) -> List[Path]:
        """Get list of pending migrations to apply"""
        applied = set(self.get_applied_migrations())
        all_migrations = sorted([
            f for f in self.migrations_dir.glob("*.sql")
            if f.is_file()
        ])
        
        return [m for m in all_migrations if m.stem not in applied]
    
    def apply_migration(self, migration_file: Path) -> bool:
        """Apply a single migration file"""
        try:
            logger.info(f"Applying migration: {migration_file.name}")
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Extract rollback SQL if present (between -- ROLLBACK and -- END ROLLBACK)
            rollback_sql = self._extract_rollback_sql(migration_sql)
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Apply migration
                    cur.execute(migration_sql)
                    
                    # Record in migration history
                    cur.execute("""
                        INSERT INTO migration_history (migration_name, rollback_sql)
                        VALUES (%s, %s)
                        ON CONFLICT (migration_name) DO NOTHING
                    """, (migration_file.stem, rollback_sql))
                    
                    conn.commit()
                    
            logger.info(f"✅ Migration applied successfully: {migration_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration_file.name}: {e}")
            return False
    
    def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a specific migration"""
        try:
            logger.info(f"Rolling back migration: {migration_name}")
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get rollback SQL
                    cur.execute("""
                        SELECT rollback_sql FROM migration_history 
                        WHERE migration_name = %s
                    """, (migration_name,))
                    
                    result = cur.fetchone()
                    if not result or not result[0]:
                        logger.error(f"No rollback SQL found for {migration_name}")
                        return False
                    
                    rollback_sql = result[0]
                    
                    # Execute rollback
                    cur.execute(rollback_sql)
                    
                    # Remove from migration history
                    cur.execute("""
                        DELETE FROM migration_history 
                        WHERE migration_name = %s
                    """, (migration_name,))
                    
                    conn.commit()
                    
            logger.info(f"✅ Migration rolled back successfully: {migration_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback migration {migration_name}: {e}")
            return False
    
    def migrate(self) -> bool:
        """Apply all pending migrations"""
        logger.info("🔄 Checking for pending database migrations...")
        
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ No pending migrations to apply")
            return True
        
        logger.info(f"📋 Found {len(pending)} pending migrations")
        
        success_count = 0
        for migration in pending:
            if self.apply_migration(migration):
                success_count += 1
            else:
                logger.error(f"💥 Migration failed, stopping at: {migration.name}")
                break
        
        if success_count == len(pending):
            logger.info(f"✅ All {success_count} migrations applied successfully")
            return True
        else:
            logger.error(f"❌ Applied {success_count}/{len(pending)} migrations")
            return False
    
    def get_migration_status(self) -> Dict:
        """Get current migration status"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied_migrations": applied,
            "pending_migrations": [p.stem for p in pending],
            "last_migration": applied[-1] if applied else None,
            "status": "up_to_date" if not pending else "pending_migrations"
        }
    
    def create_migration_template(self, name: str) -> Path:
        """Create a new migration template file"""
        # Generate migration number based on existing files
        existing_numbers = []
        for f in self.migrations_dir.glob("*.sql"):
            try:
                number = int(f.stem.split('_')[0])
                existing_numbers.append(number)
            except (ValueError, IndexError):
                continue
        
        next_number = max(existing_numbers, default=0) + 1
        
        # Create migration filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{next_number:03d}_{name}_{timestamp}.sql"
        migration_file = self.migrations_dir / filename
        
        # Create template content
        template = f"""-- Database Migration {next_number:03d}: {name.replace('_', ' ').title()}
-- Created: {datetime.now().strftime('%Y-%m-%d')}
-- Description: [Add description here]

BEGIN;

-- Your migration SQL here
-- Example:
-- ALTER TABLE users ADD COLUMN new_field VARCHAR(255);
-- CREATE INDEX idx_users_new_field ON users(new_field);

COMMIT;

-- ROLLBACK
-- BEGIN;
-- Your rollback SQL here
-- Example:
-- ALTER TABLE users DROP COLUMN new_field;
-- END ROLLBACK
"""
        
        with open(migration_file, 'w') as f:
            f.write(template)
        
        logger.info(f"✅ Created migration template: {filename}")
        return migration_file
    
    def _extract_rollback_sql(self, migration_sql: str) -> Optional[str]:
        """Extract rollback SQL from migration file"""
        try:
            lines = migration_sql.split('\n')
            rollback_lines = []
            in_rollback = False
            
            for line in lines:
                if '-- ROLLBACK' in line:
                    in_rollback = True
                    continue
                elif '-- END ROLLBACK' in line:
                    break
                elif in_rollback and not line.strip().startswith('--'):
                    rollback_lines.append(line)
            
            return '\n'.join(rollback_lines).strip() if rollback_lines else None
            
        except Exception:
            return None

def get_migration_manager():
    """Get configured migration manager instance"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    return MigrationManager(database_url)