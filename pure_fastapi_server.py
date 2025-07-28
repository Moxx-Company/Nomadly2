#!/usr/bin/env python3
"""
Pure FastAPI-Compatible Server for Nomadly2
Uses only built-in Python libraries with FastAPI-like syntax
"""

import json
import logging
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FastAPIStyleHandler(BaseHTTPRequestHandler):
    """FastAPI-style HTTP handler with async processing"""
    
    def __init__(self, *args, **kwargs):
        # Initialize routes
        self.routes = {
            ('GET', '/'): self.root_handler,
            ('GET', '/health'): self.health_handler,
            ('GET', '/docs'): self.docs_handler,

            ('POST', '/webhook/blockbee'): self.webhook_handler
        }
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        self.handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self.handle_request('POST')
    
    def handle_request(self, method: str):
        """Route requests to appropriate handlers"""
        try:
            path = urlparse(self.path).path
            
            # Match exact routes first
            route_key = (method, path)
            if route_key in self.routes:
                self.routes[route_key]()
                return
            
            # Handle parameterized routes
            if (method == 'POST' or method == 'GET') and path.startswith('/webhook/blockbee/'):
                order_id = path.split('/webhook/blockbee/')[-1] if '/' in path.split('/webhook/blockbee/')[-1] else path.split('/webhook/blockbee/')[-1]
                self.webhook_handler(order_id)
                return
            
            # 404 for unmatched routes
            self.send_error_response(404, "Not Found")
            
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            self.send_error_response(500, f"Internal Server Error: {str(e)}")
    
    def root_handler(self):
        """Root endpoint - FastAPI style"""
        response = {
            "message": "Nomadly2 FastAPI-Style Webhook Server",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
        self.send_json_response(200, response)
    
    def health_handler(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "nomadly2-fastapi-style",
            "version": "1.0.0",
            "uptime_seconds": int(time.time() - getattr(self.server, 'start_time', time.time()))
        }
        self.send_json_response(200, response)
    
    def docs_handler(self):
        """API documentation endpoint"""
        docs = {
            "title": "Nomadly2 Webhook API",
            "version": "1.0.0",
            "description": "FastAPI-style webhook server for domain registration payments",
            "endpoints": [
                {
                    "path": "/",
                    "method": "GET",
                    "description": "Root endpoint with server info"
                },
                {
                    "path": "/health",
                    "method": "GET", 
                    "description": "Health check endpoint"
                },
                {
                    "path": "/webhook/blockbee/{order_id}",
                    "method": "POST",
                    "description": "BlockBee payment webhook endpoint",
                    "parameters": {
                        "order_id": "Payment order identifier",
                        "value": "Payment amount",
                        "coin": "Cryptocurrency used",
                        "confirmations": "Number of confirmations"
                    }
                }
            ]
        }
        self.send_json_response(200, docs)
    
    def webhook_handler(self, order_id: Optional[str] = None):
        """BlockBee webhook handler - FastAPI style"""
        try:
            # Extract order_id from URL if not provided
            if not order_id:
                path_parts = self.path.split('/')
                if 'blockbee' in path_parts:
                    blockbee_index = path_parts.index('blockbee')
                    if len(path_parts) > blockbee_index + 1:
                        order_id = path_parts[blockbee_index + 1].split('?')[0]
            
            if not order_id:
                self.send_error_response(400, "Missing order_id")
                return
            
            # Parse webhook data
            webhook_data = {}
            
            # Try to parse JSON body first
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    webhook_data = json.loads(post_data.decode('utf-8'))
            except:
                pass
            
            # Fallback to query parameters
            if not webhook_data:
                parsed_url = urlparse(self.path)
                webhook_data = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
            
            logger.info(f"Processing webhook for order {order_id}: {webhook_data}")
            
            # Validate required fields (FastAPI-style validation)
            required_fields = ['value', 'coin']
            missing_fields = [field for field in required_fields if field not in webhook_data]
            
            if missing_fields:
                self.send_error_response(422, {
                    "detail": f"Missing required fields: {missing_fields}",
                    "type": "validation_error"
                })
                return
            
            # Process webhook asynchronously (FastAPI background task style)
            threading.Thread(
                target=self.process_webhook_background,
                args=(order_id, webhook_data),
                daemon=True
            ).start()
            
            # Immediate response (FastAPI style)
            response = {
                "status": "accepted",
                "order_id": order_id,
                "message": "Webhook received and queued for processing",
                "timestamp": datetime.utcnow().isoformat(),
                "data_received": webhook_data
            }
            
            self.send_json_response(202, response)  # 202 Accepted
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            self.send_error_response(500, {
                "detail": f"Webhook processing failed: {str(e)}",
                "type": "processing_error"
            })
    
    def process_webhook_background(self, order_id: str, webhook_data: Dict[str, Any]):
        """Background webhook processing (FastAPI BackgroundTasks style)"""
        try:
            logger.info(f"Background processing started for order {order_id}")
            
            # Add current directory to Python path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # Import webhook processor
            try:
                import asyncio
                # Add nomadly_clean to path
                nomadly_path = os.path.join(current_dir, 'nomadly_clean')
                if nomadly_path not in sys.path:
                    sys.path.insert(0, nomadly_path)
                    
                from webhook_processor import WebhookProcessor
                processor = WebhookProcessor()
                
                # Process the payment with proper async handling
                success = asyncio.run(processor.process_payment(order_id, webhook_data))
                
                if success:
                    logger.info(f"✅ Payment processed successfully for order {order_id}")
                else:
                    logger.warning(f"⚠️ Payment processing failed for order {order_id}")
                    
            except ImportError as e:
                logger.error(f"Could not import webhook processor: {e}")
            except Exception as e:
                logger.error(f"Payment processing error: {e}")
                
        except Exception as e:
            logger.error(f"Background processing error for {order_id}: {e}")
    
    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response (FastAPI JSONResponse style)"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2, default=str)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, detail: Any):
        """Send error response (FastAPI HTTPException style)"""
        if isinstance(detail, str):
            error_data = {"detail": detail}
        else:
            error_data = detail if isinstance(detail, dict) else {"detail": str(detail)}
        
        error_data.update({
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self.send_json_response(status_code, error_data)
    
    def log_message(self, format, *args):
        """Override logging to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

class FastAPIStyleServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP Server (FastAPI uvicorn style)"""
    daemon_threads = True
    allow_reuse_address = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()

def create_app():
    """FastAPI app factory style function"""
    logger.info("Creating FastAPI-style application")
    return FastAPIStyleServer

def main():
    """Main function (uvicorn.run style)"""
    host = "0.0.0.0"
    port = 5000  # Changed to Replit public port for BlockBee webhooks
    
    server = FastAPIStyleServer((host, port), FastAPIStyleHandler)
    
    logger.info("=" * 60)
    logger.info("🚀 NOMADLY2 FASTAPI-STYLE WEBHOOK SERVER")
    logger.info("=" * 60)
    logger.info(f"📡 Server running on: http://{host}:{port}")
    logger.info(f"🏥 Health check: http://{host}:{port}/health")
    logger.info(f"📚 API docs: http://{host}:{port}/docs")
    logger.info(f"🎯 Webhook endpoint: http://{host}:{port}/webhook/blockbee/{{order_id}}")
    logger.info("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"💥 Server error: {e}")
    finally:
        server.shutdown()
        server.server_close()
        logger.info("✅ Server shutdown complete")

if __name__ == "__main__":
    main()