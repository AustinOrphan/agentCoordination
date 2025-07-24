#!/usr/bin/env python3
"""
Authority Delegation Scenarios
Tests complex authority management scenarios in the dynamic system
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthorityDelegationTester:
    """Tests various authority delegation scenarios."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
        # Import the dynamic authority manager
        import sys
        sys.path.append(str(self.project_root))
        sys.path.append(str(self.project_root / "coordination_system"))
        try:
            from coordination_system.dynamic_authority_manager import DynamicAuthorityManager
            self.authority_manager = DynamicAuthorityManager(project_root)
        except ImportError as e:
            logger.error(f"Could not import DynamicAuthorityManager: {e}")
            self.authority_manager = None
            
        self.test_results = []
        
    def setup_test_environment(self):
        """Set up test environment with mock agents."""
        logger.info("Setting up test environment...")
        
        # Create mock agent status files
        agent_status_dir = self.project_root / "agent_status"
        agent_status_dir.mkdir(exist_ok=True)
        
        # Create 6 test agents with varying workloads
        test_agents = [
            {"name": "shark", "workload": 30, "expertise": ["backend", "security"]},
            {"name": "dolphin", "workload": 50, "expertise": ["frontend", "ui"]},
            {"name": "whale", "workload": 20, "expertise": ["infrastructure", "deployment"]},
            {"name": "octopus", "workload": 70, "expertise": ["data", "analytics"]},
            {"name": "jellyfish", "workload": 40, "expertise": ["quality", "testing"]},
            {"name": "seahorse", "workload": 60, "expertise": ["architecture", "design"]}
        ]
        
        for agent in test_agents:
            status_file = agent_status_dir / f"{agent['name']}_status.json"
            status_data = {
                "agent_name": agent["name"],
                "status": "active",
                "current_task": "Available for assignment",
                "progress": 0,
                "last_update": datetime.now().isoformat(),
                "workload": agent["workload"],
                "expertise": agent["expertise"],
                "activities": [],
                "blockers": []
            }
            
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        
        logger.info(f"Created {len(test_agents)} test agent status files")
        
    def test_scenario_1_authority_transfer(self):
        """Test Scenario 1: Authority Transfer Due to Workload"""
        logger.info("🧪 Testing Scenario 1: Authority Transfer Due to Workload")
        
        scenario_result = {
            "scenario": "Authority Transfer Due to Workload",
            "description": "Agent becomes overloaded and transfers authority to less busy agent",
            "steps": [],
            "success": False,
            "issues": []
        }
        
        try:
            # Step 1: Assign authority to a moderately loaded agent
            result1 = self.authority_manager.assign_authority(
                "Implement user authentication system with OAuth2",
                preferred_agent="dolphin"  # Currently at 50% workload
            )
            scenario_result["steps"].append({
                "step": 1,
                "action": "Assign backend authority to dolphin (50% workload)",
                "result": f"Assigned to {result1.get('agent', 'None')}"
            })
            
            # Step 2: Simulate workload increase
            self.authority_manager._update_agent_workload("dolphin", 30)  # Now at 80%
            scenario_result["steps"].append({
                "step": 2,
                "action": "Increase dolphin's workload to 80%",
                "result": "Workload updated"
            })
            
            # Step 3: Try to assign another task - should go to less loaded agent
            result2 = self.authority_manager.assign_authority(
                "Add OAuth2 token refresh mechanism"
            )
            scenario_result["steps"].append({
                "step": 3,
                "action": "Assign related task - should go to less loaded agent",
                "result": f"Assigned to {result2.get('agent', 'None')}"
            })
            
            # Step 4: Test authority rebalancing
            self.authority_manager.rebalance_authorities()
            scenario_result["steps"].append({
                "step": 4,
                "action": "Trigger authority rebalancing",
                "result": "Rebalancing completed"
            })
            
            scenario_result["success"] = True
            
        except Exception as e:
            scenario_result["issues"].append(f"Error: {str(e)}")
            logger.error(f"Scenario 1 failed: {e}")
        
        self.test_results.append(scenario_result)
        return scenario_result
    
    def test_scenario_2_collaborative_decision(self):
        """Test Scenario 2: Collaborative Decision Making"""
        logger.info("🧪 Testing Scenario 2: Collaborative Decision Making")
        
        scenario_result = {
            "scenario": "Collaborative Decision Making",
            "description": "Multiple agents need to make a joint decision on architecture",
            "steps": [],
            "success": False,
            "issues": []
        }
        
        try:
            # Step 1: Assign collaborative authority for architecture decision
            result1 = self.authority_manager.assign_authority(
                "Decide on microservices architecture for the user service",
                task_type="collaborative"
            )
            scenario_result["steps"].append({
                "step": 1,
                "action": "Assign collaborative authority for architecture decision",
                "result": f"Primary authority: {result1.get('agent', 'None')}"
            })
            
            # Step 2: Find stakeholder agents
            from coordination_system.dynamic_authority_manager import DomainType
            backend_authority = self.authority_manager.get_authority_holders(
                domain=DomainType.BACKEND
            )
            infrastructure_authority = self.authority_manager.get_authority_holders(
                domain=DomainType.INFRASTRUCTURE
            )
            
            scenario_result["steps"].append({
                "step": 2,
                "action": "Identify stakeholder agents",
                "result": f"Backend: {len(backend_authority)}, Infrastructure: {len(infrastructure_authority)}"
            })
            
            # Step 3: Simulate decision process
            decision_data = {
                "decision_id": f"ARCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "type": "architecture",
                "description": "Microservices architecture for user service",
                "stakeholders": [result1.get('agent')],
                "status": "pending_approval",
                "options": [
                    "Monolithic approach with clear module boundaries",
                    "Microservices with event-driven communication",
                    "Hybrid approach with core services separated"
                ],
                "created_at": datetime.now().isoformat()
            }
            
            scenario_result["steps"].append({
                "step": 3,
                "action": "Create collaborative decision structure",
                "result": f"Decision ID: {decision_data['decision_id']}"
            })
            
            scenario_result["success"] = True
            
        except Exception as e:
            scenario_result["issues"].append(f"Error: {str(e)}")
            logger.error(f"Scenario 2 failed: {e}")
        
        self.test_results.append(scenario_result)
        return scenario_result
    
    def test_scenario_3_emergency_override(self):
        """Test Scenario 3: Emergency Authority Override"""
        logger.info("🧪 Testing Scenario 3: Emergency Authority Override")
        
        scenario_result = {
            "scenario": "Emergency Authority Override",
            "description": "Critical issue requiring immediate authority override",
            "steps": [],
            "success": False,
            "issues": []
        }
        
        try:
            # Step 1: Simulate critical security issue
            emergency_result = self.authority_manager.assign_authority(
                "URGENT: Security breach detected in authentication system - immediate action required",
                task_type="emergency"
            )
            scenario_result["steps"].append({
                "step": 1,
                "action": "Assign emergency authority for security breach",
                "result": f"Emergency authority granted to: {emergency_result.get('agent', 'None')}"
            })
            
            # Step 2: Check authority type and expiration
            if emergency_result.get('agent'):
                authorities = self.authority_manager.get_agent_authorities(emergency_result['agent'])
                emergency_auth = [a for a in authorities if a.get('authority_type') == 'emergency']
                
                scenario_result["steps"].append({
                    "step": 2,
                    "action": "Verify emergency authority properties",
                    "result": f"Emergency authorities: {len(emergency_auth)}"
                })
                
                if emergency_auth:
                    expiry = emergency_auth[0].get('expires_at')
                    scenario_result["steps"].append({
                        "step": 3,
                        "action": "Check emergency authority expiration",
                        "result": f"Expires: {expiry}"
                    })
            
            # Step 3: Test emergency authority can override normal restrictions
            # Simulate all agents being busy
            for agent in ["shark", "dolphin", "whale", "octopus", "jellyfish", "seahorse"]:
                self.authority_manager._update_agent_workload(agent, 50)  # Make everyone busy
            
            # Emergency should still be assignable
            emergency_result2 = self.authority_manager.assign_authority(
                "CRITICAL: Database corruption detected - immediate backup required",
                task_type="emergency"
            )
            
            scenario_result["steps"].append({
                "step": 4,
                "action": "Test emergency override when all agents busy",
                "result": f"Emergency authority granted to: {emergency_result2.get('agent', 'None')}"
            })
            
            scenario_result["success"] = True
            
        except Exception as e:
            scenario_result["issues"].append(f"Error: {str(e)}")
            logger.error(f"Scenario 3 failed: {e}")
        
        self.test_results.append(scenario_result)
        return scenario_result
    
    def test_scenario_4_domain_expertise_matching(self):
        """Test Scenario 4: Domain Expertise Matching"""
        logger.info("🧪 Testing Scenario 4: Domain Expertise Matching")
        
        scenario_result = {
            "scenario": "Domain Expertise Matching",
            "description": "Authority assigned based on agent expertise in specific domains",
            "steps": [],
            "success": False,
            "issues": []
        }
        
        try:
            # Step 1: Test backend task assignment
            backend_result = self.authority_manager.assign_authority(
                "Optimize database queries for user authentication"
            )
            scenario_result["steps"].append({
                "step": 1,
                "action": "Assign backend database task",
                "result": f"Assigned to: {backend_result.get('agent', 'None')} (Domain: {backend_result.get('domain')})"
            })
            
            # Step 2: Test frontend task assignment  
            frontend_result = self.authority_manager.assign_authority(
                "Redesign user interface for better accessibility"
            )
            scenario_result["steps"].append({
                "step": 2,
                "action": "Assign frontend UI task",
                "result": f"Assigned to: {frontend_result.get('agent', 'None')} (Domain: {frontend_result.get('domain')})"
            })
            
            # Step 3: Test infrastructure task assignment
            infra_result = self.authority_manager.assign_authority(
                "Deploy application using Docker containers to production"
            )
            scenario_result["steps"].append({
                "step": 3,
                "action": "Assign infrastructure deployment task",
                "result": f"Assigned to: {infra_result.get('agent', 'None')} (Domain: {infra_result.get('domain')})"
            })
            
            # Step 4: Test security task assignment
            security_result = self.authority_manager.assign_authority(
                "Conduct security vulnerability assessment of authentication endpoints"
            )
            scenario_result["steps"].append({
                "step": 4,
                "action": "Assign security assessment task",
                "result": f"Assigned to: {security_result.get('agent', 'None')} (Domain: {security_result.get('domain')})"
            })
            
            scenario_result["success"] = True
            
        except Exception as e:
            scenario_result["issues"].append(f"Error: {str(e)}")
            logger.error(f"Scenario 4 failed: {e}")
        
        self.test_results.append(scenario_result)
        return scenario_result
    
    def test_scenario_5_authority_expiration(self):
        """Test Scenario 5: Authority Expiration and Renewal"""
        logger.info("🧪 Testing Scenario 5: Authority Expiration and Renewal")
        
        scenario_result = {
            "scenario": "Authority Expiration and Renewal",
            "description": "Test authority expiration handling and renewal process",
            "steps": [],
            "success": False,
            "issues": []
        }
        
        try:
            # Step 1: Assign a short-term task authority
            task_result = self.authority_manager.assign_authority(
                "Update user profile validation logic",
                task_type="task"
            )
            scenario_result["steps"].append({
                "step": 1,
                "action": "Assign task authority (8 hour expiration)",
                "result": f"Assigned to: {task_result.get('agent', 'None')}"
            })
            
            # Step 2: Check authority details
            if task_result.get('agent'):
                authorities = self.authority_manager.get_agent_authorities(task_result['agent'])
                task_auth = [a for a in authorities if a.get('task') == "Update user profile validation logic"]
                
                if task_auth:
                    expiry_time = task_auth[0].get('expires_at')
                    scenario_result["steps"].append({
                        "step": 2,
                        "action": "Check authority expiration time",
                        "result": f"Expires at: {expiry_time}"
                    })
            
            # Step 3: Test project authority (longer term)
            project_result = self.authority_manager.assign_authority(
                "Lead the user management project initiative",
                task_type="project"
            )
            scenario_result["steps"].append({
                "step": 3,
                "action": "Assign project authority (1 week expiration)",
                "result": f"Assigned to: {project_result.get('agent', 'None')}"
            })
            
            # Step 4: Simulate authority release
            if task_result.get('id') and task_result.get('agent'):
                release_success = self.authority_manager.release_authority(
                    task_result['id'], 
                    task_result['agent']
                )
                scenario_result["steps"].append({
                    "step": 4,
                    "action": "Release task authority manually",
                    "result": f"Release successful: {release_success}"
                })
            
            scenario_result["success"] = True
            
        except Exception as e:
            scenario_result["issues"].append(f"Error: {str(e)}")
            logger.error(f"Scenario 5 failed: {e}")
        
        self.test_results.append(scenario_result)
        return scenario_result
    
    def run_all_scenarios(self):
        """Run all delegation scenarios."""
        logger.info("🚀 Starting Authority Delegation Scenario Testing")
        
        if not self.authority_manager:
            logger.error("Authority manager not available - cannot run tests")
            return
        
        # Setup test environment
        self.setup_test_environment()
        
        # Run all scenarios
        scenarios = [
            self.test_scenario_1_authority_transfer,
            self.test_scenario_2_collaborative_decision,
            self.test_scenario_3_emergency_override,
            self.test_scenario_4_domain_expertise_matching,
            self.test_scenario_5_authority_expiration
        ]
        
        for scenario_func in scenarios:
            try:
                result = scenario_func()
                print(f"\n{'='*60}")
                print(f"📋 {result['scenario']}")
                print(f"{'='*60}")
                print(f"Description: {result['description']}")
                print(f"Success: {'✅' if result['success'] else '❌'}")
                
                if result['steps']:
                    print("\nSteps:")
                    for step in result['steps']:
                        print(f"  {step['step']}. {step['action']}")
                        print(f"     → {step['result']}")
                
                if result['issues']:
                    print(f"\nIssues: {', '.join(result['issues'])}")
                    
            except Exception as e:
                logger.error(f"Failed to run scenario {scenario_func.__name__}: {e}")
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate and save test summary."""
        summary = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": len(self.test_results),
                "successful_scenarios": len([r for r in self.test_results if r['success']]),
                "failed_scenarios": len([r for r in self.test_results if not r['success']])
            },
            "scenarios": self.test_results
        }
        
        # Save to file
        summary_file = self.project_root / "authority_delegation_test_results.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Scenarios: {summary['test_run']['total_scenarios']}")
        print(f"Successful: {summary['test_run']['successful_scenarios']} ✅")
        print(f"Failed: {summary['test_run']['failed_scenarios']} ❌")
        print(f"Success Rate: {(summary['test_run']['successful_scenarios'] / summary['test_run']['total_scenarios'] * 100):.1f}%")
        print(f"\nDetailed results saved to: {summary_file}")


def main():
    """Run authority delegation tests."""
    tester = AuthorityDelegationTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    main()