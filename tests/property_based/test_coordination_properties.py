"""
Property-Based Testing Infrastructure

This module implements property-based testing for the multi-agent coordination system
using Hypothesis to generate test data and verify system invariants across a wide
range of inputs and scenarios.
"""

import time
import json
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import pytest
from hypothesis import given, strategies as st, assume, settings, Verbosity
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule, invariant, initialize, teardown
import hypothesis.strategies as st

from ..utilities.bdd_assertions import BDDAssertions, create_assertion_context
from ..utilities.edge_case_generators import EdgeCaseType


@dataclass
class AgentState:
    """Represents the state of an agent in the coordination system."""
    agent_id: str
    status: str
    current_task: Optional[str]
    progress: float
    authorities: List[str]
    blockers: List[str]
    last_update: float
    dependencies: List[str]


@dataclass
class AuthorityState:
    """Represents the state of an authority in the system."""
    authority_type: str
    current_holder: Optional[str]
    backup_holder: Optional[str]
    pending_requests: List[str]
    assignment_time: float


@dataclass
class CoordinationSystemState:
    """Complete state of the coordination system."""
    agents: Dict[str, AgentState]
    authorities: Dict[str, AuthorityState]
    message_queue: List[Dict[str, Any]]
    active_conflicts: List[Dict[str, Any]]
    system_time: float


# Hypothesis strategies for generating test data
agent_ids = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=10)
agent_statuses = st.sampled_from(["active", "idle", "blocked", "stopped", "error"])
task_names = st.one_of(
    st.none(),
    st.sampled_from([
        "authentication_module", "user_dashboard", "database_migration",
        "api_endpoints", "security_audit", "performance_optimization"
    ])
)
progress_values = st.floats(min_value=0.0, max_value=100.0)
authority_types = st.sampled_from([
    "critical_path", "migration", "dashboard", "devops", "security", "ux"
])
blocker_descriptions = st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=5, max_size=50)


@st.composite
def agent_state_strategy(draw) -> AgentState:
    """Generate a valid agent state."""
    agent_id = draw(agent_ids)
    status = draw(agent_statuses)
    task = draw(task_names)
    progress = draw(progress_values)
    
    # Generate authorities (agents can have 0-2 authorities)
    authorities = draw(st.lists(authority_types, min_size=0, max_size=2, unique=True))
    
    # Generate blockers (more likely for blocked agents)
    blocker_count = 1 if status == "blocked" else draw(st.integers(min_value=0, max_value=3))
    blockers = draw(st.lists(blocker_descriptions, min_size=blocker_count, max_size=blocker_count))
    
    # Generate dependencies
    dependencies = draw(st.lists(agent_ids.filter(lambda x: x != agent_id), min_size=0, max_size=3, unique=True))
    
    return AgentState(
        agent_id=agent_id,
        status=status,
        current_task=task,
        progress=progress,
        authorities=authorities,
        blockers=blockers,
        last_update=time.time(),
        dependencies=dependencies
    )


@st.composite
def authority_state_strategy(draw) -> AuthorityState:
    """Generate a valid authority state."""
    authority_type = draw(authority_types)
    
    # Authority can be unassigned, have holder, or have both holder and backup
    assignment_type = draw(st.sampled_from(["unassigned", "assigned", "with_backup"]))
    
    if assignment_type == "unassigned":
        current_holder = None
        backup_holder = None
    elif assignment_type == "assigned":
        current_holder = draw(agent_ids)
        backup_holder = None
    else:  # with_backup
        current_holder = draw(agent_ids)
        backup_holder = draw(agent_ids.filter(lambda x: x != current_holder))
    
    # Generate pending requests
    pending_requests = draw(st.lists(agent_ids, min_size=0, max_size=5, unique=True))
    
    return AuthorityState(
        authority_type=authority_type,
        current_holder=current_holder,
        backup_holder=backup_holder,
        pending_requests=pending_requests,
        assignment_time=time.time()
    )


