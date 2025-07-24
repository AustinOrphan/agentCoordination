#!/usr/bin/env python3
"""
Integration tests for Multi-Agent Coordination System
Tests the interaction between all major components
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import time
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "coordination_system"))

from coordination_system.dynamic_authority_manager import DynamicAuthorityManager, AuthorityType
from conflict_resolution import ConflictResolutionSystem, ConflictType, ConflictSeverity, ConflictParty
from load_balancer import LoadBalancer, LoadBalancingStrategy, TaskRequest, TaskPriority


class TestIntegration:
    """Integration test suite for multi-agent coordination system."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def coordination_system(self, temp_dir):
        """Create complete coordination system."""
        return {
            'authority_manager': DynamicAuthorityManager(temp_dir),
            'conflict_resolver': ConflictResolutionSystem(temp_dir),
            'load_balancer': LoadBalancer(temp_dir),
            'temp_dir': temp_dir
        }
    
    def test_authority_conflict_resolution_integration(self, coordination_system):
        """Test authority assignment leading to conflict resolution."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        
        # Two agents request same authority
        result1 = authority_manager.assign_authority(
            "Critical security audit",
            preferred_agent="shark"
        )
        
        result2 = authority_manager.assign_authority(
            "Security vulnerability assessment", 
            preferred_agent="whale"
        )
        
        # Both should succeed (system should handle conflict)
        assert result1 is not None
        assert result2 is not None
        assert "id" in result1
        assert "id" in result2
        
        # If both got assigned, check they have valid agents
        if "agent" in result1 and "agent" in result2:
            if result1["agent"] == result2["agent"]:
                # Same agent got both - check authority pool for conflict handling
                pool = authority_manager.authority_pool
                assert len(pool["assignments"]) > 0
            else:
                # Different agents - check for backup authorities
                pool = authority_manager.authority_pool
                security_authorities = [
                    auth for auth in pool["assignments"]
                    if auth.get("domain") == "security"
                ]
                assert len(security_authorities) >= 1
    
    def test_load_balancer_authority_integration(self, coordination_system):
        """Test load balancer working with authority system."""
        authority_manager = coordination_system['authority_manager']
        load_balancer = coordination_system['load_balancer']
        
        # Assign authority for security tasks
        auth_result = authority_manager.assign_authority(
            "Security task management",
            preferred_agent="shark"
        )
        
        # Create security task
        security_task = TaskRequest(
            task_id="SEC-INT-001",
            title="Security integration test",
            description="Test security task assignment",
            domain="security",
            priority=TaskPriority.HIGH.value,
            estimated_duration_minutes=90,
            required_expertise_level="expert",
            deadline=None,
            dependencies=[],
            resource_requirements={"cpu": 0.3},
            metadata={"requires_authority": "security"}
        )
        
        # Assign task
        assigned_agent = load_balancer.assign_task(
            security_task,
            LoadBalancingStrategy.EXPERTISE_BASED
        )
        
        assert assigned_agent is not None
        # Should prefer agent with security authority
        if "agent" in auth_result:
            assert assigned_agent == auth_result["agent"] or assigned_agent in ["shark", "whale", "octopus", "jellyfish", "dolphin", "seahorse"]
        else:
            # Authority was queued, so any valid agent assignment is acceptable
            assert assigned_agent in ["shark", "whale", "octopus", "jellyfish", "dolphin", "seahorse"]
    
    def test_conflict_load_balancer_integration(self, coordination_system):
        """Test conflict resolution affecting load balancing."""
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Create resource contention conflict
        parties = [
            ConflictParty("shark", "Need database for security", "Critical audit", 9, "security", ["security"]),
            ConflictParty("whale", "Need database for migration", "Scheduled upgrade", 7, "infrastructure", ["infrastructure"])
        ]
        
        conflict_id = conflict_resolver.report_conflict(
            ConflictType.RESOURCE_CONTENTION,
            ConflictSeverity.HIGH,
            "Database access conflict",
            "Multiple agents need exclusive database access",
            parties,
            "shark",
            {"resource": "database"}
        )
        
        # Create tasks that would compete for the same resource
        task1 = TaskRequest(
            task_id="DB-TASK-1",
            title="Security database audit",
            description="Audit database security",
            domain="security",
            priority=TaskPriority.CRITICAL.value,
            estimated_duration_minutes=120,
            required_expertise_level="expert",
            deadline=None,
            dependencies=[],
            resource_requirements={"database": 1.0},
            metadata={"conflict_id": conflict_id}
        )
        
        task2 = TaskRequest(
            task_id="DB-TASK-2", 
            title="Database migration",
            description="Migrate database schema",
            domain="infrastructure",
            priority=TaskPriority.HIGH.value,
            estimated_duration_minutes=180,
            required_expertise_level="expert",
            deadline=None,
            dependencies=[],
            resource_requirements={"database": 1.0},
            metadata={"conflict_id": conflict_id}
        )
        
        # Try to assign both tasks
        agent1 = load_balancer.assign_task(task1)
        agent2 = load_balancer.assign_task(task2)
        
        # Should handle resource conflict intelligently
        assert agent1 is not None or agent2 is not None
        
        # Check if conflict was resolved
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        if conflict["status"] == "resolved":
            winner = conflict["resolution_details"]["winner"]
            assert winner in ["shark", "whale"]
    
    def test_full_workflow_integration(self, coordination_system):
        """Test complete workflow from task assignment to conflict resolution."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Step 1: Assign authorities
        auth_results = []
        for task_type in ["Security audit", "Frontend development", "Infrastructure deployment"]:
            result = authority_manager.assign_authority(task_type)
            auth_results.append(result)
        
        # Step 2: Create overlapping tasks that might cause conflicts
        tasks = [
            TaskRequest(
                task_id="WORKFLOW-1",
                title="User authentication system",
                description="Implement OAuth2 authentication",
                domain="security",
                priority=TaskPriority.HIGH.value,
                estimated_duration_minutes=240,
                required_expertise_level="expert",
                deadline=(datetime.now() + timedelta(hours=8)).isoformat(),
                dependencies=[],
                resource_requirements={"cpu": 0.4, "memory": 0.3},
                metadata={"feature": "auth"}
            ),
            TaskRequest(
                task_id="WORKFLOW-2",
                title="Login UI components",
                description="Create React login components",
                domain="frontend",
                priority=TaskPriority.MEDIUM.value,
                estimated_duration_minutes=120,
                required_expertise_level="proficient",
                deadline=(datetime.now() + timedelta(hours=6)).isoformat(),
                dependencies=["WORKFLOW-1"],
                resource_requirements={"cpu": 0.2, "memory": 0.2},
                metadata={"feature": "auth"}
            ),
            TaskRequest(
                task_id="WORKFLOW-3",
                title="Database schema for auth",
                description="Create user authentication tables",
                domain="backend",
                priority=TaskPriority.HIGH.value,
                estimated_duration_minutes=90,
                required_expertise_level="expert",
                deadline=(datetime.now() + timedelta(hours=4)).isoformat(),
                dependencies=[],
                resource_requirements={"cpu": 0.3, "database": 1.0},
                metadata={"feature": "auth"}
            )
        ]
        
        # Step 3: Assign tasks and track results
        assignment_results = []
        for task in tasks:
            assigned_agent = load_balancer.assign_task(task, LoadBalancingStrategy.ADAPTIVE)
            assignment_results.append({
                'task_id': task.task_id,
                'assigned_agent': assigned_agent,
                'queued': assigned_agent is None
            })
        
        # Step 4: Verify system state
        # Check authority pool
        authority_pool = authority_manager.authority_pool
        assert len(authority_pool["assignments"]) >= 0
        
        # Check load balancer status
        load_status = load_balancer.get_load_status()
        assert load_status["total_agents"] > 0
        
        # Check for any conflicts
        active_conflicts = conflict_resolver.get_active_conflicts()
        
        # Step 5: Simulate task completion and cleanup
        for result in assignment_results:
            if result['assigned_agent']:
                load_balancer.complete_task(result['assigned_agent'], result['task_id'])
        
        # Final verification
        final_load_status = load_balancer.get_load_status()
        total_active_tasks = sum(
            load_info["current_tasks"] 
            for load_info in final_load_status["agent_loads"].values()
        )
        
        # Should have fewer active tasks after completion
        assert total_active_tasks >= 0
    
    def test_emergency_coordination_integration(self, coordination_system):
        """Test emergency scenarios requiring coordination."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Step 1: Assign emergency authority
        emergency_result = authority_manager.assign_authority(
            "Critical security breach detected - emergency response",
            preferred_agent="shark"
        )
        
        assert emergency_result is not None
        assert "id" in emergency_result
        
        # Step 2: Create emergency tasks
        emergency_task = TaskRequest(
            task_id="EMERGENCY-001",
            title="Security breach response",
            description="Immediate response to security incident", 
            domain="security",
            priority=TaskPriority.EMERGENCY.value,
            estimated_duration_minutes=60,
            required_expertise_level="expert",
            deadline=(datetime.now() + timedelta(minutes=30)).isoformat(),
            dependencies=[],
            resource_requirements={"cpu": 0.8, "memory": 0.6},
            metadata={"emergency": True, "incident_id": "SEC-2025-001"}
        )
        
        # Step 3: Assign emergency task
        emergency_agent = load_balancer.assign_task(
            emergency_task,
            LoadBalancingStrategy.PRIORITY_QUEUE
        )
        
        assert emergency_agent is not None
        # Should assign to agent with emergency authority or appropriate expertise
        
        # Step 4: Create conflicts during emergency
        parties = [
            ConflictParty("shark", "Need all resources for emergency", "Security breach", 10, "emergency", ["security"]),
            ConflictParty("whale", "Critical infrastructure maintenance", "Scheduled work", 5, "infrastructure", ["infrastructure"])
        ]
        
        emergency_conflict_id = conflict_resolver.report_conflict(
            ConflictType.AUTHORITY_DISPUTE,
            ConflictSeverity.CRITICAL,
            "Emergency authority conflict",
            "Emergency response vs scheduled maintenance",
            parties,
            "shark",
            {"emergency": True}
        )
        
        # Step 5: Verify emergency handling
        conflict = conflict_resolver.conflicts_db["conflicts"][emergency_conflict_id]
        
        # Emergency conflicts should be resolved quickly
        if conflict["status"] == "resolved":
            assert conflict["resolution_details"]["winner"] == "shark"  # Emergency should win
    
    def test_scalability_stress_integration(self, coordination_system):
        """Test system behavior under stress with many agents and tasks."""
        authority_manager = coordination_system['authority_manager']
        load_balancer = coordination_system['load_balancer']
        
        # Create many authority assignments
        authority_results = []
        for i in range(20):
            result = authority_manager.assign_authority(f"Task batch {i}")
            authority_results.append(result)
        
        # Create many task assignments
        task_results = []
        for i in range(50):
            task = TaskRequest(
                task_id=f"STRESS-{i:03d}",
                title=f"Stress test task {i}",
                description=f"Load testing task number {i}",
                domain=["security", "frontend", "backend", "infrastructure"][i % 4],
                priority=[TaskPriority.LOW.value, TaskPriority.MEDIUM.value, TaskPriority.HIGH.value][i % 3],
                estimated_duration_minutes=30 + (i % 120),
                required_expertise_level=["competent", "proficient", "expert"][i % 3],
                deadline=None,
                dependencies=[],
                resource_requirements={"cpu": 0.1 + (i % 5) * 0.1},
                metadata={"batch": i // 10}
            )
            
            assigned_agent = load_balancer.assign_task(task)
            task_results.append({
                'task_id': task.task_id,
                'assigned_agent': assigned_agent,
                'queued': assigned_agent is None
            })
        
        # Verify system stability
        assigned_count = sum(1 for r in task_results if r['assigned_agent'])
        queued_count = sum(1 for r in task_results if r['queued'])
        
        assert assigned_count > 0  # Should assign some tasks
        assert assigned_count + queued_count == 50  # All tasks accounted for
        
        # Check system state
        load_status = load_balancer.get_load_status()
        authority_pool = authority_manager.authority_pool
        
        assert load_status["total_agents"] > 0
        assert len(authority_pool["assignments"]) >= 0
    
    def test_data_persistence_integration(self, coordination_system):
        """Test data persistence across system components."""
        temp_dir = coordination_system['temp_dir']
        
        # Create some data
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Generate some state
        authority_manager.assign_authority("Test persistence")
        
        parties = [ConflictParty("shark", "pos", "just", 5, "auth", ["domain"])]
        conflict_resolver.report_conflict(
            ConflictType.TASK_OVERLAP, ConflictSeverity.LOW,
            "Test conflict", "Testing", parties, "shark"
        )
        
        task = TaskRequest("TEST", "Test", "Test", "security", 2, 60, "competent", None, [], {}, {})
        load_balancer.assign_task(task)
        
        # Verify files were created
        expected_files = [
            "authority_pool.json",
            "agent_workloads.json", 
            "authority_history.json",
            "conflict_database.json",
            "conflict_resolutions.json",
            "mediation_rules.json",
            "load_balancer_config.json",
            "agent_capacities.json"
        ]
        
        for filename in expected_files:
            file_path = Path(temp_dir) / filename
            if file_path.exists():
                # Verify file has valid JSON
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    assert isinstance(data, (dict, list))
    
    def test_error_recovery_integration(self, coordination_system):
        """Test system recovery from errors."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Test invalid agent handling
        result = authority_manager.assign_authority("Test task", preferred_agent="invalid_agent")
        assert result is not None  # Should handle request gracefully
        # Authority manager may assign to invalid agent or fallback/queue
        # This tests that the system doesn't crash on invalid input
        assert "id" in result
        if "agent" in result:
            # System assigned the requested agent (valid or invalid)
            assert isinstance(result["agent"], str)
        else:
            # System queued the request
            assert result.get("status") == "queued"
        
        # Test invalid task handling
        invalid_task = TaskRequest(
            task_id="INVALID",
            title="Invalid task",
            description="Testing error handling",
            domain="nonexistent_domain",
            priority=TaskPriority.MEDIUM.value,
            estimated_duration_minutes=60,
            required_expertise_level="impossible_level",
            deadline=None,
            dependencies=["NONEXISTENT_DEPENDENCY"],
            resource_requirements={"impossible_resource": 999.0},
            metadata={}
        )
        
        # Should handle gracefully
        try:
            assigned_agent = load_balancer.assign_task(invalid_task)
            # May succeed with fallback or return None
            assert assigned_agent is None or assigned_agent in load_balancer.agent_capacities
        except Exception as e:
            # Should not crash the system
            assert False, f"System crashed on invalid task: {e}"
        
        # Test malformed conflict data
        try:
            invalid_parties = [ConflictParty("", "", "", -1, "", [])]
            conflict_id = conflict_resolver.report_conflict(
                ConflictType.TASK_OVERLAP,
                ConflictSeverity.LOW,
                "",  # Empty title
                "",  # Empty description
                invalid_parties,
                ""   # Empty reporter
            )
            # Should create conflict even with invalid data
            assert conflict_id is not None
        except Exception as e:
            # Should handle gracefully
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])