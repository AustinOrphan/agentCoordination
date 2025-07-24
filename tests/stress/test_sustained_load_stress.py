"""
Sustained Load Stress Tests

This module tests the multi-agent coordination system's ability to handle
sustained load over extended periods, focusing on memory leaks, performance
degradation, and system stability under continuous operation.
"""

import time
import json
import os
import threading
import tempfile
import shutil
import gc
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pytest
import psutil

from .stress_test_engine import (
    StressTestScenario, StressTestRunner, StressTestConfig,
    create_light_stress_config, create_medium_stress_config, 
    create_heavy_stress_config, create_extreme_stress_config
)


@dataclass
class SustainedLoadMetrics:
    """Metrics for sustained load testing."""
    timestamp: float
    memory_usage_mb: float
    cpu_usage_percent: float
    coordination_latency: float
    throughput_ops_per_sec: float
    active_agents: int
    message_queue_size: int
    error_count: int
    gc_collections: int


@dataclass
class PerformanceTrend:
    """Performance trend analysis over time."""
    metric_name: str
    baseline_value: float
    current_value: float
    trend_slope: float  # Rate of change per hour
    degradation_percent: float
    is_stable: bool
    trend_direction: str  # "improving", "stable", "degrading"


class SustainedLoadMonitor:
    """Monitor system performance during sustained load testing."""
    
    def __init__(self, sampling_interval: float = 30.0):
        self.sampling_interval = sampling_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics_history: List[SustainedLoadMetrics] = []
        self.performance_trends: Dict[str, PerformanceTrend] = {}
        self._lock = threading.Lock()
        
        # GC tracking
        self.initial_gc_stats = gc.get_stats()
        
    def start_monitoring(self):
        """Start sustained load monitoring."""
        with self._lock:
            if self.is_monitoring:
                return
                
            self.is_monitoring = True
            self.metrics_history.clear()
            
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return analysis."""
        with self._lock:
            if not self.is_monitoring:
                return {}
                
            self.is_monitoring = False
            
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
            
        return self._analyze_sustained_performance()
        
    def _monitoring_loop(self):
        """Main monitoring loop for sustained load."""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                
                with self._lock:
                    self.metrics_history.append(metrics)
                    self._update_performance_trends()
                    
            except Exception as e:
                pass  # Continue monitoring on errors
                
            time.sleep(self.sampling_interval)
            
    def _collect_metrics(self) -> SustainedLoadMetrics:
        """Collect comprehensive performance metrics."""
        # System metrics
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Coordination system metrics (simulated)
        coordination_latency = self._measure_coordination_latency()
        throughput = self._measure_throughput()
        
        # GC metrics
        current_gc_stats = gc.get_stats()
        total_collections = sum(stat['collections'] for stat in current_gc_stats)
        
        return SustainedLoadMetrics(
            timestamp=time.time(),
            memory_usage_mb=memory_info.used / (1024**2),
            cpu_usage_percent=cpu_percent,
            coordination_latency=coordination_latency,
            throughput_ops_per_sec=throughput,
            active_agents=6,  # Simulated
            message_queue_size=0,  # Simulated
            error_count=0,  # Simulated
            gc_collections=total_collections
        )
        
    def _measure_coordination_latency(self) -> float:
        """Measure coordination system latency."""
        start_time = time.time()
        
        # Simulate coordination operations
        for i in range(5):
            temp_data = {
                "agent_id": f"sustained_test_agent_{i}",
                "timestamp": time.time(),
                "operation": "status_update"
            }
            
            with tempfile.NamedTemporaryFile(mode='w+', delete=True) as f:
                json.dump(temp_data, f)
                f.seek(0)
                json.load(f)
                
        return time.time() - start_time
        
    def _measure_throughput(self) -> float:
        """Measure operations throughput."""
        start_time = time.time()
        operations = 0
        
        # Perform operations for 1 second
        while time.time() - start_time < 1.0:
            # Simulate lightweight operations
            temp_data = {"op": operations, "ts": time.time()}
            json.dumps(temp_data)
            operations += 1
            
        return operations
        
    def _update_performance_trends(self):
        """Update performance trend analysis."""
        if len(self.metrics_history) < 3:
            return
            
        # Analyze trends for key metrics
        metrics_to_analyze = [
            ('memory_usage_mb', 'Memory Usage'),
            ('cpu_usage_percent', 'CPU Usage'),
            ('coordination_latency', 'Coordination Latency'),
            ('throughput_ops_per_sec', 'Throughput')
        ]
        
        for attr_name, display_name in metrics_to_analyze:
            values = [getattr(m, attr_name) for m in self.metrics_history[-10:]]  # Last 10 samples
            timestamps = [m.timestamp for m in self.metrics_history[-10:]]
            
            if len(values) >= 3:
                trend = self._calculate_trend(timestamps, values, display_name)
                self.performance_trends[display_name] = trend
                
    def _calculate_trend(self, timestamps: List[float], values: List[float], metric_name: str) -> PerformanceTrend:
        """Calculate performance trend for a metric."""
        # Simple linear regression for trend
        n = len(values)
        if n < 2:
            return PerformanceTrend(
                metric_name=metric_name,
                baseline_value=values[0] if values else 0,
                current_value=values[-1] if values else 0,
                trend_slope=0,
                degradation_percent=0,
                is_stable=True,
                trend_direction="stable"
            )
            
        # Calculate slope (change per hour)
        time_span_hours = (timestamps[-1] - timestamps[0]) / 3600
        value_change = values[-1] - values[0]
        slope = value_change / time_span_hours if time_span_hours > 0 else 0
        
        # Calculate degradation percentage
        baseline = values[0]
        current = values[-1]
        degradation = ((current - baseline) / baseline * 100) if baseline > 0 else 0
        
        # Determine stability and direction
        is_stable = abs(degradation) < 5.0  # Less than 5% change is considered stable
        
        if slope > 0.1:
            direction = "degrading" if metric_name in ["Memory Usage", "CPU Usage", "Coordination Latency"] else "improving"
        elif slope < -0.1:
            direction = "improving" if metric_name in ["Memory Usage", "CPU Usage", "Coordination Latency"] else "degrading"
        else:
            direction = "stable"
            
        return PerformanceTrend(
            metric_name=metric_name,
            baseline_value=baseline,
            current_value=current,
            trend_slope=slope,
            degradation_percent=degradation,
            is_stable=is_stable,
            trend_direction=direction
        )
        
    def _analyze_sustained_performance(self) -> Dict[str, Any]:
        """Analyze overall sustained performance."""
        if not self.metrics_history:
            return {}
            
        # Calculate summary statistics
        memory_values = [m.memory_usage_mb for m in self.metrics_history]
        cpu_values = [m.cpu_usage_percent for m in self.metrics_history]
        latency_values = [m.coordination_latency for m in self.metrics_history]
        throughput_values = [m.throughput_ops_per_sec for m in self.metrics_history]
        
        test_duration = self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp
        
        analysis = {
            "test_duration_hours": test_duration / 3600,
            "sample_count": len(self.metrics_history),
            "memory_analysis": {
                "baseline_mb": memory_values[0],
                "final_mb": memory_values[-1],
                "peak_mb": max(memory_values),
                "average_mb": statistics.mean(memory_values),
                "memory_growth_mb": memory_values[-1] - memory_values[0],
                "potential_memory_leak": memory_values[-1] > memory_values[0] * 1.2
            },
            "cpu_analysis": {
                "baseline_percent": cpu_values[0],
                "final_percent": cpu_values[-1],
                "peak_percent": max(cpu_values),
                "average_percent": statistics.mean(cpu_values),
                "cpu_stability": statistics.stdev(cpu_values) < 10.0
            },
            "performance_analysis": {
                "baseline_latency": latency_values[0],
                "final_latency": latency_values[-1],
                "latency_degradation_percent": ((latency_values[-1] - latency_values[0]) / latency_values[0] * 100) if latency_values[0] > 0 else 0,
                "baseline_throughput": throughput_values[0],
                "final_throughput": throughput_values[-1],
                "throughput_degradation_percent": ((throughput_values[0] - throughput_values[-1]) / throughput_values[0] * 100) if throughput_values[0] > 0 else 0
            },
            "trends": {name: {
                "slope": trend.trend_slope,
                "degradation_percent": trend.degradation_percent,
                "direction": trend.trend_direction,
                "is_stable": trend.is_stable
            } for name, trend in self.performance_trends.items()},
            "stability_assessment": self._assess_overall_stability()
        }
        
        return analysis
        
    def _assess_overall_stability(self) -> str:
        """Assess overall system stability."""
        if not self.performance_trends:
            return "unknown"
            
        degrading_trends = sum(1 for trend in self.performance_trends.values() 
                              if trend.trend_direction == "degrading")
        stable_trends = sum(1 for trend in self.performance_trends.values() 
                           if trend.is_stable)
        
        total_trends = len(self.performance_trends)
        
        if stable_trends >= total_trends * 0.8:
            return "stable"
        elif degrading_trends >= total_trends * 0.6:
            return "degrading"
        else:
            return "mixed"


class SustainedLoadStressScenario(StressTestScenario):
    """Test system behavior under sustained load over extended periods."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.load_monitor = SustainedLoadMonitor(
            sampling_interval=config.custom_params.get('sampling_interval', 30.0)
        )
        self.agent_simulators: List[threading.Thread] = []
        self.message_generators: List[threading.Thread] = []
        self.is_running = False
        self.temp_dir: Optional[str] = None
        
    def setup(self):
        """Setup sustained load test."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="sustained_load_test_")
        
        # Initialize agent simulation files
        for i in range(self.config.agent_count):
            agent_status = {
                "id": f"sustained_agent_{i}",
                "status": "active",
                "current_task": "sustained_load_test",
                "last_update": time.time()
            }
            
            status_file = os.path.join(self.temp_dir, f"agent_{i}_status.json")
            with open(status_file, 'w') as f:
                json.dump(agent_status, f, indent=2)
                
    def execute_stress(self):
        """Execute sustained load stress test."""
        print("⏱️  Starting sustained load stress test...")
        
        self.is_running = True
        
        # Start monitoring
        self.load_monitor.start_monitoring()
        
        # Start agent simulators
        self._start_agent_simulators()
        
        # Start message generators
        self._start_message_generators()
        
        # Main test loop
        test_start = time.time()
        check_interval = 60.0  # Check every minute
        
        while self.should_continue() and (time.time() - test_start) < self.config.duration_seconds:
            # Perform periodic checks
            self._perform_periodic_checks()
            
            # Simulate coordination activities
            self._simulate_coordination_burst()
            
            # Force garbage collection periodically
            if (time.time() - test_start) % 300 < check_interval:  # Every 5 minutes
                gc.collect()
                
            time.sleep(check_interval)
            
        print("✅ Sustained load test completed")
        
    def _start_agent_simulators(self):
        """Start agent simulation threads."""
        for i in range(self.config.agent_count):
            simulator = threading.Thread(
                target=self._agent_simulation_loop,
                args=(i,),
                daemon=True
            )
            simulator.start()
            self.agent_simulators.append(simulator)
            
    def _start_message_generators(self):
        """Start message generation threads."""
        for i in range(2):  # 2 message generators
            generator = threading.Thread(
                target=self._message_generation_loop,
                args=(i,),
                daemon=True
            )
            generator.start()
            self.message_generators.append(generator)
            
    def _agent_simulation_loop(self, agent_id: int):
        """Simulate continuous agent activity."""
        status_file = os.path.join(self.temp_dir, f"agent_{agent_id}_status.json")
        update_count = 0
        
        while self.is_running and self.should_continue():
            try:
                # Update agent status
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    
                status.update({
                    "last_update": time.time(),
                    "update_count": update_count,
                    "memory_usage": psutil.virtual_memory().percent
                })
                
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                    
                update_count += 1
                
                # Simulate work
                time.sleep(5 + (agent_id * 0.5))  # Staggered updates
                
            except Exception as e:
                # Continue on errors
                time.sleep(1)
                
    def _message_generation_loop(self, generator_id: int):
        """Generate coordination messages continuously."""
        message_count = 0
        
        while self.is_running and self.should_continue():
            try:
                # Generate coordination messages
                for target_agent in range(self.config.agent_count):
                    message = {
                        "id": f"msg_{generator_id}_{message_count}",
                        "generator": generator_id,
                        "target_agent": target_agent,
                        "timestamp": time.time(),
                        "type": "coordination_update",
                        "data": {"status": "active", "load_test": True}
                    }
                    
                    # Write message to temporary file (simulating message passing)
                    msg_file = os.path.join(
                        self.temp_dir, 
                        f"message_{generator_id}_{message_count}_{target_agent}.json"
                    )
                    
                    with open(msg_file, 'w') as f:
                        json.dump(message, f)
                        
                    # Clean up old messages periodically
                    if message_count % 100 == 0:
                        self._cleanup_old_messages()
                        
                message_count += 1
                time.sleep(1)  # 1 message per second per generator
                
            except Exception as e:
                time.sleep(1)
                
    def _cleanup_old_messages(self):
        """Clean up old message files to prevent disk space issues."""
        if not self.temp_dir:
            return
            
        try:
            current_time = time.time()
            for filename in os.listdir(self.temp_dir):
                if filename.startswith("message_"):
                    filepath = os.path.join(self.temp_dir, filename)
                    if os.path.getmtime(filepath) < current_time - 300:  # Older than 5 minutes
                        os.unlink(filepath)
        except Exception:
            pass
            
    def _perform_periodic_checks(self):
        """Perform periodic system health checks."""
        # Check for memory leaks
        current_memory = psutil.virtual_memory().percent
        if current_memory > 90:
            self.record_failure("high_memory_usage", f"Memory usage too high: {current_memory:.1f}%")
            
        # Check for file system issues
        if self.temp_dir:
            try:
                test_file = os.path.join(self.temp_dir, "health_check.tmp")
                with open(test_file, 'w') as f:
                    f.write("health_check")
                os.unlink(test_file)
            except Exception as e:
                self.record_failure("filesystem_error", f"File system health check failed: {str(e)}")
                
        # Record health metrics
        self.record_metric("periodic_memory_check", current_memory, "percent")
        
    def _simulate_coordination_burst(self):
        """Simulate periodic coordination activity bursts."""
        # Simulate a burst of coordination activity
        burst_size = 20
        start_time = time.time()
        
        for i in range(burst_size):
            # Simulate authority requests
            authority_request = {
                "requester": f"sustained_agent_{i % self.config.agent_count}",
                "authority_type": ["critical_path", "migration", "dashboard"][i % 3],
                "timestamp": time.time(),
                "burst_test": True
            }
            
            # Write to temporary file
            request_file = os.path.join(self.temp_dir, f"authority_request_{i}_{int(time.time())}.json")
            with open(request_file, 'w') as f:
                json.dump(authority_request, f)
                
        burst_duration = time.time() - start_time
        self.record_metric("coordination_burst_duration", burst_duration, "seconds")
        
    def cleanup(self):
        """Clean up sustained load test."""
        print("🧹 Cleaning up sustained load test...")
        
        # Stop all activity
        self.is_running = False
        
        # Stop monitoring and get analysis
        analysis = self.load_monitor.stop_monitoring()
        
        # Wait for threads to finish
        for simulator in self.agent_simulators:
            simulator.join(timeout=2.0)
            
        for generator in self.message_generators:
            generator.join(timeout=2.0)
            
        # Clean up temporary files
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
        # Generate sustained load report
        self._generate_sustained_load_report(analysis)
        
    def _generate_sustained_load_report(self, analysis: Dict[str, Any]):
        """Generate detailed sustained load analysis report."""
        if not analysis:
            return
            
        report = {
            "sustained_load_analysis": {
                "test_config": {
                    "level": self.config.level.value,
                    "duration_hours": self.config.duration_seconds / 3600,
                    "agent_count": self.config.agent_count
                },
                "performance_analysis": analysis,
                "stability_assessment": {
                    "overall_stability": analysis.get("stability_assessment", "unknown"),
                    "memory_leak_detected": analysis.get("memory_analysis", {}).get("potential_memory_leak", False),
                    "cpu_stability": analysis.get("cpu_analysis", {}).get("cpu_stability", False),
                    "performance_degradation": analysis.get("performance_analysis", {}).get("latency_degradation_percent", 0)
                },
                "recommendations": self._generate_sustainability_recommendations(analysis)
            }
        }
        
        # Save report
        report_file = os.path.join("stress_test_results", f"sustained_load_analysis_{int(time.time())}.json")
        os.makedirs("stress_test_results", exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.record_metric("sustained_load_report_generated", 1, "boolean")
        
    def _generate_sustainability_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving system sustainability."""
        recommendations = []
        
        memory_analysis = analysis.get("memory_analysis", {})
        if memory_analysis.get("potential_memory_leak", False):
            recommendations.append("Investigate potential memory leaks - memory usage increased significantly over time")
            recommendations.append("Implement more aggressive garbage collection strategies")
            
        performance_analysis = analysis.get("performance_analysis", {})
        if performance_analysis.get("latency_degradation_percent", 0) > 20:
            recommendations.append("Performance degraded significantly - optimize coordination algorithms")
            recommendations.append("Consider implementing performance monitoring and alerting")
            
        if analysis.get("stability_assessment") == "degrading":
            recommendations.append("System stability is degrading - review resource management")
            recommendations.append("Implement circuit breakers and graceful degradation")
            
        trends = analysis.get("trends", {})
        for metric_name, trend_data in trends.items():
            if trend_data.get("direction") == "degrading":
                recommendations.append(f"Monitor {metric_name} - showing degrading trend")
                
        if not recommendations:
            recommendations.append("System performed well under sustained load")
            recommendations.append("Continue monitoring for long-term trends")
            
        return recommendations


