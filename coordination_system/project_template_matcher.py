#!/usr/bin/env python3
"""
Project Template Matcher - Intelligent matching system for selecting optimal workflow templates
"""

import json
import math
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

from .project_analyzer import ProjectAnalyzer, AnalysisResult, ProjectType, TechnologyStack
from .workflow_template_engine import WorkflowTemplateEngine, WorkflowTemplate
from .auto_task_generator import AutoTaskGenerator, GeneratedTask

@dataclass
class TemplateMatch:
    template_id: str
    template_name: str
    match_score: float
    confidence: float
    reasoning: List[str]
    missing_requirements: List[str]
    compatibility_issues: List[str]
    recommended_modifications: List[str]

@dataclass
class MatchingCriteria:
    project_type_weight: float = 0.3
    technology_stack_weight: float = 0.25
    complexity_weight: float = 0.15
    team_size_weight: float = 0.1
    timeline_weight: float = 0.1
    existing_structure_weight: float = 0.1

@dataclass
class ProjectRequirements:
    max_timeline_weeks: Optional[int] = None
    available_team_size: Optional[int] = None
    required_skills: List[str] = None
    prohibited_technologies: List[str] = None
    must_have_features: List[str] = None
    preferred_patterns: List[str] = None
    constraints: Dict[str, Any] = None