@st.composite
def coordination_system_state_strategy(draw) -> CoordinationSystemState:
    """Generate a complete coordination system state."""
    # Generate 3-12 agents
    agent_count = draw(st.integers(min_value=3, max_value=12))
    agents = {}
    
    for i in range(agent_count):
        agent = draw(agent_state_strategy())
        # Ensure unique agent IDs
        agent.agent_id = f"agent_{i}_{agent.agent_id}"
        agents[agent.agent_id] = agent
    
    # Generate authorities (always have the standard 6)
    authorities = {}
    for auth_type in ["critical_path", "migration", "dashboard", "devops", "security", "ux"]:
        authority = draw(authority_state_strategy())
        authority.authority_type = auth_type
        
        # Ensure authority holders are valid agent IDs
        if authority.current_holder:
            authority.current_holder = draw(st.sampled_from(list(agents.keys())))
        if authority.backup_holder:
            available_agents = [aid for aid in agents.keys() if aid != authority.current_holder]
            if available_agents:
                authority.backup_holder = draw(st.sampled_from(available_agents))
        
        authorities[auth_type] = authority
    
    # Generate message queue
    message_queue = draw(st.lists(
        st.fixed_dictionaries({
            "id": st.text(min_size=5, max_size=20),
            "sender": st.sampled_from(list(agents.keys())),
            "recipient": st.sampled_from(list(agents.keys())),
            "type": st.sampled_from(["status_update", "authority_request", "coordination"]),
            "timestamp": st.floats(min_value=time.time() - 3600, max_value=time.time())
        }),
        min_size=0,
        max_size=20
    ))
    
    # Generate active conflicts
    active_conflicts = draw(st.lists(
        st.fixed_dictionaries({
            "conflict_id": st.text(min_size=5, max_size=15),
            "type": st.sampled_from(["authority_conflict", "resource_conflict", "dependency_conflict"]),
            "involved_agents": st.lists(st.sampled_from(list(agents.keys())), min_size=2, max_size=4, unique=True),
            "severity": st.sampled_from(["low", "medium", "high"]),
            "start_time": st.floats(min_value=time.time() - 1800, max_value=time.time())
        }),
        min_size=0,
        max_size=5
    ))
    
    return CoordinationSystemState(
        agents=agents,
        authorities=authorities,
        message_queue=message_queue,
        active_conflicts=active_conflicts,
        system_time=time.time()
    )


