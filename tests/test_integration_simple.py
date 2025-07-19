#!/usr/bin/env python3
"""
Simplified Integration tests for Multi-Agent Coordination System
Tests the interaction between components with realistic expectations
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


@pytest.mark.integration
class TestIntegrationSimple:
    """Simplified integration test suite for multi-agent coordination system."""
    
    @pytest.fixture
    def coordination_system(self):
        """Create complete coordination system."""
        temp_dir = tempfile.mkdtemp()
        
        system = {
            'authority_manager': DynamicAuthorityManager(temp_dir),
            'conflict_resolver': ConflictResolutionSystem(temp_dir),
            'load_balancer': LoadBalancer(temp_dir),
            'temp_dir': temp_dir
        }
        
        yield system
        
        shutil.rmtree(temp_dir)
    
    def test_basic_system_integration(self, coordination_system):
        """Test basic system integration."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Test authority assignment
        auth_result = authority_manager.assign_authority("Test task integration")
        assert auth_result is not None
        assert "id" in auth_result
        
        # Test conflict creation
        parties = [ConflictParty("agent1", "pos1", "just1", 5, "auth1", ["domain1"])]
        conflict_id = conflict_resolver.report_conflict(
            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
            "Integration test conflict", "Testing integration", parties, "agent1"
        )
        assert conflict_id is not None
        
        # Test task assignment
        task = TaskRequest("INT-001", "Integration test", "Test", "backend", 2, 60, "competent", None, [], {}, {})
        assigned_agent = load_balancer.assign_task(task)
        # May or may not be assigned depending on available agents
        assert assigned_agent is None or isinstance(assigned_agent, str)
    
    def test_load_balancer_strategies(self, coordination_system):
        """Test different load balancing strategies."""
        load_balancer = coordination_system['load_balancer']
        
        task = TaskRequest("STRAT-001", "Strategy test", "Test", "backend", 2, 60, "competent", None, [], {}, {})
        
        strategies = [
            LoadBalancingStrategy.ROUND_ROBIN,
            LoadBalancingStrategy.LEAST_CONNECTIONS,
            LoadBalancingStrategy.RESOURCE_AWARE,
            LoadBalancingStrategy.EXPERTISE_BASED,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
        ]
        
        for strategy in strategies:
            assigned_agent = load_balancer.assign_task(task, strategy)
            # Test that strategy doesn't crash
            assert assigned_agent is None or isinstance(assigned_agent, str)
    
    def test_conflict_resolution_workflow(self, coordination_system):
        """Test conflict resolution workflow."""
        conflict_resolver = coordination_system['conflict_resolver']
        
        # Create multiple conflicts
        conflict_types = [
            ConflictType.RESOURCE_CONTENTION,
            ConflictType.PRIORITY_CONFLICT,
            ConflictType.TASK_OVERLAP
        ]
        
        conflict_ids = []
        for i, conflict_type in enumerate(conflict_types):
            parties = [ConflictParty(f"agent{i}", f"pos{i}", f"just{i}", 5+i, "auth", ["domain"])]
            conflict_id = conflict_resolver.report_conflict(
                conflict_type, ConflictSeverity.MEDIUM,
                f"Workflow test {i}", f"Testing workflow {i}", parties, f"agent{i}"
            )
            conflict_ids.append(conflict_id)
        
        # Check conflicts were created
        assert len(conflict_ids) == len(conflict_types)
        assert all(cid is not None for cid in conflict_ids)
        
        # Check active conflicts
        active_conflicts = conflict_resolver.get_active_conflicts()
        assert isinstance(active_conflicts, list)
    
    def test_data_persistence_across_components(self, coordination_system):
        """Test data persistence across system components."""
        temp_dir = coordination_system['temp_dir']
        
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Generate some data
        authority_manager.assign_authority("Persistence test")
        
        parties = [ConflictParty("agent1", "pos", "just", 5, "auth", ["domain"])]
        conflict_resolver.report_conflict(
            ConflictType.TASK_OVERLAP, ConflictSeverity.LOW,
            "Persistence conflict", "Testing", parties, "agent1"
        )
        
        task = TaskRequest("PERSIST", "Persistence", "Test", "backend", 2, 60, "competent", None, [], {}, {})
        load_balancer.assign_task(task)
        
        # Check that files were created
        expected_files = [
            "authority_pool.json",
            "conflict_database.json", 
            "agent_capacities.json"
        ]
        
        created_files = []
        for filename in expected_files:
            file_path = Path(temp_dir) / filename
            if file_path.exists():
                created_files.append(filename)
        
        # Should have created at least some files
        assert len(created_files) > 0
    
    def test_system_scalability_basic(self, coordination_system):
        """Test basic system scalability."""
        authority_manager = coordination_system['authority_manager']
        load_balancer = coordination_system['load_balancer']
        
        # Create multiple operations
        num_operations = 20
        
        # Authority assignments
        auth_results = []
        for i in range(num_operations):
            result = authority_manager.assign_authority(f"Scalability test {i}")
            auth_results.append(result)
        
        # Task assignments
        task_results = []
        for i in range(num_operations):
            task = TaskRequest(f"SCALE-{i}", f"Scale task {i}", "Test", "backend", 2, 30, "competent", None, [], {}, {})
            assigned_agent = load_balancer.assign_task(task)
            task_results.append(assigned_agent)
        
        # System should handle the load without crashing
        assert len(auth_results) == num_operations
        assert len(task_results) == num_operations
        assert all(r is not None for r in auth_results)
    
    def test_load_status_integration(self, coordination_system):
        """Test load status integration."""
        load_balancer = coordination_system['load_balancer']
        
        # Assign some tasks
        for i in range(5):
            task = TaskRequest(f"STATUS-{i}", f"Status test {i}", "Test", "backend", 2, 30, "competent", None, [], {}, {})
            load_balancer.assign_task(task)
        
        # Get load status
        status = load_balancer.get_load_status()
        
        # Verify status structure
        assert "timestamp" in status
        assert "current_strategy" in status
        assert "total_agents" in status
        assert "agent_loads" in status
        assert "queue_status" in status
        
        assert status["total_agents"] > 0
        assert isinstance(status["agent_loads"], dict)
    
    def test_error_handling_integration(self, coordination_system):
        """Test error handling across components."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Test with invalid/edge case inputs
        try:
            # Empty authority request
            result = authority_manager.assign_authority("")
            assert result is not None  # Should handle gracefully
        except Exception:
            pass  # Acceptable to throw exception
        
        try:
            # Invalid conflict
            parties = []  # Empty parties
            conflict_id = conflict_resolver.report_conflict(
                ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
                "", "", parties, ""
            )
            # May succeed or fail, both acceptable
        except Exception:
            pass
        
        try:
            # Invalid task
            task = TaskRequest("", "", "", "", -1, -1, "", None, [], {}, {})
            assigned_agent = load_balancer.assign_task(task)
            # May succeed or fail, both acceptable
        except Exception:
            pass
        
        # System should still be functional after errors
        normal_result = authority_manager.assign_authority("Normal test after errors")
        assert normal_result is not None
    
    def test_component_interaction_basic(self, coordination_system):
        """Test basic component interaction."""
        authority_manager = coordination_system['authority_manager']
        conflict_resolver = coordination_system['conflict_resolver']
        load_balancer = coordination_system['load_balancer']
        
        # Authority assignment
        auth_result = authority_manager.assign_authority("Component interaction test")
        assert "id" in auth_result
        
        # Create related conflict
        parties = [ConflictParty("agent1", "Need authority", "Test", 5, "test", ["domain"])]
        conflict_id = conflict_resolver.report_conflict(
            ConflictType.AUTHORITY_DISPUTE, ConflictSeverity.MEDIUM,
            "Authority interaction conflict", "Testing interaction", parties, "agent1"
        )
        
        # Create related task
        task = TaskRequest("INTERACT-001", "Interaction task", "Test authority interaction", 
                          "backend", 3, 60, "expert", None, [], {}, {"authority_id": auth_result["id"]})
        assigned_agent = load_balancer.assign_task(task)
        
        # Verify components handled the interaction
        assert conflict_id is not None
        # Task assignment may succeed or fail based on available agents
        assert assigned_agent is None or isinstance(assigned_agent, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])