#!/usr/bin/env python3
"""
Simple Monitoring System without External Dependencies
Compatible version of enhanced monitoring for current environment
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class SimpleMetrics:
    """Simple metrics without external dependencies"""
    
    def __init__(self):
        self.counters = {}
        self.timers = {}
        
    def increment(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        key = f"{name}|{labels}" if labels else name
        self.counters[key] = self.counters.get(key, 0) + value
        logger.info(f"📊 {name}: {self.counters[key]}")
    
    def record_duration(self, name: str, duration_ms: float, labels: Dict[str, str] = None):
        key = f"{name}|{labels}" if labels else name
        if key not in self.timers:
            self.timers[key] = []
        
        self.timers[key].append(duration_ms)
        if len(self.timers[key]) > 100:
            self.timers[key] = self.timers[key][-100:]
        
        avg = sum(self.timers[key]) / len(self.timers[key])
        logger.info(f"⏱️ {name}: {duration_ms:.2f}ms (avg: {avg:.2f}ms)")

def simple_performance_monitor(func_name: str = None):
    """Simple performance monitoring decorator"""
    def decorator(func):
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                simple_metrics.record_duration(name, duration_ms, {"success": str(success)})
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                simple_metrics.record_duration(name, duration_ms, {"success": str(success)})
            
            return result
        
        return async_wrapper if hasattr(func, '__await__') else sync_wrapper
    return decorator

# Global metrics instance
simple_metrics = SimpleMetrics()

# Export for compatibility
monitor_performance = simple_performance_monitor
business_metrics = simple_metrics

def get_health_report() -> Dict[str, Any]:
    """Get simple health report"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "metrics": {
            "counters": simple_metrics.counters,
            "timer_count": len(simple_metrics.timers)
        }
    }

logger.info("✅ Simple monitoring system initialized")
