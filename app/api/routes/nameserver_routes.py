"""
Nameserver Management API Routes
Provides RESTful endpoints for nameserver operations via OpenProvider API
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import logging

from ...services.nameserver_service import NameserverService
from ...schemas.nameserver_schemas import (
    NameserverInfoResponse,
    UpdateNameserversRequest,
    UpdateNameserversResponse,
    NameserverPresetResponse,
    PropagationStatusResponse,
    NameserverHistoryResponse,
    BulkUpdateRequest,
    BulkUpdateResponse
)
from ...core.dependencies import get_nameserver_service

logger = logging.getLogger(__name__)

nameserver_router = APIRouter(prefix="/nameservers", tags=["nameservers"])

@nameserver_router.get("/{domain_id}", response_model=NameserverInfoResponse)
async def get_domain_nameservers(
    domain_id: int,
    telegram_id: int,
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Get current nameserver configuration for a domain
    UI Integration: Display current nameservers with provider detection
    """
    try:
        result = nameserver_service.get_domain_nameservers(domain_id, telegram_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to get nameservers")
            )
        
        return NameserverInfoResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_domain_nameservers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.put("/{domain_id}", response_model=UpdateNameserversResponse)
async def update_domain_nameservers(
    domain_id: int,
    request: UpdateNameserversRequest,
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Update nameservers for a domain via OpenProvider API
    UI Integration: Process nameserver change requests with validation
    """
    try:
        result = nameserver_service.update_domain_nameservers(
            domain_id=domain_id,
            telegram_id=request.telegram_id,
            nameservers=request.nameservers,
            provider_name=request.provider_name
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to update nameservers")
            )
        
        return UpdateNameserversResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_domain_nameservers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.post("/{domain_id}/preset/{preset_name}", response_model=UpdateNameserversResponse)
async def set_nameserver_preset(
    domain_id: int,
    preset_name: str,
    telegram_id: int,
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Set nameservers using a predefined preset (Cloudflare, OpenProvider, etc.)
    UI Integration: Quick nameserver switching with preset buttons
    """
    try:
        result = nameserver_service.set_nameserver_preset(
            domain_id=domain_id,
            telegram_id=telegram_id,
            preset_name=preset_name
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to set nameserver preset")
            )
        
        return UpdateNameserversResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set_nameserver_preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.get("/presets", response_model=NameserverPresetResponse)
async def get_nameserver_presets(
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Get available nameserver presets
    UI Integration: Display preset options with descriptions and features
    """
    try:
        presets = nameserver_service.NAMESERVER_PRESETS
        
        return NameserverPresetResponse(
            success=True,
            presets=presets
        )
        
    except Exception as e:
        logger.error(f"Error in get_nameserver_presets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.get("/{domain_id}/propagation", response_model=PropagationStatusResponse)
async def get_propagation_status(
    domain_id: int,
    telegram_id: int,
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Check nameserver propagation status across global DNS
    UI Integration: Show propagation progress with global status
    """
    try:
        result = nameserver_service.get_nameserver_propagation_status(domain_id, telegram_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to check propagation")
            )
        
        return PropagationStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_propagation_status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.get("/history/{telegram_id}", response_model=NameserverHistoryResponse)
async def get_nameserver_history(
    telegram_id: int,
    limit: int = 10,
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Get nameserver change history for user
    UI Integration: Display recent nameserver changes across all domains
    """
    try:
        result = nameserver_service.get_user_nameserver_history(telegram_id, limit)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to get history")
            )
        
        return NameserverHistoryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_nameserver_history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.put("/bulk-update", response_model=BulkUpdateResponse)
async def bulk_update_nameservers(
    request: BulkUpdateRequest,
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Update nameservers for multiple domains at once
    UI Integration: Bulk nameserver management for power users
    """
    try:
        result = nameserver_service.bulk_update_nameservers(
            domain_ids=request.domain_ids,
            telegram_id=request.telegram_id,
            nameservers=request.nameservers,
            provider_name=request.provider_name
        )
        
        return BulkUpdateResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in bulk_update_nameservers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@nameserver_router.post("/validate", response_model=dict)
async def validate_nameservers(
    nameservers: List[str],
    nameserver_service: NameserverService = Depends(get_nameserver_service)
):
    """
    Validate nameserver format and accessibility
    UI Integration: Real-time validation feedback for nameserver input
    """
    try:
        result = nameserver_service.validate_nameservers(nameservers)
        return result
        
    except Exception as e:
        logger.error(f"Error in validate_nameservers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )