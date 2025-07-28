"""
Email Repository - Data Access Layer for Email Operations
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EmailRepository:
    """Repository for email notification data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_email_log(self, email_data: Dict[str, Any]) -> bool:
        """Create a new email log entry"""
        try:
            from database import EmailNotification
            
            email_log = EmailNotification(
                telegram_id=email_data.get('telegram_id'),
                email_address=email_data['email_address'],
                subject=email_data['subject'],
                template_name=email_data.get('template_name'),
                status=email_data.get('status', 'sent'),
                provider=email_data.get('provider', 'brevo'),
                external_id=email_data.get('external_id'),
                error_message=email_data.get('error_message'),
                created_at=datetime.now()
            )
            
            self.db.add(email_log)
            self.db.commit()
            
            logger.info(f"Created email log: {email_data['subject']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating email log: {e}")
            self.db.rollback()
            return False
    
    def get_email_logs(self, telegram_id: Optional[int] = None,
                      status: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get email logs with optional filters"""
        try:
            from database import EmailNotification
            
            query = self.db.query(EmailNotification)
            
            if telegram_id:
                query = query.filter(EmailNotification.telegram_id == telegram_id)
            if status:
                query = query.filter(EmailNotification.status == status)
            
            logs = query.order_by(desc(EmailNotification.created_at)).limit(limit).offset(offset).all()
            
            return [self._email_log_to_dict(log) for log in logs]
            
        except Exception as e:
            logger.error(f"Error getting email logs: {e}")
            return []
    
    def get_failed_emails(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed email deliveries"""
        try:
            from database import EmailNotification
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            failed_emails = self.db.query(EmailNotification).filter(
                and_(
                    EmailNotification.status == 'failed',
                    EmailNotification.created_at >= start_time
                )
            ).order_by(desc(EmailNotification.created_at)).all()
            
            return [self._email_log_to_dict(log) for log in failed_emails]
            
        except Exception as e:
            logger.error(f"Error getting failed emails: {e}")
            return []
    
    def get_email_statistics(self) -> Dict[str, Any]:
        """Get email delivery statistics"""
        try:
            from database import EmailNotification
            from sqlalchemy import func
            
            # Total emails
            total_emails = self.db.query(EmailNotification).count()
            
            # Status breakdown
            status_stats = self.db.query(
                EmailNotification.status,
                func.count(EmailNotification.id).label('count')
            ).group_by(EmailNotification.status).all()
            
            # Recent activity (last 24 hours)
            last_24h = datetime.now() - timedelta(hours=24)
            recent_emails = self.db.query(EmailNotification).filter(
                EmailNotification.created_at >= last_24h
            ).count()
            
            # Template usage
            template_stats = self.db.query(
                EmailNotification.template_name,
                func.count(EmailNotification.id).label('count')
            ).filter(
                EmailNotification.template_name.isnot(None)
            ).group_by(EmailNotification.template_name).all()
            
            return {
                'total_emails': total_emails,
                'recent_emails_24h': recent_emails,
                'status_breakdown': {status: count for status, count in status_stats},
                'template_usage': {template: count for template, count in template_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting email statistics: {e}")
            return {}
    
    def update_email_status(self, email_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """Update email delivery status"""
        try:
            from database import EmailNotification
            
            email_log = self.db.query(EmailNotification).filter(
                EmailNotification.id == email_id
            ).first()
            
            if not email_log:
                return False
            
            email_log.status = status
            if error_message:
                email_log.error_message = error_message
            email_log.updated_at = datetime.now()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating email status: {e}")
            self.db.rollback()
            return False
    
    def cleanup_old_logs(self, days_old: int = 30) -> int:
        """Clean up old email logs"""
        try:
            from database import EmailNotification
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            deleted_count = self.db.query(EmailNotification).filter(
                EmailNotification.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old email logs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old email logs: {e}")
            self.db.rollback()
            return 0
    
    def _email_log_to_dict(self, email_log) -> Dict[str, Any]:
        """Convert email log model to dictionary"""
        return {
            'id': email_log.id,
            'telegram_id': email_log.telegram_id,
            'email_address': email_log.email_address,
            'subject': email_log.subject,
            'template_name': email_log.template_name,
            'status': email_log.status,
            'provider': email_log.provider,
            'external_id': email_log.external_id,
            'error_message': email_log.error_message,
            'created_at': email_log.created_at.isoformat() if email_log.created_at else None,
            'updated_at': getattr(email_log, 'updated_at', None)
        }