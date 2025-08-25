"""
Observability Service
Handles OpenTelemetry tracing, metrics collection, cost tracking, and monitoring.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
import json
from contextlib import asynccontextmanager
import psutil
import os
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import Counter, Histogram, UpDownCounter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

logger = structlog.get_logger()

class MetricType(Enum):
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"

class CostBucket(Enum):
    LOW = "low"  # < $1 per request
    MEDIUM = "medium"  # $1-10 per request
    HIGH = "high"  # > $10 per request

@dataclass
class CostMetrics:
    """Cost tracking metrics."""
    user_id: str
    operation: str
    cost_usd: float
    tokens_used: int
    model: str
    timestamp: datetime
    bucket: CostBucket

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics."""
    operation: str
    duration_ms: float
    success: bool
    error_type: Optional[str]
    timestamp: datetime
    user_id: Optional[str]

@dataclass
class ResourceUsage:
    """System resource usage metrics."""
    cpu_percent: float
    memory_percent: float
    memory_mb: int
    disk_usage_percent: float
    active_connections: int
    timestamp: datetime

class ObservabilityService:
    """Service for observability, monitoring, and cost tracking."""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)
        
        # Initialize metrics
        self.request_counter = self.meter.create_counter(
            name="requests_total",
            description="Total number of requests"
        )
        self.request_duration = self.meter.create_histogram(
            name="request_duration_seconds",
            description="Request duration in seconds"
        )
        self.error_counter = self.meter.create_counter(
            name="errors_total",
            description="Total number of errors"
        )
        self.cost_counter = self.meter.create_counter(
            name="cost_usd_total",
            description="Total cost in USD"
        )
        self.token_counter = self.meter.create_counter(
            name="tokens_used_total",
            description="Total tokens used"
        )
        self.active_users = self.meter.create_up_down_counter(
            name="active_users",
            description="Number of active users"
        )
        
        # Cost tracking
        self.cost_metrics: List[CostMetrics] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.resource_usage: List[ResourceUsage] = []
        
        # Concurrency limits
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
        self.max_cost_per_user_per_day = float(os.getenv("MAX_COST_PER_USER_PER_DAY", "50.0"))
        self.max_tokens_per_request = int(os.getenv("MAX_TOKENS_PER_REQUEST", "10000"))
        
        # Initialize Sentry
        self._setup_sentry()
        
        # Initialize OpenTelemetry
        self._setup_opentelemetry()
    
    def _setup_sentry(self):
        """Initialize Sentry for error tracking."""
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=os.getenv("ENVIRONMENT", "development"),
                integrations=[
                    FastApiIntegration(),
                    RedisIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
                profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
            )
            self.logger.info("Sentry initialized", dsn=sentry_dsn)
    
    def _setup_opentelemetry(self):
        """Initialize OpenTelemetry tracing and metrics."""
        # Create resource
        resource = Resource.create({
            "service.name": "health-wellness-orchestrator",
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        })
        
        # Setup tracing
        trace_provider = TracerProvider(resource=resource)
        jaeger_exporter = JaegerExporter(
            agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
            agent_port=int(os.getenv("JAEGER_PORT", "6831")),
        )
        trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        trace.set_tracer_provider(trace_provider)
        
        # Setup metrics
        prometheus_exporter = PrometheusExporter()
        metric_reader = PeriodicExportingMetricReader(prometheus_exporter)
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        
        self.logger.info("OpenTelemetry initialized")
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, user_id: Optional[str] = None, 
                            attributes: Optional[Dict[str, Any]] = None):
        """Context manager for tracing operations."""
        start_time = time.time()
        span = self.tracer.start_span(operation_name)
        
        if user_id:
            span.set_attribute("user.id", user_id)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            duration = time.time() - start_time
            span.set_attribute("duration", duration)
            span.end()
            
            # Record performance metrics
            await self.record_performance_metrics(
                operation_name, duration * 1000, True, None, user_id
            )
    
    async def record_cost_metrics(self, user_id: str, operation: str, cost_usd: float, 
                                tokens_used: int, model: str):
        """Record cost metrics for AI operations."""
        timestamp = datetime.now()
        
        # Determine cost bucket
        if cost_usd < 1.0:
            bucket = CostBucket.LOW
        elif cost_usd < 10.0:
            bucket = CostBucket.MEDIUM
        else:
            bucket = CostBucket.HIGH
        
        cost_metric = CostMetrics(
            user_id=user_id,
            operation=operation,
            cost_usd=cost_usd,
            tokens_used=tokens_used,
            model=model,
            timestamp=timestamp,
            bucket=bucket
        )
        
        self.cost_metrics.append(cost_metric)
        
        # Update OpenTelemetry metrics
        self.cost_counter.add(cost_usd, {"user_id": user_id, "operation": operation, "model": model})
        self.token_counter.add(tokens_used, {"user_id": user_id, "operation": operation, "model": model})
        
        # Check cost limits
        await self._check_cost_limits(user_id, cost_usd)
        
        self.logger.info("Cost metrics recorded", 
                        user_id=user_id, operation=operation, cost_usd=cost_usd, 
                        tokens_used=tokens_used, model=model)
    
    async def record_performance_metrics(self, operation: str, duration_ms: float, 
                                       success: bool, error_type: Optional[str] = None,
                                       user_id: Optional[str] = None):
        """Record performance metrics."""
        timestamp = datetime.now()
        
        perf_metric = PerformanceMetrics(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            error_type=error_type,
            timestamp=timestamp,
            user_id=user_id
        )
        
        self.performance_metrics.append(perf_metric)
        
        # Update OpenTelemetry metrics
        self.request_counter.add(1, {"operation": operation, "success": str(success)})
        self.request_duration.record(duration_ms / 1000, {"operation": operation})
        
        if not success:
            self.error_counter.add(1, {"operation": operation, "error_type": error_type or "unknown"})
    
    async def record_resource_usage(self):
        """Record system resource usage metrics."""
        timestamp = datetime.now()
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get active connections (mock for now)
        active_connections = len(psutil.net_connections())
        
        resource_usage = ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=int(memory.used / 1024 / 1024),
            disk_usage_percent=disk.percent,
            active_connections=active_connections,
            timestamp=timestamp
        )
        
        self.resource_usage.append(resource_usage)
        
        # Update OpenTelemetry metrics
        self.meter.create_observable_gauge(
            name="cpu_usage_percent",
            description="CPU usage percentage",
            callbacks=[lambda: [cpu_percent]]
        )
        
        self.meter.create_observable_gauge(
            name="memory_usage_mb",
            description="Memory usage in MB",
            callbacks=[lambda: [resource_usage.memory_mb]]
        )
        
        self.logger.debug("Resource usage recorded", 
                         cpu_percent=cpu_percent, memory_percent=memory.percent,
                         memory_mb=resource_usage.memory_mb, disk_percent=disk.percent)
    
    async def _check_cost_limits(self, user_id: str, cost_usd: float):
        """Check if user has exceeded cost limits."""
        today = datetime.now().date()
        daily_cost = sum(
            metric.cost_usd for metric in self.cost_metrics
            if metric.user_id == user_id and metric.timestamp.date() == today
        )
        
        if daily_cost > self.max_cost_per_user_per_day:
            self.logger.warning("User exceeded daily cost limit", 
                              user_id=user_id, daily_cost=daily_cost, 
                              limit=self.max_cost_per_user_per_day)
            
            # In production, this would trigger alerts or rate limiting
            raise ValueError(f"Daily cost limit exceeded: ${daily_cost:.2f} > ${self.max_cost_per_user_per_day}")
    
    async def get_user_cost_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get cost summary for a user."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        user_costs = [
            metric for metric in self.cost_metrics
            if metric.user_id == user_id and metric.timestamp >= cutoff_date
        ]
        
        total_cost = sum(metric.cost_usd for metric in user_costs)
        total_tokens = sum(metric.tokens_used for metric in user_costs)
        
        # Group by operation
        operation_costs = {}
        for metric in user_costs:
            if metric.operation not in operation_costs:
                operation_costs[metric.operation] = {"cost": 0, "tokens": 0}
            operation_costs[metric.operation]["cost"] += metric.cost_usd
            operation_costs[metric.operation]["tokens"] += metric.tokens_used
        
        # Group by model
        model_costs = {}
        for metric in user_costs:
            if metric.model not in model_costs:
                model_costs[metric.model] = {"cost": 0, "tokens": 0}
            model_costs[metric.model]["cost"] += metric.cost_usd
            model_costs[metric.model]["tokens"] += metric.tokens_used
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "operation_breakdown": operation_costs,
            "model_breakdown": model_costs,
            "daily_average": total_cost / days if days > 0 else 0,
            "cost_limit": self.max_cost_per_user_per_day,
            "limit_remaining": max(0, self.max_cost_per_user_per_day - total_cost)
        }
    
    async def get_performance_summary(self, operation: Optional[str] = None, 
                                    hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for operations."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metrics = [
            metric for metric in self.performance_metrics
            if metric.timestamp >= cutoff_time and (operation is None or metric.operation == operation)
        ]
        
        if not metrics:
            return {
                "operation": operation,
                "period_hours": hours,
                "total_requests": 0,
                "success_rate": 0,
                "avg_duration_ms": 0,
                "error_count": 0
            }
        
        total_requests = len(metrics)
        successful_requests = sum(1 for m in metrics if m.success)
        error_count = total_requests - successful_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        avg_duration = sum(m.duration_ms for m in metrics) / total_requests
        
        # Error breakdown
        error_types = {}
        for metric in metrics:
            if not metric.success and metric.error_type:
                error_types[metric.error_type] = error_types.get(metric.error_type, 0) + 1
        
        return {
            "operation": operation,
            "period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_count": error_count,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "error_breakdown": error_types
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        if not self.resource_usage:
            return {"status": "unknown", "message": "No resource data available"}
        
        latest = self.resource_usage[-1]
        
        # Determine health status
        if latest.cpu_percent > 90 or latest.memory_percent > 90:
            status = "critical"
        elif latest.cpu_percent > 70 or latest.memory_percent > 70:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "timestamp": latest.timestamp.isoformat(),
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "memory_mb": latest.memory_mb,
            "disk_usage_percent": latest.disk_usage_percent,
            "active_connections": latest.active_connections,
            "uptime_seconds": time.time() - os.path.getctime('/proc/uptime') if os.path.exists('/proc/uptime') else 0
        }
    
    async def cleanup_old_metrics(self, days_to_keep: int = 30):
        """Clean up old metrics data."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean up cost metrics
        original_cost_count = len(self.cost_metrics)
        self.cost_metrics = [
            metric for metric in self.cost_metrics
            if metric.timestamp >= cutoff_date
        ]
        
        # Clean up performance metrics
        original_perf_count = len(self.performance_metrics)
        self.performance_metrics = [
            metric for metric in self.performance_metrics
            if metric.timestamp >= cutoff_date
        ]
        
        # Clean up resource usage (keep more granular data for shorter period)
        resource_cutoff = datetime.now() - timedelta(days=7)
        original_resource_count = len(self.resource_usage)
        self.resource_usage = [
            usage for usage in self.resource_usage
            if usage.timestamp >= resource_cutoff
        ]
        
        self.logger.info("Cleaned up old metrics", 
                        cost_metrics_removed=original_cost_count - len(self.cost_metrics),
                        perf_metrics_removed=original_perf_count - len(self.performance_metrics),
                        resource_metrics_removed=original_resource_count - len(self.resource_usage))
    
    async def export_metrics_for_grafana(self) -> Dict[str, Any]:
        """Export metrics in format suitable for Grafana dashboards."""
        return {
            "cost_metrics": {
                "total_cost_usd": sum(m.cost_usd for m in self.cost_metrics),
                "total_tokens": sum(m.tokens_used for m in self.cost_metrics),
                "cost_by_bucket": {
                    bucket.value: sum(m.cost_usd for m in self.cost_metrics if m.bucket == bucket)
                    for bucket in CostBucket
                },
                "cost_by_operation": {},
                "cost_by_model": {},
                "daily_costs": {}
            },
            "performance_metrics": {
                "total_requests": len(self.performance_metrics),
                "success_rate": sum(1 for m in self.performance_metrics if m.success) / len(self.performance_metrics) if self.performance_metrics else 0,
                "avg_duration_ms": sum(m.duration_ms for m in self.performance_metrics) / len(self.performance_metrics) if self.performance_metrics else 0,
                "errors_by_type": {},
                "requests_by_operation": {}
            },
            "resource_usage": {
                "current": self.resource_usage[-1].__dict__ if self.resource_usage else {},
                "history": [usage.__dict__ for usage in self.resource_usage[-100:]]  # Last 100 readings
            },
            "limits": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "max_cost_per_user_per_day": self.max_cost_per_user_per_day,
                "max_tokens_per_request": self.max_tokens_per_request
            }
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring."""
        self.logger.info("Starting observability monitoring")
        
        while True:
            try:
                await self.record_resource_usage()
                await asyncio.sleep(60)  # Record every minute
            except Exception as e:
                self.logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(60)
