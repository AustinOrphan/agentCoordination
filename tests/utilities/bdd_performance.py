"""
Performance Measurement Utilities for BDD Tests

This module provides comprehensive performance monitoring and measurement capabilities
for BDD edge case testing, including timing, resource usage, throughput analysis,
and performance regression detection.
"""

import time
import psutil
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict, deque
import statistics
import functools

from .bdd_test_reporter import add_performance_metric


@dataclass
class PerformanceMetric:
    """Individual performance metric data."""
    name: str
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSample:
    """Single performance measurement sample."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: Optional[int] = None
    network_bytes_recv: Optional[int] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceProfile:
    """Complete performance profile for a test scenario."""
    scenario_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    samples: List[PerformanceSample] = field(default_factory=list)
    metrics: List[PerformanceMetric] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def finalize(self):
        """Finalize the performance profile."""
        if self.end_time is None:
            self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self._calculate_summary()
        
    def _calculate_summary(self):
        """Calculate summary statistics."""
        if not self.samples:
            return
            
        cpu_values = [s.cpu_percent for s in self.samples]
        memory_values = [s.memory_mb for s in self.samples]
        
        self.summary = {
            'duration': self.duration,
            'sample_count': len(self.samples),
            'cpu': {
                'avg': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'std': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            },
            'memory': {
                'avg': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'std': statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            'io': {
                'total_read_mb': sum(s.disk_io_read_mb for s in self.samples),
                'total_write_mb': sum(s.disk_io_write_mb for s in self.samples)
            }
        }


class PerformanceMonitor:
    """Real-time performance monitoring for BDD tests."""
    
    def __init__(self, sampling_interval: float = 0.1):
        self.sampling_interval = sampling_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.current_profile: Optional[PerformanceProfile] = None
        self.baseline_profiles: Dict[str, PerformanceProfile] = {}
        self._lock = threading.Lock()
        
        # System monitoring setup
        self.process = psutil.Process()
        self.initial_io = self.process.io_counters()
        
    def start_monitoring(self, scenario_name: str) -> PerformanceProfile:
        """Start monitoring performance for a scenario."""
        with self._lock:
            if self.is_monitoring:
                self.stop_monitoring()
                
            self.current_profile = PerformanceProfile(
                scenario_name=scenario_name,
                start_time=time.time()
            )
            
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            return self.current_profile
            
    def stop_monitoring(self) -> Optional[PerformanceProfile]:
        """Stop monitoring and return the performance profile."""
        with self._lock:
            if not self.is_monitoring:
                return None
                
            self.is_monitoring = False
            
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
        if self.current_profile:
            self.current_profile.finalize()
            profile = self.current_profile
            self.current_profile = None
            return profile
            
        return None
        
    def add_metric(self, name: str, value: float, unit: str = "", **tags):
        """Add custom metric to current monitoring session."""
        if self.current_profile:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                tags=tags
            )
            self.current_profile.metrics.append(metric)
            
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                sample = self._take_sample()
                if self.current_profile:
                    self.current_profile.samples.append(sample)
            except Exception as e:
                # Silently handle monitoring errors to not interfere with tests
                pass
                
            time.sleep(self.sampling_interval)
            
    def _take_sample(self) -> PerformanceSample:
        """Take a single performance sample."""
        # CPU and memory
        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Disk I/O
        try:
            io_counters = self.process.io_counters()
            disk_read_mb = (io_counters.read_bytes - self.initial_io.read_bytes) / 1024 / 1024
            disk_write_mb = (io_counters.write_bytes - self.initial_io.write_bytes) / 1024 / 1024
        except (AttributeError, psutil.AccessDenied):
            disk_read_mb = 0
            disk_write_mb = 0
            
        # Network (if available)
        network_sent = None
        network_recv = None
        try:
            network_io = psutil.net_io_counters()
            network_sent = network_io.bytes_sent
            network_recv = network_io.bytes_recv
        except (AttributeError, psutil.AccessDenied):
            pass
            
        return PerformanceSample(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_bytes_sent=network_sent,
            network_bytes_recv=network_recv
        )
        
    def save_baseline(self, profile: PerformanceProfile):
        """Save a performance profile as baseline for comparison."""
        self.baseline_profiles[profile.scenario_name] = profile
        
    def compare_with_baseline(self, profile: PerformanceProfile) -> Dict[str, Any]:
        """Compare performance profile with baseline."""
        baseline = self.baseline_profiles.get(profile.scenario_name)
        if not baseline:
            return {"status": "no_baseline", "message": "No baseline available for comparison"}
            
        comparison = {
            "status": "compared",
            "baseline_duration": baseline.duration,
            "current_duration": profile.duration,
            "duration_change_percent": ((profile.duration - baseline.duration) / baseline.duration) * 100,
            "cpu": self._compare_metric_summary(baseline.summary.get('cpu', {}), profile.summary.get('cpu', {})),
            "memory": self._compare_metric_summary(baseline.summary.get('memory', {}), profile.summary.get('memory', {})),
            "regression_detected": False
        }
        
        # Simple regression detection
        if comparison["duration_change_percent"] > 20:  # 20% slower
            comparison["regression_detected"] = True
            comparison["regression_type"] = "duration"
            
        cpu_regression = comparison["cpu"].get("avg_change_percent", 0) > 30
        memory_regression = comparison["memory"].get("avg_change_percent", 0) > 50
        
        if cpu_regression:
            comparison["regression_detected"] = True
            comparison["regression_type"] = "cpu"
        elif memory_regression:
            comparison["regression_detected"] = True
            comparison["regression_type"] = "memory"
            
        return comparison
        
    def _compare_metric_summary(self, baseline: Dict[str, float], current: Dict[str, float]) -> Dict[str, Any]:
        """Compare metric summaries."""
        if not baseline or not current:
            return {"status": "insufficient_data"}
            
        return {
            "baseline_avg": baseline.get('avg', 0),
            "current_avg": current.get('avg', 0),
            "avg_change_percent": ((current.get('avg', 0) - baseline.get('avg', 0)) / baseline.get('avg', 1)) * 100,
            "baseline_max": baseline.get('max', 0),
            "current_max": current.get('max', 0),
            "max_change_percent": ((current.get('max', 0) - baseline.get('max', 0)) / baseline.get('max', 1)) * 100
        }


class BDDPerformanceTracker:
    """High-level performance tracking for BDD tests."""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.active_timers: Dict[str, float] = {}
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.throughput_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
    @contextmanager
    def measure_scenario(self, scenario_name: str):
        """Context manager for measuring entire scenario performance."""
        profile = self.monitor.start_monitoring(scenario_name)
        start_time = time.time()
        
        try:
            yield self
        finally:
            end_time = time.time()
            final_profile = self.monitor.stop_monitoring()
            
            # Add scenario-level metrics
            if final_profile:
                self.monitor.add_metric("scenario_duration", end_time - start_time, "seconds")
                
                # Compare with baseline if available
                comparison = self.monitor.compare_with_baseline(final_profile)
                if comparison.get("regression_detected"):
                    print(f"⚠️  Performance regression detected in {scenario_name}: {comparison.get('regression_type')}")
                    
    @contextmanager
    def measure_operation(self, operation_name: str):
        """Context manager for measuring specific operations."""
        start_time = time.time()
        self.monitor.add_metric(f"{operation_name}_start", start_time, "timestamp")
        
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            self.operation_times[operation_name].append(duration)
            self.monitor.add_metric(f"{operation_name}_duration", duration, "seconds")
            self.monitor.add_metric(f"{operation_name}_end", end_time, "timestamp")
            
    def start_timer(self, timer_name: str):
        """Start a named timer."""
        self.active_timers[timer_name] = time.time()
        
    def stop_timer(self, timer_name: str) -> float:
        """Stop a named timer and return duration."""
        if timer_name not in self.active_timers:
            return 0.0
            
        duration = time.time() - self.active_timers[timer_name]
        del self.active_timers[timer_name]
        self.operation_times[timer_name].append(duration)
        self.monitor.add_metric(f"timer_{timer_name}", duration, "seconds")
        return duration
        
    def count_throughput(self, counter_name: str, count: int = 1):
        """Count throughput events."""
        timestamp = time.time()
        for _ in range(count):
            self.throughput_counters[counter_name].append(timestamp)
            
    def get_throughput(self, counter_name: str, window_seconds: float = 60.0) -> float:
        """Get throughput rate for the specified window."""
        now = time.time()
        window_start = now - window_seconds
        counter = self.throughput_counters[counter_name]
        
        # Count events in the window
        events_in_window = sum(1 for timestamp in counter if timestamp >= window_start)
        return events_in_window / window_seconds
        
    def get_operation_stats(self, operation_name: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        times = self.operation_times.get(operation_name, [])
        if not times:
            return {"count": 0}
            
        return {
            "count": len(times),
            "total": sum(times),
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "std": statistics.stdev(times) if len(times) > 1 else 0,
            "median": statistics.median(times),
            "p95": self._percentile(times, 0.95),
            "p99": self._percentile(times, 0.99)
        }
        
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
        
    def export_metrics(self, filename: str):
        """Export all metrics to JSON file."""
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "operation_stats": {op: self.get_operation_stats(op) for op in self.operation_times},
            "throughput": {name: self.get_throughput(name) for name in self.throughput_counters},
            "baseline_profiles": {name: asdict(profile) for name, profile in self.monitor.baseline_profiles.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=2)


# Decorators for performance measurement
def measure_performance(operation_name: str = None, track_args: bool = False):
    """Decorator to measure function performance."""
    def decorator(func):
        nonlocal operation_name
        if operation_name is None:
            operation_name = f"{func.__module__}.{func.__name__}"
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get current tracker from thread-local storage or create new one
            tracker = getattr(wrapper, '_performance_tracker', None)
            if tracker is None:
                tracker = BDDPerformanceTracker()
                wrapper._performance_tracker = tracker
                
            op_name = operation_name
            if track_args and args:
                op_name += f"_args_{len(args)}"
                
            with tracker.measure_operation(op_name):
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


def track_throughput(counter_name: str = None):
    """Decorator to track function call throughput."""
    def decorator(func):
        nonlocal counter_name
        if counter_name is None:
            counter_name = f"{func.__module__}.{func.__name__}_calls"
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracker = getattr(wrapper, '_performance_tracker', None)
            if tracker is None:
                tracker = BDDPerformanceTracker()
                wrapper._performance_tracker = tracker
                
            tracker.count_throughput(counter_name)
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# Utility functions for BDD integration
def create_performance_tracker() -> BDDPerformanceTracker:
    """Create a new performance tracker for BDD tests."""
    return BDDPerformanceTracker()


def load_baseline_profiles(tracker: BDDPerformanceTracker, filename: str):
    """Load baseline performance profiles from file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            
        profiles_data = data.get('baseline_profiles', {})
        for name, profile_dict in profiles_data.items():
            # Reconstruct PerformanceProfile from dict
            profile = PerformanceProfile(**profile_dict)
            tracker.monitor.save_baseline(profile)
            
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # No baseline available


def save_baseline_profiles(tracker: BDDPerformanceTracker, filename: str):
    """Save current baseline profiles to file."""
    tracker.export_metrics(filename)


# Example usage
if __name__ == "__main__":
    # Example performance measurement
    tracker = BDDPerformanceTracker()
    
    with tracker.measure_scenario("Authority Assignment Test"):
        with tracker.measure_operation("authority_request"):
            time.sleep(0.1)  # Simulate work
            
        tracker.count_throughput("requests_processed", 5)
        
        with tracker.measure_operation("authority_validation"):
            time.sleep(0.05)  # Simulate work
            
    # Print results
    print("Authority Request Stats:", tracker.get_operation_stats("authority_request"))
    print("Throughput:", tracker.get_throughput("requests_processed"))
    
    # Export metrics
    tracker.export_metrics("performance_metrics.json")