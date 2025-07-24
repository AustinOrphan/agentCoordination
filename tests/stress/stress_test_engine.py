"""
Core Stress Testing Engine

This module provides the foundational framework for stress testing the multi-agent
coordination system. It includes base classes, resource monitoring, scenario management,
and comprehensive reporting capabilities.
"""

import time
import psutil
import threading
import multiprocessing
import json
import os
import signal
import gc
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from contextlib import contextmanager
from enum import Enum
import statistics
import traceback

from ..utilities.bdd_performance import PerformanceMonitor, PerformanceProfile
from ..utilities.bdd_assertions import BDDAssertions, create_assertion_context


class StressLevel(Enum):
    """Stress testing intensity levels."""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    EXTREME = "extreme"


class StressTestPhase(Enum):
    """Phases of stress test execution."""
    SETUP = "setup"
    WARMUP = "warmup"
    STRESS = "stress"
    COOLDOWN = "cooldown"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StressTestConfig:
    """Configuration for stress test scenarios."""
    name: str
    level: StressLevel
    duration_seconds: float
    warmup_seconds: float = 30.0
    cooldown_seconds: float = 30.0
    agent_count: int = 6
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[float] = None
    failure_threshold: Dict[str, float] = field(default_factory=dict)
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StressTestResult:
    """Result of a stress test execution."""
    config: StressTestConfig
    start_time: datetime
    end_time: Optional[datetime] = None
    phase: StressTestPhase = StressTestPhase.SETUP
    success: bool = False
    error_message: Optional[str] = None
    performance_profile: Optional[PerformanceProfile] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    phase_durations: Dict[str, float] = field(default_factory=dict)
    resource_peaks: Dict[str, float] = field(default_factory=dict)
    failures: List[Dict[str, Any]] = field(default_factory=list)
    
    def finalize(self):
        """Finalize the test result."""
        if self.end_time is None:
            self.end_time = datetime.now()
            
        if self.phase not in [StressTestPhase.COMPLETED, StressTestPhase.FAILED]:
            self.phase = StressTestPhase.COMPLETED if self.success else StressTestPhase.FAILED


class ResourceMonitor:
    """Advanced resource monitoring for stress tests."""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.samples: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds: Dict[str, float] = {}
        self._lock = threading.Lock()
        
        # System info
        self.process = psutil.Process()
        self.system_cpu_count = psutil.cpu_count()
        self.system_memory_gb = psutil.virtual_memory().total / (1024**3)
        
    def set_thresholds(self, **thresholds):
        """Set resource threshold values for alerting."""
        self.thresholds.update(thresholds)
        
    def start_monitoring(self):
        """Start resource monitoring."""
        with self._lock:
            if self.is_monitoring:
                return
                
            self.is_monitoring = True
            self.samples.clear()
            self.alerts.clear()
            
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return summary."""
        with self._lock:
            if not self.is_monitoring:
                return {}
                
            self.is_monitoring = False
            
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
        return self._calculate_summary()
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                sample = self._take_sample()
                
                with self._lock:
                    self.samples.append(sample)
                    self._check_thresholds(sample)
                    
            except Exception as e:
                # Log but don't stop monitoring
                pass
                
            time.sleep(self.sampling_interval)
            
    def _take_sample(self) -> Dict[str, Any]:
        """Take a comprehensive resource sample."""
        # Process-specific metrics
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()
        
        # System-wide metrics
        system_memory = psutil.virtual_memory()
        system_cpu = psutil.cpu_percent()
        
        # I/O metrics
        try:
            io_counters = self.process.io_counters()
            disk_read_mb = io_counters.read_bytes / (1024**2)
            disk_write_mb = io_counters.write_bytes / (1024**2)
        except (AttributeError, psutil.AccessDenied):
            disk_read_mb = 0
            disk_write_mb = 0
            
        # File descriptors
        try:
            num_fds = self.process.num_fds() if hasattr(self.process, 'num_fds') else 0
        except (AttributeError, psutil.AccessDenied):
            num_fds = 0
            
        # Network I/O (system-wide)
        try:
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / (1024**2) if net_io else 0
            net_recv_mb = net_io.bytes_recv / (1024**2) if net_io else 0
        except (AttributeError, psutil.AccessDenied):
            net_sent_mb = 0
            net_recv_mb = 0
            
        return {
            'timestamp': time.time(),
            'process_memory_mb': memory_info.rss / (1024**2),
            'process_cpu_percent': cpu_percent,
            'system_memory_percent': system_memory.percent,
            'system_cpu_percent': system_cpu,
            'disk_read_mb': disk_read_mb,
            'disk_write_mb': disk_write_mb,
            'num_file_descriptors': num_fds,
            'network_sent_mb': net_sent_mb,
            'network_recv_mb': net_recv_mb,
            'available_memory_gb': system_memory.available / (1024**3)
        }
        
    def _check_thresholds(self, sample: Dict[str, Any]):
        """Check if any thresholds are exceeded."""
        for metric, threshold in self.thresholds.items():
            value = sample.get(metric)
            if value is not None and value > threshold:
                alert = {
                    'timestamp': sample['timestamp'],
                    'metric': metric,
                    'value': value,
                    'threshold': threshold,
                    'severity': 'high' if value > threshold * 1.5 else 'medium'
                }
                self.alerts.append(alert)
                
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate monitoring summary statistics."""
        if not self.samples:
            return {}
            
        metrics = {}
        for key in self.samples[0].keys():
            if key != 'timestamp':
                values = [s[key] for s in self.samples if s[key] is not None]
                if values:
                    metrics[key] = {
                        'avg': statistics.mean(values),
                        'max': max(values),
                        'min': min(values),
                        'std': statistics.stdev(values) if len(values) > 1 else 0
                    }
                    
        return {
            'sample_count': len(self.samples),
            'duration_seconds': self.samples[-1]['timestamp'] - self.samples[0]['timestamp'],
            'metrics': metrics,
            'alerts': self.alerts,
            'peak_memory_mb': metrics.get('process_memory_mb', {}).get('max', 0),
            'peak_cpu_percent': metrics.get('process_cpu_percent', {}).get('max', 0)
        }


