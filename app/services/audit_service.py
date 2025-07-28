"""
Audit Service for Nomadly3 Domain Registration Bot
Comprehensive audit logging and monitoring service
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models.audit_log import AuditLog, SystemEvent, SecurityEvent
from ..core.database import get_db_session

class AuditService:
    """Service for managing audit logs and system monitoring"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session or get_db_session()
    
    def log_user_action(
        self,
        telegram_id: int,
        action_type: str,
        resource_type: str,
        resource_id: str,
        description: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[int] = None
    ) -> AuditLog:
        """Log user action for audit trail"""
        
        audit_entry = AuditLog(
            telegram_id=telegram_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action_description=description,
            old_values=old_values or {},
            new_values=new_values or {},
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )
        
        self.db.add(audit_entry)
        self.db.commit()
        self.db.refresh(audit_entry)
        
        return audit_entry
    
    def log_domain_registration(
        self,
        telegram_id: int,
        domain_name: str,
        registration_data: Dict[str, Any],
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log domain registration attempt"""
        
        return self.log_user_action(
            telegram_id=telegram_id,
            action_type="domain_register",
            resource_type="domain",
            resource_id=domain_name,
            description=f"Domain registration attempt for {domain_name}",
            new_values=registration_data,
            success=success,
            error_message=error_message
        )
    
    def log_payment_transaction(
        self,
        telegram_id: int,
        order_id: str,
        payment_data: Dict[str, Any],
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log payment transaction"""
        
        return self.log_user_action(
            telegram_id=telegram_id,
            action_type="payment_process",
            resource_type="payment",
            resource_id=order_id,
            description=f"Payment transaction for order {order_id}",
            new_values=payment_data,
            success=success,
            error_message=error_message
        )
    
    def log_dns_operation(
        self,
        telegram_id: int,
        domain_name: str,
        operation: str,
        dns_data: Dict[str, Any],
        old_dns_data: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log DNS record operations"""
        
        return self.log_user_action(
            telegram_id=telegram_id,
            action_type=f"dns_{operation}",
            resource_type="dns_record",
            resource_id=domain_name,
            description=f"DNS {operation} operation for {domain_name}",
            old_values=old_dns_data,
            new_values=dns_data,
            success=success,
            error_message=error_message
        )
    
    def log_admin_action(
        self,
        admin_telegram_id: int,
        action_type: str,
        target_resource: str,
        target_id: str,
        description: str,
        changes: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log administrative actions"""
        
        return self.log_user_action(
            telegram_id=admin_telegram_id,
            action_type=f"admin_{action_type}",
            resource_type=target_resource,
            resource_id=target_id,
            description=f"Admin action: {description}",
            new_values=changes or {},
            metadata={"admin_action": True}
        )
    
    def log_system_event(
        self,
        event_type: str,
        event_category: str,
        event_name: str,
        description: str,
        severity: str = "info",
        component: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """Log system-wide events"""
        
        system_event = SystemEvent(
            event_type=event_type,
            event_category=event_category,
            severity=severity,
            event_name=event_name,
            event_description=description,
            component=component,
            event_data=event_data or {},
            performance_metrics=performance_metrics or {}
        )
        
        self.db.add(system_event)
        self.db.commit()
        self.db.refresh(system_event)
        
        return system_event
    
    def log_security_event(
        self,
        telegram_id: Optional[int],
        event_type: str,
        description: str,
        threat_level: str = "low",
        ip_address: Optional[str] = None,
        detection_method: Optional[str] = None,
        action_taken: Optional[str] = None,
        request_details: Optional[Dict[str, Any]] = None
    ) -> SecurityEvent:
        """Log security-related events"""
        
        security_event = SecurityEvent(
            telegram_id=telegram_id,
            event_type=event_type,
            threat_level=threat_level,
            event_description=description,
            detection_method=detection_method,
            ip_address=ip_address,
            action_taken=action_taken,
            request_details=request_details or {}
        )
        
        self.db.add(security_event)
        self.db.commit()
        self.db.refresh(security_event)
        
        return security_event
    
    def get_user_audit_trail(
        self,
        telegram_id: int,
        limit: int = 100,
        action_type: Optional[str] = None
    ) -> List[AuditLog]:
        """Get audit trail for specific user"""
        
        query = self.db.query(AuditLog).filter(AuditLog.telegram_id == telegram_id)
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def get_resource_audit_trail(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """Get audit trail for specific resource"""
        
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_failed_operations(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get failed operations for troubleshooting"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.success == False,
                AuditLog.created_at >= since
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_security_events(
        self,
        threat_level: Optional[str] = None,
        unresolved_only: bool = False,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """Get security events for monitoring"""
        
        query = self.db.query(SecurityEvent)
        
        if threat_level:
            query = query.filter(SecurityEvent.threat_level == threat_level)
        
        if unresolved_only:
            query = query.filter(SecurityEvent.resolved_at.is_(None))
        
        return query.order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean up old audit logs (retention policy)"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Clean audit logs
        audit_deleted = (
            self.db.query(AuditLog)
            .filter(AuditLog.created_at < cutoff_date)
            .delete()
        )
        
        # Clean system events (keep longer for analysis)
        system_deleted = (
            self.db.query(SystemEvent)
            .filter(
                SystemEvent.created_at < cutoff_date,
                SystemEvent.severity.in_(['debug', 'info']),
                SystemEvent.is_resolved == True
            )
            .delete()
        )
        
        self.db.commit()
        
        return {
            'audit_logs_deleted': audit_deleted,
            'system_events_deleted': system_deleted
        }

# Decorator for automatic audit logging
def audit_operation(
    action_type: str,
    resource_type: str,
    description_template: str = "{action_type} operation on {resource_type}"
):
    """Decorator to automatically audit function calls"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            audit_service = AuditService()
            
            # Extract user context (assumes first arg is user context or has telegram_id)
            telegram_id = None
            if args and hasattr(args[0], 'telegram_id'):
                telegram_id = args[0].telegram_id
            elif 'telegram_id' in kwargs:
                telegram_id = kwargs['telegram_id']
            
            resource_id = kwargs.get('resource_id', 'unknown')
            
            try:
                result = func(*args, **kwargs)
                execution_time = int((time.time() - start_time) * 1000)
                
                if telegram_id:
                    audit_service.log_user_action(
                        telegram_id=telegram_id,
                        action_type=action_type,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        description=description_template.format(
                            action_type=action_type,
                            resource_type=resource_type,
                            resource_id=resource_id
                        ),
                        success=True,
                        execution_time_ms=execution_time
                    )
                
                return result
                
            except Exception as e:
                execution_time = int((time.time() - start_time) * 1000)
                
                if telegram_id:
                    audit_service.log_user_action(
                        telegram_id=telegram_id,
                        action_type=action_type,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        description=description_template.format(
                            action_type=action_type,
                            resource_type=resource_type,
                            resource_id=resource_id
                        ),
                        success=False,
                        error_message=str(e),
                        execution_time_ms=execution_time
                    )
                
                raise
        
        return wrapper
    return decorator