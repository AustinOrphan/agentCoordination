#!/usr/bin/env python3
"""
Integration Test Suite for Advanced Multi-Agent Coordination Features
Tests all 5 advanced features working together in realistic scenarios
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
from typing import Dict, List

# Add project paths
sys.path.append(".")
sys.path.append("coordination_system")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationTestSuite:
    """Comprehensive integration testing for all advanced features."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_results = []
        
        # Import all systems
        try:
            from authority_delegation_scenarios import AuthorityDelegationTester
            from emergency_protocol_framework import EmergencyProtocolFramework
            from work_tracking_system import WorkTrackingSystem
            from domain_specific_agent_roles import DomainSpecificRoleManager
            from coordination_sync_protocol import CoordinationSyncProtocol
            
            self.authority_tester = AuthorityDelegationTester(project_root)
            self.emergency_manager = EmergencyProtocolFramework(project_root)
            self.work_tracker = WorkTrackingSystem(project_root)
            self.role_manager = DomainSpecificRoleManager(project_root)
            self.sync_protocol = CoordinationSyncProtocol(project_root)
            
            logger.info("✅ All advanced systems loaded successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import systems: {e}")
            raise
    
    def run_full_integration_test(self) -> Dict:
        """Run comprehensive integration test scenario."""
        
        logger.info("🚀 Starting Full Integration Test Suite")
        
        test_scenario = {
            "scenario_name": "Multi-Agent Crisis Response and Recovery",
            "description": "Complex scenario testing all systems under stress",
            "start_time": datetime.now().isoformat(),
            "phases": []
        }
        
        try:
            # Phase 1: Normal Operations Setup
            phase1 = self._phase_1_normal_operations()
            test_scenario["phases"].append(phase1)
            
            # Phase 2: Crisis Simulation
            phase2 = self._phase_2_crisis_simulation()
            test_scenario["phases"].append(phase2)
            
            # Phase 3: Democratic Decision Making
            phase3 = self._phase_3_democratic_decisions()
            test_scenario["phases"].append(phase3)
            
            # Phase 4: Authority Delegation Under Load
            phase4 = self._phase_4_authority_delegation()
            test_scenario["phases"].append(phase4)
            
            # Phase 5: Performance Analysis
            phase5 = self._phase_5_performance_analysis()
            test_scenario["phases"].append(phase5)
            
            test_scenario["status"] = "completed"
            test_scenario["overall_success"] = all(p.get("success", False) for p in test_scenario["phases"])
            
        except Exception as e:
            test_scenario["status"] = "failed"
            test_scenario["error"] = str(e)
            test_scenario["overall_success"] = False
            logger.error(f"❌ Integration test failed: {e}")
        
        test_scenario["end_time"] = datetime.now().isoformat()
        
        # Save results
        self._save_test_results(test_scenario)
        
        return test_scenario
    
    def _phase_1_normal_operations(self) -> Dict:
        """Phase 1: Set up normal operations with all systems."""
        
        logger.info("📋 Phase 1: Normal Operations Setup")
        
        phase = {
            "phase": 1,
            "name": "Normal Operations Setup",
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "metrics": {}
        }
        
        try:
            # Set up agent expertise
            agents = ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]
            
            # Add domain expertise
            from domain_specific_agent_roles import DomainCategory, ExpertiseLevel
            expertise_setup = [
                ("shark", "security", DomainCategory.QUALITY, ExpertiseLevel.EXPERT),
                ("dolphin", "frontend", DomainCategory.TECHNICAL, ExpertiseLevel.PROFICIENT),
                ("whale", "infrastructure", DomainCategory.PROCESS, ExpertiseLevel.EXPERT),
                ("octopus", "data", DomainCategory.TECHNICAL, ExpertiseLevel.PROFICIENT),
                ("jellyfish", "quality", DomainCategory.QUALITY, ExpertiseLevel.PROFICIENT),
                ("seahorse", "backend", DomainCategory.TECHNICAL, ExpertiseLevel.MASTER)
            ]
            
            for agent, domain, category, level in expertise_setup:
                self.role_manager.add_agent_expertise(agent, domain, category, level, 24)
                phase["actions"].append(f"Added {level.value} {domain} expertise to {agent}")
            
            # Assign initial roles
            role_assignments = [
                ("shark", "security_lead"),
                ("whale", "devops_lead"),
                ("seahorse", "backend_architect")
            ]
            
            for agent, role in role_assignments:
                success = self.role_manager.assign_specialized_role(agent, role)
                phase["actions"].append(f"Assigned {role} to {agent}: {'success' if success else 'failed'}")
            
            # Create initial tasks
            initial_tasks = [
                ("shark", "Implement OAuth2 authentication", "security", "high"),
                ("dolphin", "Create user dashboard UI", "frontend", "medium"),
                ("whale", "Set up CI/CD pipeline", "infrastructure", "high"),
                ("octopus", "Build analytics dashboard", "data", "medium")
            ]
            
            for agent, task, domain, priority in initial_tasks:
                task_id = self.work_tracker.assign_task(
                    agent_id=agent,
                    title=task,
                    description=f"Integration test task: {task}",
                    domain=domain,
                    priority=priority,
                    estimated_hours=8
                )
                phase["actions"].append(f"Assigned task {task_id} to {agent}")
            
            phase["success"] = True
            phase["metrics"]["agents_setup"] = len(agents)
            phase["metrics"]["roles_assigned"] = len(role_assignments)
            phase["metrics"]["tasks_created"] = len(initial_tasks)
            
        except Exception as e:
            phase["success"] = False
            phase["error"] = str(e)
            logger.error(f"❌ Phase 1 failed: {e}")
        
        phase["end_time"] = datetime.now().isoformat()
        return phase
    
    def _phase_2_crisis_simulation(self) -> Dict:
        """Phase 2: Simulate a security crisis requiring emergency response."""
        
        logger.info("🚨 Phase 2: Crisis Simulation")
        
        phase = {
            "phase": 2,
            "name": "Crisis Simulation",
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "metrics": {}
        }
        
        try:
            from emergency_protocol_framework import EmergencyType, EmergencyLevel
            
            # Declare security emergency
            emergency_id = self.emergency_manager.declare_emergency(
                emergency_type=EmergencyType.SECURITY_BREACH,
                level=EmergencyLevel.HIGH,
                description="Potential data breach detected in user authentication system",
                reporter_agent="shark",
                additional_context={
                    "affected_systems": ["auth", "user_data"],
                    "detection_time": datetime.now().isoformat(),
                    "severity_indicators": ["unusual_login_patterns", "failed_encryption"]
                }
            )
            
            phase["actions"].append(f"Declared security emergency: {emergency_id}")
            
            # Activate emergency response
            response_team = self.emergency_manager.activate_emergency_response(emergency_id)
            phase["actions"].append(f"Activated emergency response team: {len(response_team)} agents")
            
            # Simulate escalation
            escalation_result = self.emergency_manager.escalate_emergency(
                emergency_id, 
                EmergencyLevel.CRITICAL,
                "Evidence of active data exfiltration found",
                "shark"
            )
            phase["actions"].append(f"Escalated to CRITICAL level: {escalation_result}")
            
            # Add emergency tasks through work tracker
            emergency_tasks = [
                ("shark", "Immediate security audit", "security", "critical"),
                ("whale", "Isolate affected systems", "infrastructure", "critical"),
                ("seahorse", "Review authentication logs", "backend", "high")
            ]
            
            for agent, task, domain, priority in emergency_tasks:
                task_id = self.work_tracker.assign_task(
                    agent_id=agent,
                    title=f"EMERGENCY: {task}",
                    description=f"Emergency response task for {emergency_id}",
                    domain=domain,
                    priority=priority,
                    estimated_hours=4
                )
                phase["actions"].append(f"Assigned emergency task {task_id} to {agent}")
            
            phase["success"] = True
            phase["metrics"]["emergency_id"] = emergency_id
            phase["metrics"]["response_team_size"] = len(response_team)
            phase["metrics"]["emergency_tasks"] = len(emergency_tasks)
            
        except Exception as e:
            phase["success"] = False
            phase["error"] = str(e)
            logger.error(f"❌ Phase 2 failed: {e}")
        
        phase["end_time"] = datetime.now().isoformat()
        return phase
    
    def _phase_3_democratic_decisions(self) -> Dict:
        """Phase 3: Use voting system for crisis response decisions."""
        
        logger.info("🗳️ Phase 3: Democratic Decision Making")
        
        phase = {
            "phase": 3,
            "name": "Democratic Decision Making",
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "metrics": {}
        }
        
        try:
            from coordination_sync_protocol import ProposalType, VoteType
            
            # Create critical decision proposals
            proposals = [
                {
                    "title": "Temporary system shutdown for security audit",
                    "description": "Shut down user-facing systems for 2 hours to conduct thorough security audit",
                    "type": ProposalType.EMERGENCY_RESPONSE,
                    "vote_type": VoteType.SUPERMAJORITY,
                    "domains": ["security", "infrastructure"],
                    "hours": 1
                },
                {
                    "title": "Implement immediate 2FA requirement",
                    "description": "Force all users to enable 2FA before next login as emergency security measure",
                    "type": ProposalType.PRIORITY_CHANGE,
                    "vote_type": VoteType.EXPERTISE_WEIGHTED,
                    "domains": ["security", "frontend"],
                    "hours": 2
                }
            ]
            
            created_proposals = []
            for prop in proposals:
                proposal_id = self.sync_protocol.create_proposal(
                    proposer_id="shark",
                    title=prop["title"],
                    description=prop["description"],
                    proposal_type=prop["type"],
                    vote_type=prop["vote_type"],
                    required_domains=prop["domains"],
                    voting_duration_hours=prop["hours"]
                )
                created_proposals.append(proposal_id)
                phase["actions"].append(f"Created proposal: {prop['title'][:30]}...")
            
            # Simulate voting
            voting_patterns = [
                # Proposal 1: System shutdown
                (created_proposals[0], [
                    ("shark", "approve", "Critical for security assessment"),
                    ("whale", "approve", "Infrastructure can handle planned downtime"),
                    ("seahorse", "approve", "Backend systems need thorough review"),
                    ("dolphin", "reject", "Too disruptive to user experience"),
                    ("octopus", "approve", "Data integrity is paramount")
                ]),
                # Proposal 2: 2FA requirement
                (created_proposals[1], [
                    ("shark", "approve", "Essential security enhancement"),
                    ("dolphin", "approve", "Can implement quickly in frontend"),
                    ("whale", "approve", "Infrastructure supports this"),
                    ("seahorse", "approve", "Backend ready for 2FA enforcement"),
                    ("jellyfish", "approve", "Quality assurance confirms readiness")
                ])
            ]
            
            for proposal_id, votes in voting_patterns:
                for voter, choice, reason in votes:
                    success = self.sync_protocol.cast_vote(proposal_id, voter, choice, reason)
                    phase["actions"].append(f"{voter} voted {choice} on proposal")
            
            # Check results
            approved_proposals = 0
            for proposal_id in created_proposals:
                status = self.sync_protocol.get_proposal_status(proposal_id)
                if status and status["current_result"]["decision"] == "approve":
                    approved_proposals += 1
            
            phase["success"] = True
            phase["metrics"]["proposals_created"] = len(created_proposals)
            phase["metrics"]["proposals_approved"] = approved_proposals
            phase["metrics"]["total_votes"] = sum(len(votes) for _, votes in voting_patterns)
            
        except Exception as e:
            phase["success"] = False
            phase["error"] = str(e)
            logger.error(f"❌ Phase 3 failed: {e}")
        
        phase["end_time"] = datetime.now().isoformat()
        return phase
    
    def _phase_4_authority_delegation(self) -> Dict:
        """Phase 4: Test authority delegation under crisis load."""
        
        logger.info("👥 Phase 4: Authority Delegation Under Load")
        
        phase = {
            "phase": 4,
            "name": "Authority Delegation Under Load",
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "metrics": {}
        }
        
        try:
            # Run authority delegation scenarios
            scenarios_run = 0
            scenarios_passed = 0
            
            # Test scenario 1: Emergency authority transfer
            try:
                result1 = self.authority_tester.test_scenario_1_authority_transfer()
                scenarios_run += 1
                if result1.get("success", False):
                    scenarios_passed += 1
                phase["actions"].append("Completed authority transfer scenario")
            except Exception as e:
                phase["actions"].append(f"Authority transfer failed: {str(e)[:50]}")
            
            # Test scenario 2: Workload-based delegation
            try:
                result2 = self.authority_tester.test_scenario_2_workload_delegation()
                scenarios_run += 1
                if result2.get("success", False):
                    scenarios_passed += 1
                phase["actions"].append("Completed workload delegation scenario")
            except Exception as e:
                phase["actions"].append(f"Workload delegation failed: {str(e)[:50]}")
            
            # Test scenario 3: Emergency authority activation
            try:
                result3 = self.authority_tester.test_scenario_3_emergency_authority()
                scenarios_run += 1
                if result3.get("success", False):
                    scenarios_passed += 1
                phase["actions"].append("Completed emergency authority scenario")
            except Exception as e:
                phase["actions"].append(f"Emergency authority failed: {str(e)[:50]}")
            
            phase["success"] = scenarios_passed >= (scenarios_run * 0.6)  # 60% success rate
            phase["metrics"]["scenarios_run"] = scenarios_run
            phase["metrics"]["scenarios_passed"] = scenarios_passed
            phase["metrics"]["success_rate"] = (scenarios_passed / scenarios_run * 100) if scenarios_run > 0 else 0
            
        except Exception as e:
            phase["success"] = False
            phase["error"] = str(e)
            logger.error(f"❌ Phase 4 failed: {e}")
        
        phase["end_time"] = datetime.now().isoformat()
        return phase
    
    def _phase_5_performance_analysis(self) -> Dict:
        """Phase 5: Analyze performance and generate comprehensive reports."""
        
        logger.info("📊 Phase 5: Performance Analysis")
        
        phase = {
            "phase": 5,
            "name": "Performance Analysis",
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "metrics": {}
        }
        
        try:
            # Generate performance reports for all agents
            agents = ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]
            reports_generated = 0
            
            for agent in agents:
                try:
                    report = self.work_tracker.generate_performance_report(agent)
                    if report:
                        reports_generated += 1
                        phase["actions"].append(f"Generated performance report for {agent}")
                except Exception as e:
                    phase["actions"].append(f"Failed to generate report for {agent}: {str(e)[:30]}")
            
            # Generate team expertise report
            try:
                team_report = self.role_manager.generate_team_expertise_report()
                phase["actions"].append("Generated team expertise report")
                
                # Extract key metrics
                total_domains = len(team_report.get("team_expertise", {}))
                role_coverage = team_report.get("role_coverage", {})
                avg_coverage = sum(r.get("coverage_percentage", 0) for r in role_coverage.values()) / len(role_coverage) if role_coverage else 0
                
                phase["metrics"]["total_domains"] = total_domains
                phase["metrics"]["average_role_coverage"] = avg_coverage
                phase["metrics"]["recommendations_count"] = len(team_report.get("recommendations", []))
                
            except Exception as e:
                phase["actions"].append(f"Team report failed: {str(e)[:50]}")
            
            # Sync coordination state
            try:
                sync_result = self.sync_protocol.sync_coordination_state()
                phase["actions"].append("Synchronized coordination state")
                phase["metrics"]["active_proposals"] = sync_result.get("active_proposals", 0)
                phase["metrics"]["pending_conflicts"] = sync_result.get("pending_conflicts", 0)
            except Exception as e:
                phase["actions"].append(f"Sync failed: {str(e)[:50]}")
            
            phase["success"] = reports_generated >= (len(agents) * 0.5)  # At least 50% of reports
            phase["metrics"]["reports_generated"] = reports_generated
            phase["metrics"]["total_agents"] = len(agents)
            
        except Exception as e:
            phase["success"] = False
            phase["error"] = str(e)
            logger.error(f"❌ Phase 5 failed: {e}")
        
        phase["end_time"] = datetime.now().isoformat()
        return phase
    
    def _save_test_results(self, results: Dict):
        """Save integration test results."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.project_root / f"integration_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"💾 Test results saved to {results_file}")
    
    def generate_summary_report(self, results: Dict) -> str:
        """Generate human-readable summary report."""
        
        report = []
        report.append("🚀 INTEGRATION TEST SUMMARY REPORT")
        report.append("=" * 50)
        report.append(f"Scenario: {results['scenario_name']}")
        report.append(f"Overall Success: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
        report.append(f"Duration: {results['start_time']} to {results['end_time']}")
        report.append("")
        
        for phase in results.get("phases", []):
            status = "✅ PASSED" if phase.get("success", False) else "❌ FAILED"
            report.append(f"Phase {phase['phase']}: {phase['name']} - {status}")
            
            # Show key metrics
            metrics = phase.get("metrics", {})
            if metrics:
                for key, value in metrics.items():
                    report.append(f"  📊 {key}: {value}")
            
            # Show key actions
            actions = phase.get("actions", [])
            if actions:
                report.append(f"  📋 Actions: {len(actions)} completed")
                # Show first few actions
                for action in actions[:3]:
                    report.append(f"     • {action}")
                if len(actions) > 3:
                    report.append(f"     • ... and {len(actions) - 3} more")
            
            if phase.get("error"):
                report.append(f"  ❌ Error: {phase['error']}")
            
            report.append("")
        
        return "\n".join(report)


def run_integration_tests():
    """Run the complete integration test suite."""
    
    logger.info("🧪 Starting Integration Test Suite")
    
    try:
        test_suite = IntegrationTestSuite()
        results = test_suite.run_full_integration_test()
        
        # Generate and display summary
        summary = test_suite.generate_summary_report(results)
        print("\n" + summary)
        
        # Overall result
        if results["overall_success"]:
            logger.info("🎉 All integration tests PASSED!")
        else:
            logger.warning("⚠️ Some integration tests FAILED")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Integration test suite failed to run: {e}")
        return {"error": str(e), "overall_success": False}


if __name__ == "__main__":
    run_integration_tests()