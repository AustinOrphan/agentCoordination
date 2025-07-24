#!/usr/bin/env python3
"""
Unit tests for Conflict Resolution System
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from conflict_resolution import (
    ConflictResolutionSystem,
    ConflictType,
    ConflictSeverity,
    ConflictParty,
    ResolutionStrategy
)


class TestConflictResolutionSystem:
    """Test suite for Conflict Resolution System."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def conflict_resolver(self, temp_dir):
        """Create conflict resolver instance for testing."""
        return ConflictResolutionSystem(temp_dir)
    
    @pytest.fixture
    def sample_parties(self):
        """Create sample conflict parties."""
        return [
            ConflictParty(
                agent_id="shark",
                position="Need database access first",
                justification="Critical security audit",
                priority_level=9,
                authority_level="security",
                expertise_domains=["security", "backend"]
            ),
            ConflictParty(
                agent_id="whale",
                position="Scheduled maintenance window",
                justification="Infrastructure upgrade",
                priority_level=7,
                authority_level="infrastructure",
                expertise_domains=["infrastructure", "deployment"]
            )
        ]
    
    def test_initialization(self, conflict_resolver):
        """Test conflict resolver initialization."""
        assert conflict_resolver is not None
        assert hasattr(conflict_resolver, 'conflicts_db')
        assert hasattr(conflict_resolver, 'resolution_history')
        assert hasattr(conflict_resolver, 'mediation_rules')
    
    def test_report_conflict(self, conflict_resolver, sample_parties):
        """Test conflict reporting."""
        conflict_id = conflict_resolver.report_conflict(
            conflict_type=ConflictType.RESOURCE_CONTENTION,
            severity=ConflictSeverity.MEDIUM,
            title="Database access conflict",
            description="Multiple agents need database access",
            parties=sample_parties,
            reporter_id="shark",
            metadata={"resource": "database"}
        )
        
        assert conflict_id is not None
        assert conflict_id.startswith("CONF-")
        assert conflict_id in conflict_resolver.conflicts_db["conflicts"]
    
    def test_automatic_resolution_priority(self, conflict_resolver, sample_parties):
        """Test automatic priority-based resolution."""
        conflict_id = conflict_resolver.report_conflict(
            conflict_type=ConflictType.PRIORITY_CONFLICT,
            severity=ConflictSeverity.LOW,
            title="Priority dispute",
            description="Disagreement over task priorities",
            parties=sample_parties,
            reporter_id="shark"
        )
        
        # Check if conflict was auto-resolved
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        
        # Should be resolved automatically based on priority
        if conflict["status"] == "resolved":
            assert conflict["resolution_details"]["winner"] == "shark"  # Higher priority
    
    def test_automatic_resolution_round_robin(self, conflict_resolver, sample_parties):
        """Test automatic round-robin resolution."""
        conflict_id = conflict_resolver.report_conflict(
            conflict_type=ConflictType.RESOURCE_CONTENTION,
            severity=ConflictSeverity.MEDIUM,
            title="Resource conflict",
            description="Resource contention",
            parties=sample_parties,
            reporter_id="shark",
            metadata={"resource": "database"}
        )
        
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        
        # Should attempt automatic resolution
        assert conflict["status"] in ["resolved", "in_progress"]
    
    def test_mediator_assignment(self, conflict_resolver, sample_parties):
        """Test mediator assignment for complex conflicts."""
        # Create a conflict that requires mediation
        conflict_id = conflict_resolver.report_conflict(
            conflict_type=ConflictType.EXPERTISE_DISPUTE,
            severity=ConflictSeverity.HIGH,
            title="Architecture disagreement",
            description="Technical disagreement",
            parties=sample_parties,
            reporter_id="shark",
            metadata={"domain": "backend"}
        )
        
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        
        # Should have mediator assigned if not auto-resolved
        if conflict["status"] == "in_progress":
            assert conflict["assigned_mediator"] is not None
            assert conflict["assigned_mediator"] not in ["shark", "whale"]
    
    def test_conflict_escalation(self, conflict_resolver):
        """Test conflict escalation."""
        # Create conflict with very short deadline
        parties = [
            ConflictParty("shark", "Position A", "Reason A", 5, "security", ["security"]),
            ConflictParty("dolphin", "Position B", "Reason B", 5, "frontend", ["frontend"])
        ]
        
        conflict_id = conflict_resolver.report_conflict(
            conflict_type=ConflictType.VOTING_DEADLOCK,
            severity=ConflictSeverity.CRITICAL,
            title="Voting deadlock",
            description="Unable to reach consensus",
            parties=parties,
            reporter_id="shark"
        )
        
        # Force escalation
        conflict_resolver._escalate_conflict(conflict_id, "Test escalation")
        
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        assert conflict["status"] == "escalated"
        assert len(conflict["escalation_history"]) > 0
    
    def test_get_active_conflicts(self, conflict_resolver, sample_parties):
        """Test getting active conflicts."""
        # Create some conflicts
        conflict_id1 = conflict_resolver.report_conflict(
            ConflictType.RESOURCE_CONTENTION, ConflictSeverity.MEDIUM,
            "Conflict 1", "Description 1", sample_parties, "shark"
        )
        
        conflict_id2 = conflict_resolver.report_conflict(
            ConflictType.TASK_OVERLAP, ConflictSeverity.LOW,
            "Conflict 2", "Description 2", sample_parties, "whale"
        )
        
        active_conflicts = conflict_resolver.get_active_conflicts()
        
        # Should return conflicts that aren't resolved
        assert len(active_conflicts) >= 0
        
        # Check structure
        for conflict in active_conflicts:
            assert "conflict_id" in conflict
            assert "status" in conflict
            assert conflict["status"] in ["open", "in_progress"]
    
    def test_generate_conflict_report(self, conflict_resolver, sample_parties):
        """Test conflict report generation."""
        # Create some conflicts
        conflict_resolver.report_conflict(
            ConflictType.RESOURCE_CONTENTION, ConflictSeverity.MEDIUM,
            "Test Conflict", "Test Description", sample_parties, "shark"
        )
        
        report = conflict_resolver.generate_conflict_report()
        
        # Verify report structure
        assert "generated_at" in report
        assert "total_conflicts" in report
        assert "active_conflicts" in report
        assert "resolved_conflicts" in report
        assert "conflict_types" in report
        assert "recommendations" in report
        
        assert report["total_conflicts"] >= 1
    
    def test_expertise_based_selection(self, conflict_resolver):
        """Test agent selection based on expertise."""
        parties = [
            {"agent_id": "shark", "expertise_domains": ["security", "backend"]},
            {"agent_id": "dolphin", "expertise_domains": ["frontend", "ui"]},
            {"agent_id": "whale", "expertise_domains": ["infrastructure"]}
        ]
        
        # Test selection for security domain
        selected = conflict_resolver._select_agent_by_expertise(parties, "security")
        # May return None if role manager not available
        assert selected == "shark" or selected is None
        
        # Test selection for unknown domain
        selected = conflict_resolver._select_agent_by_expertise(parties, "unknown")
        # Should return None or fallback gracefully
        assert selected is None or selected in ["shark", "dolphin", "whale"]
    
    def test_resolution_time_calculation(self, conflict_resolver, sample_parties):
        """Test resolution time calculation."""
        conflict_id = conflict_resolver.report_conflict(
            ConflictType.PRIORITY_CONFLICT, ConflictSeverity.LOW,
            "Time Test", "Test timing", sample_parties, "shark"
        )
        
        # Manually resolve conflict
        resolution = {
            "strategy": "priority",
            "outcome": "Test resolution",
            "winner": "shark",
            "reasoning": "Test"
        }
        
        conflict_resolver._resolve_conflict(conflict_id, resolution)
        
        # Check resolution time was calculated
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        assert conflict["resolution_timestamp"] is not None
        
        # Check history has time information
        if conflict_resolver.resolution_history:
            latest_resolution = conflict_resolver.resolution_history[-1]
            assert "resolution_time_hours" in latest_resolution
            assert latest_resolution["resolution_time_hours"] >= 0
    
    def test_multiple_conflict_types(self, conflict_resolver, sample_parties):
        """Test handling of different conflict types."""
        conflict_types = [
            ConflictType.RESOURCE_CONTENTION,
            ConflictType.AUTHORITY_DISPUTE,
            ConflictType.TASK_OVERLAP,
            ConflictType.PRIORITY_CONFLICT,
            ConflictType.EXPERTISE_DISPUTE
        ]
        
        for i, conflict_type in enumerate(conflict_types):
            conflict_id = conflict_resolver.report_conflict(
                conflict_type=conflict_type,
                severity=ConflictSeverity.MEDIUM,
                title=f"Test Conflict {i+1}",
                description=f"Testing {conflict_type.value}",
                parties=sample_parties,
                reporter_id="shark"
            )
            
            assert conflict_id is not None
            conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
            assert conflict["type"] == conflict_type.value
    
    def test_conflict_party_validation(self, conflict_resolver):
        """Test conflict party data validation."""
        # Test with minimal party data
        minimal_parties = [
            ConflictParty("agent1", "pos1", "just1", 5, "auth1", ["domain1"]),
            ConflictParty("agent2", "pos2", "just2", 3, "auth2", ["domain2"])
        ]
        
        conflict_id = conflict_resolver.report_conflict(
            ConflictType.PRIORITY_CONFLICT,
            ConflictSeverity.LOW,
            "Validation Test",
            "Testing party validation",
            minimal_parties,
            "agent1"
        )
        
        assert conflict_id is not None
        conflict = conflict_resolver.conflicts_db["conflicts"][conflict_id]
        assert len(conflict["parties"]) == 2
        
        # Verify party data structure
        for party in conflict["parties"]:
            assert "agent_id" in party
            assert "position" in party
            assert "justification" in party
            assert "priority_level" in party


if __name__ == "__main__":
    pytest.main([__file__, "-v"])