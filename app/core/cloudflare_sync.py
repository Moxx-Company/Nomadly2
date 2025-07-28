"""
Cloudflare Sync Layer - Standalone DNS Logic Module
Abstracts all Cloudflare DNS operations with proper error handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DNSRecord:
    """DNS Record data structure"""
    id: Optional[str]
    name: str
    type: str
    content: str
    ttl: int
    priority: Optional[int] = None
    cloudflare_id: Optional[str] = None

@dataclass
class SyncResult:
    """Sync operation result"""
    success: bool
    records_synced: int
    errors: List[str]
    details: Dict[str, Any]

class CloudflareSyncLayer:
    """
    Standalone Cloudflare DNS synchronization layer
    Handles all DNS logic abstraction
    """
    
    def __init__(self, cloudflare_api=None):
        self.cloudflare_api = cloudflare_api
        self.sync_queue = asyncio.Queue()
        self.sync_running = False
    
    async def sync_domain_records(self, domain_id: int, local_records: List[DNSRecord]) -> SyncResult:
        """
        Sync local DNS records with Cloudflare
        
        Args:
            domain_id: Local domain ID
            local_records: List of local DNS records
            
        Returns:
            SyncResult with sync status and details
        """
        try:
            logger.info(f"Starting DNS sync for domain {domain_id}")
            
            # Get domain info from database
            domain_info = await self._get_domain_info(domain_id)
            if not domain_info:
                return SyncResult(
                    success=False,
                    records_synced=0,
                    errors=["Domain not found"],
                    details={}
                )
            
            # Get current Cloudflare records
            cf_records = await self._get_cloudflare_records(domain_info['zone_id'])
            
            # Compare and sync
            sync_operations = self._plan_sync_operations(local_records, cf_records)
            
            results = await self._execute_sync_operations(
                domain_info['zone_id'], sync_operations
            )
            
            return SyncResult(
                success=True,
                records_synced=len(results['synced']),
                errors=results.get('errors', []),
                details=results
            )
            
        except Exception as e:
            logger.error(f"DNS sync error for domain {domain_id}: {e}")
            return SyncResult(
                success=False,
                records_synced=0,
                errors=[str(e)],
                details={}
            )
    
    async def create_cloudflare_record(self, zone_id: str, record: DNSRecord) -> Optional[str]:
        """
        Create DNS record in Cloudflare
        
        Args:
            zone_id: Cloudflare zone ID
            record: DNS record to create
            
        Returns:
            Cloudflare record ID if successful
        """
        try:
            if not self.cloudflare_api:
                raise Exception("Cloudflare API not initialized")
            
            record_data = {
                "type": record.type,
                "name": record.name,
                "content": record.content,
                "ttl": record.ttl
            }
            
            if record.priority and record.type == "MX":
                record_data["priority"] = record.priority
            
            result = await self.cloudflare_api.create_dns_record(zone_id, record_data)
            
            if result.get('success'):
                cloudflare_id = result['result']['id']
                logger.info(f"Created Cloudflare record: {cloudflare_id}")
                return cloudflare_id
            else:
                logger.error(f"Failed to create Cloudflare record: {result.get('errors')}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Cloudflare record: {e}")
            return None
    
    async def update_cloudflare_record(self, zone_id: str, record_id: str, record: DNSRecord) -> bool:
        """
        Update DNS record in Cloudflare
        
        Args:
            zone_id: Cloudflare zone ID
            record_id: Cloudflare record ID
            record: Updated DNS record data
            
        Returns:
            True if successful
        """
        try:
            if not self.cloudflare_api:
                raise Exception("Cloudflare API not initialized")
            
            record_data = {
                "type": record.type,
                "name": record.name,
                "content": record.content,
                "ttl": record.ttl
            }
            
            if record.priority and record.type == "MX":
                record_data["priority"] = record.priority
            
            result = await self.cloudflare_api.update_dns_record(zone_id, record_id, record_data)
            
            if result.get('success'):
                logger.info(f"Updated Cloudflare record: {record_id}")
                return True
            else:
                logger.error(f"Failed to update Cloudflare record: {result.get('errors')}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Cloudflare record: {e}")
            return False
    
    async def delete_cloudflare_record(self, zone_id: str, record_id: str) -> bool:
        """
        Delete DNS record from Cloudflare
        
        Args:
            zone_id: Cloudflare zone ID
            record_id: Cloudflare record ID
            
        Returns:
            True if successful
        """
        try:
            if not self.cloudflare_api:
                raise Exception("Cloudflare API not initialized")
            
            result = await self.cloudflare_api.delete_dns_record(zone_id, record_id)
            
            if result.get('success'):
                logger.info(f"Deleted Cloudflare record: {record_id}")
                return True
            else:
                logger.error(f"Failed to delete Cloudflare record: {result.get('errors')}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Cloudflare record: {e}")
            return False
    
    async def start_background_sync(self):
        """Start background sync daemon"""
        if self.sync_running:
            return
        
        self.sync_running = True
        logger.info("Starting Cloudflare background sync daemon")
        
        while self.sync_running:
            try:
                # Wait for sync requests
                sync_request = await asyncio.wait_for(
                    self.sync_queue.get(), timeout=30.0
                )
                
                # Process sync request
                await self._process_sync_request(sync_request)
                
            except asyncio.TimeoutError:
                # Periodic health check
                await self._health_check()
            except Exception as e:
                logger.error(f"Background sync error: {e}")
                await asyncio.sleep(5)
    
    def stop_background_sync(self):
        """Stop background sync daemon"""
        self.sync_running = False
        logger.info("Stopping Cloudflare background sync daemon")
    
    async def queue_sync_request(self, domain_id: int, operation: str, record_data: Dict):
        """Queue a sync request for background processing"""
        sync_request = {
            'domain_id': domain_id,
            'operation': operation,
            'record_data': record_data,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        await self.sync_queue.put(sync_request)
        logger.info(f"Queued sync request for domain {domain_id}: {operation}")
    
    # Private methods
    
    async def _get_domain_info(self, domain_id: int) -> Optional[Dict]:
        """Get domain information from database"""
        # This would typically query the database
        # For now, return mock data
        return {
            'zone_id': 'mock_zone_id',
            'domain_name': 'example.com'
        }
    
    async def _get_cloudflare_records(self, zone_id: str) -> List[Dict]:
        """Get current DNS records from Cloudflare"""
        if not self.cloudflare_api:
            return []
        
        try:
            result = await self.cloudflare_api.list_dns_records(zone_id)
            if result.get('success'):
                return result['result']
            else:
                logger.error(f"Failed to get Cloudflare records: {result.get('errors')}")
                return []
        except Exception as e:
            logger.error(f"Error getting Cloudflare records: {e}")
            return []
    
    def _plan_sync_operations(self, local_records: List[DNSRecord], cf_records: List[Dict]) -> Dict:
        """Plan sync operations based on record differences"""
        operations = {
            'create': [],
            'update': [],
            'delete': []
        }
        
        # Create lookup for Cloudflare records
        cf_lookup = {r['id']: r for r in cf_records}
        
        for local_record in local_records:
            if local_record.cloudflare_id:
                # Record exists in Cloudflare, check for updates
                cf_record = cf_lookup.get(local_record.cloudflare_id)
                if cf_record:
                    if self._records_different(local_record, cf_record):
                        operations['update'].append((local_record, cf_record))
                else:
                    # Cloudflare record deleted, recreate
                    operations['create'].append(local_record)
            else:
                # New record, create in Cloudflare
                operations['create'].append(local_record)
        
        return operations
    
    def _records_different(self, local_record: DNSRecord, cf_record: Dict) -> bool:
        """Check if local and Cloudflare records are different"""
        return (
            local_record.content != cf_record.get('content') or
            local_record.ttl != cf_record.get('ttl') or
            local_record.priority != cf_record.get('priority')
        )
    
    async def _execute_sync_operations(self, zone_id: str, operations: Dict) -> Dict:
        """Execute planned sync operations"""
        results = {
            'synced': [],
            'errors': []
        }
        
        # Execute creates
        for record in operations['create']:
            cloudflare_id = await self.create_cloudflare_record(zone_id, record)
            if cloudflare_id:
                results['synced'].append(f"Created {record.name}")
            else:
                results['errors'].append(f"Failed to create {record.name}")
        
        # Execute updates
        for local_record, cf_record in operations['update']:
            success = await self.update_cloudflare_record(
                zone_id, local_record.cloudflare_id, local_record
            )
            if success:
                results['synced'].append(f"Updated {local_record.name}")
            else:
                results['errors'].append(f"Failed to update {local_record.name}")
        
        return results
    
    async def _process_sync_request(self, sync_request: Dict):
        """Process a background sync request"""
        try:
            domain_id = sync_request['domain_id']
            operation = sync_request['operation']
            
            logger.info(f"Processing sync request: {operation} for domain {domain_id}")
            
            # Process based on operation type
            if operation == 'full_sync':
                await self._full_domain_sync(domain_id)
            elif operation == 'record_update':
                await self._single_record_sync(sync_request)
            
        except Exception as e:
            logger.error(f"Error processing sync request: {e}")
    
    async def _full_domain_sync(self, domain_id: int):
        """Perform full domain synchronization"""
        # Get all local records for domain
        # This would typically query the database
        local_records = []  # Mock
        
        # Perform sync
        result = await self.sync_domain_records(domain_id, local_records)
        logger.info(f"Full sync completed for domain {domain_id}: {result.success}")
    
    async def _single_record_sync(self, sync_request: Dict):
        """Sync a single DNS record"""
        # Implementation for single record sync
        pass
    
    async def _health_check(self):
        """Perform periodic health check"""
        # Check Cloudflare API connectivity
        # Log system status
        logger.debug("Cloudflare sync daemon health check")

# Global sync layer instance
sync_layer = CloudflareSyncLayer()

async def get_sync_layer():
    """Get the global sync layer instance"""
    return sync_layer