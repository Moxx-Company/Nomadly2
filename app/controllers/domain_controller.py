"""
Domain Controller - Handles domain management operations
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from .base_controller import BaseController
from app.schemas.domain_schemas import (
    DomainRegistrationRequest, 
    DomainListResponse,
    DomainAvailabilityRequest,
    DomainUpdateRequest
)
import logging

logger = logging.getLogger(__name__)

class DomainController(BaseController):
    """Controller for domain management operations"""
    
    def __init__(self, domain_service, user_service):
        super().__init__()
        self.domain_service = domain_service
        self.user_service = user_service
    
    async def check_domain_availability(self, request: DomainAvailabilityRequest) -> Dict[str, Any]:
        """
        Controller: Check domain availability
        - Receives input from API
        - Validates domain format
        - Calls domain service
        - Formats response with pricing
        """
        try:
            # Validate input
            domain_data = self.validate_input(request)
            domain_name = domain_data['domain_name']
            
            self.logger.info(f"Checking availability for domain: {domain_name}")
            
            # Call service layer
            availability_result = await self.domain_service.check_domain_availability(domain_name)
            
            # Map domain result to DTO
            response_dto = {
                "domain_name": availability_result.domain_name,
                "available": availability_result.available,
                "price_usd": availability_result.price_usd,
                "currency": "USD",
                "premium_multiplier": availability_result.premium_multiplier,
                "tld": availability_result.tld,
                "registration_period": availability_result.registration_period,
                "alternative_suggestions": availability_result.alternatives or []
            }
            
            return self.success_response(
                data=response_dto,
                message=f"Domain availability checked for {domain_name}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "domain availability check")
    
    async def register_domain(self, request: DomainRegistrationRequest, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Register new domain
        - Receives registration request
        - Validates user authorization
        - Coordinates domain + DNS setup
        - Returns registration status
        """
        try:
            # Validate input
            registration_data = self.validate_input(request)
            
            self.logger.info(f"Processing domain registration for user {telegram_id}")
            
            # Verify user exists and has sufficient balance
            user = await self.user_service.get_user_by_telegram_id(telegram_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user.balance_usd < registration_data['price_usd']:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            
            # Call service layer for domain registration
            registration_result = await self.domain_service.register_domain(
                telegram_id=telegram_id,
                domain_name=registration_data['domain_name'],
                registration_years=registration_data.get('registration_years', 1),
                dns_provider=registration_data.get('dns_provider', 'cloudflare'),
                email_contact=registration_data.get('email_contact'),
                auto_renew=registration_data.get('auto_renew', True)
            )
            
            # Map registration result to DTO
            response_dto = {
                "domain_id": registration_result.domain_id,
                "domain_name": registration_result.domain_name,
                "status": registration_result.status,
                "expires_at": registration_result.expires_at.isoformat(),
                "nameservers": registration_result.nameservers,
                "dns_zone_id": registration_result.dns_zone_id,
                "registration_cost": registration_result.cost_usd,
                "order_id": registration_result.order_id
            }
            
            return self.success_response(
                data=response_dto,
                message=f"Domain {registration_data['domain_name']} registered successfully"
            )
            
        except Exception as e:
            self.handle_service_error(e, "domain registration")
    
    async def get_user_domains(self, telegram_id: int, include_dns: bool = False, 
                              page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Controller: Get user's domain portfolio
        - Receives user ID and filters
        - Calls service for domain list
        - Maps domains to DTOs
        - Returns paginated response
        """
        try:
            # Validate input parameters
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Fetching domains for user {telegram_id}")
            
            # Call service layer
            domains_result = await self.domain_service.get_user_domain_portfolio(
                telegram_id=telegram_id,
                include_dns_records=include_dns,
                page=page,
                per_page=per_page
            )
            
            # Map domains to DTOs
            domain_dtos = []
            for domain in domains_result.domains:
                domain_dto = {
                    "id": domain.id,
                    "domain_name": domain.domain_name,
                    "tld": domain.tld,
                    "status": domain.status,
                    "expires_at": domain.expires_at.isoformat(),
                    "days_until_expiry": domain.days_until_expiry,
                    "auto_renew": domain.auto_renew,
                    "nameservers": domain.nameservers,
                    "registrar": "OpenProvider",
                    "dns_provider": domain.dns_provider,
                    "created_at": domain.created_at.isoformat()
                }
                
                # Include DNS records if requested
                if include_dns and hasattr(domain, 'dns_records'):
                    domain_dto["dns_records"] = [
                        {
                            "id": record.id,
                            "type": record.record_type,
                            "name": record.name,
                            "content": record.content,
                            "ttl": record.ttl,
                            "priority": record.priority
                        }
                        for record in domain.dns_records
                    ]
                
                domain_dtos.append(domain_dto)
            
            return self.success_response(
                data={
                    "items": domain_dtos,
                    "pagination": {
                        "total": domains_result.total_count,
                        "page": page,
                        "per_page": per_page,
                        "pages": (domains_result.total_count + per_page - 1) // per_page
                    }
                },
                message=f"Retrieved {len(domain_dtos)} domains"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get user domains")
    
    async def get_domain_details(self, domain_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Get detailed domain information
        - Validates domain ownership
        - Calls service for full domain data
        - Maps to comprehensive DTO
        """
        try:
            # Validate input parameters
            if not domain_id or domain_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid domain_id")
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Fetching details for domain {domain_id}")
            
            # Call service layer
            domain_details = await self.domain_service.get_domain_details(
                domain_id=domain_id,
                telegram_id=telegram_id
            )
            
            if not domain_details:
                raise HTTPException(status_code=404, detail="Domain not found")
            
            # Map to comprehensive DTO
            details_dto = {
                "domain_info": {
                    "id": domain_details.id,
                    "domain_name": domain_details.domain_name,
                    "tld": domain_details.tld,
                    "status": domain_details.status,
                    "expires_at": domain_details.expires_at.isoformat(),
                    "days_until_expiry": domain_details.days_until_expiry,
                    "auto_renew": domain_details.auto_renew,
                    "registrar_id": domain_details.registrar_id,
                    "price_paid_usd": float(domain_details.price_paid_usd)
                },
                "dns_info": {
                    "provider": domain_details.dns_provider,
                    "zone_id": domain_details.cloudflare_zone_id,
                    "nameservers": domain_details.nameservers,
                    "record_count": len(domain_details.dns_records) if domain_details.dns_records else 0
                },
                "statistics": {
                    "created_at": domain_details.created_at.isoformat(),
                    "last_updated": domain_details.updated_at.isoformat() if domain_details.updated_at else None,
                    "renewal_history": getattr(domain_details, 'renewal_history', [])
                }
            }
            
            return self.success_response(
                data=details_dto,
                message=f"Domain details retrieved for {domain_details.domain_name}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get domain details")
    
    async def update_domain_settings(self, domain_id: int, request: DomainUpdateRequest, 
                                   telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Update domain settings
        - Validates ownership and input
        - Calls service for updates
        - Returns updated domain DTO
        """
        try:
            # Validate input
            update_data = self.validate_input(request)
            
            self.logger.info(f"Updating domain {domain_id} settings")
            
            # Call service layer
            updated_domain = await self.domain_service.update_domain_settings(
                domain_id=domain_id,
                telegram_id=telegram_id,
                settings=update_data
            )
            
            # Map updated domain to DTO
            domain_dto = self.map_domain_to_dto(updated_domain, include_relations=False)
            domain_dto.update({
                "domain_name": updated_domain.domain_name,
                "auto_renew": updated_domain.auto_renew,
                "dns_provider": updated_domain.dns_provider,
                "status": updated_domain.status
            })
            
            return self.success_response(
                data=domain_dto,
                message=f"Domain {updated_domain.domain_name} settings updated"
            )
            
        except Exception as e:
            self.handle_service_error(e, "update domain settings")