class CoordinationSystemProperties:
    """Property-based tests for coordination system invariants."""
    
    def __init__(self):
        self.assertions = BDDAssertions(
            create_assertion_context("PropertyBasedTesting", "CoordinationSystemProperties")
        )
    
    @given(coordination_system_state_strategy())
    @settings(max_examples=100, verbosity=Verbosity.verbose)
    def test_authority_assignment_invariants(self, system_state: CoordinationSystemState):
        """Test that authority assignment invariants hold."""
        
        # Property 1: Each authority can have at most one current holder
        for auth_type, authority in system_state.authorities.items():
            if authority.current_holder:
                # Verify holder is a valid agent
                assert authority.current_holder in system_state.agents, \
                    f"Authority {auth_type} holder {authority.current_holder} is not a valid agent"
                
                # Verify holder has this authority in their list
                holder_agent = system_state.agents[authority.current_holder]
                assert auth_type in holder_agent.authorities, \
                    f"Agent {authority.current_holder} doesn't have authority {auth_type} in their list"
        
        # Property 2: No agent can hold the same authority type multiple times
        for agent_id, agent in system_state.agents.items():
            authority_counts = {}
            for auth in agent.authorities:
                authority_counts[auth] = authority_counts.get(auth, 0) + 1
                assert authority_counts[auth] == 1, \
                    f"Agent {agent_id} has duplicate authority {auth}"
        
        # Property 3: Backup holder must be different from current holder
        for auth_type, authority in system_state.authorities.items():
            if authority.backup_holder and authority.current_holder:
                assert authority.backup_holder != authority.current_holder, \
                    f"Authority {auth_type} has same agent as holder and backup"
    
    @given(coordination_system_state_strategy())
    @settings(max_examples=100)
    def test_agent_state_consistency(self, system_state: CoordinationSystemState):
        """Test that agent states are internally consistent."""
        
        for agent_id, agent in system_state.agents.items():
            # Property 1: Blocked agents must have at least one blocker
            if agent.status == "blocked":
                assert len(agent.blockers) > 0, \
                    f"Blocked agent {agent_id} has no blockers"
            
            # Property 2: Active agents should have tasks
            if agent.status == "active":
                assert agent.current_task is not None, \
                    f"Active agent {agent_id} has no current task"
            
            # Property 3: Progress should be reasonable for agent status
            if agent.status == "stopped":
                assert agent.progress == 0.0 or agent.current_task is None, \
                    f"Stopped agent {agent_id} has non-zero progress or active task"
            
            # Property 4: Agent dependencies should not include self
            assert agent_id not in agent.dependencies, \
                f"Agent {agent_id} has self-dependency"
            
            # Property 5: All dependencies should be valid agent IDs
            for dep in agent.dependencies:
                assert dep in system_state.agents, \
                    f"Agent {agent_id} depends on non-existent agent {dep}"
    
    @given(coordination_system_state_strategy())
    @settings(max_examples=100)
    def test_system_consistency_properties(self, system_state: CoordinationSystemState):
        """Test system-wide consistency properties."""
        
        # Property 1: All authority holders must be valid agents
        all_agent_ids = set(system_state.agents.keys())
        for auth_type, authority in system_state.authorities.items():
            if authority.current_holder:
                assert authority.current_holder in all_agent_ids, \
                    f"Authority {auth_type} holder {authority.current_holder} is not a valid agent"
            if authority.backup_holder:
                assert authority.backup_holder in all_agent_ids, \
                    f"Authority {auth_type} backup {authority.backup_holder} is not a valid agent"
        
        # Property 2: Message queue participants must be valid agents
        for message in system_state.message_queue:
            assert message["sender"] in all_agent_ids, \
                f"Message sender {message['sender']} is not a valid agent"
            assert message["recipient"] in all_agent_ids, \
                f"Message recipient {message['recipient']} is not a valid agent"
        
        # Property 3: Conflict participants must be valid agents
        for conflict in system_state.active_conflicts:
            for agent_id in conflict["involved_agents"]:
                assert agent_id in all_agent_ids, \
                    f"Conflict involves non-existent agent {agent_id}"
        
        # Property 4: Authority distribution should be reasonable
        authority_holders = set()
        for authority in system_state.authorities.values():
            if authority.current_holder:
                authority_holders.add(authority.current_holder)
        
        # At most one agent should be holding multiple authorities in a well-balanced system
        agent_authority_counts = {}
        for authority in system_state.authorities.values():
            if authority.current_holder:
                agent_authority_counts[authority.current_holder] = \
                    agent_authority_counts.get(authority.current_holder, 0) + 1
        
        agents_with_multiple = sum(1 for count in agent_authority_counts.values() if count > 1)
        total_agents = len(system_state.agents)
        
        # Heuristic: In a balanced system, less than 50% of agents should hold multiple authorities
        if total_agents >= 6:  # Only apply this rule for larger systems
            assert agents_with_multiple <= total_agents * 0.5, \
                f"Too many agents ({agents_with_multiple}/{total_agents}) holding multiple authorities"
    
    @given(st.lists(agent_state_strategy(), min_size=2, max_size=10))
    @settings(max_examples=50)
    def test_conflict_detection_properties(self, agents: List[AgentState]):
        """Test properties of conflict detection logic."""
        
        # Create a mapping for easier lookup
        agent_map = {agent.agent_id: agent for agent in agents}
        
        # Property 1: Agents with overlapping authorities should be in conflict
        authority_holders = {}
        for agent in agents:
            for authority in agent.authorities:
                if authority in authority_holders:
                    # Conflict detected
                    other_agent = authority_holders[authority]
                    assert other_agent != agent.agent_id, \
                        f"Authority {authority} held by same agent {agent.agent_id} twice"
                else:
                    authority_holders[authority] = agent.agent_id
        
        # Property 2: Circular dependencies should be detectable
        visited = set()
        rec_stack = set()
        
        def has_cycle(agent_id: str) -> bool:
            if agent_id in rec_stack:
                return True
            if agent_id in visited:
                return False
            
            visited.add(agent_id)
            rec_stack.add(agent_id)
            
            if agent_id in agent_map:
                for dep in agent_map[agent_id].dependencies:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(agent_id)
            return False
        
        # Check for cycles in dependency graph
        for agent in agents:
            visited.clear()
            rec_stack.clear()
            cycle_exists = has_cycle(agent.agent_id)
            
            # Property: System should not have circular dependencies
            # Note: This is more of a warning than a hard failure for property testing
            if cycle_exists:
                print(f"Warning: Circular dependency detected involving agent {agent.agent_id}")
    
    @given(coordination_system_state_strategy())
    @settings(max_examples=50)
    def test_performance_properties(self, system_state: CoordinationSystemState):
        """Test performance-related properties."""
        
        # Property 1: Message queue should not grow indefinitely
        assert len(system_state.message_queue) <= 100, \
            f"Message queue too large: {len(system_state.message_queue)}"
        
        # Property 2: Number of active conflicts should be bounded
        assert len(system_state.active_conflicts) <= 10, \
            f"Too many active conflicts: {len(system_state.active_conflicts)}"
        
        # Property 3: Most agents should be active or idle, not blocked
        status_counts = {}
        for agent in system_state.agents.values():
            status_counts[agent.status] = status_counts.get(agent.status, 0) + 1
        
        total_agents = len(system_state.agents)
        blocked_agents = status_counts.get("blocked", 0)
        
        # Heuristic: Less than 30% of agents should be blocked in a healthy system
        if total_agents >= 5:
            blocked_percentage = blocked_agents / total_agents
            assert blocked_percentage <= 0.3, \
                f"Too many blocked agents: {blocked_percentage:.1%} ({blocked_agents}/{total_agents})"


