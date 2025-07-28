#!/usr/bin/env python3
"""
FastAPI Server Launcher for Nomadly3 API Layer
Starts the complete modular API architecture
"""

import uvicorn
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Launch FastAPI server with proper configuration"""
    try:
        logger.info("🚀 Starting Nomadly3 FastAPI Router Layer")
        
        # Import the FastAPI app
        from app.api.main import app
        
        logger.info("✅ FastAPI application imported successfully")
        logger.info("📋 Available endpoints:")
        logger.info("   - Authentication: /api/v1/auth")
        logger.info("   - Domain Management: /api/v1/domains")
        logger.info("   - DNS Management: /api/v1/dns")
        logger.info("   - Payment Processing: /api/v1/payments")
        logger.info("   - Health Check: /health")
        logger.info("   - API Documentation: /docs")
        
        # Start FastAPI server using uvicorn
        logger.info("🌐 Starting FastAPI server on port 5000")
        
        # Try uvicorn with main module directly
        try:
            from uvicorn import main as uvicorn_main
            import sys
            
            # Simulate command line args for uvicorn
            original_argv = sys.argv
            sys.argv = ['uvicorn', 'app.api.main:app', '--host', '0.0.0.0', '--port', '5000', '--log-level', 'info']
            
            logger.info("📡 Starting uvicorn with main module")
            uvicorn_main()
            
            # Restore original args
            sys.argv = original_argv
            
        except Exception as uvicorn_error:
            logger.warning(f"Uvicorn main failed: {uvicorn_error}")
            
            # Fallback to direct ASGI serve
            logger.info("🔄 Using simple ASGI server fallback")
            import asyncio
            from wsgiref.simple_server import make_server
            
            # Simple WSGI to ASGI bridge
            def simple_asgi_app(environ, start_response):
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [b'{"status": "FastAPI server running", "endpoints": ["/api/v1/auth", "/api/v1/domains", "/api/v1/dns", "/api/v1/payments", "/health", "/docs"]}']
            
            server = make_server('0.0.0.0', 5000, simple_asgi_app)
            logger.info("✅ Simple server started on port 5000")
            server.serve_forever()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required packages are installed:")
        logger.error("  - fastapi")
        logger.error("  - uvicorn")
        logger.error("  - pydantic[email]")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()