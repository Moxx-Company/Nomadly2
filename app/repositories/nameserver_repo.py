"""
Nameserver Repository - Data Access Layer for Nameserver Operations
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NameserverRepository:
    """Repository for nameserver operation data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_nameserver_operation(self, operation_data: Dict[str, Any]) -> bool:
        """Create a new nameserver operation record"""
        try:
            from database import NameserverOperation
            
            operation = NameserverOperation(
                domain_id=operation_data['domain_id'],
                telegram_id=operation_data['telegram_id'],
                operation_type=operation_data['operation_type'],
                old_nameservers=operation_data.get('old_nameservers', []),
                new_nameservers=operation_data.get('new_nameservers', []),
                preset_used=operation_data.get('preset_used'),
                status=operation_data.get('status', 'pending'),
                created_at=datetime.now()
            )
            
            self.db.add(operation)
            self.db.commit()
            
            logger.info(f"Created nameserver operation: {operation.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating nameserver operation: {e}")
            self.db.rollback()
            return False
    
    def update_operation_status(self, operation_id: int, status: str, 
                              error_message: Optional[str] = None) -> bool:
        """Update nameserver operation status"""
        try:
            from database import NameserverOperation
            
            operation = self.db.query(NameserverOperation).filter(
                NameserverOperation.id == operation_id
            ).first()
            
            if not operation:
                return False
            
            operation.status = status
            if error_message:
                operation.error_message = error_message
            operation.updated_at = datetime.now()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating operation status: {e}")
            self.db.rollback()
            return False
    
    def get_domain_nameserver_history(self, domain_id: int) -> List[Dict[str, Any]]:
        """Get nameserver change history for a domain"""
        try:
            from database import NameserverOperation
            
            operations = self.db.query(NameserverOperation).filter(
                NameserverOperation.domain_id == domain_id
            ).order_by(desc(NameserverOperation.created_at)).all()
            
            return [self._operation_to_dict(op) for op in operations]
            
        except Exception as e:
            logger.error(f"Error getting nameserver history: {e}")
            return []
    
    def get_user_nameserver_operations(self, telegram_id: int, 
                                     limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's nameserver operations"""
        try:
            from database import NameserverOperation
            
            operations = self.db.query(NameserverOperation).filter(
                NameserverOperation.telegram_id == telegram_id
            ).order_by(desc(NameserverOperation.created_at)).limit(limit).all()
            
            return [self._operation_to_dict(op) for op in operations]
            
        except Exception as e:
            logger.error(f"Error getting user operations: {e}")
            return []
    
    def get_pending_operations(self) -> List[Dict[str, Any]]:
        """Get pending nameserver operations"""
        try:
            from database import NameserverOperation
            
            operations = self.db.query(NameserverOperation).filter(
                NameserverOperation.status == 'pending'
            ).all()
            
            return [self._operation_to_dict(op) for op in operations]
            
        except Exception as e:
            logger.error(f"Error getting pending operations: {e}")
            return []
    
    def get_operation_statistics(self) -> Dict[str, Any]:
        """Get nameserver operation statistics"""
        try:
            from database import NameserverOperation
            from sqlalchemy import func
            
            # Total operations
            total_ops = self.db.query(NameserverOperation).count()
            
            # Status breakdown
            status_stats = self.db.query(
                NameserverOperation.status,
                func.count(NameserverOperation.id).label('count')
            ).group_by(NameserverOperation.status).all()
            
            # Operations by type
            type_stats = self.db.query(
                NameserverOperation.operation_type,
                func.count(NameserverOperation.id).label('count')
            ).group_by(NameserverOperation.operation_type).all()
            
            # Preset usage
            preset_stats = self.db.query(
                NameserverOperation.preset_used,
                func.count(NameserverOperation.id).label('count')
            ).filter(
                NameserverOperation.preset_used.isnot(None)
            ).group_by(NameserverOperation.preset_used).all()
            
            return {
                'total_operations': total_ops,
                'status_breakdown': {status: count for status, count in status_stats},
                'operation_types': {op_type: count for op_type, count in type_stats},
                'preset_usage': {preset: count for preset, count in preset_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting operation statistics: {e}")
            return {}
    
    def _operation_to_dict(self, operation) -> Dict[str, Any]:
        """Convert nameserver operation model to dictionary"""
        return {
            'id': operation.id,
            'domain_id': operation.domain_id,
            'telegram_id': operation.telegram_id,
            'operation_type': operation.operation_type,
            'old_nameservers': operation.old_nameservers or [],
            'new_nameservers': operation.new_nameservers or [],
            'preset_used': operation.preset_used,
            'status': operation.status,
            'error_message': operation.error_message,
            'created_at': operation.created_at.isoformat() if operation.created_at else None,
            'updated_at': getattr(operation, 'updated_at', None)
        }