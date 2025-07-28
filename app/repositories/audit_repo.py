"""
Audit Repository - Data Access Layer for Audit Operations
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AuditRepository:
    """Repository for audit log data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_audit_log(self, audit_data: Dict[str, Any]) -> bool:
        """Create a new audit log entry"""
        try:
            from database import AuditLog
            
            audit_log = AuditLog(
                telegram_id=audit_data.get('telegram_id'),
                action=audit_data['action'],
                resource_type=audit_data.get('resource_type'),
                resource_id=audit_data.get('resource_id'),
                details=audit_data.get('details', {}),
                ip_address=audit_data.get('ip_address'),
                user_agent=audit_data.get('user_agent'),
                created_at=datetime.now()
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
            logger.debug(f"Created audit log: {audit_data['action']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            self.db.rollback()
            return False
    
    def get_audit_logs(self, telegram_id: Optional[int] = None, 
                      action: Optional[str] = None,
                      resource_type: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get audit logs with optional filters"""
        try:
            from database import AuditLog
            
            query = self.db.query(AuditLog)
            
            # Apply filters
            if telegram_id:
                query = query.filter(AuditLog.telegram_id == telegram_id)
            if action:
                query = query.filter(AuditLog.action == action)
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            # Order by newest first
            logs = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset).all()
            
            return [self._audit_log_to_dict(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    def get_user_activity(self, telegram_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get user activity for specified days"""
        try:
            from database import AuditLog
            
            start_date = datetime.now() - timedelta(days=days)
            
            logs = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.telegram_id == telegram_id,
                    AuditLog.created_at >= start_date
                )
            ).order_by(desc(AuditLog.created_at)).all()
            
            return [self._audit_log_to_dict(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []
    
    def get_system_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get system-wide activity for specified hours"""
        try:
            from database import AuditLog
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            logs = self.db.query(AuditLog).filter(
                AuditLog.created_at >= start_time
            ).order_by(desc(AuditLog.created_at)).limit(1000).all()
            
            return [self._audit_log_to_dict(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Error getting system activity: {e}")
            return []
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit statistics"""
        try:
            from database import AuditLog
            from sqlalchemy import func
            
            # Total logs
            total_logs = self.db.query(AuditLog).count()
            
            # Logs by action
            action_stats = self.db.query(
                AuditLog.action,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.action).all()
            
            # Recent activity (last 24 hours)
            last_24h = datetime.now() - timedelta(hours=24)
            recent_logs = self.db.query(AuditLog).filter(
                AuditLog.created_at >= last_24h
            ).count()
            
            # Most active users (last 7 days)
            last_7d = datetime.now() - timedelta(days=7)
            active_users = self.db.query(
                AuditLog.telegram_id,
                func.count(AuditLog.id).label('activity_count')
            ).filter(
                and_(
                    AuditLog.created_at >= last_7d,
                    AuditLog.telegram_id.isnot(None)
                )
            ).group_by(AuditLog.telegram_id).order_by(
                desc('activity_count')
            ).limit(10).all()
            
            return {
                'total_logs': total_logs,
                'recent_logs_24h': recent_logs,
                'actions': {action: count for action, count in action_stats},
                'most_active_users': [
                    {'telegram_id': uid, 'activity_count': count}
                    for uid, count in active_users
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting audit statistics: {e}")
            return {}
    
    def cleanup_old_logs(self, days_old: int = 90) -> int:
        """Clean up old audit logs"""
        try:
            from database import AuditLog
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            deleted_count = self.db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            self.db.rollback()
            return 0
    
    def search_logs(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search audit logs by action or details"""
        try:
            from database import AuditLog
            
            # Search in action and details (assuming details is JSON)
            from sqlalchemy import or_
            
            logs = self.db.query(AuditLog).filter(
                or_(
                    AuditLog.action.ilike(f'%{search_term}%'),
                    AuditLog.details.op('->>')('message').ilike(f'%{search_term}%')
                )
            ).order_by(desc(AuditLog.created_at)).limit(limit).all()
            
            return [self._audit_log_to_dict(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []
    
    def _audit_log_to_dict(self, audit_log) -> Dict[str, Any]:
        """Convert audit log model to dictionary"""
        return {
            'id': audit_log.id,
            'telegram_id': audit_log.telegram_id,
            'action': audit_log.action,
            'resource_type': audit_log.resource_type,
            'resource_id': audit_log.resource_id,
            'details': audit_log.details or {},
            'ip_address': audit_log.ip_address,
            'user_agent': audit_log.user_agent,
            'created_at': audit_log.created_at.isoformat() if audit_log.created_at else None
        }