class StressTestScenario(ABC):
    """Base class for all stress test scenarios."""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.result = StressTestResult(
            config=config,
            start_time=datetime.now()
        )
        self.monitor = ResourceMonitor()
        self.performance_tracker = PerformanceMonitor()
        self.assertions = BDDAssertions(
            create_assertion_context(config.name, "stress_test")
        )
        self._shutdown_requested = False
        
    @abstractmethod
    def setup(self):
        """Setup the stress test scenario."""
        pass
        
    @abstractmethod
    def execute_stress(self):
        """Execute the main stress test logic."""
        pass
        
    @abstractmethod
    def cleanup(self):
        """Clean up after the stress test."""
        pass
        
    def warmup(self):
        """Warmup phase - can be overridden."""
        time.sleep(self.config.warmup_seconds)
        
    def cooldown(self):
        """Cooldown phase - can be overridden."""
        time.sleep(self.config.cooldown_seconds)
        
    def should_continue(self) -> bool:
        """Check if the test should continue running."""
        return not self._shutdown_requested
        
    def request_shutdown(self):
        """Request graceful shutdown."""
        self._shutdown_requested = True
        
    def record_failure(self, failure_type: str, message: str, **metadata):
        """Record a test failure."""
        self.result.failures.append({
            'timestamp': datetime.now().isoformat(),
            'type': failure_type,
            'message': message,
            'metadata': metadata
        })
        
    def record_metric(self, name: str, value: float, unit: str = ""):
        """Record a custom metric."""
        self.result.metrics[name] = {
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }


