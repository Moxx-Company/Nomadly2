#!/usr/bin/env python3
"""
Enhanced Monitoring and Metrics for Nomadly2
Structured logging, Prometheus metrics, and comprehensive observability
"""

import time
import psutil
import structlog
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps
from collections import defaultdict, deque
from dataclasses import dataclass, asdict

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@dataclass
class MetricData:
    """Structured metric data"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: str  # counter, gauge, histogram

@dataclass
class PerformanceMetrics:
    """Performance tracking data"""
    function_name: str
    duration_ms: float
    start_time: datetime
    end_time: datetime
    success: bool
    error_message: Optional[str] = None

class MetricsCollector:
    """Centralized metrics collection and storage"""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        key = self._make_key(name, labels or {})
        self.counters[key] += value
        
        metric = MetricData(
            name=name,
            value=self.counters[key],
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type="counter"
        )
        
        self.metrics[name].append(metric)
        
        logger.info(
            "metric_counter_incremented",
            metric_name=name,
            value=value,
            total=self.counters[key],
            labels=labels
        )
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        key = self._make_key(name, labels or {})
        self.gauges[key] = value
        
        metric = MetricData(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type="gauge"
        )
        
        self.metrics[name].append(metric)
        
        logger.debug(
            "metric_gauge_set",
            metric_name=name,
            value=value,
            labels=labels
        )
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        key = self._make_key(name, labels or {})
        self.histograms[key].append(value)
        
        metric = MetricData(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type="histogram"
        )
        
        self.metrics[name].append(metric)
        
        logger.debug(
            "metric_histogram_recorded",
            metric_name=name,
            value=value,
            labels=labels
        )
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Create unique key for metric with labels"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}|{label_str}"
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histogram_counts": {k: len(v) for k, v in self.histograms.items()},
            "total_metrics": sum(len(v) for v in self.metrics.values()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return summary

# Global metrics collector instance
metrics = MetricsCollector()

class PerformanceMonitor:
    """Performance monitoring and tracking"""
    
    def __init__(self):
        self.performance_data: deque = deque(maxlen=1000)
        
    def record_performance(self, perf_data: PerformanceMetrics):
        """Record performance data"""
        self.performance_data.append(perf_data)
        
        # Record as histogram metric
        metrics.record_histogram(
            "function_duration_ms",
            perf_data.duration_ms,
            labels={
                "function": perf_data.function_name,
                "success": str(perf_data.success)
            }
        )
        
        logger.info(
            "performance_recorded",
            function=perf_data.function_name,
            duration_ms=perf_data.duration_ms,
            success=perf_data.success,
            error=perf_data.error_message
        )
    
    def get_function_stats(self, function_name: str) -> Dict[str, Any]:
        """Get performance statistics for a function"""
        function_data = [
            p for p in self.performance_data 
            if p.function_name == function_name
        ]
        
        if not function_data:
            return {"error": f"No data for function {function_name}"}
        
        durations = [p.duration_ms for p in function_data]
        successes = sum(1 for p in function_data if p.success)
        
        return {
            "function_name": function_name,
            "total_calls": len(function_data),
            "success_rate": successes / len(function_data),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "recent_errors": [
                p.error_message for p in function_data[-10:] 
                if not p.success and p.error_message
            ]
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(function_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        name = function_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            start_timestamp = time.time()
            
            try:
                result = await func(*args, **kwargs)
                success = True
                error_message = None
            except Exception as e:
                result = None
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = datetime.utcnow()
                duration_ms = (time.time() - start_timestamp) * 1000
                
                perf_data = PerformanceMetrics(
                    function_name=name,
                    duration_ms=duration_ms,
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    error_message=error_message
                )
                
                performance_monitor.record_performance(perf_data)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            start_timestamp = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error_message = None
            except Exception as e:
                result = None
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = datetime.utcnow()
                duration_ms = (time.time() - start_timestamp) * 1000
                
                perf_data = PerformanceMetrics(
                    function_name=name,
                    duration_ms=duration_ms,
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    error_message=error_message
                )
                
                performance_monitor.record_performance(perf_data)
            
            return result
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__await__'):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            except:
                network_stats = {}
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            system_metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "percent_used": memory.percent,
                    "process_rss_mb": process_memory.rss / (1024**2),
                    "process_vms_mb": process_memory.vms / (1024**2)
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "percent_used": (disk.used / disk.total) * 100
                },
                "network": network_stats
            }
            
            # Record as gauge metrics
            metrics.set_gauge("system_cpu_percent", cpu_percent)
            metrics.set_gauge("system_memory_percent", memory.percent)
            metrics.set_gauge("system_disk_percent", (disk.used / disk.total) * 100)
            metrics.set_gauge("process_memory_mb", process_memory.rss / (1024**2))
            
            return system_metrics
            
        except Exception as e:
            logger.error(
                "system_metrics_error",
                error=str(e)
            )
            return {"error": str(e)}
    
    def log_system_status(self):
        """Log current system status"""
        metrics_data = self.get_system_metrics()
        
        logger.info(
            "system_status",
            **metrics_data
        )

# Global system monitor
system_monitor = SystemMonitor()

class BusinessMetricsTracker:
    """Track business-specific metrics for domain registration"""
    
    def __init__(self):
        self.business_metrics = defaultdict(int)
        
    def track_domain_registration_started(self, domain: str, payment_method: str):
        """Track when domain registration starts"""
        metrics.increment_counter(
            "domain_registration_started",
            labels={"payment_method": payment_method}
        )
        
        logger.info(
            "business_metric_domain_registration_started",
            domain=domain,
            payment_method=payment_method
        )
    
    def track_domain_registration_completed(self, domain: str, duration_ms: float):
        """Track successful domain registration"""
        metrics.increment_counter("domain_registration_completed")
        metrics.record_histogram("domain_registration_duration_ms", duration_ms)
        
        logger.info(
            "business_metric_domain_registration_completed",
            domain=domain,
            duration_ms=duration_ms
        )
    
    def track_domain_registration_failed(self, domain: str, error_type: str):
        """Track failed domain registration"""
        metrics.increment_counter(
            "domain_registration_failed",
            labels={"error_type": error_type}
        )
        
        logger.error(
            "business_metric_domain_registration_failed",
            domain=domain,
            error_type=error_type
        )
    
    def track_payment_received(self, amount: float, cryptocurrency: str):
        """Track payment received"""
        metrics.increment_counter(
            "payments_received",
            labels={"cryptocurrency": cryptocurrency}
        )
        metrics.record_histogram("payment_amount_usd", amount)
        
        logger.info(
            "business_metric_payment_received",
            amount=amount,
            cryptocurrency=cryptocurrency
        )
    
    def track_api_call(self, api_name: str, success: bool, duration_ms: float):
        """Track external API calls"""
        status = "success" if success else "failed"
        
        metrics.increment_counter(
            "api_calls_total",
            labels={"api": api_name, "status": status}
        )
        metrics.record_histogram(
            "api_call_duration_ms",
            duration_ms,
            labels={"api": api_name}
        )
        
        logger.info(
            "business_metric_api_call",
            api=api_name,
            success=success,
            duration_ms=duration_ms
        )

# Global business metrics tracker
business_metrics = BusinessMetricsTracker()

def get_comprehensive_health_report() -> Dict[str, Any]:
    """Generate comprehensive health and metrics report"""
    try:
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "nomadly2-domain-bot",
            "version": "2.0.0",
            "status": "healthy",
            "system_metrics": system_monitor.get_system_metrics(),
            "application_metrics": metrics.get_metrics_summary(),
            "performance_summary": {
                "total_function_calls": len(performance_monitor.performance_data),
                "recent_performance": [
                    asdict(p) for p in list(performance_monitor.performance_data)[-5:]
                ]
            }
        }
        
        logger.info(
            "health_report_generated",
            total_metrics=report["application_metrics"]["total_metrics"],
            system_status="healthy"
        )
        
        return report
        
    except Exception as e:
        logger.error(
            "health_report_error",
            error=str(e)
        )
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }

# Export monitoring utilities
__all__ = [
    "logger",
    "metrics",
    "performance_monitor", 
    "system_monitor",
    "business_metrics",
    "monitor_performance",
    "get_comprehensive_health_report"
]