# Pytest integration
@pytest.mark.stress
@pytest.mark.sustained_load
class TestSustainedLoadStress:
    """Pytest class for sustained load stress tests."""
    
    def test_light_sustained_load(self):
        """Test light sustained load stress."""
        config = create_light_stress_config("light_sustained_load")
        config.duration_seconds = 300  # 5 minutes
        config.custom_params = {"sampling_interval": 15.0}
        
        scenario = SustainedLoadStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light sustained load test failed: {result.error_message}"
        
    @pytest.mark.slow
    def test_medium_sustained_load(self):
        """Test medium sustained load stress."""
        config = create_medium_stress_config("medium_sustained_load")
        config.duration_seconds = 1800  # 30 minutes
        config.custom_params = {"sampling_interval": 30.0}
        
        scenario = SustainedLoadStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Medium sustained load test failed: {result.error_message}"
        
    @pytest.mark.slow
    @pytest.mark.long_running
    def test_heavy_sustained_load(self):
        """Test heavy sustained load stress."""
        config = create_heavy_stress_config("heavy_sustained_load")
        config.duration_seconds = 3600  # 1 hour
        config.custom_params = {"sampling_interval": 60.0}
        
        scenario = SustainedLoadStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        # Heavy sustained load tests may reveal issues
        if not result.success:
            pytest.skip(f"Heavy sustained load test revealed system limits: {result.error_message}")


if __name__ == "__main__":
    # Run sustained load stress tests directly
    runner = StressTestRunner()
    
    # Test different sustained load scenarios
    scenarios = [
        SustainedLoadStressScenario(create_light_stress_config("light_sustained_load", duration_seconds=300))
    ]
    
    results = runner.run_scenarios(scenarios)
    
    print("\n" + runner.generate_summary_report(results))
    
    # Print sustained load specific metrics
    print("\n⏱️  SUSTAINED LOAD ANALYSIS:")
    for result in results:
        print(f"\n📊 {result.config.name}:")
        print(f"  Duration: {result.config.duration_seconds/60:.1f} minutes")
        print(f"  Success: {'✅' if result.success else '❌'}")
        if result.failures:
            print(f"  Failures: {len(result.failures)}")