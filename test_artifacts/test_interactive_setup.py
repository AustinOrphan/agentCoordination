#!/usr/bin/env python3
"""
Test script for the interactive setup functionality
"""

import tempfile
import os
import sys
from pathlib import Path

# Add coordination_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'coordination_system'))

def test_cli_commands():
    """Test basic CLI command functionality"""
    print("🧪 Testing CLI Commands")
    
    from coordination_system.cli import main as cli_main
    from coordination_system.project_analyzer import ProjectAnalyzer
    
    # Test analyzer
    analyzer = ProjectAnalyzer()
    current_dir = "."
    
    try:
        result = analyzer.analyze_project(current_dir)
        print(f"✅ Project analysis works: {result.project_type}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Languages: {result.tech_stack.languages if result.tech_stack else 'None'}")
    except Exception as e:
        print(f"❌ Project analysis failed: {e}")
    
    print("\n🎯 CLI Commands Available:")
    print("   python -m coordination_system.cli analyze .")
    print("   python -m coordination_system.cli generate-tasks .")
    print("   python -m coordination_system.cli setup")
    print("   python -m coordination_system.cli create-smart")


def test_project_types():
    """Test different project type setups"""
    print("\n🏗️ Testing Project Type Detection")
    
    from coordination_system.interactive_setup import InteractiveSetup
    
    setup = InteractiveSetup()
    
    # List available project types
    print("📋 Available New Project Types:")
    for choice in setup.setup_choices["new_project"]:
        print(f"   • {choice.name}: {choice.description}")
    
    print("\n📋 Available Enhancement Types:")
    for choice in setup.setup_choices["existing_project"]:
        print(f"   • {choice.name}: {choice.description}")


def create_sample_project_structure():
    """Create a sample project structure for testing"""
    print("\n🏗️ Creating Sample Project for Testing")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "sample-react-app"
        project_path.mkdir()
        
        # Create React-like structure
        (project_path / "package.json").write_text('''
{
  "name": "sample-react-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}''')
        
        (project_path / "src").mkdir()
        (project_path / "src" / "App.js").write_text('''
import React from 'react';

function App() {
  return <div>Hello React!</div>;
}

export default App;
''')
        
        # Test analysis
        from coordination_system.project_analyzer import ProjectAnalyzer
        analyzer = ProjectAnalyzer()
        
        try:
            result = analyzer.analyze_project(str(project_path))
            print(f"✅ Sample project detected as: {result.project_type}")
            print(f"   Frameworks: {result.tech_stack.frameworks}")
            
            # Test task generation
            from coordination_system.auto_task_generator import AutoTaskGenerator
            generator = AutoTaskGenerator()
            tasks, report = generator.generate_tasks_from_project(str(project_path))
            
            print(f"✅ Generated {len(tasks)} tasks for sample project")
            if tasks:
                print(f"   First task: {tasks[0].title}")
            
        except Exception as e:
            print(f"❌ Sample project analysis failed: {e}")


def test_dependencies():
    """Test if required dependencies are available"""
    print("\n📦 Testing Dependencies")
    
    required_modules = [
        'questionary',
        'rich',
        'pathlib',
        'json',
        'tempfile'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError:
            print(f"❌ {module} - Missing (pip install {module})")


def main():
    """Main test function"""
    print("🚀 Interactive Setup Test Suite")
    print("=" * 50)
    
    test_dependencies()
    test_cli_commands()
    test_project_types()
    create_sample_project_structure()
    
    print("\n" + "=" * 50)
    print("✅ Interactive Setup Tests Complete!")
    print("\n🎯 To try the interactive setup:")
    print("   python coordination_system/interactive_setup.py")
    print("   # or")
    print("   python coordination_system/cli.py setup")


if __name__ == "__main__":
    main()