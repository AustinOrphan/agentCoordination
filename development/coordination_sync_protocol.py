#!/usr/bin/env python3
"""
Coordination Sync Protocol with Voting System
Enables democratic decision-making and conflict resolution among agents
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import logging
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoteType(Enum):
    """Types of voting mechanisms."""
    SIMPLE_MAJORITY = "simple_majority"      # >50% required
    SUPERMAJORITY = "supermajority"          # ≥66% required
    UNANIMOUS = "unanimous"                   # 100% required
    EXPERTISE_WEIGHTED = "expertise_weighted" # Votes weighted by domain expertise
    AUTHORITY_WEIGHTED = "authority_weighted" # Votes weighted by current authority

class ProposalType(Enum):
    """Types of proposals that can be voted on."""
    ARCHITECTURE_DECISION = "architecture_decision"
    PROCESS_CHANGE = "process_change"
    PRIORITY_CHANGE = "priority_change"
    RESOURCE_ALLOCATION = "resource_allocation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    EMERGENCY_RESPONSE = "emergency_response"
    ROLE_ASSIGNMENT = "role_assignment"
    POLICY_UPDATE = "policy_update"

class ProposalStatus(Enum):
    """Status of proposals in the voting system."""
    DRAFT = "draft"
    OPEN_FOR_VOTING = "open_for_voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    SUPERSEDED = "superseded"

@dataclass
class Vote:
    """Individual vote record."""
    voter_id: str
    choice: str  # "approve", "reject", "abstain"
    reasoning: Optional[str]
    cast_at: str
    weight: float = 1.0
    expertise_domains: List[str] = None
    
    def __post_init__(self):
        if self.expertise_domains is None:
            self.expertise_domains = []

@dataclass
class Proposal:
    """Proposal for agent voting."""
    proposal_id: str
    title: str
    description: str
    type: str
    proposed_by: str
    created_at: str
    voting_deadline: str
    vote_type: str
    required_domains: List[str]
    minimum_participation: float
    status: str
    options: List[str]
    votes: Dict[str, Dict]  # voter_id -> vote data
    metadata: Dict
    
    def __post_init__(self):
        if self.required_domains is None:
            self.required_domains = []
        if self.votes is None:
            self.votes = {}
        if self.metadata is None:
            self.metadata = {}

class CoordinationSyncProtocol:
    """Manages democratic decision-making and coordination synchronization."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.proposals_db_file = self.project_root / "coordination_proposals.json"
        self.voting_history_file = self.project_root / "voting_history.json"
        self.sync_state_file = self.project_root / "coordination_sync_state.json"
        
        # Initialize databases
        self.proposals_db = self._load_proposals_db()
        self.voting_history = self._load_voting_history()
        self.sync_state = self._load_sync_state()
        
        # Import related systems
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        
        try:
            from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
            self.authority_manager = DynamicAuthorityManager(project_root)
        except ImportError:
            self.authority_manager = None
        
        try:
            # Try to import domain roles manager if available
            from domain_specific_agent_roles import DomainSpecificRoleManager
            self.role_manager = DomainSpecificRoleManager(project_root)
        except ImportError:
            self.role_manager = None
    
    def _load_proposals_db(self) -> Dict:
        """Load proposals database."""
        if self.proposals_db_file.exists():
            with open(self.proposals_db_file, 'r') as f:
                return json.load(f)
        return {"proposals": {}, "version": "1.0"}
    
    def _save_proposals_db(self):
        """Save proposals database."""
        with open(self.proposals_db_file, 'w') as f:
            json.dump(self.proposals_db, f, indent=2)
    
    def _load_voting_history(self) -> List:
        """Load voting history."""
        if self.voting_history_file.exists():
            with open(self.voting_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_voting_history(self):
        """Save voting history."""
        with open(self.voting_history_file, 'w') as f:
            json.dump(self.voting_history, f, indent=2)
    
    def _load_sync_state(self) -> Dict:
        """Load coordination sync state."""
        if self.sync_state_file.exists():
            with open(self.sync_state_file, 'r') as f:
                return json.load(f)
        return {
            "last_sync": datetime.now().isoformat(),
            "consensus_state": {},
            "pending_conflicts": [],
            "version": "1.0"
        }
    
    def _save_sync_state(self):
        """Save coordination sync state."""
        with open(self.sync_state_file, 'w') as f:
            json.dump(self.sync_state, f, indent=2)\n    \n    def create_proposal(\n        self,\n        proposer_id: str,\n        title: str,\n        description: str,\n        proposal_type: ProposalType,\n        vote_type: VoteType = VoteType.SIMPLE_MAJORITY,\n        required_domains: Optional[List[str]] = None,\n        voting_duration_hours: int = 24,\n        minimum_participation: float = 0.5,\n        options: Optional[List[str]] = None\n    ) -> str:\n        \"\"\"Create a new proposal for voting.\"\"\"\n        \n        proposal_id = f\"PROP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{proposer_id}\"\n        voting_deadline = (datetime.now() + timedelta(hours=voting_duration_hours)).isoformat()\n        \n        # Default options for binary decisions\n        if options is None:\n            options = [\"approve\", \"reject\"]\n        \n        proposal = Proposal(\n            proposal_id=proposal_id,\n            title=title,\n            description=description,\n            type=proposal_type.value,\n            proposed_by=proposer_id,\n            created_at=datetime.now().isoformat(),\n            voting_deadline=voting_deadline,\n            vote_type=vote_type.value,\n            required_domains=required_domains or [],\n            minimum_participation=minimum_participation,\n            status=ProposalStatus.OPEN_FOR_VOTING.value,\n            options=options,\n            votes={},\n            metadata={\n                \"voting_duration_hours\": voting_duration_hours,\n                \"eligible_voters\": self._get_eligible_voters(required_domains)\n            }\n        )\n        \n        self.proposals_db[\"proposals\"][proposal_id] = asdict(proposal)\n        self._save_proposals_db()\n        \n        logger.info(f\"📝 Created proposal {proposal_id}: {title}\")\n        logger.info(f\"   Type: {proposal_type.value}, Vote: {vote_type.value}\")\n        logger.info(f\"   Deadline: {voting_deadline}\")\n        \n        return proposal_id\n    \n    def _get_eligible_voters(self, required_domains: Optional[List[str]] = None) -> List[str]:\n        \"\"\"Get list of agents eligible to vote on a proposal.\"\"\"\n        \n        if self.authority_manager:\n            eligible_agents = self.authority_manager.get_active_agents()\n        else:\n            # Fallback to configured agents\n            eligible_agents = [\"shark\", \"dolphin\", \"whale\", \"octopus\", \"jellyfish\", \"seahorse\"]\n        \n        # Filter by domain expertise if required\n        if required_domains and self.role_manager:\n            domain_eligible = []\n            for agent in eligible_agents:\n                agent_expertise = self.role_manager.get_agent_expertise_summary(agent)\n                agent_domains = list(agent_expertise.get(\"expertise\", {}).keys())\n                \n                if any(domain in agent_domains for domain in required_domains):\n                    domain_eligible.append(agent)\n            \n            return domain_eligible\n        \n        return eligible_agents\n    \n    def cast_vote(\n        self,\n        proposal_id: str,\n        voter_id: str,\n        choice: str,\n        reasoning: Optional[str] = None\n    ) -> bool:\n        \"\"\"Cast a vote on a proposal.\"\"\"\n        \n        if proposal_id not in self.proposals_db[\"proposals\"]:\n            logger.error(f\"Proposal {proposal_id} not found\")\n            return False\n        \n        proposal = self.proposals_db[\"proposals\"][proposal_id]\n        \n        # Check if voting is still open\n        if proposal[\"status\"] != ProposalStatus.OPEN_FOR_VOTING.value:\n            logger.warning(f\"Voting is closed for proposal {proposal_id}\")\n            return False\n        \n        # Check if deadline has passed\n        deadline = datetime.fromisoformat(proposal[\"voting_deadline\"])\n        if datetime.now() > deadline:\n            logger.warning(f\"Voting deadline has passed for proposal {proposal_id}\")\n            return False\n        \n        # Check if voter is eligible\n        eligible_voters = proposal[\"metadata\"].get(\"eligible_voters\", [])\n        if voter_id not in eligible_voters:\n            logger.warning(f\"Agent {voter_id} is not eligible to vote on proposal {proposal_id}\")\n            return False\n        \n        # Check if choice is valid\n        if choice not in proposal[\"options\"] and choice != \"abstain\":\n            logger.error(f\"Invalid choice '{choice}' for proposal {proposal_id}\")\n            return False\n        \n        # Calculate vote weight\n        vote_weight = self._calculate_vote_weight(\n            voter_id, \n            proposal[\"vote_type\"], \n            proposal[\"required_domains\"]\n        )\n        \n        # Get voter expertise domains\n        voter_domains = []\n        if self.role_manager:\n            expertise = self.role_manager.get_agent_expertise_summary(voter_id)\n            voter_domains = list(expertise.get(\"expertise\", {}).keys())\n        \n        # Create vote record\n        vote = Vote(\n            voter_id=voter_id,\n            choice=choice,\n            reasoning=reasoning,\n            cast_at=datetime.now().isoformat(),\n            weight=vote_weight,\n            expertise_domains=voter_domains\n        )\n        \n        # Store vote\n        proposal[\"votes\"][voter_id] = asdict(vote)\n        self._save_proposals_db()\n        \n        logger.info(f\"🗳️  {voter_id} voted '{choice}' on proposal {proposal_id} (weight: {vote_weight:.2f})\")\n        \n        # Check if proposal can be resolved\n        self._check_proposal_resolution(proposal_id)\n        \n        return True\n    \n    def _calculate_vote_weight(\n        self, \n        voter_id: str, \n        vote_type: str, \n        required_domains: List[str]\n    ) -> float:\n        \"\"\"Calculate the weight of a vote based on vote type and voter expertise.\"\"\"\n        \n        base_weight = 1.0\n        \n        if vote_type == VoteType.SIMPLE_MAJORITY.value or vote_type == VoteType.UNANIMOUS.value:\n            return base_weight\n        \n        elif vote_type == VoteType.EXPERTISE_WEIGHTED.value and self.role_manager:\n            # Weight based on expertise in required domains\n            expertise = self.role_manager.get_agent_expertise_summary(voter_id)\n            agent_expertise = expertise.get(\"expertise\", {})\n            \n            expertise_multiplier = 1.0\n            \n            for domain in required_domains:\n                if domain in agent_expertise:\n                    level = agent_expertise[domain][\"level\"]\n                    level_weights = {\n                        \"novice\": 0.5,\n                        \"competent\": 1.0,\n                        \"proficient\": 1.5,\n                        \"expert\": 2.0,\n                        \"master\": 2.5\n                    }\n                    expertise_multiplier *= level_weights.get(level, 1.0)\n            \n            return min(expertise_multiplier, 3.0)  # Cap at 3x weight\n        \n        elif vote_type == VoteType.AUTHORITY_WEIGHTED.value and self.authority_manager:\n            # Weight based on current authority level\n            authorities = self.authority_manager.get_agent_authorities(voter_id)\n            \n            if not authorities:\n                return 0.5  # Reduced weight for agents without authority\n            \n            authority_multiplier = 1.0\n            for auth in authorities:\n                auth_type = auth.get(\"authority_type\", \"task\")\n                if auth_type == \"project\":\n                    authority_multiplier += 1.0\n                elif auth_type == \"emergency\":\n                    authority_multiplier += 0.5\n                elif auth_type == \"collaborative\":\n                    authority_multiplier += 0.3\n            \n            return min(authority_multiplier, 2.5)  # Cap at 2.5x weight\n        \n        return base_weight\n    \n    def _check_proposal_resolution(self, proposal_id: str):\n        \"\"\"Check if a proposal can be resolved based on current votes.\"\"\"\n        \n        proposal = self.proposals_db[\"proposals\"][proposal_id]\n        \n        # Check if deadline has passed\n        deadline = datetime.fromisoformat(proposal[\"voting_deadline\"])\n        if datetime.now() <= deadline:\n            # Check if we have enough votes to make a decision early\n            if not self._can_resolve_early(proposal):\n                return\n        \n        eligible_voters = proposal[\"metadata\"].get(\"eligible_voters\", [])\n        total_eligible = len(eligible_voters)\n        \n        # Calculate participation rate\n        voters_participated = len([v for v in proposal[\"votes\"].values() if v[\"choice\"] != \"abstain\"])\n        participation_rate = voters_participated / total_eligible if total_eligible > 0 else 0\n        \n        # Check minimum participation requirement\n        if participation_rate < proposal[\"minimum_participation\"]:\n            if datetime.now() > deadline:\n                self._reject_proposal(proposal_id, \"Insufficient participation\")\n            return\n        \n        # Calculate vote results\n        result = self._calculate_vote_result(proposal)\n        \n        if result[\"decision\"] == \"approve\":\n            self._approve_proposal(proposal_id, result)\n        elif result[\"decision\"] == \"reject\":\n            self._reject_proposal(proposal_id, \"Majority rejection\")\n        # If \"pending\", continue voting until deadline\n    \n    def _can_resolve_early(self, proposal: Dict) -> bool:\n        \"\"\"Check if proposal can be resolved before deadline.\"\"\"\n        \n        eligible_voters = proposal[\"metadata\"].get(\"eligible_voters\", [])\n        total_eligible = len(eligible_voters)\n        \n        # For unanimous votes, need all voters\n        if proposal[\"vote_type\"] == VoteType.UNANIMOUS.value:\n            return len(proposal[\"votes\"]) == total_eligible\n        \n        # For other vote types, check if remaining votes can't change outcome\n        result = self._calculate_vote_result(proposal)\n        \n        if result[\"decision\"] in [\"approve\", \"reject\"]:\n            # Check if remaining voters can change the outcome\n            remaining_voters = total_eligible - len(proposal[\"votes\"])\n            \n            if proposal[\"vote_type\"] == VoteType.SUPERMAJORITY.value:\n                required_percentage = 0.66\n            else:\n                required_percentage = 0.50\n            \n            # Simplified check - in practice would need more sophisticated analysis\n            return remaining_voters < (total_eligible * 0.2)  # Less than 20% remaining\n        \n        return False\n    \n    def _calculate_vote_result(self, proposal: Dict) -> Dict:\n        \"\"\"Calculate the current result of voting.\"\"\"\n        \n        vote_type = proposal[\"vote_type\"]\n        votes = proposal[\"votes\"]\n        \n        # Separate votes by choice\n        approve_votes = [v for v in votes.values() if v[\"choice\"] == \"approve\"]\n        reject_votes = [v for v in votes.values() if v[\"choice\"] == \"reject\"]\n        abstain_votes = [v for v in votes.values() if v[\"choice\"] == \"abstain\"]\n        \n        # Calculate weighted totals\n        approve_weight = sum(v[\"weight\"] for v in approve_votes)\n        reject_weight = sum(v[\"weight\"] for v in reject_votes)\n        total_weight = approve_weight + reject_weight  # Abstentions don't count toward total\n        \n        if total_weight == 0:\n            return {\"decision\": \"pending\", \"approve_percentage\": 0, \"reject_percentage\": 0}\n        \n        approve_percentage = (approve_weight / total_weight) * 100\n        reject_percentage = (reject_weight / total_weight) * 100\n        \n        # Determine decision based on vote type\n        decision = \"pending\"\n        \n        if vote_type == VoteType.UNANIMOUS.value:\n            if reject_weight > 0:\n                decision = \"reject\"\n            elif len(approve_votes) == len(proposal[\"metadata\"].get(\"eligible_voters\", [])):\n                decision = \"approve\"\n        \n        elif vote_type == VoteType.SUPERMAJORITY.value:\n            if approve_percentage >= 66.67:\n                decision = \"approve\"\n            elif reject_percentage > 33.33:\n                decision = \"reject\"\n        \n        else:  # SIMPLE_MAJORITY, EXPERTISE_WEIGHTED, AUTHORITY_WEIGHTED\n            if approve_percentage > 50:\n                decision = \"approve\"\n            elif reject_percentage > 50:\n                decision = \"reject\"\n        \n        return {\n            \"decision\": decision,\n            \"approve_percentage\": approve_percentage,\n            \"reject_percentage\": reject_percentage,\n            \"approve_weight\": approve_weight,\n            \"reject_weight\": reject_weight,\n            \"total_votes\": len(votes),\n            \"abstentions\": len(abstain_votes)\n        }\n    \n    def _approve_proposal(self, proposal_id: str, result: Dict):\n        \"\"\"Approve a proposal and execute its outcome.\"\"\"\n        \n        proposal = self.proposals_db[\"proposals\"][proposal_id]\n        proposal[\"status\"] = ProposalStatus.APPROVED.value\n        proposal[\"resolved_at\"] = datetime.now().isoformat()\n        proposal[\"result\"] = result\n        \n        self._save_proposals_db()\n        \n        # Add to voting history\n        self.voting_history.append({\n            \"proposal_id\": proposal_id,\n            \"title\": proposal[\"title\"],\n            \"result\": \"approved\",\n            \"resolved_at\": proposal[\"resolved_at\"],\n            \"vote_breakdown\": result\n        })\n        self._save_voting_history()\n        \n        logger.info(f\"✅ Proposal {proposal_id} APPROVED ({result['approve_percentage']:.1f}% approval)\")\n        \n        # Execute proposal outcome\n        self._execute_proposal_outcome(proposal)\n    \n    def _reject_proposal(self, proposal_id: str, reason: str):\n        \"\"\"Reject a proposal.\"\"\"\n        \n        proposal = self.proposals_db[\"proposals\"][proposal_id]\n        proposal[\"status\"] = ProposalStatus.REJECTED.value\n        proposal[\"resolved_at\"] = datetime.now().isoformat()\n        proposal[\"rejection_reason\"] = reason\n        \n        self._save_proposals_db()\n        \n        # Add to voting history\n        self.voting_history.append({\n            \"proposal_id\": proposal_id,\n            \"title\": proposal[\"title\"],\n            \"result\": \"rejected\",\n            \"resolved_at\": proposal[\"resolved_at\"],\n            \"rejection_reason\": reason\n        })\n        self._save_voting_history()\n        \n        logger.info(f\"❌ Proposal {proposal_id} REJECTED: {reason}\")\n    \n    def _execute_proposal_outcome(self, proposal: Dict):\n        \"\"\"Execute the outcome of an approved proposal.\"\"\"\n        \n        proposal_type = proposal[\"type\"]\n        \n        logger.info(f\"🔄 Executing proposal outcome: {proposal['title']}\")\n        \n        # Implementation would depend on proposal type\n        execution_result = {\n            \"executed_at\": datetime.now().isoformat(),\n            \"execution_status\": \"completed\",\n            \"actions_taken\": []\n        }\n        \n        if proposal_type == ProposalType.ROLE_ASSIGNMENT.value:\n            # Handle role assignment\n            execution_result[\"actions_taken\"].append(\"Role assignment processed\")\n        \n        elif proposal_type == ProposalType.PRIORITY_CHANGE.value:\n            # Handle priority changes\n            execution_result[\"actions_taken\"].append(\"Priority levels updated\")\n        \n        elif proposal_type == ProposalType.PROCESS_CHANGE.value:\n            # Handle process changes\n            execution_result[\"actions_taken\"].append(\"Process documentation updated\")\n        \n        # Add execution result to proposal\n        proposal[\"execution_result\"] = execution_result\n    \n    def get_active_proposals(self) -> List[Dict]:\n        \"\"\"Get all proposals currently open for voting.\"\"\"\n        \n        active_proposals = []\n        \n        for proposal_id, proposal in self.proposals_db[\"proposals\"].items():\n            if proposal[\"status\"] == ProposalStatus.OPEN_FOR_VOTING.value:\n                # Check if deadline has passed\n                deadline = datetime.fromisoformat(proposal[\"voting_deadline\"])\n                if datetime.now() <= deadline:\n                    active_proposals.append(proposal)\n                else:\n                    # Auto-close expired proposals\n                    self._check_proposal_resolution(proposal_id)\n        \n        return sorted(active_proposals, key=lambda p: p[\"voting_deadline\"])\n    \n    def get_proposal_status(self, proposal_id: str) -> Optional[Dict]:\n        \"\"\"Get detailed status of a proposal.\"\"\"\n        \n        if proposal_id not in self.proposals_db[\"proposals\"]:\n            return None\n        \n        proposal = self.proposals_db[\"proposals\"][proposal_id]\n        result = self._calculate_vote_result(proposal)\n        \n        eligible_voters = proposal[\"metadata\"].get(\"eligible_voters\", [])\n        voted_agents = list(proposal[\"votes\"].keys())\n        not_voted = [agent for agent in eligible_voters if agent not in voted_agents]\n        \n        return {\n            \"proposal\": proposal,\n            \"current_result\": result,\n            \"participation\": {\n                \"eligible_voters\": len(eligible_voters),\n                \"votes_cast\": len(voted_agents),\n                \"participation_rate\": len(voted_agents) / len(eligible_voters) if eligible_voters else 0,\n                \"not_voted\": not_voted\n            },\n            \"time_remaining\": self._get_time_remaining(proposal[\"voting_deadline\"])\n        }\n    \n    def _get_time_remaining(self, deadline_iso: str) -> Dict:\n        \"\"\"Get time remaining until deadline.\"\"\"\n        \n        deadline = datetime.fromisoformat(deadline_iso)\n        now = datetime.now()\n        \n        if now >= deadline:\n            return {\"expired\": True, \"hours_remaining\": 0}\n        \n        time_diff = deadline - now\n        hours_remaining = time_diff.total_seconds() / 3600\n        \n        return {\n            \"expired\": False,\n            \"hours_remaining\": hours_remaining,\n            \"deadline\": deadline_iso\n        }\n    \n    def sync_coordination_state(self) -> Dict:\n        \"\"\"Synchronize coordination state across all agents.\"\"\"\n        \n        logger.info(\"🔄 Synchronizing coordination state across agents\")\n        \n        sync_result = {\n            \"sync_timestamp\": datetime.now().isoformat(),\n            \"active_proposals\": len(self.get_active_proposals()),\n            \"pending_conflicts\": len(self.sync_state.get(\"pending_conflicts\", [])),\n            \"consensus_items\": 0,\n            \"sync_status\": \"success\"\n        }\n        \n        # Update sync state\n        self.sync_state[\"last_sync\"] = sync_result[\"sync_timestamp\"]\n        self._save_sync_state()\n        \n        return sync_result\n\n\ndef demonstrate_coordination_sync():\n    \"\"\"Demonstrate the coordination sync protocol with voting.\"\"\"\n    \n    logger.info(\"🗳️  Starting Coordination Sync Protocol Demonstration\")\n    \n    protocol = CoordinationSyncProtocol()\n    \n    # Create sample proposals\n    proposals = [\n        {\n            \"proposer\": \"shark\",\n            \"title\": \"Adopt microservices architecture for user service\",\n            \"description\": \"Proposal to break down the monolithic user service into microservices for better scalability and maintainability.\",\n            \"type\": ProposalType.ARCHITECTURE_DECISION,\n            \"vote_type\": VoteType.EXPERTISE_WEIGHTED,\n            \"required_domains\": [\"backend\", \"architecture\"],\n            \"hours\": 48\n        },\n        {\n            \"proposer\": \"dolphin\",\n            \"title\": \"Implement weekly code review sessions\",\n            \"description\": \"Establish mandatory weekly code review sessions to improve code quality and knowledge sharing.\",\n            \"type\": ProposalType.PROCESS_CHANGE,\n            \"vote_type\": VoteType.SIMPLE_MAJORITY,\n            \"required_domains\": [],\n            \"hours\": 24\n        },\n        {\n            \"proposer\": \"whale\",\n            \"title\": \"Prioritize security audit over new features\",\n            \"description\": \"Temporarily halt new feature development to focus on comprehensive security audit.\",\n            \"type\": ProposalType.PRIORITY_CHANGE,\n            \"vote_type\": VoteType.SUPERMAJORITY,\n            \"required_domains\": [\"security\"],\n            \"hours\": 12\n        }\n    ]\n    \n    print(\"\\n\" + \"=\"*60)\n    print(\"📝 CREATING PROPOSALS\")\n    print(\"=\"*60)\n    \n    created_proposals = []\n    for prop in proposals:\n        proposal_id = protocol.create_proposal(\n            proposer_id=prop[\"proposer\"],\n            title=prop[\"title\"],\n            description=prop[\"description\"],\n            proposal_type=prop[\"type\"],\n            vote_type=prop[\"vote_type\"],\n            required_domains=prop[\"required_domains\"],\n            voting_duration_hours=prop[\"hours\"]\n        )\n        created_proposals.append(proposal_id)\n        print(f\"✅ {prop['title'][:50]}...\")\n    \n    # Simulate voting\n    print(\"\\n\" + \"=\"*60)\n    print(\"🗳️  SIMULATING VOTING\")\n    print(\"=\"*60)\n    \n    # Proposal 1: Architecture decision (expertise-weighted)\n    voting_scenarios = [\n        # Proposal 1: Architecture decision\n        (created_proposals[0], [\n            (\"shark\", \"approve\", \"Strong security benefits\"),\n            (\"seahorse\", \"approve\", \"Better scalability for growth\"),\n            (\"whale\", \"reject\", \"Too complex for current team size\"),\n            (\"dolphin\", \"approve\", \"Easier frontend integration\")\n        ]),\n        # Proposal 2: Code review process\n        (created_proposals[1], [\n            (\"shark\", \"approve\", \"Improves code quality\"),\n            (\"dolphin\", \"approve\", \"Great for knowledge sharing\"),\n            (\"whale\", \"approve\", \"Worth the time investment\"),\n            (\"octopus\", \"reject\", \"Too time-consuming\"),\n            (\"jellyfish\", \"approve\", \"Helps catch bugs early\")\n        ]),\n        # Proposal 3: Security priority (supermajority required)\n        (created_proposals[2], [\n            (\"shark\", \"approve\", \"Critical for user trust\"),\n            (\"whale\", \"approve\", \"Security should be top priority\"),\n            (\"seahorse\", \"approve\", \"Necessary for compliance\"),\n            (\"dolphin\", \"reject\", \"Will delay product roadmap\")\n        ])\n    ]\n    \n    for proposal_id, votes in voting_scenarios:\n        proposal_status = protocol.get_proposal_status(proposal_id)\n        print(f\"\\n📊 Voting on: {proposal_status['proposal']['title'][:40]}...\")\n        \n        for voter, choice, reason in votes:\n            success = protocol.cast_vote(proposal_id, voter, choice, reason)\n            if success:\n                print(f\"   {voter}: {choice} - {reason}\")\n        \n        # Show results\n        final_status = protocol.get_proposal_status(proposal_id)\n        result = final_status[\"current_result\"]\n        print(f\"   Result: {result['decision']} ({result['approve_percentage']:.1f}% approval)\")\n    \n    # Show active proposals\n    print(\"\\n\" + \"=\"*60)\n    print(\"📋 ACTIVE PROPOSALS SUMMARY\")\n    print(\"=\"*60)\n    \n    active_proposals = protocol.get_active_proposals()\n    for proposal in active_proposals:\n        status = protocol.get_proposal_status(proposal[\"proposal_id\"])\n        result = status[\"current_result\"]\n        participation = status[\"participation\"]\n        \n        print(f\"\\n📄 {proposal['title']}\")\n        print(f\"   Status: {proposal['status']}\")\n        print(f\"   Votes: {participation['votes_cast']}/{participation['eligible_voters']} ({participation['participation_rate']*100:.0f}%)\")\n        print(f\"   Current: {result['approve_percentage']:.1f}% approve, {result['reject_percentage']:.1f}% reject\")\n        \n        if not status[\"time_remaining\"][\"expired\"]:\n            hours = status[\"time_remaining\"][\"hours_remaining\"]\n            print(f\"   Time left: {hours:.1f} hours\")\n    \n    # Sync coordination state\n    print(\"\\n\" + \"=\"*60)\n    print(\"🔄 COORDINATION SYNC\")\n    print(\"=\"*60)\n    \n    sync_result = protocol.sync_coordination_state()\n    print(f\"✅ Sync completed at {sync_result['sync_timestamp']}\")\n    print(f\"   Active proposals: {sync_result['active_proposals']}\")\n    print(f\"   Pending conflicts: {sync_result['pending_conflicts']}\")\n    print(f\"   Status: {sync_result['sync_status']}\")\n    \n    logger.info(\"🗳️  Coordination Sync Protocol demonstration completed\")\n\n\nif __name__ == \"__main__\":\n    demonstrate_coordination_sync()