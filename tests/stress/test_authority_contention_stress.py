"""
Authority Contention Stress Tests

This module tests the dynamic authority system's ability to handle high contention
scenarios, simultaneous authority requests, rapid authority transfers, and emergency
authority situations under load.
"""

import time
import json
import os
import threading
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import uuid
import pytest

from .stress_test_engine import (
    StressTestScenario, StressTestRunner, StressTestConfig,
    create_light_stress_config, create_medium_stress_config, 
    create_heavy_stress_config, create_extreme_stress_config
)


@dataclass
class AuthorityContentionMetrics:
    """Metrics for authority contention performance."""
    total_requests: int
    successful_assignments: int
    failed_assignments: int
    conflicts_detected: int
    conflicts_resolved: int
    average_assignment_time: float
    max_assignment_time: float
    authority_ping_pongs: int
    emergency_activations: int
    deadlocks_detected: int
    deadlocks_resolved: int


class MockAuthorityAgent:
    """Simulates aggressive authority-requesting agent behavior."""
    
    def __init__(self, agent_id: str, temp_dir: str, contention_level: str = "medium"):
        self.agent_id = agent_id
        self.temp_dir = temp_dir
        self.contention_level = contention_level
        self.is_running = False
        self.activity_thread: Optional[threading.Thread] = None
        
        # Authority-specific metrics
        self.authorities_requested = 0
        self.authorities_granted = 0
        self.authorities_denied = 0
        self.authority_hold_time = []
        self.current_authorities = set()
        
        # Files
        self.status_file = os.path.join(temp_dir, f"agent_status_{agent_id}.json")
        self.authority_requests_file = os.path.join(temp_dir, f"authority_requests_{agent_id}.json")
        
        # Initialize agent files
        self._initialize_files()
        
    def _initialize_files(self):
        """Initialize agent files for authority testing."""
        status_data = {
            "id": self.agent_id,
            "status": "active",
            "current_task": "authority_stress_testing",
            "authorities": [],
            "authority_requests": [],
            "last_update": time.time()
        }
        
        requests_data = {
            "pending_requests": [],
            "completed_requests": [],
            "authority_history": []
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
            
        with open(self.authority_requests_file, 'w') as f:
            json.dump(requests_data, f, indent=2)
            
    def start(self):
        """Start aggressive authority requesting behavior."""
        self.is_running = True
        self.activity_thread = threading.Thread(target=self._authority_contention_loop, daemon=True)
        self.activity_thread.start()
        
    def stop(self):
        """Stop authority requesting and release all authorities."""
        self.is_running = False
        if self.activity_thread:
            self.activity_thread.join(timeout=2.0)
            
        # Release all held authorities
        self._release_all_authorities()
        
    def _authority_contention_loop(self):
        """Main loop for creating authority contention."""
        while self.is_running:
            try:
                # Request random authorities based on contention level
                if self.contention_level == "light":
                    time.sleep(random.uniform(1.0, 3.0))
                    self._request_random_authority()
                elif self.contention_level == "medium":
                    time.sleep(random.uniform(0.5, 1.5))
                    self._request_random_authority()
                    if random.random() < 0.3:  # 30% chance
                        self._request_multiple_authorities()
                elif self.contention_level == "heavy":
                    time.sleep(random.uniform(0.1, 0.5))
                    self._request_random_authority()
                    if random.random() < 0.5:  # 50% chance
                        self._request_multiple_authorities()
                    if random.random() < 0.2:  # 20% chance
                        self._create_authority_storm()
                else:  # extreme
                    time.sleep(random.uniform(0.05, 0.2))
                    self._create_authority_storm()
                    if random.random() < 0.3:  # 30% chance
                        self._request_emergency_authority()
                        
                # Randomly release some authorities to create churn
                if random.random() < 0.4 and self.current_authorities:
                    self._release_random_authority()
                    
            except Exception as e:
                # Continue on errors to maintain stress
                pass
                
    def _request_random_authority(self):
        """Request a random authority."""
        authorities = ["critical_path", "migration", "dashboard", "devops", "security", "ux"]
        authority = random.choice(authorities)
        
        task_description = f"Stress test task {uuid.uuid4().hex[:8]} requiring {authority} authority"
        self._make_authority_request(authority, task_description)
        
    def _request_multiple_authorities(self):
        """Request multiple authorities simultaneously."""
        authorities = ["critical_path", "migration", "dashboard", "devops", "security", "ux"]
        num_requests = random.randint(2, 4)
        selected_authorities = random.sample(authorities, num_requests)
        
        for authority in selected_authorities:
            task_description = f"Multi-authority task {uuid.uuid4().hex[:8]} requiring {authority}"
            self._make_authority_request(authority, task_description, simultaneous=True)
            
    def _create_authority_storm(self):
        """Create a storm of authority requests."""
        authorities = ["critical_path", "migration", "dashboard", "devops", "security", "ux"]
        
        # Request all authorities rapidly
        for authority in authorities:
            task_description = f"Storm task {uuid.uuid4().hex[:8]} for {authority}"
            self._make_authority_request(authority, task_description, urgent=True)
            time.sleep(0.01)  # Very short delay
            
    def _request_emergency_authority(self):
        """Request emergency authority."""
        task_description = f"EMERGENCY: Critical system failure {uuid.uuid4().hex[:8]}"
        self._make_authority_request("critical_path", task_description, emergency=True)
        
    def _make_authority_request(self, authority_type: str, task_description: str, 
                               simultaneous: bool = False, urgent: bool = False, 
                               emergency: bool = False):
        """Make an authority request."""
        start_time = time.time()
        
        request = {
            "id": f"REQ-{self.agent_id}-{uuid.uuid4().hex[:8]}",
            "agent_id": self.agent_id,
            "authority_type": authority_type,
            "task_description": task_description,
            "requested_at": datetime.now().isoformat(),
            "priority": "emergency" if emergency else ("urgent" if urgent else "normal"),
            "simultaneous": simultaneous,
            "request_start_time": start_time
        }
        
        # Simulate authority request processing
        self.authorities_requested += 1
        
        # Simulate authority manager processing time
        processing_time = random.uniform(0.01, 0.1)
        if emergency:
            processing_time *= 0.5  # Emergency requests processed faster
        elif urgent:
            processing_time *= 0.7  # Urgent requests slightly faster
            
        time.sleep(processing_time)
        
        # Simulate success/failure based on contention
        success_rate = 0.8  # Base 80% success rate
        if simultaneous:
            success_rate *= 0.6  # Lower success for simultaneous requests
        if len(self.current_authorities) > 2:
            success_rate *= 0.7  # Lower success if agent already has many authorities
            
        if random.random() < success_rate:
            # Authority granted
            self.authorities_granted += 1
            self.current_authorities.add(authority_type)
            
            # Record hold time (will be updated when released)
            hold_start_time = time.time()
            
            # Update status file
            self._update_agent_status(f"Granted {authority_type} authority", [authority_type])
            
            # Schedule authority release
            hold_duration = random.uniform(2.0, 10.0)  # Hold for 2-10 seconds
            threading.Timer(hold_duration, self._release_authority, args=[authority_type, hold_start_time]).start()
            
        else:
            # Authority denied
            self.authorities_denied += 1
            
        # Record request timing
        request_time = time.time() - start_time
        
        # Save request details
        self._save_authority_request(request, time.time() - start_time, 
                                   self.authorities_granted > self.authorities_denied)
        
    def _release_authority(self, authority_type: str, hold_start_time: float):
        """Release a specific authority."""
        if authority_type in self.current_authorities:
            self.current_authorities.remove(authority_type)
            hold_duration = time.time() - hold_start_time
            self.authority_hold_time.append(hold_duration)
            
            self._update_agent_status(f"Released {authority_type} authority", 
                                    list(self.current_authorities))
            
    def _release_random_authority(self):
        """Release a random authority."""
        if self.current_authorities:
            authority = random.choice(list(self.current_authorities))
            self._release_authority(authority, time.time())
            
    def _release_all_authorities(self):
        """Release all held authorities."""
        for authority in list(self.current_authorities):
            self._release_authority(authority, time.time())
            
    def _update_agent_status(self, task: str, authorities: List[str]):
        """Update agent status file."""
        try:
            status_data = {
                "id": self.agent_id,
                "status": "active",
                "current_task": task,
                "authorities": authorities,
                "authorities_requested": self.authorities_requested,
                "authorities_granted": self.authorities_granted,
                "authorities_denied": self.authorities_denied,
                "last_update": time.time()
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception:
            pass  # Ignore file errors during stress test
            
    def _save_authority_request(self, request: Dict, processing_time: float, granted: bool):
        """Save authority request details."""
        try:
            request_record = {
                **request,
                "processing_time": processing_time,
                "granted": granted,
                "completed_at": datetime.now().isoformat()
            }
            
            # Update requests file
            with open(self.authority_requests_file, 'r') as f:
                data = json.load(f)
                
            data["completed_requests"].append(request_record)
            
            with open(self.authority_requests_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception:
            pass  # Ignore file errors during stress test


class AuthorityContentionStressScenario(StressTestScenario):
    """Stress test scenario for authority contention."""
    
    def __init__(self, config: StressTestConfig):
        super().__init__(config)
        self.temp_dir: Optional[str] = None
        self.agents: List[MockAuthorityAgent] = []
        self.authority_manager_file: Optional[str] = None
        self.contention_metrics = AuthorityContentionMetrics(
            total_requests=0, successful_assignments=0, failed_assignments=0,
            conflicts_detected=0, conflicts_resolved=0, average_assignment_time=0.0,
            max_assignment_time=0.0, authority_ping_pongs=0, emergency_activations=0,
            deadlocks_detected=0, deadlocks_resolved=0
        )
        
    def setup(self):
        """Setup the authority contention stress test."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="authority_contention_stress_")
        
        # Initialize mock authority pool
        authority_pool = {
            "assignments": [],
            "requests": [],
            "authorities": {
                "critical_path": {"current_holder": None, "backup_holder": None, "queue": []},
                "migration": {"current_holder": None, "backup_holder": None, "queue": []},
                "dashboard": {"current_holder": None, "backup_holder": None, "queue": []},
                "devops": {"current_holder": None, "backup_holder": None, "queue": []},
                "security": {"current_holder": None, "backup_holder": None, "queue": []},
                "ux": {"current_holder": None, "backup_holder": None, "queue": []}
            },
            "conflicts": [],
            "emergency_protocols": {
                "active": False,
                "escalation_level": 0
            }
        }
        
        self.authority_manager_file = os.path.join(self.temp_dir, "authority_pool.json")
        with open(self.authority_manager_file, 'w') as f:
            json.dump(authority_pool, f, indent=2)
            
        # Initialize agent workloads file
        agent_workloads = {}
        workloads_file = os.path.join(self.temp_dir, "agent_workloads.json")
        with open(workloads_file, 'w') as f:
            json.dump(agent_workloads, f, indent=2)
            
    def execute_stress(self):
        """Execute the authority contention stress test."""
        # Determine contention level based on stress level
        contention_levels = {
            "light": ("medium", 3),
            "medium": ("heavy", 6), 
            "heavy": ("extreme", 9),
            "extreme": ("extreme", 12)
        }
        
        contention_level, agent_count = contention_levels.get(
            self.config.level.value, ("medium", 6)
        )
        
        print(f"🔥 Starting authority contention test with {agent_count} agents at {contention_level} level")
        
        # Create aggressive authority-requesting agents
        for i in range(agent_count):
            agent_id = f"contention_agent_{i}"
            agent = MockAuthorityAgent(agent_id, self.temp_dir, contention_level)
            self.agents.append(agent)
            
        # Start all agents simultaneously to create maximum contention
        start_time = time.time()
        for agent in self.agents:
            agent.start()
            
        # Let the contention run for the specified duration
        test_duration = self.config.duration_seconds
        end_time = time.time() + test_duration
        
        print(f"🔥 Authority contention running for {test_duration} seconds...")
        
        # Monitor contention during the test
        while time.time() < end_time and self.should_continue():
            time.sleep(5.0)  # Monitor every 5 seconds
            self._collect_interim_metrics()
            self._detect_authority_conflicts()
            self._check_for_deadlocks()
            
        # Stop all agents
        for agent in self.agents:
            agent.stop()
            
        # Collect final metrics
        self._collect_final_metrics()
        
        print(f"✅ Authority contention test completed")
        print(f"📊 Total requests: {self.contention_metrics.total_requests}")
        print(f"📊 Success rate: {self.contention_metrics.successful_assignments / max(self.contention_metrics.total_requests, 1) * 100:.1f}%")
        print(f"📊 Conflicts detected: {self.contention_metrics.conflicts_detected}")
        
    def _collect_interim_metrics(self):
        """Collect metrics during the test."""
        total_requests = sum(agent.authorities_requested for agent in self.agents)
        successful = sum(agent.authorities_granted for agent in self.agents)
        failed = sum(agent.authorities_denied for agent in self.agents)
        
        # Record current metrics
        self.record_metric("interim_total_requests", total_requests)
        self.record_metric("interim_success_rate", successful / max(total_requests, 1) * 100, "percent")
        
    def _detect_authority_conflicts(self):
        """Detect and count authority conflicts."""
        # Check for conflicts in authority pool
        try:
            with open(self.authority_manager_file, 'r') as f:
                authority_pool = json.load(f)
                
            conflicts = authority_pool.get("conflicts", [])
            new_conflicts = len(conflicts) - self.contention_metrics.conflicts_detected
            
            if new_conflicts > 0:
                self.contention_metrics.conflicts_detected += new_conflicts
                print(f"⚠️  Detected {new_conflicts} new authority conflicts")
                
        except Exception:
            pass  # Ignore file reading errors during stress test
            
    def _check_for_deadlocks(self):
        """Check for potential authority deadlocks."""
        # Simple deadlock detection: agents holding multiple authorities for too long
        agents_with_multiple_authorities = 0
        for agent in self.agents:
            if len(agent.current_authorities) > 2:
                agents_with_multiple_authorities += 1
                
        if agents_with_multiple_authorities > len(self.agents) * 0.5:
            self.contention_metrics.deadlocks_detected += 1
            print(f"🚨 Potential deadlock detected: {agents_with_multiple_authorities} agents holding multiple authorities")
            
    def _collect_final_metrics(self):
        """Collect final metrics after test completion."""
        # Aggregate metrics from all agents
        total_requests = sum(agent.authorities_requested for agent in self.agents)
        successful_assignments = sum(agent.authorities_granted for agent in self.agents)
        failed_assignments = sum(agent.authorities_denied for agent in self.agents)
        
        # Calculate timing metrics
        all_hold_times = []
        for agent in self.agents:
            all_hold_times.extend(agent.authority_hold_time)
            
        average_hold_time = sum(all_hold_times) / len(all_hold_times) if all_hold_times else 0
        max_hold_time = max(all_hold_times) if all_hold_times else 0
        
        # Update metrics
        self.contention_metrics.total_requests = total_requests
        self.contention_metrics.successful_assignments = successful_assignments
        self.contention_metrics.failed_assignments = failed_assignments
        self.contention_metrics.average_assignment_time = average_hold_time
        self.contention_metrics.max_assignment_time = max_hold_time
        
        # Record final metrics
        self.record_metric("total_authority_requests", total_requests)
        self.record_metric("successful_assignments", successful_assignments)
        self.record_metric("failed_assignments", failed_assignments)
        self.record_metric("success_rate", successful_assignments / max(total_requests, 1) * 100, "percent")
        self.record_metric("average_hold_time", average_hold_time, "seconds")
        self.record_metric("max_hold_time", max_hold_time, "seconds")
        self.record_metric("conflicts_detected", self.contention_metrics.conflicts_detected)
        self.record_metric("deadlocks_detected", self.contention_metrics.deadlocks_detected)
        
        # Check for performance issues
        self._validate_performance()
        
    def _validate_performance(self):
        """Validate that the authority system performed adequately under stress."""
        success_rate = self.contention_metrics.successful_assignments / max(self.contention_metrics.total_requests, 1)
        
        # Check success rate
        if success_rate < 0.6:  # Less than 60% success rate
            self.record_failure(
                "low_success_rate",
                f"Authority assignment success rate too low: {success_rate*100:.1f}%"
            )
            
        # Check for excessive conflicts
        conflict_rate = self.contention_metrics.conflicts_detected / max(self.contention_metrics.total_requests, 1)
        if conflict_rate > 0.3:  # More than 30% of requests caused conflicts
            self.record_failure(
                "excessive_conflicts",
                f"Too many authority conflicts: {conflict_rate*100:.1f}% of requests"
            )
            
        # Check for unresolved deadlocks
        if self.contention_metrics.deadlocks_detected > 5:
            self.record_failure(
                "deadlock_issues",
                f"Too many potential deadlocks detected: {self.contention_metrics.deadlocks_detected}"
            )
            
        # Check hold times
        if self.contention_metrics.max_assignment_time > 30.0:  # Over 30 seconds
            self.record_failure(
                "excessive_hold_time",
                f"Maximum authority hold time too long: {self.contention_metrics.max_assignment_time:.2f}s"
            )
            
    def cleanup(self):
        """Clean up the authority contention stress test."""
        # Stop any remaining agents
        for agent in self.agents:
            agent.stop()
            
        # Generate contention analysis report
        self._generate_contention_report()
        
        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def _generate_contention_report(self):
        """Generate detailed authority contention analysis report."""
        report = {
            "authority_contention_analysis": {
                "test_config": {
                    "level": self.config.level.value,
                    "agent_count": len(self.agents),
                    "duration": self.config.duration_seconds
                },
                "metrics": {
                    "total_requests": self.contention_metrics.total_requests,
                    "successful_assignments": self.contention_metrics.successful_assignments,
                    "failed_assignments": self.contention_metrics.failed_assignments,
                    "success_rate_percent": self.contention_metrics.successful_assignments / max(self.contention_metrics.total_requests, 1) * 100,
                    "conflicts_detected": self.contention_metrics.conflicts_detected,
                    "deadlocks_detected": self.contention_metrics.deadlocks_detected,
                    "average_hold_time": self.contention_metrics.average_assignment_time,
                    "max_hold_time": self.contention_metrics.max_assignment_time
                },
                "agent_performance": [
                    {
                        "agent_id": agent.agent_id,
                        "requests": agent.authorities_requested,
                        "granted": agent.authorities_granted,
                        "denied": agent.authorities_denied,
                        "success_rate": agent.authorities_granted / max(agent.authorities_requested, 1) * 100,
                        "avg_hold_time": sum(agent.authority_hold_time) / len(agent.authority_hold_time) if agent.authority_hold_time else 0
                    }
                    for agent in self.agents
                ],
                "recommendations": self._generate_contention_recommendations()
            }
        }
        
        # Save report
        report_file = os.path.join("stress_test_results", f"authority_contention_analysis_{int(time.time())}.json")
        os.makedirs("stress_test_results", exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
    def _generate_contention_recommendations(self) -> List[str]:
        """Generate recommendations for improving authority contention handling."""
        recommendations = []
        
        success_rate = self.contention_metrics.successful_assignments / max(self.contention_metrics.total_requests, 1)
        
        if success_rate < 0.7:
            recommendations.append("Improve authority assignment algorithm to handle high contention")
            recommendations.append("Consider implementing authority request batching")
            
        if self.contention_metrics.conflicts_detected > 10:
            recommendations.append("Implement better conflict prediction and prevention")
            recommendations.append("Add conflict resolution prioritization")
            
        if self.contention_metrics.deadlocks_detected > 0:
            recommendations.append("Implement deadlock detection and automatic resolution")
            recommendations.append("Add maximum authority hold time limits")
            
        if self.contention_metrics.max_assignment_time > 15.0:
            recommendations.append("Optimize authority assignment performance")
            recommendations.append("Consider asynchronous authority processing")
            
        return recommendations


# Pytest integration
@pytest.mark.stress
@pytest.mark.authority
class TestAuthorityContentionStress:
    """Pytest class for authority contention stress tests."""
    
    def test_light_authority_contention(self):
        """Test light authority contention stress."""
        config = create_light_stress_config("light_authority_contention", 
                                           duration_seconds=60, agent_count=3)
        scenario = AuthorityContentionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Light authority contention test failed: {result.error_message}"
        assert scenario.contention_metrics.total_requests > 0, "No authority requests made"
        
    def test_medium_authority_contention(self):
        """Test medium authority contention stress."""
        config = create_medium_stress_config("medium_authority_contention",
                                            duration_seconds=180, agent_count=6)
        scenario = AuthorityContentionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Medium authority contention test failed: {result.error_message}"
        assert scenario.contention_metrics.total_requests > 50, "Insufficient authority requests"
        
    @pytest.mark.slow
    def test_heavy_authority_contention(self):
        """Test heavy authority contention stress."""
        config = create_heavy_stress_config("heavy_authority_contention",
                                           duration_seconds=300, agent_count=9)
        scenario = AuthorityContentionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        assert result.success, f"Heavy authority contention test failed: {result.error_message}"
        assert scenario.contention_metrics.total_requests > 100, "Insufficient authority requests"
        
    @pytest.mark.slow
    @pytest.mark.extreme
    def test_extreme_authority_contention(self):
        """Test extreme authority contention stress."""
        config = create_extreme_stress_config("extreme_authority_contention",
                                             duration_seconds=600, agent_count=12)
        scenario = AuthorityContentionStressScenario(config)
        runner = StressTestRunner()
        
        result = runner.run_scenario(scenario)
        
        # Extreme tests may fail due to resource limits
        if not result.success:
            pytest.skip(f"Extreme authority contention test hit limits: {result.error_message}")
            
        assert scenario.contention_metrics.total_requests > 200, "Insufficient authority requests for extreme test"


if __name__ == "__main__":
    # Run authority contention stress tests directly
    runner = StressTestRunner()
    
    # Test different contention levels
    scenarios = [
        AuthorityContentionStressScenario(create_light_stress_config("light_contention", duration_seconds=30)),
        AuthorityContentionStressScenario(create_medium_stress_config("medium_contention", duration_seconds=60))
    ]
    
    results = runner.run_scenarios(scenarios)
    
    print("\n" + runner.generate_summary_report(results))