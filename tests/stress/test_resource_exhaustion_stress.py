"""
Resource Exhaustion Stress Tests

This module tests the multi-agent coordination system's behavior under
resource exhaustion conditions, including memory, disk space, file handles,
and CPU starvation scenarios.
"""

import time
import json
import os
import threading
import tempfile
import shutil
import gc
import mmap
import multiprocessing
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pytest
import psutil

from .stress_test_engine import (
    StressTestScenario, StressTestRunner, StressTestConfig,
    create_light_stress_config, create_medium_stress_config, 
    create_heavy_stress_config, create_extreme_stress_config
)


@dataclass
class ResourceExhaustionMetrics:
    """Metrics for resource exhaustion testing."""
    resource_type: str
    baseline_usage: float
    peak_usage: float
    exhaustion_threshold: float
    recovery_time: float
    performance_degradation: float
    system_stability: str  # "stable", "degraded", "unstable"
    recovery_success: bool


class SafeResourceManager:
    """Manages safe resource consumption with automatic cleanup."""
    
    def __init__(self, max_memory_mb: int = 512, max_files: int = 100):
        self.max_memory_mb = max_memory_mb
        self.max_files = max_files
        self.allocated_memory: List[bytearray] = []
        self.open_files: List[Any] = []
        self.temp_files: List[str] = []
        self.temp_dir: Optional[str] = None
        
    def allocate_memory(self, size_mb: float) -> bool:
        """Safely allocate memory up to limits."""
        current_memory = sum(len(arr) for arr in self.allocated_memory) / (1024**2)
        
        if current_memory + size_mb > self.max_memory_mb:
            return False
            
        try:
            # Allocate memory in chunks to avoid large single allocations
            chunk_size = min(size_mb, 10)  # 10MB chunks
            while size_mb > 0:
                current_chunk = min(chunk_size, size_mb) * 1024 * 1024
                memory_chunk = bytearray(int(current_chunk))
                # Write to memory to ensure actual allocation
                for i in range(0, len(memory_chunk), 4096):
                    memory_chunk[i] = 1
                self.allocated_memory.append(memory_chunk)
                size_mb -= chunk_size
            return True
        except MemoryError:
            return False
            
    def create_temp_files(self, count: int, size_mb: float = 1.0) -> int:
        """Create temporary files for disk space testing."""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="resource_exhaustion_")
            
        created = 0
        for i in range(count):
            if len(self.temp_files) >= self.max_files:
                break
                
            try:
                temp_file = os.path.join(self.temp_dir, f"temp_file_{i}_{int(time.time())}.dat")
                with open(temp_file, 'wb') as f:
                    # Write data in chunks to control size
                    chunk_size = 1024 * 1024  # 1MB chunks
                    total_bytes = int(size_mb * 1024 * 1024)
                    written = 0
                    
                    while written < total_bytes:
                        chunk = min(chunk_size, total_bytes - written)
                        f.write(b'0' * chunk)
                        written += chunk
                        
                self.temp_files.append(temp_file)
                created += 1
            except (OSError, IOError):
                break
                
        return created
        
    def open_file_handles(self, count: int) -> int:
        """Open multiple file handles for file descriptor testing."""
        opened = 0
        for i in range(count):
            if len(self.open_files) >= self.max_files:
                break
                
            try:
                # Create a temporary file and keep it open
                temp_file = tempfile.NamedTemporaryFile(delete=False, prefix="fd_test_")
                self.open_files.append(temp_file)
                self.temp_files.append(temp_file.name)
                opened += 1
            except (OSError, IOError):
                break
                
        return opened
        
    def cleanup(self):
        """Clean up all allocated resources."""
        # Free memory
        self.allocated_memory.clear()
        gc.collect()
        
        # Close file handles
        for f in self.open_files:
            try:
                f.close()
            except:
                pass
        self.open_files.clear()
        
        # Remove temporary files
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        self.temp_files.clear()
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
        self.temp_dir = None