class ProjectTemplateMatcher:
    def __init__(self):
        self.analyzer = ProjectAnalyzer()
        self.workflow_engine = WorkflowTemplateEngine()
        self.task_generator = AutoTaskGenerator()
        self.similarity_cache = {}

    def find_best_templates(self, project_path: str, 
                          requirements: Optional[ProjectRequirements] = None,
                          criteria: Optional[MatchingCriteria] = None,
                          max_results: int = 5) -> List[TemplateMatch]:
        """Find the best matching workflow templates for a project"""
        
        # Analyze the project
        analysis = self.analyzer.analyze_project(project_path)
        
        # Use default criteria if not provided
        if criteria is None:
            criteria = MatchingCriteria()
        
        # Use default requirements if not provided
        if requirements is None:
            requirements = ProjectRequirements()
        
        # Get all available templates
        available_templates = self.workflow_engine.get_available_templates()
        template_matches = []
        
        # Score each template
        for template_id in available_templates:
            template = self.workflow_engine.get_template(template_id)
            if template:
                match = self._evaluate_template_match(
                    template, analysis, requirements, criteria
                )
                template_matches.append(match)
        
        # Sort by match score and return top results
        template_matches.sort(key=lambda x: x.match_score, reverse=True)
        return template_matches[:max_results]

    def _evaluate_template_match(self, template: WorkflowTemplate, 
                                analysis: AnalysisResult,
                                requirements: ProjectRequirements,
                                criteria: MatchingCriteria) -> TemplateMatch:
        """Evaluate how well a template matches the project"""
        
        # Calculate individual scores
        project_type_score = self._score_project_type_match(template, analysis)
        tech_stack_score = self._score_technology_stack_match(template, analysis)
        complexity_score = self._score_complexity_match(template, analysis)
        team_size_score = self._score_team_size_match(template, analysis)
        timeline_score = self._score_timeline_match(template, requirements)
        structure_score = self._score_existing_structure_match(template, analysis)
        
        # Calculate weighted overall score
        match_score = (
            project_type_score * criteria.project_type_weight +
            tech_stack_score * criteria.technology_stack_weight +
            complexity_score * criteria.complexity_weight +
            team_size_score * criteria.team_size_weight +
            timeline_score * criteria.timeline_weight +
            structure_score * criteria.existing_structure_weight
        )
        
        # Calculate confidence based on how many factors align well
        scores = [project_type_score, tech_stack_score, complexity_score, 
                 team_size_score, timeline_score, structure_score]
        high_scores = len([s for s in scores if s >= 0.7])
        confidence = high_scores / len(scores)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            template, analysis, 
            project_type_score, tech_stack_score, complexity_score,
            team_size_score, timeline_score, structure_score
        )
        
        # Identify missing requirements and issues
        missing_requirements = self._identify_missing_requirements(template, analysis)
        compatibility_issues = self._identify_compatibility_issues(template, analysis, requirements)
        recommended_modifications = self._recommend_modifications(template, analysis, requirements)
        
        return TemplateMatch(
            template_id=template.id,
            template_name=template.name,
            match_score=match_score,
            confidence=confidence,
            reasoning=reasoning,
            missing_requirements=missing_requirements,
            compatibility_issues=compatibility_issues,
            recommended_modifications=recommended_modifications
        )

    def _score_project_type_match(self, template: WorkflowTemplate, 
                                 analysis: AnalysisResult) -> float:
        """Score how well the template matches the detected project type"""
        if template.project_type == analysis.project_type:
            return 1.0
        
        # Define project type similarities
        type_similarities = {
            ProjectType.WEB_APP: {
                ProjectType.API_SERVICE: 0.6,
                ProjectType.MICROSERVICE: 0.5,
                ProjectType.MOBILE_APP: 0.3
            },
            ProjectType.API_SERVICE: {
                ProjectType.WEB_APP: 0.6,
                ProjectType.MICROSERVICE: 0.8,
                ProjectType.LIBRARY: 0.4
            },
            ProjectType.ML_PROJECT: {
                ProjectType.DATA_PIPELINE: 0.7,
                ProjectType.API_SERVICE: 0.3
            },
            ProjectType.MOBILE_APP: {
                ProjectType.WEB_APP: 0.3,
                ProjectType.DESKTOP_APP: 0.5
            },
            ProjectType.CLI_TOOL: {
                ProjectType.LIBRARY: 0.6,
                ProjectType.DESKTOP_APP: 0.4
            }
        }
        
        return type_similarities.get(analysis.project_type, {}).get(template.project_type, 0.2)

    def _score_technology_stack_match(self, template: WorkflowTemplate, 
                                     analysis: AnalysisResult) -> float:
        """Score how well the template supports the project's technology stack"""
        required_skills = set(skill.lower() for skill in template.required_skills)
        optional_skills = set(skill.lower() for skill in template.optional_skills)
        all_template_skills = required_skills | optional_skills
        
        # Combine all technologies from analysis
        project_technologies = set()
        project_technologies.update(tech.lower() for tech in analysis.tech_stack.languages)
        project_technologies.update(tech.lower() for tech in analysis.tech_stack.frameworks)
        project_technologies.update(tech.lower() for tech in analysis.tech_stack.databases)
        
        if not project_technologies:
            return 0.5  # Neutral score if no technologies detected
        
        # Calculate overlap
        matching_technologies = project_technologies & all_template_skills
        coverage = len(matching_technologies) / len(project_technologies)
        
        # Bonus for required skills match
        required_matches = project_technologies & required_skills
        required_coverage = len(required_matches) / len(required_skills) if required_skills else 1.0
        
        # Combined score
        return (coverage * 0.7) + (required_coverage * 0.3)

    def _score_complexity_match(self, template: WorkflowTemplate, 
                               analysis: AnalysisResult) -> float:
        """Score how well the template matches project complexity"""
        # Map complexity to numerical values
        complexity_values = {"low": 1, "medium": 2, "high": 3}
        project_complexity = complexity_values.get(analysis.estimated_complexity, 2)
        
        # Estimate template complexity based on total weeks and phases
        template_complexity_score = (
            template.total_estimated_weeks / 20 +  # Weeks component
            len(template.phases) / 10               # Phases component
        )
        template_complexity = max(1, min(3, template_complexity_score))
        
        # Calculate match score (closer = better)
        difference = abs(project_complexity - template_complexity)
        return max(0, 1.0 - (difference / 2))

    def _score_team_size_match(self, template: WorkflowTemplate, 
                              analysis: AnalysisResult) -> float:
        """Score team size compatibility"""
        template_team_size = template.recommended_team_size
        project_team_size = analysis.team_size_recommendation
        
        # Perfect match
        if template_team_size == project_team_size:
            return 1.0
        
        # Calculate compatibility (closer sizes are better)
        difference = abs(template_team_size - project_team_size)
        max_difference = max(template_team_size, project_team_size)
        
        if max_difference == 0:
            return 1.0
        
        compatibility = max(0, 1.0 - (difference / max_difference))
        
        # Slight preference for templates that can scale down vs up
        if template_team_size > project_team_size:
            compatibility *= 0.9  # Small penalty for oversized teams
        
        return compatibility

    def _score_timeline_match(self, template: WorkflowTemplate, 
                             requirements: ProjectRequirements) -> float:
        """Score timeline compatibility"""
        if not requirements.max_timeline_weeks:
            return 1.0  # No timeline constraint
        
        template_weeks = template.total_estimated_weeks
        max_weeks = requirements.max_timeline_weeks
        
        if template_weeks <= max_weeks:
            # Template fits within timeline
            utilization = template_weeks / max_weeks
            return 0.7 + (0.3 * utilization)  # Prefer fuller utilization
        else:
            # Template exceeds timeline
            excess = (template_weeks - max_weeks) / max_weeks
            return max(0, 1.0 - excess)

    def _score_existing_structure_match(self, template: WorkflowTemplate, 
                                       analysis: AnalysisResult) -> float:
        """Score how well template aligns with existing project structure"""
        structure = analysis.structure
        score = 0.0
        factors = 0
        
        # Check alignment with existing structure
        structure_checks = [
            (structure.has_tests, "testing"),
            (structure.has_docs, "documentation"),
            (structure.has_ci_cd, "ci/cd"),
            (structure.has_docker, "containerization"),
            (structure.has_api, "api development"),
            (structure.has_frontend, "frontend development"),
            (structure.has_backend, "backend development"),
            (structure.has_database, "database management")
        ]
        
        for has_feature, feature_name in structure_checks:
            factors += 1
            # Check if template addresses this area
            template_addresses_feature = self._template_addresses_feature(
                template, feature_name
            )
            
            if has_feature and template_addresses_feature:
                score += 1.0  # Template builds on existing structure
            elif not has_feature and template_addresses_feature:
                score += 0.7  # Template adds missing capability
            elif has_feature and not template_addresses_feature:
                score += 0.3  # Existing capability not addressed
            else:
                score += 0.5  # Neutral
        
        return score / factors if factors > 0 else 0.5

    def _template_addresses_feature(self, template: WorkflowTemplate, 
                                   feature_name: str) -> bool:
        """Check if template addresses a specific feature area"""
        feature_keywords = {
            "testing": ["test", "quality", "coverage"],
            "documentation": ["doc", "documentation", "readme"],
            "ci/cd": ["ci", "cd", "pipeline", "deployment"],
            "containerization": ["docker", "container", "deployment"],
            "api development": ["api", "service", "endpoint"],
            "frontend development": ["frontend", "ui", "component"],
            "backend development": ["backend", "server", "api"],
            "database management": ["database", "data", "model"]
        }
        
        keywords = feature_keywords.get(feature_name, [feature_name])
        
        # Check template phases and tasks for relevant keywords
        for phase in template.phases:
            phase_text = f"{phase.name} {phase.description}".lower()
            for task in phase.tasks:
                task_text = f"{task.title} {task.description}".lower()
                combined_text = f"{phase_text} {task_text}"
                
                if any(keyword in combined_text for keyword in keywords):
                    return True
        
        return False

    def _generate_reasoning(self, template: WorkflowTemplate, analysis: AnalysisResult,
                           project_type_score: float, tech_stack_score: float,
                           complexity_score: float, team_size_score: float,
                           timeline_score: float, structure_score: float) -> List[str]:
        """Generate human-readable reasoning for template match"""
        reasoning = []
        
        # Project type reasoning
        if project_type_score >= 0.8:
            reasoning.append(f"Excellent project type match - template designed for {template.project_type.value.replace('_', ' ')}")
        elif project_type_score >= 0.5:
            reasoning.append(f"Good project type compatibility - template adaptable to {analysis.project_type.value.replace('_', ' ')} projects")
        else:
            reasoning.append(f"Limited project type match - template may need significant adaptation")
        
        # Technology stack reasoning
        if tech_stack_score >= 0.7:
            reasoning.append("Strong technology stack alignment - template supports most project technologies")
        elif tech_stack_score >= 0.4:
            reasoning.append("Moderate technology stack compatibility - some technologies well-supported")
        else:
            reasoning.append("Limited technology support - template may not cover project's tech stack")
        
        # Complexity reasoning
        if complexity_score >= 0.8:
            reasoning.append(f"Well-matched complexity level - template suits {analysis.estimated_complexity} complexity projects")
        elif complexity_score >= 0.5:
            reasoning.append("Acceptable complexity match - template can be adjusted for project needs")
        else:
            reasoning.append("Complexity mismatch - template may be too simple or complex")
        
        # Team size reasoning
        if team_size_score >= 0.8:
            reasoning.append(f"Optimal team size match - template designed for {template.recommended_team_size} person teams")
        elif team_size_score >= 0.5:
            reasoning.append("Workable team size - template can be adapted for different team configurations")
        else:
            reasoning.append("Team size mismatch - significant workflow adjustments needed")
        
        # Structure reasoning
        if structure_score >= 0.7:
            reasoning.append("Good alignment with existing project structure")
        elif structure_score >= 0.4:
            reasoning.append("Moderate structural compatibility - builds on some existing elements")
        else:
            reasoning.append("Limited structural alignment - significant setup work required")
        
        return reasoning

    def _identify_missing_requirements(self, template: WorkflowTemplate, 
                                     analysis: AnalysisResult) -> List[str]:
        """Identify requirements that the project doesn't meet"""
        missing = []
        
        # Check required skills
        required_skills = set(skill.lower() for skill in template.required_skills)
        project_skills = set()
        project_skills.update(tech.lower() for tech in analysis.tech_stack.languages)
        project_skills.update(tech.lower() for tech in analysis.tech_stack.frameworks)
        
        missing_skills = required_skills - project_skills
        if missing_skills:
            missing.append(f"Missing required skills: {', '.join(missing_skills)}")
        
        # Check team size requirements
        if analysis.team_size_recommendation < template.recommended_team_size:
            missing.append(f"Team size may be insufficient (need {template.recommended_team_size}, have {analysis.team_size_recommendation})")
        
        return missing

    def _identify_compatibility_issues(self, template: WorkflowTemplate, 
                                      analysis: AnalysisResult,
                                      requirements: ProjectRequirements) -> List[str]:
        """Identify potential compatibility issues"""
        issues = []
        
        # Timeline constraints
        if (requirements.max_timeline_weeks and 
            template.total_estimated_weeks > requirements.max_timeline_weeks):
            overage = template.total_estimated_weeks - requirements.max_timeline_weeks
            issues.append(f"Timeline exceeds constraint by {overage} weeks")
        
        # Team size constraints
        if (requirements.available_team_size and 
            template.recommended_team_size > requirements.available_team_size):
            shortage = template.recommended_team_size - requirements.available_team_size
            issues.append(f"Requires {shortage} additional team members")
        
        # Prohibited technologies
        if requirements.prohibited_technologies:
            prohibited = set(tech.lower() for tech in requirements.prohibited_technologies)
            template_techs = set(skill.lower() for skill in 
                               template.required_skills + template.optional_skills)
            conflicts = prohibited & template_techs
            if conflicts:
                issues.append(f"Uses prohibited technologies: {', '.join(conflicts)}")
        
        return issues

    def _recommend_modifications(self, template: WorkflowTemplate, 
                                analysis: AnalysisResult,
                                requirements: ProjectRequirements) -> List[str]:
        """Recommend modifications to better fit the project"""
        modifications = []
        
        # Timeline adjustments
        if (requirements.max_timeline_weeks and 
            template.total_estimated_weeks > requirements.max_timeline_weeks):
            modifications.append("Consider parallelizing more phases to reduce timeline")
            modifications.append("Prioritize core features and defer nice-to-have elements")
        
        # Technology adaptations
        project_techs = set()
        project_techs.update(analysis.tech_stack.languages)
        project_techs.update(analysis.tech_stack.frameworks)
        
        if "python" in [t.lower() for t in project_techs] and "javascript" not in [t.lower() for t in project_techs]:
            modifications.append("Adapt frontend tasks for Python-based solutions (Flask/Django templates)")
        
        if "react" in [t.lower() for t in project_techs] and template.project_type != ProjectType.WEB_APP:
            modifications.append("Add React-specific component development phases")
        
        # Existing structure adaptations
        if analysis.structure.has_tests:
            modifications.append("Skip basic test setup and focus on advanced testing strategies")
        
        if analysis.structure.has_ci_cd:
            modifications.append("Build on existing CI/CD rather than starting from scratch")
        
        if analysis.structure.has_docker:
            modifications.append("Leverage existing containerization for deployment phases")
        
        return modifications

    def generate_custom_template(self, project_path: str, 
                                requirements: Optional[ProjectRequirements] = None) -> WorkflowTemplate:
        """Generate a completely custom template based on project analysis"""
        
        analysis = self.analyzer.analyze_project(project_path)
        
        # Find best matching base template
        matches = self.find_best_templates(project_path, requirements, max_results=1)
        
        if matches:
            base_template = self.workflow_engine.get_template(matches[0].template_id)
            custom_template = self.workflow_engine._customize_template(base_template, analysis)
        else:
            # Create from scratch if no good matches
            custom_template = self.workflow_engine._create_generic_template(analysis)
        
        # Generate additional tasks from analysis
        generated_tasks, _ = self.task_generator.generate_tasks_from_project(project_path)
        
        # Integrate generated tasks into template
        custom_template = self._integrate_generated_tasks(custom_template, generated_tasks)
        
        return custom_template

    def _integrate_generated_tasks(self, template: WorkflowTemplate, 
                                  generated_tasks: List[GeneratedTask]) -> WorkflowTemplate:
        """Integrate automatically generated tasks into workflow template"""
        
        # Group generated tasks by category
        tasks_by_category = defaultdict(list)
        for task in generated_tasks:
            tasks_by_category[task.category].append(task)
        
        # Map categories to template phases
        category_to_phase = {
            "setup": "setup",
            "development": "core_development", 
            "testing": "testing_quality",
            "deployment": "deployment",
            "security": "testing_quality",
            "documentation": "setup",
            "maintenance": "deployment"
        }
        
        # Add tasks to appropriate phases
        for category, tasks in tasks_by_category.items():
            phase_name = category_to_phase.get(category, "core_development")
            
            # Find matching phase or create new one
            target_phase = None
            for phase in template.phases:
                if phase_name in phase.id.lower() or phase_name in phase.name.lower():
                    target_phase = phase
                    break
            
            if not target_phase:
                # Create new phase if needed
                from .workflow_template_engine import Phase, Task
                target_phase = Phase(
                    id=category,
                    name=category.replace('_', ' ').title(),
                    description=f"Tasks for {category}",
                    estimated_weeks=1,
                    parallel_execution=True,
                    tasks=[]
                )
                template.phases.append(target_phase)
            
            # Convert generated tasks to template tasks
            for gen_task in tasks:
                if gen_task.confidence >= 0.7:  # Only include high-confidence tasks
                    from .workflow_template_engine import Task
                    template_task = Task(
                        id=gen_task.id,
                        title=gen_task.title,
                        description=gen_task.description,
                        estimated_hours=gen_task.estimated_hours,
                        priority=gen_task.priority,
                        dependencies=gen_task.dependencies,
                        agent_specialization=gen_task.agent_specialization,
                        tags=gen_task.tags,
                        acceptance_criteria=gen_task.acceptance_criteria
                    )
                    target_phase.tasks.append(template_task)
        
        # Recalculate total estimated weeks
        template.total_estimated_weeks = sum(phase.estimated_weeks for phase in template.phases)
        
        return template

    def compare_templates(self, template_ids: List[str], project_path: str) -> Dict[str, TemplateMatch]:
        """Compare multiple templates for a specific project"""
        analysis = self.analyzer.analyze_project(project_path)
        criteria = MatchingCriteria()
        requirements = ProjectRequirements()
        
        comparisons = {}
        for template_id in template_ids:
            template = self.workflow_engine.get_template(template_id)
            if template:
                match = self._evaluate_template_match(template, analysis, requirements, criteria)
                comparisons[template_id] = match
        
        return comparisons

    def get_template_recommendations(self, project_path: str, 
                                   user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive template recommendations with explanations"""
        
        analysis = self.analyzer.analyze_project(project_path)
        
        # Create requirements from user preferences
        requirements = ProjectRequirements()
        if user_preferences:
            requirements.max_timeline_weeks = user_preferences.get('max_weeks')
            requirements.available_team_size = user_preferences.get('team_size')
            requirements.required_skills = user_preferences.get('required_skills', [])
            requirements.prohibited_technologies = user_preferences.get('prohibited_tech', [])
        
        # Find best matches
        matches = self.find_best_templates(project_path, requirements, max_results=10)
        
        # Generate comprehensive recommendation
        recommendation = {
            "project_analysis": {
                "type": analysis.project_type.value,
                "complexity": analysis.estimated_complexity,
                "confidence": analysis.confidence,
                "technologies": {
                    "languages": analysis.tech_stack.languages,
                    "frameworks": analysis.tech_stack.frameworks,
                    "databases": analysis.tech_stack.databases
                },
                "structure": {
                    "has_tests": analysis.structure.has_tests,
                    "has_docs": analysis.structure.has_docs,
                    "has_ci_cd": analysis.structure.has_ci_cd,
                    "has_docker": analysis.structure.has_docker
                }
            },
            "template_matches": [asdict(match) for match in matches],
            "top_recommendation": asdict(matches[0]) if matches else None,
            "alternative_approaches": self._suggest_alternative_approaches(analysis),
            "customization_suggestions": self._suggest_customizations(matches[0] if matches else None, analysis)
        }
        
        return recommendation

    def _suggest_alternative_approaches(self, analysis: AnalysisResult) -> List[str]:
        """Suggest alternative approaches based on project characteristics"""
        suggestions = []
        
        if analysis.estimated_complexity == "high":
            suggestions.append("Consider breaking into multiple smaller projects")
            suggestions.append("Implement MVP first, then expand features incrementally")
        
        if len(analysis.tech_stack.languages) > 2:
            suggestions.append("Consider standardizing on fewer languages for maintainability")
        
        if not analysis.structure.has_tests and analysis.project_type != ProjectType.CLI_TOOL:
            suggestions.append("Start with test setup to establish quality practices early")
        
        if analysis.project_type == ProjectType.WEB_APP and not analysis.structure.has_api:
            suggestions.append("Consider API-first approach for better scalability")
        
        return suggestions

    def _suggest_customizations(self, best_match: Optional[TemplateMatch], 
                               analysis: AnalysisResult) -> List[str]:
        """Suggest specific customizations for the best matching template"""
        if not best_match:
            return ["No template match found - consider custom workflow development"]
        
        customizations = []
        
        # Based on confidence level
        if best_match.confidence < 0.6:
            customizations.append("Significant template customization recommended")
            customizations.extend(best_match.recommended_modifications)
        
        # Based on existing structure
        if analysis.structure.has_ci_cd:
            customizations.append("Integrate with existing CI/CD pipeline")
        
        if analysis.structure.has_docker:
            customizations.append("Leverage existing containerization setup")
        
        if analysis.structure.has_tests:
            customizations.append("Build on existing test infrastructure")
        
        return customizations

def main():
    """Command-line interface for template matching"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Find best workflow templates for projects")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of results")
    parser.add_argument("--max-weeks", type=int, help="Maximum timeline in weeks")
    parser.add_argument("--team-size", type=int, help="Available team size")
    parser.add_argument("--output", "-o", help="Output file for recommendations")
    parser.add_argument("--format", choices=["json", "report"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    matcher = ProjectTemplateMatcher()
    
    try:
        # Create requirements from command line args
        requirements = ProjectRequirements(
            max_timeline_weeks=args.max_weeks,
            available_team_size=args.team_size
        )
        
        if args.format == "report":
            # Generate comprehensive recommendation
            user_prefs = {}
            if args.max_weeks:
                user_prefs['max_weeks'] = args.max_weeks
            if args.team_size:
                user_prefs['team_size'] = args.team_size
                
            recommendations = matcher.get_template_recommendations(
                args.project_path, user_prefs
            )
            output = json.dumps(recommendations, indent=2, default=str)
        else:
            # Simple template matching
            matches = matcher.find_best_templates(
                args.project_path, requirements, max_results=args.max_results
            )
            output = json.dumps([asdict(match) for match in matches], indent=2, default=str)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Recommendations written to {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error finding template matches: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())