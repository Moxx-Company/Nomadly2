"""
External Integration Models for Nomadly3
Database models to support all external service integrations
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any

from .base import Base

class CloudflareIntegration(Base):
    """
    Database model for Cloudflare DNS integration tracking
    Stores zone information, API credentials status, and DNS operation logs
    """
    __tablename__ = "cloudflare_integrations"
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("registered_domains.id"), nullable=False)
    zone_id = Column(String(255), nullable=False, unique=True)
    zone_name = Column(String(255), nullable=False)
    nameservers = Column(JSON, nullable=True)  # ['ns1.cloudflare.com', 'ns2.cloudflare.com']
    plan_type = Column(String(50), default="free")  # free, pro, business, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="active")  # active, error, suspended
    api_errors = Column(Text, nullable=True)
    
    # Relationships
    domain = relationship("RegisteredDomain", back_populates="cloudflare_integration")
    dns_operations = relationship("DNSOperation", back_populates="cloudflare_integration")

class OpenProviderIntegration(Base):
    """
    Database model for OpenProvider domain registration integration
    Stores domain registration details, contact handles, and API operation tracking
    """
    __tablename__ = "openprovider_integrations"
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("registered_domains.id"), nullable=False)
    openprovider_domain_id = Column(String(255), nullable=False, unique=True)
    contact_handle = Column(String(255), nullable=False)
    registrant_contact = Column(JSON, nullable=True)  # Contact details
    admin_contact = Column(JSON, nullable=True)
    tech_contact = Column(JSON, nullable=True)
    billing_contact = Column(JSON, nullable=True)
    nameservers = Column(JSON, nullable=True)
    registration_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True)
    transfer_lock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="active")  # active, error, expired
    api_errors = Column(Text, nullable=True)
    
    # Relationships
    domain = relationship("RegisteredDomain", back_populates="openprovider_integration")
    nameserver_operations = relationship("NameserverOperation", back_populates="openprovider_integration")

class FastForexIntegration(Base):
    """
    Database model for FastForex currency conversion tracking
    Stores exchange rates, conversion history, and API usage
    """
    __tablename__ = "fastforex_integrations"
    
    id = Column(Integer, primary_key=True)
    from_currency = Column(String(10), nullable=False)  # USD
    to_currency = Column(String(10), nullable=False)    # BTC, ETH, LTC, DOGE
    exchange_rate = Column(DECIMAL(20, 8), nullable=False)
    rate_timestamp = Column(DateTime, nullable=False)
    api_response = Column(JSON, nullable=True)  # Full API response for debugging
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Rate cache expiry
    is_cached = Column(Boolean, default=True)
    
    # API usage tracking
    api_calls_today = Column(Integer, default=0)
    api_limit_reached = Column(Boolean, default=False)
    last_api_error = Column(Text, nullable=True)

class BrevoIntegration(Base):
    """
    Database model for Brevo email service integration
    Tracks email campaigns, templates, and delivery status
    """
    __tablename__ = "brevo_integrations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_type = Column(String(100), nullable=False)  # domain_expiry, payment_confirmation, etc.
    brevo_message_id = Column(String(255), nullable=True)
    template_id = Column(Integer, nullable=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=False)
    template_data = Column(JSON, nullable=True)  # Data sent to template
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_status = Column(String(50), default="pending")  # pending, sent, delivered, bounced, failed
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    bounce_reason = Column(Text, nullable=True)
    api_response = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="email_integrations")

class TelegramIntegration(Base):
    """
    Database model for Telegram bot integration tracking
    Stores bot messages, user interactions, and notification history
    """
    __tablename__ = "telegram_integrations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    telegram_message_id = Column(String(255), nullable=True)
    message_type = Column(String(100), nullable=False)  # notification, confirmation, alert, etc.
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    user_action = Column(String(100), nullable=True)  # button_clicked, message_read, etc.
    action_timestamp = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime, nullable=True)
    api_error = Column(Text, nullable=True)
    
    # Message context
    related_domain_id = Column(Integer, ForeignKey("registered_domains.id"), nullable=True)
    related_order_id = Column(String(255), nullable=True)
    callback_data = Column(JSON, nullable=True)  # For interactive buttons
    
    # Relationships
    user = relationship("User", back_populates="telegram_integrations")
    domain = relationship("RegisteredDomain", back_populates="telegram_notifications")

class DNSOperation(Base):
    """
    Database model for DNS operations tracking (Cloudflare API calls)
    Stores all DNS record changes, API calls, and operation history
    """
    __tablename__ = "dns_operations"
    
    id = Column(Integer, primary_key=True)
    cloudflare_integration_id = Column(Integer, ForeignKey("cloudflare_integrations.id"), nullable=False)
    operation_type = Column(String(50), nullable=False)  # create, update, delete, bulk_update
    record_type = Column(String(10), nullable=False)     # A, AAAA, CNAME, MX, TXT, NS, SRV
    record_name = Column(String(255), nullable=False)
    record_content = Column(Text, nullable=False)
    ttl = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    is_proxied = Column(Boolean, default=False)
    cloudflare_record_id = Column(String(255), nullable=True)
    operation_status = Column(String(50), default="pending")  # pending, success, failed
    api_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    cloudflare_integration = relationship("CloudflareIntegration", back_populates="dns_operations")

class NameserverOperation(Base):
    """
    Database model for nameserver operations tracking (OpenProvider API calls)
    Stores nameserver updates, delegation changes, and API operation history
    """
    __tablename__ = "nameserver_operations"
    
    id = Column(Integer, primary_key=True)
    openprovider_integration_id = Column(Integer, ForeignKey("openprovider_integrations.id"), nullable=False)
    operation_type = Column(String(50), nullable=False)  # update_nameservers, delegate_to_cloudflare, custom_ns
    old_nameservers = Column(JSON, nullable=True)
    new_nameservers = Column(JSON, nullable=False)
    operation_status = Column(String(50), default="pending")  # pending, success, failed
    api_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    propagation_status = Column(String(50), default="pending")  # pending, propagating, complete
    propagation_checked_at = Column(DateTime, nullable=True)
    
    # Relationships
    openprovider_integration = relationship("OpenProviderIntegration", back_populates="nameserver_operations")

class APIUsageLog(Base):
    """
    Database model for tracking all external API usage
    Monitors rate limits, costs, and performance across all integrations
    """
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True)
    service_name = Column(String(50), nullable=False)  # cloudflare, openprovider, fastforex, brevo, telegram
    api_endpoint = Column(String(255), nullable=False)
    http_method = Column(String(10), nullable=False)   # GET, POST, PUT, DELETE
    request_data = Column(JSON, nullable=True)
    response_status = Column(Integer, nullable=False)  # HTTP status code
    response_data = Column(JSON, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    domain_id = Column(Integer, ForeignKey("registered_domains.id"), nullable=True)
    
    # Rate limiting tracking
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset_at = Column(DateTime, nullable=True)
    cost_credits = Column(DECIMAL(10, 4), nullable=True)  # API call cost if applicable
    
    # Error tracking
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User")
    domain = relationship("RegisteredDomain")

class ExternalServiceStatus(Base):
    """
    Database model for monitoring external service health and availability
    Tracks service uptime, API status, and system health checks
    """
    __tablename__ = "external_service_status"
    
    id = Column(Integer, primary_key=True)
    service_name = Column(String(50), nullable=False, unique=True)
    status = Column(String(20), default="unknown")  # operational, degraded, outage, maintenance
    last_check_at = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer, nullable=True)
    error_rate_percent = Column(DECIMAL(5, 2), default=0.0)
    uptime_percent_24h = Column(DECIMAL(5, 2), default=100.0)
    last_error = Column(Text, nullable=True)
    maintenance_mode = Column(Boolean, default=False)
    maintenance_message = Column(Text, nullable=True)
    
    # Configuration
    health_check_url = Column(String(500), nullable=True)
    check_interval_minutes = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=30)
    
    # Notifications
    alert_threshold_error_rate = Column(DECIMAL(5, 2), default=5.0)
    alert_threshold_response_time = Column(Integer, default=5000)  # 5 seconds
    last_alert_sent_at = Column(DateTime, nullable=True)