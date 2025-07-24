#!/usr/bin/env python3
"""
Task Communicator
Integrates Task Assignment Manager with the existing agent communication system.
Sends task assignments as messages to agents.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path

from task_assignment_manager import TaskAssignmentManager, TaskStatus, TaskType, TaskPriority
from agent_communication import CommunicationChannel, Message, MessageType, Priority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskCommunicator:
    """Bridges task assignment with agent communication"""
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.task_manager = TaskAssignmentManager(config_file)
        self.communication_dir = Path("agent_communication")
        self.processed_assignments = set()  # Track which assignments we've sent
        
    def process_assignments(self) -> int:
        """Process pending task assignments and send them to agents"""
        assignments = self.task_manager.assign_next_tasks()
        sent_count = 0
        
        for assignment in assignments:
            if self._send_task_assignment(assignment):
                sent_count += 1
                
        return sent_count
    
    def _send_task_assignment(self, assignment: Dict) -> bool:
        """Send task assignment message to agent"""
        try:
            agent_id = assignment['agent_id']
            task_id = assignment['task_id']
            
            # Get full task details
            task = self.task_manager.tasks[task_id]
            
            # Create communication channel
            channel = CommunicationChannel(agent_id, str(self.communication_dir))
            
            # Create task assignment message
            task_message = Message(
                from_id="task_manager",
                to_id=agent_id,
                msg_type=MessageType.TASK_ASSIGNMENT,
                priority=self._map_task_priority(task.priority),
                payload={
                    "task_id": task_id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "priority": task.priority.value,
                    "estimated_hours": task.estimated_hours,
                    "tags": task.tags,
                    "deadline": task.deadline,
                    "dependencies": task.dependencies,
                    "assigned_at": assignment['assigned_at'],
                    "assignment_score": assignment['assignment_score'],
                    "instructions": self._generate_task_instructions(task)
                },
                requires_ack=True
            )
            
            # Send message
            channel.send_message(task_message)
            
            logger.info(f"Sent task assignment {task_id} to {agent_id}: {task.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending task assignment: {e}")
            return False
    
    def _map_task_priority(self, task_priority: TaskPriority) -> Priority:
        """Map task priority to message priority"""
        mapping = {
            TaskPriority.CRITICAL: Priority.HIGH,
            TaskPriority.HIGH: Priority.HIGH,
            TaskPriority.NORMAL: Priority.NORMAL,
            TaskPriority.LOW: Priority.LOW
        }
        return mapping.get(task_priority, Priority.NORMAL)
    
    def _generate_task_instructions(self, task) -> str:
        """Generate detailed instructions for the task"""
        instructions = f"""
📋 **Task Assignment: {task.title}**

**Description:**
{task.description}

**Task Type:** {task.task_type.value.title()}
**Priority:** {task.priority.value.title()}
**Estimated Time:** {task.estimated_hours} hours

**Your Role:** You have been selected for this task based on your role and expertise.

**Next Steps:**
1. Acknowledge this task assignment
2. Update your status to show you're working on this task
3. Break down the task into smaller steps if needed
4. Begin implementation
5. Send progress updates regularly
6. Report any blockers immediately

**Status Updates:**
Please send status updates using this format:
```python
from coordination_system.agent_communication import CommunicationChannel, Message, MessageType

channel = CommunicationChannel("{task.assigned_agent}")
status_msg = Message(
    from_id="{task.assigned_agent}",
    to_id="task_manager", 
    msg_type=MessageType.STATUS_UPDATE,
    payload={{
        "task_id": "{task.task_id}",
        "status": "in_progress",  # or "completed", "blocked"
        "progress": 25,  # 0-100
        "message": "Description of current progress",
        "estimated_completion": "2025-01-01T12:00:00Z"  # ISO format
    }}
)
channel.send_message(status_msg)
```

