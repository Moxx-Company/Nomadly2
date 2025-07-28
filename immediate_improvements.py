#!/usr/bin/env python3
"""
Immediate Improvements for Nomadly2
Implements immediate fixes using current dependencies
"""

import asyncio
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Setup enhanced logging without external dependencies
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class SimpleAsyncWrapper:
    """Simple async wrapper for sync API calls"""
    
    @staticmethod
    async def run_sync_in_executor(func, *args, **kwargs):
        """Run sync function in thread executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

class WebhookTimeoutHandler:
    """Add timeout handling to existing webhook server"""
    
    def __init__(self, timeout_seconds: int = 25):
        self.timeout_seconds = timeout_seconds
        self.processing_jobs = {}
        
    async def process_with_timeout(self, order_id: str, webhook_data: Dict[str, Any]):
        """Process webhook with timeout handling"""
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Processing webhook for order {order_id} with {self.timeout_seconds}s timeout")
            
            # Import existing payment service
            from payment_service import PaymentService
            
            payment_service = PaymentService()
            
            # Create timeout task
            timeout_task = asyncio.create_task(asyncio.sleep(self.timeout_seconds))
            
            # Create processing task
            processing_task = asyncio.create_task(
                payment_service.complete_domain_registration(order_id, webhook_data)
            )
            
            # Wait for first to complete
            done, pending = await asyncio.wait(
                [timeout_task, processing_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                
            if timeout_task in done:
                # Timeout occurred
                logger.warning(f"⏰ Webhook processing timeout for order {order_id}")
                
                # Queue for background processing
                await self._queue_for_background_processing(order_id, webhook_data)
                
                return {
                    "status": "timeout",
                    "message": "Processing queued for background completion",
                    "order_id": order_id
                }
            else:
                # Processing completed
                result = processing_task.result()
                duration = time.time() - start_time
                
                logger.info(f"✅ Webhook processed successfully for order {order_id} in {duration:.2f}s")
                
                return {
                    "status": "completed",
                    "message": "Domain registration completed",
                    "order_id": order_id,
                    "duration": duration
                }
                
        except Exception as e:
            logger.error(f"❌ Webhook processing error for order {order_id}: {e}")
            
            # Queue for retry
            await self._queue_for_background_processing(order_id, webhook_data)
            
            return {
                "status": "error", 
                "message": "Processing failed - queued for retry",
                "order_id": order_id,
                "error": str(e)
            }
    
    async def _queue_for_background_processing(self, order_id: str, webhook_data: Dict[str, Any]):
        """Queue order for background processing (simple file-based queue)"""
        try:
            import os
            
            # Create simple queue directory
            queue_dir = "background_queue"
            os.makedirs(queue_dir, exist_ok=True)
            
            # Write job file
            job_data = {
                "order_id": order_id,
                "webhook_data": webhook_data,
                "queued_at": datetime.utcnow().isoformat(),
                "attempts": 0
            }
            
            job_file = f"{queue_dir}/job_{order_id}_{int(time.time())}.json"
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            logger.info(f"📝 Queued job for background processing: {job_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to queue background job: {e}")

class EnhancedErrorHandling:
    """Enhanced error handling and retry logic"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = min(2 ** attempt, 60)  # Max 60 seconds
                    logger.info(f"🔄 Retry attempt {attempt} after {delay}s delay")
                    await asyncio.sleep(delay)
                
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✅ Function succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries:
                    break
        
        logger.error(f"❌ All {self.max_retries + 1} attempts failed")
        raise last_exception

class SimpleMetrics:
    """Simple metrics tracking without external dependencies"""
    
    def __init__(self):
        self.counters = {}
        self.timers = {}
        
    def increment(self, metric_name: str, value: int = 1):
        """Increment counter metric"""
        self.counters[metric_name] = self.counters.get(metric_name, 0) + value
        logger.info(f"📊 Metric {metric_name}: {self.counters[metric_name]}")
    
    def record_duration(self, metric_name: str, duration_ms: float):
        """Record duration metric"""
        if metric_name not in self.timers:
            self.timers[metric_name] = []
        
        self.timers[metric_name].append(duration_ms)
        
        # Keep only last 100 measurements
        if len(self.timers[metric_name]) > 100:
            self.timers[metric_name] = self.timers[metric_name][-100:]
        
        avg_duration = sum(self.timers[metric_name]) / len(self.timers[metric_name])
        logger.info(f"⏱️ {metric_name}: {duration_ms:.2f}ms (avg: {avg_duration:.2f}ms)")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "counters": self.counters.copy(),
            "timer_averages": {}
        }
        
        for metric, durations in self.timers.items():
            if durations:
                summary["timer_averages"][metric] = {
                    "avg_ms": sum(durations) / len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "count": len(durations)
                }
        
        return summary

# Global instances
webhook_timeout_handler = WebhookTimeoutHandler(timeout_seconds=25)
error_handler = EnhancedErrorHandling(max_retries=3)
simple_metrics = SimpleMetrics()

async def process_background_queue():
    """Simple background queue processor"""
    import os
    import glob
    
    queue_dir = "background_queue"
    if not os.path.exists(queue_dir):
        return
    
    job_files = glob.glob(f"{queue_dir}/job_*.json")
    
    for job_file in job_files:
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            order_id = job_data["order_id"]
            webhook_data = job_data["webhook_data"]
            attempts = job_data.get("attempts", 0)
            
            if attempts >= 3:
                logger.warning(f"⚠️ Job {order_id} exceeded max attempts, moving to failed")
                os.rename(job_file, job_file.replace("job_", "failed_"))
                continue
            
            logger.info(f"🔄 Processing background job: {order_id}")
            
            # Process the job
            from payment_service import PaymentService
            from database import get_db_manager
            
            db_manager = get_db_manager()
            payment_service = PaymentService(db_manager)
            
            success = await payment_service.complete_domain_registration(order_id, webhook_data)
            
            if success:
                logger.info(f"✅ Background job completed: {order_id}")
                os.remove(job_file)
                simple_metrics.increment("background_jobs_completed")
            else:
                logger.warning(f"⚠️ Background job failed: {order_id}")
                job_data["attempts"] = attempts + 1
                
                with open(job_file, 'w') as f:
                    json.dump(job_data, f, indent=2)
                
                simple_metrics.increment("background_jobs_failed")
            
        except Exception as e:
            logger.error(f"❌ Background job processing error: {e}")

async def run_immediate_improvements():
    """Run immediate improvements"""
    logger.info("🚀 Starting immediate improvements for Nomadly2")
    
    # Start background queue processor
    background_task = asyncio.create_task(background_queue_worker())
    
    logger.info("✅ Immediate improvements running")
    
    # Keep running
    try:
        await background_task
    except KeyboardInterrupt:
        logger.info("🛑 Stopping immediate improvements")
        background_task.cancel()

async def background_queue_worker():
    """Background worker for processing queued jobs"""
    while True:
        try:
            await process_background_queue()
            await asyncio.sleep(30)  # Process queue every 30 seconds
        except Exception as e:
            logger.error(f"❌ Background worker error: {e}")
            await asyncio.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    asyncio.run(run_immediate_improvements())