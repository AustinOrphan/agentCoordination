"""
Real System Integration Adapter

This module provides adapters to connect the test suite with the actual
multi-agent coordination system, replacing mock objects with real system calls.
"""

import json
import os
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .base_adapter import BaseCoordinationAdapter, AdapterConfig


@dataclass
class RealSystemConfig(AdapterConfig):
    """Configuration for real system integration."""
    coordination_root: str
    agent_status_dir: str = "agent_status"
    authority_pool_file: str = "authority_pool.json"
    communication_dir: str = "agent_communication"
    backup_original_files: bool = True
    cleanup_on_exit: bool = True
    use_existing_agents: bool = True
    agent_startup_timeout: int = 30


class RealSystemAdapter(BaseCoordinationAdapter):
    """Adapter for integrating with the real coordination system."""
    
    def __init__(self, config: RealSystemConfig):
        super().__init__(config)
        self.config = config
        self.coordination_root = Path(config.coordination_root)
        self.agent_status_dir = self.coordination_root / config.agent_status_dir
        self.authority_pool_file = self.coordination_root / config.authority_pool_file
        self.communication_dir = self.coordination_root / config.communication_dir
        
        # Backup and cleanup management
        self.backup_dir: Optional[Path] = None
        self.original_files: List[Path] = []
        self.created_files: List[Path] = []
        
        self.logger = logging.getLogger(__name__)
        
        # Validate system paths
        self._validate_system_paths()
        
    def _validate_system_paths(self):
        """Validate that required system paths exist."""
        required_paths = [
            self.coordination_root,
            self.agent_status_dir,
            self.authority_pool_file,
            self.communication_dir
        ]
        
        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(f"Required coordination system path not found: {path}")
                
    def setup_test_environment(self) -> bool:
        """Setup test environment with real system."""
        try:
            # Create backup of original system state
            if self.config.backup_original_files:
                self._create_system_backup()
            
            # Discover existing agents
            self.active_agents = self._discover_active_agents()
            self.logger.info(f"Discovered {len(self.active_agents)} active agents: {list(self.active_agents.keys())}")
            
            # Load current authority state
            self._load_authority_state()
            
            # Setup communication monitoring
            self._setup_communication_monitoring()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup test environment: {e}")
            return False
            
    def _create_system_backup(self):
        """Create backup of original system files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.coordination_root / f"test_backup_{timestamp}"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup critical files
        files_to_backup = [
            self.authority_pool_file,
        ]
        
        # Backup agent status files
        if self.agent_status_dir.exists():
            for status_file in self.agent_status_dir.glob("*.json"):
                files_to_backup.append(status_file)
                
        for file_path in files_to_backup:
            if file_path.exists():
                backup_path = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                self.original_files.append(file_path)
                
        self.logger.info(f"Created system backup at {self.backup_dir}")
        
    def _discover_active_agents(self) -> Dict[str, Dict[str, Any]]:
        """Discover currently active agents from status files."""
        agents = {}
        
        if not self.agent_status_dir.exists():
            return agents
            
        for status_file in self.agent_status_dir.glob("*_status.json"):
            try:
                with open(status_file, 'r') as f:
                    agent_data = json.load(f)
                    
                agent_name = status_file.stem.replace("_status", "")
                agents[agent_name] = {
                    "status_file": status_file,
                    "data": agent_data,
                    "last_seen": status_file.stat().st_mtime
                }
                
            except Exception as e:
                self.logger.warning(f"Failed to read agent status file {status_file}: {e}")
                
        return agents
        
    def _load_authority_state(self):
        """Load current authority pool state."""
        try:
            with open(self.authority_pool_file, 'r') as f:
                self.authority_state = json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load authority state: {e}")
            self.authority_state = {"assignments": [], "requests": [], "available": []}
            
    def _setup_communication_monitoring(self):
        """Setup monitoring for agent communication."""
        self.communication_state = {}
        
        if not self.communication_dir.exists():
            return
            
        for agent_name in self.active_agents:
            agent_comm_dir = self.communication_dir / agent_name
            if agent_comm_dir.exists():
                self.communication_state[agent_name] = {
                    "inbox_file": agent_comm_dir / "input" / "inbox.json",
                    "outbox_file": agent_comm_dir / "output" / "outbox.json",
                    "status_file": agent_comm_dir / "status" / "lifecycle.json"
                }
                
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get real-time status of an agent."""
        if agent_name not in self.active_agents:
            return None
            
        try:
            status_file = self.active_agents[agent_name]["status_file"]
            with open(status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to get status for agent {agent_name}: {e}")
            return None
            
    def update_agent_status(self, agent_name: str, status_data: Dict[str, Any]) -> bool:
        """Update agent status in real system."""
        if agent_name not in self.active_agents:
            self.logger.warning(f"Agent {agent_name} not found in active agents")
            return False
            
        try:
            status_file = self.active_agents[agent_name]["status_file"]
            
            # Read current status
            with open(status_file, 'r') as f:
                current_status = json.load(f)
                
            # Update with new data
            current_status.update(status_data)
            current_status["last_update"] = datetime.now().isoformat()
            
            # Write back to file
            with open(status_file, 'w') as f:
                json.dump(current_status, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update status for agent {agent_name}: {e}")
            return False
            
    def request_authority(self, agent_name: str, authority_type: str, domain: str, task: str) -> bool:
        """Request authority for an agent through real system."""
        try:
            # Use the coordination system's authority manager
            cmd = [
                "python3", 
                str(self.coordination_root / "coordination_system" / "dynamic_authority_manager.py"),
                "request",
                "--agent", agent_name,
                "--type", authority_type,
                "--domain", domain,
                "--task", task
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self._load_authority_state()  # Reload authority state
                return True
            else:
                self.logger.error(f"Authority request failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to request authority: {e}")
            return False
            
    def release_authority(self, agent_name: str, authority_id: str) -> bool:
        """Release authority through real system."""
        try:
            cmd = [
                "python3",
                str(self.coordination_root / "coordination_system" / "dynamic_authority_manager.py"),
                "release",
                "--agent", agent_name,
                "--authority-id", authority_id
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self._load_authority_state()
                return True
            else:
                self.logger.error(f"Authority release failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to release authority: {e}")
            return False
            
    def send_message(self, sender: str, recipient: str, message_type: str, content: Dict[str, Any]) -> bool:
        """Send message through real agent communication system."""
        if recipient not in self.communication_state:
            self.logger.warning(f"No communication setup for recipient {recipient}")
            return False
            
        try:
            inbox_file = self.communication_state[recipient]["inbox_file"]
            
            # Read current inbox
            if inbox_file.exists():
                with open(inbox_file, 'r') as f:
                    inbox_data = json.load(f)
            else:
                inbox_data = {"messages": []}
                
            # Add new message
            message = {
                "id": f"msg_{int(time.time() * 1000)}",
                "sender": sender,
                "recipient": recipient,
                "type": message_type,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "processed": False
            }
            
            inbox_data["messages"].append(message)
            
            # Write back to inbox
            inbox_file.parent.mkdir(parents=True, exist_ok=True)
            with open(inbox_file, 'w') as f:
                json.dump(inbox_data, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message from {sender} to {recipient}: {e}")
            return False
            
    def get_messages(self, agent_name: str, mark_as_read: bool = True) -> List[Dict[str, Any]]:
        """Get messages for an agent from real communication system."""
        if agent_name not in self.communication_state:
            return []
            
        try:
            outbox_file = self.communication_state[agent_name]["outbox_file"]
            
            if not outbox_file.exists():
                return []
                
            with open(outbox_file, 'r') as f:
                outbox_data = json.load(f)
                
            messages = outbox_data.get("messages", [])
            
            if mark_as_read:
                # Mark messages as processed
                for msg in messages:
                    msg["processed"] = True
                    
                with open(outbox_file, 'w') as f:
                    json.dump(outbox_data, f, indent=2)
                    
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to get messages for agent {agent_name}: {e}")
            return []
            
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get real system performance metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(self.active_agents),
            "total_authorities": len(self.authority_state.get("assignments", [])),
            "pending_requests": len(self.authority_state.get("requests", [])),
            "system_load": self._calculate_system_load()
        }
        
        # Add per-agent metrics
        agent_metrics = {}
        for agent_name, agent_info in self.active_agents.items():
            agent_status = self.get_agent_status(agent_name)
            if agent_status:
                agent_metrics[agent_name] = {
                    "status": agent_status.get("status", "unknown"),
                    "workload": agent_status.get("workload", 0),
                    "last_update": agent_status.get("last_update", "never")
                }
                
        metrics["agents"] = agent_metrics
        return metrics
        
    def _calculate_system_load(self) -> float:
        """Calculate overall system load based on agent activity."""
        if not self.active_agents:
            return 0.0
            
        total_workload = 0
        active_count = 0
        
        for agent_name in self.active_agents:
            agent_status = self.get_agent_status(agent_name)
            if agent_status and agent_status.get("status") == "active":
                total_workload += agent_status.get("workload", 0)
                active_count += 1
                
        if active_count == 0:
            return 0.0
            
        return total_workload / active_count
        
    def start_agent(self, agent_name: str) -> bool:
        """Start an agent using real system scripts."""
        try:
            script_path = self.coordination_root / f"start_agent_{agent_name}.sh"
            
            if not script_path.exists():
                self.logger.error(f"Start script not found for agent {agent_name}: {script_path}")
                return False
                
            # Make script executable
            script_path.chmod(0o755)
            
            # Start agent in background
            result = subprocess.run(
                ["bash", str(script_path)],
                cwd=self.coordination_root,
                capture_output=True,
                text=True,
                timeout=self.config.agent_startup_timeout
            )
            
            if result.returncode == 0:
                # Wait a moment for agent to initialize
                time.sleep(2)
                
                # Verify agent started
                agent_status = self.get_agent_status(agent_name)
                if agent_status:
                    self.logger.info(f"Successfully started agent {agent_name}")
                    return True
                else:
                    self.logger.warning(f"Agent {agent_name} started but status not available")
                    return False
            else:
                self.logger.error(f"Failed to start agent {agent_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception starting agent {agent_name}: {e}")
            return False
            
    def stop_agent(self, agent_name: str) -> bool:
        """Stop an agent gracefully."""
        try:
            # Send stop signal through agent communication
            stop_message = {
                "command": "stop",
                "reason": "test_cleanup",
                "timestamp": datetime.now().isoformat()
            }
            
            success = self.send_message("test_system", agent_name, "control", stop_message)
            
            if success:
                # Wait for agent to stop
                for _ in range(10):  # Wait up to 10 seconds
                    agent_status = self.get_agent_status(agent_name)
                    if not agent_status or agent_status.get("status") == "stopped":
                        self.logger.info(f"Agent {agent_name} stopped successfully")
                        return True
                    time.sleep(1)
                    
                self.logger.warning(f"Agent {agent_name} did not stop gracefully")
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to stop agent {agent_name}: {e}")
            return False
            
    def cleanup_test_environment(self):
        """Clean up test environment and restore original state."""
        try:
            # Stop any agents we started
            if self.config.cleanup_on_exit:
                for agent_name in self.active_agents:
                    if self.active_agents[agent_name].get("started_by_test", False):
                        self.stop_agent(agent_name)
                        
            # Remove any files we created
            for file_path in self.created_files:
                try:
                    if file_path.exists():
                        file_path.unlink()
                except Exception as e:
                    self.logger.warning(f"Failed to remove created file {file_path}: {e}")
                    
            # Restore original files from backup
            if self.backup_dir and self.backup_dir.exists():
                for original_file in self.original_files:
                    backup_file = self.backup_dir / original_file.name
                    if backup_file.exists():
                        shutil.copy2(backup_file, original_file)
                        
                # Remove backup directory
                shutil.rmtree(self.backup_dir)
                self.logger.info("Restored original system state from backup")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    def is_system_healthy(self) -> bool:
        """Check if the coordination system is healthy."""
        try:
            # Check if critical files exist and are readable
            if not self.authority_pool_file.exists():
                return False
                
            # Check if at least one agent is responsive
            responsive_agents = 0
            for agent_name in self.active_agents:
                agent_status = self.get_agent_status(agent_name)
                if agent_status and agent_status.get("status") in ["active", "idle"]:
                    responsive_agents += 1
                    
            return responsive_agents > 0
            
        except Exception:
            return False