class StressTestRunner:
    """Main stress test execution engine."""
    
    def __init__(self, output_dir: str = "stress_test_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.active_scenarios: List[StressTestScenario] = []
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, requesting graceful shutdown...")
            for scenario in self.active_scenarios:
                scenario.request_shutdown()
                
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def run_scenario(self, scenario: StressTestScenario) -> StressTestResult:
        """Run a single stress test scenario."""
        self.active_scenarios.append(scenario)
        
        try:
            return self._execute_scenario(scenario)
        finally:
            if scenario in self.active_scenarios:
                self.active_scenarios.remove(scenario)
                
    def run_scenarios(self, scenarios: List[StressTestScenario]) -> List[StressTestResult]:
        """Run multiple stress test scenarios."""
        results = []
        
        for scenario in scenarios:
            print(f"\n🚀 Starting stress test: {scenario.config.name}")
            result = self.run_scenario(scenario)
            results.append(result)
            
            if not result.success:
                print(f"❌ Stress test failed: {result.error_message}")
                if not self._should_continue_after_failure():
                    break
            else:
                print(f"✅ Stress test completed successfully")
                
        return results
        
    def _execute_scenario(self, scenario: StressTestScenario) -> StressTestResult:
        """Execute a single scenario with full lifecycle."""
        start_time = time.time()
        
        try:
            # Setup phase
            scenario.result.phase = StressTestPhase.SETUP
            phase_start = time.time()
            scenario.setup()
            scenario.result.phase_durations['setup'] = time.time() - phase_start
            
            # Configure resource monitoring
            scenario.monitor.set_thresholds(
                process_memory_mb=scenario.config.max_memory_mb or 1000,
                process_cpu_percent=scenario.config.max_cpu_percent or 80
            )
            scenario.monitor.start_monitoring()
            
            # Start performance tracking
            performance_profile = scenario.performance_tracker.start_monitoring(scenario.config.name)
            
            # Warmup phase
            if scenario.config.warmup_seconds > 0:
                scenario.result.phase = StressTestPhase.WARMUP
                phase_start = time.time()
                scenario.warmup()
                scenario.result.phase_durations['warmup'] = time.time() - phase_start
                
            # Main stress phase
            scenario.result.phase = StressTestPhase.STRESS
            phase_start = time.time()
            
            # Set up timeout
            end_time = time.time() + scenario.config.duration_seconds
            
            # Execute stress with timeout monitoring
            stress_thread = threading.Thread(target=scenario.execute_stress)
            stress_thread.start()
            
            # Monitor progress
            while stress_thread.is_alive() and time.time() < end_time and scenario.should_continue():
                time.sleep(1.0)
                self._check_resource_limits(scenario)
                
            # If thread is still alive, request shutdown
            if stress_thread.is_alive():
                scenario.request_shutdown()
                stress_thread.join(timeout=30.0)
                
                if stress_thread.is_alive():
                    # Force termination as last resort
                    scenario.record_failure("timeout", "Stress test did not complete within timeout")
                    
            scenario.result.phase_durations['stress'] = time.time() - phase_start
            
            # Cooldown phase
            if scenario.config.cooldown_seconds > 0:
                scenario.result.phase = StressTestPhase.COOLDOWN
                phase_start = time.time()
                scenario.cooldown()
                scenario.result.phase_durations['cooldown'] = time.time() - phase_start
                
            # Determine success
            scenario.result.success = len(scenario.result.failures) == 0
            
        except Exception as e:
            scenario.result.error_message = f"Unexpected error: {str(e)}"
            scenario.result.success = False
            scenario.record_failure("exception", str(e), traceback=traceback.format_exc())
            
        finally:
            # Cleanup phase
            scenario.result.phase = StressTestPhase.CLEANUP
            phase_start = time.time()
            
            try:
                # Stop monitoring
                resource_summary = scenario.monitor.stop_monitoring()
                scenario.result.resource_peaks = {
                    'memory_mb': resource_summary.get('peak_memory_mb', 0),
                    'cpu_percent': resource_summary.get('peak_cpu_percent', 0)
                }
                
                # Stop performance tracking
                scenario.result.performance_profile = scenario.performance_tracker.stop_monitoring()
                
                # Run cleanup
                scenario.cleanup()
                
            except Exception as e:
                scenario.record_failure("cleanup", f"Cleanup failed: {str(e)}")
                
            scenario.result.phase_durations['cleanup'] = time.time() - phase_start
            
            # Finalize result
            scenario.result.finalize()
            
            # Save results
            self._save_result(scenario.result)
            
            # Force garbage collection
            gc.collect()
            
        return scenario.result
        
    def _check_resource_limits(self, scenario: StressTestScenario):
        """Check if resource limits are exceeded."""
        if not scenario.monitor.samples:
            return
            
        latest_sample = scenario.monitor.samples[-1]
        
        # Check memory limit
        max_memory = scenario.config.max_memory_mb
        if max_memory and latest_sample.get('process_memory_mb', 0) > max_memory:
            scenario.record_failure(
                "memory_limit",
                f"Memory usage exceeded limit: {latest_sample['process_memory_mb']:.1f}MB > {max_memory}MB"
            )
            scenario.request_shutdown()
            
        # Check CPU limit
        max_cpu = scenario.config.max_cpu_percent
        if max_cpu and latest_sample.get('process_cpu_percent', 0) > max_cpu:
            scenario.record_failure(
                "cpu_limit",
                f"CPU usage exceeded limit: {latest_sample['process_cpu_percent']:.1f}% > {max_cpu}%"
            )
            
    def _should_continue_after_failure(self) -> bool:
        """Determine if testing should continue after a failure."""
        # For now, continue with remaining tests
        return True
        
    def _save_result(self, result: StressTestResult):
        """Save test result to file."""
        timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_{result.config.name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert result to JSON-serializable format
        result_dict = asdict(result)
        result_dict['start_time'] = result.start_time.isoformat()
        if result.end_time:
            result_dict['end_time'] = result.end_time.isoformat()
            
        with open(filepath, 'w') as f:
            json.dump(result_dict, f, indent=2, default=str)
            
    def generate_summary_report(self, results: List[StressTestResult]) -> str:
        """Generate a summary report for multiple test results."""
        if not results:
            return "No stress test results to report."
            
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        report = []
        report.append("🔥 STRESS TEST SUMMARY REPORT")
        report.append("=" * 50)
        report.append(f"Total Tests: {len(results)}")
        report.append(f"Successful: {len(successful)} ✅")
        report.append(f"Failed: {len(failed)} ❌")
        report.append(f"Success Rate: {len(successful)/len(results)*100:.1f}%")
        report.append("")
        
        if successful:
            report.append("🟢 SUCCESSFUL TESTS:")
            for result in successful:
                duration = sum(result.phase_durations.values())
                peak_memory = result.resource_peaks.get('memory_mb', 0)
                report.append(f"  • {result.config.name} ({result.config.level.value})")
                report.append(f"    Duration: {duration:.1f}s, Peak Memory: {peak_memory:.1f}MB")
                
        if failed:
            report.append("\n🔴 FAILED TESTS:")
            for result in failed:
                report.append(f"  • {result.config.name} ({result.config.level.value})")
                report.append(f"    Error: {result.error_message}")
                if result.failures:
                    report.append(f"    Failures: {len(result.failures)}")
                    
        return "\n".join(report)


# Utility functions for creating standard stress test configurations
def create_light_stress_config(name: str, **kwargs) -> StressTestConfig:
    """Create a light stress test configuration."""
    defaults = {
        'level': StressLevel.LIGHT,
        'duration_seconds': 60,
        'agent_count': 3,
        'max_memory_mb': 500,
        'max_cpu_percent': 50
    }
    defaults.update(kwargs)
    return StressTestConfig(name=name, **defaults)


def create_medium_stress_config(name: str, **kwargs) -> StressTestConfig:
    """Create a medium stress test configuration."""
    defaults = {
        'level': StressLevel.MEDIUM,
        'duration_seconds': 300,
        'agent_count': 6,
        'max_memory_mb': 1000,
        'max_cpu_percent': 70
    }
    defaults.update(kwargs)
    return StressTestConfig(name=name, **kwargs)


def create_heavy_stress_config(name: str, **kwargs) -> StressTestConfig:
    """Create a heavy stress test configuration."""
    defaults = {
        'level': StressLevel.HEAVY,
        'duration_seconds': 600,
        'agent_count': 12,
        'max_memory_mb': 2000,
        'max_cpu_percent': 85
    }
    defaults.update(kwargs)
    return StressTestConfig(name=name, **defaults)


def create_extreme_stress_config(name: str, **kwargs) -> StressTestConfig:
    """Create an extreme stress test configuration."""
    defaults = {
        'level': StressLevel.EXTREME,
        'duration_seconds': 1200,
        'agent_count': 24,
        'max_memory_mb': 4000,
        'max_cpu_percent': 95
    }
    defaults.update(kwargs)
    return StressTestConfig(name=name, **defaults)


if __name__ == "__main__":
    # Example usage and testing
    print("Stress Test Engine initialized successfully!")
    print(f"System specs: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / (1024**3):.1f}GB RAM")