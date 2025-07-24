#!/usr/bin/env python3
"""
Workflow Template Engine - Generates and manages workflow templates for different project types
"""

import json
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta

from .project_analyzer import ProjectAnalyzer, AnalysisResult, ProjectType

@dataclass
class Task:
    id: str
    title: str
    description: str
    estimated_hours: int
    priority: str  # high, medium, low
    dependencies: List[str]
    agent_specialization: Optional[str]
    tags: List[str]
    acceptance_criteria: List[str]

@dataclass
class Phase:
    id: str
    name: str
    description: str
    tasks: List[Task]
    estimated_weeks: int
    parallel_execution: bool

@dataclass
class WorkflowTemplate:
    id: str
    name: str
    description: str
    project_type: ProjectType
    phases: List[Phase]
    total_estimated_weeks: int
    recommended_team_size: int
    required_skills: List[str]
    optional_skills: List[str]
    success_metrics: List[str]

class WorkflowTemplateEngine:
    def __init__(self):
        self.templates = self._load_templates()
        self.task_generators = self._load_task_generators()
        self.analyzer = ProjectAnalyzer()

    def _load_templates(self) -> Dict[str, WorkflowTemplate]:
        """Load predefined workflow templates"""
        templates = {}
        
        # Web Application Template
        templates["web_app"] = WorkflowTemplate(
            id="web_app",
            name="Web Application Development",
            description="Complete workflow for developing modern web applications",
            project_type=ProjectType.WEB_APP,
            phases=[
                Phase(
                    id="setup",
                    name="Project Setup & Configuration",
                    description="Initialize project structure and development environment",
                    estimated_weeks=1,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="setup_repo",
                            title="Initialize Repository",
                            description="Set up version control and repository structure",
                            estimated_hours=4,
                            priority="high",
                            dependencies=[],
                            agent_specialization="devops",
                            tags=["setup", "git", "repository"],
                            acceptance_criteria=[
                                "Repository initialized with proper .gitignore",
                                "Branch protection rules configured",
                                "README.md created with project overview"
                            ]
                        ),
                        Task(
                            id="setup_dev_env",
                            title="Configure Development Environment",
                            description="Set up local development environment and tools",
                            estimated_hours=8,
                            priority="high",
                            dependencies=["setup_repo"],
                            agent_specialization="fullstack",
                            tags=["setup", "environment", "tooling"],
                            acceptance_criteria=[
                                "Package manager configured",
                                "Development server running",
                                "Hot reload functionality working",
                                "Environment variables properly configured"
                            ]
                        ),
                        Task(
                            id="setup_linting",
                            title="Configure Code Quality Tools",
                            description="Set up linting, formatting, and code quality tools",
                            estimated_hours=4,
                            priority="medium",
                            dependencies=["setup_dev_env"],
                            agent_specialization="fullstack",
                            tags=["setup", "quality", "linting"],
                            acceptance_criteria=[
                                "ESLint/TSLint configured",
                                "Prettier formatting set up",
                                "Pre-commit hooks working",
                                "Code quality standards documented"
                            ]
                        ),
                        Task(
                            id="setup_testing",
                            title="Initialize Testing Framework",
                            description="Set up unit and integration testing infrastructure",
                            estimated_hours=6,
                            priority="high",
                            dependencies=["setup_dev_env"],
                            agent_specialization="fullstack",
                            tags=["setup", "testing", "framework"],
                            acceptance_criteria=[
                                "Testing framework installed and configured",
                                "Sample tests created and passing",
                                "Test coverage reporting enabled",
                                "Testing documentation created"
                            ]
                        )
                    ]
                ),
                Phase(
                    id="frontend",
                    name="Frontend Development",
                    description="Build user interface and user experience components",
                    estimated_weeks=3,
                    parallel_execution=True,
                    tasks=[
                        Task(
                            id="ui_architecture",
                            title="Design Component Architecture",
                            description="Plan and design the component structure and state management",
                            estimated_hours=12,
                            priority="high",
                            dependencies=["setup_testing"],
                            agent_specialization="frontend",
                            tags=["architecture", "components", "design"],
                            acceptance_criteria=[
                                "Component hierarchy documented",
                                "State management strategy defined",
                                "Design system established",
                                "Routing architecture planned"
                            ]
                        ),
                        Task(
                            id="implement_routing",
                            title="Implement Application Routing",
                            description="Set up client-side routing and navigation",
                            estimated_hours=8,
                            priority="high",
                            dependencies=["ui_architecture"],
                            agent_specialization="frontend",
                            tags=["routing", "navigation", "spa"],
                            acceptance_criteria=[
                                "Router configured with all main routes",
                                "Navigation components implemented",
                                "Protected routes working",
                                "URL parameters handling correctly"
                            ]
                        ),
                        Task(
                            id="build_components",
                            title="Build Core UI Components",
                            description="Implement reusable UI components and layouts",
                            estimated_hours=24,
                            priority="high",
                            dependencies=["ui_architecture"],
                            agent_specialization="frontend",
                            tags=["components", "ui", "reusable"],
                            acceptance_criteria=[
                                "Core components implemented and tested",
                                "Component library documented",
                                "Consistent styling across components",
                                "Accessibility standards met"
                            ]
                        ),
                        Task(
                            id="responsive_design",
                            title="Implement Responsive Design",
                            description="Ensure application works across different screen sizes",
                            estimated_hours=16,
                            priority="medium",
                            dependencies=["build_components"],
                            agent_specialization="frontend",
                            tags=["responsive", "mobile", "css"],
                            acceptance_criteria=[
                                "Mobile-first design implemented",
                                "Breakpoints defined and working",
                                "Touch interactions optimized",
                                "Cross-device testing completed"
                            ]
                        ),
                        Task(
                            id="state_management",
                            title="Implement State Management",
                            description="Set up global state management and data flow",
                            estimated_hours=12,
                            priority="high",
                            dependencies=["implement_routing"],
                            agent_specialization="frontend",
                            tags=["state", "management", "data-flow"],
                            acceptance_criteria=[
                                "State management library integrated",
                                "Global state structure defined",
                                "Actions and reducers implemented",
                                "State persistence configured"
                            ]
                        )
                    ]
                ),
                Phase(
                    id="backend_integration",
                    name="Backend Integration",
                    description="Connect frontend to backend services and APIs",
                    estimated_weeks=2,
                    parallel_execution=True,
                    tasks=[
                        Task(
                            id="api_client",
                            title="Set Up API Client",
                            description="Configure HTTP client and API communication layer",
                            estimated_hours=8,
                            priority="high",
                            dependencies=["state_management"],
                            agent_specialization="fullstack",
                            tags=["api", "http", "client"],
                            acceptance_criteria=[
                                "HTTP client configured with interceptors",
                                "API base URLs and endpoints defined",
                                "Request/response transformation implemented",
                                "Error handling mechanisms in place"
                            ]
                        ),
                        Task(
                            id="authentication",
                            title="Implement Authentication",
                            description="Add user authentication and authorization",
                            estimated_hours=16,
                            priority="high",
                            dependencies=["api_client"],
                            agent_specialization="fullstack",
                            tags=["auth", "security", "login"],
                            acceptance_criteria=[
                                "Login/logout functionality working",
                                "Token management implemented",
                                "Protected routes secured",
                                "User session persistence working"
                            ]
                        ),
                        Task(
                            id="data_fetching",
                            title="Implement Data Fetching Logic",
                            description="Add data fetching, caching, and synchronization",
                            estimated_hours=12,
                            priority="high",
                            dependencies=["api_client"],
                            agent_specialization="fullstack",
                            tags=["data", "fetching", "cache"],
                            acceptance_criteria=[
                                "Data fetching patterns established",
                                "Loading states implemented",
                                "Caching strategy working",
                                "Real-time updates functional"
                            ]
                        ),
                        Task(
                            id="error_handling",
                            title="Add Comprehensive Error Handling",
                            description="Implement error boundaries and user-friendly error messages",
                            estimated_hours=8,
                            priority="medium",
                            dependencies=["data_fetching"],
                            agent_specialization="fullstack",
                            tags=["error", "handling", "ux"],
                            acceptance_criteria=[
                                "Error boundaries implemented",
                                "User-friendly error messages displayed",
                                "Retry mechanisms in place",
                                "Error logging configured"
                            ]
                        ),
                        Task(
                            id="loading_states",
                            title="Implement Loading and Empty States",
                            description="Add loading indicators and empty state handling",
                            estimated_hours=6,
                            priority="medium",
                            dependencies=["data_fetching"],
                            agent_specialization="frontend",
                            tags=["loading", "empty-state", "ux"],
                            acceptance_criteria=[
                                "Loading indicators for all async operations",
                                "Skeleton screens implemented",
                                "Empty state designs implemented",
                                "Progressive loading optimized"
                            ]
                        )
                    ]
                ),
                Phase(
                    id="testing_quality",
                    name="Testing & Quality Assurance",
                    description="Comprehensive testing and code quality assurance",
                    estimated_weeks=2,
                    parallel_execution=True,
                    tasks=[
                        Task(
                            id="unit_tests",
                            title="Write Unit Tests",
                            description="Create comprehensive unit tests for components and utilities",
                            estimated_hours=20,
                            priority="high",
                            dependencies=["error_handling", "loading_states"],
                            agent_specialization="fullstack",
                            tags=["testing", "unit", "coverage"],
                            acceptance_criteria=[
                                "80%+ code coverage achieved",
                                "All critical functions tested",
                                "Test suite runs in CI/CD",
                                "Test documentation created"
                            ]
                        ),
                        Task(
                            id="integration_tests",
                            title="Add Integration Tests",
                            description="Test component interactions and API integrations",
                            estimated_hours=16,
                            priority="high",
                            dependencies=["unit_tests"],
                            agent_specialization="fullstack",
                            tags=["testing", "integration", "api"],
                            acceptance_criteria=[
                                "API integration tests passing",
                                "Component interaction tests implemented",
                                "Database integration tested",
                                "Mock services configured"
                            ]
                        ),
                        Task(
                            id="e2e_tests",
                            title="End-to-End Testing",
                            description="Create automated end-to-end user journey tests",
                            estimated_hours=12,
                            priority="medium",
                            dependencies=["integration_tests"],
                            agent_specialization="qa",
                            tags=["testing", "e2e", "automation"],
                            acceptance_criteria=[
                                "Critical user journeys automated",
                                "Cross-browser testing implemented",
                                "Test data management working",
                                "E2E tests run in CI/CD"
                            ]
                        ),
                        Task(
                            id="performance_testing",
                            title="Performance Testing & Optimization",
                            description="Test and optimize application performance",
                            estimated_hours=8,
                            priority="medium",
                            dependencies=["integration_tests"],
                            agent_specialization="fullstack",
                            tags=["performance", "optimization", "metrics"],
                            acceptance_criteria=[
                                "Performance benchmarks established",
                                "Load time optimization completed",
                                "Memory usage optimized",
                                "Performance monitoring configured"
                            ]
                        ),
                        Task(
                            id="code_review",
                            title="Code Review and Refactoring",
                            description="Comprehensive code review and refactoring session",
                            estimated_hours=12,
                            priority="medium",
                            dependencies=["unit_tests"],
                            agent_specialization="senior",
                            tags=["review", "refactoring", "quality"],
                            acceptance_criteria=[
                                "Code review completed for all components",
                                "Technical debt documented and addressed",
                                "Code quality metrics improved",
                                "Best practices documentation updated"
                            ]
                        )
                    ]
                ),
                Phase(
                    id="deployment",
                    name="Deployment & Production",
                    description="Deploy application to production with monitoring",
                    estimated_weeks=1,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="ci_cd_pipeline",
                            title="Set Up CI/CD Pipeline",
                            description="Configure automated build, test, and deployment pipeline",
                            estimated_hours=12,
                            priority="high",
                            dependencies=["e2e_tests", "performance_testing"],
                            agent_specialization="devops",
                            tags=["cicd", "automation", "deployment"],
                            acceptance_criteria=[
                                "Automated build pipeline working",
                                "Test automation integrated",
                                "Deployment automation configured",
                                "Rollback mechanisms in place"
                            ]
                        ),
                        Task(
                            id="production_environment",
                            title="Configure Production Environment",
                            description="Set up and configure production infrastructure",
                            estimated_hours=8,
                            priority="high",
                            dependencies=["ci_cd_pipeline"],
                            agent_specialization="devops",
                            tags=["production", "infrastructure", "config"],
                            acceptance_criteria=[
                                "Production environment provisioned",
                                "Environment variables configured",
                                "SSL certificates installed",
                                "Security configurations applied"
                            ]
                        ),
                        Task(
                            id="monitoring_analytics",
                            title="Add Monitoring and Analytics",
                            description="Implement application monitoring and user analytics",
                            estimated_hours=6,
                            priority="medium",
                            dependencies=["production_environment"],
                            agent_specialization="devops",
                            tags=["monitoring", "analytics", "observability"],
                            acceptance_criteria=[
                                "Error monitoring configured",
                                "Performance monitoring active",
                                "User analytics implemented",
                                "Alerting systems configured"
                            ]
                        ),
                        Task(
                            id="performance_optimization",
                            title="Production Performance Optimization",
                            description="Optimize application for production performance",
                            estimated_hours=8,
                            priority="medium",
                            dependencies=["monitoring_analytics"],
                            agent_specialization="fullstack",
                            tags=["optimization", "performance", "production"],
                            acceptance_criteria=[
                                "Bundle size optimized",
                                "Caching strategies implemented",
                                "CDN configuration optimized",
                                "Performance metrics meeting targets"
                            ]
                        ),
                        Task(
                            id="production_deployment",
                            title="Deploy to Production",
                            description="Execute production deployment and go-live",
                            estimated_hours=4,
                            priority="high",
                            dependencies=["performance_optimization"],
                            agent_specialization="devops",
                            tags=["deployment", "production", "go-live"],
                            acceptance_criteria=[
                                "Application successfully deployed",
                                "All critical functionality verified",
                                "Performance metrics within targets",
                                "Monitoring and alerting active"
                            ]
                        )
                    ]
                )
            ],
            total_estimated_weeks=9,
            recommended_team_size=3,
            required_skills=["JavaScript/TypeScript", "React/Vue/Angular", "CSS/HTML", "Git"],
            optional_skills=["Node.js", "Docker", "AWS/Azure", "Testing Frameworks"],
            success_metrics=[
                "Application loads in under 3 seconds",
                "99.9% uptime achieved",
                "All critical user journeys working",
                "80%+ test coverage maintained",
                "Zero critical security vulnerabilities"
            ]
        )
        
        # API Service Template
        templates["api_service"] = WorkflowTemplate(
            id="api_service",
            name="API Service Development",
            description="Complete workflow for developing RESTful API services",
            project_type=ProjectType.API_SERVICE,
            phases=[
                Phase(
                    id="architecture",
                    name="Architecture & Design",
                    description="Design API architecture and data models",
                    estimated_weeks=1,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="api_design",
                            title="Design API Architecture",
                            description="Define API endpoints, request/response schemas, and architecture",
                            estimated_hours=12,
                            priority="high",
                            dependencies=[],
                            agent_specialization="backend",
                            tags=["architecture", "api", "design"],
                            acceptance_criteria=[
                                "API specification documented (OpenAPI/Swagger)",
                                "Endpoint design follows REST conventions",
                                "Authentication strategy defined",
                                "Rate limiting strategy planned"
                            ]
                        ),
                        Task(
                            id="data_models",
                            title="Define Data Models",
                            description="Design database schema and data models",
                            estimated_hours=8,
                            priority="high",
                            dependencies=["api_design"],
                            agent_specialization="backend",
                            tags=["database", "models", "schema"],
                            acceptance_criteria=[
                                "Database schema designed",
                                "Data models defined",
                                "Relationships mapped",
                                "Migration strategy planned"
                            ]
                        ),
                        Task(
                            id="database_schema",
                            title="Plan Database Schema",
                            description="Design database tables, indexes, and constraints",
                            estimated_hours=6,
                            priority="high",
                            dependencies=["data_models"],
                            agent_specialization="backend",
                            tags=["database", "schema", "sql"],
                            acceptance_criteria=[
                                "Database tables designed",
                                "Indexes planned for performance",
                                "Constraints and validations defined",
                                "Migration scripts outlined"
                            ]
                        ),
                        Task(
                            id="auth_design",
                            title="Design Authentication System",
                            description="Plan authentication and authorization mechanisms",
                            estimated_hours=6,
                            priority="high",
                            dependencies=["api_design"],
                            agent_specialization="security",
                            tags=["authentication", "security", "authorization"],
                            acceptance_criteria=[
                                "Authentication method selected (JWT/OAuth)",
                                "User roles and permissions defined",
                                "Security policies documented",
                                "Token management strategy planned"
                            ]
                        ),
                        Task(
                            id="api_documentation",
                            title="Create API Documentation",
                            description="Document API endpoints and usage examples",
                            estimated_hours=8,
                            priority="medium",
                            dependencies=["api_design"],
                            agent_specialization="backend",
                            tags=["documentation", "api", "swagger"],
                            acceptance_criteria=[
                                "OpenAPI/Swagger documentation created",
                                "Usage examples provided",
                                "Error codes documented",
                                "Rate limiting documented"
                            ]
                        )
                    ]
                )
                # Additional phases would be added here following the same pattern
            ],
            total_estimated_weeks=6,
            recommended_team_size=2,
            required_skills=["Python/Java/Node.js", "SQL", "REST APIs", "Git"],
            optional_skills=["Docker", "Kubernetes", "AWS/GCP", "Redis"],
            success_metrics=[
                "API response time under 200ms",
                "99.5% API uptime",
                "Complete API documentation",
                "Zero data security breaches",
                "Automated testing coverage >90%"
            ]
        )
        
        # ML Project Template
        templates["ml_project"] = WorkflowTemplate(
            id="ml_project",
            name="Machine Learning Project",
            description="Complete workflow for machine learning project development",
            project_type=ProjectType.ML_PROJECT,
            phases=[
                Phase(
                    id="data_exploration",
                    name="Data Exploration & Analysis",
                    description="Understand and analyze the dataset",
                    estimated_weeks=2,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="data_collection",
                            title="Collect and Validate Datasets",
                            description="Gather datasets and validate data quality",
                            estimated_hours=16,
                            priority="high",
                            dependencies=[],
                            agent_specialization="data_scientist",
                            tags=["data", "collection", "validation"],
                            acceptance_criteria=[
                                "Datasets collected from all sources",
                                "Data quality assessment completed",
                                "Data lineage documented",
                                "Privacy and compliance checks passed"
                            ]
                        ),
                        Task(
                            id="exploratory_analysis",
                            title="Perform Exploratory Data Analysis",
                            description="Conduct comprehensive EDA to understand data patterns",
                            estimated_hours=20,
                            priority="high",
                            dependencies=["data_collection"],
                            agent_specialization="data_scientist",
                            tags=["eda", "analysis", "patterns"],
                            acceptance_criteria=[
                                "Statistical summary of all variables",
                                "Data distributions analyzed",
                                "Correlations and relationships identified",
                                "Outliers and anomalies documented"
                            ]
                        ),
                        Task(
                            id="data_quality_issues",
                            title="Identify Data Quality Issues",
                            description="Document and plan resolution for data quality issues",
                            estimated_hours=8,
                            priority="high",
                            dependencies=["exploratory_analysis"],
                            agent_specialization="data_scientist",
                            tags=["quality", "issues", "cleaning"],
                            acceptance_criteria=[
                                "Missing data patterns analyzed",
                                "Data inconsistencies identified",
                                "Quality issues prioritized",
                                "Cleaning strategy defined"
                            ]
                        ),
                        Task(
                            id="success_metrics",
                            title="Define Success Metrics",
                            description="Establish clear success criteria and evaluation metrics",
                            estimated_hours=4,
                            priority="high",
                            dependencies=["exploratory_analysis"],
                            agent_specialization="data_scientist",
                            tags=["metrics", "evaluation", "kpi"],
                            acceptance_criteria=[
                                "Business success metrics defined",
                                "Technical performance metrics established",
                                "Baseline performance measured",
                                "Success criteria documented"
                            ]
                        ),
                        Task(
                            id="data_visualization",
                            title="Create Data Visualizations",
                            description="Develop visualizations to communicate findings",
                            estimated_hours=12,
                            priority="medium",
                            dependencies=["data_quality_issues"],
                            agent_specialization="data_scientist",
                            tags=["visualization", "communication", "insights"],
                            acceptance_criteria=[
                                "Key insights visualized",
                                "Interactive dashboards created",
                                "Findings documented in notebooks",
                                "Stakeholder presentation prepared"
                            ]
                        )
                    ]
                )
                # Additional phases would be added here
            ],
            total_estimated_weeks=12,
            recommended_team_size=2,
            required_skills=["Python", "Pandas", "Scikit-learn", "Statistics"],
            optional_skills=["TensorFlow/PyTorch", "MLOps", "Cloud ML", "Spark"],
            success_metrics=[
                "Model accuracy meets business requirements",
                "Model performance is reproducible",
                "Data pipeline is automated",
                "Model monitoring is in place",
                "Business impact is measurable"
            ]
        )
        
        # Game Development Template
        templates["game_dev"] = WorkflowTemplate(
            id="game_dev",
            name="Game Development Project",
            description="Complete workflow for game development projects",
            project_type=ProjectType.GAME_DEV,
            phases=[
                Phase(
                    id="concept_design",
                    name="Concept & Design",
                    description="Define game concept, mechanics, and design",
                    estimated_weeks=2,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="game_concept",
                            title="Define Game Concept and Mechanics",
                            description="Create detailed game design document with core mechanics",
                            estimated_hours=16,
                            priority="high",
                            dependencies=[],
                            agent_specialization="game_designer",
                            tags=["design", "concept", "mechanics"],
                            acceptance_criteria=[
                                "Game concept document created",
                                "Core mechanics defined",
                                "Target audience identified",
                                "Unique selling points established"
                            ]
                        ),
                        Task(
                            id="level_design",
                            title="Design Level Architecture",
                            description="Plan level progression and difficulty curve",
                            estimated_hours=12,
                            priority="high",
                            dependencies=["game_concept"],
                            agent_specialization="level_designer",
                            tags=["levels", "design", "progression"],
                            acceptance_criteria=[
                                "Level flow documented",
                                "Difficulty curve planned",
                                "Tutorial levels designed",
                                "Boss encounters outlined"
                            ]
                        ),
                        Task(
                            id="art_style",
                            title="Create Art Style Guide",
                            description="Define visual aesthetics and art direction",
                            estimated_hours=20,
                            priority="high",
                            dependencies=["game_concept"],
                            agent_specialization="art_director",
                            tags=["art", "visuals", "style"],
                            acceptance_criteria=[
                                "Art style guide created",
                                "Color palette defined",
                                "Character design concepts",
                                "Environment style established"
                            ]
                        )
                    ]
                ),
                Phase(
                    id="prototype",
                    name="Prototype Development",
                    description="Build core gameplay prototype",
                    estimated_weeks=3,
                    parallel_execution=True,
                    tasks=[
                        Task(
                            id="engine_setup",
                            title="Set Up Game Engine Project",
                            description="Configure game engine and project structure",
                            estimated_hours=8,
                            priority="high",
                            dependencies=[],
                            agent_specialization="game_programmer",
                            tags=["engine", "setup", "configuration"],
                            acceptance_criteria=[
                                "Game engine project created",
                                "Version control configured",
                                "Build pipeline established",
                                "Development environment ready"
                            ]
                        ),
                        Task(
                            id="player_controls",
                            title="Implement Player Controls",
                            description="Create responsive player movement and actions",
                            estimated_hours=16,
                            priority="high",
                            dependencies=["engine_setup"],
                            agent_specialization="gameplay_programmer",
                            tags=["controls", "player", "input"],
                            acceptance_criteria=[
                                "Player movement implemented",
                                "Action system working",
                                "Controls feel responsive",
                                "Input mapping configurable"
                            ]
                        ),
                        Task(
                            id="prototype_level",
                            title="Build Prototype Level",
                            description="Create playable prototype showcasing core mechanics",
                            estimated_hours=20,
                            priority="high",
                            dependencies=["player_controls"],
                            agent_specialization="level_designer",
                            tags=["prototype", "level", "gameplay"],
                            acceptance_criteria=[
                                "Prototype level playable",
                                "Core mechanics demonstrated",
                                "Basic enemies/obstacles added",
                                "Win/lose conditions working"
                            ]
                        )
                    ]
                )
            ],
            total_estimated_weeks=16,
            recommended_team_size=4,
            required_skills=["C#/C++", "Game Engine (Unity/Unreal)", "3D Modeling", "Game Design"],
            optional_skills=["Shader Programming", "AI Programming", "Audio Design", "Level Design"],
            success_metrics=[
                "Game runs at target framerate",
                "Core gameplay loop is engaging",
                "All planned features implemented",
                "Game is bug-free and polished",
                "Positive player feedback received"
            ]
        )
        
        # Blockchain/Smart Contract Template
        templates["blockchain"] = WorkflowTemplate(
            id="blockchain",
            name="Blockchain/Smart Contract Development",
            description="Complete workflow for blockchain and smart contract projects",
            project_type=ProjectType.BLOCKCHAIN,
            phases=[
                Phase(
                    id="architecture_design",
                    name="Architecture & Design",
                    description="Design blockchain architecture and token economics",
                    estimated_weeks=2,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="token_economics",
                            title="Define Token Economics",
                            description="Design tokenomics model and economic incentives",
                            estimated_hours=16,
                            priority="high",
                            dependencies=[],
                            agent_specialization="blockchain_architect",
                            tags=["tokenomics", "economics", "design"],
                            acceptance_criteria=[
                                "Token distribution model defined",
                                "Economic incentives designed",
                                "Inflation/deflation mechanics planned",
                                "Utility clearly defined"
                            ]
                        ),
                        Task(
                            id="contract_architecture",
                            title="Design Smart Contract Architecture",
                            description="Plan contract structure and interactions",
                            estimated_hours=20,
                            priority="high",
                            dependencies=["token_economics"],
                            agent_specialization="smart_contract_developer",
                            tags=["architecture", "contracts", "design"],
                            acceptance_criteria=[
                                "Contract architecture documented",
                                "State variables defined",
                                "Function interfaces designed",
                                "Upgrade strategy planned"
                            ]
                        ),
                        Task(
                            id="security_model",
                            title="Plan Security Model",
                            description="Design security measures and access controls",
                            estimated_hours=12,
                            priority="high",
                            dependencies=["contract_architecture"],
                            agent_specialization="security_engineer",
                            tags=["security", "access-control", "design"],
                            acceptance_criteria=[
                                "Security model documented",
                                "Access control patterns defined",
                                "Attack vectors identified",
                                "Mitigation strategies planned"
                            ]
                        )
                    ]
                ),
                Phase(
                    id="smart_contract_dev",
                    name="Smart Contract Development",
                    description="Implement and test smart contracts",
                    estimated_weeks=4,
                    parallel_execution=False,
                    tasks=[
                        Task(
                            id="dev_environment",
                            title="Set Up Development Environment",
                            description="Configure blockchain development tools and framework",
                            estimated_hours=8,
                            priority="high",
                            dependencies=[],
                            agent_specialization="blockchain_developer",
                            tags=["setup", "environment", "tools"],
                            acceptance_criteria=[
                                "Development framework configured",
                                "Testing environment ready",
                                "Deployment scripts created",
                                "Version control established"
                            ]
                        ),
                        Task(
                            id="core_contracts",
                            title="Write Core Smart Contracts",
                            description="Implement main contract logic and functionality",
                            estimated_hours=40,
                            priority="high",
                            dependencies=["dev_environment"],
                            agent_specialization="smart_contract_developer",
                            tags=["development", "contracts", "solidity"],
                            acceptance_criteria=[
                                "Core contracts implemented",
                                "Business logic working",
                                "Gas optimization applied",
                                "Code follows best practices"
                            ]
                        ),
                        Task(
                            id="contract_testing",
                            title="Write Comprehensive Tests",
                            description="Create unit and integration tests for all contracts",
                            estimated_hours=24,
                            priority="high",
                            dependencies=["core_contracts"],
                            agent_specialization="blockchain_developer",
                            tags=["testing", "unit-tests", "coverage"],
                            acceptance_criteria=[
                                "100% function coverage",
                                "Edge cases tested",
                                "Gas usage benchmarked",
                                "Integration tests passing"
                            ]
                        )
                    ]
                )
            ],
            total_estimated_weeks=10,
            recommended_team_size=3,
            required_skills=["Solidity", "Web3.js/Ethers.js", "Smart Contract Security", "DeFi Protocols"],
            optional_skills=["Rust (for Solana)", "Cairo (for StarkNet)", "Vyper", "Formal Verification"],
            success_metrics=[
                "Smart contracts pass security audit",
                "Gas costs are optimized",
                "All tests passing with 100% coverage",
                "Contracts deployed successfully",
                "No critical vulnerabilities found"
            ]
        )
        
        return templates

    def _load_task_generators(self) -> Dict[str, Any]:
        """Load task generators for dynamic task creation"""
        return {
            "technology_setup": {
                "react": [
                    "Set up Create React App or Next.js",
                    "Configure React Router for navigation",
                    "Set up state management (Redux/Context)",
                    "Configure styled-components or CSS modules"
                ],
                "vue": [
                    "Initialize Vue.js project with Vue CLI",
                    "Set up Vue Router for navigation",
                    "Configure Vuex for state management",
                    "Set up component library (Vuetify/Quasar)"
                ],
                "angular": [
                    "Create Angular project with Angular CLI",
                    "Set up Angular routing",
                    "Configure NgRx for state management",
                    "Set up Angular Material UI components"
                ],
                "django": [
                    "Set up Django project structure",
                    "Configure Django REST Framework",
                    "Set up database models and migrations",
                    "Configure Django authentication"
                ],
                "flask": [
                    "Initialize Flask application",
                    "Set up Flask-RESTful for API endpoints",
                    "Configure SQLAlchemy for database ORM",
                    "Set up Flask-JWT for authentication"
                ],
                "fastapi": [
                    "Set up FastAPI project structure",
                    "Configure Pydantic models for validation",
                    "Set up SQLAlchemy for database operations",
                    "Configure OAuth2 with JWT tokens"
                ]
            },
            "database_setup": {
                "postgresql": [
                    "Set up PostgreSQL database",
                    "Create database schema and tables",
                    "Set up connection pooling",
                    "Configure database migrations"
                ],
                "mongodb": [
                    "Set up MongoDB database",
                    "Design document schemas",
                    "Set up database indexing",
                    "Configure aggregation pipelines"
                ],
                "redis": [
                    "Set up Redis for caching",
                    "Configure session storage",
                    "Set up pub/sub messaging",
                    "Configure data persistence"
                ]
            },
            "testing_setup": {
                "jest": [
                    "Configure Jest testing framework",
                    "Set up test coverage reporting",
                    "Create unit test templates",
                    "Set up mocking and fixtures"
                ],
                "pytest": [
                    "Configure pytest framework",
                    "Set up test fixtures and factories",
                    "Configure test coverage with pytest-cov",
                    "Set up integration test database"
                ]
            },
            "deployment_setup": {
                "docker": [
                    "Create Dockerfile for application",
                    "Set up docker-compose for development",
                    "Configure multi-stage builds",
                    "Set up container health checks"
                ],
                "kubernetes": [
                    "Create Kubernetes deployment manifests",
                    "Set up service and ingress configurations",
                    "Configure ConfigMaps and Secrets",
                    "Set up horizontal pod autoscaling"
                ],
                "aws": [
                    "Set up AWS infrastructure with Terraform",
                    "Configure CI/CD with AWS CodePipeline",
                    "Set up monitoring with CloudWatch",
                    "Configure load balancing and auto-scaling"
                ]
            }
        }

    def generate_workflow_from_analysis(self, analysis: AnalysisResult, 
                                      project_name: str = None) -> WorkflowTemplate:
        """Generate a customized workflow template based on project analysis"""
        base_template = self.templates.get(analysis.project_type.value)
        
        if not base_template:
            # Create a generic template
            base_template = self._create_generic_template(analysis)
        
        # Customize template based on analysis
        customized_template = self._customize_template(base_template, analysis, project_name)
        
        return customized_template

    def _create_generic_template(self, analysis: AnalysisResult) -> WorkflowTemplate:
        """Create a generic workflow template for unrecognized project types"""
        return WorkflowTemplate(
            id="generic",
            name="Generic Development Workflow",
            description="Customizable workflow for general software development",
            project_type=analysis.project_type,
            phases=[
                Phase(
                    id="setup",
                    name="Project Setup",
                    description="Initialize project and development environment",
                    estimated_weeks=1,
                    parallel_execution=False,
                    tasks=self._generate_setup_tasks(analysis.tech_stack)
                ),
                Phase(
                    id="development",
                    name="Core Development",
                    description="Implement main project functionality",
                    estimated_weeks=4,
                    parallel_execution=True,
                    tasks=self._generate_development_tasks(analysis)
                ),
                Phase(
                    id="testing",
                    name="Testing & Quality Assurance",
                    description="Comprehensive testing and quality checks",
                    estimated_weeks=2,
                    parallel_execution=True,
                    tasks=self._generate_testing_tasks(analysis.tech_stack)
                ),
                Phase(
                    id="deployment",
                    name="Deployment",
                    description="Deploy and monitor application",
                    estimated_weeks=1,
                    parallel_execution=False,
                    tasks=self._generate_deployment_tasks(analysis.tech_stack)
                )
            ],
            total_estimated_weeks=8,
            recommended_team_size=analysis.team_size_recommendation,
            required_skills=analysis.tech_stack.languages + analysis.tech_stack.frameworks[:2],
            optional_skills=analysis.tech_stack.databases + analysis.tech_stack.cloud_services,
            success_metrics=[
                "All core functionality implemented",
                "Test coverage above 80%",
                "Application deployed successfully",
                "Performance requirements met"
            ]
        )

    def _customize_template(self, template: WorkflowTemplate, analysis: AnalysisResult, 
                          project_name: str = None) -> WorkflowTemplate:
        """Customize template based on specific project analysis"""
        customized = template
        
        # Update project name if provided
        if project_name:
            customized.name = f"{project_name} - {template.name}"
        
        # Adjust team size based on analysis
        customized.recommended_team_size = analysis.team_size_recommendation
        
        # Add technology-specific tasks
        for phase in customized.phases:
            phase.tasks = self._enhance_tasks_with_tech_stack(phase.tasks, analysis.tech_stack)
        
        # Adjust time estimates based on complexity
        complexity_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.3}.get(
            analysis.estimated_complexity, 1.0
        )
        
        for phase in customized.phases:
            phase.estimated_weeks = max(1, int(phase.estimated_weeks * complexity_multiplier))
        
        customized.total_estimated_weeks = sum(phase.estimated_weeks for phase in customized.phases)
        
        return customized

    def _generate_setup_tasks(self, tech_stack) -> List[Task]:
        """Generate setup tasks based on technology stack"""
        tasks = []
        task_id = 0
        
        # Repository setup (always needed)
        tasks.append(Task(
            id=f"setup_{task_id}",
            title="Initialize Repository",
            description="Set up version control and project structure",
            estimated_hours=4,
            priority="high",
            dependencies=[],
            agent_specialization="devops",
            tags=["setup", "git"],
            acceptance_criteria=["Repository initialized with proper structure"]
        ))
        task_id += 1
        
        # Language-specific setup
        for lang in tech_stack.languages:
            if lang in self.task_generators["technology_setup"]:
                for task_title in self.task_generators["technology_setup"][lang]:
                    tasks.append(Task(
                        id=f"setup_{task_id}",
                        title=task_title,
                        description=f"Configure {lang} development environment",
                        estimated_hours=6,
                        priority="high",
                        dependencies=[f"setup_{task_id-1}"] if task_id > 0 else [],
                        agent_specialization="fullstack",
                        tags=["setup", lang],
                        acceptance_criteria=[f"{lang} environment properly configured"]
                    ))
                    task_id += 1
        
        # Framework-specific setup
        for framework in tech_stack.frameworks:
            if framework in self.task_generators["technology_setup"]:
                for task_title in self.task_generators["technology_setup"][framework]:
                    tasks.append(Task(
                        id=f"setup_{task_id}",
                        title=task_title,
                        description=f"Set up {framework} framework",
                        estimated_hours=4,
                        priority="medium",
                        dependencies=[f"setup_{max(0, task_id-2)}"],
                        agent_specialization="fullstack",
                        tags=["setup", framework],
                        acceptance_criteria=[f"{framework} framework configured and working"]
                    ))
                    task_id += 1
        
        return tasks

    def _generate_development_tasks(self, analysis: AnalysisResult) -> List[Task]:
        """Generate development tasks based on project analysis"""
        tasks = []
        task_id = 0
        
        # Core development tasks based on project structure
        if analysis.structure.has_api:
            tasks.append(Task(
                id=f"dev_{task_id}",
                title="Implement API Endpoints",
                description="Create RESTful API endpoints for core functionality",
                estimated_hours=20,
                priority="high",
                dependencies=[],
                agent_specialization="backend",
                tags=["api", "backend"],
                acceptance_criteria=["All API endpoints implemented and documented"]
            ))
            task_id += 1
        
        if analysis.structure.has_frontend:
            tasks.append(Task(
                id=f"dev_{task_id}",
                title="Build User Interface",
                description="Implement user interface components and layouts",
                estimated_hours=24,
                priority="high",
                dependencies=[],
                agent_specialization="frontend",
                tags=["ui", "frontend"],
                acceptance_criteria=["User interface implemented with responsive design"]
            ))
            task_id += 1
        
        if analysis.structure.has_database:
            tasks.append(Task(
                id=f"dev_{task_id}",
                title="Implement Data Layer",
                description="Create database models and data access logic",
                estimated_hours=16,
                priority="high",
                dependencies=[],
                agent_specialization="backend",
                tags=["database", "models"],
                acceptance_criteria=["Database models implemented with proper relationships"]
            ))
            task_id += 1
        
        # Add authentication if patterns suggest it
        if "authentication" in [pattern.lower() for pattern in analysis.detected_patterns]:
            tasks.append(Task(
                id=f"dev_{task_id}",
                title="Implement Authentication",
                description="Add user authentication and authorization",
                estimated_hours=12,
                priority="high",
                dependencies=[f"dev_{max(0, task_id-1)}"] if task_id > 0 else [],
                agent_specialization="fullstack",
                tags=["auth", "security"],
                acceptance_criteria=["Authentication system working with proper security"]
            ))
            task_id += 1
        
        return tasks

    def _generate_testing_tasks(self, tech_stack) -> List[Task]:
        """Generate testing tasks based on technology stack"""
        tasks = []
        task_id = 0
        
        # Determine testing framework
        testing_framework = None
        if "jest" in tech_stack.testing_frameworks:
            testing_framework = "jest"
        elif "pytest" in tech_stack.testing_frameworks:
            testing_framework = "pytest"
        
        if testing_framework and testing_framework in self.task_generators["testing_setup"]:
            for task_title in self.task_generators["testing_setup"][testing_framework]:
                tasks.append(Task(
                    id=f"test_{task_id}",
                    title=task_title,
                    description=f"Set up {testing_framework} testing infrastructure",
                    estimated_hours=6,
                    priority="high",
                    dependencies=[f"test_{task_id-1}"] if task_id > 0 else [],
                    agent_specialization="fullstack",
                    tags=["testing", testing_framework],
                    acceptance_criteria=[f"{testing_framework} testing framework configured"]
                ))
                task_id += 1
        
        # Add general testing tasks
        tasks.extend([
            Task(
                id=f"test_{task_id}",
                title="Write Unit Tests",
                description="Create comprehensive unit tests for core functionality",
                estimated_hours=16,
                priority="high",
                dependencies=[f"test_{max(0, task_id-1)}"] if task_id > 0 else [],
                agent_specialization="fullstack",
                tags=["testing", "unit"],
                acceptance_criteria=["Unit tests achieve 80%+ code coverage"]
            ),
            Task(
                id=f"test_{task_id+1}",
                title="Add Integration Tests",
                description="Test component interactions and system integration",
                estimated_hours=12,
                priority="medium",
                dependencies=[f"test_{task_id}"],
                agent_specialization="fullstack",
                tags=["testing", "integration"],
                acceptance_criteria=["Integration tests cover main user workflows"]
            )
        ])
        
        return tasks

    def _generate_deployment_tasks(self, tech_stack) -> List[Task]:
        """Generate deployment tasks based on technology stack"""
        tasks = []
        task_id = 0
        
        # Check for containerization
        if "docker" in tech_stack.deployment_tools:
            for task_title in self.task_generators["deployment_setup"]["docker"]:
                tasks.append(Task(
                    id=f"deploy_{task_id}",
                    title=task_title,
                    description="Set up Docker containerization",
                    estimated_hours=4,
                    priority="high",
                    dependencies=[f"deploy_{task_id-1}"] if task_id > 0 else [],
                    agent_specialization="devops",
                    tags=["deployment", "docker"],
                    acceptance_criteria=["Application containerized and running in Docker"]
                ))
                task_id += 1
        
        # Add CI/CD pipeline
        tasks.append(Task(
            id=f"deploy_{task_id}",
            title="Set Up CI/CD Pipeline",
            description="Configure automated build and deployment pipeline",
            estimated_hours=8,
            priority="high",
            dependencies=[f"deploy_{max(0, task_id-1)}"] if task_id > 0 else [],
            agent_specialization="devops",
            tags=["cicd", "automation"],
            acceptance_criteria=["CI/CD pipeline working with automated deployments"]
        ))
        task_id += 1
        
        # Production deployment
        tasks.append(Task(
            id=f"deploy_{task_id}",
            title="Deploy to Production",
            description="Deploy application to production environment",
            estimated_hours=6,
            priority="high",
            dependencies=[f"deploy_{task_id-1}"],
            agent_specialization="devops",
            tags=["deployment", "production"],
            acceptance_criteria=["Application successfully deployed and monitored"]
        ))
        
        return tasks

    def _enhance_tasks_with_tech_stack(self, tasks: List[Task], tech_stack) -> List[Task]:
        """Enhance existing tasks with technology-specific details"""
        enhanced_tasks = []
        
        for task in tasks:
            enhanced_task = task
            
            # Add technology-specific acceptance criteria
            if any(tech in task.tags for tech in tech_stack.languages):
                enhanced_task.acceptance_criteria.extend([
                    f"Code follows {tech} best practices" for tech in tech_stack.languages 
                    if tech in task.tags
                ])
            
            # Add framework-specific requirements
            if any(fw in task.tags for fw in tech_stack.frameworks):
                enhanced_task.acceptance_criteria.extend([
                    f"{fw} framework integration working properly" for fw in tech_stack.frameworks
                    if fw in task.tags
                ])
            
            enhanced_tasks.append(enhanced_task)
        
        return enhanced_tasks

    def export_workflow_template(self, template: WorkflowTemplate, 
                                format: str = "json") -> str:
        """Export workflow template in specified format"""
        template_dict = asdict(template)
        
        if format.lower() == "json":
            return json.dumps(template_dict, indent=2, default=str)
        elif format.lower() == "yaml":
            return yaml.dump(template_dict, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def import_workflow_template(self, template_data: str, 
                               format: str = "json") -> WorkflowTemplate:
        """Import workflow template from specified format"""
        if format.lower() == "json":
            data = json.loads(template_data)
        elif format.lower() == "yaml":
            data = yaml.safe_load(template_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Convert dict back to WorkflowTemplate
        # This would need proper deserialization logic
        return WorkflowTemplate(**data)

    def get_available_templates(self) -> List[str]:
        """Get list of available workflow template IDs"""
        return list(self.templates.keys())

    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get specific workflow template by ID"""
        return self.templates.get(template_id)

def main():
    """Command-line interface for workflow template engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate workflow templates from project analysis")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file for workflow template")
    parser.add_argument("--format", choices=["json", "yaml"], default="json",
                       help="Output format")
    parser.add_argument("--template", help="Base template to use (optional)")
    
    args = parser.parse_args()
    
    engine = WorkflowTemplateEngine()
    analyzer = ProjectAnalyzer()
    
    try:
        # Analyze project
        analysis = analyzer.analyze_project(args.project_path)
        
        # Generate workflow template
        if args.template:
            base_template = engine.get_template(args.template)
            if not base_template:
                print(f"Template '{args.template}' not found")
                return 1
            workflow = engine._customize_template(base_template, analysis)
        else:
            workflow = engine.generate_workflow_from_analysis(analysis)
        
        # Export template
        output = engine.export_workflow_template(workflow, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Workflow template written to {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error generating workflow template: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())