class MemoryExhaustionStressScenario(StressTestScenario):
    """Test system behavior under memory pressure."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.resource_manager = SafeResourceManager(
            max_memory_mb=config.custom_params.get('max_memory_mb', 512)
        )
        self.metrics: List[ResourceExhaustionMetrics] = []
        
    def setup(self):
        """Setup memory exhaustion test."""
        # Record baseline memory usage
        self.baseline_memory = psutil.virtual_memory().percent
        
    def execute_stress(self):
        """Execute memory exhaustion stress test."""
        print("🧠 Starting memory exhaustion stress test...")
        
        # Gradually increase memory allocation
        allocation_steps = [10, 25, 50, 100, 200, 400]  # MB increments
        
        for step_mb in allocation_steps:
            if not self.should_continue():
                break
                
            start_time = time.time()
            baseline_performance = self._measure_coordination_performance()
            
            # Allocate memory
            success = self.resource_manager.allocate_memory(step_mb)
            if not success:
                self.record_failure("memory_allocation", f"Failed to allocate {step_mb}MB")
                break
                
            # Test system under memory pressure
            current_memory = psutil.virtual_memory().percent
            stressed_performance = self._measure_coordination_performance()
            
            # Test recovery
            recovery_start = time.time()
            # Force garbage collection to test recovery
            gc.collect()
            recovery_time = time.time() - recovery_start
            
            # Calculate metrics
            performance_degradation = (
                (stressed_performance - baseline_performance) / baseline_performance * 100
                if baseline_performance > 0 else 0
            )
            
            stability = self._assess_system_stability(current_memory)
            
            metrics = ResourceExhaustionMetrics(
                resource_type="memory",
                baseline_usage=self.baseline_memory,
                peak_usage=current_memory,
                exhaustion_threshold=85.0,  # 85% memory usage threshold
                recovery_time=recovery_time,
                performance_degradation=performance_degradation,
                system_stability=stability,
                recovery_success=current_memory < self.baseline_memory + 20
            )
            
            self.metrics.append(metrics)
            
            # Record metrics
            self.record_metric(f"memory_usage_step_{step_mb}mb", current_memory, "percent")
            self.record_metric(f"performance_degradation_step_{step_mb}mb", performance_degradation, "percent")
            
            # Stop if we hit dangerous memory levels
            if current_memory > 85:
                print(f"⚠️  Memory usage too high ({current_memory:.1f}%), stopping test")
                break
                
            time.sleep(2)  # Brief pause between allocations
            
    def _measure_coordination_performance(self) -> float:
        """Measure coordination system performance (simulated)."""
        # Simulate coordination operations and measure time
        start_time = time.time()
        
        # Create temporary coordination files to simulate activity
        for i in range(10):
            temp_data = {"agent_id": f"test_agent_{i}", "timestamp": time.time()}
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.json')
            json.dump(temp_data, temp_file)
            temp_file.flush()
            
        return time.time() - start_time
        
    def _assess_system_stability(self, memory_percent: float) -> str:
        """Assess system stability based on resource usage."""
        if memory_percent < 70:
            return "stable"
        elif memory_percent < 85:
            return "degraded"
        else:
            return "unstable"
            
    def cleanup(self):
        """Clean up memory exhaustion test."""
        self.resource_manager.cleanup()


class DiskSpaceExhaustionStressScenario(StressTestScenario):
    """Test system behavior under disk space pressure."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.resource_manager = SafeResourceManager(
            max_files=config.custom_params.get('max_files', 100)
        )
        self.metrics: List[ResourceExhaustionMetrics] = []
        
    def setup(self):
        """Setup disk space exhaustion test."""
        # Record baseline disk usage
        disk_usage = psutil.disk_usage('/')
        self.baseline_disk_percent = (disk_usage.used / disk_usage.total) * 100
        
    def execute_stress(self):
        """Execute disk space exhaustion stress test."""
        print("💾 Starting disk space exhaustion stress test...")
        
        # Create files of increasing sizes
        file_sizes = [1, 5, 10, 20, 50]  # MB per file
        files_per_size = [10, 5, 3, 2, 1]
        
        for size_mb, file_count in zip(file_sizes, files_per_size):
            if not self.should_continue():
                break
                
            baseline_performance = self._measure_file_operations_performance()
            
            # Create files
            created = self.resource_manager.create_temp_files(file_count, size_mb)
            if created < file_count:
                self.record_failure("disk_space", f"Could only create {created}/{file_count} files of {size_mb}MB")
                
            # Measure current disk usage
            disk_usage = psutil.disk_usage('/')
            current_disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Test performance under disk pressure
            stressed_performance = self._measure_file_operations_performance()
            
            # Calculate metrics
            performance_degradation = (
                (stressed_performance - baseline_performance) / baseline_performance * 100
                if baseline_performance > 0 else 0
            )
            
            stability = self._assess_disk_stability(current_disk_percent)
            
            metrics = ResourceExhaustionMetrics(
                resource_type="disk_space",
                baseline_usage=self.baseline_disk_percent,
                peak_usage=current_disk_percent,
                exhaustion_threshold=90.0,  # 90% disk usage threshold
                recovery_time=0.0,  # Will measure during cleanup
                performance_degradation=performance_degradation,
                system_stability=stability,
                recovery_success=True  # Will update during cleanup
            )
            
            self.metrics.append(metrics)
            
            # Record metrics
            self.record_metric(f"disk_usage_files_{file_count}x{size_mb}mb", current_disk_percent, "percent")
            self.record_metric(f"file_ops_degradation_{file_count}x{size_mb}mb", performance_degradation, "percent")
            
            # Stop if disk usage gets too high
            if current_disk_percent > 90:
                print(f"⚠️  Disk usage too high ({current_disk_percent:.1f}%), stopping test")
                break
                
            time.sleep(1)
            
    def _measure_file_operations_performance(self) -> float:
        """Measure file operations performance."""
        start_time = time.time()
        
        # Perform multiple file operations
        temp_files = []
        try:
            for i in range(20):
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                temp_file.write(f"test_data_{i}" * 100)
                temp_file.close()
                temp_files.append(temp_file.name)
                
                # Read the file back
                with open(temp_file.name, 'r') as f:
                    f.read()
                    
        finally:
            # Clean up test files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        return time.time() - start_time
        
    def _assess_disk_stability(self, disk_percent: float) -> str:
        """Assess system stability based on disk usage."""
        if disk_percent < 80:
            return "stable"
        elif disk_percent < 90:
            return "degraded"
        else:
            return "unstable"
            
    def cleanup(self):
        """Clean up disk space exhaustion test."""
        recovery_start = time.time()
        self.resource_manager.cleanup()
        recovery_time = time.time() - recovery_start
        
        # Update recovery metrics
        for metrics in self.metrics:
            metrics.recovery_time = recovery_time


