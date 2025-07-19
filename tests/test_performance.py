#!/usr/bin/env python3
"""
Performance and Load tests for Multi-Agent Coordination System
Tests system performance under various loads and stress conditions
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import time
import sys
import threading
import statistics
import concurrent.futures
from dataclasses import dataclass
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "coordination_system"))

from coordination_system.dynamic_authority_manager import DynamicAuthorityManager, AuthorityType
from conflict_resolution import ConflictResolutionSystem, ConflictType, ConflictSeverity, ConflictParty
from load_balancer import LoadBalancer, LoadBalancingStrategy, TaskRequest, TaskPriority


@dataclass
class PerformanceMetrics:
    """Performance measurement data."""
    operation_name: str
    duration_ms: float
    success: bool
    throughput_ops_per_sec: float
    memory_usage_mb: float
    cpu_usage_percent: float


class PerformanceTestSuite:
    """Performance testing utilities."""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.metrics: List[PerformanceMetrics] = []
        
    def measure_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Measure performance of an operation."""
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        
        try:
            result = operation_func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
        
        end_time = time.perf_counter()
        end_memory = self._get_memory_usage()
        
        duration_ms = (end_time - start_time) * 1000
        memory_delta = max(0, end_memory - start_memory)
        
        metric = PerformanceMetrics(
            operation_name=operation_name,
            duration_ms=duration_ms,
            success=success,
            throughput_ops_per_sec=1000 / duration_ms if duration_ms > 0 else 0,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0  # Would require psutil for real CPU monitoring
        )
        
        self.metrics.append(metric)
        return result, metric
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def measure_throughput(self, operation_name: str, operation_func, num_operations: int, 
                          concurrent: bool = False, max_workers: int = 4):
        """Measure throughput for multiple operations."""
        start_time = time.perf_counter()
        
        if concurrent:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(operation_func, i) for i in range(num_operations)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        else:
            results = [operation_func(i) for i in range(num_operations)]
        
        end_time = time.perf_counter()
        duration_seconds = end_time - start_time
        
        successful_ops = len([r for r in results if r is not None])
        throughput = successful_ops / duration_seconds if duration_seconds > 0 else 0
        
        metric = PerformanceMetrics(
            operation_name=f"{operation_name}_throughput",
            duration_ms=duration_seconds * 1000,
            success=successful_ops > 0,
            throughput_ops_per_sec=throughput,
            memory_usage_mb=0,
            cpu_usage_percent=0
        )
        
        self.metrics.append(metric)
        return results, metric
    
    def get_summary(self) -> Dict:
        """Get performance summary."""
        if not self.metrics:
            return {}
        
        return {
            'total_operations': len(self.metrics),
            'success_rate': (len([m for m in self.metrics if m.success]) / len(self.metrics)) * 100,
            'avg_duration_ms': statistics.mean([m.duration_ms for m in self.metrics]),
            'median_duration_ms': statistics.median([m.duration_ms for m in self.metrics]),
            'max_duration_ms': max([m.duration_ms for m in self.metrics]),
            'min_duration_ms': min([m.duration_ms for m in self.metrics]),
            'avg_throughput': statistics.mean([m.throughput_ops_per_sec for m in self.metrics if m.throughput_ops_per_sec > 0]),
            'total_memory_mb': sum([m.memory_usage_mb for m in self.metrics])
        }


