"""
Background Job Queue System for Nomadly2
Handles asynchronous processing of payments, domain registrations, and notifications
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Job:
    """Represents a background job"""
    id: str
    job_type: str
    payload: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class BackgroundJobQueue:
    """Manages background job processing with priority queue and retry logic"""
    
    def __init__(self, max_workers: int = 4):
        self.jobs: Dict[str, Job] = {}
        self.job_handlers: Dict[str, Callable] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.worker_tasks = []
        
    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler function for a specific job type"""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    def add_job(self, job_type: str, payload: Dict[str, Any], 
                priority: JobPriority = JobPriority.NORMAL,
                max_retries: int = 3) -> str:
        """Add a new job to the queue"""
        job_id = f"{job_type}_{int(time.time() * 1000)}_{hash(str(payload)) % 10000}"
        
        job = Job(
            id=job_id,
            job_type=job_type,
            payload=payload,
            priority=priority,
            max_retries=max_retries
        )
        
        self.jobs[job_id] = job
        logger.info(f"Added job {job_id} of type {job_type} with priority {priority.name}")
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_pending_jobs(self) -> List[Job]:
        """Get all pending jobs sorted by priority and creation time"""
        pending_jobs = [
            job for job in self.jobs.values() 
            if job.status == JobStatus.PENDING
        ]
        
        # Sort by priority (descending) then by creation time (ascending)
        return sorted(pending_jobs, key=lambda j: (-j.priority.value, j.created_at))
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with specific status"""
        return [job for job in self.jobs.values() if job.status == status]
    
    def get_jobs_by_type(self, job_type: str) -> List[Job]:
        """Get all jobs of specific type"""
        return [job for job in self.jobs.values() if job.job_type == job_type]
    
    async def process_job(self, job: Job) -> bool:
        """Process a single job"""
        if job.job_type not in self.job_handlers:
            logger.error(f"No handler registered for job type: {job.job_type}")
            job.status = JobStatus.FAILED
            job.error_message = f"No handler for job type: {job.job_type}"
            return False
        
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        
        try:
            logger.info(f"Processing job {job.id} of type {job.job_type}")
            
            handler = self.job_handlers[job.job_type]
            
            # Run handler in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                handler, 
                job.payload
            )
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result = result if isinstance(result, dict) else {"success": True, "result": result}
            
            logger.info(f"Successfully completed job {job.id}")
            return True
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            
            job.retry_count += 1
            job.error_message = str(e)
            
            if job.retry_count >= job.max_retries:
                job.status = JobStatus.FAILED
                logger.error(f"Job {job.id} failed permanently after {job.retry_count} retries")
                return False
            else:
                job.status = JobStatus.PENDING  # Will be retried
                logger.info(f"Job {job.id} will be retried ({job.retry_count}/{job.max_retries})")
                return False
    
    async def worker(self, worker_id: int):
        """Background worker to process jobs"""
        logger.info(f"Starting worker {worker_id}")
        
        while self.running:
            try:
                pending_jobs = self.get_pending_jobs()
                
                if not pending_jobs:
                    await asyncio.sleep(1)  # No jobs, wait a bit
                    continue
                
                # Get highest priority job
                job = pending_jobs[0]
                
                # Check if we should delay retry
                if job.retry_count > 0:
                    delay = min(300, 2 ** job.retry_count)  # Exponential backoff, max 5 minutes
                    time_since_last_attempt = (datetime.utcnow() - job.started_at).total_seconds() if job.started_at else float('inf')
                    
                    if time_since_last_attempt < delay:
                        await asyncio.sleep(1)  # Not time to retry yet
                        continue
                
                await self.process_job(job)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def start(self):
        """Start the job queue processing"""
        if self.running:
            logger.warning("Job queue is already running")
            return
        
        self.running = True
        logger.info(f"Starting job queue with {self.max_workers} workers")
        
        # Start worker tasks
        self.worker_tasks = [
            asyncio.create_task(self.worker(i)) 
            for i in range(self.max_workers)
        ]
        
        logger.info("Job queue started successfully")
    
    async def stop(self):
        """Stop the job queue processing"""
        if not self.running:
            return
        
        logger.info("Stopping job queue...")
        self.running = False
        
        # Wait for workers to finish
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            self.worker_tasks = []
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Job queue stopped")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        status_counts = {}
        for status in JobStatus:
            status_counts[status.value] = len(self.get_jobs_by_status(status))
        
        return {
            "total_jobs": len(self.jobs),
            "status_counts": status_counts,
            "job_types": list(set(job.job_type for job in self.jobs.values())),
            "oldest_pending": min(
                (job.created_at for job in self.jobs.values() if job.status == JobStatus.PENDING),
                default=None
            ),
            "workers": self.max_workers,
            "running": self.running
        }
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove old completed/failed jobs"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        jobs_to_remove = [
            job_id for job_id, job in self.jobs.items()
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]
            and job.created_at < cutoff_time
        ]
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
        
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")

# Global job queue instance
_job_queue: Optional[BackgroundJobQueue] = None

def get_job_queue() -> BackgroundJobQueue:
    """Get the global job queue instance"""
    global _job_queue
    if _job_queue is None:
        _job_queue = BackgroundJobQueue()
    return _job_queue

def setup_job_handlers():
    """Set up job handlers for different job types"""
    queue = get_job_queue()
    
    # Payment processing handler
    def process_payment_confirmation(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment confirmation in background"""
        try:
            from payment_service import get_payment_service
            from services.confirmation_service import get_confirmation_service
            
            order_id = payload['order_id']
            payment_data = payload['payment_data']
            
            logger.info(f"Processing payment confirmation for order {order_id}")
            
            # Use sync version since we're in thread pool
            payment_service = get_payment_service()
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Process payment
                result = loop.run_until_complete(
                    payment_service.process_webhook_payment(order_id, payment_data)
                )
                
                if result.get('success'):
                    # Send notifications
                    confirmation_service = get_confirmation_service()
                    
                    # Get order details
                    from database import get_db_manager
                    db = get_db_manager()
                    order = db.get_order(order_id)
                    
                    if order:
                        order_data = {
                            'order_id': order_id,
                            'amount_usd': getattr(order, 'amount_usd', 0),
                            'payment_method': 'Cryptocurrency',
                            'transaction_id': payment_data.get('txid', 'N/A')
                        }
                        
                        loop.run_until_complete(
                            confirmation_service.send_payment_confirmation(
                                order.telegram_id, order_data
                            )
                        )
                
                return result
                
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Payment processing job failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # Domain registration handler
    def process_domain_registration(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process domain registration in background"""
        try:
            from payment_service import get_payment_service
            
            order_id = payload['order_id']
            telegram_id = payload['telegram_id']
            
            logger.info(f"Processing domain registration for order {order_id}")
            
            payment_service = get_payment_service()
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    payment_service._complete_domain_registration_sync(order_id)
                )
                
                return {'success': True, 'result': result}
                
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Domain registration job failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # Email notification handler
    def send_email_notification(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification in background"""
        try:
            from services.confirmation_service import get_confirmation_service
            
            notification_type = payload['type']
            telegram_id = payload['telegram_id']
            data = payload['data']
            
            logger.info(f"Sending {notification_type} email to user {telegram_id}")
            
            confirmation_service = get_confirmation_service()
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                if notification_type == 'payment_confirmation':
                    result = loop.run_until_complete(
                        confirmation_service.send_payment_confirmation(telegram_id, data)
                    )
                elif notification_type == 'domain_registration':
                    result = loop.run_until_complete(
                        confirmation_service.send_domain_registration_confirmation(telegram_id, data)
                    )
                else:
                    result = False
                
                return {'success': result}
                
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Email notification job failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # Register handlers
    queue.register_handler('payment_confirmation', process_payment_confirmation)
    queue.register_handler('domain_registration', process_domain_registration)
    queue.register_handler('email_notification', send_email_notification)
    
    logger.info("Job handlers registered successfully")

async def start_job_queue():
    """Start the background job queue"""
    queue = get_job_queue()
    setup_job_handlers()
    await queue.start()

async def stop_job_queue():
    """Stop the background job queue"""
    queue = get_job_queue()
    await queue.stop()

# Convenience functions for common job types
def queue_payment_confirmation(order_id: str, payment_data: Dict[str, Any]) -> str:
    """Queue a payment confirmation job"""
    queue = get_job_queue()
    return queue.add_job('payment_confirmation', {
        'order_id': order_id,
        'payment_data': payment_data
    }, priority=JobPriority.HIGH)

def queue_domain_registration(order_id: str, telegram_id: int) -> str:
    """Queue a domain registration job"""
    queue = get_job_queue()
    return queue.add_job('domain_registration', {
        'order_id': order_id,
        'telegram_id': telegram_id
    }, priority=JobPriority.HIGH)

def queue_email_notification(notification_type: str, telegram_id: int, data: Dict[str, Any]) -> str:
    """Queue an email notification job"""
    queue = get_job_queue()
    return queue.add_job('email_notification', {
        'type': notification_type,
        'telegram_id': telegram_id,
        'data': data
    }, priority=JobPriority.NORMAL)