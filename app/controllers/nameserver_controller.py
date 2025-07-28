"""
Nameserver Controller - Handles nameserver management operations
"""

from typing import Dict, Any, List
from fastapi import HTTPException
from .base_controller import BaseController
from app.schemas.nameserver_schemas import (
    UpdateNameserversRequest,
    BulkUpdateRequest
)
import logging

logger = logging.getLogger(__name__)

class NameserverController(BaseController):
    """Controller for nameserver management operations"""
    
    def __init__(self, nameserver_service, domain_service):
        super().__init__()
        self.nameserver_service = nameserver_service
        self.domain_service = domain_service
    
    async def get_domain_nameservers(self, domain_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Get current nameservers for domain
        - Validates domain ownership
        - Retrieves current nameserver configuration
        - Returns nameserver DTO with provider info
        """
        try:
            # Validate input parameters
            if not domain_id or domain_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid domain_id")
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Fetching nameservers for domain {domain_id}")
            
            # Verify domain ownership
            domain = await self.domain_service.get_domain_details(domain_id, telegram_id)
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found or access denied")
            
            # Call nameserver service
            nameserver_info = await self.nameserver_service.get_domain_nameservers(domain_id)
            
            # Map to DTO
            nameserver_dto = {
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "current_nameservers": nameserver_info.nameservers,
                "provider_info": {
                    "detected_provider": nameserver_info.detected_provider,
                    "provider_confidence": nameserver_info.confidence_score,
                    "provider_features": nameserver_info.provider_features
                },
                "propagation_status": {
                    "all_propagated": nameserver_info.propagation_complete,
                    "propagation_percentage": nameserver_info.propagation_percentage,
                    "last_checked": nameserver_info.last_checked.isoformat()
                },
                "presets_available": [
                    {
                        "name": preset.name,
                        "description": preset.description,
                        "nameservers": preset.nameservers,
                        "features": preset.features
                    }
                    for preset in nameserver_info.available_presets
                ]
            }
            
            return self.success_response(
                data=nameserver_dto,
                message=f"Nameservers retrieved for {domain.domain_name}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get domain nameservers")
    
    async def update_domain_nameservers(self, domain_id: int, request: UpdateNameserversRequest, 
                                      telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Update domain nameservers
        - Validates domain ownership and nameserver format
        - Updates nameservers via OpenProvider
        - Tracks operation in audit log
        - Returns update result DTO
        """
        try:
            # Validate input
            nameserver_data = self.validate_input(request)
            
            self.logger.info(f"Updating nameservers for domain {domain_id}")
            
            # Verify domain ownership
            domain = await self.domain_service.get_domain_details(domain_id, telegram_id)
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found or access denied")
            
            # Call nameserver service
            update_result = await self.nameserver_service.update_domain_nameservers(
                domain_id=domain_id,
                nameservers=nameserver_data['nameservers'],
                telegram_id=telegram_id
            )
            
            # Map to DTO
            update_dto = {
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "operation_id": update_result.operation_id,
                "previous_nameservers": update_result.old_nameservers,
                "new_nameservers": update_result.new_nameservers,
                "update_status": update_result.status,
                "provider_response": {
                    "success": update_result.provider_success,
                    "message": update_result.provider_message,
                    "operation_time": update_result.operation_time
                },
                "propagation_info": {
                    "estimated_time": "24-48 hours",
                    "status_check_url": f"/api/v1/nameservers/{domain_id}/propagation",
                    "next_check": update_result.next_propagation_check.isoformat()
                },
                "updated_at": update_result.updated_at.isoformat()
            }
            
            return self.success_response(
                data=update_dto,
                message=f"Nameservers updated for {domain.domain_name}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "update domain nameservers")
    
    async def set_nameserver_preset(self, domain_id: int, preset_name: str, 
                                  telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Apply nameserver preset
        - Validates domain ownership and preset availability
        - Applies predefined nameserver configuration
        - Returns preset application result DTO
        """
        try:
            # Validate input parameters
            if not domain_id or domain_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid domain_id")
            if not preset_name or not preset_name.strip():
                raise HTTPException(status_code=400, detail="Invalid preset_name")
            if not telegram_id or telegram_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid telegram_id")
            
            self.logger.info(f"Applying nameserver preset '{preset_name}' to domain {domain_id}")
            
            # Verify domain ownership
            domain = await self.domain_service.get_domain_details(domain_id, telegram_id)
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found or access denied")
            
            # Call nameserver service
            preset_result = await self.nameserver_service.set_nameserver_preset(
                domain_id=domain_id,
                preset_name=preset_name,
                telegram_id=telegram_id
            )
            
            # Map to DTO
            preset_dto = {
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "preset_applied": {
                    "name": preset_result.preset_name,
                    "description": preset_result.preset_description,
                    "provider": preset_result.provider_name,
                    "features": preset_result.features_enabled
                },
                "nameservers_set": preset_result.nameservers_applied,
                "operation_id": preset_result.operation_id,
                "application_status": preset_result.status,
                "benefits": preset_result.preset_benefits,
                "applied_at": preset_result.applied_at.isoformat()
            }
            
            return self.success_response(
                data=preset_dto,
                message=f"Preset '{preset_name}' applied to {domain.domain_name}"
            )
            
        except Exception as e:
            self.handle_service_error(e, "set nameserver preset")
    
    async def get_nameserver_presets(self) -> Dict[str, Any]:
        """
        Controller: Get available nameserver presets
        - Retrieves all available preset configurations
        - Returns preset list with features and descriptions
        """
        try:
            # Validate input (method has no required parameters, but validate for consistency)
            self.logger.info("Fetching available nameserver presets")
            
            # Call nameserver service
            presets = await self.nameserver_service.get_available_presets()
            
            # Map to DTOs
            preset_dtos = []
            for preset in presets:
                preset_dto = {
                    "name": preset.name,
                    "display_name": preset.display_name,
                    "description": preset.description,
                    "provider": preset.provider,
                    "nameservers": preset.nameservers,
                    "features": {
                        "cdn": preset.features.get('cdn', False),
                        "ddos_protection": preset.features.get('ddos_protection', False),
                        "geo_blocking": preset.features.get('geo_blocking', False),
                        "ssl_certificates": preset.features.get('ssl_certificates', False),
                        "analytics": preset.features.get('analytics', False)
                    },
                    "performance_rating": preset.performance_rating,
                    "setup_complexity": preset.setup_complexity,
                    "recommended_for": preset.recommended_use_cases
                }
                preset_dtos.append(preset_dto)
            
            return self.success_response(
                data={"presets": preset_dtos, "total_count": len(preset_dtos)},
                message=f"Retrieved {len(preset_dtos)} nameserver presets"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get nameserver presets")
    
    async def get_propagation_status(self, domain_id: int, telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Check nameserver propagation status
        - Validates domain ownership
        - Checks propagation across global DNS servers
        - Returns propagation status DTO
        """
        try:
            self.logger.info(f"Checking propagation status for domain {domain_id}")
            
            # Verify domain ownership
            domain = await self.domain_service.get_domain_details(domain_id, telegram_id)
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found or access denied")
            
            # Call nameserver service
            propagation_status = await self.nameserver_service.get_nameserver_propagation_status(
                domain_id
            )
            
            # Map to DTO
            propagation_dto = {
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "propagation_summary": {
                    "overall_status": propagation_status.overall_status,
                    "completion_percentage": propagation_status.completion_percentage,
                    "estimated_completion": propagation_status.estimated_completion.isoformat() if propagation_status.estimated_completion else None
                },
                "server_checks": [
                    {
                        "server_location": check.location,
                        "server_ip": check.server_ip,
                        "nameservers_returned": check.nameservers,
                        "response_time_ms": check.response_time,
                        "status": check.status,
                        "last_checked": check.last_checked.isoformat()
                    }
                    for check in propagation_status.server_checks
                ],
                "expected_nameservers": propagation_status.expected_nameservers,
                "issues_detected": propagation_status.issues or [],
                "last_updated": propagation_status.last_updated.isoformat()
            }
            
            return self.success_response(
                data=propagation_dto,
                message=f"Propagation status: {propagation_status.completion_percentage}% complete"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get propagation status")
    
    async def get_nameserver_history(self, telegram_id: int, limit: int = 50) -> Dict[str, Any]:
        """
        Controller: Get nameserver change history for user
        - Retrieves historical nameserver operations
        - Returns paginated history DTO
        """
        try:
            self.logger.info(f"Fetching nameserver history for user {telegram_id}")
            
            # Call nameserver service
            history = await self.nameserver_service.get_user_nameserver_history(
                telegram_id=telegram_id,
                limit=limit
            )
            
            # Map to DTOs
            history_dtos = []
            for operation in history:
                history_dto = {
                    "operation_id": operation.id,
                    "domain_name": operation.domain_name,
                    "operation_type": operation.operation_type,
                    "old_nameservers": operation.old_nameservers,
                    "new_nameservers": operation.new_nameservers,
                    "preset_used": operation.preset_used,
                    "status": operation.status,
                    "created_at": operation.created_at.isoformat(),
                    "completed_at": operation.completed_at.isoformat() if operation.completed_at else None
                }
                history_dtos.append(history_dto)
            
            return self.success_response(
                data={"operations": history_dtos, "total_count": len(history_dtos)},
                message=f"Retrieved {len(history_dtos)} nameserver operations"
            )
            
        except Exception as e:
            self.handle_service_error(e, "get nameserver history")
    
    async def bulk_update_nameservers(self, request: BulkUpdateRequest, 
                                    telegram_id: int) -> Dict[str, Any]:
        """
        Controller: Bulk update nameservers for multiple domains
        - Validates domain ownership for all domains
        - Processes bulk nameserver updates
        - Returns bulk operation result DTO
        """
        try:
            # Validate input
            bulk_data = self.validate_input(request)
            
            self.logger.info(f"Bulk nameserver update for {len(bulk_data['domain_updates'])} domains")
            
            # Call nameserver service
            bulk_result = await self.nameserver_service.bulk_update_nameservers(
                domain_updates=bulk_data['domain_updates'],
                telegram_id=telegram_id
            )
            
            # Map to DTO
            bulk_dto = {
                "bulk_operation_id": bulk_result.operation_id,
                "total_domains": bulk_result.total_domains,
                "successful_updates": bulk_result.successful_count,
                "failed_updates": bulk_result.failed_count,
                "results": [
                    {
                        "domain_id": result.domain_id,
                        "domain_name": result.domain_name,
                        "status": result.status,
                        "nameservers_applied": result.nameservers if result.status == 'success' else None,
                        "error_message": result.error_message if result.status == 'failed' else None
                    }
                    for result in bulk_result.individual_results
                ],
                "overall_status": bulk_result.overall_status,
                "completed_at": bulk_result.completed_at.isoformat()
            }
            
            return self.success_response(
                data=bulk_dto,
                message=f"Bulk update completed: {bulk_result.successful_count}/{bulk_result.total_domains} successful"
            )
            
        except Exception as e:
            self.handle_service_error(e, "bulk update nameservers")