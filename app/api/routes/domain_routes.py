"""
Domain Management Routes for Nomadly3 API
FastAPI router for domain operations (list, add, update, delete)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
import logging

from ...schemas.domain_schemas import (
    DomainRegistrationRequest, DomainResponse, DomainListResponse,
    DomainUpdateRequest, DomainAvailabilityRequest
)
from ...services.domain_service import DomainService
from ...repositories.domain_repo import DomainRepository
from ...repositories.user_repo import UserRepository
from ...repositories.external_integration_repo import (
    OpenProviderIntegrationRepository, CloudflareIntegrationRepository
)
from ...core.database import get_db_session
from .auth_routes import get_current_user

logger = logging.getLogger(__name__)

# Create router
domain_router = APIRouter(
    prefix="/domains",
    tags=["Domain Management"],
    responses={404: {"description": "Not found"}}
)

def get_domain_service() -> DomainService:
    """Dependency injection for DomainService"""
    db_session = get_db_session()
    domain_repo = DomainRepository(db_session)
    user_repo = UserRepository(db_session)
    openprovider_repo = OpenProviderIntegrationRepository(db_session)
    cloudflare_repo = CloudflareIntegrationRepository(db_session)
    return DomainService(domain_repo, user_repo, openprovider_repo, cloudflare_repo)

@domain_router.get("/", response_model=DomainListResponse)
async def list_user_domains(
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status: active, expired, pending")
) -> Dict[str, Any]:
    """
    List user domains with pagination and filtering
    
    Returns paginated list of user's registered domains
    """
    try:
        logger.info(f"Listing domains for user: {current_user['telegram_id']}")
        
        result = domain_service.get_user_domains_paginated(
            telegram_id=current_user["telegram_id"],
            page=page,
            limit=limit,
            status_filter=status_filter
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to retrieve domains")
            )
        
        return {
            "success": True,
            "domains": result["domains"],
            "pagination": result["pagination"],
            "message": f"Retrieved {len(result['domains'])} domains"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Domain listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve domains"
        )

@domain_router.post("/check-availability", response_model=Dict[str, Any])
async def check_domain_availability(
    availability_request: DomainAvailabilityRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service)
) -> Dict[str, Any]:
    """
    Check domain availability and pricing
    
    Validates domain format and checks availability with OpenProvider
    """
    try:
        logger.info(f"Checking availability for: {availability_request.domain_name}")
        
        result = domain_service.check_domain_availability(availability_request.domain_name)
        
        return {
            "success": True,
            "domain": result.domain,
            "available": result.available,
            "price": float(result.price) if result.price else None,
            "premium": result.premium,
            "alternative_suggestions": result.alternative_suggestions,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"Domain availability check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check domain availability"
        )

@domain_router.post("/register", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def register_domain(
    registration_request: DomainRegistrationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service)
) -> Dict[str, Any]:
    """
    Register new domain
    
    Processes domain registration with OpenProvider and sets up DNS
    """
    try:
        logger.info(f"Registering domain: {registration_request.domain_name} for user: {current_user['telegram_id']}")
        
        # Validate user has sufficient balance
        total_cost = domain_service.calculate_domain_pricing(
            registration_request.domain_name,
            registration_request.registration_period or 1
        )
        
        if not total_cost.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to calculate domain pricing"
            )
        
        # Process registration
        result = domain_service.register_domain(
            telegram_id=current_user["telegram_id"],
            domain_name=registration_request.domain_name,
            nameserver_mode=registration_request.nameserver_mode,
            custom_nameservers=registration_request.custom_nameservers,
            technical_email=registration_request.technical_email,
            registration_period=registration_request.registration_period or 1
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Domain registration failed")
            )
        
        return {
            "success": True,
            "domain": result["domain"],
            "message": "Domain registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Domain registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain registration failed"
        )

@domain_router.get("/my/{telegram_id}")
async def get_user_domains(
    telegram_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service)
) -> Dict[str, Any]:
    """Get all domains for a user"""
    try:
        domains = await domain_service.get_user_domain_portfolio(telegram_id)
        return {"success": True, "domains": domains}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not get domains: {str(e)}")

@domain_router.get("/search")
async def search_domains(
    query: str,
    tlds: str = "com,net,org",
    telegram_id: int = None,
    domain_service: DomainService = Depends(get_domain_service)
):
    """Search for domain availability"""
    try:
        tld_list = tlds.split(",")
        results = await domain_service.check_multiple_domain_availability(query, tld_list)
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain search failed: {str(e)}")

@domain_router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain_details(
    domain_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service)
) -> Dict[str, Any]:
    """
    Get detailed domain information
    
    Returns comprehensive domain details including DNS records and settings
    """
    try:
        logger.info(f"Getting domain details: {domain_id} for user: {current_user['telegram_id']}")
        
        result = domain_service.get_domain_details(
            domain_id=domain_id,
            telegram_id=current_user["telegram_id"]
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Domain not found")
            )
        
        return {
            "success": True,
            "domain": result["domain"],
            "message": "Domain details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Domain details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve domain details"
        )

@domain_router.put("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: int,
    update_request: DomainUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service)
) -> Dict[str, Any]:
    """
    Update domain settings
    
    Updates domain configuration including nameservers and auto-renewal
    """
    try:
        logger.info(f"Updating domain: {domain_id} for user: {current_user['telegram_id']}")
        
        result = domain_service.update_domain_settings(
            domain_id=domain_id,
            telegram_id=current_user["telegram_id"],
            nameserver_mode=update_request.nameserver_mode,
            custom_nameservers=update_request.custom_nameservers,
            auto_renew=update_request.auto_renew,
            technical_contact=update_request.technical_contact
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Domain update failed")
            )
        
        return {
            "success": True,
            "domain": result["domain"],
            "message": "Domain updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Domain update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain update failed"
        )

@domain_router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service)
) -> None:
    """
    Delete domain registration
    
    Removes domain from user account (does not cancel registration with provider)
    """
    try:
        logger.info(f"Deleting domain: {domain_id} for user: {current_user['telegram_id']}")
        
        result = domain_service.remove_domain_from_account(
            domain_id=domain_id,
            telegram_id=current_user["telegram_id"]
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Domain not found or access denied")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Domain deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain deletion failed"
        )

@domain_router.post("/{domain_id}/renew", response_model=DomainResponse)
async def renew_domain(
    domain_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    domain_service: DomainService = Depends(get_domain_service),
    years: int = Query(1, ge=1, le=10, description="Renewal period in years")
) -> Dict[str, Any]:
    """
    Renew domain registration
    
    Extends domain registration period with OpenProvider
    """
    try:
        logger.info(f"Renewing domain: {domain_id} for {years} years, user: {current_user['telegram_id']}")
        
        result = domain_service.renew_domain(
            domain_id=domain_id,
            telegram_id=current_user["telegram_id"],
            renewal_period=years
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Domain renewal failed")
            )
        
        return {
            "success": True,
            "domain": result["domain"],
            "message": f"Domain renewed for {years} year(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Domain renewal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain renewal failed"
        )
# Fix for app/api/routes/domain_routes.py - Export router correctly
router = domain_router  # Add this line at the end of the file

# Export router for import compatibility  
router = domain_router
