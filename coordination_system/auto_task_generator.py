#!/usr/bin/env python3
"""
Automatic Task Generator - Generates project tasks automatically based on codebase analysis
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from .project_analyzer import ProjectAnalyzer, AnalysisResult, ProjectType, TechnologyStack
from .workflow_template_engine import WorkflowTemplateEngine, Task, Phase, WorkflowTemplate
from .advanced_gap_analyzer import AdvancedGapAnalyzer, GapAnalysis
from .code_quality_analyzer import CodeQualityAnalyzer, TechnicalDebt, QualityReport

@dataclass
class GeneratedTask:
    id: str
    title: str
    description: str
    category: str  # setup, development, testing, deployment, maintenance
    priority: str  # high, medium, low
    estimated_hours: int
    dependencies: List[str]
    files_involved: List[str]
    agent_specialization: str
    confidence: float  # How confident we are this task is needed
    reasoning: str  # Why this task was generated
    acceptance_criteria: List[str]
    tags: List[str]

@dataclass
class TaskGenerationReport:
    total_tasks_generated: int
    tasks_by_category: Dict[str, int]
    high_confidence_tasks: int
    detected_gaps: List[str]
    recommendations: List[str]
    generation_timestamp: str

class AutoTaskGenerator:
    def __init__(self):
        self.analyzer = ProjectAnalyzer()
        self.workflow_engine = WorkflowTemplateEngine()
        self.advanced_gap_analyzer = AdvancedGapAnalyzer()
        self.code_quality_analyzer = CodeQualityAnalyzer()
        self.file_analyzers = self._setup_file_analyzers()
        self.pattern_matchers = self._setup_pattern_matchers()
        self.gap_detectors = self._setup_gap_detectors()

    def _setup_file_analyzers(self) -> Dict[str, Any]:
        """Set up file-specific analyzers for different file types"""
        return {
            "package_json": self._analyze_package_json,
            "requirements_txt": self._analyze_requirements_txt,
            "dockerfile": self._analyze_dockerfile,
            "docker_compose": self._analyze_docker_compose,
            "github_actions": self._analyze_github_actions,
            "makefile": self._analyze_makefile,
            "readme": self._analyze_readme,
            "api_files": self._analyze_api_files,
            "test_files": self._analyze_test_files,
            "config_files": self._analyze_config_files,
            "database_files": self._analyze_database_files
        }

    def _setup_pattern_matchers(self) -> Dict[str, Any]:
        """Set up pattern matchers for detecting common development patterns"""
        return {
            "missing_tests": self._detect_missing_tests,
            "missing_docs": self._detect_missing_documentation,
            "missing_ci_cd": self._detect_missing_ci_cd,
            "security_gaps": self._detect_security_gaps,
            "performance_issues": self._detect_performance_issues,
            "code_quality_issues": self._detect_code_quality_issues,
            "dependency_issues": self._detect_dependency_issues,
            "deployment_gaps": self._detect_deployment_gaps,
            "monitoring_gaps": self._detect_monitoring_gaps,
            "accessibility_gaps": self._detect_accessibility_gaps
        }

    def _setup_gap_detectors(self) -> Dict[str, Any]:
        """Set up detectors for common development gaps"""
        return {
            "setup_gaps": [
                "No .gitignore file",
                "No README.md file", 
                "No license file",
                "No contribution guidelines"
            ],
            "testing_gaps": [
                "No test directory",
                "No test configuration",
                "No test coverage setup",
                "No integration tests"
            ],
            "deployment_gaps": [
                "No Dockerfile",
                "No CI/CD configuration",
                "No deployment scripts",
                "No environment configuration"
            ],
            "documentation_gaps": [
                "No API documentation",
                "No code comments",
                "No architecture documentation",
                "No setup instructions"
            ],
            "security_gaps": [
                "No dependency scanning",
                "No security headers",
                "No authentication",
                "No input validation"
            ]
        }

    def generate_tasks_from_project(self, project_path: str, 
                                  exclude_existing: bool = True) -> Tuple[List[GeneratedTask], TaskGenerationReport]:
        """Generate tasks automatically based on project analysis"""
        project_path = Path(project_path).resolve()
        
        # Analyze project structure
        analysis = self.analyzer.analyze_project(str(project_path))
        
        # Get file list
        file_list = self._scan_project_files(project_path)
        
        # Generate tasks from different sources
        generated_tasks = []
        
        # 1. Generate tasks from file analysis
        file_tasks = self._generate_tasks_from_files(project_path, file_list, analysis)
        generated_tasks.extend(file_tasks)
        
        # 2. Generate tasks from pattern detection
        pattern_tasks = self._generate_tasks_from_patterns(project_path, file_list, analysis)
        generated_tasks.extend(pattern_tasks)
        
        # 3. Generate tasks from basic gap detection
        gap_tasks = self._generate_tasks_from_gaps(project_path, file_list, analysis)
        generated_tasks.extend(gap_tasks)
        
        # 3b. Generate tasks from advanced gap analysis
        advanced_gap_tasks = self._generate_tasks_from_advanced_gaps(project_path, analysis)
        generated_tasks.extend(advanced_gap_tasks)
        
        # 3c. Generate tasks from code quality analysis
        code_quality_tasks = self._generate_tasks_from_code_quality(project_path, analysis)
        generated_tasks.extend(code_quality_tasks)
        
        # 4. Generate tasks from workflow templates
        template_tasks = self._generate_tasks_from_templates(analysis)
        generated_tasks.extend(template_tasks)
        
        # 5. Filter and prioritize tasks
        if exclude_existing:
            generated_tasks = self._filter_existing_tasks(generated_tasks, project_path)
        
        generated_tasks = self._prioritize_and_deduplicate_tasks(generated_tasks)
        
        # Generate report
        report = self._generate_report(generated_tasks, analysis)
        
        return generated_tasks, report

    def _scan_project_files(self, project_path: Path) -> List[str]:
        """Scan project directory and return list of all files"""
        files = []
        try:
            for root, dirs, filenames in os.walk(project_path):
                # Skip common ignored directories
                dirs[:] = [d for d in dirs if d not in {
                    '.git', 'node_modules', '__pycache__', '.pytest_cache',
                    'venv', 'env', '.env', 'dist', 'build', '.next',
                    'target', 'bin', 'obj'
                }]
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    relative_path = file_path.relative_to(project_path)
                    files.append(str(relative_path))
        except Exception as e:
            print(f"Warning: Error scanning project files: {e}")
        
        return files

    def _generate_tasks_from_files(self, project_path: Path, file_list: List[str], 
                                 analysis: AnalysisResult) -> List[GeneratedTask]:
        """Generate tasks based on analysis of specific files"""
        tasks = []
        
        # Analyze package.json
        if "package.json" in file_list:
            tasks.extend(self._analyze_package_json(project_path, analysis))
        
        # Analyze requirements.txt
        if "requirements.txt" in file_list:
            tasks.extend(self._analyze_requirements_txt(project_path, analysis))
        
        # Analyze Dockerfile
        if "Dockerfile" in file_list:
            tasks.extend(self._analyze_dockerfile(project_path, analysis))
        
        # Analyze docker-compose.yml
        docker_compose_files = [f for f in file_list if f.startswith("docker-compose")]
        if docker_compose_files:
            tasks.extend(self._analyze_docker_compose(project_path, analysis))
        
        # Analyze GitHub Actions
        github_workflows = [f for f in file_list if f.startswith(".github/workflows/")]
        if github_workflows:
            tasks.extend(self._analyze_github_actions(project_path, analysis))
        
        # Analyze Makefile
        if "Makefile" in file_list or "makefile" in file_list:
            tasks.extend(self._analyze_makefile(project_path, analysis))
        
        # Analyze README
        readme_files = [f for f in file_list if f.lower().startswith("readme")]
        if readme_files:
            tasks.extend(self._analyze_readme(project_path, analysis))
        
        # Analyze API files
        api_files = [f for f in file_list if "api" in f.lower() or "routes" in f.lower()]
        if api_files:
            tasks.extend(self._analyze_api_files(project_path, api_files, analysis))
        
        # Analyze test files
        test_files = [f for f in file_list if "test" in f.lower()]
        if test_files:
            tasks.extend(self._analyze_test_files(project_path, test_files, analysis))
        
        return tasks

    def _analyze_package_json(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze package.json and generate relevant tasks"""
        tasks = []
        package_json_path = project_path / "package.json"
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Check for missing scripts
            scripts = package_data.get('scripts', {})
            
            if 'test' not in scripts:
                tasks.append(GeneratedTask(
                    id="add_test_script",
                    title="Add Test Script to package.json",
                    description="Add a test script to package.json for running tests",
                    category="setup",
                    priority="medium",
                    estimated_hours=1,
                    dependencies=[],
                    files_involved=["package.json"],
                    agent_specialization="frontend",
                    confidence=0.8,
                    reasoning="No test script found in package.json",
                    acceptance_criteria=["Test script added to package.json", "Script runs without errors"],
                    tags=["testing", "setup", "npm"]
                ))
            
            if 'build' not in scripts:
                tasks.append(GeneratedTask(
                    id="add_build_script",
                    title="Add Build Script to package.json",
                    description="Add a build script for production builds",
                    category="setup",
                    priority="high",
                    estimated_hours=2,
                    dependencies=[],
                    files_involved=["package.json"],
                    agent_specialization="frontend",
                    confidence=0.9,
                    reasoning="No build script found in package.json",
                    acceptance_criteria=["Build script added", "Production build works correctly"],
                    tags=["build", "setup", "npm"]
                ))
            
            if 'start' not in scripts:
                tasks.append(GeneratedTask(
                    id="add_start_script",
                    title="Add Start Script to package.json",
                    description="Add a start script for running the application",
                    category="setup",
                    priority="high",
                    estimated_hours=1,
                    dependencies=[],
                    files_involved=["package.json"],
                    agent_specialization="frontend",
                    confidence=0.8,
                    reasoning="No start script found in package.json",
                    acceptance_criteria=["Start script added", "Application starts correctly"],
                    tags=["setup", "npm", "development"]
                ))
            
            # Check for outdated dependencies
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            if dependencies or dev_dependencies:
                tasks.append(GeneratedTask(
                    id="audit_dependencies",
                    title="Audit and Update Dependencies",
                    description="Check for outdated or vulnerable dependencies and update them",
                    category="maintenance",
                    priority="medium",
                    estimated_hours=4,
                    dependencies=[],
                    files_involved=["package.json", "package-lock.json"],
                    agent_specialization="fullstack",
                    confidence=0.7,
                    reasoning="Dependencies should be regularly audited for security and updates",
                    acceptance_criteria=["Dependencies audited", "Vulnerable packages updated", "Tests pass after updates"],
                    tags=["security", "dependencies", "maintenance"]
                ))
            
        except Exception as e:
            print(f"Warning: Could not analyze package.json: {e}")
        
        return tasks

    def _analyze_requirements_txt(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze requirements.txt and generate relevant tasks"""
        tasks = []
        requirements_path = project_path / "requirements.txt"
        
        try:
            with open(requirements_path, 'r') as f:
                requirements = f.read().strip()
            
            # Check if requirements are pinned
            unpinned_packages = []
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' not in line and '>=' not in line and '<=' not in line:
                        unpinned_packages.append(line)
            
            if unpinned_packages:
                tasks.append(GeneratedTask(
                    id="pin_requirements",
                    title="Pin Package Versions in requirements.txt",
                    description="Pin specific versions for all packages to ensure reproducible builds",
                    category="setup",
                    priority="medium",
                    estimated_hours=2,
                    dependencies=[],
                    files_involved=["requirements.txt"],
                    agent_specialization="backend",
                    confidence=0.7,
                    reasoning=f"Found {len(unpinned_packages)} unpinned packages",
                    acceptance_criteria=["All packages have pinned versions", "Application still works after pinning"],
                    tags=["dependencies", "reproducibility", "setup"]
                ))
            
            # Check for development requirements
            if not (project_path / "requirements-dev.txt").exists():
                tasks.append(GeneratedTask(
                    id="create_dev_requirements",
                    title="Create Development Requirements File",
                    description="Separate development dependencies into requirements-dev.txt",
                    category="setup",
                    priority="low",
                    estimated_hours=1,
                    dependencies=[],
                    files_involved=["requirements-dev.txt"],
                    agent_specialization="backend",
                    confidence=0.6,
                    reasoning="No separate development requirements file found",
                    acceptance_criteria=["Development requirements file created", "Development dependencies separated"],
                    tags=["dependencies", "development", "setup"]
                ))
            
            # Check for security scanning
            tasks.append(GeneratedTask(
                id="security_scan_python",
                title="Set Up Python Security Scanning",
                description="Add security scanning for Python dependencies (safety, bandit)",
                category="security",
                priority="medium",
                estimated_hours=3,
                dependencies=[],
                files_involved=["requirements.txt"],
                agent_specialization="security",
                confidence=0.8,
                reasoning="Python projects should include security scanning",
                acceptance_criteria=["Security scanning tools added", "No critical vulnerabilities found"],
                tags=["security", "scanning", "python"]
            ))
            
        except Exception as e:
            print(f"Warning: Could not analyze requirements.txt: {e}")
        
        return tasks

    def _analyze_dockerfile(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze Dockerfile and generate relevant tasks"""
        tasks = []
        dockerfile_path = project_path / "Dockerfile"
        
        try:
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
            
            # Check for multi-stage builds
            if dockerfile_content.count("FROM") == 1:
                tasks.append(GeneratedTask(
                    id="multistage_dockerfile",
                    title="Implement Multi-stage Docker Build",
                    description="Optimize Dockerfile with multi-stage builds to reduce image size",
                    category="deployment",
                    priority="medium",
                    estimated_hours=4,
                    dependencies=[],
                    files_involved=["Dockerfile"],
                    agent_specialization="devops",
                    confidence=0.7,
                    reasoning="Single-stage build found, multi-stage could reduce image size",
                    acceptance_criteria=["Multi-stage build implemented", "Image size reduced", "Application still works"],
                    tags=["docker", "optimization", "deployment"]
                ))
            
            # Check for health checks
            if "HEALTHCHECK" not in dockerfile_content:
                tasks.append(GeneratedTask(
                    id="docker_healthcheck",
                    title="Add Docker Health Check",
                    description="Add health check to Dockerfile for better container monitoring",
                    category="deployment",
                    priority="medium",
                    estimated_hours=2,
                    dependencies=[],
                    files_involved=["Dockerfile"],
                    agent_specialization="devops",
                    confidence=0.8,
                    reasoning="No health check found in Dockerfile",
                    acceptance_criteria=["Health check added to Dockerfile", "Health check working correctly"],
                    tags=["docker", "monitoring", "health"]
                ))
            
            # Check for non-root user
            if "USER" not in dockerfile_content:
                tasks.append(GeneratedTask(
                    id="docker_nonroot_user",
                    title="Add Non-root User to Dockerfile",
                    description="Run container as non-root user for better security",
                    category="security",
                    priority="high",
                    estimated_hours=2,
                    dependencies=[],
                    files_involved=["Dockerfile"],
                    agent_specialization="security",
                    confidence=0.9,
                    reasoning="Container runs as root, which is a security risk",
                    acceptance_criteria=["Non-root user added", "Application works with non-root user"],
                    tags=["docker", "security", "user"]
                ))
            
        except Exception as e:
            print(f"Warning: Could not analyze Dockerfile: {e}")
        
        return tasks

    def _analyze_docker_compose(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze docker-compose.yml and generate relevant tasks"""
        tasks = []
        
        # Check for environment variables
        tasks.append(GeneratedTask(
            id="docker_compose_env",
            title="Add Environment Configuration to Docker Compose",
            description="Ensure proper environment variable configuration in docker-compose.yml",
            category="deployment",
            priority="medium",
            estimated_hours=2,
            dependencies=[],
            files_involved=["docker-compose.yml"],
            agent_specialization="devops",
            confidence=0.7,
            reasoning="Docker Compose should have proper environment configuration",
            acceptance_criteria=["Environment variables properly configured", "Services start correctly"],
            tags=["docker", "environment", "configuration"]
        ))
        
        # Check for volumes
        tasks.append(GeneratedTask(
            id="docker_compose_volumes",
            title="Configure Persistent Volumes in Docker Compose",
            description="Set up persistent volumes for data that should survive container restarts",
            category="deployment",
            priority="medium",
            estimated_hours=3,
            dependencies=[],
            files_involved=["docker-compose.yml"],
            agent_specialization="devops",
            confidence=0.6,
            reasoning="Persistent volumes important for data persistence",
            acceptance_criteria=["Volumes configured for persistent data", "Data persists across restarts"],
            tags=["docker", "volumes", "persistence"]
        ))
        
        return tasks

    def _analyze_github_actions(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze GitHub Actions workflows and generate relevant tasks"""
        tasks = []
        
        # Check for test workflow
        workflow_files = list((project_path / ".github" / "workflows").glob("*.yml"))
        has_test_workflow = any("test" in f.name.lower() for f in workflow_files)
        
        if not has_test_workflow:
            tasks.append(GeneratedTask(
                id="github_test_workflow",
                title="Add GitHub Actions Test Workflow",
                description="Create automated testing workflow for GitHub Actions",
                category="ci_cd",
                priority="high",
                estimated_hours=4,
                dependencies=[],
                files_involved=[".github/workflows/test.yml"],
                agent_specialization="devops",
                confidence=0.9,
                reasoning="No test workflow found in GitHub Actions",
                acceptance_criteria=["Test workflow created", "Tests run on pull requests", "Tests pass"],
                tags=["ci", "testing", "github-actions"]
            ))
        
        # Check for deployment workflow
        has_deploy_workflow = any("deploy" in f.name.lower() or "release" in f.name.lower() 
                                for f in workflow_files)
        
        if not has_deploy_workflow:
            tasks.append(GeneratedTask(
                id="github_deploy_workflow",
                title="Add GitHub Actions Deployment Workflow",
                description="Create automated deployment workflow for releases",
                category="ci_cd",
                priority="medium",
                estimated_hours=6,
                dependencies=["github_test_workflow"],
                files_involved=[".github/workflows/deploy.yml"],
                agent_specialization="devops",
                confidence=0.7,
                reasoning="No deployment workflow found in GitHub Actions",
                acceptance_criteria=["Deployment workflow created", "Automatic deployment on releases"],
                tags=["cd", "deployment", "github-actions"]
            ))
        
        return tasks

    def _analyze_makefile(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze Makefile and generate relevant tasks"""
        tasks = []
        
        makefile_path = project_path / "Makefile"
        if not makefile_path.exists():
            makefile_path = project_path / "makefile"
        
        try:
            with open(makefile_path, 'r') as f:
                makefile_content = f.read()
            
            # Check for common targets
            common_targets = ["test", "build", "clean", "install", "deploy"]
            missing_targets = []
            
            for target in common_targets:
                if f"{target}:" not in makefile_content:
                    missing_targets.append(target)
            
            if missing_targets:
                tasks.append(GeneratedTask(
                    id="makefile_targets",
                    title="Add Missing Makefile Targets",
                    description=f"Add missing common targets to Makefile: {', '.join(missing_targets)}",
                    category="setup",
                    priority="medium",
                    estimated_hours=3,
                    dependencies=[],
                    files_involved=["Makefile"],
                    agent_specialization="devops",
                    confidence=0.6,
                    reasoning=f"Common targets missing: {', '.join(missing_targets)}",
                    acceptance_criteria=["Missing targets added", "All targets work correctly"],
                    tags=["makefile", "automation", "setup"]
                ))
                
        except Exception as e:
            print(f"Warning: Could not analyze Makefile: {e}")
        
        return tasks

    def _analyze_readme(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze README file and generate relevant tasks"""
        tasks = []
        
        readme_files = list(project_path.glob("README*"))
        if not readme_files:
            tasks.append(GeneratedTask(
                id="create_readme",
                title="Create README.md File",
                description="Create comprehensive README.md with project documentation",
                category="documentation",
                priority="high",
                estimated_hours=4,
                dependencies=[],
                files_involved=["README.md"],
                agent_specialization="fullstack",
                confidence=0.9,
                reasoning="No README file found",
                acceptance_criteria=["README.md created", "Installation instructions included", "Usage examples provided"],
                tags=["documentation", "readme", "setup"]
            ))
        else:
            # Analyze existing README
            readme_path = readme_files[0]
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read().lower()
                
                sections_to_check = {
                    "installation": ["install", "setup", "getting started"],
                    "usage": ["usage", "example", "how to"],
                    "contributing": ["contribut", "development"],
                    "license": ["license", "copyright"],
                    "testing": ["test", "testing"]
                }
                
                missing_sections = []
                for section, keywords in sections_to_check.items():
                    if not any(keyword in readme_content for keyword in keywords):
                        missing_sections.append(section)
                
                if missing_sections:
                    tasks.append(GeneratedTask(
                        id="improve_readme",
                        title="Improve README Documentation",
                        description=f"Add missing sections to README: {', '.join(missing_sections)}",
                        category="documentation",
                        priority="medium",
                        estimated_hours=3,
                        dependencies=[],
                        files_involved=[readme_path.name],
                        agent_specialization="fullstack",
                        confidence=0.7,
                        reasoning=f"README missing sections: {', '.join(missing_sections)}",
                        acceptance_criteria=["Missing sections added", "Documentation is comprehensive"],
                        tags=["documentation", "readme", "improvement"]
                    ))
                    
            except Exception as e:
                print(f"Warning: Could not analyze README: {e}")
        
        return tasks

    def _analyze_api_files(self, project_path: Path, api_files: List[str], 
                          analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze API files and generate relevant tasks"""
        tasks = []
        
        # Check for API documentation
        has_api_docs = any("swagger" in f.lower() or "openapi" in f.lower() 
                          for f in api_files)
        
        if not has_api_docs:
            tasks.append(GeneratedTask(
                id="api_documentation",
                title="Add API Documentation",
                description="Create comprehensive API documentation (OpenAPI/Swagger)",
                category="documentation",
                priority="high",
                estimated_hours=8,
                dependencies=[],
                files_involved=api_files,
                agent_specialization="backend",
                confidence=0.8,
                reasoning="API endpoints found but no documentation",
                acceptance_criteria=["API documentation created", "All endpoints documented", "Examples provided"],
                tags=["api", "documentation", "swagger"]
            ))
        
        # Check for API testing
        api_test_files = [f for f in api_files if "test" in f.lower()]
        if not api_test_files:
            tasks.append(GeneratedTask(
                id="api_testing",
                title="Add API Integration Tests",
                description="Create comprehensive integration tests for API endpoints",
                category="testing",
                priority="high",
                estimated_hours=12,
                dependencies=[],
                files_involved=api_files,
                agent_specialization="backend",
                confidence=0.9,
                reasoning="API endpoints found but no tests",
                acceptance_criteria=["Integration tests created", "All endpoints tested", "Error cases covered"],
                tags=["api", "testing", "integration"]
            ))
        
        # Check for API validation
        tasks.append(GeneratedTask(
            id="api_validation",
            title="Add API Input Validation",
            description="Implement comprehensive input validation for API endpoints",
            category="security",
            priority="high",
            estimated_hours=6,
            dependencies=[],
            files_involved=api_files,
            agent_specialization="backend",
            confidence=0.8,
            reasoning="Input validation is critical for API security",
            acceptance_criteria=["Input validation implemented", "Invalid inputs rejected", "Error messages are helpful"],
            tags=["api", "validation", "security"]
        ))
        
        return tasks

    def _analyze_test_files(self, project_path: Path, test_files: List[str], 
                           analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze test files and generate relevant tasks"""
        tasks = []
        
        # Check test coverage
        if test_files:
            tasks.append(GeneratedTask(
                id="test_coverage",
                title="Set Up Test Coverage Reporting",
                description="Add test coverage reporting and set minimum coverage thresholds",
                category="testing",
                priority="medium",
                estimated_hours=4,
                dependencies=[],
                files_involved=test_files,
                agent_specialization="fullstack",
                confidence=0.7,
                reasoning="Tests exist but coverage reporting should be added",
                acceptance_criteria=["Coverage reporting configured", "Minimum coverage threshold set", "Coverage reports generated"],
                tags=["testing", "coverage", "quality"]
            ))
        
        # Check for different types of tests
        test_types = {
            "unit": any("unit" in f.lower() for f in test_files),
            "integration": any("integration" in f.lower() for f in test_files),
            "e2e": any("e2e" in f.lower() or "end-to-end" in f.lower() or "selenium" in f.lower() for f in test_files)
        }
        
        for test_type, exists in test_types.items():
            if not exists:
                tasks.append(GeneratedTask(
                    id=f"add_{test_type}_tests",
                    title=f"Add {test_type.title()} Tests",
                    description=f"Create comprehensive {test_type} tests for the application",
                    category="testing",
                    priority="medium" if test_type != "unit" else "high",
                    estimated_hours=8 if test_type == "unit" else 12,
                    dependencies=[],
                    files_involved=test_files,
                    agent_specialization="fullstack",
                    confidence=0.8,
                    reasoning=f"No {test_type} tests found",
                    acceptance_criteria=[f"{test_type.title()} tests created", "Tests pass consistently", "Good test coverage"],
                    tags=["testing", test_type, "quality"]
                ))
        
        return tasks

    def _generate_tasks_from_patterns(self, project_path: Path, file_list: List[str], 
                                    analysis: AnalysisResult) -> List[GeneratedTask]:
        """Generate tasks based on detected patterns and anti-patterns"""
        tasks = []
        
        for pattern_name, detector in self.pattern_matchers.items():
            detected_issues = detector(project_path, file_list, analysis)
            tasks.extend(detected_issues)
        
        return tasks

    def _detect_missing_tests(self, project_path: Path, file_list: List[str], 
                            analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect missing test coverage"""
        tasks = []
        
        # Count source files vs test files
        source_files = [f for f in file_list if f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx'))]
        test_files = [f for f in file_list if 'test' in f.lower()]
        
        test_ratio = len(test_files) / len(source_files) if source_files else 0
        
        if test_ratio < 0.3:  # Less than 30% test coverage by file count
            tasks.append(GeneratedTask(
                id="increase_test_coverage",
                title="Increase Test Coverage",
                description="Add more tests to improve overall test coverage",
                category="testing",
                priority="high",
                estimated_hours=16,
                dependencies=[],
                files_involved=source_files[:10],  # Limit to first 10 files
                agent_specialization="fullstack",
                confidence=0.9,
                reasoning=f"Test ratio is {test_ratio:.2f}, should be at least 0.3",
                acceptance_criteria=["Test coverage increased", "Critical paths tested", "Test ratio improved"],
                tags=["testing", "coverage", "quality"]
            ))
        
        return tasks

    def _detect_missing_documentation(self, project_path: Path, file_list: List[str], 
                                    analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect missing documentation"""
        tasks = []
        
        # Check for docs directory
        has_docs_dir = any(f.startswith('docs/') for f in file_list)
        
        if not has_docs_dir and analysis.estimated_complexity in ['medium', 'high']:
            tasks.append(GeneratedTask(
                id="create_docs_directory",
                title="Create Documentation Directory",
                description="Set up documentation structure with architecture and API docs",
                category="documentation",
                priority="medium",
                estimated_hours=6,
                dependencies=[],
                files_involved=["docs/"],
                agent_specialization="fullstack",
                confidence=0.7,
                reasoning="Medium/high complexity project needs dedicated documentation",
                acceptance_criteria=["Docs directory created", "Architecture documented", "Setup guide created"],
                tags=["documentation", "architecture", "setup"]
            ))
        
        return tasks

    def _detect_missing_ci_cd(self, project_path: Path, file_list: List[str], 
                            analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect missing CI/CD configuration"""
        tasks = []
        
        ci_cd_files = [f for f in file_list if any(pattern in f.lower() for pattern in [
            '.github/workflows', '.gitlab-ci', 'jenkinsfile', '.circleci', '.travis'
        ])]
        
        if not ci_cd_files:
            tasks.append(GeneratedTask(
                id="setup_ci_cd",
                title="Set Up CI/CD Pipeline",
                description="Configure continuous integration and deployment pipeline",
                category="ci_cd",
                priority="high",
                estimated_hours=8,
                dependencies=[],
                files_involved=[".github/workflows/ci.yml"],
                agent_specialization="devops",
                confidence=0.8,
                reasoning="No CI/CD configuration found",
                acceptance_criteria=["CI/CD pipeline configured", "Automated testing on PRs", "Deployment automation ready"],
                tags=["ci", "cd", "automation", "devops"]
            ))
        
        return tasks

    def _detect_security_gaps(self, project_path: Path, file_list: List[str], 
                            analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect security-related gaps"""
        tasks = []
        
        # Check for security scanning
        has_security_config = any(pattern in ' '.join(file_list).lower() for pattern in [
            'security', 'bandit', 'eslint-plugin-security', 'snyk', 'safety'
        ])
        
        if not has_security_config:
            tasks.append(GeneratedTask(
                id="security_scanning",
                title="Set Up Security Scanning",
                description="Add automated security scanning for dependencies and code",
                category="security",
                priority="high",
                estimated_hours=4,
                dependencies=[],
                files_involved=[".github/workflows/security.yml"],
                agent_specialization="security",
                confidence=0.9,
                reasoning="No security scanning configuration found",
                acceptance_criteria=["Security scanning configured", "Vulnerability alerts enabled", "Regular security audits"],
                tags=["security", "scanning", "automation"]
            ))
        
        # Check for authentication
        if analysis.structure.has_api and not any('auth' in f.lower() for f in file_list):
            tasks.append(GeneratedTask(
                id="implement_authentication",
                title="Implement Authentication System",
                description="Add user authentication and authorization to the API",
                category="security",
                priority="high",
                estimated_hours=12,
                dependencies=[],
                files_involved=["auth/"],
                agent_specialization="security",
                confidence=0.8,
                reasoning="API detected but no authentication system found",
                acceptance_criteria=["Authentication system implemented", "JWT tokens working", "Protected endpoints secured"],
                tags=["security", "authentication", "api"]
            ))
        
        return tasks

    def _detect_performance_issues(self, project_path: Path, file_list: List[str], 
                                 analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect potential performance issues"""
        tasks = []
        
        # Check for performance monitoring
        has_monitoring = any(pattern in ' '.join(file_list).lower() for pattern in [
            'monitoring', 'metrics', 'prometheus', 'grafana', 'newrelic'
        ])
        
        if not has_monitoring and analysis.project_type in [ProjectType.WEB_APP, ProjectType.API_SERVICE]:
            tasks.append(GeneratedTask(
                id="performance_monitoring",
                title="Add Performance Monitoring",
                description="Set up performance monitoring and metrics collection",
                category="monitoring",
                priority="medium",
                estimated_hours=6,
                dependencies=[],
                files_involved=["monitoring/"],
                agent_specialization="devops",
                confidence=0.7,
                reasoning="Web/API application should have performance monitoring",
                acceptance_criteria=["Performance monitoring configured", "Key metrics tracked", "Alerting set up"],
                tags=["monitoring", "performance", "metrics"]
            ))
        
        return tasks

    def _detect_code_quality_issues(self, project_path: Path, file_list: List[str], 
                                   analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect code quality issues"""
        tasks = []
        
        # Check for linting configuration
        linting_configs = [f for f in file_list if any(pattern in f.lower() for pattern in [
            '.eslintrc', 'pylint', '.flake8', 'mypy.ini', 'tslint.json'
        ])]
        
        if not linting_configs:
            tasks.append(GeneratedTask(
                id="setup_linting",
                title="Set Up Code Linting",
                description="Configure code linting and formatting tools",
                category="quality",
                priority="medium",
                estimated_hours=3,
                dependencies=[],
                files_involved=[".eslintrc.js"],
                agent_specialization="fullstack",
                confidence=0.8,
                reasoning="No linting configuration found",
                acceptance_criteria=["Linting configured", "Code style consistent", "Pre-commit hooks set up"],
                tags=["quality", "linting", "formatting"]
            ))
        
        return tasks

    def _detect_dependency_issues(self, project_path: Path, file_list: List[str], 
                                 analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect dependency management issues"""
        tasks = []
        
        # Check for dependency management
        package_files = [f for f in file_list if f in [
            'package.json', 'requirements.txt', 'Pipfile', 'poetry.lock', 'composer.json'
        ]]
        
        if package_files:
            tasks.append(GeneratedTask(
                id="dependency_audit",
                title="Regular Dependency Auditing",
                description="Set up automated dependency auditing and updates",
                category="maintenance",
                priority="medium",
                estimated_hours=2,
                dependencies=[],
                files_involved=package_files,
                agent_specialization="devops",
                confidence=0.6,
                reasoning="Dependencies should be regularly audited",
                acceptance_criteria=["Dependency auditing configured", "Automated updates set up", "Security alerts enabled"],
                tags=["dependencies", "security", "maintenance"]
            ))
        
        return tasks

    def _detect_deployment_gaps(self, project_path: Path, file_list: List[str], 
                               analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect deployment-related gaps"""
        tasks = []
        
        # Check for environment configuration
        env_files = [f for f in file_list if '.env' in f or 'config' in f.lower()]
        
        if not env_files:
            tasks.append(GeneratedTask(
                id="environment_config",
                title="Set Up Environment Configuration",
                description="Create environment-specific configuration files",
                category="deployment",
                priority="medium",
                estimated_hours=3,
                dependencies=[],
                files_involved=[".env.example"],
                agent_specialization="devops",
                confidence=0.7,
                reasoning="No environment configuration files found",
                acceptance_criteria=["Environment config created", "Different environments supported", "Secrets properly managed"],
                tags=["deployment", "configuration", "environment"]
            ))
        
        return tasks

    def _detect_monitoring_gaps(self, project_path: Path, file_list: List[str], 
                               analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect monitoring and observability gaps"""
        tasks = []
        
        # Check for logging configuration
        has_logging = any(pattern in ' '.join(file_list).lower() for pattern in [
            'logging', 'logger', 'log4j', 'winston'
        ])
        
        if not has_logging:
            tasks.append(GeneratedTask(
                id="setup_logging",
                title="Set Up Structured Logging",
                description="Implement structured logging throughout the application",
                category="monitoring",
                priority="medium",
                estimated_hours=4,
                dependencies=[],
                files_involved=["logging/"],
                agent_specialization="fullstack",
                confidence=0.7,
                reasoning="No logging configuration found",
                acceptance_criteria=["Structured logging implemented", "Log levels configured", "Log rotation set up"],
                tags=["monitoring", "logging", "observability"]
            ))
        
        return tasks

    def _detect_accessibility_gaps(self, project_path: Path, file_list: List[str], 
                                  analysis: AnalysisResult) -> List[GeneratedTask]:
        """Detect accessibility issues"""
        tasks = []
        
        if analysis.structure.has_frontend:
            # Check for accessibility testing
            has_a11y_tests = any(pattern in ' '.join(file_list).lower() for pattern in [
                'accessibility', 'a11y', 'axe', 'lighthouse'
            ])
            
            if not has_a11y_tests:
                tasks.append(GeneratedTask(
                    id="accessibility_testing",
                    title="Add Accessibility Testing",
                    description="Implement automated accessibility testing and audits",
                    category="testing",
                    priority="medium",
                    estimated_hours=6,
                    dependencies=[],
                    files_involved=["tests/accessibility/"],
                    agent_specialization="frontend",
                    confidence=0.6,
                    reasoning="Frontend application should include accessibility testing",
                    acceptance_criteria=["Accessibility tests added", "WCAG compliance checked", "Automated audits configured"],
                    tags=["accessibility", "testing", "frontend"]
                ))
        
        return tasks

    def _generate_tasks_from_gaps(self, project_path: Path, file_list: List[str], 
                                analysis: AnalysisResult) -> List[GeneratedTask]:
        """Generate tasks based on detected gaps in project structure"""
        tasks = []
        
        for gap_category, gap_indicators in self.gap_detectors.items():
            for indicator in gap_indicators:
                if self._check_gap_exists(indicator, file_list, project_path):
                    task = self._create_gap_task(indicator, gap_category)
                    if task:
                        tasks.append(task)
        
        return tasks

    def _check_gap_exists(self, indicator: str, file_list: List[str], project_path: Path) -> bool:
        """Check if a specific gap exists in the project"""
        if indicator == "No .gitignore file":
            return ".gitignore" not in file_list
        elif indicator == "No README.md file":
            return not any(f.lower().startswith("readme") for f in file_list)
        elif indicator == "No license file":
            return not any("license" in f.lower() for f in file_list)
        elif indicator == "No test directory":
            return not any("test" in f.lower() for f in file_list)
        elif indicator == "No Dockerfile":
            return "Dockerfile" not in file_list
        elif indicator == "No CI/CD configuration":
            return not any(ci_pattern in f.lower() for f in file_list for ci_pattern in [
                '.github/workflows', '.gitlab-ci', 'jenkinsfile'
            ])
        # Add more gap checks as needed
        return False

    def _create_gap_task(self, indicator: str, category: str) -> Optional[GeneratedTask]:
        """Create a task to address a detected gap"""
        gap_tasks = {
            "No .gitignore file": GeneratedTask(
                id="create_gitignore",
                title="Create .gitignore File",
                description="Add appropriate .gitignore file for the project type",
                category="setup",
                priority="medium",
                estimated_hours=1,
                dependencies=[],
                files_involved=[".gitignore"],
                agent_specialization="fullstack",
                confidence=0.9,
                reasoning="Project should have .gitignore to exclude unnecessary files",
                acceptance_criteria=[".gitignore created", "Common files excluded", "Language-specific patterns included"],
                tags=["setup", "git", "configuration"]
            ),
            "No license file": GeneratedTask(
                id="add_license",
                title="Add License File",
                description="Choose and add appropriate license for the project",
                category="documentation",
                priority="low",
                estimated_hours=1,
                dependencies=[],
                files_involved=["LICENSE"],
                agent_specialization="fullstack",
                confidence=0.6,
                reasoning="Open source projects should have a license",
                acceptance_criteria=["License file added", "Appropriate license chosen", "License referenced in README"],
                tags=["documentation", "legal", "license"]
            )
        }
        
        return gap_tasks.get(indicator)

    def _generate_tasks_from_templates(self, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Generate tasks from workflow templates"""
        tasks = []
        
        # Get appropriate workflow template
        workflow_template = self.workflow_engine.generate_workflow_from_analysis(analysis)
        
        # Convert template tasks to generated tasks
        for phase in workflow_template.phases:
            for template_task in phase.tasks:
                generated_task = GeneratedTask(
                    id=f"template_{template_task.id}",
                    title=template_task.title,
                    description=template_task.description,
                    category=phase.name.lower().replace(' ', '_'),
                    priority=template_task.priority,
                    estimated_hours=template_task.estimated_hours,
                    dependencies=[f"template_{dep}" for dep in template_task.dependencies],
                    files_involved=[],  # Template tasks don't specify files
                    agent_specialization=template_task.agent_specialization,
                    confidence=0.8,  # Template tasks have high confidence
                    reasoning=f"Task from {workflow_template.name} template",
                    acceptance_criteria=template_task.acceptance_criteria,
                    tags=template_task.tags
                )
                tasks.append(generated_task)
        
        return tasks

    def _filter_existing_tasks(self, tasks: List[GeneratedTask], project_path: Path) -> List[GeneratedTask]:
        """Filter out tasks that seem to already be completed"""
        filtered_tasks = []
        
        for task in tasks:
            if not self._task_appears_complete(task, project_path):
                filtered_tasks.append(task)
        
        return filtered_tasks

    def _task_appears_complete(self, task: GeneratedTask, project_path: Path) -> bool:
        """Check if a task appears to already be completed"""
        # Simple heuristics - could be made more sophisticated
        
        if task.id == "create_readme" and (project_path / "README.md").exists():
            return True
        
        if task.id == "create_gitignore" and (project_path / ".gitignore").exists():
            return True
        
        if task.id == "add_license" and any((project_path / f).exists() for f in ["LICENSE", "LICENSE.txt", "LICENSE.md"]):
            return True
        
        if "dockerfile" in task.id.lower() and (project_path / "Dockerfile").exists():
            return True
        
        # Add more completion checks as needed
        return False

    def _prioritize_and_deduplicate_tasks(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """Prioritize tasks and remove duplicates"""
        # Remove duplicates based on ID
        seen_ids = set()
        deduplicated = []
        
        for task in tasks:
            if task.id not in seen_ids:
                deduplicated.append(task)
                seen_ids.add(task.id)
        
        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        return sorted(deduplicated, key=lambda t: (
            priority_order.get(t.priority, 0),
            t.confidence,
            -t.estimated_hours  # Prefer shorter tasks when priority/confidence are equal
        ), reverse=True)

    def _generate_tasks_from_advanced_gaps(self, project_path: str, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Generate tasks from advanced gap analysis with sophisticated dependency mapping"""
        tasks = []
        
        try:
            # Perform comprehensive gap analysis
            gaps, dependency_map = self.advanced_gap_analyzer.analyze_comprehensive_gaps(project_path, analysis)
            
            # Convert gap analysis to generated tasks
            for gap in gaps:
                # Create tasks for each gap's dependencies
                for i, dependency in enumerate(gap.dependencies):
                    task_id = f"{gap.category}_{dependency}_{i}"
                    
                    # Map severity to priority
                    priority_mapping = {
                        "critical": "high",
                        "high": "high", 
                        "medium": "medium",
                        "low": "low"
                    }
                    
                    # Estimate hours based on remediation effort
                    try:
                        if '-' in gap.remediation_effort:
                            min_hours, max_hours = map(int, gap.remediation_effort.split('-'))
                            estimated_hours = (min_hours + max_hours) // 2
                        else:
                            estimated_hours = int(gap.remediation_effort)
                    except (ValueError, AttributeError):
                        estimated_hours = 8  # Default
                    
                    # Determine agent specialization based on category
                    specialization_mapping = {
                        "security": "security",
                        "testing": "backend",
                        "performance": "backend", 
                        "accessibility": "frontend",
                        "documentation": "technical_writer",
                        "deployment": "devops",
                        "architecture": "senior_developer",
                        "quality": "backend"
                    }
                    
                    # Create acceptance criteria from best practices
                    acceptance_criteria = gap.best_practices[:3] if gap.best_practices else [
                        f"Address {gap.description.lower()}",
                        "Verify implementation meets industry standards",
                        "Update documentation if needed"
                    ]
                    
                    # Create task with rich metadata from gap analysis
                    task = GeneratedTask(
                        id=task_id,
                        title=self._generate_task_title_from_gap(gap, dependency),
                        description=f"{gap.description}\n\nImpact: {gap.impact}\n\nBest Practices:\n" + 
                                  '\n'.join(f"- {bp}" for bp in gap.best_practices[:5]),
                        category=gap.category,
                        priority=priority_mapping.get(gap.severity, "medium"),
                        estimated_hours=estimated_hours,
                        dependencies=self._map_gap_dependencies(dependency, gaps, dependency_map),
                        files_involved=self._infer_files_from_gap(gap, dependency),
                        agent_specialization=specialization_mapping.get(gap.category, "backend"),
                        confidence=gap.confidence,
                        reasoning=f"Gap detected: {gap.gap_type} {gap.category} issue. Evidence: {'; '.join(gap.evidence[:3])}",
                        acceptance_criteria=acceptance_criteria,
                        tags=self._generate_tags_from_gap(gap)
                    )
                    
                    tasks.append(task)
            
            # Sort tasks by dependency order and priority
            tasks = self._sort_tasks_by_dependencies(tasks, dependency_map)
            
        except Exception as e:
            print(f"Warning: Advanced gap analysis failed: {e}")
            # Fall back to basic gap detection if advanced analysis fails
        
        return tasks

    def _generate_task_title_from_gap(self, gap: GapAnalysis, dependency: str) -> str:
        """Generate a clear task title from gap analysis"""
        # Convert dependency ID to human-readable title
        title_mapping = {
            "setup_dependency_scanning": "Set Up Dependency Vulnerability Scanning",
            "remove_secrets_from_code": "Remove Hardcoded Secrets from Codebase",
            "implement_authentication": "Implement User Authentication System",
            "implement_input_validation": "Add Input Validation and Sanitization",
            "increase_test_coverage": "Increase Automated Test Coverage",
            "setup_unit_testing": "Set Up Unit Testing Framework",
            "setup_integration_testing": "Configure Integration Test Suite",
            "setup_performance_monitoring": "Implement Performance Monitoring",
            "create_readme": "Create Comprehensive README Documentation",
            "create_api_documentation": "Create API Documentation",
            "setup_containerization": "Set Up Docker Containerization",
            "setup_ci_cd_pipeline": "Configure CI/CD Pipeline",
            "setup_monitoring": "Set Up Application Monitoring",
            "setup_code_linting": "Configure Code Linting and Formatting",
            "setup_accessibility_testing": "Set Up Accessibility Testing",
            "refactor_complex_code": "Refactor High-Complexity Code Areas"
        }
        
        return title_mapping.get(dependency, dependency.replace('_', ' ').title())

    def _map_gap_dependencies(self, dependency: str, gaps: List[GapAnalysis], 
                             dependency_map: List) -> List[str]:
        """Map gap dependencies to task dependencies"""
        # Find dependency mapping for this task
        for dep_map in dependency_map:
            if dep_map.task_id == dependency:
                return dep_map.depends_on
        return []

    def _infer_files_from_gap(self, gap: GapAnalysis, dependency: str) -> List[str]:
        """Infer which files might be involved in addressing the gap"""
        file_mappings = {
            "setup_dependency_scanning": [".github/workflows/security.yml", "requirements.txt", "package.json"],
            "remove_secrets_from_code": ["config/", ".env.example"],
            "implement_authentication": ["auth/", "middleware/", "models/user.py"],
            "setup_unit_testing": ["tests/", "pytest.ini", "jest.config.js"],
            "create_readme": ["README.md"],
            "setup_containerization": ["Dockerfile", "docker-compose.yml"],
            "setup_ci_cd_pipeline": [".github/workflows/", ".gitlab-ci.yml"],
            "setup_code_linting": [".eslintrc.js", ".flake8", "pyproject.toml"]
        }
        
        return file_mappings.get(dependency, [])

    def _generate_tags_from_gap(self, gap: GapAnalysis) -> List[str]:
        """Generate relevant tags from gap analysis"""
        tags = [gap.category, gap.severity, gap.gap_type]
        
        # Add specific tags based on category
        category_tags = {
            "security": ["vulnerability", "compliance"],
            "testing": ["quality", "automation"],
            "performance": ["optimization", "monitoring"],
            "accessibility": ["a11y", "compliance"],
            "documentation": ["docs", "onboarding"],
            "deployment": ["infrastructure", "automation"],
            "architecture": ["design", "maintainability"],
            "quality": ["code-quality", "maintainability"]
        }
        
        tags.extend(category_tags.get(gap.category, []))
        return list(set(tags))  # Remove duplicates

    def _sort_tasks_by_dependencies(self, tasks: List[GeneratedTask], 
                                   dependency_map: List) -> List[GeneratedTask]:
        """Sort tasks based on their dependency relationships"""
        # Create a simple topological sort based on dependencies
        task_dict = {task.id: task for task in tasks}
        sorted_tasks = []
        visited = set()
        
        def visit(task_id: str):
            if task_id in visited or task_id not in task_dict:
                return
            
            visited.add(task_id)
            task = task_dict[task_id]
            
            # Visit dependencies first
            for dep_id in task.dependencies:
                visit(dep_id)
            
            sorted_tasks.append(task)
        
        # Visit all tasks
        for task in tasks:
            visit(task.id)
        
        return sorted_tasks

    def _generate_tasks_from_code_quality(self, project_path: str, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Generate tasks from code quality analysis and technical debt detection"""
        tasks = []
        
        try:
            # Perform code quality analysis
            technical_debts, quality_report = self.code_quality_analyzer.analyze_code_quality(project_path)
            
            # Only generate tasks if quality score is below threshold
            if quality_report.overall_score < 80:  # Threshold for "good" quality
                # Group technical debts by file and category for better task organization
                debt_by_file = {}
                for debt in technical_debts:
                    if debt.file_path not in debt_by_file:
                        debt_by_file[debt.file_path] = []
                    debt_by_file[debt.file_path].append(debt)
                
                # Create tasks for high-impact technical debt
                for file_path, file_debts in debt_by_file.items():
                    # Group by category to avoid too many small tasks
                    category_groups = {}
                    for debt in file_debts:
                        if debt.category not in category_groups:
                            category_groups[debt.category] = []
                        category_groups[debt.category].append(debt)
                    
                    # Create tasks for each category group
                    for category, debts in category_groups.items():
                        # Only create task if significant debt exists
                        if len(debts) >= 2 or any(d.severity in ['critical', 'high'] for d in debts):
                            total_hours = sum(d.estimated_hours for d in debts)
                            
                            # Determine priority based on severity
                            severity_priority = {
                                'critical': 'high',
                                'high': 'high',
                                'medium': 'medium',
                                'low': 'low'
                            }
                            highest_severity = max(debts, key=lambda d: ['low', 'medium', 'high', 'critical'].index(d.severity)).severity
                            
                            # Create aggregated task description
                            issues_summary = '\n'.join([f"- {d.description}" for d in debts[:5]])
                            if len(debts) > 5:
                                issues_summary += f"\n- ... and {len(debts) - 5} more issues"
                            
                            # Determine agent specialization
                            specialization_map = {
                                'complexity': 'backend',
                                'duplication': 'backend',
                                'standards': 'fullstack',
                                'architecture': 'senior_developer',
                                'test': 'backend'
                            }
                            
                            task = GeneratedTask(
                                id=f"code_quality_{category}_{file_path.replace('/', '_').replace('.', '_')}",
                                title=f"Refactor {category.title()} Issues in {Path(file_path).name}",
                                description=f"Address {len(debts)} {category} issues detected in {file_path}:\n\n{issues_summary}\n\nTotal estimated effort: {total_hours} hours",
                                category="code_quality",
                                priority=severity_priority.get(highest_severity, 'medium'),
                                estimated_hours=total_hours,
                                dependencies=[],
                                files_involved=[file_path],
                                agent_specialization=specialization_map.get(category, 'backend'),
                                confidence=0.8,
                                reasoning=f"Code quality analysis detected {len(debts)} {category} issues with {highest_severity} severity",
                                acceptance_criteria=[
                                    f"All {category} issues in {Path(file_path).name} resolved",
                                    "Code passes quality checks",
                                    "Tests still pass after refactoring",
                                    "No new issues introduced"
                                ],
                                tags=["refactoring", "technical-debt", category, "code-quality"]
                            )
                            
                            tasks.append(task)
                
                # Add overall quality improvement task if score is very low
                if quality_report.overall_score < 60:
                    tasks.append(GeneratedTask(
                        id="improve_overall_code_quality",
                        title="Comprehensive Code Quality Improvement Initiative",
                        description=f"Current code quality score: {quality_report.overall_score:.1f}/100\n\n" +
                                  f"Total technical debt: {quality_report.total_debt_hours} hours\n\n" +
                                  "Top recommendations:\n" + '\n'.join(f"- {rec}" for rec in quality_report.improvement_recommendations),
                        category="code_quality",
                        priority="high",
                        estimated_hours=40,
                        dependencies=[],
                        files_involved=quality_report.hotspot_files[:5],
                        agent_specialization="senior_developer",
                        confidence=0.9,
                        reasoning=f"Overall code quality score ({quality_report.overall_score:.1f}) is below acceptable threshold",
                        acceptance_criteria=[
                            "Code quality score improved to at least 70",
                            "Critical and high severity issues resolved",
                            "Coding standards enforced project-wide",
                            "Technical debt reduction plan implemented"
                        ],
                        tags=["refactoring", "technical-debt", "quality", "improvement"]
                    ))
                
                # Add specific tasks for top recommendations
                if quality_report.debt_by_severity.get('critical', 0) > 0:
                    tasks.append(GeneratedTask(
                        id="resolve_critical_technical_debt",
                        title="Resolve Critical Technical Debt Issues",
                        description=f"Address {quality_report.debt_by_severity['critical']} critical technical debt items immediately",
                        category="code_quality",
                        priority="high",
                        estimated_hours=quality_report.debt_by_severity['critical'] * 8,
                        dependencies=[],
                        files_involved=quality_report.hotspot_files[:3],
                        agent_specialization="senior_developer",
                        confidence=0.95,
                        reasoning="Critical technical debt poses immediate risk to system stability",
                        acceptance_criteria=[
                            "All critical issues resolved",
                            "Root causes addressed",
                            "Preventive measures implemented"
                        ],
                        tags=["critical", "technical-debt", "urgent"]
                    ))
                
        except Exception as e:
            print(f"Warning: Code quality analysis failed: {e}")
            # Don't fail the entire task generation if code quality analysis fails
        
        return tasks

    def _generate_report(self, tasks: List[GeneratedTask], analysis: AnalysisResult) -> TaskGenerationReport:
        """Generate a comprehensive report of task generation"""
        tasks_by_category = {}
        for task in tasks:
            tasks_by_category[task.category] = tasks_by_category.get(task.category, 0) + 1
        
        high_confidence_tasks = len([t for t in tasks if t.confidence >= 0.8])
        
        # Identify gaps
        detected_gaps = []
        if not analysis.structure.has_tests:
            detected_gaps.append("No testing infrastructure")
        if not analysis.structure.has_docs:
            detected_gaps.append("Limited documentation")
        if not analysis.structure.has_ci_cd:
            detected_gaps.append("No CI/CD pipeline")
        if not analysis.structure.has_docker:
            detected_gaps.append("No containerization")
        
        # Generate recommendations
        recommendations = []
        if analysis.estimated_complexity == "high":
            recommendations.append("Consider breaking project into smaller modules")
        if len(analysis.tech_stack.languages) > 3:
            recommendations.append("Multiple languages detected - ensure team has required skills")
        if not analysis.structure.has_tests:
            recommendations.append("Prioritize adding comprehensive test coverage")
        
        return TaskGenerationReport(
            total_tasks_generated=len(tasks),
            tasks_by_category=tasks_by_category,
            high_confidence_tasks=high_confidence_tasks,
            detected_gaps=detected_gaps,
            recommendations=recommendations,
            generation_timestamp=datetime.now().isoformat()
        )

    def export_tasks(self, tasks: List[GeneratedTask], format: str = "json") -> str:
        """Export generated tasks in specified format"""
        tasks_dict = [asdict(task) for task in tasks]
        
        if format.lower() == "json":
            return json.dumps(tasks_dict, indent=2, default=str)
        elif format.lower() == "csv":
            import csv
            import io
            output = io.StringIO()
            if tasks_dict:
                writer = csv.DictWriter(output, fieldnames=tasks_dict[0].keys())
                writer.writeheader()
                writer.writerows(tasks_dict)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _analyze_config_files(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze configuration files to suggest configuration improvements"""
        tasks = []
        
        # Check for missing environment configuration
        env_files = [".env", ".env.example", ".env.local"]
        has_env = any((project_path / env_file).exists() for env_file in env_files)
        
        if not has_env and analysis.project_type in ['api_service', 'web_app']:
            tasks.append(GeneratedTask(
                id="setup_environment_config",
                title="Set up environment configuration",
                description="Create environment configuration files for different deployment stages",
                category="setup",
                priority="medium",
                estimated_hours=2,
                confidence=0.8,
                dependencies=[],
                agent_specialization="devops",
                tags=["configuration", "environment"],
                acceptance_criteria=[
                    "Environment configuration files created",
                    "Example configuration provided",
                    "Documentation updated"
                ]
            ))
        
        return tasks
    
    def _analyze_database_files(self, project_path: Path, analysis: AnalysisResult) -> List[GeneratedTask]:
        """Analyze database-related files to suggest database improvements"""
        tasks = []
        
        # Check for database migrations
        migration_dirs = ["migrations", "db/migrations", "alembic", "prisma/migrations"]
        has_migrations = any((project_path / migration_dir).exists() for migration_dir in migration_dirs)
        
        if analysis.structure.has_database and not has_migrations:
            tasks.append(GeneratedTask(
                id="setup_database_migrations",
                title="Set up database migrations",
                description="Implement database migration system for schema management",
                category="development",
                priority="high",
                estimated_hours=6,
                confidence=0.9,
                dependencies=[],
                agent_specialization="backend",
                tags=["database", "migrations"],
                acceptance_criteria=[
                    "Migration system configured",
                    "Initial migration created",
                    "Migration scripts documented"
                ]
            ))
        
        return tasks

def main():
    """Command-line interface for automatic task generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate tasks automatically from project analysis")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file for generated tasks")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                       help="Output format")
    parser.add_argument("--report", help="Output file for generation report")
    parser.add_argument("--exclude-existing", action="store_true", default=True,
                       help="Exclude tasks that appear to be already completed")
    
    args = parser.parse_args()
    
    generator = AutoTaskGenerator()
    
    try:
        tasks, report = generator.generate_tasks_from_project(
            args.project_path, 
            exclude_existing=args.exclude_existing
        )
        
        print(f"Generated {len(tasks)} tasks for project: {args.project_path}")
        print(f"High confidence tasks: {report.high_confidence_tasks}")
        print(f"Tasks by category: {report.tasks_by_category}")
        
        # Export tasks
        output = generator.export_tasks(tasks, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Tasks written to {args.output}")
        else:
            print("\nGenerated Tasks:")
            print(output)
        
        # Export report
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(asdict(report), f, indent=2, default=str)
            print(f"Report written to {args.report}")
        
    except Exception as e:
        print(f"Error generating tasks: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())