#!/usr/bin/env python3
"""
Celery Worker for Nomadly2 Background Jobs
Handles domain registration, retry logic, and long-running tasks
"""

import os
import asyncio
import structlog
from datetime import datetime, timedelta
from celery import Celery
from celery.signals import worker_ready, worker_shutdown

# Configure structured logging
logger = structlog.get_logger()

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize Celery app
celery_app = Celery(
    'nomadly2_worker',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_worker']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_routes={
        'celery_worker.process_domain_registration': {'queue': 'domain_registration'},
        'celery_worker.retry_failed_registration': {'queue': 'retry_queue'},
        'celery_worker.send_status_notification': {'queue': 'notifications'},
    }
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_domain_registration(self, order_id: str, webhook_data: dict):
    """
    Background task for domain registration with automatic retry
    """
    try:
        logger.info(
            "celery_domain_registration_started",
            order_id=order_id,
            task_id=self.request.id,
            retry_count=self.request.retries
        )
        
        # Run async domain registration in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                _async_domain_registration(order_id, webhook_data)
            )
        finally:
            loop.close()
        
        if success:
            logger.info(
                "celery_domain_registration_completed",
                order_id=order_id,
                task_id=self.request.id
            )
            return {"status": "success", "order_id": order_id}
        else:
            raise Exception("Domain registration failed")
            
    except Exception as exc:
        logger.error(
            "celery_domain_registration_error",
            order_id=order_id,
            task_id=self.request.id,
            error=str(exc),
            retry_count=self.request.retries
        )
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = (2 ** self.request.retries) * 60  # 1min, 2min, 4min
            
            logger.info(
                "celery_retrying_domain_registration",
                order_id=order_id,
                retry_in_seconds=retry_delay,
                retry_count=self.request.retries + 1
            )
            
            # Send status notification
            send_status_notification.delay(
                order_id,
                f"Registration attempt {self.request.retries + 1} failed - retrying in {retry_delay//60} minutes..."
            )
            
            raise self.retry(exc=exc, countdown=retry_delay)
        else:
            # All retries exhausted
            logger.error(
                "celery_domain_registration_failed_permanently",
                order_id=order_id,
                task_id=self.request.id
            )
            
            # Queue for manual review
            queue_for_manual_review.delay(order_id, str(exc))
            
            # Notify user of failure
            send_status_notification.delay(
                order_id,
                "Registration failed after multiple attempts - support team notified"
            )
            
            return {"status": "failed", "order_id": order_id, "error": str(exc)}

@celery_app.task
def send_status_notification(order_id: str, message: str):
    """
    Send status notification to user
    """
    try:
        logger.info(
            "celery_sending_notification",
            order_id=order_id,
            message=message
        )
        
        # Run async notification in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(_async_send_notification(order_id, message))
        finally:
            loop.close()
            
        logger.info(
            "celery_notification_sent",
            order_id=order_id
        )
        
    except Exception as e:
        logger.error(
            "celery_notification_error",
            order_id=order_id,
            error=str(e)
        )

@celery_app.task
def queue_for_manual_review(order_id: str, reason: str):
    """
    Queue failed orders for manual admin review
    """
    try:
        logger.error(
            "manual_review_required",
            order_id=order_id,
            reason=reason,
            priority="high"
        )
        
        # Store in database for admin panel
        from database import get_db_manager
        db_manager = get_db_manager()
        
        # Add to admin notifications
        # This would integrate with admin panel system
        
        return {"status": "queued", "order_id": order_id}
        
    except Exception as e:
        logger.error(
            "manual_review_queue_error",
            order_id=order_id,
            error=str(e)
        )

@celery_app.task(bind=True)
def retry_failed_registration(self, order_id: str, original_error: str):
    """
    Retry a previously failed domain registration
    """
    try:
        logger.info(
            "celery_retry_registration",
            order_id=order_id,
            original_error=original_error
        )
        
        # Get original order data
        from database import get_db_manager
        db_manager = get_db_manager()
        
        session = db_manager.get_session()
        try:
            order = session.query(db_manager.Order).filter_by(order_id=order_id).first()
            if not order:
                raise Exception(f"Order {order_id} not found")
            
            # Retry the registration
            success = asyncio.run(_async_domain_registration(order_id, {}))
            
            if success:
                logger.info(
                    "celery_retry_successful",
                    order_id=order_id
                )
                return {"status": "success", "order_id": order_id}
            else:
                raise Exception("Retry failed")
                
        finally:
            session.close()
            
    except Exception as e:
        logger.error(
            "celery_retry_error",
            order_id=order_id,
            error=str(e)
        )
        raise

# Async helper functions
async def _async_domain_registration(order_id: str, webhook_data: dict):
    """Async wrapper for domain registration"""
    try:
        from payment_service import PaymentService
        from database import get_db_manager
        
        db_manager = get_db_manager()
        payment_service = PaymentService(db_manager)
        
        # Process domain registration
        success = await payment_service.complete_domain_registration(order_id, webhook_data)
        return success
        
    except Exception as e:
        logger.error(
            "async_domain_registration_error",
            order_id=order_id,
            error=str(e)
        )
        return False

async def _async_send_notification(order_id: str, message: str):
    """Async wrapper for sending notifications"""
    try:
        from telegram import Bot
        from database import get_db_manager
        import os
        
        # Get user telegram_id from order
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            order = session.query(db_manager.Order).filter_by(order_id=order_id).first()
            if order and order.telegram_id:
                bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
                await bot.send_message(
                    chat_id=order.telegram_id,
                    text=message
                )
        finally:
            session.close()
            
    except Exception as e:
        logger.error(
            "async_notification_error",
            order_id=order_id,
            error=str(e)
        )

# Worker lifecycle events
@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    logger.info("celery_worker_ready", worker_id=sender.hostname)

@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    logger.info("celery_worker_shutdown", worker_id=sender.hostname)

if __name__ == '__main__':
    celery_app.start()