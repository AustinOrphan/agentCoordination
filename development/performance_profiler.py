#!/usr/bin/env python3
"""
Performance Profiler for Multi-Agent Coordination System
Analyzes and optimizes system performance for scale
"""

import json
import time
import psutil
import tracemalloc
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional
import threading
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    active_threads: int
    operation_duration_ms: float
    operation_type: str
    agent_count: int
    success: bool

@dataclass
class ScalabilityTest:
    """Scalability test configuration."""
    name: str
    agent_counts: List[int]
    operations_per_agent: int
    concurrent_operations: bool
    test_duration_seconds: int

class PerformanceProfiler:
    """Profiles and optimizes system performance."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.metrics_file = self.project_root / "performance_metrics.json"
        self.optimization_file = self.project_root / "performance_optimizations.json"
        
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance baselines
        self.baselines = {
            "authority_assignment_ms": 50,
            "emergency_declaration_ms": 100,
            "task_assignment_ms": 30,
            "role_assignment_ms": 75,
            "vote_casting_ms": 25,
            "max_memory_mb": 512,
            "max_cpu_percent": 80
        }
    
    def start_monitoring(self):
        """Start continuous performance monitoring."""
        
        if self.monitoring:
            logger.warning("Performance monitoring already running")
            return
        
        self.monitoring = True
        tracemalloc.start()
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self._collect_system_metrics()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("📊 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        tracemalloc.stop()
        self._save_metrics()
        
        logger.info("📊 Performance monitoring stopped")
    
    def _collect_system_metrics(self):
        """Collect current system performance metrics."""
        
        try:
            process = psutil.Process()
            
            # System metrics
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # I/O metrics
            io_counters = process.io_counters()
            disk_read_mb = io_counters.read_bytes / 1024 / 1024
            disk_write_mb = io_counters.write_bytes / 1024 / 1024
            
            # Thread count
            thread_count = process.num_threads()
            
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                active_threads=thread_count,
                operation_duration_ms=0,
                operation_type="system_monitor",
                agent_count=6,  # Default agent count
                success=True
            )
            
            self.metrics.append(asdict(metric))
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def profile_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Profile a specific operation."""
        
        start_time = time.perf_counter()
        start_memory = tracemalloc.get_traced_memory()[0] / 1024 / 1024
        
        success = False
        result = None
        
        try:
            result = operation_func(*args, **kwargs)
            success = True
        except Exception as e:
            logger.error(f"Operation {operation_name} failed: {e}")
            result = None
        
        end_time = time.perf_counter()
        end_memory = tracemalloc.get_traced_memory()[0] / 1024 / 1024
        
        duration_ms = (end_time - start_time) * 1000
        memory_delta = end_memory - start_memory
        
        # Get system stats
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            disk_io_read_mb=0,  # Not tracked per operation
            disk_io_write_mb=0,
            active_threads=process.num_threads(),
            operation_duration_ms=duration_ms,
            operation_type=operation_name,
            agent_count=6,
            success=success
        )
        
        self.metrics.append(asdict(metric))
        
        # Check against baselines
        baseline_key = f"{operation_name.lower().replace(' ', '_')}_ms"
        if baseline_key in self.baselines:
            baseline = self.baselines[baseline_key]
            if duration_ms > baseline * 2:  # 2x baseline is concerning
                logger.warning(f"⚠️ Operation {operation_name} took {duration_ms:.1f}ms (baseline: {baseline}ms)")
        
        logger.info(f"📊 {operation_name}: {duration_ms:.1f}ms, Memory: {memory_delta:+.1f}MB")
        
        return result
    
    def run_scalability_tests(self) -> Dict:
        """Run comprehensive scalability tests."""
        
        logger.info("🔬 Starting Scalability Tests")
        
        test_configs = [
            ScalabilityTest(
                name="Authority Assignment Scale",
                agent_counts=[1, 3, 6, 12, 24],
                operations_per_agent=10,
                concurrent_operations=False,
                test_duration_seconds=30
            ),
            ScalabilityTest(
                name="Emergency Response Scale",
                agent_counts=[1, 3, 6, 12],
                operations_per_agent=5,
                concurrent_operations=True,
                test_duration_seconds=20
            ),
            ScalabilityTest(
                name="Task Assignment Scale",
                agent_counts=[1, 5, 10, 20],
                operations_per_agent=20,
                concurrent_operations=True,
                test_duration_seconds=45
            )
        ]
        
        test_results = {
            "test_suite": "Scalability Analysis",
            "start_time": datetime.now().isoformat(),
            "tests": []
        }
        
        for test_config in test_configs:
            test_result = self._run_scalability_test(test_config)
            test_results["tests"].append(test_result)
        
        test_results["end_time"] = datetime.now().isoformat()
        
        # Generate optimization recommendations
        recommendations = self._analyze_scalability_results(test_results["tests"])
        test_results["recommendations"] = recommendations
        
        # Save results
        with open(self.project_root / "scalability_test_results.json", 'w') as f:
            json.dump(test_results, f, indent=2)
        
        logger.info("🔬 Scalability tests completed")
        return test_results
    
    def _run_scalability_test(self, test_config: ScalabilityTest) -> Dict:
        """Run a single scalability test."""
        
        logger.info(f"🧪 Running {test_config.name}")
        
        test_result = {
            "test_name": test_config.name,
            "start_time": datetime.now().isoformat(),
            "results": []
        }
        
        for agent_count in test_config.agent_counts:
            logger.info(f"  Testing with {agent_count} agents")
            
            # Simulate different agent counts
            start_time = time.perf_counter()
            operations_completed = 0
            total_duration = 0
            errors = 0
            
            try:
                # Simulate operations
                for i in range(test_config.operations_per_agent):
                    op_start = time.perf_counter()
                    
                    # Simulate work based on test type
                    if "Authority" in test_config.name:
                        self._simulate_authority_operation(agent_count)
                    elif "Emergency" in test_config.name:
                        self._simulate_emergency_operation(agent_count)
                    elif "Task" in test_config.name:
                        self._simulate_task_operation(agent_count)
                    
                    op_end = time.perf_counter()
                    total_duration += (op_end - op_start) * 1000
                    operations_completed += 1
                    
                    # Check if we've exceeded test duration
                    elapsed = time.perf_counter() - start_time
                    if elapsed > test_config.test_duration_seconds:
                        break
                
            except Exception as e:
                errors += 1
                logger.error(f"Error in scalability test: {e}")
            
            # Calculate metrics
            elapsed_time = time.perf_counter() - start_time
            avg_operation_time = total_duration / operations_completed if operations_completed > 0 else 0
            operations_per_second = operations_completed / elapsed_time if elapsed_time > 0 else 0
            
            result = {
                "agent_count": agent_count,
                "operations_completed": operations_completed,
                "total_duration_seconds": elapsed_time,
                "avg_operation_time_ms": avg_operation_time,
                "operations_per_second": operations_per_second,
                "error_count": errors,
                "success_rate": (operations_completed - errors) / operations_completed if operations_completed > 0 else 0
            }
            
            test_result["results"].append(result)
            
            logger.info(f"    {operations_completed} ops, {avg_operation_time:.1f}ms avg, {operations_per_second:.1f} ops/sec")
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def _simulate_authority_operation(self, agent_count: int):
        """Simulate authority assignment operation."""
        # Simulate processing time based on agent count
        base_time = 0.01  # 10ms base
        scale_factor = agent_count * 0.002  # 2ms per agent
        time.sleep(base_time + scale_factor)
    
    def _simulate_emergency_operation(self, agent_count: int):
        """Simulate emergency response operation."""
        base_time = 0.02  # 20ms base
        scale_factor = agent_count * 0.003  # 3ms per agent
        time.sleep(base_time + scale_factor)
    
    def _simulate_task_operation(self, agent_count: int):
        """Simulate task assignment operation."""
        base_time = 0.005  # 5ms base
        scale_factor = agent_count * 0.001  # 1ms per agent
        time.sleep(base_time + scale_factor)
    
    def _analyze_scalability_results(self, test_results: List[Dict]) -> List[str]:
        """Analyze scalability test results and generate recommendations."""
        
        recommendations = []
        
        for test in test_results:
            test_name = test["test_name"]
            results = test["results"]
            
            if not results:
                continue
            
            # Analyze performance degradation
            baseline_result = results[0]  # Smallest agent count
            worst_result = results[-1]    # Largest agent count
            
            baseline_ops_per_sec = baseline_result["operations_per_second"]
            worst_ops_per_sec = worst_result["operations_per_second"]
            
            if baseline_ops_per_sec > 0:
                performance_ratio = worst_ops_per_sec / baseline_ops_per_sec
                
                if performance_ratio < 0.5:  # Performance drops below 50%
                    recommendations.append(
                        f"{test_name}: Significant performance degradation at scale. "
                        f"Consider implementing caching or connection pooling."
                    )
                elif performance_ratio < 0.7:  # Performance drops below 70%
                    recommendations.append(
                        f"{test_name}: Moderate performance impact at scale. "
                        f"Monitor resource usage and consider optimization."
                    )
            
            # Check for high error rates
            for result in results:
                if result["success_rate"] < 0.95:  # Less than 95% success
                    recommendations.append(
                        f"{test_name}: High error rate ({(1-result['success_rate'])*100:.1f}%) "
                        f"with {result['agent_count']} agents. Implement better error handling."
                    )
            
            # Check for slow operations
            for result in results:
                if result["avg_operation_time_ms"] > 1000:  # Slower than 1 second
                    recommendations.append(
                        f"{test_name}: Slow operations ({result['avg_operation_time_ms']:.0f}ms) "
                        f"with {result['agent_count']} agents. Consider async processing."
                    )
        
        if not recommendations:
            recommendations.append("✅ All systems performing within acceptable parameters")
        
        return recommendations
    
    def generate_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report."""
        
        logger.info("📈 Generating Optimization Report")
        
        # Analyze collected metrics
        if not self.metrics:
            logger.warning("No metrics collected for analysis")
            return {"error": "No metrics available"}
        
        # Calculate statistics
        cpu_usage = [m["cpu_percent"] for m in self.metrics if m["cpu_percent"] > 0]
        memory_usage = [m["memory_mb"] for m in self.metrics]
        operation_times = [m["operation_duration_ms"] for m in self.metrics if m["operation_duration_ms"] > 0]
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics_analyzed": len(self.metrics),
            "system_performance": {
                "avg_cpu_percent": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                "max_cpu_percent": max(cpu_usage) if cpu_usage else 0,
                "avg_memory_mb": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                "max_memory_mb": max(memory_usage) if memory_usage else 0,
                "avg_operation_time_ms": sum(operation_times) / len(operation_times) if operation_times else 0,
                "max_operation_time_ms": max(operation_times) if operation_times else 0
            },
            "optimizations": [],
            "performance_score": 0
        }
        
        # Generate optimization recommendations
        optimizations = []
        
        # CPU optimization
        if report["system_performance"]["max_cpu_percent"] > 90:
            optimizations.append({
                "category": "CPU",
                "priority": "high",
                "issue": f"High CPU usage ({report['system_performance']['max_cpu_percent']:.1f}%)",
                "recommendation": "Implement operation queuing and limit concurrent operations"
            })
        
        # Memory optimization
        if report["system_performance"]["max_memory_mb"] > 1024:
            optimizations.append({
                "category": "Memory",
                "priority": "medium",
                "issue": f"High memory usage ({report['system_performance']['max_memory_mb']:.0f}MB)",
                "recommendation": "Implement data cleanup and memory pooling"
            })
        
        # Operation time optimization
        if report["system_performance"]["max_operation_time_ms"] > 500:
            optimizations.append({
                "category": "Performance",
                "priority": "medium",
                "issue": f"Slow operations ({report['system_performance']['max_operation_time_ms']:.0f}ms)",
                "recommendation": "Add caching and optimize database queries"
            })
        
        report["optimizations"] = optimizations
        
        # Calculate performance score (0-100)
        score = 100
        score -= min(report["system_performance"]["max_cpu_percent"] - 50, 30)  # Penalize high CPU
        score -= min(report["system_performance"]["max_memory_mb"] - 256, 30) / 10  # Penalize high memory
        score -= min(report["system_performance"]["max_operation_time_ms"] - 100, 30) / 10  # Penalize slow ops
        score = max(0, score)
        
        report["performance_score"] = score
        
        # Save report
        with open(self.optimization_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📈 Optimization report generated (Score: {score:.0f}/100)")
        return report
    
    def _save_metrics(self):
        """Save collected metrics to file."""
        
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"💾 Saved {len(self.metrics)} performance metrics")


def demonstrate_performance_profiling():
    """Demonstrate the performance profiling system."""
    
    logger.info("📊 Starting Performance Profiling Demonstration")
    
    profiler = PerformanceProfiler()
    
    print("\n" + "="*60)
    print("📊 PERFORMANCE PROFILING DEMO")
    print("="*60)
    
    # Start monitoring
    profiler.start_monitoring()
    
    # Simulate some operations with profiling
    print("\n🔬 Profiling Operations:")
    
    def dummy_authority_operation():
        time.sleep(0.05)  # Simulate 50ms operation
        return "authority_assigned"
    
    def dummy_emergency_operation():
        time.sleep(0.1)   # Simulate 100ms operation
        return "emergency_declared"
    
    def dummy_task_operation():
        time.sleep(0.03)  # Simulate 30ms operation
        return "task_assigned"
    
    # Profile individual operations
    profiler.profile_operation("Authority Assignment", dummy_authority_operation)
    profiler.profile_operation("Emergency Declaration", dummy_emergency_operation)
    profiler.profile_operation("Task Assignment", dummy_task_operation)
    
    print("\n📈 Running Scalability Tests:")
    
    # Run scalability tests
    scalability_results = profiler.run_scalability_tests()
    
    print(f"✅ Completed {len(scalability_results['tests'])} scalability tests")
    for test in scalability_results["tests"]:
        print(f"   {test['test_name']}: {len(test['results'])} agent configurations tested")
    
    # Generate optimization report
    print("\n📋 Generating Optimization Report:")
    
    time.sleep(2)  # Let monitoring collect some data
    profiler.stop_monitoring()
    
    optimization_report = profiler.generate_optimization_report()
    
    print(f"📊 Performance Score: {optimization_report['performance_score']:.0f}/100")
    print(f"📊 Metrics Analyzed: {optimization_report['metrics_analyzed']}")
    
    if optimization_report["optimizations"]:
        print("\n💡 Optimization Recommendations:")
        for opt in optimization_report["optimizations"]:
            priority = opt["priority"].upper()
            print(f"   [{priority}] {opt['category']}: {opt['issue']}")
            print(f"       → {opt['recommendation']}")
    else:
        print("\n✅ System performing optimally")
    
    print(f"\n📈 Scalability Recommendations:")
    for rec in scalability_results.get("recommendations", []):
        print(f"   • {rec}")
    
    logger.info("📊 Performance profiling demonstration completed")


if __name__ == "__main__":
    demonstrate_performance_profiling()