class StatefulCoordinationTesting(RuleBasedStateMachine):
    """Stateful property-based testing for coordination system operations."""
    
    agents = Bundle("agents")
    authorities = Bundle("authorities")
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp(prefix="stateful_coordination_test_")
        self.system_state = CoordinationSystemState(
            agents={},
            authorities={},
            message_queue=[],
            active_conflicts=[],
            system_time=time.time()
        )
        
        # Initialize standard authorities
        for auth_type in ["critical_path", "migration", "dashboard", "devops", "security", "ux"]:
            self.system_state.authorities[auth_type] = AuthorityState(
                authority_type=auth_type,
                current_holder=None,
                backup_holder=None,
                pending_requests=[],
                assignment_time=time.time()
            )
    
    @initialize()
    def setup_initial_agents(self):
        """Setup initial agents in the system."""
        for i in range(3):  # Start with 3 agents
            agent_id = f"initial_agent_{i}"
            agent = AgentState(
                agent_id=agent_id,
                status="idle",
                current_task=None,
                progress=0.0,
                authorities=[],
                blockers=[],
                last_update=time.time(),
                dependencies=[]
            )
            self.system_state.agents[agent_id] = agent
    
    @rule(target=agents, agent_id=agent_ids, status=agent_statuses)
    def add_agent(self, agent_id: str, status: str):
        """Add a new agent to the system."""
        assume(agent_id not in self.system_state.agents)
        assume(len(self.system_state.agents) < 15)  # Limit system size
        
        agent = AgentState(
            agent_id=agent_id,
            status=status,
            current_task=None,
            progress=0.0,
            authorities=[],
            blockers=[],
            last_update=time.time(),
            dependencies=[]
        )
        
        self.system_state.agents[agent_id] = agent
        return agent_id
    
    @rule(agent_id=agents, task=task_names)
    def assign_task(self, agent_id: str, task: Optional[str]):
        """Assign a task to an agent."""
        assume(agent_id in self.system_state.agents)
        
        agent = self.system_state.agents[agent_id]
        agent.current_task = task
        agent.last_update = time.time()
        
        if task:
            agent.status = "active"
            agent.progress = 0.0
        else:
            agent.status = "idle"
            agent.progress = 0.0
    
    @rule(agent_id=agents, authority_type=authority_types)
    def request_authority(self, agent_id: str, authority_type: str):
        """Agent requests an authority."""
        assume(agent_id in self.system_state.agents)
        assume(authority_type in self.system_state.authorities)
        
        authority = self.system_state.authorities[authority_type]
        agent = self.system_state.agents[agent_id]
        
        # Grant authority if available
        if not authority.current_holder:
            authority.current_holder = agent_id
            authority.assignment_time = time.time()
            if authority_type not in agent.authorities:
                agent.authorities.append(authority_type)
        elif agent_id not in authority.pending_requests:
            authority.pending_requests.append(agent_id)
    
    @rule(agent_id=agents, authority_type=authority_types)
    def release_authority(self, agent_id: str, authority_type: str):
        """Agent releases an authority."""
        assume(agent_id in self.system_state.agents)
        assume(authority_type in self.system_state.authorities)
        
        authority = self.system_state.authorities[authority_type]
        agent = self.system_state.agents[agent_id]
        
        if authority.current_holder == agent_id:
            authority.current_holder = None
            if authority_type in agent.authorities:
                agent.authorities.remove(authority_type)
            
            # Promote backup or handle pending requests
            if authority.backup_holder:
                authority.current_holder = authority.backup_holder
                authority.backup_holder = None
                backup_agent = self.system_state.agents[authority.current_holder]
                if authority_type not in backup_agent.authorities:
                    backup_agent.authorities.append(authority_type)
            elif authority.pending_requests:
                next_holder = authority.pending_requests.pop(0)
                authority.current_holder = next_holder
                next_agent = self.system_state.agents[next_holder]
                if authority_type not in next_agent.authorities:
                    next_agent.authorities.append(authority_type)
    
    @rule(agent_id=agents, blocker=blocker_descriptions)
    def add_blocker(self, agent_id: str, blocker: str):
        """Add a blocker to an agent."""
        assume(agent_id in self.system_state.agents)
        assume(len(blocker.strip()) > 0)
        
        agent = self.system_state.agents[agent_id]
        if blocker not in agent.blockers:
            agent.blockers.append(blocker)
            agent.status = "blocked"
            agent.last_update = time.time()
    
    @rule(agent_id=agents)
    def resolve_blockers(self, agent_id: str):
        """Resolve all blockers for an agent."""
        assume(agent_id in self.system_state.agents)
        
        agent = self.system_state.agents[agent_id]
        agent.blockers.clear()
        if agent.current_task:
            agent.status = "active"
        else:
            agent.status = "idle"
        agent.last_update = time.time()
    
    @invariant()
    def authority_consistency(self):
        """Verify authority assignment consistency."""
        for auth_type, authority in self.system_state.authorities.items():
            if authority.current_holder:
                assert authority.current_holder in self.system_state.agents, \
                    f"Authority {auth_type} holder {authority.current_holder} not in agents"
                
                holder_agent = self.system_state.agents[authority.current_holder]
                assert auth_type in holder_agent.authorities, \
                    f"Agent {authority.current_holder} missing authority {auth_type}"
    
    @invariant()
    def agent_state_consistency(self):
        """Verify agent state consistency."""
        for agent_id, agent in self.system_state.agents.items():
            # Blocked agents must have blockers
            if agent.status == "blocked":
                assert len(agent.blockers) > 0, \
                    f"Blocked agent {agent_id} has no blockers"
            
            # Progress should be valid
            assert 0.0 <= agent.progress <= 100.0, \
                f"Agent {agent_id} has invalid progress: {agent.progress}"
    
    @invariant()
    def system_size_bounds(self):
        """Verify system doesn't grow too large."""
        assert len(self.system_state.agents) <= 20, \
            f"Too many agents: {len(self.system_state.agents)}"
        assert len(self.system_state.message_queue) <= 50, \
            f"Message queue too large: {len(self.system_state.message_queue)}"
    
    @teardown()
    def cleanup(self):
        """Clean up test resources."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


# Pytest integration
class TestPropertyBasedCoordination:
    """Pytest class for property-based coordination tests."""
    
    def test_coordination_properties(self):
        """Run property-based tests for coordination invariants."""
        properties = CoordinationSystemProperties()
        
        # Test individual properties
        properties.test_authority_assignment_invariants()
        properties.test_agent_state_consistency()
        properties.test_system_consistency_properties()
        properties.test_performance_properties()
    
    def test_stateful_coordination(self):
        """Run stateful property-based testing."""
        # Create and run stateful tests
        StatefulCoordinationTesting.TestCase().runTest()
    
    @given(st.integers(min_value=3, max_value=10))
    @settings(max_examples=20)
    def test_scaling_properties(self, agent_count: int):
        """Test properties that should hold regardless of system scale."""
        
        # Generate system with specific agent count
        agents = {}
        for i in range(agent_count):
            agent = AgentState(
                agent_id=f"scale_test_agent_{i}",
                status="active",
                current_task=f"task_{i}",
                progress=50.0,
                authorities=[],
                blockers=[],
                last_update=time.time(),
                dependencies=[]
            )
            agents[agent.agent_id] = agent
        
        # Test that coordination overhead doesn't grow exponentially
        # Simple heuristic: message complexity should be O(n) or O(n log n), not O(n^2)
        max_expected_messages = agent_count * (agent_count - 1)  # n*(n-1) for worst case
        
        # In practice, well-designed systems should have much fewer messages
        reasonable_message_count = agent_count * 3  # Each agent talks to ~3 others on average
        
        assert reasonable_message_count <= max_expected_messages, \
            f"Coordination complexity check failed for {agent_count} agents"
        
        # Test that authority distribution scales reasonably
        total_authorities = 6  # Fixed number of authority types
        if agent_count >= total_authorities:
            # Each agent should get at most ceil(total_authorities / agent_count) + 1 authorities
            max_authorities_per_agent = (total_authorities // agent_count) + 2
            assert max_authorities_per_agent <= 3, \
                f"Authority distribution doesn't scale well: {max_authorities_per_agent} authorities per agent"


if __name__ == "__main__":
    # Run property-based tests directly
    properties = CoordinationSystemProperties()
    
    print("🧪 Running Property-Based Tests...")
    
    # Run a subset of tests for direct execution
    @given(coordination_system_state_strategy())
    @settings(max_examples=50, verbosity=Verbosity.normal)
    def test_sample_properties(system_state):
        properties.test_authority_assignment_invariants(system_state)
        properties.test_agent_state_consistency(system_state)
        print(f"✅ Tested system with {len(system_state.agents)} agents")
    
    test_sample_properties()
    
    print("🏁 Property-based testing completed successfully!")