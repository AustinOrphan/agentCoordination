#!/usr/bin/env python3
"""
Migration CLI - Command-line interface for project migration analysis and planning
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

try:
    from .migration_analyzer import MigrationAnalyzer, MigrationAssessment
    from .migration_workflows import MigrationWorkflowGenerator, MigrationType, MigrationComplexity
    from .project_analyzer import ProjectAnalyzer
except ImportError:
    # When run as a script
    from migration_analyzer import MigrationAnalyzer, MigrationAssessment
    from migration_workflows import MigrationWorkflowGenerator, MigrationType, MigrationComplexity
    from project_analyzer import ProjectAnalyzer

class MigrationCLI:
    """Command-line interface for migration analysis and planning"""
    
    def __init__(self):
        self.migration_analyzer = MigrationAnalyzer()
        self.workflow_generator = MigrationWorkflowGenerator()
        self.project_analyzer = ProjectAnalyzer()
    
    def analyze_migration_opportunities(self, project_path: str, output_format: str = "json") -> Dict[str, Any]:
        """Analyze migration opportunities for a project"""
        try:
            # First, analyze the project with the standard analyzer
            project_analysis = self.project_analyzer.analyze_project(project_path)
            
            # Then perform migration-specific analysis
            migration_assessment = self.migration_analyzer.analyze_migration_opportunities(project_path)
            
            # Combine results
            combined_results = {
                "project_analysis": {
                    "project_type": str(project_analysis.project_type),
                    "confidence": project_analysis.confidence,
                    "tech_stack": {
                        "languages": project_analysis.tech_stack.languages,
                        "frameworks": project_analysis.tech_stack.frameworks,
                        "databases": project_analysis.tech_stack.databases
                    },
                    "complexity": project_analysis.estimated_complexity
                },
                "migration_assessment": {
                    "current_architecture": migration_assessment.current_architecture,
                    "migration_readiness_score": migration_assessment.migration_readiness_score,
                    "opportunities": [self._serialize_opportunity(opp) for opp in migration_assessment.opportunities],
                    "domain_boundaries": [self._serialize_domain_boundary(db) for db in migration_assessment.domain_boundaries],
                    "technical_debt_blockers": migration_assessment.technical_debt_blockers,
                    "organizational_considerations": migration_assessment.organizational_considerations,
                    "recommended_approach": migration_assessment.recommended_approach,
                    "migration_roadmap": migration_assessment.migration_roadmap
                }
            }
            
            if output_format == "json":
                return combined_results
            else:
                return self._format_human_readable(combined_results)
                
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_migration_workflow(self, migration_type: str, complexity: str = "medium") -> Dict[str, Any]:
        """Generate detailed migration workflow"""
        try:
            # Convert string inputs to enums
            migration_type_enum = MigrationType(migration_type)
            complexity_enum = MigrationComplexity(complexity)
            
            workflow = self.workflow_generator.generate_workflow(migration_type_enum, complexity_enum)
            
            return self._serialize_workflow(workflow)
            
        except ValueError as e:
            return {"error": f"Invalid migration type or complexity: {str(e)}"}
        except Exception as e:
            return {"error": f"Workflow generation failed: {str(e)}"}
    
    def _serialize_opportunity(self, opportunity) -> Dict[str, Any]:
        """Serialize migration opportunity to dictionary"""
        return {
            "migration_type": opportunity.migration_type.value,
            "name": opportunity.name,
            "description": opportunity.description,
            "business_value": opportunity.business_value,
            "technical_benefits": opportunity.technical_benefits,
            "complexity": opportunity.complexity.value,
            "estimated_effort_weeks": opportunity.estimated_effort_weeks,
            "prerequisites": opportunity.prerequisites,
            "risks": opportunity.risks,
            "success_metrics": opportunity.success_metrics
        }
    
    def _serialize_domain_boundary(self, boundary) -> Dict[str, Any]:
        """Serialize domain boundary to dictionary"""
        return {
            "name": boundary.name,
            "files": boundary.files,
            "dependencies": boundary.dependencies,
            "external_dependencies": boundary.external_dependencies,
            "cohesion_score": boundary.cohesion_score,
            "coupling_score": boundary.coupling_score,
            "size_estimate": boundary.size_estimate,
            "extraction_difficulty": boundary.extraction_difficulty
        }
    
    def _serialize_workflow(self, workflow) -> Dict[str, Any]:
        """Serialize migration workflow to dictionary"""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "migration_type": workflow.migration_type.value,
            "complexity": workflow.complexity.value,
            "total_duration_weeks": workflow.total_duration_weeks,
            "phases": [self._serialize_phase(phase) for phase in workflow.phases],
            "prerequisites": workflow.prerequisites,
            "success_metrics": workflow.success_metrics,
            "common_pitfalls": workflow.common_pitfalls,
            "best_practices": workflow.best_practices,
            "required_skills": workflow.required_skills,
            "tools_and_technologies": workflow.tools_and_technologies
        }
    
    def _serialize_phase(self, phase) -> Dict[str, Any]:
        """Serialize migration phase to dictionary"""
        return {
            "phase_number": phase.phase_number,
            "name": phase.name,
            "description": phase.description,
            "duration_weeks": phase.duration_weeks,
            "objectives": phase.objectives,
            "tasks": [self._serialize_task(task) for task in phase.tasks],
            "success_criteria": phase.success_criteria,
            "exit_criteria": phase.exit_criteria,
            "rollback_plan": phase.rollback_plan
        }
    
    def _serialize_task(self, task) -> Dict[str, Any]:
        """Serialize migration task to dictionary"""
        return {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "category": task.category,
            "estimated_hours": task.estimated_hours,
            "prerequisites": task.prerequisites,
            "deliverables": task.deliverables,
            "acceptance_criteria": task.acceptance_criteria,
            "assigned_roles": task.assigned_roles,
            "tools_required": task.tools_required,
            "risks": task.risks,
            "mitigation_strategies": task.mitigation_strategies
        }
    
    def _format_human_readable(self, results: Dict[str, Any]) -> str:
        """Format results in human-readable format"""
        output = []
        
        # Project Analysis Summary
        project = results["project_analysis"]
        output.append("# Project Migration Analysis Report\n")
        output.append(f"**Project Type**: {project['project_type']}")
        output.append(f"**Confidence**: {project['confidence']:.2f}")
        output.append(f"**Complexity**: {project['complexity']}")
        output.append(f"**Languages**: {', '.join(project['tech_stack']['languages'])}")
        output.append(f"**Frameworks**: {', '.join(project['tech_stack']['frameworks'])}")
        
        # Migration Assessment
        migration = results["migration_assessment"]
        output.append(f"\n## Migration Assessment")
        output.append(f"**Current Architecture**: {migration['current_architecture']}")
        output.append(f"**Migration Readiness Score**: {migration['migration_readiness_score']:.1f}/100")
        output.append(f"**Recommended Approach**: {migration['recommended_approach']}")
        
        # Migration Opportunities
        if migration["opportunities"]:
            output.append(f"\n## Migration Opportunities ({len(migration['opportunities'])} found)")
            for i, opp in enumerate(migration["opportunities"], 1):
                output.append(f"\n### {i}. {opp['name']}")
                output.append(f"**Type**: {opp['migration_type']}")
                output.append(f"**Complexity**: {opp['complexity']}")
                output.append(f"**Effort**: {opp['estimated_effort_weeks']} weeks")
                output.append(f"**Business Value**: {opp['business_value']}")
                output.append(f"**Technical Benefits**:")
                for benefit in opp['technical_benefits']:
                    output.append(f"- {benefit}")
        
        # Domain Boundaries
        if migration["domain_boundaries"]:
            output.append(f"\n## Domain Boundaries ({len(migration['domain_boundaries'])} identified)")
            for boundary in migration["domain_boundaries"]:
                output.append(f"\n### {boundary['name']}")
                output.append(f"**Cohesion Score**: {boundary['cohesion_score']:.2f}")
                output.append(f"**Coupling Score**: {boundary['coupling_score']:.2f}")
                output.append(f"**Extraction Difficulty**: {boundary['extraction_difficulty']}")
                output.append(f"**Files**: {len(boundary['files'])}")
        
        # Technical Debt Blockers
        if migration["technical_debt_blockers"]:
            output.append(f"\n## Technical Debt Blockers")
            for blocker in migration["technical_debt_blockers"]:
                output.append(f"- {blocker}")
        
        # Organizational Considerations
        if migration["organizational_considerations"]:
            output.append(f"\n## Organizational Considerations")
            for consideration in migration["organizational_considerations"]:
                output.append(f"- {consideration}")
        
        # Migration Roadmap
        if migration["migration_roadmap"]:
            output.append(f"\n## Migration Roadmap")
            for phase in migration["migration_roadmap"]:
                output.append(f"\n### Phase {phase['phase']}: {phase['name']} ({phase['duration_weeks']} weeks)")
                output.append(f"**Objectives**:")
                for objective in phase['objectives']:
                    output.append(f"- {objective}")
                output.append(f"**Deliverables**:")
                for deliverable in phase['deliverables']:
                    output.append(f"- {deliverable}")
        
        return "\n".join(output)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Migration Analysis and Planning Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze migration opportunities
  python migration_cli.py analyze /path/to/project
  
  # Generate specific migration workflow
  python migration_cli.py workflow --type monolith_to_microservices --complexity high
  
  # Save analysis to file
  python migration_cli.py analyze /path/to/project --output analysis.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze migration opportunities')
    analyze_parser.add_argument('project_path', help='Path to project directory')
    analyze_parser.add_argument('--format', choices=['json', 'human'], default='human',
                               help='Output format (default: human)')
    analyze_parser.add_argument('--output', '-o', help='Output file path')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Generate migration workflow')
    workflow_parser.add_argument('--type', required=True,
                                choices=[t.value for t in MigrationType],
                                help='Migration type')
    workflow_parser.add_argument('--complexity', 
                                choices=[c.value for c in MigrationComplexity],
                                default='medium', help='Migration complexity')
    workflow_parser.add_argument('--output', '-o', help='Output file path')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available migration types and complexities')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = MigrationCLI()
    
    try:
        if args.command == 'analyze':
            if not Path(args.project_path).exists():
                print(f"Error: Project path '{args.project_path}' does not exist")
                return 1
            
            results = cli.analyze_migration_opportunities(args.project_path, args.format)
            
            if args.format == 'json':
                output = json.dumps(results, indent=2)
            else:
                output = results if isinstance(results, str) else json.dumps(results, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Analysis saved to {args.output}")
            else:
                print(output)
        
        elif args.command == 'workflow':
            results = cli.generate_migration_workflow(args.type, args.complexity)
            output = json.dumps(results, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Workflow saved to {args.output}")
            else:
                print(output)
        
        elif args.command == 'list':
            print("Available Migration Types:")
            for migration_type in MigrationType:
                print(f"  - {migration_type.value}")
            
            print("\nAvailable Complexity Levels:")
            for complexity in MigrationComplexity:
                print(f"  - {complexity.value}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())