class FileHandleExhaustionStressScenario(StressTestScenario):
    """Test system behavior when file descriptors are exhausted."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.resource_manager = SafeResourceManager(
            max_files=config.custom_params.get('max_file_handles', 50)
        )
        self.metrics: List[ResourceExhaustionMetrics] = []
        
    def setup(self):
        """Setup file handle exhaustion test."""
        # Get baseline file descriptor count
        try:
            self.baseline_fds = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 10
        except:
            self.baseline_fds = 10
            
    def execute_stress(self):
        """Execute file handle exhaustion stress test."""
        print("📁 Starting file handle exhaustion stress test...")
        
        # Gradually open more file handles
        handle_increments = [5, 10, 15, 20, 25]
        
        for increment in handle_increments:
            if not self.should_continue():
                break
                
            baseline_performance = self._measure_file_access_performance()
            
            # Open file handles
            opened = self.resource_manager.open_file_handles(increment)
            if opened < increment:
                self.record_failure("file_handles", f"Could only open {opened}/{increment} file handles")
                
            # Get current file descriptor count
            try:
                current_fds = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else self.baseline_fds + len(self.resource_manager.open_files)
            except:
                current_fds = self.baseline_fds + len(self.resource_manager.open_files)
                
            # Test performance with many open handles
            stressed_performance = self._measure_file_access_performance()
            
            # Calculate metrics
            performance_degradation = (
                (stressed_performance - baseline_performance) / baseline_performance * 100
                if baseline_performance > 0 else 0
            )
            
            stability = self._assess_fd_stability(current_fds)
            
            metrics = ResourceExhaustionMetrics(
                resource_type="file_handles",
                baseline_usage=self.baseline_fds,
                peak_usage=current_fds,
                exhaustion_threshold=1000,  # Reasonable limit for open files
                recovery_time=0.0,
                performance_degradation=performance_degradation,
                system_stability=stability,
                recovery_success=True
            )
            
            self.metrics.append(metrics)
            
            # Record metrics
            self.record_metric(f"open_file_handles_{increment}", current_fds, "count")
            self.record_metric(f"file_access_degradation_{increment}", performance_degradation, "percent")
            
            time.sleep(1)
            
    def _measure_file_access_performance(self) -> float:
        """Measure file access performance."""
        start_time = time.time()
        
        # Perform file access operations
        temp_files = []
        try:
            for i in range(10):
                temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
                temp_file.write(f"performance_test_{i}")
                temp_file.seek(0)
                temp_file.read()
                temp_file.close()
                temp_files.append(temp_file.name)
                
        finally:
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        return time.time() - start_time
        
    def _assess_fd_stability(self, fd_count: int) -> str:
        """Assess system stability based on file descriptor count."""
        if fd_count < 500:
            return "stable"
        elif fd_count < 1000:
            return "degraded"
        else:
            return "unstable"
            
    def cleanup(self):
        """Clean up file handle exhaustion test."""
        self.resource_manager.cleanup()


class CPUStarvationStressScenario(StressTestScenario):
    """Test system behavior under high CPU load."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.cpu_workers: List[multiprocessing.Process] = []
        self.metrics: List[ResourceExhaustionMetrics] = []
        
    def setup(self):
        """Setup CPU starvation test."""
        self.baseline_cpu = psutil.cpu_percent(interval=1)
        self.cpu_count = multiprocessing.cpu_count()
        
    def execute_stress(self):
        """Execute CPU starvation stress test."""
        print("🔥 Starting CPU starvation stress test...")
        
        # Gradually increase CPU load
        cpu_worker_counts = [1, 2, self.cpu_count // 2, self.cpu_count, self.cpu_count * 2]
        
        for worker_count in cpu_worker_counts:
            if not self.should_continue():
                break
                
            baseline_performance = self._measure_coordination_latency()
            
            # Start CPU workers
            self._start_cpu_workers(worker_count)
            
            # Let CPU load stabilize
            time.sleep(3)
            
            # Measure CPU usage
            current_cpu = psutil.cpu_percent(interval=2)
            
            # Test coordination performance under CPU load
            stressed_performance = self._measure_coordination_latency()
            
            # Calculate metrics
            performance_degradation = (
                (stressed_performance - baseline_performance) / baseline_performance * 100
                if baseline_performance > 0 else 0
            )
            
            stability = self._assess_cpu_stability(current_cpu)
            
            metrics = ResourceExhaustionMetrics(
                resource_type="cpu",
                baseline_usage=self.baseline_cpu,
                peak_usage=current_cpu,
                exhaustion_threshold=95.0,  # 95% CPU usage threshold
                recovery_time=0.0,
                performance_degradation=performance_degradation,
                system_stability=stability,
                recovery_success=True
            )
            
            self.metrics.append(metrics)
            
            # Record metrics
            self.record_metric(f"cpu_usage_{worker_count}_workers", current_cpu, "percent")
            self.record_metric(f"coordination_latency_degradation_{worker_count}", performance_degradation, "percent")
            
            # Stop workers before next iteration
            self._stop_cpu_workers()
            time.sleep(2)  # Recovery time
            
    def _start_cpu_workers(self, count: int):
        """Start CPU-intensive worker processes."""
        def cpu_intensive_task():
            """CPU-intensive task for stress testing."""
            while True:
                # Perform CPU-intensive calculations
                sum([i**2 for i in range(10000)])
                
        self._stop_cpu_workers()  # Ensure no leftover workers
        
        for _ in range(count):
            worker = multiprocessing.Process(target=cpu_intensive_task)
            worker.start()
            self.cpu_workers.append(worker)
            
    def _stop_cpu_workers(self):
        """Stop all CPU worker processes."""
        for worker in self.cpu_workers:
            worker.terminate()
            worker.join(timeout=1)
            if worker.is_alive():
                worker.kill()
        self.cpu_workers.clear()
        
    def _measure_coordination_latency(self) -> float:
        """Measure coordination system latency."""
        start_time = time.time()
        
        # Simulate coordination operations
        for i in range(50):
            # Simulate agent status updates
            temp_data = {
                "agent_id": f"cpu_test_agent_{i}",
                "status": "active",
                "timestamp": time.time(),
                "cpu_test": True
            }
            
            # Write and read coordination data
            with tempfile.NamedTemporaryFile(mode='w+', delete=True) as f:
                json.dump(temp_data, f)
                f.seek(0)
                json.load(f)
                
        return time.time() - start_time
        
    def _assess_cpu_stability(self, cpu_percent: float) -> str:
        """Assess system stability based on CPU usage."""
        if cpu_percent < 80:
            return "stable"
        elif cpu_percent < 95:
            return "degraded"
        else:
            return "unstable"
            
    def cleanup(self):
        """Clean up CPU starvation test."""
        self._stop_cpu_workers()


# Pytest integration
@pytest.mark.stress
@pytest.mark.resource_exhaustion
class TestResourceExhaustionStress:
    """Pytest class for resource exhaustion stress tests."""
    
    def test_light_memory_exhaustion(self):
        """Test light memory exhaustion stress."""
        config = create_light_stress_config("light_memory_exhaustion")
        config.custom_params = {"max_memory_mb": 100}
        
        scenario = MemoryExhaustionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light memory exhaustion test failed: {result.error_message}"
        assert len(scenario.metrics) > 0, "Should have collected memory exhaustion metrics"
        
    def test_light_disk_exhaustion(self):
        """Test light disk space exhaustion stress."""
        config = create_light_stress_config("light_disk_exhaustion")
        config.custom_params = {"max_files": 20}
        
        scenario = DiskSpaceExhaustionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light disk exhaustion test failed: {result.error_message}"
        assert len(scenario.metrics) > 0, "Should have collected disk exhaustion metrics"
        
    def test_light_file_handle_exhaustion(self):
        """Test light file handle exhaustion stress."""
        config = create_light_stress_config("light_file_handle_exhaustion")
        config.custom_params = {"max_file_handles": 25}
        
        scenario = FileHandleExhaustionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light file handle exhaustion test failed: {result.error_message}"
        assert len(scenario.metrics) > 0, "Should have collected file handle exhaustion metrics"
        
    @pytest.mark.slow
    def test_medium_cpu_starvation(self):
        """Test medium CPU starvation stress."""
        config = create_medium_stress_config("medium_cpu_starvation")
        config.duration_seconds = 120  # Shorter duration for CPU tests
        
        scenario = CPUStarvationStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Medium CPU starvation test failed: {result.error_message}"
        assert len(scenario.metrics) > 0, "Should have collected CPU starvation metrics"


if __name__ == "__main__":
    # Run resource exhaustion stress tests directly
    runner = StressTestRunner()
    
    # Test different resource exhaustion scenarios
    scenarios = [
        MemoryExhaustionStressScenario(create_light_stress_config("memory_exhaustion", max_memory_mb=100)),
        DiskSpaceExhaustionStressScenario(create_light_stress_config("disk_exhaustion", max_files=20)),
        FileHandleExhaustionStressScenario(create_light_stress_config("file_handle_exhaustion", max_file_handles=25))
    ]
    
    results = runner.run_scenarios(scenarios)
    
    print("\n" + runner.generate_summary_report(results))
    
    # Generate resource exhaustion report
    print("\n🔍 RESOURCE EXHAUSTION ANALYSIS:")
    for result in results:
        if hasattr(result, 'metrics') and result.metrics:
            print(f"\n📊 {result.config.name}:")
            for metric_name, metric_data in result.metrics.items():
                print(f"  • {metric_name}: {metric_data['value']:.2f} {metric_data['unit']}")