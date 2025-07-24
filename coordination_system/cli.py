#!/usr/bin/env python3
"""
Command Line Interface for Project Analysis and Setup Tools
Provides unified access to all project automation features
"""

import argparse
import sys
from pathlib import Path
import json

from .project_analyzer import ProjectAnalyzer
from .auto_task_generator import AutoTaskGenerator
from .migration_analyzer import MigrationAnalyzer
from .migration_workflows import MigrationWorkflowGenerator
from .interactive_setup import InteractiveSetup


def cmd_analyze(args):
    """Analyze a project and display results"""
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project(args.path)

    print(f"Project Type: {result.project_type}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Complexity: {result.estimated_complexity}")
    print(f"Team Size: {result.team_size_recommendation}")

    if result.tech_stack:
        if result.tech_stack.languages:
            print(f"Languages: {', '.join(result.tech_stack.languages)}")
        if result.tech_stack.frameworks:
            print(f"Frameworks: {', '.join(result.tech_stack.frameworks)}")
        if result.tech_stack.databases:
            print(f"Databases: {', '.join(result.tech_stack.databases)}")

    if args.output:
        output_data = {
            "project_type": str(result.project_type),
            "confidence": result.confidence,
            "complexity": result.estimated_complexity,
            "team_size": result.team_size_recommendation,
            "tech_stack": {
                "languages": result.tech_stack.languages if result.tech_stack else [],
                "frameworks": result.tech_stack.frameworks if result.tech_stack else [],
                "databases": result.tech_stack.databases if result.tech_stack else [],
                "build_tools": (
                    result.tech_stack.build_tools if result.tech_stack else []
                ),
            },
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nAnalysis saved to {args.output}")


def cmd_generate_tasks(args):
    """Generate tasks for a project"""
    generator = AutoTaskGenerator()
    tasks, report = generator.generate_tasks_from_project(args.path)

    print(f"Generated {len(tasks)} tasks:")
    for task in tasks:
        print(f"- {task.title} ({task.category}, {task.estimated_hours}h)")

    if args.output:
        tasks_data = []
        for task in tasks:
            tasks_data.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "category": task.category,
                    "priority": task.priority,
                    "estimated_hours": task.estimated_hours,
                    "dependencies": task.dependencies,
                    "tags": task.tags,
                }
            )

        with open(args.output, "w") as f:
            json.dump(tasks_data, f, indent=2)
        print(f"Tasks saved to {args.output}")


def cmd_migration_analysis(args):
    """Analyze migration opportunities"""
    analyzer = MigrationAnalyzer()
    assessment = analyzer.analyze_migration_opportunities(args.path)

    print(f"Migration Readiness Score: {assessment.readiness_score}/100")
    print(f"Recommended Migration: {assessment.recommended_migration_type}")
    print(f"Estimated Duration: {assessment.estimated_duration_weeks} weeks")

    if assessment.identified_services:
        print(f"\nIdentified {len(assessment.identified_services)} potential services:")
        for service in assessment.identified_services[:5]:
            print(f"- {service.name}: {service.description}")

    if assessment.blocking_factors:
        print(f"\nBlocking Factors:")
        for factor in assessment.blocking_factors:
            print(f"- {factor}")

    if args.workflow:
        workflows = MigrationWorkflowGenerator()
        workflow_data = workflows.generate_workflow(assessment)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(workflow_data, f, indent=2)
            print(f"Migration workflow saved to {args.output}")


def cmd_interactive_setup(args):
    """Launch interactive project setup"""
    setup = InteractiveSetup()
    setup.run()


def cmd_create_smart(args):
    """Smart project creation with analysis-driven setup"""
    print("🚀 Smart Project Creation")

    if args.path and Path(args.path).exists():
        # Analyze existing project and enhance
        print(f"Analyzing existing project at {args.path}...")

        analyzer = ProjectAnalyzer()
        result = analyzer.analyze_project(args.path)

        print(f"Detected: {result.project_type} (confidence: {result.confidence:.2f})")

        # Generate enhancement tasks
        generator = AutoTaskGenerator()
        tasks, report = generator.generate_tasks_from_project(args.path)

        print(f"Generated {len(tasks)} enhancement tasks")

        if args.output:
            output_data = {
                "analysis": {
                    "project_type": str(result.project_type),
                    "confidence": result.confidence,
                    "complexity": result.estimated_complexity,
                },
                "tasks": [
                    {
                        "title": task.title,
                        "description": task.description,
                        "category": task.category,
                        "priority": task.priority,
                        "estimated_hours": task.estimated_hours,
                    }
                    for task in tasks
                ],
            }

            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Smart analysis saved to {args.output}")

    else:
        # Launch interactive setup for new project
        print("Launching interactive setup for new project...")
        cmd_interactive_setup(args)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Project Analysis and Automation Tools", prog="project-cli"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze project structure and technology"
    )
    analyze_parser.add_argument("path", help="Path to project directory")
    analyze_parser.add_argument(
        "-o", "--output", help="Output file for analysis results"
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # Generate tasks command
    tasks_parser = subparsers.add_parser(
        "generate-tasks", help="Generate recommended tasks for project"
    )
    tasks_parser.add_argument("path", help="Path to project directory")
    tasks_parser.add_argument("-o", "--output", help="Output file for tasks")
    tasks_parser.set_defaults(func=cmd_generate_tasks)

    # Migration analysis command
    migration_parser = subparsers.add_parser(
        "migration", help="Analyze migration opportunities"
    )
    migration_parser.add_argument("path", help="Path to project directory")
    migration_parser.add_argument(
        "-w", "--workflow", action="store_true", help="Generate migration workflow"
    )
    migration_parser.add_argument(
        "-o", "--output", help="Output file for migration plan"
    )
    migration_parser.set_defaults(func=cmd_migration_analysis)

    # Interactive setup command
    setup_parser = subparsers.add_parser("setup", help="Interactive project setup")
    setup_parser.set_defaults(func=cmd_interactive_setup)

    # Smart create command
    smart_parser = subparsers.add_parser(
        "create-smart", help="Smart project creation with analysis"
    )
    smart_parser.add_argument(
        "-p", "--path", help="Path to existing project (optional)"
    )
    smart_parser.add_argument("-o", "--output", help="Output file for results")
    smart_parser.set_defaults(func=cmd_create_smart)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(args, "debug") and args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
