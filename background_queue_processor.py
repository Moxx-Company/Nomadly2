#!/usr/bin/env python3
"""
Background Queue Processor for Nomadly2
Simple file-based queue system for handling domain registration timeouts
"""

import asyncio
import json
import os
import glob
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackgroundQueueProcessor:
    """Processes queued domain registration jobs"""
    
    def __init__(self, queue_dir: str = "background_queue", max_attempts: int = 3):
        self.queue_dir = queue_dir
        self.max_attempts = max_attempts
        self.processing = False
        
        # Create queue directory
        os.makedirs(queue_dir, exist_ok=True)
        os.makedirs(f"{queue_dir}/failed", exist_ok=True)
        os.makedirs(f"{queue_dir}/completed", exist_ok=True)
        
    async def start_processing(self):
        """Start the background queue processor"""
        logger.info("🚀 Starting background queue processor")
        self.processing = True
        
        try:
            while self.processing:
                await self.process_queue()
                await asyncio.sleep(30)  # Process every 30 seconds
        except Exception as e:
            logger.error(f"❌ Background processor error: {e}")
        finally:
            logger.info("🛑 Background queue processor stopped")
    
    def stop_processing(self):
        """Stop the background queue processor"""
        self.processing = False
    
    async def process_queue(self):
        """Process all jobs in the queue"""
        job_files = glob.glob(f"{self.queue_dir}/job_*.json")
        
        if not job_files:
            return
        
        logger.info(f"📋 Processing {len(job_files)} queued jobs")
        
        for job_file in job_files:
            try:
                await self._process_job_file(job_file)
            except Exception as e:
                logger.error(f"❌ Error processing job file {job_file}: {e}")
    
    async def _process_job_file(self, job_file: str):
        """Process individual job file"""
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            order_id = job_data["order_id"]
            webhook_data = job_data["webhook_data"]
            attempts = job_data.get("attempts", 0)
            queued_at = job_data.get("queued_at")
            
            logger.info(f"🔄 Processing job {order_id} (attempt {attempts + 1})")
            
            # Check if max attempts exceeded
            if attempts >= self.max_attempts:
                logger.warning(f"⚠️ Job {order_id} exceeded max attempts ({self.max_attempts})")
                await self._move_to_failed(job_file, job_data)
                return
            
            # Check if job is too old (older than 24 hours)
            if queued_at:
                queued_time = datetime.fromisoformat(queued_at)
                if datetime.utcnow() - queued_time > timedelta(hours=24):
                    logger.warning(f"⚠️ Job {order_id} is too old, moving to failed")
                    await self._move_to_failed(job_file, job_data)
                    return
            
            # Process the domain registration
            success = await self._process_domain_registration(order_id, webhook_data)
            
            if success:
                logger.info(f"✅ Job {order_id} completed successfully")
                await self._move_to_completed(job_file, job_data)
                
                # Send success notification to user
                await self._notify_user_success(order_id, webhook_data)
                
            else:
                logger.warning(f"⚠️ Job {order_id} failed, updating attempts")
                
                # Update attempts and retry later
                job_data["attempts"] = attempts + 1
                job_data["last_attempt"] = datetime.utcnow().isoformat()
                
                with open(job_file, 'w') as f:
                    json.dump(job_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error processing job file {job_file}: {e}")
    
    async def _process_domain_registration(self, order_id: str, webhook_data: Dict[str, Any]) -> bool:
        """Process domain registration with enhanced error handling and recovery"""
        from enhanced_error_recovery import with_error_recovery, ErrorCategory, ErrorSeverity, error_recovery
        
        @with_error_recovery(ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.HIGH, max_retries=2)
        async def _process_internal():
            # Import payment service
            from payment_service import PaymentService
            
            payment_service = PaymentService()
            
            # Add timeout to prevent hanging
            try:
                result = await asyncio.wait_for(
                    payment_service.complete_domain_registration(order_id, webhook_data),
                    timeout=300  # 5 minutes timeout
                )
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Domain registration timeout for order {order_id}")
                return False
        
        return await _process_internal()
    
    async def _notify_user_success(self, order_id: str, webhook_data: Dict[str, Any]):
        """Notify user of successful background processing"""
        try:
            # Get order details to find telegram_id
            from database import get_db_manager
            
            db_manager = get_db_manager()
            session = db_manager.get_session()
            
            try:
                order = session.query(db_manager.Order).filter_by(order_id=order_id).first()
                
                if order and order.telegram_id:
                    from telegram import Bot
                    import os
                    
                    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
                    
                    # Get domain name from service data
                    service_data = order.service_data or {}
                    domain_name = service_data.get("domain_name", "your domain")
                    
                    message = f"🎉 Great news! Domain registration for {domain_name} has been completed successfully!"
                    
                    await bot.send_message(
                        chat_id=order.telegram_id,
                        text=message
                    )
                    
                    logger.info(f"📱 Success notification sent for order {order_id}")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"❌ Failed to notify user for order {order_id}: {e}")
    
    async def _move_to_failed(self, job_file: str, job_data: Dict[str, Any]):
        """Move job to failed directory"""
        try:
            filename = os.path.basename(job_file)
            failed_path = f"{self.queue_dir}/failed/{filename}"
            
            # Add failure metadata
            job_data["failed_at"] = datetime.utcnow().isoformat()
            job_data["status"] = "failed"
            
            with open(failed_path, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            os.remove(job_file)
            
            logger.info(f"📁 Moved failed job to {failed_path}")
            
        except Exception as e:
            logger.error(f"❌ Error moving job to failed: {e}")
    
    async def _move_to_completed(self, job_file: str, job_data: Dict[str, Any]):
        """Move job to completed directory"""
        try:
            filename = os.path.basename(job_file)
            completed_path = f"{self.queue_dir}/completed/{filename}"
            
            # Add completion metadata
            job_data["completed_at"] = datetime.utcnow().isoformat()
            job_data["status"] = "completed"
            
            with open(completed_path, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            os.remove(job_file)
            
            logger.info(f"📁 Moved completed job to {completed_path}")
            
        except Exception as e:
            logger.error(f"❌ Error moving job to completed: {e}")
    
    def queue_job(self, order_id: str, webhook_data: Dict[str, Any]) -> str:
        """Queue a new job for background processing"""
        try:
            job_data = {
                "order_id": order_id,
                "webhook_data": webhook_data,
                "queued_at": datetime.utcnow().isoformat(),
                "attempts": 0,
                "status": "queued"
            }
            
            job_file = f"{self.queue_dir}/job_{order_id}_{int(time.time())}.json"
            
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            logger.info(f"📝 Queued job: {job_file}")
            return job_file
            
        except Exception as e:
            logger.error(f"❌ Error queuing job: {e}")
            raise
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            queued_jobs = len(glob.glob(f"{self.queue_dir}/job_*.json"))
            failed_jobs = len(glob.glob(f"{self.queue_dir}/failed/job_*.json"))
            completed_jobs = len(glob.glob(f"{self.queue_dir}/completed/job_*.json"))
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "queued": queued_jobs,
                "failed": failed_jobs,
                "completed": completed_jobs,
                "total": queued_jobs + failed_jobs + completed_jobs,
                "processing": self.processing
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting queue status: {e}")
            return {"error": str(e)}

# Global queue processor instance
queue_processor = BackgroundQueueProcessor()

async def main():
    """Main function to run the background queue processor"""
    try:
        logger.info("🚀 Starting Nomadly2 Background Queue Processor")
        await queue_processor.start_processing()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping background queue processor")
        queue_processor.stop_processing()

if __name__ == "__main__":
    asyncio.run(main())