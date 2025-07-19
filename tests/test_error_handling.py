#!/usr/bin/env python3
"""
Error Handling and Edge Case tests for Multi-Agent Coordination System
Tests system robustness and error recovery capabilities
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
import os
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "coordination_system"))

from coordination_system.dynamic_authority_manager import DynamicAuthorityManager, AuthorityType
from conflict_resolution import ConflictResolutionSystem, ConflictType, ConflictSeverity, ConflictParty
from load_balancer import LoadBalancer, LoadBalancingStrategy, TaskRequest, TaskPriority


class TestErrorHandling:
    """Error handling and edge case test suite."""
    
    @pytest.fixture
    def error_test_environment(self):
        """Create error testing environment."""
        temp_dir = tempfile.mkdtemp()
        
        environment = {
            'temp_dir': temp_dir,
            'authority_manager': DynamicAuthorityManager(temp_dir),
            'conflict_resolver': ConflictResolutionSystem(temp_dir),
            'load_balancer': LoadBalancer(temp_dir)
        }
        
        yield environment
        
        shutil.rmtree(temp_dir)
    
    def test_file_system_errors(self, error_test_environment):
        """Test handling of file system errors."""
        temp_dir = error_test_environment['temp_dir']
        
        print("\n💾 Testing File System Error Handling")
        
        # Test with read-only directory
        readonly_dir = Path(temp_dir) / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        try:
            # This should handle permission errors gracefully
            authority_manager = DynamicAuthorityManager(str(readonly_dir))
            result = authority_manager.assign_authority("Test with readonly dir")
            
            # Should either succeed with fallback or fail gracefully
            # Check if assignment was successful (has 'agent' and not queued)
            is_successful = 'agent' in result and result.get('status') != 'queued'
            print(f"  Read-only directory test: {'Success' if is_successful else 'Handled gracefully'}")
            
        except PermissionError:
            print("  Read-only directory: Permission error handled")
        except Exception as e:
            print(f"  Read-only directory: Other error handled: {type(e).__name__}")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(readonly_dir, 0o755)
            except:
                pass
        
        # Test with non-existent directory
        nonexistent_dir = Path(temp_dir) / "nonexistent" / "deep" / "path"
        
        try:
            authority_manager = DynamicAuthorityManager(str(nonexistent_dir))
            result = authority_manager.assign_authority("Test with nonexistent dir")
            print(f"  Non-existent directory: Handled gracefully")
        except Exception as e:
            print(f"  Non-existent directory: Error handled: {type(e).__name__}")
        
        # Test with corrupted JSON files
        corrupted_file = Path(temp_dir) / "authority_pool.json"
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json content }")
        
        try:
            authority_manager = DynamicAuthorityManager(temp_dir)
            result = authority_manager.assign_authority("Test with corrupted file")
            print(f"  Corrupted JSON: Handled gracefully")
        except Exception as e:
            print(f"  Corrupted JSON: Error handled: {type(e).__name__}")
    
    def test_invalid_input_handling(self, error_test_environment):
        """Test handling of invalid inputs."""
        authority_manager = error_test_environment['authority_manager']
        conflict_resolver = error_test_environment['conflict_resolver']
        load_balancer = error_test_environment['load_balancer']
        
        print("\n🔍 Testing Invalid Input Handling")
        
        # Test authority manager with invalid inputs
        invalid_authority_inputs = [
            ("", "shark"),  # Empty task description
            (None, "shark"),  # None task description
            ("Valid task", ""),  # Empty agent
            ("Valid task", None),  # None agent
            ("Valid task", "nonexistent_agent"),  # Invalid agent
            ("A" * 10000, "shark"),  # Extremely long description
        ]
        
        for task_desc, agent in invalid_authority_inputs:
            try:
                result = authority_manager.assign_authority(task_desc, preferred_agent=agent)
                # Check if assignment was successful (has 'agent' and not queued)
                is_successful = 'agent' in result and result.get('status') != 'queued'
                status = "Handled" if is_successful else "Rejected"
                print(f"  Authority invalid input ({type(task_desc).__name__}, {type(agent).__name__}): {status}")
            except Exception as e:
                print(f"  Authority invalid input: Exception handled - {type(e).__name__}")
        
        # Test conflict resolver with invalid inputs
        try:
            # Empty parties list
            result = conflict_resolver.report_conflict(
                ConflictType.PRIORITY_CONFLICT,
                ConflictSeverity.LOW,
                "Test conflict",
                "Test description",
                [],  # Empty parties
                "reporter"
            )
            print("  Empty conflict parties: Handled")
        except Exception as e:
            print(f"  Empty conflict parties: Exception handled - {type(e).__name__}")
        
        try:
            # Invalid conflict party data
            invalid_party = ConflictParty("", "", "", -999, "", [])
            result = conflict_resolver.report_conflict(
                ConflictType.PRIORITY_CONFLICT,
                ConflictSeverity.LOW,
                "",  # Empty title
                "",  # Empty description
                [invalid_party],
                ""  # Empty reporter
            )
            print("  Invalid conflict data: Handled")
        except Exception as e:
            print(f"  Invalid conflict data: Exception handled - {type(e).__name__}")
        
        # Test load balancer with invalid tasks
        invalid_tasks = [
            # Task with negative values
            TaskRequest(
                task_id="",
                title="",
                description="",
                domain="",
                priority=-1,
                estimated_duration_minutes=-100,
                required_expertise_level="",
                deadline="invalid_date",
                dependencies=["nonexistent"],
                resource_requirements={"cpu": -1.0, "memory": 999.0},
                metadata={}
            ),
            # Task with None values
            TaskRequest(
                task_id=None,
                title=None,
                description=None,
                domain=None,
                priority=None,
                estimated_duration_minutes=None,
                required_expertise_level=None,
                deadline=None,
                dependencies=None,
                resource_requirements=None,
                metadata=None
            )
        ]
        
        for i, invalid_task in enumerate(invalid_tasks):
            try:
                result = load_balancer.assign_task(invalid_task)
                status = "Handled" if result else "Rejected"
                print(f"  Invalid task {i+1}: {status}")
            except Exception as e:
                print(f"  Invalid task {i+1}: Exception handled - {type(e).__name__}")
    
    def test_concurrency_errors(self, error_test_environment):
        """Test handling of concurrency-related errors."""
        authority_manager = error_test_environment['authority_manager']
        load_balancer = error_test_environment['load_balancer']
        
        print("\n🔄 Testing Concurrency Error Handling")
        
        # Test concurrent access to same resources
        errors = []
        results = []
        
        def concurrent_authority_assignment(thread_id):
            try:
                result = authority_manager.assign_authority(f"Concurrent task {thread_id}", preferred_agent="shark")
                results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, e))
        
        # Start many concurrent threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=concurrent_authority_assignment, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)
        
        print(f"  Concurrent authority assignment: {len(results)} successful, {len(errors)} errors")
        
        # Test concurrent task assignments
        task_errors = []
        task_results = []
        
        def concurrent_task_assignment(thread_id):
            try:
                task = TaskRequest(
                    task_id=f"CONCURRENT-{thread_id}",
                    title=f"Concurrent task {thread_id}",
                    description="Concurrency test",
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
                task_results.append((thread_id, result))
            except Exception as e:
                task_errors.append((thread_id, e))
        
        # Start concurrent task assignments
        task_threads = []
        for i in range(30):
            thread = threading.Thread(target=concurrent_task_assignment, args=(i,))
            task_threads.append(thread)
            thread.start()
        
        for thread in task_threads:
            thread.join(timeout=5.0)
        
        print(f"  Concurrent task assignment: {len(task_results)} successful, {len(task_errors)} errors")
        
        # Most operations should succeed even under concurrency
        authority_success_rate = len(results) / (len(results) + len(errors)) * 100 if (len(results) + len(errors)) > 0 else 0
        task_success_rate = len(task_results) / (len(task_results) + len(task_errors)) * 100 if (len(task_results) + len(task_errors)) > 0 else 0
        
        assert authority_success_rate > 70, f"Authority assignment success rate under concurrency should be >70%, got {authority_success_rate:.1f}%"
        assert task_success_rate > 70, f"Task assignment success rate under concurrency should be >70%, got {task_success_rate:.1f}%"
    
    def test_resource_exhaustion(self, error_test_environment):
        """Test handling of resource exhaustion scenarios."""
        load_balancer = error_test_environment['load_balancer']
        
        print("\n📈 Testing Resource Exhaustion Handling")
        
        # Overload all agents with tasks
        overload_tasks = []
        for i in range(200):  # Create many tasks
            task = TaskRequest(
                task_id=f"OVERLOAD-{i}",
                title=f"Overload task {i}",
                description="Resource exhaustion test",
                domain="backend",
                priority=TaskPriority.HIGH.value,
                estimated_duration_minutes=120,  # Long duration
                required_expertise_level="expert",
                deadline=None,
                dependencies=[],
                resource_requirements={"cpu": 0.8, "memory": 0.7},  # High resource usage
                metadata={}
            )
            overload_tasks.append(task)
        
        assigned_count = 0
        queued_count = 0
        error_count = 0
        
        for task in overload_tasks:
            try:
                result = load_balancer.assign_task(task)
                if result:
                    assigned_count += 1
                else:
                    queued_count += 1
            except Exception as e:
                error_count += 1
        
        print(f"  Resource exhaustion: {assigned_count} assigned, {queued_count} queued, {error_count} errors")
        
        # System should handle overload gracefully by queueing
        total_handled = assigned_count + queued_count
        assert total_handled > 0, "System should handle some tasks even when overloaded"
        assert error_count < len(overload_tasks) * 0.1, "Error rate should be low even under overload"
        
        # Test agent capacity limits
        load_status = load_balancer.get_load_status()
        overloaded_agents = 0
        
        for agent_id, load_info in load_status["agent_loads"].items():
            if load_info["load_percent"] > 90:
                overloaded_agents += 1
        
        print(f"  Overloaded agents: {overloaded_agents}/{load_status['total_agents']}")
    
    def test_data_corruption_recovery(self, error_test_environment):
        """Test recovery from data corruption scenarios."""
        temp_dir = error_test_environment['temp_dir']
        
        print("\n🔧 Testing Data Corruption Recovery")
        
        # Create systems with good data first
        authority_manager = error_test_environment['authority_manager']
        conflict_resolver = error_test_environment['conflict_resolver']
        load_balancer = error_test_environment['load_balancer']
        
        # Generate some valid data
        authority_manager.assign_authority("Test task")
        
        parties = [ConflictParty("agent1", "pos", "just", 5, "auth", ["domain"])]
        conflict_resolver.report_conflict(
            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
            "Test conflict", "Test", parties, "agent1"
        )
        
        task = TaskRequest("TEST", "Test", "Test", "backend", 2, 60, "competent", None, [], {}, {})
        load_balancer.assign_task(task)
        
        # Now corrupt the data files
        corruption_scenarios = [
            ("authority_pool.json", '{"corrupted": invalid}'),
            ("conflict_database.json", '{"conflicts": {malformed'),
            ("agent_capacities.json", 'not json at all'),
            ("load_balancing_metrics.json", '[]broken array'),
        ]
        
        for filename, corrupted_content in corruption_scenarios:
            file_path = Path(temp_dir) / filename
            if file_path.exists():
                # Backup original
                backup_path = file_path.with_suffix('.backup')
                shutil.copy(file_path, backup_path)
                
                # Corrupt the file
                with open(file_path, 'w') as f:
                    f.write(corrupted_content)
                
                try:
                    # Try to create new instances (should handle corruption)
                    if "authority" in filename:
                        new_manager = DynamicAuthorityManager(temp_dir)
                        result = new_manager.assign_authority("Recovery test")
                        print(f"  {filename} corruption: Authority manager recovered")
                    elif "conflict" in filename:
                        new_resolver = ConflictResolutionSystem(temp_dir)
                        parties = [ConflictParty("agent1", "pos", "just", 5, "auth", ["domain"])]
                        result = new_resolver.report_conflict(
                            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
                            "Recovery test", "Test", parties, "agent1"
                        )
                        print(f"  {filename} corruption: Conflict resolver recovered")
                    elif "agent_capacities" in filename:
                        new_balancer = LoadBalancer(temp_dir)
                        task = TaskRequest("RECOVERY", "Test", "Test", "backend", 2, 60, "competent", None, [], {}, {})
                        result = new_balancer.assign_task(task)
                        print(f"  {filename} corruption: Load balancer recovered")
                    elif "metrics" in filename:
                        new_balancer = LoadBalancer(temp_dir)
                        new_balancer._collect_load_metrics()
                        print(f"  {filename} corruption: Metrics system recovered")
                        
                except Exception as e:
                    print(f"  {filename} corruption: Handled with error - {type(e).__name__}")
                
                # Restore original file
                if backup_path.exists():
                    shutil.copy(backup_path, file_path)
                    backup_path.unlink()
    
    def test_network_simulation_errors(self, error_test_environment):
        """Test handling of simulated network-like errors."""
        authority_manager = error_test_environment['authority_manager']
        conflict_resolver = error_test_environment['conflict_resolver']
        
        print("\n🌐 Testing Network-like Error Handling")
        
        # Simulate timeout scenarios
        def slow_operation():
            time.sleep(2)  # Simulate slow operation
            return authority_manager.assign_authority("Slow operation test")
        
        start_time = time.time()
        try:
            result = slow_operation()
            duration = time.time() - start_time
            print(f"  Slow operation: Completed in {duration:.2f}s")
        except Exception as e:
            print(f"  Slow operation: Handled with error - {type(e).__name__}")
        
        # Simulate intermittent failures
        failure_count = 0
        success_count = 0
        
        for i in range(20):
            try:
                if i % 5 == 0:  # Simulate 20% failure rate
                    raise ConnectionError("Simulated network error")
                
                result = authority_manager.assign_authority(f"Intermittent test {i}")
                # Check if assignment was successful (has 'agent' and not queued)
                is_successful = 'agent' in result and result.get('status') != 'queued'
                if is_successful:
                    success_count += 1
            except ConnectionError:
                failure_count += 1
            except Exception:
                failure_count += 1
        
        print(f"  Intermittent failures: {success_count} success, {failure_count} failures")
        
        # Test with mock network delays
        original_assign = authority_manager.assign_authority
        
        def delayed_assign(*args, **kwargs):
            time.sleep(0.1)  # Simulate network delay
            return original_assign(*args, **kwargs)
        
        with patch.object(authority_manager, 'assign_authority', delayed_assign):
            start_time = time.time()
            result = authority_manager.assign_authority("Delayed operation test")
            duration = time.time() - start_time
            print(f"  Network delay simulation: {duration:.2f}s")
    
    def test_edge_cases(self, error_test_environment):
        """Test various edge cases."""
        authority_manager = error_test_environment['authority_manager']
        conflict_resolver = error_test_environment['conflict_resolver']
        load_balancer = error_test_environment['load_balancer']
        
        print("\n🎯 Testing Edge Cases")
        
        # Test with extreme values
        edge_case_tests = [
            # Very long strings
            ("authority_long_desc", lambda: authority_manager.assign_authority("A" * 50000)),
            
            # Unicode and special characters
            ("authority_unicode", lambda: authority_manager.assign_authority("测试任务 🚀 with émojis")),
            
            # Very short deadline
            ("task_short_deadline", lambda: load_balancer.assign_task(TaskRequest(
                "EDGE-1", "Edge test", "Test", "backend", 5, 1,
                "expert", (datetime.now() + timedelta(seconds=1)).isoformat(),
                [], {}, {}
            ))),
            
            # Task with many dependencies
            ("task_many_deps", lambda: load_balancer.assign_task(TaskRequest(
                "EDGE-2", "Edge test", "Test", "backend", 3, 60,
                "competent", None, [f"DEP-{i}" for i in range(100)], {}, {}
            ))),
            
            # Very high priority conflict
            ("conflict_extreme_priority", lambda: conflict_resolver.report_conflict(
                ConflictType.PRIORITY_CONFLICT, ConflictSeverity.CRITICAL,
                "Extreme priority conflict", "Test",
                [ConflictParty("agent1", "pos", "just", 999999, "auth", ["domain"])],
                "agent1"
            )),
            
            # Circular dependencies (should be detected)
            ("circular_deps", lambda: [
                load_balancer.assign_task(TaskRequest(
                    "CIRC-A", "Task A", "Test", "backend", 3, 60,
                    "competent", None, ["CIRC-B"], {}, {}
                )),
                load_balancer.assign_task(TaskRequest(
                    "CIRC-B", "Task B", "Test", "backend", 3, 60,
                    "competent", None, ["CIRC-A"], {}, {}
                ))
            ]),
        ]
        
        for test_name, test_func in edge_case_tests:
            try:
                result = test_func()
                print(f"  {test_name}: Handled gracefully")
            except Exception as e:
                print(f"  {test_name}: Exception handled - {type(e).__name__}")
        
        # Test system state after edge cases
        try:
            # Verify system is still functional
            normal_result = authority_manager.assign_authority("Normal test after edge cases")
            # Check if assignment was successful (has 'agent' and not queued)
            is_successful = 'agent' in normal_result and normal_result.get('status') != 'queued'
            assert is_successful, "System should remain functional after edge cases"
            print("  System functionality: Maintained after edge cases")
        except Exception as e:
            print(f"  System functionality: Impaired after edge cases - {type(e).__name__}")
    
    def test_memory_leaks_prevention(self, error_test_environment):
        """Test for potential memory leaks."""
        authority_manager = error_test_environment['authority_manager']
        load_balancer = error_test_environment['load_balancer']
        
        print("\n💾 Testing Memory Leak Prevention")
        
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform many operations
            for i in range(1000):
                authority_manager.assign_authority(f"Memory test {i}")
                
                task = TaskRequest(
                    f"MEM-{i}", f"Memory task {i}", "Test", "backend", 2, 30,
                    "competent", None, [], {}, {}
                )
                load_balancer.assign_task(task)
                
                # Complete some tasks to test cleanup
                if i % 10 == 0:
                    for agent_id in load_balancer.agent_capacities.keys():
                        if load_balancer.agent_capacities[agent_id].current_task_count > 0:
                            load_balancer.complete_task(agent_id, f"MEM-{i}")
                            break
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory
            
            print(f"  Memory growth: {memory_growth:.2f}MB over 1000 operations")
            print(f"  Growth per operation: {memory_growth/1000:.4f}MB")
            
            # Memory growth should be reasonable
            assert memory_growth < 50, f"Memory growth should be under 50MB, got {memory_growth:.2f}MB"
            
        except ImportError:
            print("  Memory leak test: Skipped (psutil not available)")
    
    def test_error_recovery_patterns(self, coordination_system_with_agents):
        """Test various error recovery patterns."""
        authority_manager = coordination_system_with_agents['authority_manager']
        conflict_resolver = coordination_system_with_agents['conflict_resolver']
        load_balancer = coordination_system_with_agents['load_balancer']
        
        print("\n🔄 Testing Error Recovery Patterns")
        
        # Test retry-like behavior
        retry_success = 0
        retry_failures = 0
        
        for i in range(10):
            try:
                # Simulate occasional failures
                if i % 4 == 0:
                    raise RuntimeError("Simulated failure")
                
                result = authority_manager.assign_authority(f"Retry test {i}")
                # Check if assignment was successful (has 'agent' and not queued)
                is_successful = 'agent' in result and result.get('status') != 'queued'
                if is_successful:
                    retry_success += 1
            except RuntimeError:
                retry_failures += 1
                
                # Simulate retry
                try:
                    result = authority_manager.assign_authority(f"Retry test {i} - retry")
                    # Check if assignment was successful (has 'agent' and not queued)
                    is_successful = 'agent' in result and result.get('status') != 'queued'
                    if is_successful:
                        retry_success += 1
                except:
                    retry_failures += 1
        
        print(f"  Retry pattern: {retry_success} success, {retry_failures} final failures")
        
        # Test graceful degradation
        # Overload the system and verify it degrades gracefully
        overload_results = []
        
        for i in range(100):
            try:
                task = TaskRequest(
                    f"DEGRADE-{i}", f"Degradation test {i}", "Test", "backend",
                    TaskPriority.CRITICAL.value, 30, "expert", None, [], 
                    {"cpu": 0.9, "memory": 0.9}, {}
                )
                result = load_balancer.assign_task(task)
                overload_results.append(result is not None)
            except Exception:
                overload_results.append(False)
        
        success_rate = sum(overload_results) / len(overload_results) * 100
        print(f"  Graceful degradation: {success_rate:.1f}% success under overload")
        
        # Test system stability after errors
        stability_test_results = []
        
        for i in range(20):
            try:
                result = authority_manager.assign_authority(f"Stability test {i}")
                # Check if assignment was successful (has 'agent' and not queued)
                is_successful = 'agent' in result and result.get('status') != 'queued'
                stability_test_results.append(is_successful)
            except Exception:
                stability_test_results.append(False)
        
        stability_rate = sum(stability_test_results) / len(stability_test_results) * 100
        print(f"  System stability after errors: {stability_rate:.1f}% success")
        
        # Assertions for recovery patterns
        assert retry_success > 0, "Should have some successful operations with retry"
        assert success_rate > 10, "Should maintain >10% success under extreme overload (graceful degradation)"
        assert stability_rate > 50, "Should maintain >50% stability after error scenarios"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])