**Report Blockers:**
If you encounter any blockers, report them immediately:
```python
blocker_msg = Message(
    from_id="{task.assigned_agent}",
    to_id="task_manager",
    msg_type=MessageType.BLOCKER_REPORT,
    payload={{
        "task_id": "{task.task_id}",
        "blocker_description": "Description of what's blocking you",
        "severity": "high",  # or "medium", "low"
        "needs_help_from": "other_agent_id"  # if specific help needed
    }}
)
channel.send_message(blocker_msg)
```

Good luck with your task! 🚀
"""
        return instructions.strip()
    
    def check_agent_responses(self) -> int:
        """Check for status updates from agents and update task manager"""
        updates_processed = 0
        
        # Check each agent's outbox for task-related messages
        for agent_id in self.task_manager.agents.keys():
            outbox_file = self.communication_dir / agent_id / "output" / "outbox.json"
            
            if outbox_file.exists():
                try:
                    with open(outbox_file, 'r') as f:
                        outbox_data = json.load(f)
                    
                    messages = outbox_data.get('messages', [])
                    
                    for message in messages:
                        if self._process_agent_message(message):
                            updates_processed += 1
                            
                except Exception as e:
                    logger.error(f"Error reading outbox for {agent_id}: {e}")
        
        return updates_processed
    
    def _process_agent_message(self, message: Dict) -> bool:
        """Process a message from an agent"""
        try:
            msg_type = message.get('type')
            payload = message.get('payload', {})
            
            if msg_type == MessageType.STATUS_UPDATE.value:
                return self._handle_status_update(payload)
            elif msg_type == MessageType.BLOCKER_REPORT.value:
                return self._handle_blocker_report(payload)
            elif msg_type == MessageType.ACKNOWLEDGMENT.value:
                return self._handle_task_acknowledgment(payload)
                
        except Exception as e:
            logger.error(f"Error processing agent message: {e}")
            
        return False
    
    def _handle_status_update(self, payload: Dict) -> bool:
        """Handle task status update from agent"""
        task_id = payload.get('task_id')
        if not task_id or task_id not in self.task_manager.tasks:
            return False
        
        status_str = payload.get('status', 'in_progress')
        progress = payload.get('progress', 0)
        
        # Map status string to TaskStatus enum
        status_mapping = {
            'assigned': TaskStatus.ASSIGNED,
            'in_progress': TaskStatus.IN_PROGRESS,
            'completed': TaskStatus.COMPLETED,
            'blocked': TaskStatus.BLOCKED,
            'failed': TaskStatus.FAILED
        }
        
        status = status_mapping.get(status_str, TaskStatus.IN_PROGRESS)
        
        # Update task in manager
        success = self.task_manager.update_task_status(task_id, status, progress)
        
        if success:
            logger.info(f"Updated task {task_id} status to {status.value} ({progress}%)")
            
            # Also update agent status file for compatibility
            self._update_agent_status_file(payload, task_id)
        
        return success
    
    def _handle_blocker_report(self, payload: Dict) -> bool:
        """Handle blocker report from agent"""
        task_id = payload.get('task_id')
        if not task_id or task_id not in self.task_manager.tasks:
            return False
        
        blocker_description = payload.get('blocker_description', 'Unknown blocker')
        
        # Update task status to blocked
        success = self.task_manager.update_task_status(
            task_id, 
            TaskStatus.BLOCKED, 
            blocker_reason=blocker_description
        )
        
        if success:
            logger.warning(f"Task {task_id} blocked: {blocker_description}")
        
        return success
    
    def _handle_task_acknowledgment(self, payload: Dict) -> bool:
        """Handle task acknowledgment from agent"""
        task_id = payload.get('task_id')
        if not task_id or task_id not in self.task_manager.tasks:
            return False
        
        logger.info(f"Agent acknowledged task {task_id}")
        return True
    
    def _update_agent_status_file(self, payload: Dict, task_id: str):
        """Update agent status file for legacy compatibility"""
        try:
            task = self.task_manager.tasks[task_id]
            agent_id = task.assigned_agent
            
            if not agent_id:
                return
            
            status_file = Path(f"agent_status/{agent_id}_status.json")
            
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                
                # Update current status
                status['current_status']['task'] = task.title
                status['current_status']['progress'] = payload.get('progress', 0)
                status['current_status']['last_update'] = datetime.now(timezone.utc).isoformat()
                
                # Update status emoji based on progress
                progress = payload.get('progress', 0)
                if progress >= 100:
                    status['current_status']['status'] = '🟢'
                    status['current_status']['status_text'] = 'Completed'
                elif progress > 0:
                    status['current_status']['status'] = '🟡'
                    status['current_status']['status_text'] = 'Working'
                else:
                    status['current_status']['status'] = '🔵'
                    status['current_status']['status_text'] = 'Starting'
                
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Error updating agent status file: {e}")
    
    def create_sample_tasks(self) -> int:
        """Create sample tasks for testing"""
        tasks = [
            ("Implement user authentication", "Create secure login/logout functionality with JWT tokens", 
             TaskType.DEVELOPMENT, TaskPriority.HIGH, 4.0, ["backend", "security"]),
            
            ("Design user dashboard", "Create intuitive dashboard mockups and prototypes", 
             TaskType.DESIGN, TaskPriority.NORMAL, 3.0, ["frontend", "ui"]),
            
            ("Setup CI/CD pipeline", "Configure automated testing and deployment pipeline", 
             TaskType.DEPLOYMENT, TaskPriority.HIGH, 6.0, ["devops", "automation"]),
            
            ("Security vulnerability audit", "Comprehensive security review of codebase", 
             TaskType.SECURITY, TaskPriority.CRITICAL, 8.0, ["security", "audit"]),
            
            ("API documentation", "Document all REST endpoints with examples", 
             TaskType.DOCUMENTATION, TaskPriority.NORMAL, 2.0, ["documentation", "api"]),
            
            ("Fix session timeout bug", "Resolve issue where user sessions expire too quickly", 
             TaskType.BUGFIX, TaskPriority.HIGH, 1.5, ["backend", "bugfix"]),
            
            ("Performance load testing", "Test system performance under high load", 
             TaskType.TESTING, TaskPriority.NORMAL, 3.0, ["testing", "performance"]),
            
            ("Database migration to PostgreSQL", "Migrate from SQLite to PostgreSQL with zero downtime", 
             TaskType.INTEGRATION, TaskPriority.HIGH, 5.0, ["database", "migration"])
        ]
        
        created_count = 0
        for title, description, task_type, priority, hours, tags in tasks:
            task_id = self.task_manager.create_task(
                title=title,
                description=description, 
                task_type=task_type,
                priority=priority,
                estimated_hours=hours,
                tags=tags
            )
            created_count += 1
            logger.info(f"Created sample task: {task_id}")
        
        return created_count
    
    def get_system_status(self) -> Dict:
        """Get comprehensive status of the task assignment system"""
        queue_status = self.task_manager.get_task_queue_status()
        workloads = self.task_manager.get_agent_workloads()
        
        return {
            'queue_status': queue_status,
            'agent_workloads': workloads,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

def main():
    """CLI interface for task communicator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Assignment Communicator')
    parser.add_argument('--process', action='store_true', help='Process pending assignments')
    parser.add_argument('--check-responses', action='store_true', help='Check agent responses')
    parser.add_argument('--create-samples', action='store_true', help='Create sample tasks')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--auto', action='store_true', help='Run in auto mode (process + check)')
    
    args = parser.parse_args()
    
    communicator = TaskCommunicator()
    
    if args.create_samples:
        count = communicator.create_sample_tasks()
        print(f"Created {count} sample tasks")
    
    if args.process or args.auto:
        count = communicator.process_assignments()
        print(f"Processed {count} task assignments")
    
    if args.check_responses or args.auto:
        count = communicator.check_agent_responses()
        print(f"Processed {count} agent responses")
    
    if args.status:
        status = communicator.get_system_status()
        print("System Status:")
        print(f"  Queue: {status['queue_status']}")
        print(f"  Agents: {len(status['agent_workloads'])} total")

if __name__ == '__main__':
    main()