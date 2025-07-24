#!/usr/bin/env python3
"""Show all possible reset challenge types"""

import sys
sys.path.append('coordination_system')

from project_manager import ProjectManager

def show_all_challenges():
    """Show examples of all challenge types"""
    manager = ProjectManager()
    
    # Create a fake project for demonstration
    class FakeProject:
        def __init__(self):
            self.project_id = "proj_12345678"
            self.name = "Example Project"
    
    project = FakeProject()
    
    print("=== PRODUCTION RESET CHALLENGE TYPES ===\n")
    
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
            f"Type the first 8 characters of the project ID ({project.project_id[:8]}) to confirm:",
            project.project_id[:8]
        ),
        (
            f"Type 'DELETE ALL DATA' to confirm reset of {project.name}:",
            "DELETE ALL DATA"
        )
    ]
    
    for i, (challenge, response) in enumerate(challenges, 1):
        print(f"Challenge Type {i}:")
        print(f"  Prompt: {challenge}")
        print(f"  Required Response: {response}")
        print()

if __name__ == "__main__":
    show_all_challenges()