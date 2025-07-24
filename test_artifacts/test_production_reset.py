#!/usr/bin/env python3
"""Test script for production reset with challenge"""

import sys
import os
sys.path.append('coordination_system')

from project_manager import ProjectManager

def test_production_reset():
    """Test the production reset challenge system"""
    manager = ProjectManager()
    
    # Get the production project
    project = manager.get_project_by_name("Production Project")
    if not project:
        print("Production Project not found")
        return
    
    print(f"Testing reset for: {project.name}")
    print(f"Project ID: {project.project_id}")
    print(f"Is test project: {project.metadata.get('is_test', False)}")
    
    # Generate a challenge
    challenge = manager.generate_reset_challenge(project.project_id)
    if challenge:
        print(f"\nChallenge: {challenge[0]}")
        print(f"Expected response: {challenge[1]}")
        
        # Simulate correct response
        print("\nSimulating correct response...")
        result = manager.reset_project(project.project_id, is_test=False, skip_challenge=True)
        if result:
            print("✅ Reset successful!")
        else:
            print("❌ Reset failed!")
    else:
        print("Failed to generate challenge")

if __name__ == "__main__":
    test_production_reset()