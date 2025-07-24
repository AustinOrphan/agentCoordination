#!/usr/bin/env python3
"""
Project Manager for Multi-Project Coordination System
Manages multiple concurrent projects with isolated agent workspaces.
"""

import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

# Import new workflow analysis components
try:
    # Try absolute imports with coordination_system prefix
    from coordination_system.project_analyzer import ProjectAnalyzer, AnalysisResult
    from coordination_system.workflow_template_engine import WorkflowTemplateEngine
    from coordination_system.auto_task_generator import AutoTaskGenerator
    from coordination_system.project_template_matcher import ProjectTemplateMatcher, ProjectRequirements
except ImportError:
    try:
        # Try relative imports (when used as module)
        from .project_analyzer import ProjectAnalyzer, AnalysisResult
        from .workflow_template_engine import WorkflowTemplateEngine
        from .auto_task_generator import AutoTaskGenerator
        from .project_template_matcher import ProjectTemplateMatcher, ProjectRequirements
    except ImportError:
        try:
            # Try direct imports (when run from same directory)
            from project_analyzer import ProjectAnalyzer, AnalysisResult
            from workflow_template_engine import WorkflowTemplateEngine
            from auto_task_generator import AutoTaskGenerator
            from project_template_matcher import ProjectTemplateMatcher, ProjectRequirements
        except ImportError as e:
            # Fallback for when modules aren't available
            print(f"Warning: Failed to import workflow analysis components: {e}")
            ProjectAnalyzer = None
            WorkflowTemplateEngine = None
            AutoTaskGenerator = None
            ProjectTemplateMatcher = None
            ProjectRequirements = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    """Project lifecycle states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    INITIALIZING = "initializing"

class Project:
    """Represents a single project workspace"""
    
    def __init__(self, project_id: str, name: str, codebase_path: str, 
                 description: str = "", agent_count: int = 6):
        self.project_id = project_id
        self.name = name
        self.codebase_path = Path(codebase_path).resolve()
        self.description = description
        self.agent_count = agent_count
        self.status = ProjectStatus.INITIALIZING
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_active = self.created_at
        self.metadata = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'codebase_path': str(self.codebase_path),
            'description': self.description,
            'agent_count': self.agent_count,
            'status': self.status.value,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create project from dictionary"""
        project = cls(
            project_id=data['project_id'],
            name=data['name'],
            codebase_path=data['codebase_path'],
            description=data.get('description', ''),
            agent_count=data.get('agent_count', 6)
        )
        project.status = ProjectStatus(data.get('status', 'initializing'))
        project.created_at = data.get('created_at', project.created_at)
        project.last_active = data.get('last_active', project.last_active)
        project.metadata = data.get('metadata', {})
        return project