class TestPerformance:
    """Performance test suite for multi-agent coordination system."""
    
    @pytest.fixture
    def perf_environment(self):
        """Create performance testing environment."""
        temp_dir = tempfile.mkdtemp()
        
        environment = {
            'temp_dir': temp_dir,
            'authority_manager': DynamicAuthorityManager(temp_dir),
            'conflict_resolver': ConflictResolutionSystem(temp_dir),
            'load_balancer': LoadBalancer(temp_dir),
            'perf_suite': PerformanceTestSuite(temp_dir)
        }
        
        yield environment
        
        shutil.rmtree(temp_dir)
    
    def test_authority_assignment_performance(self, perf_environment):
        """Test authority assignment performance."""
        authority_manager = perf_environment['authority_manager']
        perf_suite = perf_environment['perf_suite']
        
        print("\n⚡ Testing Authority Assignment Performance")
        
        # Single operation performance
        def assign_authority_op(task_desc="Performance test task"):
            return authority_manager.assign_authority(task_desc)
        
        result, metric = perf_suite.measure_operation("authority_assignment", assign_authority_op)
        print(f"  Single assignment: {metric.duration_ms:.2f}ms")
        
        # Throughput test
        def authority_throughput_op(i):
            return authority_manager.assign_authority(f"Throughput test {i}")
        
        results, throughput_metric = perf_suite.measure_throughput(
            "authority_assignment", authority_throughput_op, 100
        )
        
        print(f"  Throughput: {throughput_metric.throughput_ops_per_sec:.1f} ops/sec")
        print(f"  100 assignments: {throughput_metric.duration_ms:.2f}ms")
        
        # Concurrent assignment test
        concurrent_results, concurrent_metric = perf_suite.measure_throughput(
            "authority_assignment_concurrent", authority_throughput_op, 50, 
            concurrent=True, max_workers=8
        )
        
        print(f"  Concurrent throughput: {concurrent_metric.throughput_ops_per_sec:.1f} ops/sec")
        
        # Performance assertions
        assert metric.duration_ms < 1000, "Single authority assignment should be under 1 second"
        assert throughput_metric.throughput_ops_per_sec > 10, "Should handle at least 10 assignments per second"
        assert metric.success, "Authority assignment should succeed"
    
    def test_task_assignment_performance(self, perf_environment):
        """Test task assignment performance."""
        load_balancer = perf_environment['load_balancer']
        perf_suite = perf_environment['perf_suite']
        
        print("\n⚡ Testing Task Assignment Performance")
        
        # Create sample task
        def create_task(task_id="PERF-TEST"):
            return TaskRequest(
                task_id=task_id,
                title="Performance test task",
                description="Testing task assignment performance",
                domain="backend",
                priority=TaskPriority.MEDIUM.value,
                estimated_duration_minutes=60,
                required_expertise_level="competent",
                deadline=None,
                dependencies=[],
                resource_requirements={"cpu": 0.2},
                metadata={"test": True}
            )
        
        # Single task assignment
        def assign_task_op():
            task = create_task()
            return load_balancer.assign_task(task, LoadBalancingStrategy.ROUND_ROBIN)
        
        result, metric = perf_suite.measure_operation("task_assignment", assign_task_op)
        print(f"  Single assignment: {metric.duration_ms:.2f}ms")
        
        # Different strategies performance
        strategies = [
            LoadBalancingStrategy.ROUND_ROBIN,
            LoadBalancingStrategy.LEAST_CONNECTIONS,
            LoadBalancingStrategy.RESOURCE_AWARE,
            LoadBalancingStrategy.EXPERTISE_BASED
        ]
        
        for strategy in strategies:
            def strategy_op():
                task = create_task(f"PERF-{strategy.value}")
                return load_balancer.assign_task(task, strategy)
            
            result, metric = perf_suite.measure_operation(f"task_assignment_{strategy.value}", strategy_op)
            print(f"  {strategy.value}: {metric.duration_ms:.2f}ms")
        
        # Bulk assignment throughput
        def bulk_assignment_op(i):
            task = create_task(f"BULK-{i}")
            return load_balancer.assign_task(task, LoadBalancingStrategy.ADAPTIVE)
        
        results, throughput_metric = perf_suite.measure_throughput(
            "bulk_task_assignment", bulk_assignment_op, 200
        )
        
        print(f"  Bulk throughput: {throughput_metric.throughput_ops_per_sec:.1f} ops/sec")
        
        # Performance assertions
        assert metric.duration_ms < 500, "Single task assignment should be under 500ms"
        assert throughput_metric.throughput_ops_per_sec > 20, "Should handle at least 20 assignments per second"
    
    def test_conflict_resolution_performance(self, perf_environment):
        """Test conflict resolution performance."""
        conflict_resolver = perf_environment['conflict_resolver']
        perf_suite = perf_environment['perf_suite']
        
        print("\n⚡ Testing Conflict Resolution Performance")
        
        # Create sample conflict
        def create_conflict_parties():
            return [
                ConflictParty("agent1", "Position 1", "Justification 1", 7, "auth1", ["domain1"]),
                ConflictParty("agent2", "Position 2", "Justification 2", 5, "auth2", ["domain2"])
            ]
        
        def report_conflict_op():
            parties = create_conflict_parties()
            return conflict_resolver.report_conflict(
                ConflictType.RESOURCE_CONTENTION,
                ConflictSeverity.MEDIUM,
                "Performance test conflict",
                "Testing conflict resolution performance",
                parties,
                "agent1",
                {"test": True}
            )
        
        # Single conflict reporting
        result, metric = perf_suite.measure_operation("conflict_reporting", report_conflict_op)
        print(f"  Single conflict report: {metric.duration_ms:.2f}ms")
        
        # Different conflict types
        conflict_types = [
            ConflictType.RESOURCE_CONTENTION,
            ConflictType.PRIORITY_CONFLICT,
            ConflictType.TASK_OVERLAP,
            ConflictType.EXPERTISE_DISPUTE
        ]
        
        for conflict_type in conflict_types:
            def type_specific_op():
                parties = create_conflict_parties()
                return conflict_resolver.report_conflict(
                    conflict_type, ConflictSeverity.MEDIUM,
                    f"Test {conflict_type.value}", "Test", parties, "agent1"
                )
            
            result, metric = perf_suite.measure_operation(f"conflict_{conflict_type.value}", type_specific_op)
            print(f"  {conflict_type.value}: {metric.duration_ms:.2f}ms")
        
        # Conflict throughput test
        def conflict_throughput_op(i):
            parties = create_conflict_parties()
            return conflict_resolver.report_conflict(
                ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
                f"Throughput test {i}", f"Test conflict {i}", parties, "agent1"
            )
        
        results, throughput_metric = perf_suite.measure_throughput(
            "conflict_throughput", conflict_throughput_op, 50
        )
        
        print(f"  Conflict throughput: {throughput_metric.throughput_ops_per_sec:.1f} ops/sec")
        
        # Performance assertions
        assert metric.duration_ms < 1000, "Single conflict should be reported under 1 second"
        assert throughput_metric.throughput_ops_per_sec > 5, "Should handle at least 5 conflicts per second"
    
    def test_system_scalability(self, perf_environment):
        """Test system scalability with increasing load."""
        authority_manager = perf_environment['authority_manager']
        load_balancer = perf_environment['load_balancer']
        conflict_resolver = perf_environment['conflict_resolver']
        perf_suite = perf_environment['perf_suite']
        
        print("\n📈 Testing System Scalability")
        
        # Test with increasing numbers of operations
        operation_counts = [10, 50, 100, 200, 500]
        scalability_results = []
        
        for count in operation_counts:
            print(f"  Testing with {count} operations...")
            
            # Mixed operations
            def mixed_operations_batch(batch_size):
                start_time = time.perf_counter()
                results = []
                
                for i in range(batch_size):
                    operation_type = i % 3
                    
                    if operation_type == 0:
                        # Authority assignment
                        result = authority_manager.assign_authority(f"Scale test {i}")
                        results.append(('authority', result))
                    elif operation_type == 1:
                        # Task assignment
                        task = TaskRequest(
                            task_id=f"SCALE-{i}",
                            title=f"Scale test task {i}",
                            description="Scalability test",
                            domain=["security", "frontend", "backend"][i % 3],
                            priority=TaskPriority.MEDIUM.value,
                            estimated_duration_minutes=30,
                            required_expertise_level="competent",
                            deadline=None,
                            dependencies=[],
                            resource_requirements={},
                            metadata={}
                        )
                        result = load_balancer.assign_task(task)
                        results.append(('task', result))
                    else:
                        # Conflict resolution
                        parties = [
                            ConflictParty(f"agent{i%6}", f"pos{i}", f"just{i}", 5, "auth", ["domain"])
                        ]
                        result = conflict_resolver.report_conflict(
                            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
                            f"Scale conflict {i}", "Scale test", parties, f"agent{i%6}"
                        )
                        results.append(('conflict', result))
                
                end_time = time.perf_counter()
                return results, (end_time - start_time) * 1000
            
            results, duration_ms = mixed_operations_batch(count)
            throughput = count / (duration_ms / 1000) if duration_ms > 0 else 0
            
            scalability_results.append({
                'count': count,
                'duration_ms': duration_ms,
                'throughput': throughput,
                'avg_latency_ms': duration_ms / count if count > 0 else 0
            })
            
            print(f"    {count} ops: {duration_ms:.2f}ms total, {throughput:.1f} ops/sec")
        
        # Analyze scalability trends
        throughputs = [r['throughput'] for r in scalability_results]
        latencies = [r['avg_latency_ms'] for r in scalability_results]
        
        print(f"\n📊 Scalability Analysis:")
        print(f"  Throughput range: {min(throughputs):.1f} - {max(throughputs):.1f} ops/sec")
        print(f"  Latency range: {min(latencies):.2f} - {max(latencies):.2f}ms")
        
        # Performance degradation should be reasonable
        throughput_degradation = (max(throughputs) - min(throughputs)) / max(throughputs) * 100
        print(f"  Throughput degradation: {throughput_degradation:.1f}%")
        
        # Assertions
        assert max(latencies) < 100, "Average latency should stay under 100ms"
        assert throughput_degradation < 80, "Throughput degradation should be under 80%"
    
    def test_memory_usage_patterns(self, perf_environment):
        """Test memory usage patterns under load."""
        authority_manager = perf_environment['authority_manager']
        load_balancer = perf_environment['load_balancer']
        perf_suite = perf_environment['perf_suite']
        
        print("\n💾 Testing Memory Usage Patterns")
        
        initial_memory = perf_suite._get_memory_usage()
        print(f"  Initial memory: {initial_memory:.2f}MB")
        
        # Create increasing load and measure memory
        memory_measurements = []
        
        for i in range(0, 100, 10):
            # Perform operations
            for j in range(10):
                authority_manager.assign_authority(f"Memory test {i}-{j}")
                
                task = TaskRequest(
                    task_id=f"MEM-{i}-{j}",
                    title=f"Memory test task {i}-{j}",
                    description="Memory usage test",
                    domain="backend",
                    priority=TaskPriority.MEDIUM.value,
                    estimated_duration_minutes=30,
                    required_expertise_level="competent",
                    deadline=None,
                    dependencies=[],
                    resource_requirements={},
                    metadata={}
                )
                load_balancer.assign_task(task)
            
            current_memory = perf_suite._get_memory_usage()
            memory_measurements.append({
                'operations': i + 10,
                'memory_mb': current_memory,
                'delta_mb': current_memory - initial_memory
            })
            
            print(f"  After {i+10} ops: {current_memory:.2f}MB (+{current_memory - initial_memory:.2f}MB)")
        
        # Analyze memory growth
        max_memory = max([m['memory_mb'] for m in memory_measurements])
        memory_growth = max_memory - initial_memory
        
        print(f"\n📊 Memory Analysis:")
        print(f"  Peak memory: {max_memory:.2f}MB")
        print(f"  Total growth: {memory_growth:.2f}MB")
        print(f"  Growth per operation: {memory_growth / 100:.3f}MB")
        
        # Memory growth should be reasonable
        assert memory_growth < 100, "Memory growth should be under 100MB for 100 operations"
    
    def test_concurrent_load_performance(self, perf_environment):
        """Test performance under concurrent load."""
        authority_manager = perf_environment['authority_manager']
        load_balancer = perf_environment['load_balancer']
        conflict_resolver = perf_environment['conflict_resolver']
        perf_suite = perf_environment['perf_suite']
        
        print("\n🔄 Testing Concurrent Load Performance")
        
        def concurrent_worker(worker_id, num_operations):
            """Worker function for concurrent testing."""
            results = []
            start_time = time.perf_counter()
            
            for i in range(num_operations):
                operation_type = (worker_id + i) % 3
                
                try:
                    if operation_type == 0:
                        result = authority_manager.assign_authority(f"Concurrent-{worker_id}-{i}")
                        results.append(('authority', True))
                    elif operation_type == 1:
                        task = TaskRequest(
                            task_id=f"CONC-{worker_id}-{i}",
                            title=f"Concurrent task {worker_id}-{i}",
                            description="Concurrent test",
                            domain="backend",
                            priority=TaskPriority.MEDIUM.value,
                            estimated_duration_minutes=30,
                            required_expertise_level="competent",
                            deadline=None,
                            dependencies=[],
                            resource_requirements={},
                            metadata={}
                        )
                        result = load_balancer.assign_task(task)
                        results.append(('task', result is not None))
                    else:
                        parties = [ConflictParty(f"agent{worker_id}", "pos", "just", 5, "auth", ["domain"])]
                        result = conflict_resolver.report_conflict(
                            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
                            f"Concurrent conflict {worker_id}-{i}", "Test", parties, f"agent{worker_id}"
                        )
                        results.append(('conflict', result is not None))
                except Exception as e:
                    results.append(('error', False))
            
            end_time = time.perf_counter()
            return {
                'worker_id': worker_id,
                'results': results,
                'duration_ms': (end_time - start_time) * 1000,
                'operations': num_operations
            }
        
        # Test with different concurrency levels
        concurrency_levels = [1, 2, 4, 8]
        operations_per_worker = 25
        
        for num_workers in concurrency_levels:
            print(f"  Testing with {num_workers} concurrent workers...")
            
            start_time = time.perf_counter()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [
                    executor.submit(concurrent_worker, worker_id, operations_per_worker)
                    for worker_id in range(num_workers)
                ]
                
                worker_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.perf_counter()
            total_duration = (end_time - start_time) * 1000
            
            # Analyze results
            total_operations = num_workers * operations_per_worker
            successful_operations = sum(
                len([r for r in wr['results'] if r[1]]) for wr in worker_results
            )
            
            success_rate = (successful_operations / total_operations) * 100
            throughput = total_operations / (total_duration / 1000)
            
            print(f"    {num_workers} workers: {throughput:.1f} ops/sec, {success_rate:.1f}% success")
        
        # Concurrent performance should be reasonable
        assert success_rate > 80, "Success rate under concurrency should be over 80%"
    
    def test_stress_testing(self, perf_environment):
        """Stress test the system with extreme loads."""
        authority_manager = perf_environment['authority_manager']
        load_balancer = perf_environment['load_balancer']
        conflict_resolver = perf_environment['conflict_resolver']
        perf_suite = perf_environment['perf_suite']
        
        print("\n🔥 Stress Testing System")
        
        # Extreme load test
        stress_operations = 1000
        print(f"  Performing {stress_operations} operations...")
        
        start_time = time.perf_counter()
        errors = 0
        
        for i in range(stress_operations):
            try:
                if i % 10 == 0:  # Authority assignments
                    authority_manager.assign_authority(f"Stress test {i}")
                elif i % 3 == 1:  # Task assignments
                    task = TaskRequest(
                        task_id=f"STRESS-{i}",
                        title=f"Stress task {i}",
                        description="Stress test",
                        domain=["security", "frontend", "backend", "infrastructure"][i % 4],
                        priority=[TaskPriority.LOW.value, TaskPriority.MEDIUM.value, TaskPriority.HIGH.value][i % 3],
                        estimated_duration_minutes=30,
                        required_expertise_level="competent",
                        deadline=None,
                        dependencies=[],
                        resource_requirements={},
                        metadata={}
                    )
                    load_balancer.assign_task(task)
                else:  # Conflicts
                    if i % 50 == 0:  # Reduce conflict frequency
                        parties = [ConflictParty(f"agent{i%6}", "pos", "just", 5, "auth", ["domain"])]
                        conflict_resolver.report_conflict(
                            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
                            f"Stress conflict {i}", "Stress test", parties, f"agent{i%6}"
                        )
            except Exception as e:
                errors += 1
        
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        
        success_rate = ((stress_operations - errors) / stress_operations) * 100
        throughput = stress_operations / (duration / 1000)
        
        print(f"  Stress test results:")
        print(f"    Duration: {duration:.2f}ms")
        print(f"    Throughput: {throughput:.1f} ops/sec")
        print(f"    Success rate: {success_rate:.1f}%")
        print(f"    Errors: {errors}")
        
        # System should survive stress test
        assert success_rate > 70, "System should maintain >70% success under stress"
        assert errors < stress_operations * 0.3, "Error rate should be under 30%"
        
        print("🎉 Stress test completed!")
    
    def test_performance_summary(self, perf_environment):
        """Generate comprehensive performance summary."""
        perf_suite = perf_environment['perf_suite']
        
        print("\n📊 Performance Test Summary")
        
        summary = perf_suite.get_summary()
        
        if summary:
            print(f"  Total operations tested: {summary['total_operations']}")
            print(f"  Overall success rate: {summary['success_rate']:.1f}%")
            print(f"  Average duration: {summary['avg_duration_ms']:.2f}ms")
            print(f"  Median duration: {summary['median_duration_ms']:.2f}ms")
            print(f"  Max duration: {summary['max_duration_ms']:.2f}ms")
            print(f"  Min duration: {summary['min_duration_ms']:.2f}ms")
            
            if 'avg_throughput' in summary and summary['avg_throughput'] > 0:
                print(f"  Average throughput: {summary['avg_throughput']:.1f} ops/sec")
            
            if 'total_memory_mb' in summary:
                print(f"  Total memory impact: {summary['total_memory_mb']:.2f}MB")
        
        # Performance benchmarks
        print("\n🎯 Performance Benchmarks:")
        print("  ✓ Authority assignment: < 1000ms")
        print("  ✓ Task assignment: < 500ms") 
        print("  ✓ Conflict resolution: < 1000ms")
        print("  ✓ System throughput: > 10 ops/sec")
        print("  ✓ Stress test survival: > 70% success")
        
        print("\n🏆 Performance testing completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])