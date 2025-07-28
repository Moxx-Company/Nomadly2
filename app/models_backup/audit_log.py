"""
Audit Log Model for Nomadly3 Domain Registration Bot
Comprehensive audit trail for all system operations
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, BIGINT, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuditLog(Base):
    """Comprehensive audit trail for all system operations"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    
    # User and session information
    telegram_id = Column(BIGINT, index=True)  # Nullable for system operations
    username = Column(String(100))
    
    # Operation details
    action_type = Column(String(100), nullable=False, index=True)  # domain_register, payment_process, dns_create, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # domain, user, payment, dns_record
    resource_id = Column(String(100), index=True)  # domain_name, order_id, record_id, etc.
    
    # Action description and context
    action_description = Column(Text, nullable=False)
    old_values = Column(JSONB)  # Previous state before change
    new_values = Column(JSONB)  # New state after change
    
    # Technical details
    ip_address = Column(String(45))  # IPv4/IPv6 support
    user_agent = Column(Text)
    api_endpoint = Column(String(255))
    http_method = Column(String(10))
    
    # Result and metadata
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)  # Performance tracking
    metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_audit_user_action', 'telegram_id', 'action_type'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_timestamp', 'created_at'),
        Index('idx_audit_action_success', 'action_type', 'success'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.telegram_id}, action={self.action_type}, resource={self.resource_type}:{self.resource_id})>"

class SystemEvent(Base):
    """System-wide events and operational monitoring"""
    
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True)
    
    # Event classification
    event_type = Column(String(100), nullable=False, index=True)  # startup, shutdown, error, maintenance
    event_category = Column(String(50), nullable=False, index=True)  # system, security, performance, business
    severity = Column(String(20), nullable=False, default='info', index=True)  # debug, info, warning, error, critical
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text)
    event_data = Column(JSONB, default={})
    
    # Source information
    component = Column(String(100))  # bot, api, payment_processor, dns_manager
    source_file = Column(String(255))
    source_function = Column(String(100))
    
    # Metrics and monitoring
    performance_metrics = Column(JSONB)  # response_time, memory_usage, cpu_usage
    affected_users_count = Column(Integer, default=0)
    
    # Resolution tracking
    is_resolved = Column(Boolean, default=True)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Indexes for monitoring and alerting
    __table_args__ = (
        Index('idx_system_event_type_severity', 'event_type', 'severity'),
        Index('idx_system_event_unresolved', 'is_resolved', 'severity'),
        Index('idx_system_event_component', 'component', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SystemEvent(id={self.id}, type={self.event_type}, severity={self.severity}, component={self.component})>"

class SecurityEvent(Base):
    """Security-specific events and threat monitoring"""
    
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True)
    
    # User and session
    telegram_id = Column(BIGINT, index=True)
    username = Column(String(100))
    
    # Security event details
    event_type = Column(String(100), nullable=False, index=True)  # login_attempt, admin_access, suspicious_activity
    threat_level = Column(String(20), nullable=False, default='low', index=True)  # low, medium, high, critical
    
    # Event description
    event_description = Column(Text, nullable=False)
    detection_method = Column(String(100))  # rate_limiting, pattern_matching, manual_review
    
    # Technical details
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    request_details = Column(JSONB)
    
    # Geographic and network info
    country_code = Column(String(2))
    isp = Column(String(255))
    is_vpn = Column(Boolean)
    is_tor = Column(Boolean)
    
    # Response and mitigation
    action_taken = Column(String(100))  # blocked, logged, alerted, manual_review
    is_blocked = Column(Boolean, default=False)
    alert_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime)
    
    # Indexes for security monitoring
    __table_args__ = (
        Index('idx_security_user_threat', 'telegram_id', 'threat_level'),
        Index('idx_security_ip_timestamp', 'ip_address', 'created_at'),
        Index('idx_security_unresolved', 'threat_level', 'resolved_at'),
    )
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, user={self.telegram_id}, type={self.event_type}, threat={self.threat_level})>"