class ProjectManager:
    """Manages multiple project workspaces for agent coordination"""
    
    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Default to current directory
            self.base_dir = Path.cwd()
        
        self.projects_dir = self.base_dir / "projects"
        self.templates_dir = self.base_dir / "templates"
        self.global_config_file = self.base_dir / "global_config.json"
        
        # Ensure directories exist
        self.projects_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Load or initialize global configuration
        self.global_config = self._load_global_config()
        self.projects: Dict[str, Project] = self._load_projects()
        
        # Initialize workflow analysis components
        self.analyzer = ProjectAnalyzer() if ProjectAnalyzer else None
        self.workflow_engine = WorkflowTemplateEngine() if WorkflowTemplateEngine else None
        self.task_generator = AutoTaskGenerator() if AutoTaskGenerator else None
        self.template_matcher = ProjectTemplateMatcher() if ProjectTemplateMatcher else None
        
    def _load_global_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        if self.global_config_file.exists():
            try:
                with open(self.global_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading global config: {e}")
        
        # Default configuration
        return {
            'version': '1.0',
            'max_concurrent_projects': 10,
            'default_agent_count': 6,
            'agent_themes': ['ocean_creatures', 'greek_letters', 'marvel'],
            'current_theme': 'ocean_creatures',
            'active_project': None,
            'project_isolation': True,
            'shared_agent_pool': False
        }
    
    def _save_global_config(self):
        """Save global configuration"""
        try:
            with open(self.global_config_file, 'w') as f:
                json.dump(self.global_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving global config: {e}")
    
    def _load_projects(self) -> Dict[str, Project]:
        """Load all projects from disk"""
        projects = {}
        
        if not self.projects_dir.exists():
            return projects
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                config_file = project_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            project_data = json.load(f)
                        project = Project.from_dict(project_data)
                        projects[project.project_id] = project
                    except Exception as e:
                        logger.error(f"Error loading project {project_dir.name}: {e}")
        
        return projects
    
    def create_project(self, name: str, codebase_path: str, 
                      description: str = "", agent_count: int = 6,
                      theme: Optional[str] = None) -> Project:
        """Create a new project workspace"""
        # Generate unique project ID
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        
        # Validate codebase path
        codebase_path = Path(codebase_path).resolve()
        if not codebase_path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")
        
        # Create project instance
        project = Project(project_id, name, str(codebase_path), description, agent_count)
        
        # Create project workspace
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # Create project subdirectories
        (project_dir / "agent_status").mkdir(exist_ok=True)
        (project_dir / "agent_communication").mkdir(exist_ok=True)
        (project_dir / "task_assignments").mkdir(exist_ok=True)
        (project_dir / "agent_prompts").mkdir(exist_ok=True)
        (project_dir / "worktrees").mkdir(exist_ok=True)
        (project_dir / "logs").mkdir(exist_ok=True)
        
        # Save project configuration
        config_data = project.to_dict()
        config_data['theme'] = theme or self.global_config.get('current_theme', 'ocean_creatures')
        config_data['workspace_path'] = str(project_dir)
        
        with open(project_dir / "config.json", 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Initialize project-specific files
        self._initialize_project_files(project, project_dir)
        
        # Update project status
        project.status = ProjectStatus.ACTIVE
        
        # Save to projects dict
        self.projects[project_id] = project
        
        # Update global config
        if not self.global_config.get('active_project'):
            self.global_config['active_project'] = project_id
        self._save_global_config()
        
        logger.info(f"Created project: {name} (ID: {project_id})")
        return project
    
    def _initialize_project_files(self, project: Project, project_dir: Path):
        """Initialize project-specific files"""
        # Create AGENT_COORDINATION.md for this project
        coordination_md = project_dir / "AGENT_COORDINATION.md"
        with open(coordination_md, 'w') as f:
            f.write(f"# Agent Coordination Status - {project.name}\n\n")
            f.write(f"**Project ID**: {project.project_id}\n")
            f.write(f"**Codebase**: {project.codebase_path}\n")
            f.write(f"**Created**: {project.created_at}\n")
            f.write(f"**Status**: {project.status.value}\n\n")
            f.write("## Agent Status\n\n")
            f.write("*Agents will be initialized when project starts*\n")
        
        # Create task queue for this project
        task_queue = project_dir / "task_assignments" / "task_queue.json"
        with open(task_queue, 'w') as f:
            json.dump({
                'project_id': project.project_id,
                'tasks': [],
                'queue': [],
                'last_updated': datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        # Create project activity log
        activity_log = project_dir / "logs" / "activity.log"
        with open(activity_log, 'w') as f:
            f.write(f"Project {project.name} created at {project.created_at}\n")
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """Get project by name"""
        for project in self.projects.values():
            if project.name.lower() == name.lower():
                return project
        return None
    
    def list_projects(self, status: Optional[ProjectStatus] = None) -> List[Project]:
        """List all projects, optionally filtered by status"""
        projects = list(self.projects.values())
        
        if status:
            projects = [p for p in projects if p.status == status]
        
        # Sort by last active time
        projects.sort(key=lambda p: p.last_active, reverse=True)
        return projects
    
    def set_active_project(self, project_id: str) -> bool:
        """Set the currently active project"""
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return False
        
        self.global_config['active_project'] = project_id
        self._save_global_config()
        
        # Update last active time
        project = self.projects[project_id]
        project.last_active = datetime.now(timezone.utc).isoformat()
        self._save_project(project)
        
        logger.info(f"Set active project: {project.name} ({project_id})")
        return True
    
    def get_active_project(self) -> Optional[Project]:
        """Get the currently active project"""
        active_id = self.global_config.get('active_project')
        if active_id:
            return self.projects.get(active_id)
        return None
    
    def pause_project(self, project_id: str) -> bool:
        """Pause a project"""
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        if project.status != ProjectStatus.ACTIVE:
            logger.warning(f"Project {project.name} is not active")
            return False
        
        project.status = ProjectStatus.PAUSED
        self._save_project(project)
        
        logger.info(f"Paused project: {project.name}")
        return True
    
    def resume_project(self, project_id: str) -> bool:
        """Resume a paused project"""
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        if project.status != ProjectStatus.PAUSED:
            logger.warning(f"Project {project.name} is not paused")
            return False
        
        project.status = ProjectStatus.ACTIVE
        project.last_active = datetime.now(timezone.utc).isoformat()
        self._save_project(project)
        
        logger.info(f"Resumed project: {project.name}")
        return True
    
    def archive_project(self, project_id: str) -> bool:
        """Archive a project (keeps data but marks as inactive)"""
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        project.status = ProjectStatus.ARCHIVED
        self._save_project(project)
        
        # If this was the active project, clear it
        if self.global_config.get('active_project') == project_id:
            self.global_config['active_project'] = None
            self._save_global_config()
        
        logger.info(f"Archived project: {project.name}")
        return True
    
    def delete_project(self, project_id: str, confirm: bool = False) -> bool:
        """Delete a project and all its data"""
        if not confirm:
            logger.error("Delete operation requires confirmation")
            return False
        
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        # Remove project directory
        project_dir = self.projects_dir / project_id
        if project_dir.exists():
            shutil.rmtree(project_dir)
        
        # Remove from projects dict
        del self.projects[project_id]
        
        # Update global config if needed
        if self.global_config.get('active_project') == project_id:
            self.global_config['active_project'] = None
            self._save_global_config()
        
        logger.info(f"Deleted project: {project.name}")
        return True
    
    def reset_project(self, project_id: str, is_test: bool = False, 
                     skip_challenge: bool = False) -> bool:
        """Reset a project to initial state, clearing all data while preserving structure.
        
        This method clears all project data including agent status, communication channels,
        task assignments, prompts, worktrees, and logs. The project configuration and
        directory structure are preserved. Reset metadata is tracked in the project config.
        
        Args:
            project_id (str): The unique identifier of the project to reset
            is_test (bool, optional): If True, skip all confirmations and reset immediately.
                Used for test projects that need frequent resets. Defaults to False.
            skip_challenge (bool, optional): If True, skip the interactive challenge.
                Used by the CLI when challenge validation is done externally. Defaults to False.
            
        Returns:
            bool: True if reset was successful, False if project not found or reset failed
            
        Example:
            >>> manager = ProjectManager()
            >>> # Reset a test project instantly
            >>> success = manager.reset_project("proj_test_123", is_test=True)
            >>> # Reset a production project (requires challenge in interactive mode)
            >>> success = manager.reset_project("proj_prod_456", is_test=False)
        
        Note:
            Production projects (is_test=False) require user confirmation through
            a challenge-response system when skip_challenge=False.
        """
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        # For non-test projects, require confirmation
        if not is_test and not skip_challenge:
            logger.warning(f"Reset will clear all data for project: {project.name}")
            # Challenge will be handled by CLI
        
        workspace = self.projects_dir / project_id
        
        # Clear all subdirectories but keep the project
        subdirs_to_clear = [
            'agent_status',
            'agent_communication', 
            'task_assignments',
            'agent_prompts',
            'worktrees',
            'logs'
        ]
        
        for subdir_name in subdirs_to_clear:
            subdir = workspace / subdir_name
            if subdir.exists():
                import shutil
                shutil.rmtree(subdir)
                logger.info(f"Cleared {subdir_name} for project {project.name}")
        
        # Recreate directory structure
        (workspace / "agent_status").mkdir(exist_ok=True)
        (workspace / "agent_communication").mkdir(exist_ok=True)
        (workspace / "task_assignments").mkdir(exist_ok=True)
        (workspace / "agent_prompts").mkdir(exist_ok=True)
        (workspace / "worktrees").mkdir(exist_ok=True)
        (workspace / "logs").mkdir(exist_ok=True)
        
        # Reset project state
        project.status = ProjectStatus.INITIALIZING
        project.last_active = datetime.now(timezone.utc).isoformat()
        project.metadata['reset_at'] = datetime.now(timezone.utc).isoformat()
        project.metadata['reset_count'] = project.metadata.get('reset_count', 0) + 1
        
        # Save updated project config
        self._save_project(project)
        
        # Recreate initial task queue
        task_queue = workspace / "task_assignments" / "task_queue.json"
        with open(task_queue, 'w') as f:
            json.dump({
                'project_id': project.project_id,
                'tasks': [],
                'queue': [],
                'last_updated': datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        logger.info(f"Reset project: {project.name} (test_mode={is_test})")
        return True
    
    def reset_all_test_projects(self) -> int:
        """Reset all projects marked as test projects in bulk.
        
        This method finds all projects with is_test=True in their metadata and resets
        them without requiring any confirmation. Useful for cleaning up after test suites
        or resetting multiple development environments at once.
        
        Returns:
            int: The number of projects successfully reset
            
        Example:
            >>> manager = ProjectManager()
            >>> count = manager.reset_all_test_projects()
            >>> print(f"Reset {count} test projects")
            Reset 3 test projects
            
        Note:
            Only projects explicitly marked with is_test=True are reset.
            Projects with "test" in their name but not marked are skipped.
        """
        reset_count = 0
        test_projects = []
        
        # Find all test projects
        for project_id, project in self.projects.items():
            # Check if project is a test project by name pattern or metadata
            is_test = (
                project.name.lower().startswith('test') or
                project.metadata.get('is_test', False) or
                'test' in project.name.lower()
            )
            
            if is_test:
                test_projects.append(project_id)
        
        # Reset each test project
        for project_id in test_projects:
            if self.reset_project(project_id, is_test=True):
                reset_count += 1
        
        logger.info(f"Reset {reset_count} test projects")
        return reset_count
    
    def mark_as_test_project(self, project_id: str, is_test: bool = True, skip_challenge: bool = False) -> bool:
        """Mark or unmark a project as a test project for easy reset.
        
        Test projects can be reset without confirmation, making them ideal for
        development, testing, and CI/CD environments. This setting is stored
        in the project's metadata and persists across sessions.
        
        SECURITY: Marking a production project as test requires challenge confirmation
        since it enables unrestricted resets.
        
        Args:
            project_id (str): The unique identifier of the project to mark
            is_test (bool, optional): True to mark as test project, False to mark
                as production project. Defaults to True.
            skip_challenge (bool, optional): If True, skip the interactive challenge.
                Used by CLI when challenge validation is done externally. Defaults to False.
            
        Returns:
            bool: True if successfully updated, False if project not found or challenge failed
            
        Example:
            >>> manager = ProjectManager()
            >>> # Mark as test project (requires challenge if production)
            >>> manager.mark_as_test_project("proj_123", is_test=True)
            >>> # Now can reset without confirmation
            >>> manager.reset_project("proj_123", is_test=True)
            >>> 
            >>> # Mark as production (remove test flag - no challenge needed)
            >>> manager.mark_as_test_project("proj_123", is_test=False)
            
        Note:
            Projects with "test" in their name are treated as test projects
            even without this flag, but explicit marking takes precedence.
        """
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        # Check if project is currently a test project
        current_is_test = (
            project.name.lower().startswith('test') or
            project.metadata.get('is_test', False) or
            'test' in project.name.lower()
        )
        
        # If marking production project as test, require challenge
        if is_test and not current_is_test and not skip_challenge:
            logger.info(f"Production project requires challenge to mark as test: {project.name}")
            
            # Generate and present challenge
            challenge = self.generate_reset_challenge(project_id)
            if not challenge:
                logger.error("Failed to generate challenge")
                return False
            
            challenge_text, expected_response = challenge
            print(f"\n⚠️  SECURITY WARNING: Marking as Test Project ⚠️")
            print(f"Project '{project.name}' will allow unrestricted resets once marked as test.")
            print(f"This is a significant security change for production projects.\n")
            print(f"Challenge: {challenge_text}")
            
            try:
                user_response = input("Your response: ").strip()
                if user_response != expected_response:
                    print("Challenge failed. Project marking cancelled.")
                    logger.warning(f"Failed challenge for marking test project: {project.name}")
                    return False
                print("Challenge passed. Marking project as test.")
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                return False
        
        # Update the project metadata
        project.metadata['is_test'] = is_test
        self._save_project(project)
        
        action = "test" if is_test else "production"
        logger.info(f"Marked project {project.name} as {action}")
        print(f"✅ Project '{project.name}' marked as {action}")
        return True
    
    def generate_reset_challenge(self, project_id: str) -> Optional[Tuple[str, str]]:
        """Generate a random challenge for resetting a production project.
        
        Creates one of four challenge types to ensure users understand the
        consequences of resetting a production project. Challenges are designed
        to be deliberate actions that can't be completed accidentally.
        
        Challenge Types:
            1. Type project name in UPPERCASE
            2. Type "RESET" + first 3 letters of project name
            3. Type first 8 characters of project ID
            4. Type "DELETE ALL DATA"
        
        Args:
            project_id (str): The unique identifier of the project
            
        Returns:
            Optional[Tuple[str, str]]: A tuple containing (challenge_prompt, expected_response),
                or None if the project is not found
                
        Example:
            >>> manager = ProjectManager()
            >>> challenge = manager.generate_reset_challenge("proj_12345678")
            >>> if challenge:
            ...     prompt, expected = challenge
            ...     print(f"Challenge: {prompt}")
            ...     user_response = input("Your response: ")
            ...     if user_response == expected:
            ...         print("Challenge passed!")
            Challenge: Type the project name in UPPERCASE to confirm reset: My Project
            Your response: MY PROJECT
            Challenge passed!
            
        Note:
            Challenges are case-sensitive and must be typed exactly as expected.
            This method is typically called internally by reset_project() for
            production projects.
        """
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # Generate challenge based on project details
        import random
        challenges = [
            (
                f"Type the project name in UPPERCASE to confirm reset: {project.name}",
                project.name.upper()
            ),
            (
                f"Type 'RESET {project.name[:3].upper()}' to confirm:",
                f"RESET {project.name[:3].upper()}"
            ),
            (
                f"Type the first 8 characters of the project ID ({project_id[:8]}) to confirm:",
                project_id[:8]
            ),
            (
                f"Type 'DELETE ALL DATA' to confirm reset of {project.name}:",
                "DELETE ALL DATA"
            )
        ]
        
        return random.choice(challenges)
    
    def _save_project(self, project: Project):
        """Save project configuration to disk"""
        project_dir = self.projects_dir / project.project_id
        config_file = project_dir / "config.json"
        
        config_data = project.to_dict()
        config_data['workspace_path'] = str(project_dir)
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_project_workspace(self, project_id: str) -> Optional[Path]:
        """Get the workspace directory for a project"""
        if project_id in self.projects:
            return self.projects_dir / project_id
        return None
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a project"""
        project = self.projects.get(project_id)
        if not project:
            return {}
        
        workspace = self.projects_dir / project_id
        
        stats = {
            'project_id': project_id,
            'name': project.name,
            'status': project.status.value,
            'created_at': project.created_at,
            'last_active': project.last_active,
            'agent_count': project.agent_count,
            'workspace_size': 0,
            'task_count': 0,
            'active_agents': 0,
            'completed_tasks': 0
        }
        
        # Calculate workspace size
        if workspace.exists():
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(workspace):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            stats['workspace_size'] = total_size
        
        # Count tasks
        task_file = workspace / "task_assignments" / "task_queue.json"
        if task_file.exists():
            try:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                stats['task_count'] = len(task_data.get('tasks', []))
            except:
                pass
        
        return stats
    
    def export_project_config(self, project_id: str, output_file: str):
        """Export project configuration for backup or sharing"""
        project = self.projects.get(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        export_data = {
            'project': project.to_dict(),
            'export_date': datetime.now(timezone.utc).isoformat(),
            'version': self.global_config.get('version', '1.0')
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported project config to: {output_file}")
        return True
    
    def import_project_config(self, config_file: str, new_codebase_path: Optional[str] = None) -> Optional[Project]:
        """Import a project from exported configuration"""
        try:
            with open(config_file, 'r') as f:
                export_data = json.load(f)
            
            project_data = export_data['project']
            
            # Update codebase path if provided
            if new_codebase_path:
                project_data['codebase_path'] = new_codebase_path
            
            # Create new project with imported data
            project = self.create_project(
                name=project_data['name'] + " (Imported)",
                codebase_path=project_data['codebase_path'],
                description=project_data.get('description', ''),
                agent_count=project_data.get('agent_count', 6)
            )
            
            # Preserve original metadata
            project.metadata = project_data.get('metadata', {})
            project.metadata['imported_from'] = config_file
            project.metadata['import_date'] = datetime.now(timezone.utc).isoformat()
            self._save_project(project)
            
            logger.info(f"Imported project: {project.name}")
            return project
            
        except Exception as e:
            logger.error(f"Error importing project: {e}")
            return None

    def analyze_project_codebase(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Analyze project codebase and return comprehensive analysis"""
        if not self.analyzer:
            logger.warning("Project analyzer not available")
            return None
            
        project = self.get_project(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return None
        
        try:
            analysis = self.analyzer.analyze_project(str(project.codebase_path))
            
            # Generate analysis report
            report = self.analyzer.generate_project_report(analysis, str(project.codebase_path))
            
            # Convert analysis to serializable format
            serializable_analysis = {
                'project_type': analysis.project_type.value,
                'complexity': analysis.estimated_complexity,
                'confidence': analysis.confidence,
                'team_size_recommendation': analysis.team_size_recommendation,
                'patterns': analysis.detected_patterns,
                'suggested_workflow': analysis.suggested_workflow,
                'technologies': {
                    'languages': analysis.tech_stack.languages,
                    'frameworks': analysis.tech_stack.frameworks,
                    'databases': analysis.tech_stack.databases,
                    'cloud_services': analysis.tech_stack.cloud_services,
                    'build_tools': analysis.tech_stack.build_tools,
                    'testing_frameworks': analysis.tech_stack.testing_frameworks,
                    'deployment_tools': analysis.tech_stack.deployment_tools,
                    'package_managers': analysis.tech_stack.package_managers
                },
                'structure': {
                    'has_tests': analysis.structure.has_tests,
                    'has_docs': analysis.structure.has_docs,
                    'has_ci_cd': analysis.structure.has_ci_cd,
                    'has_docker': analysis.structure.has_docker,
                    'has_api': analysis.structure.has_api,
                    'has_frontend': analysis.structure.has_frontend,
                    'has_backend': analysis.structure.has_backend,
                    'has_database': analysis.structure.has_database,
                    'entry_points': analysis.structure.entry_points,
                    'config_files': analysis.structure.config_files
                }
            }
            
            # Store analysis in project metadata
            project.metadata['last_analysis'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis': serializable_analysis,
                'report': report
            }
            self._save_project(project)
            
            return serializable_analysis
        except Exception as e:
            logger.error(f"Error analyzing project {project_id}: {e}")
            return None
    
    def generate_project_workflow(self, project_id: str, requirements: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Generate workflow template for project based on analysis"""
        if not self.template_matcher or not self.analyzer:
            logger.warning("Workflow components not available")
            return None
            
        project = self.get_project(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return None
        
        try:
            # Convert requirements dict to ProjectRequirements object
            project_requirements = None
            if requirements and ProjectRequirements:
                project_requirements = ProjectRequirements(
                    max_timeline_weeks=requirements.get('max_timeline_weeks'),
                    available_team_size=requirements.get('available_team_size'),
                    required_skills=requirements.get('required_skills', []),
                    prohibited_technologies=requirements.get('prohibited_technologies', []),
                    must_have_features=requirements.get('must_have_features', []),
                    preferred_patterns=requirements.get('preferred_patterns', []),
                    constraints=requirements.get('constraints', {})
                )
            
            # Get template recommendations
            recommendations = self.template_matcher.get_template_recommendations(
                str(project.codebase_path), 
                requirements or {}
            )
            
            # Store workflow in project metadata
            project.metadata['generated_workflow'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'recommendations': recommendations,
                'requirements': requirements
            }
            self._save_project(project)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating workflow for project {project_id}: {e}")
            return None
    
    def generate_project_tasks(self, project_id: str, exclude_existing: bool = True) -> Optional[Dict[str, Any]]:
        """Generate tasks automatically for project based on codebase analysis"""
        if not self.task_generator:
            logger.warning("Task generator not available")
            return None
            
        project = self.get_project(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            return None
        
        try:
            tasks, report = self.task_generator.generate_tasks_from_project(
                str(project.codebase_path),
                exclude_existing=exclude_existing
            )
            
            # Convert tasks to serializable format
            tasks_data = [task.__dict__ for task in tasks]
            report_data = report.__dict__
            
            # Store generated tasks in project metadata
            project.metadata['generated_tasks'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'tasks': tasks_data,
                'report': report_data,
                'exclude_existing': exclude_existing
            }
            self._save_project(project)
            
            return {
                'tasks': tasks_data,
                'report': report_data,
                'total_tasks': len(tasks),
                'high_confidence_tasks': report.high_confidence_tasks,
                'categories': report.tasks_by_category
            }
            
        except Exception as e:
            logger.error(f"Error generating tasks for project {project_id}: {e}")
            return None
    
    def create_project_with_analysis(self, name: str, codebase_path: str, 
                                   description: str = "", 
                                   auto_analyze: bool = True,
                                   auto_generate_workflow: bool = True,
                                   auto_generate_tasks: bool = True,
                                   requirements: Optional[Dict[str, Any]] = None,
                                   **kwargs) -> Optional[Project]:
        """Create project with automatic analysis and workflow generation"""
        
        # Create the basic project first
        try:
            project = self.create_project(name, codebase_path, description, **kwargs)
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
        
        if not any([auto_analyze, auto_generate_workflow, auto_generate_tasks]):
            return project
        
        print(f"🔍 Analyzing project codebase...")
        
        # Perform analysis if requested
        analysis_result = None
        if auto_analyze:
            analysis_result = self.analyze_project_codebase(project.project_id)
            if analysis_result:
                print(f"✅ Project analysis completed:")
                print(f"   - Type: {analysis_result['project_type'].replace('_', ' ').title()}")
                print(f"   - Complexity: {analysis_result['complexity'].title()}")
                print(f"   - Languages: {', '.join(analysis_result['technologies']['languages'])}")
                print(f"   - Recommended team size: {analysis_result['team_size_recommendation']}")
            else:
                print("⚠️  Project analysis failed")
        
        # Generate workflow if requested
        if auto_generate_workflow and analysis_result:
            print(f"🔧 Generating workflow template...")
            workflow_result = self.generate_project_workflow(project.project_id, requirements)
            if workflow_result:
                top_match = workflow_result.get('top_recommendation')
                if top_match:
                    print(f"✅ Workflow template generated:")
                    print(f"   - Template: {top_match['template_name']}")
                    print(f"   - Match score: {top_match['match_score']:.2%}")
                    print(f"   - Confidence: {top_match['confidence']:.2%}")
                else:
                    print("⚠️  No suitable workflow template found")
            else:
                print("⚠️  Workflow generation failed")
        
        # Generate tasks if requested
        if auto_generate_tasks:
            print(f"📋 Generating project tasks...")
            tasks_result = self.generate_project_tasks(project.project_id)
            if tasks_result:
                print(f"✅ Task generation completed:")
                print(f"   - Total tasks: {tasks_result['total_tasks']}")
                print(f"   - High confidence tasks: {tasks_result['high_confidence_tasks']}")
                print(f"   - Categories: {', '.join(tasks_result['categories'].keys())}")
            else:
                print("⚠️  Task generation failed")
        
        print(f"🎉 Project '{name}' created successfully with ID: {project.project_id}")
        return project
    
    def get_project_analysis(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get stored project analysis"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.metadata.get('last_analysis')
    
    def get_project_workflow(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get stored project workflow"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.metadata.get('generated_workflow')
    
    def get_project_tasks(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get stored project tasks"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.metadata.get('generated_tasks')

def main():
    """CLI interface for project manager"""
    import argparse
    
    # ANSI color codes for terminal output
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    parser = argparse.ArgumentParser(description='Multi-Project Coordination Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('codebase', help='Path to codebase')
    create_parser.add_argument('-d', '--description', help='Project description')
    create_parser.add_argument('-a', '--agents', type=int, default=6, help='Number of agents')
    create_parser.add_argument('-t', '--theme', help='Agent theme')
    
    # Create smart project with analysis
    create_smart_parser = subparsers.add_parser('create-smart', help='Create project with automatic analysis and workflow generation')
    create_smart_parser.add_argument('name', help='Project name')
    create_smart_parser.add_argument('codebase', help='Path to codebase')
    create_smart_parser.add_argument('-d', '--description', help='Project description')
    create_smart_parser.add_argument('-a', '--agents', type=int, help='Number of agents (auto-detected if not specified)')
    create_smart_parser.add_argument('-t', '--theme', help='Agent theme')
    create_smart_parser.add_argument('--max-weeks', type=int, help='Maximum project timeline in weeks')
    create_smart_parser.add_argument('--team-size', type=int, help='Available team size')
    create_smart_parser.add_argument('--skip-analysis', action='store_true', help='Skip codebase analysis')
    create_smart_parser.add_argument('--skip-workflow', action='store_true', help='Skip workflow generation')
    create_smart_parser.add_argument('--skip-tasks', action='store_true', help='Skip automatic task generation')
    
    # Analyze existing project
    analyze_parser = subparsers.add_parser('analyze', help='Analyze existing project codebase')
    analyze_parser.add_argument('project', help='Project ID or name')
    
    # Generate tasks for existing project
    generate_tasks_parser = subparsers.add_parser('generate-tasks', help='Generate tasks for existing project')
    generate_tasks_parser.add_argument('project', help='Project ID or name')
    
    # List projects
    list_parser = subparsers.add_parser('list', help='List all projects')
    list_parser.add_argument('--status', choices=['active', 'paused', 'completed', 'archived'],
                            help='Filter by status')
    
    # Switch project
    switch_parser = subparsers.add_parser('switch', help='Switch active project')
    switch_parser.add_argument('project', help='Project ID or name')
    
    # Pause/resume/archive
    pause_parser = subparsers.add_parser('pause', help='Pause a project')
    pause_parser.add_argument('project', help='Project ID or name')
    
    resume_parser = subparsers.add_parser('resume', help='Resume a project')
    resume_parser.add_argument('project', help='Project ID or name')
    
    archive_parser = subparsers.add_parser('archive', help='Archive a project')
    archive_parser.add_argument('project', help='Project ID or name')
    
    # Delete project
    delete_parser = subparsers.add_parser('delete', help='Delete a project')
    delete_parser.add_argument('project', help='Project ID or name')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    # Stats
    stats_parser = subparsers.add_parser('stats', help='Show project statistics')
    stats_parser.add_argument('project', help='Project ID or name')
    
    # Reset project
    reset_parser = subparsers.add_parser('reset', help='Reset a project to initial state')
    reset_parser.add_argument('project', help='Project ID or name')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirm reset')
    reset_parser.add_argument('--test', action='store_true', help='Mark as test project (no confirmation needed)')
    
    # Reset all test projects
    reset_test_parser = subparsers.add_parser('reset-tests', help='Reset all test projects')
    
    # Mark as test project
    mark_test_parser = subparsers.add_parser('mark-test', help='Mark project as test/non-test')
    mark_test_parser.add_argument('project', help='Project ID or name')
    mark_test_parser.add_argument('--unmark', action='store_true', help='Remove test marking')
    mark_test_parser.add_argument('--confirm', action='store_true', help='Confirm marking production project as test')
    
    # Export/import
    export_parser = subparsers.add_parser('export', help='Export project config')
    export_parser.add_argument('project', help='Project ID or name')
    export_parser.add_argument('-o', '--output', required=True, help='Output file')
    
    import_parser = subparsers.add_parser('import', help='Import project config')
    import_parser.add_argument('config', help='Config file to import')
    import_parser.add_argument('--codebase', help='New codebase path')
    
    args = parser.parse_args()
    
    # Initialize project manager
    manager = ProjectManager()
    
    # Execute command
    if args.command == 'create':
        project = manager.create_project(
            args.name, args.codebase, 
            args.description or "", 
            args.agents,
            args.theme
        )
        print(f"Created project: {project.name} (ID: {project.project_id})")
        
    elif args.command == 'create-smart':
        # Build requirements from command line args
        requirements = {}
        if args.max_weeks:
            requirements['max_timeline_weeks'] = args.max_weeks
        if args.team_size:
            requirements['available_team_size'] = args.team_size
        
        # Use auto-detected team size if not specified
        agent_count = args.agents if args.agents else None
        
        project = manager.create_project_with_analysis(
            args.name, 
            args.codebase,
            args.description or "",
            auto_analyze=not args.skip_analysis,
            auto_generate_workflow=not args.skip_workflow,
            auto_generate_tasks=not args.skip_tasks,
            requirements=requirements if requirements else None,
            agent_count=agent_count,
            theme=args.theme
        )
        if project:
            print(f"\n🎉 Smart project created successfully: {project.name} (ID: {project.project_id})")
        else:
            print(f"{RED}❌ Failed to create smart project{NC}")
            return 1
        
    elif args.command == 'analyze':
        # Try by ID first, then by name
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            print(f"🔍 Analyzing project: {project.name}")
            analysis = manager.analyze_project_codebase(project.project_id)
            if analysis:
                print(f"\n✅ Analysis completed:")
                print(f"   Project Type: {analysis['project_type'].replace('_', ' ').title()}")
                print(f"   Complexity: {analysis['complexity'].title()}")
                print(f"   Confidence: {analysis['confidence']:.2%}")
                print(f"   Languages: {', '.join(analysis['technologies']['languages'])}")
                print(f"   Frameworks: {', '.join(analysis['technologies']['frameworks'])}")
                print(f"   Recommended Team Size: {analysis['team_size_recommendation']}")
                print(f"   Detected Patterns: {', '.join(analysis['patterns'])}")
            else:
                print(f"{RED}❌ Analysis failed{NC}")
                return 1
        else:
            print(f"Project not found: {args.project}")
            return 1
        
    elif args.command == 'generate-tasks':
        # Try by ID first, then by name
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            print(f"📋 Generating tasks for project: {project.name}")
            tasks_result = manager.generate_project_tasks(project.project_id)
            if tasks_result:
                print(f"\n✅ Task generation completed:")
                print(f"   Total Tasks: {tasks_result['total_tasks']}")
                print(f"   High Confidence Tasks: {tasks_result['high_confidence_tasks']}")
                print(f"   Categories: {', '.join(tasks_result['categories'].keys())}")
                
                # Show some example tasks
                if 'examples' in tasks_result and tasks_result['examples']:
                    print(f"\n   Example Tasks:")
                    for task in tasks_result['examples'][:3]:
                        print(f"   • {task['title']} ({task['category']})")
            else:
                print(f"{RED}❌ Task generation failed{NC}")
                return 1
        else:
            print(f"Project not found: {args.project}")
            return 1
        
    elif args.command == 'list':
        status_filter = ProjectStatus(args.status) if args.status else None
        projects = manager.list_projects(status_filter)
        
        if not projects:
            print("No projects found")
        else:
            print(f"{'ID':<12} {'Name':<30} {'Status':<10} {'Agents':<8} {'Last Active'}")
            print("-" * 80)
            for project in projects:
                last_active = project.last_active[:10] if project.last_active else "Never"
                agent_count = project.agent_count if project.agent_count is not None else 0
                print(f"{project.project_id:<12} {project.name:<30} {project.status.value:<10} "
                      f"{agent_count:<8} {last_active}")
    
    elif args.command == 'switch':
        # Try by ID first, then by name
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            manager.set_active_project(project.project_id)
            print(f"Switched to project: {project.name}")
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command in ['pause', 'resume', 'archive']:
        # Try by ID first, then by name
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            if args.command == 'pause':
                success = manager.pause_project(project.project_id)
            elif args.command == 'resume':
                success = manager.resume_project(project.project_id)
            else:  # archive
                success = manager.archive_project(project.project_id)
            
            if success:
                print(f"{args.command.capitalize()}d project: {project.name}")
            else:
                print(f"Failed to {args.command} project")
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command == 'delete':
        if not args.confirm:
            print("Delete requires --confirm flag")
            return
        
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            if manager.delete_project(project.project_id, confirm=True):
                print(f"Deleted project: {project.name}")
            else:
                print("Failed to delete project")
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command == 'stats':
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            stats = manager.get_project_stats(project.project_id)
            print(f"Project: {stats['name']}")
            print(f"Status: {stats['status']}")
            print(f"Created: {stats['created_at'][:19]}")
            print(f"Last Active: {stats['last_active'][:19]}")
            print(f"Agents: {stats['agent_count']}")
            print(f"Tasks: {stats['task_count']}")
            print(f"Workspace Size: {stats['workspace_size'] / 1024:.1f} KB")
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command == 'reset':
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            # Check if test project or has confirmation
            is_test = args.test or project.metadata.get('is_test', False)
            
            if is_test:
                # Test projects can be reset without challenge
                if manager.reset_project(project.project_id, is_test=True):
                    print(f"Reset project: {project.name}")
                    if args.test:
                        print("Project marked as test project")
                else:
                    print("Failed to reset project")
            elif args.confirm:
                # Production project with confirmation - require challenge
                challenge = manager.generate_reset_challenge(project.project_id)
                if challenge:
                    print(f"\n{RED}⚠️  WARNING: This will DELETE ALL DATA for {project.name}!{NC}")
                    print(f"{RED}This action CANNOT be undone.{NC}\n")
                    print(challenge[0])
                    
                    try:
                        response = input("> ")
                        if response == challenge[1]:
                            print("\nChallenge passed. Resetting project...")
                            if manager.reset_project(project.project_id, is_test=False, skip_challenge=True):
                                print(f"✅ Reset project: {project.name}")
                            else:
                                print("Failed to reset project")
                        else:
                            print(f"\n{RED}Challenge failed. Reset cancelled.{NC}")
                    except KeyboardInterrupt:
                        print(f"\n\n{YELLOW}Reset cancelled by user.{NC}")
                else:
                    print("Failed to generate challenge")
            else:
                print(f"Reset requires --confirm flag for non-test project: {project.name}")
                print("Use --test to mark as test project and reset without confirmation")
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command == 'reset-tests':
        count = manager.reset_all_test_projects()
        print(f"Reset {count} test projects")
    
    elif args.command == 'mark-test':
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            is_test = not args.unmark
            
            # Check if this is a production project being marked as test
            current_is_test = (
                project.name.lower().startswith('test') or
                project.metadata.get('is_test', False) or
                'test' in project.name.lower()
            )
            
            # Require --confirm for marking production projects as test
            if is_test and not current_is_test and not args.confirm:
                print(f"❌ Error: Marking production project '{project.name}' as test requires --confirm flag")
                print("This enables unrestricted resets and is a significant security change.")
                print(f"Usage: {sys.argv[0]} mark-test \"{project.name}\" --confirm")
                sys.exit(1)
            
            # Show warning for production projects even with --confirm
            if is_test and not current_is_test and args.confirm:
                print(f"⚠️  SECURITY WARNING: Marking Production Project as Test ⚠️")
                print(f"Project: {project.name}")
                print("This will enable unrestricted resets without confirmation.")
                print("This is a significant security change for production projects.")
                print("═" * 60)
                input("Press ENTER to continue or Ctrl+C to cancel...")
            
            # Skip challenge since we've done CLI validation
            if manager.mark_as_test_project(project.project_id, is_test, skip_challenge=True):
                action = "test" if is_test else "production" 
                print(f"✅ Marked '{project.name}' as {action} project")
            else:
                print("❌ Failed to update project marking")
        else:
            print(f"❌ Project not found: {args.project}")
    
    elif args.command == 'export':
        project = manager.get_project(args.project)
        if not project:
            project = manager.get_project_by_name(args.project)
        
        if project:
            manager.export_project_config(project.project_id, args.output)
        else:
            print(f"Project not found: {args.project}")
    
    elif args.command == 'import':
        project = manager.import_project_config(args.config, args.codebase)
        if project:
            print(f"Imported project: {project.name} (ID: {project.project_id})")
        else:
            print("Failed to import project")

if __name__ == '__main__':
    main()