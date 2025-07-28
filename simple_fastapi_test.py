#!/usr/bin/env python3
"""
Simple FastAPI test server to verify functionality
"""
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Testing FastAPI server startup")
        
        # Import app
        from app.api.main import app
        logger.info("App imported successfully")
        
        # Direct uvicorn run
        logger.info("Starting uvicorn on port 5000")
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=5000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()