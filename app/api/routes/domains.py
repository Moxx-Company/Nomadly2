"""
Domain API Routes for Nomadly3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from decimal import Decimal

from ...repositories.domain_repo import DomainRepository
from ...services.domain_service import DomainService
from ...schemas.domain_schemas import (
    DomainResponse, DomainCreate, DomainUpdate, 
    NameserverUpdate, DomainRenewal, ContactResponse
)

router = APIRouter(prefix="/api/domains", tags=["domains"])

def get_domain_repository() -> DomainRepository:
    return None

def get_domain_service() -> DomainService:
    return None

@router.get("/", response_model=List[DomainResponse])
async def get_domains(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    domain_repo: DomainRepository = Depends(get_domain_repository)
):
    """Get domains with optional filtering"""
    try:
        if user_id:
            domains = domain_repo.get_user_domains(user_id, limit=limit, offset=offset)
        elif status:
            domains = domain_repo.get_domains_by_status(status, limit=limit, offset=offset)
        else:
            domains = domain_repo.get_all_domains(limit=limit, offset=offset)
        
        return [DomainResponse.from_orm(domain) for domain in domains]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching domains: {str(e)}"
        )

@router.get("/{domain_name}", response_model=DomainResponse)
async def get_domain(
    domain_name: str,
    domain_repo: DomainRepository = Depends(get_domain_repository)
):
    """Get domain by name"""
    domain = domain_repo.get_by_domain_name(domain_name)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    return DomainResponse.from_orm(domain)

@router.post("/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def register_domain(
    domain_data: DomainCreate,
    domain_service: DomainService = Depends(get_domain_service)
):
    """Register a new domain"""
    try:
        domain = await domain_service.register_domain(
            telegram_id=domain_data.telegram_id,
            domain_name=domain_data.domain_name,
            nameserver_mode=domain_data.nameserver_mode,
            price_paid=domain_data.price_paid,
            payment_method=domain_data.payment_method
        )
        return DomainResponse.from_orm(domain)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering domain: {str(e)}"
        )

@router.put("/{domain_name}", response_model=DomainResponse)
async def update_domain(
    domain_name: str,
    domain_data: DomainUpdate,
    domain_repo: DomainRepository = Depends(get_domain_repository)
):
    """Update domain configuration"""
    domain = domain_repo.get_by_domain_name(domain_name)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    try:
        updated_domain = domain_repo.update_domain(domain_name, domain_data.dict(exclude_unset=True))
        return DomainResponse.from_orm(updated_domain)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating domain: {str(e)}"
        )

@router.put("/{domain_name}/nameservers", response_model=DomainResponse)
async def update_nameservers(
    domain_name: str,
    nameserver_data: NameserverUpdate,
    domain_service: DomainService = Depends(get_domain_service)
):
    """Update domain nameservers"""
    try:
        domain = await domain_service.update_nameservers(
            domain_name=domain_name,
            nameservers=nameserver_data.nameservers,
            nameserver_mode=nameserver_data.nameserver_mode
        )
        return DomainResponse.from_orm(domain)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating nameservers: {str(e)}"
        )

@router.post("/{domain_name}/renew", response_model=DomainResponse)
async def renew_domain(
    domain_name: str,
    renewal_data: DomainRenewal,
    domain_service: DomainService = Depends(get_domain_service)
):
    """Renew domain registration"""
    try:
        domain = await domain_service.renew_domain(
            domain_name=domain_name,
            new_expiry_date=renewal_data.new_expiry_date,
            price_paid=renewal_data.price_paid
        )
        return DomainResponse.from_orm(domain)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error renewing domain: {str(e)}"
        )

@router.delete("/{domain_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_name: str,
    domain_repo: DomainRepository = Depends(get_domain_repository)
):
    """Delete domain registration"""
    domain = domain_repo.get_by_domain_name(domain_name)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    try:
        success = domain_repo.delete_domain(domain_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete domain"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting domain: {str(e)}"
        )

@router.get("/{domain_name}/contacts", response_model=List[ContactResponse])
async def get_domain_contacts(
    domain_name: str,
    domain_repo: DomainRepository = Depends(get_domain_repository)
):
    """Get contacts for domain"""
    try:
        contacts = domain_repo.get_domain_contacts(domain_name)
        return [ContactResponse.from_orm(contact) for contact in contacts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching domain contacts: {str(e)}"
        )