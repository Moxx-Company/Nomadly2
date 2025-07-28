"""
Base Controller - Common functionality for all controllers
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class BaseController:
    """Base controller with common functionality"""
    
    def __init__(self):
        self.logger = logger
    
    def success_response(self, data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Format successful response"""
        response = {
            "success": True,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    def error_response(self, message: str, error_code: str = "ERROR", 
                      details: Any = None) -> Dict[str, Any]:
        """Format error response"""
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }
        if details:
            response["error"]["details"] = details
        return response
    
    def paginated_response(self, items: List[Any], total: int, page: int = 1, 
                          per_page: int = 20) -> Dict[str, Any]:
        """Format paginated response"""
        return {
            "success": True,
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "pages": (total + per_page - 1) // per_page
                }
            }
        }
    
    def validate_input(self, data: BaseModel) -> Dict[str, Any]:
        """Validate input data and return dict representation"""
        try:
            return data.model_dump()
        except Exception as e:
            self.logger.error(f"Input validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    
    def handle_service_error(self, error: Exception, operation: str) -> None:
        """Handle service layer errors consistently"""
        self.logger.error(f"Service error in {operation}: {error}")
        
        if "not found" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error))
        elif "unauthorized" in str(error).lower():
            raise HTTPException(status_code=401, detail=str(error))
        elif "forbidden" in str(error).lower():
            raise HTTPException(status_code=403, detail=str(error))
        elif "invalid" in str(error).lower() or "bad" in str(error).lower():
            raise HTTPException(status_code=400, detail=str(error))
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error in {operation}")
    
    def map_domain_to_dto(self, domain_obj: Any, include_relations: bool = False) -> Dict[str, Any]:
        """Map domain object to DTO (Data Transfer Object)"""
        if not domain_obj:
            return {}
        
        # Base domain mapping
        dto = {
            "id": getattr(domain_obj, 'id', None),
            "created_at": getattr(domain_obj, 'created_at', None),
            "updated_at": getattr(domain_obj, 'updated_at', None)
        }
        
        # Include relations if requested
        if include_relations:
            dto["_relations"] = self._extract_relations(domain_obj)
        
        return dto
    
    def _extract_relations(self, obj: Any) -> Dict[str, Any]:
        """Extract relationship data from domain object"""
        relations = {}
        
        # Common relationship patterns
        relation_attrs = ['user', 'domain', 'dns_records', 'transactions', 'orders']
        
        for attr in relation_attrs:
            if hasattr(obj, attr):
                rel_value = getattr(obj, attr)
                if rel_value:
                    if hasattr(rel_value, '__iter__') and not isinstance(rel_value, str):
                        # Collection relationship
                        relations[attr] = [self.map_domain_to_dto(item) for item in rel_value]
                    else:
                        # Single relationship
                        relations[attr] = self.map_domain_to_dto(rel_value)
        
        return relations
    
    def apply_filters(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply common filters from query parameters"""
        filters = {}
        
        # Common filter patterns
        if 'status' in query_params:
            filters['status'] = query_params['status']
        if 'created_after' in query_params:
            filters['created_after'] = query_params['created_after']
        if 'created_before' in query_params:
            filters['created_before'] = query_params['created_before']
        if 'search' in query_params:
            filters['search'] = query_params['search']
        
        return filters