#!/usr/bin/env python3
"""
Advanced Metrics Collection and Logging System
Comprehensive monitoring and analytics for multi-agent coordination
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
from contextlib import contextmanager

# Configure logging with multiple handlers
def setup_advanced_logging():
    """Set up comprehensive logging system."""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Main logger
    logger = logging.getLogger("coordination_system")
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler for all messages
    file_handler = logging.FileHandler(logs_dir / "coordination_system.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Error file handler
    error_handler = logging.FileHandler(logs_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Performance file handler
    performance_handler = logging.FileHandler(logs_dir / "performance.log")
    performance_handler.setLevel(logging.DEBUG)
    performance_handler.addFilter(lambda record: "PERF" in record.getMessage())
    performance_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(performance_handler)
    
    return logger

# Set up logging
logger = setup_advanced_logging()

@dataclass
class MetricEvent:
    """Individual metric event."""
    timestamp: str
    category: str
    metric_name: str
    value: float
    unit: str
    agent_id: Optional[str] = None
    operation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PerformanceMetric:
    """Performance measurement."""
    operation_name: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    agent_id: Optional[str] = None
    error_message: Optional[str] = None
    memory_delta_mb: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class MetricsCollector:
    """Advanced metrics collection and analysis system."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.metrics_dir = self.project_root / "metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Metric storage
        self.events = []
        self.performance_metrics = []
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        
        # Collection state
        self.collecting = False
        self.collection_thread = None
        self.flush_interval = 30  # seconds
        
        # Performance tracking
        self.active_operations = {}
        self.operation_stats = defaultdict(list)
        
        logger.info("📊 Metrics collector initialized")
    
    def start_collection(self):
        """Start continuous metrics collection."""
        
        if self.collecting:
            logger.warning("Metrics collection already running")
            return
        
        self.collecting = True
        
        def collection_loop():
            while self.collecting:
                try:
                    self._collect_system_metrics()
                    self._flush_metrics()
                    time.sleep(self.flush_interval)
                except Exception as e:
                    logger.error(f"Error in metrics collection loop: {e}")
        
        self.collection_thread = threading.Thread(target=collection_loop, daemon=True)
        self.collection_thread.start()
        
        logger.info("📈 Started continuous metrics collection")
    
    def stop_collection(self):
        """Stop metrics collection and flush remaining data."""
        
        self.collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        self._flush_metrics()
        logger.info("📉 Stopped metrics collection")
    
    def record_event(self, category: str, metric_name: str, value: float, 
                    unit: str = "count", agent_id: Optional[str] = None, 
                    operation_id: Optional[str] = None, **metadata):
        """Record a metric event."""
        
        event = MetricEvent(
            timestamp=datetime.now().isoformat(),
            category=category,
            metric_name=metric_name,
            value=value,
            unit=unit,
            agent_id=agent_id,
            operation_id=operation_id,
            metadata=metadata
        )
        
        self.events.append(event)
        
        # Also update counters/gauges
        metric_key = f"{category}.{metric_name}"
        if unit in ["count", "increment"]:
            self.counters[metric_key] += value
        else:
            self.gauges[metric_key] = value
            self.histograms[metric_key].append(value)
        
        logger.debug(f"PERF: Recorded {category}.{metric_name} = {value} {unit}")
    
    def increment_counter(self, metric_name: str, value: int = 1, 
                         agent_id: Optional[str] = None, **metadata):
        """Increment a counter metric."""
        self.record_event("counter", metric_name, value, "count", agent_id, None, **metadata)
    
    def set_gauge(self, metric_name: str, value: float, unit: str = "value", 
                 agent_id: Optional[str] = None, **metadata):
        """Set a gauge metric value."""
        self.record_event("gauge", metric_name, value, unit, agent_id, None, **metadata)
    
    def record_histogram(self, metric_name: str, value: float, unit: str = "ms", 
                        agent_id: Optional[str] = None, operation_id: Optional[str] = None, **metadata):
        """Record a histogram value."""
        self.record_event("histogram", metric_name, value, unit, agent_id, operation_id, **metadata)
    
    @contextmanager
    def time_operation(self, operation_name: str, agent_id: Optional[str] = None, **metadata):
        """Context manager for timing operations."""
        
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        start_time = time.perf_counter()
        success = False
        error_message = None
        
        try:
            self.active_operations[operation_id] = {
                "name": operation_name,
                "start_time": start_time,
                "agent_id": agent_id
            }
            
            logger.debug(f"PERF: Starting operation {operation_name} (ID: {operation_id})")
            yield operation_id
            success = True
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"PERF: Operation {operation_name} failed: {e}")
            raise
            
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Record performance metric
            perf_metric = PerformanceMetric(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                success=success,
                agent_id=agent_id,
                error_message=error_message,
                metadata=metadata
            )
            
            self.performance_metrics.append(perf_metric)
            self.operation_stats[operation_name].append(duration_ms)
            
            # Record timing event
            self.record_histogram(f"{operation_name}_duration", duration_ms, "ms", agent_id, 
                                operation_id=operation_id, success=success)
            
            # Clean up
            self.active_operations.pop(operation_id, None)
            
            status = "✅" if success else "❌"
            logger.info(f"PERF: {status} {operation_name} completed in {duration_ms:.1f}ms")
    
    def _collect_system_metrics(self):
        """Collect system-level metrics."""
        
        try:
            import psutil
            
            # CPU and memory
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            self.set_gauge("system_cpu_percent", cpu_percent, "percent")
            self.set_gauge("system_memory_percent", memory.percent, "percent")
            self.set_gauge("system_memory_available_mb", memory.available / 1024 / 1024, "MB")
            
            # Disk usage
            disk = psutil.disk_usage('.')
            self.set_gauge("system_disk_percent", (disk.used / disk.total) * 100, "percent")
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024
            self.set_gauge("process_memory_mb", process_memory, "MB")
            self.set_gauge("process_threads", process.num_threads(), "count")
            
        except ImportError:
            logger.debug("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _flush_metrics(self):
        """Flush collected metrics to files."""
        
        if not self.events and not self.performance_metrics:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save events
        if self.events:
            events_file = self.metrics_dir / f"events_{timestamp}.json"
            with open(events_file, 'w') as f:
                json.dump([asdict(event) for event in self.events], f, indent=2)
            
            logger.debug(f"PERF: Flushed {len(self.events)} events to {events_file}")
            self.events.clear()
        
        # Save performance metrics
        if self.performance_metrics:
            perf_file = self.metrics_dir / f"performance_{timestamp}.json"
            with open(perf_file, 'w') as f:
                json.dump([asdict(metric) for metric in self.performance_metrics], f, indent=2)
            
            logger.debug(f"PERF: Flushed {len(self.performance_metrics)} performance metrics to {perf_file}")
            self.performance_metrics.clear()
        
        # Save aggregated metrics
        aggregated = {
            "timestamp": datetime.now().isoformat(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "operation_stats": {
                name: {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times) if times else 0,
                    "min_ms": min(times) if times else 0,
                    "max_ms": max(times) if times else 0
                }
                for name, times in self.operation_stats.items()
            }
        }
        
        aggregated_file = self.metrics_dir / "aggregated_metrics.json"
        with open(aggregated_file, 'w') as f:
            json.dump(aggregated, f, indent=2)
    
    def generate_metrics_report(self) -> Dict:
        """Generate comprehensive metrics report."""
        
        logger.info("📋 Generating metrics report")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "collection_period": {
                "start": min(event.timestamp for event in self.events) if self.events else None,
                "end": max(event.timestamp for event in self.events) if self.events else None
            },
            "summary": {
                "total_events": len(self.events),
                "total_operations": len(self.performance_metrics),
                "unique_metrics": len(set(event.metric_name for event in self.events)),
                "active_operations": len(self.active_operations)
            },
            "top_operations": {},
            "performance_analysis": {},
            "agent_analysis": {},
            "recommendations": []
        }
        
        # Analyze top operations by frequency and duration
        operation_frequency = defaultdict(int)
        operation_durations = defaultdict(list)
        
        for metric in self.performance_metrics:
            operation_frequency[metric.operation_name] += 1
            operation_durations[metric.operation_name].append(metric.duration_ms)
        
        # Top operations by frequency
        top_by_frequency = sorted(operation_frequency.items(), 
                                key=lambda x: x[1], reverse=True)[:10]
        
        report["top_operations"]["by_frequency"] = [
            {"operation": name, "count": count} 
            for name, count in top_by_frequency
        ]
        
        # Performance analysis
        for op_name, durations in operation_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                report["performance_analysis"][op_name] = {
                    "count": len(durations),
                    "avg_duration_ms": avg_duration,
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "success_rate": sum(1 for m in self.performance_metrics 
                                      if m.operation_name == op_name and m.success) / len(durations)
                }
                
                # Performance recommendations
                if avg_duration > 1000:  # Slower than 1 second
                    report["recommendations"].append(
                        f"Operation '{op_name}' is slow (avg: {avg_duration:.0f}ms). Consider optimization."
                    )
                
                success_rate = report["performance_analysis"][op_name]["success_rate"]
                if success_rate < 0.95:  # Less than 95% success
                    report["recommendations"].append(
                        f"Operation '{op_name}' has low success rate ({success_rate*100:.1f}%). Check error handling."
                    )
        
        # Agent analysis
        agent_operations = defaultdict(list)
        for metric in self.performance_metrics:
            if metric.agent_id:
                agent_operations[metric.agent_id].append(metric)
        
        for agent_id, operations in agent_operations.items():
            successful_ops = [op for op in operations if op.success]
            avg_duration = sum(op.duration_ms for op in operations) / len(operations)
            
            report["agent_analysis"][agent_id] = {
                "total_operations": len(operations),
                "successful_operations": len(successful_ops),
                "success_rate": len(successful_ops) / len(operations),
                "avg_duration_ms": avg_duration
            }
        
        # Save report
        report_file = self.metrics_dir / "metrics_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Metrics report saved to {report_file}")
        return report
    
    def get_real_time_stats(self) -> Dict:
        """Get current real-time statistics."""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_operations": len(self.active_operations),
            "recent_events": len([e for e in self.events 
                                if datetime.fromisoformat(e.timestamp) > 
                                datetime.now() - timedelta(minutes=5)]),
            "top_counters": dict(sorted(self.counters.items(), 
                                      key=lambda x: x[1], reverse=True)[:10]),
            "current_gauges": dict(self.gauges),
            "operation_queue": list(self.active_operations.keys())
        }


# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

# Convenience functions
def record_event(category: str, metric_name: str, value: float, **kwargs):
    """Record a metric event using the global collector."""
    get_metrics_collector().record_event(category, metric_name, value, **kwargs)

def increment_counter(metric_name: str, value: int = 1, **kwargs):
    """Increment a counter using the global collector."""
    get_metrics_collector().increment_counter(metric_name, value, **kwargs)

def set_gauge(metric_name: str, value: float, **kwargs):
    """Set a gauge value using the global collector."""
    get_metrics_collector().set_gauge(metric_name, value, **kwargs)

def time_operation(operation_name: str, **kwargs):
    """Time an operation using the global collector."""
    return get_metrics_collector().time_operation(operation_name, **kwargs)


def demonstrate_metrics_collection():
    """Demonstrate the metrics collection system."""
    
    logger.info("📊 Starting Metrics Collection Demonstration")
    
    collector = get_metrics_collector()
    
    print("\n" + "="*60)
    print("📊 METRICS COLLECTION DEMO")
    print("="*60)
    
    # Start collection
    collector.start_collection()
    
    print("\n📈 Recording various metrics:")
    
    # Record some sample metrics
    collector.increment_counter("tasks_assigned")
    collector.increment_counter("tasks_assigned", agent_id="shark")
    collector.increment_counter("tasks_completed", 3, agent_id="dolphin")
    
    collector.set_gauge("system_load", 0.75, "ratio")
    collector.set_gauge("active_agents", 6, "count")
    
    collector.record_histogram("response_time", 150.5, "ms", agent_id="whale")
    collector.record_histogram("response_time", 89.2, "ms", agent_id="octopus")
    
    # Demonstrate timed operations
    print("\n⏱️  Timing operations:")
    
    with collector.time_operation("authority_assignment", agent_id="shark") as op_id:
        time.sleep(0.05)  # Simulate 50ms operation
        print(f"   Authority assignment operation: {op_id}")
    
    with collector.time_operation("emergency_response", agent_id="whale") as op_id:
        time.sleep(0.1)   # Simulate 100ms operation
        print(f"   Emergency response operation: {op_id}")
    
    # Simulate operation with error
    try:
        with collector.time_operation("risky_operation", agent_id="jellyfish") as op_id:
            time.sleep(0.02)
            raise ValueError("Simulated error")
    except ValueError:
        print(f"   Risky operation failed (expected)")
    
    # Record more metrics
    collector.record_event("workflow", "proposal_created", 1, "count", 
                          agent_id="shark", proposal_type="architecture")
    collector.record_event("workflow", "vote_cast", 1, "count", 
                          agent_id="dolphin", vote_choice="approve")
    
    print("\n📊 Current real-time stats:")
    stats = collector.get_real_time_stats()
    print(f"   Active operations: {stats['active_operations']}")
    print(f"   Recent events: {stats['recent_events']}")
    print(f"   Top counters: {list(stats['top_counters'].keys())[:3]}")
    
    # Wait for collection cycle
    print("\n⏳ Waiting for metrics flush...")
    time.sleep(2)
    
    # Generate report
    print("\n📋 Generating metrics report:")
    report = collector.generate_metrics_report()
    
    print(f"   Total events: {report['summary']['total_events']}")
    print(f"   Total operations: {report['summary']['total_operations']}")
    print(f"   Unique metrics: {report['summary']['unique_metrics']}")
    
    if report["top_operations"]["by_frequency"]:
        top_op = report["top_operations"]["by_frequency"][0]
        print(f"   Most frequent operation: {top_op['operation']} ({top_op['count']} times)")
    
    if report["recommendations"]:
        print(f"   Recommendations: {len(report['recommendations'])}")
        for rec in report["recommendations"][:2]:
            print(f"     • {rec}")
    
    # Stop collection
    collector.stop_collection()
    
    print(f"\n📁 Metrics saved to: {collector.metrics_dir}")
    
    logger.info("📊 Metrics collection demonstration completed")


if __name__ == "__main__":
    demonstrate_metrics_collection()