#!/usr/bin/env python3
"""
Simple Async Webhook Server for Nomadly2
Uses built-in Python libraries with async processing
"""

import asyncio
import json
import logging
import os
import sys
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AsyncWebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler with async processing"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_health_response()
        elif self.path == '/':
            self.send_status_response()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests asynchronously"""
        try:
            # Parse the path
            if '/webhook/blockbee/' in self.path:
                order_id = self.path.split('/webhook/blockbee/')[-1].split('?')[0]
                self.handle_blockbee_webhook(order_id)
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"POST handler error: {e}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def handle_blockbee_webhook(self, order_id: str):
        """Process BlockBee webhook"""
        try:
            # Get content length and read body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                webhook_data = json.loads(post_data.decode('utf-8'))
            else:
                # Parse query parameters for GET-style webhooks
                parsed_url = urlparse(self.path)
                webhook_data = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
            
            logger.info(f"Webhook received for order {order_id}: {webhook_data}")
            
            # Schedule async processing
            threading.Thread(
                target=self.process_payment_async,
                args=(order_id, webhook_data),
                daemon=True
            ).start()
            
            # Immediate response
            response = {
                "status": "received",
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Webhook processed successfully"
            }
            
            self.send_json_response(200, response)
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            self.send_error(500, f"Webhook error: {str(e)}")
    
    def process_payment_async(self, order_id: str, webhook_data: Dict[str, Any]):
        """Background payment processing"""
        try:
            logger.info(f"Processing payment for order {order_id}")
            
            # Import payment services
            sys.path.append(os.path.dirname(__file__))
            from payment_service import PaymentService
            from database import get_db_manager
            
            # Initialize services
            payment_service = PaymentService()
            db_manager = get_db_manager()
            
            # Process the payment
            success = payment_service.process_webhook_payment(order_id, webhook_data)
            
            if success:
                logger.info(f"Payment processed successfully for order {order_id}")
            else:
                logger.warning(f"Payment processing failed for order {order_id}")
                
        except Exception as e:
            logger.error(f"Background payment processing error for {order_id}: {e}")
    
    def send_health_response(self):
        """Send health check response"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "nomadly2-async-webhook",
            "version": "1.0.0"
        }
        self.send_json_response(200, health_data)
    
    def send_status_response(self):
        """Send server status"""
        status_data = {
            "message": "Nomadly2 Async Webhook Server",
            "status": "running",
            "endpoints": [
                "GET /health - Health check",
                "POST /webhook/blockbee/{order_id} - BlockBee payment webhook"
            ]
        }
        self.send_json_response(200, status_data)
    
    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override default logging to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP Server with threading support"""
    daemon_threads = True
    allow_reuse_address = True

def start_async_webhook_server():
    """Start the async webhook server"""
    host = "0.0.0.0"
    port = 8001  # Use 8001 to avoid conflict with Flask on 8000
    
    server = ThreadedHTTPServer((host, port), AsyncWebhookHandler)
    
    logger.info(f"Starting Nomadly2 Async Webhook Server on {host}:{port}")
    logger.info(f"Health check: http://{host}:{port}/health")
    logger.info(f"Webhook endpoint: http://{host}:{port}/webhook/blockbee/{{order_id}}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    start_async_webhook_server()