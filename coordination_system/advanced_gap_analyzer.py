#!/usr/bin/env python3
"""
Advanced Gap Analyzer - Sophisticated gap analysis with dependency mapping and best practices
"""

import os
import json
import re
import ast
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime

from .project_analyzer import ProjectAnalyzer, AnalysisResult, ProjectType, TechnologyStack

@dataclass
class GapAnalysis:
    category: str
    severity: str  # critical, high, medium, low
    gap_type: str  # missing, outdated, misconfigured, insufficient
    description: str
    impact: str
    remediation_effort: str  # hours
    dependencies: List[str]
    confidence: float
    evidence: List[str]
    best_practices: List[str]

@dataclass
class DependencyMap:
    task_id: str
    depends_on: List[str]
    blocks: List[str]
    parallel_with: List[str]
    estimated_sequence: int

class AdvancedGapAnalyzer:
    def __init__(self):
        self.analyzer = ProjectAnalyzer()
        self.best_practices_db = self._load_best_practices()
        self.dependency_patterns = self._load_dependency_patterns()
        self.quality_metrics = self._setup_quality_metrics()
        
    def _load_best_practices(self) -> Dict[str, Dict[str, Any]]:
        """Load industry best practices by project type and technology"""
        return {
            "web_app": {
                "security": [
                    "Input validation and sanitization",
                    "HTTPS enforcement",
                    "Content Security Policy (CSP)",
                    "XSS protection headers",
                    "CSRF protection",
                    "Authentication and authorization",
                    "Secure session management",
                    "SQL injection prevention"
                ],
                "performance": [
                    "Code splitting and lazy loading",
                    "Image optimization",
                    "Caching strategies",
                    "Bundle size optimization",
                    "Critical CSS inlining",
                    "Resource compression",
                    "CDN implementation"
                ],
                "testing": [
                    "Unit tests (80%+ coverage)",
                    "Integration tests",
                    "End-to-end tests",
                    "Visual regression tests",
                    "Performance testing",
                    "Accessibility testing",
                    "Cross-browser testing"
                ],
                "accessibility": [
                    "WCAG 2.1 AA compliance",
                    "Semantic HTML structure",
                    "ARIA labels and roles",
                    "Keyboard navigation",
                    "Screen reader compatibility",
                    "Color contrast ratios",
                    "Focus management"
                ]
            },
            "api_service": {
                "design": [
                    "RESTful API design principles",
                    "Consistent naming conventions",
                    "Proper HTTP status codes",
                    "API versioning strategy",
                    "Request/response schemas",
                    "Error handling standards",
                    "Rate limiting implementation"
                ],
                "documentation": [
                    "OpenAPI/Swagger specification",
                    "Endpoint documentation",
                    "Authentication guide",
                    "Rate limiting documentation",
                    "Error codes reference",
                    "SDK/client examples",
                    "Postman collections"
                ],
                "monitoring": [
                    "Health check endpoints",
                    "Metrics collection",
                    "Logging standards",
                    "Distributed tracing",
                    "Error tracking",
                    "Performance monitoring",
                    "Alerting rules"
                ]
            },
            "ml_project": {
                "data": [
                    "Data validation pipelines",
                    "Data versioning",
                    "Feature engineering documentation",
                    "Data quality monitoring",
                    "Schema validation",
                    "Data lineage tracking",
                    "Privacy and compliance"
                ],
                "modeling": [
                    "Model versioning",
                    "Experiment tracking",
                    "Model validation",
                    "Cross-validation strategies",
                    "Hyperparameter tuning",
                    "Model interpretability",
                    "Bias detection and mitigation"
                ],
                "deployment": [
                    "Model serving infrastructure",
                    "A/B testing framework",
                    "Model monitoring",
                    "Drift detection",
                    "Rollback strategies",
                    "Performance benchmarking",
                    "Scalability planning"
                ]
            }
        }
    
    def _load_dependency_patterns(self) -> Dict[str, List[str]]:
        """Load common task dependency patterns"""
        return {
            "setup_before_development": [
                "setup_development_environment",
                "configure_build_tools",
                "setup_testing_framework",
                "setup_linting_and_formatting"
            ],
            "testing_before_deployment": [
                "write_unit_tests",
                "setup_integration_tests",
                "configure_ci_pipeline",
                "setup_code_coverage"
            ],
            "security_throughout": [
                "implement_authentication",
                "setup_authorization",
                "configure_security_headers",
                "implement_input_validation"
            ],
            "monitoring_after_deployment": [
                "setup_logging",
                "configure_metrics",
                "setup_alerting",
                "implement_health_checks"
            ]
        }
    
    def _setup_quality_metrics(self) -> Dict[str, Any]:
        """Setup code quality metrics and thresholds"""
        return {
            "test_coverage": {
                "minimum": 0.8,
                "target": 0.9,
                "critical_files": 0.95
            },
            "code_complexity": {
                "cyclomatic_max": 10,
                "function_length_max": 50,
                "class_length_max": 300
            },
            "documentation": {
                "api_coverage": 0.9,
                "public_method_coverage": 0.8,
                "readme_completeness": 0.9
            },
            "security": {
                "vulnerability_scan": True,
                "dependency_audit": True,
                "secrets_detection": True
            }
        }
    
    def analyze_comprehensive_gaps(self, project_path: str, 
                                 analysis: AnalysisResult) -> Tuple[List[GapAnalysis], List[DependencyMap]]:
        """Perform comprehensive gap analysis with dependency mapping"""
        project_path = Path(project_path)
        
        # Get file list
        file_list = self._scan_project_files(project_path)
        
        # Perform different types of gap analysis
        gaps = []
        
        # 1. Architecture and Design Gaps
        architecture_gaps = self._analyze_architecture_gaps(project_path, file_list, analysis)
        gaps.extend(architecture_gaps)
        
        # 2. Security Gaps
        security_gaps = self._analyze_security_gaps(project_path, file_list, analysis)
        gaps.extend(security_gaps)
        
        # 3. Testing Gaps
        testing_gaps = self._analyze_testing_gaps(project_path, file_list, analysis)
        gaps.extend(testing_gaps)
        
        # 4. Performance Gaps
        performance_gaps = self._analyze_performance_gaps(project_path, file_list, analysis)
        gaps.extend(performance_gaps)
        
        # 5. Documentation Gaps
        documentation_gaps = self._analyze_documentation_gaps(project_path, file_list, analysis)
        gaps.extend(documentation_gaps)
        
        # 6. Deployment and Operations Gaps
        deployment_gaps = self._analyze_deployment_gaps(project_path, file_list, analysis)
        gaps.extend(deployment_gaps)
        
        # 7. Code Quality Gaps
        quality_gaps = self._analyze_code_quality_gaps(project_path, file_list, analysis)
        gaps.extend(quality_gaps)
        
        # 8. Accessibility Gaps (for web applications)
        if analysis.project_type == ProjectType.WEB_APP:
            accessibility_gaps = self._analyze_accessibility_gaps(project_path, file_list, analysis)
            gaps.extend(accessibility_gaps)
        
        # Generate dependency mapping
        dependency_map = self._generate_dependency_mapping(gaps)
        
        return gaps, dependency_map
    
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
    
    def _analyze_architecture_gaps(self, project_path: Path, file_list: List[str], 
                                 analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze architecture and design gaps"""
        gaps = []
        project_type = analysis.project_type.value
        
        # Check for proper separation of concerns
        if not self._has_proper_structure(file_list, analysis.project_type):
            gaps.append(GapAnalysis(
                category="architecture",
                severity="high",
                gap_type="missing",
                description="Project lacks proper directory structure and separation of concerns",
                impact="Poor maintainability, difficult to scale, confusion for new developers",
                remediation_effort="8-16",
                dependencies=["refactor_project_structure"],
                confidence=0.9,
                evidence=self._get_structure_evidence(file_list),
                best_practices=[
                    "Implement layered architecture",
                    "Separate business logic from presentation",
                    "Use dependency injection",
                    "Follow single responsibility principle"
                ]
            ))
        
        # Check for configuration management
        config_files = [f for f in file_list if 'config' in f.lower() or f.endswith(('.env', '.ini', '.yaml', '.yml'))]
        if not config_files:
            gaps.append(GapAnalysis(
                category="architecture",
                severity="medium",
                gap_type="missing",
                description="No configuration management system found",
                impact="Hard-coded values, difficult environment management",
                remediation_effort="4-8",
                dependencies=["setup_configuration_management"],
                confidence=0.8,
                evidence=["No config files found"],
                best_practices=[
                    "Use environment-specific configurations",
                    "Externalize all configuration",
                    "Use configuration validation",
                    "Document configuration options"
                ]
            ))
        
        # Check for error handling patterns
        if not self._has_proper_error_handling(project_path, file_list, analysis):
            gaps.append(GapAnalysis(
                category="architecture",
                severity="high",
                gap_type="insufficient",
                description="Inconsistent or insufficient error handling patterns",
                impact="Poor user experience, difficult debugging, system instability",
                remediation_effort="12-24",
                dependencies=["implement_error_handling"],
                confidence=0.7,
                evidence=self._get_error_handling_evidence(project_path, file_list),
                best_practices=[
                    "Centralized error handling",
                    "Structured error responses",
                    "Proper logging of errors",
                    "Graceful degradation"
                ]
            ))
        
        return gaps
    
    def _analyze_security_gaps(self, project_path: Path, file_list: List[str], 
                             analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze security vulnerabilities and gaps"""
        gaps = []
        
        # Check for dependency vulnerabilities
        if not self._has_security_scanning(file_list):
            gaps.append(GapAnalysis(
                category="security",
                severity="critical",
                gap_type="missing",
                description="No dependency vulnerability scanning configured",
                impact="Vulnerable dependencies may expose security risks",
                remediation_effort="2-4",
                dependencies=["setup_dependency_scanning"],
                confidence=0.95,
                evidence=["No security scanning configuration found"],
                best_practices=[
                    "Regular dependency audits",
                    "Automated vulnerability scanning",
                    "Security advisories monitoring",
                    "Dependency update automation"
                ]
            ))
        
        # Check for secrets in code
        secrets_found = self._scan_for_secrets(project_path, file_list)
        if secrets_found:
            gaps.append(GapAnalysis(
                category="security",
                severity="critical",
                gap_type="misconfigured",
                description="Potential secrets or credentials found in code",
                impact="Security breach, unauthorized access, data compromise",
                remediation_effort="4-8",
                dependencies=["remove_secrets_from_code", "setup_secrets_management"],
                confidence=0.8,
                evidence=secrets_found,
                best_practices=[
                    "Use environment variables for secrets",
                    "Implement secrets management system",
                    "Use .gitignore for sensitive files",
                    "Regular secrets scanning"
                ]
            ))
        
        # Check for authentication/authorization
        if analysis.project_type in [ProjectType.WEB_APP, ProjectType.API_SERVICE]:
            if not self._has_authentication(project_path, file_list, analysis):
                gaps.append(GapAnalysis(
                    category="security",
                    severity="high",
                    gap_type="missing",
                    description="No authentication system implemented",
                    impact="Unauthorized access, data breaches, regulatory compliance issues",
                    remediation_effort="16-32",
                    dependencies=["implement_authentication", "setup_user_management"],
                    confidence=0.8,
                    evidence=["No auth-related files or imports found"],
                    best_practices=[
                        "Multi-factor authentication",
                        "Strong password policies",
                        "Session management",
                        "OAuth/OpenID Connect integration"
                    ]
                ))
        
        # Check for input validation
        if not self._has_input_validation(project_path, file_list, analysis):
            gaps.append(GapAnalysis(
                category="security",
                severity="high",
                gap_type="insufficient",
                description="Insufficient input validation and sanitization",
                impact="XSS attacks, SQL injection, data corruption",
                remediation_effort="8-16",
                dependencies=["implement_input_validation"],
                confidence=0.7,
                evidence=self._get_validation_evidence(project_path, file_list),
                best_practices=[
                    "Server-side validation",
                    "Input sanitization",
                    "Schema validation",
                    "Rate limiting"
                ]
            ))
        
        return gaps
    
    def _analyze_testing_gaps(self, project_path: Path, file_list: List[str], 
                            analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze testing coverage and quality gaps"""
        gaps = []
        
        # Calculate test metrics
        test_metrics = self._calculate_test_metrics(project_path, file_list, analysis)
        
        # Check test coverage
        if test_metrics['coverage_ratio'] < self.quality_metrics['test_coverage']['minimum']:
            severity = "critical" if test_metrics['coverage_ratio'] < 0.5 else "high"
            gaps.append(GapAnalysis(
                category="testing",
                severity=severity,
                gap_type="insufficient",
                description=f"Low test coverage ({test_metrics['coverage_ratio']:.1%})",
                impact="High risk of bugs, difficult refactoring, reduced confidence in releases",
                remediation_effort="24-48",
                dependencies=["increase_test_coverage", "setup_coverage_reporting"],
                confidence=0.9,
                evidence=[
                    f"Only {test_metrics['test_files']} test files for {test_metrics['source_files']} source files",
                    f"Coverage ratio: {test_metrics['coverage_ratio']:.1%}"
                ],
                best_practices=[
                    "Aim for 80%+ test coverage",
                    "Test critical paths first",
                    "Include edge cases",
                    "Regular coverage monitoring"
                ]
            ))
        
        # Check for different types of tests
        test_types = self._analyze_test_types(project_path, file_list)
        
        if not test_types['unit_tests']:
            gaps.append(GapAnalysis(
                category="testing",
                severity="high",
                gap_type="missing",
                description="No unit tests found",
                impact="Bugs slip through, difficult debugging, low development confidence",
                remediation_effort="16-32",
                dependencies=["setup_unit_testing"],
                confidence=0.9,
                evidence=["No unit test files detected"],
                best_practices=[
                    "Test individual functions/methods",
                    "Mock external dependencies",
                    "Fast execution time",
                    "Independent test cases"
                ]
            ))
        
        if not test_types['integration_tests'] and analysis.project_type != ProjectType.LIBRARY:
            gaps.append(GapAnalysis(
                category="testing",
                severity="medium",
                gap_type="missing",
                description="No integration tests found",
                impact="Component interaction bugs, system-level failures",
                remediation_effort="12-24",
                dependencies=["setup_integration_testing"],
                confidence=0.8,
                evidence=["No integration test files detected"],
                best_practices=[
                    "Test component interactions",
                    "Database integration testing",
                    "API endpoint testing",
                    "Third-party service mocking"
                ]
            ))
        
        return gaps
    
    def _analyze_performance_gaps(self, project_path: Path, file_list: List[str], 
                                analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze performance optimization gaps"""
        gaps = []
        
        # Check for performance monitoring
        if not self._has_performance_monitoring(project_path, file_list, analysis):
            gaps.append(GapAnalysis(
                category="performance",
                severity="medium",
                gap_type="missing",
                description="No performance monitoring implemented",
                impact="Performance degradation goes unnoticed, poor user experience",
                remediation_effort="8-16",
                dependencies=["setup_performance_monitoring"],
                confidence=0.8,
                evidence=["No performance monitoring tools detected"],
                best_practices=[
                    "Application performance monitoring (APM)",
                    "Real user monitoring (RUM)",
                    "Performance budgets",
                    "Automated performance testing"
                ]
            ))
        
        # Web-specific performance checks
        if analysis.project_type == ProjectType.WEB_APP:
            web_perf_issues = self._analyze_web_performance(project_path, file_list)
            gaps.extend(web_perf_issues)
        
        # Database performance checks
        if analysis.structure.has_database:
            db_perf_issues = self._analyze_database_performance(project_path, file_list)
            gaps.extend(db_perf_issues)
        
        return gaps
    
    def _analyze_documentation_gaps(self, project_path: Path, file_list: List[str], 
                                  analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze documentation completeness and quality"""
        gaps = []
        
        # Check for README
        readme_files = [f for f in file_list if f.lower().startswith('readme')]
        if not readme_files:
            gaps.append(GapAnalysis(
                category="documentation",
                severity="high",
                gap_type="missing",
                description="No README file found",
                impact="Difficult onboarding, poor project adoption, confusion for contributors",
                remediation_effort="4-8",
                dependencies=["create_readme"],
                confidence=0.95,
                evidence=["No README file in project root"],
                best_practices=[
                    "Project overview and purpose",
                    "Installation instructions",
                    "Usage examples",
                    "Contribution guidelines",
                    "License information"
                ]
            ))
        else:
            # Analyze README quality
            readme_quality = self._analyze_readme_quality(project_path, readme_files[0])
            if readme_quality['completeness'] < 0.7:
                gaps.append(GapAnalysis(
                    category="documentation",
                    severity="medium",
                    gap_type="insufficient",
                    description="README file lacks important sections",
                    impact="Poor developer experience, increased support burden",
                    remediation_effort="2-4",
                    dependencies=["improve_readme"],
                    confidence=0.8,
                    evidence=readme_quality['missing_sections'],
                    best_practices=[
                        "Complete installation guide",
                        "Clear usage examples",
                        "API documentation links",
                        "Contributing guidelines"
                    ]
                ))
        
        # API documentation for services
        if analysis.project_type == ProjectType.API_SERVICE:
            if not self._has_api_documentation(project_path, file_list):
                gaps.append(GapAnalysis(
                    category="documentation",
                    severity="high",
                    gap_type="missing",
                    description="No API documentation found",
                    impact="Difficult API adoption, increased support requests",
                    remediation_effort="8-16",
                    dependencies=["create_api_documentation"],
                    confidence=0.9,
                    evidence=["No OpenAPI/Swagger files found"],
                    best_practices=[
                        "OpenAPI/Swagger specification",
                        "Interactive documentation",
                        "Code examples",
                        "Authentication guide",
                        "Rate limiting documentation"
                    ]
                ))
        
        return gaps
    
    def _analyze_deployment_gaps(self, project_path: Path, file_list: List[str], 
                               analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze deployment and operations gaps"""
        gaps = []
        
        # Check for containerization
        if 'Dockerfile' not in file_list:
            gaps.append(GapAnalysis(
                category="deployment",
                severity="medium",
                gap_type="missing",
                description="No containerization setup found",
                impact="Inconsistent deployment environments, dependency issues",
                remediation_effort="4-8",
                dependencies=["setup_containerization"],
                confidence=0.8,
                evidence=["No Dockerfile found"],
                best_practices=[
                    "Multi-stage Docker builds",
                    "Minimal base images",
                    "Security scanning",
                    "Health checks",
                    "Resource limits"
                ]
            ))
        
        # Check for CI/CD
        ci_files = [f for f in file_list if f.startswith('.github/workflows/') or 
                   f in ['.gitlab-ci.yml', 'Jenkinsfile', '.circleci/config.yml']]
        if not ci_files:
            gaps.append(GapAnalysis(
                category="deployment",
                severity="high",
                gap_type="missing",
                description="No CI/CD pipeline configured",
                impact="Manual deployments, inconsistent releases, higher error rates",
                remediation_effort="8-16",
                dependencies=["setup_ci_cd_pipeline"],
                confidence=0.9,
                evidence=["No CI/CD configuration files found"],
                best_practices=[
                    "Automated testing in CI",
                    "Build artifact management",
                    "Deployment automation",
                    "Rollback strategies",
                    "Environment promotion"
                ]
            ))
        
        # Check for monitoring and logging
        if not self._has_monitoring_setup(project_path, file_list):
            gaps.append(GapAnalysis(
                category="deployment",
                severity="medium",
                gap_type="missing",
                description="No monitoring and logging setup",
                impact="Difficult troubleshooting, undetected issues, poor observability",
                remediation_effort="12-24",
                dependencies=["setup_monitoring", "setup_logging"],
                confidence=0.8,
                evidence=["No monitoring configuration found"],
                best_practices=[
                    "Structured logging",
                    "Metrics collection",
                    "Alerting rules",
                    "Distributed tracing",
                    "Health check endpoints"
                ]
            ))
        
        return gaps
    
    def _analyze_code_quality_gaps(self, project_path: Path, file_list: List[str], 
                                 analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze code quality and maintainability gaps"""
        gaps = []
        
        # Check for linting setup
        if not self._has_linting_setup(project_path, file_list, analysis):
            gaps.append(GapAnalysis(
                category="quality",
                severity="medium",
                gap_type="missing",
                description="No code linting configured",
                impact="Inconsistent code style, potential bugs, reduced maintainability",
                remediation_effort="2-4",
                dependencies=["setup_code_linting"],
                confidence=0.9,
                evidence=["No linting configuration files found"],
                best_practices=[
                    "Consistent code formatting",
                    "Static analysis rules",
                    "Pre-commit hooks",
                    "IDE integration"
                ]
            ))
        
        # Check for pre-commit hooks
        if '.pre-commit-config.yaml' not in file_list:
            gaps.append(GapAnalysis(
                category="quality",
                severity="low",
                gap_type="missing",
                description="No pre-commit hooks configured",
                impact="Code quality issues not caught early, inconsistent commits",
                remediation_effort="2-4",
                dependencies=["setup_precommit_hooks"],
                confidence=0.8,
                evidence=["No pre-commit configuration found"],
                best_practices=[
                    "Automated code formatting",
                    "Lint checking before commit",
                    "Test execution",
                    "Security scanning"
                ]
            ))
        
        # Check for code complexity
        complexity_issues = self._analyze_code_complexity(project_path, file_list, analysis)
        if complexity_issues:
            gaps.append(GapAnalysis(
                category="quality",
                severity="medium",
                gap_type="insufficient",
                description="High code complexity detected in some areas",
                impact="Difficult maintenance, higher bug probability, reduced readability",
                remediation_effort="16-32",
                dependencies=["refactor_complex_code"],
                confidence=0.7,
                evidence=complexity_issues,
                best_practices=[
                    "Extract complex functions",
                    "Reduce cyclomatic complexity",
                    "Follow single responsibility principle",
                    "Add comprehensive comments"
                ]
            ))
        
        return gaps
    
    def _analyze_accessibility_gaps(self, project_path: Path, file_list: List[str], 
                                  analysis: AnalysisResult) -> List[GapAnalysis]:
        """Analyze accessibility gaps for web applications"""
        gaps = []
        
        # Check for accessibility testing
        if not self._has_accessibility_testing(project_path, file_list):
            gaps.append(GapAnalysis(
                category="accessibility",
                severity="medium",
                gap_type="missing",
                description="No accessibility testing configured",
                impact="Poor user experience for disabled users, legal compliance issues",
                remediation_effort="8-16",
                dependencies=["setup_accessibility_testing"],
                confidence=0.8,
                evidence=["No accessibility testing tools found"],
                best_practices=[
                    "Automated accessibility testing",
                    "Screen reader testing",
                    "Keyboard navigation testing",
                    "Color contrast validation",
                    "WCAG compliance checking"
                ]
            ))
        
        # Check HTML structure in React/Vue projects
        if 'react' in analysis.tech_stack.frameworks or 'vue' in analysis.tech_stack.frameworks:
            semantic_issues = self._analyze_semantic_html(project_path, file_list)
            if semantic_issues:
                gaps.append(GapAnalysis(
                    category="accessibility",
                    severity="medium",
                    gap_type="insufficient",
                    description="Semantic HTML structure could be improved",
                    impact="Poor screen reader experience, SEO issues",
                    remediation_effort="4-8",
                    dependencies=["improve_semantic_html"],
                    confidence=0.6,
                    evidence=semantic_issues,
                    best_practices=[
                        "Use semantic HTML elements",
                        "Proper heading hierarchy",
                        "ARIA labels where needed",
                        "Alt text for images"
                    ]
                ))
        
        return gaps
    
    def _generate_dependency_mapping(self, gaps: List[GapAnalysis]) -> List[DependencyMap]:
        """Generate task dependency mapping based on gap analysis"""
        dependency_maps = []
        task_sequence = 1
        
        # Create tasks by category with proper dependencies
        tasks_by_category = defaultdict(list)
        for gap in gaps:
            tasks_by_category[gap.category].append(gap)
        
        # Define dependency rules
        dependency_rules = {
            "setup_before_all": ["architecture", "quality"],
            "security_parallel": ["security"],
            "testing_after_dev": ["testing"],
            "deployment_last": ["deployment"],
            "documentation_parallel": ["documentation"]
        }
        
        # Map tasks to sequences based on dependencies
        for category, category_gaps in tasks_by_category.items():
            for gap in category_gaps:
                for dep in gap.dependencies:
                    # Determine what this task depends on
                    depends_on = self._determine_task_dependencies(dep, gaps)
                    
                    # Determine what this task blocks
                    blocks = self._determine_task_blocks(dep, gaps)
                    
                    # Determine parallel tasks
                    parallel_with = self._determine_parallel_tasks(dep, category, gaps)
                    
                    dependency_maps.append(DependencyMap(
                        task_id=dep,
                        depends_on=depends_on,
                        blocks=blocks,
                        parallel_with=parallel_with,
                        estimated_sequence=task_sequence
                    ))
                    
                    task_sequence += 1
        
        return dependency_maps
    
    def _determine_task_dependencies(self, task_id: str, gaps: List[GapAnalysis]) -> List[str]:
        """Determine what tasks this task depends on"""
        dependencies = []
        
        # Setup tasks come first
        if any(keyword in task_id.lower() for keyword in ['setup', 'configure', 'install']):
            return []  # Setup tasks have no dependencies
        
        # Development tasks depend on setup
        if any(keyword in task_id.lower() for keyword in ['implement', 'develop', 'create']):
            setup_tasks = [gap.dependencies[0] for gap in gaps 
                          if gap.category in ['architecture', 'quality'] and gap.dependencies]
            dependencies.extend(setup_tasks)
        
        # Testing tasks depend on implementation
        if 'test' in task_id.lower():
            impl_tasks = [gap.dependencies[0] for gap in gaps 
                         if any(keyword in gap.dependencies[0].lower() 
                               for keyword in ['implement', 'develop', 'create']) and gap.dependencies]
            dependencies.extend(impl_tasks)
        
        # Deployment tasks depend on testing
        if any(keyword in task_id.lower() for keyword in ['deploy', 'release', 'ci_cd']):
            test_tasks = [gap.dependencies[0] for gap in gaps 
                         if 'test' in gap.dependencies[0].lower() and gap.dependencies]
            dependencies.extend(test_tasks)
        
        return list(set(dependencies))
    
    def _determine_task_blocks(self, task_id: str, gaps: List[GapAnalysis]) -> List[str]:
        """Determine what tasks this task blocks"""
        blocks = []
        
        # Setup tasks block development tasks
        if any(keyword in task_id.lower() for keyword in ['setup', 'configure', 'install']):
            impl_tasks = [gap.dependencies[0] for gap in gaps 
                         if any(keyword in gap.dependencies[0].lower() 
                               for keyword in ['implement', 'develop', 'create']) and gap.dependencies]
            blocks.extend(impl_tasks)
        
        # Implementation blocks testing
        if any(keyword in task_id.lower() for keyword in ['implement', 'develop', 'create']):
            test_tasks = [gap.dependencies[0] for gap in gaps 
                         if 'test' in gap.dependencies[0].lower() and gap.dependencies]
            blocks.extend(test_tasks)
        
        return list(set(blocks))
    
    def _determine_parallel_tasks(self, task_id: str, category: str, gaps: List[GapAnalysis]) -> List[str]:
        """Determine what tasks can run in parallel"""
        parallel = []
        
        # Documentation can run in parallel with most tasks
        if category == 'documentation':
            other_doc_tasks = [gap.dependencies[0] for gap in gaps 
                              if gap.category == 'documentation' and 
                              gap.dependencies and gap.dependencies[0] != task_id]
            parallel.extend(other_doc_tasks)
        
        # Security tasks can often run in parallel
        if category == 'security':
            other_security_tasks = [gap.dependencies[0] for gap in gaps 
                                   if gap.category == 'security' and 
                                   gap.dependencies and gap.dependencies[0] != task_id]
            parallel.extend(other_security_tasks)
        
        return parallel
    
    # Helper methods for specific analysis
    def _has_proper_structure(self, file_list: List[str], project_type: ProjectType) -> bool:
        """Check if project has proper directory structure"""
        if project_type == ProjectType.WEB_APP:
            return any(f.startswith('src/') for f in file_list)
        elif project_type == ProjectType.API_SERVICE:
            return any(f in ['main.py', 'app.py', 'server.js'] for f in file_list)
        elif project_type == ProjectType.ML_PROJECT:
            return any(dir_name in [f.split('/')[0] for f in file_list] 
                      for dir_name in ['notebooks', 'data', 'models', 'src'])
        return True
    
    def _get_structure_evidence(self, file_list: List[str]) -> List[str]:
        """Get evidence for structure issues"""
        evidence = []
        if not any(f.startswith('src/') for f in file_list):
            evidence.append("No src/ directory found")
        if len([f for f in file_list if f.endswith('.py') and '/' not in f]) > 5:
            evidence.append("Too many Python files in root directory")
        return evidence
    
    def _has_proper_error_handling(self, project_path: Path, file_list: List[str], 
                                 analysis: AnalysisResult) -> bool:
        """Check for proper error handling patterns"""
        # This would require actual code analysis
        # For now, return False to suggest improvement
        return False
    
    def _get_error_handling_evidence(self, project_path: Path, file_list: List[str]) -> List[str]:
        """Get evidence for error handling issues"""
        return ["Manual code review needed for error handling patterns"]
    
    def _has_security_scanning(self, file_list: List[str]) -> bool:
        """Check if security scanning is configured"""
        security_files = [
            '.github/workflows/security.yml',
            'bandit.yaml', 'bandit.yml',
            '.semgrep.yml',
            'safety.txt'
        ]
        return any(f in file_list for f in security_files)
    
    def _scan_for_secrets(self, project_path: Path, file_list: List[str]) -> List[str]:
        """Scan for potential secrets in code"""
        secrets_patterns = [
            r'(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*["\'][^"\']{8,}["\']',
            r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)',
            r'(?i)(database[_-]?url|db[_-]?url)\s*[:=]',
        ]
        
        potential_secrets = []
        
        # Check common files for secrets
        check_files = [f for f in file_list if f.endswith(('.py', '.js', '.ts', '.env', '.yaml', '.yml'))]
        
        for file_path in check_files[:10]:  # Limit to first 10 files for performance
            try:
                full_path = project_path / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)  # First 1000 chars
                        for pattern in secrets_patterns:
                            if re.search(pattern, content):
                                potential_secrets.append(f"Potential secret in {file_path}")
                                break
            except Exception:
                continue
        
        return potential_secrets
    
    def _has_authentication(self, project_path: Path, file_list: List[str], 
                          analysis: AnalysisResult) -> bool:
        """Check if authentication is implemented"""
        auth_indicators = [
            'auth', 'login', 'jwt', 'session', 'passport',
            'oauth', 'token', 'authentication', 'authorization'
        ]
        
        # Check file names
        if any(indicator in f.lower() for f in file_list for indicator in auth_indicators):
            return True
        
        # Check package.json dependencies
        if 'package.json' in file_list:
            try:
                with open(project_path / 'package.json', 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), 
                           **package_data.get('devDependencies', {})}
                    if any(indicator in dep.lower() for dep in deps for indicator in auth_indicators):
                        return True
            except Exception:
                pass
        
        return False
    
    def _has_input_validation(self, project_path: Path, file_list: List[str], 
                            analysis: AnalysisResult) -> bool:
        """Check if input validation is implemented"""
        # This would require code analysis - simplified for now
        validation_files = [f for f in file_list if 'valid' in f.lower() or 'schema' in f.lower()]
        return len(validation_files) > 0
    
    def _get_validation_evidence(self, project_path: Path, file_list: List[str]) -> List[str]:
        """Get evidence for validation issues"""
        return ["No validation-related files found"]
    
    def _calculate_test_metrics(self, project_path: Path, file_list: List[str], 
                              analysis: AnalysisResult) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        source_files = [f for f in file_list if f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx'))]
        test_files = [f for f in file_list if 'test' in f.lower()]
        
        return {
            'source_files': len(source_files),
            'test_files': len(test_files),
            'coverage_ratio': len(test_files) / len(source_files) if source_files else 0
        }
    
    def _analyze_test_types(self, project_path: Path, file_list: List[str]) -> Dict[str, bool]:
        """Analyze what types of tests exist"""
        return {
            'unit_tests': any('test' in f.lower() and not any(x in f.lower() for x in ['integration', 'e2e']) 
                             for f in file_list),
            'integration_tests': any('integration' in f.lower() for f in file_list),
            'e2e_tests': any(x in f.lower() for f in file_list for x in ['e2e', 'end-to-end', 'cypress'])
        }
    
    def _has_performance_monitoring(self, project_path: Path, file_list: List[str], 
                                  analysis: AnalysisResult) -> bool:
        """Check if performance monitoring is set up"""
        monitoring_indicators = ['monitoring', 'metrics', 'prometheus', 'grafana', 'datadog']
        return any(indicator in f.lower() for f in file_list for indicator in monitoring_indicators)
    
    def _analyze_web_performance(self, project_path: Path, file_list: List[str]) -> List[GapAnalysis]:
        """Analyze web-specific performance issues"""
        gaps = []
        
        # Check for bundle analysis
        if not any('bundle' in f.lower() or 'webpack-bundle-analyzer' in f.lower() for f in file_list):
            gaps.append(GapAnalysis(
                category="performance",
                severity="low",
                gap_type="missing",
                description="No bundle size analysis configured",
                impact="Uncontrolled bundle growth, slow loading times",
                remediation_effort="2-4",
                dependencies=["setup_bundle_analysis"],
                confidence=0.7,
                evidence=["No bundle analysis tools found"],
                best_practices=[
                    "Regular bundle size monitoring",
                    "Code splitting implementation",
                    "Tree shaking optimization",
                    "Asset optimization"
                ]
            ))
        
        return gaps
    
    def _analyze_database_performance(self, project_path: Path, file_list: List[str]) -> List[GapAnalysis]:
        """Analyze database performance issues"""
        gaps = []
        
        # Check for database migrations
        if not any('migration' in f.lower() for f in file_list):
            gaps.append(GapAnalysis(
                category="performance",
                severity="medium",
                gap_type="missing",
                description="No database migration system found",
                impact="Difficult schema changes, deployment issues",
                remediation_effort="4-8",
                dependencies=["setup_database_migrations"],
                confidence=0.8,
                evidence=["No migration files found"],
                best_practices=[
                    "Version-controlled schema changes",
                    "Rollback capabilities",
                    "Index optimization",
                    "Query performance monitoring"
                ]
            ))
        
        return gaps
    
    def _analyze_readme_quality(self, project_path: Path, readme_file: str) -> Dict[str, Any]:
        """Analyze README quality and completeness"""
        try:
            with open(project_path / readme_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            required_sections = [
                'installation', 'usage', 'contributing', 'license',
                'getting started', 'requirements', 'examples'
            ]
            
            missing_sections = [section for section in required_sections 
                              if section not in content]
            
            completeness = 1.0 - (len(missing_sections) / len(required_sections))
            
            return {
                'completeness': completeness,
                'missing_sections': missing_sections
            }
        except Exception:
            return {'completeness': 0, 'missing_sections': required_sections}
    
    def _has_api_documentation(self, project_path: Path, file_list: List[str]) -> bool:
        """Check if API documentation exists"""
        api_doc_files = [
            'openapi.yaml', 'openapi.yml', 'swagger.yaml', 'swagger.yml',
            'api.yaml', 'api.yml', 'docs/api'
        ]
        return any(f in file_list or any(doc in f for doc in api_doc_files) for f in file_list)
    
    def _has_monitoring_setup(self, project_path: Path, file_list: List[str]) -> bool:
        """Check if monitoring is set up"""
        monitoring_files = [
            'prometheus.yml', 'grafana.yml', 'monitoring.yml',
            'docker-compose.monitoring.yml'
        ]
        return any(f in file_list for f in monitoring_files)
    
    def _has_linting_setup(self, project_path: Path, file_list: List[str], 
                         analysis: AnalysisResult) -> bool:
        """Check if code linting is configured"""
        if 'python' in analysis.tech_stack.languages:
            python_linters = ['.flake8', 'pyproject.toml', 'setup.cfg', '.pylintrc']
            if any(f in file_list for f in python_linters):
                return True
        
        if any(lang in analysis.tech_stack.languages for lang in ['javascript', 'typescript']):
            js_linters = ['.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', 'eslint.config.js']
            if any(f in file_list for f in js_linters):
                return True
        
        return False
    
    def _analyze_code_complexity(self, project_path: Path, file_list: List[str], 
                               analysis: AnalysisResult) -> List[str]:
        """Analyze code complexity issues"""
        issues = []
        
        # Check for very large files (potential complexity issue)
        try:
            for file_path in file_list[:20]:  # Check first 20 files
                if file_path.endswith(('.py', '.js', '.ts')):
                    full_path = project_path / file_path
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            if len(lines) > 300:
                                issues.append(f"Large file: {file_path} ({len(lines)} lines)")
        except Exception:
            pass
        
        return issues
    
    def _has_accessibility_testing(self, project_path: Path, file_list: List[str]) -> bool:
        """Check if accessibility testing is configured"""
        a11y_tools = ['axe', 'lighthouse', 'pa11y', '@axe-core', 'cypress-axe']
        
        # Check package.json
        if 'package.json' in file_list:
            try:
                with open(project_path / 'package.json', 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), 
                           **package_data.get('devDependencies', {})}
                    if any(tool in dep for dep in deps for tool in a11y_tools):
                        return True
            except Exception:
                pass
        
        return False
    
    def _analyze_semantic_html(self, project_path: Path, file_list: List[str]) -> List[str]:
        """Analyze semantic HTML structure"""
        issues = []
        
        # Check React/Vue component files for semantic structure
        component_files = [f for f in file_list if f.endswith(('.jsx', '.tsx', '.vue'))]
        
        for file_path in component_files[:10]:  # Check first 10 components
            try:
                full_path = project_path / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Simple check for div-heavy structure
                        div_count = content.count('<div')
                        semantic_count = sum(content.count(f'<{tag}') for tag in 
                                           ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer'])
                        
                        if div_count > 5 and semantic_count == 0:
                            issues.append(f"Heavy div usage in {file_path}, consider semantic HTML")
            except Exception:
                continue
        
        return issues

def main():
    """Command-line interface for advanced gap analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Perform advanced gap analysis on projects")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file for gap analysis results")
    parser.add_argument("--format", choices=["json", "report"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    analyzer = AdvancedGapAnalyzer()
    project_analyzer = ProjectAnalyzer()
    
    try:
        # Analyze project first
        analysis = project_analyzer.analyze_project(args.project_path)
        
        # Perform gap analysis
        gaps, dependency_map = analyzer.analyze_comprehensive_gaps(args.project_path, analysis)
        
        if args.format == "json":
            output = {
                "gaps": [asdict(gap) for gap in gaps],
                "dependency_map": [asdict(dep) for dep in dependency_map],
                "summary": {
                    "total_gaps": len(gaps),
                    "critical_gaps": len([g for g in gaps if g.severity == "critical"]),
                    "high_gaps": len([g for g in gaps if g.severity == "high"]),
                    "categories": list(set(g.category for g in gaps))
                }
            }
            output_str = json.dumps(output, indent=2, default=str)
        else:
            # Generate report format
            output_str = f"""
# Advanced Gap Analysis Report

**Project**: {args.project_path}
**Analysis Date**: {datetime.now().isoformat()}

## Summary
- Total Gaps Found: {len(gaps)}
- Critical: {len([g for g in gaps if g.severity == 'critical'])}
- High: {len([g for g in gaps if g.severity == 'high'])}
- Medium: {len([g for g in gaps if g.severity == 'medium'])}
- Low: {len([g for g in gaps if g.severity == 'low'])}

## Gaps by Category
"""
            
            for category in set(g.category for g in gaps):
                category_gaps = [g for g in gaps if g.category == category]
                output_str += f"\n### {category.title()}\n"
                for gap in sorted(category_gaps, key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x.severity], reverse=True):
                    output_str += f"- **{gap.severity.upper()}**: {gap.description}\n"
                    output_str += f"  - Impact: {gap.impact}\n"
                    output_str += f"  - Effort: {gap.remediation_effort} hours\n\n"
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Gap analysis written to {args.output}")
        else:
            print(output_str)
            
    except Exception as e:
        print(f"Error performing gap analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())