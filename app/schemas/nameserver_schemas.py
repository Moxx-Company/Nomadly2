"""
Nameserver Management Schemas
Pydantic schemas for nameserver API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime

class UpdateNameserversRequest(BaseModel):
    """Request schema for updating domain nameservers"""
    telegram_id: int = Field(..., description="User's Telegram ID")
    nameservers: List[str] = Field(..., description="List of nameserver hostnames")
    provider_name: Optional[str] = Field(None, description="Nameserver provider name")
    
    @validator('nameservers')
    def validate_nameservers(cls, v):
        if not v:
            raise ValueError("At least one nameserver is required")
        if len(v) > 6:
            raise ValueError("Maximum 6 nameservers allowed")
        return v

class NameserverProvider(BaseModel):
    """Schema for nameserver provider information"""
    provider: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Provider display name")
    confidence: int = Field(..., description="Detection confidence percentage")
    description: Optional[str] = Field(None, description="Provider description")
    features: Optional[List[str]] = Field(None, description="Provider features")

class NameserverInfoResponse(BaseModel):
    """Response schema for domain nameserver information"""
    success: bool = Field(..., description="Operation success status")
    domain_name: str = Field(..., description="Domain name")
    domain_id: int = Field(..., description="Domain ID")
    current_nameservers: List[str] = Field(..., description="Current nameservers")
    provider: NameserverProvider = Field(..., description="Detected provider information")
    nameserver_status: str = Field(..., description="Nameserver status")
    propagation_status: str = Field(..., description="DNS propagation status")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    can_manage: bool = Field(..., description="Whether nameservers can be managed")
    presets: Dict[str, Any] = Field(..., description="Available nameserver presets")

class UpdateNameserversResponse(BaseModel):
    """Response schema for nameserver update operations"""
    success: bool = Field(..., description="Operation success status")
    domain_name: str = Field(..., description="Domain name")
    old_nameservers: List[str] = Field(..., description="Previous nameservers")
    new_nameservers: List[str] = Field(..., description="New nameservers")
    provider: Optional[str] = Field(None, description="Provider name")
    propagation_time: str = Field(..., description="Expected propagation time")
    message: str = Field(..., description="Success message")

class NameserverPreset(BaseModel):
    """Schema for nameserver preset configuration"""
    name: str = Field(..., description="Preset display name")
    nameservers: List[str] = Field(..., description="Nameserver list")
    description: str = Field(..., description="Preset description")
    features: List[str] = Field(..., description="Preset features")

class NameserverPresetResponse(BaseModel):
    """Response schema for nameserver presets"""
    success: bool = Field(..., description="Operation success status")
    presets: Dict[str, NameserverPreset] = Field(..., description="Available presets")

class GlobalPropagationCheck(BaseModel):
    """Schema for global DNS propagation check"""
    location: str = Field(..., description="Geographic location")
    status: str = Field(..., description="Propagation status")
    nameservers: List[str] = Field(..., description="Detected nameservers")

class PropagationInfo(BaseModel):
    """Schema for nameserver propagation information"""
    domain_name: str = Field(..., description="Domain name")
    expected_nameservers: List[str] = Field(..., description="Expected nameservers")
    propagation_percentage: int = Field(..., description="Propagation completion percentage")
    status: str = Field(..., description="Overall propagation status")
    estimated_completion: str = Field(..., description="Estimated completion time")
    global_checks: List[GlobalPropagationCheck] = Field(..., description="Global propagation checks")

class PropagationStatusResponse(BaseModel):
    """Response schema for propagation status check"""
    success: bool = Field(..., description="Operation success status")
    propagation: PropagationInfo = Field(..., description="Propagation information")

class NameserverHistoryEntry(BaseModel):
    """Schema for nameserver history entry"""
    domain_name: str = Field(..., description="Domain name")
    domain_id: int = Field(..., description="Domain ID")
    timestamp: str = Field(..., description="Change timestamp")
    old_nameservers: List[str] = Field(..., description="Previous nameservers")
    new_nameservers: List[str] = Field(..., description="New nameservers")
    provider: Optional[str] = Field(None, description="Provider name")
    success: bool = Field(..., description="Whether change was successful")

class NameserverHistoryResponse(BaseModel):
    """Response schema for nameserver history"""
    success: bool = Field(..., description="Operation success status")
    history: List[NameserverHistoryEntry] = Field(..., description="Nameserver change history")
    total_changes: int = Field(..., description="Total number of changes")

class BulkUpdateRequest(BaseModel):
    """Request schema for bulk nameserver updates"""
    telegram_id: int = Field(..., description="User's Telegram ID")
    domain_ids: List[int] = Field(..., description="List of domain IDs")
    nameservers: List[str] = Field(..., description="Nameservers to set")
    provider_name: Optional[str] = Field(None, description="Provider name")

class BulkUpdateResult(BaseModel):
    """Schema for individual bulk update result"""
    domain_id: int = Field(..., description="Domain ID")
    success: bool = Field(..., description="Update success status")
    domain_name: str = Field(..., description="Domain name")
    error: Optional[str] = Field(None, description="Error message if failed")

class BulkUpdateResponse(BaseModel):
    """Response schema for bulk nameserver updates"""
    success: bool = Field(..., description="Overall operation success")
    total_domains: int = Field(..., description="Total domains processed")
    successful_updates: int = Field(..., description="Number of successful updates")
    failed_updates: int = Field(..., description="Number of failed updates")
    results: List[BulkUpdateResult] = Field(..., description="Individual update results")
    nameservers: List[str] = Field(..., description="Nameservers that were set")
    provider: Optional[str] = Field(None, description="Provider name")