#!/usr/bin/env python3
"""
Migration Workflows - Detailed workflow templates for different migration types
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

try:
    from .migration_analyzer import MigrationType, MigrationComplexity
except ImportError:
    # When run as a script or imported directly
    from migration_analyzer import MigrationType, MigrationComplexity

@dataclass
class MigrationTask:
    """Represents a specific task in a migration workflow"""
    id: str
    name: str
    description: str
    category: str
    estimated_hours: int
    prerequisites: List[str]
    deliverables: List[str]
    acceptance_criteria: List[str]
    assigned_roles: List[str]
    tools_required: List[str]
    risks: List[str]
    mitigation_strategies: List[str]

@dataclass
class MigrationPhase:
    """Represents a phase in a migration workflow"""
    phase_number: int
    name: str
    description: str
    duration_weeks: int
    objectives: List[str]
    tasks: List[MigrationTask]
    success_criteria: List[str]
    exit_criteria: List[str]
    rollback_plan: str

@dataclass
class MigrationWorkflow:
    """Complete migration workflow template"""
    workflow_id: str
    name: str
    description: str
    migration_type: MigrationType
    complexity: MigrationComplexity
    total_duration_weeks: int
    phases: List[MigrationPhase]
    prerequisites: List[str]
    success_metrics: List[str]
    common_pitfalls: List[str]
    best_practices: List[str]
    required_skills: List[str]
    tools_and_technologies: List[str]

class MigrationWorkflowGenerator:
    """Generates detailed migration workflows based on analysis results"""
    
    def __init__(self):
        self.workflow_templates = self._initialize_workflow_templates()
    
    def _initialize_workflow_templates(self) -> Dict[MigrationType, MigrationWorkflow]:
        """Initialize all migration workflow templates"""
        templates = {}
        
        templates[MigrationType.MONOLITH_TO_MICROSERVICES] = self._create_monolith_to_microservices_workflow()
        templates[MigrationType.DATABASE_MIGRATION] = self._create_database_migration_workflow()
        templates[MigrationType.CLOUD_MIGRATION] = self._create_cloud_migration_workflow()
        templates[MigrationType.LEGACY_MODERNIZATION] = self._create_legacy_modernization_workflow()
        templates[MigrationType.FRAMEWORK_MIGRATION] = self._create_framework_migration_workflow()
        templates[MigrationType.ARCHITECTURE_REFACTORING] = self._create_architecture_refactoring_workflow()
        
        return templates
    
    def generate_workflow(self, migration_type: MigrationType, complexity: MigrationComplexity = None) -> MigrationWorkflow:
        """Generate a workflow for the specified migration type"""
        base_workflow = self.workflow_templates.get(migration_type)
        
        if not base_workflow:
            raise ValueError(f"No workflow template found for {migration_type}")
        
        # Adjust workflow based on complexity
        if complexity:
            return self._adjust_workflow_for_complexity(base_workflow, complexity)
        
        return base_workflow
    
    def _adjust_workflow_for_complexity(self, workflow: MigrationWorkflow, complexity: MigrationComplexity) -> MigrationWorkflow:
        """Adjust workflow duration and tasks based on complexity"""
        multiplier = {
            MigrationComplexity.LOW: 0.7,
            MigrationComplexity.MEDIUM: 1.0,
            MigrationComplexity.HIGH: 1.5,
            MigrationComplexity.CRITICAL: 2.0
        }.get(complexity, 1.0)
        
        # Adjust durations
        adjusted_workflow = workflow
        adjusted_workflow.total_duration_weeks = int(workflow.total_duration_weeks * multiplier)
        
        for phase in adjusted_workflow.phases:
            phase.duration_weeks = int(phase.duration_weeks * multiplier)
            for task in phase.tasks:
                task.estimated_hours = int(task.estimated_hours * multiplier)
        
        # Add complexity-specific considerations
        if complexity in [MigrationComplexity.HIGH, MigrationComplexity.CRITICAL]:
            adjusted_workflow.prerequisites.extend([
                "Senior architecture review",
                "Risk assessment and mitigation plan",
                "Dedicated DevOps support"
            ])
        
        return adjusted_workflow
    
    def _create_monolith_to_microservices_workflow(self) -> MigrationWorkflow:
        """Create detailed monolith to microservices migration workflow"""
        
        # Phase 1: Assessment and Planning
        phase1_tasks = [
            MigrationTask(
                id="assess_current_architecture",
                name="Assess Current Architecture",
                description="Comprehensive analysis of existing monolithic architecture",
                category="analysis",
                estimated_hours=40,
                prerequisites=["Access to codebase", "Architecture documentation"],
                deliverables=["Architecture assessment report", "Domain boundary analysis"],
                acceptance_criteria=[
                    "Complete inventory of system components",
                    "Identified domain boundaries",
                    "Dependency mapping completed"
                ],
                assigned_roles=["Senior Architect", "Lead Developer"],
                tools_required=["Static analysis tools", "Dependency analyzers"],
                risks=["Incomplete understanding of system"],
                mitigation_strategies=["Involve original developers", "Comprehensive code review"]
            ),
            MigrationTask(
                id="identify_service_boundaries",
                name="Identify Service Boundaries",
                description="Define clear boundaries for microservice extraction using Domain-Driven Design",
                category="design",
                estimated_hours=32,
                prerequisites=["Architecture assessment", "Business domain understanding"],
                deliverables=["Service boundary specification", "Data ownership mapping"],
                acceptance_criteria=[
                    "Clear service responsibilities defined",
                    "Minimal cross-service dependencies",
                    "Data ownership boundaries established"
                ],
                assigned_roles=["Domain Expert", "Senior Architect"],
                tools_required=["Domain modeling tools", "Collaboration tools"],
                risks=["Poor boundary definition leading to chatty services"],
                mitigation_strategies=["Domain expert involvement", "Iterative boundary refinement"]
            ),
            MigrationTask(
                id="design_api_contracts",
                name="Design API Contracts",
                description="Define RESTful API contracts for service communication",
                category="design",
                estimated_hours=24,
                prerequisites=["Service boundaries defined"],
                deliverables=["OpenAPI specifications", "API documentation"],
                acceptance_criteria=[
                    "Complete API contracts for all services",
                    "Versioning strategy defined",
                    "Error handling specifications"
                ],
                assigned_roles=["API Designer", "Backend Developer"],
                tools_required=["OpenAPI tools", "API documentation tools"],
                risks=["Breaking API changes during migration"],
                mitigation_strategies=["API versioning strategy", "Backward compatibility"]
            )
        ]
        
        phase1 = MigrationPhase(
            phase_number=1,
            name="Assessment and Planning",
            description="Comprehensive analysis and planning for microservices migration",
            duration_weeks=4,
            objectives=[
                "Understand current architecture",
                "Define service boundaries",
                "Design API contracts",
                "Create migration plan"
            ],
            tasks=phase1_tasks,
            success_criteria=[
                "Clear service boundaries identified",
                "API contracts designed and reviewed",
                "Migration roadmap approved"
            ],
            exit_criteria=[
                "Stakeholder approval of service boundaries",
                "Technical review of API contracts",
                "Migration plan signed off"
            ],
            rollback_plan="Continue with monolithic architecture improvements if migration is deemed too risky"
        )
        
        # Phase 2: Infrastructure Setup
        phase2_tasks = [
            MigrationTask(
                id="setup_service_infrastructure",
                name="Setup Service Infrastructure", 
                description="Prepare infrastructure for microservices deployment",
                category="infrastructure",
                estimated_hours=60,
                prerequisites=["Cloud platform selected", "Infrastructure requirements defined"],
                deliverables=["Container orchestration platform", "Service mesh configuration", "Monitoring setup"],
                acceptance_criteria=[
                    "Kubernetes cluster operational",
                    "Service discovery configured",
                    "Monitoring and logging operational"
                ],
                assigned_roles=["DevOps Engineer", "Site Reliability Engineer"],
                tools_required=["Kubernetes", "Docker", "Prometheus", "Grafana"],
                risks=["Infrastructure complexity", "Operational overhead"],
                mitigation_strategies=["Managed services usage", "Infrastructure as code"]
            ),
            MigrationTask(
                id="implement_api_gateway",
                name="Implement API Gateway",
                description="Deploy and configure API Gateway for request routing",
                category="infrastructure",
                estimated_hours=32,
                prerequisites=["Service infrastructure ready", "API contracts defined"],
                deliverables=["API Gateway deployment", "Routing configuration", "Security policies"],
                acceptance_criteria=[
                    "Request routing functional",
                    "Authentication/authorization working",
                    "Rate limiting configured"
                ],
                assigned_roles=["Backend Developer", "DevOps Engineer"],
                tools_required=["Kong/NGINX/AWS API Gateway", "Authentication service"],
                risks=["Single point of failure", "Performance bottleneck"],
                mitigation_strategies=["High availability setup", "Performance testing"]
            ),
            MigrationTask(
                id="setup_cicd_pipeline",
                name="Setup CI/CD Pipeline",
                description="Configure continuous integration and deployment for microservices",
                category="infrastructure",
                estimated_hours=40,
                prerequisites=["Service infrastructure ready", "Source control strategy defined"],
                deliverables=["CI/CD pipelines", "Automated testing framework", "Deployment automation"],
                acceptance_criteria=[
                    "Automated build and test pipeline",
                    "Automated deployment to staging",
                    "Rollback capabilities"
                ],
                assigned_roles=["DevOps Engineer", "Software Engineer"],
                tools_required=["Jenkins/GitLab CI/GitHub Actions", "Docker", "Testing frameworks"],
                risks=["Pipeline complexity", "Deployment failures"],
                mitigation_strategies=["Pipeline testing", "Gradual rollout capabilities"]
            )
        ]
        
        phase2 = MigrationPhase(
            phase_number=2,
            name="Infrastructure Setup",
            description="Prepare infrastructure and tooling for microservices",
            duration_weeks=6,
            objectives=[
                "Setup container orchestration",
                "Implement API Gateway",
                "Configure CI/CD pipelines",
                "Establish monitoring"
            ],
            tasks=phase2_tasks,
            success_criteria=[
                "Infrastructure fully operational",
                "API Gateway routing requests",
                "CI/CD pipelines functional"
            ],
            exit_criteria=[
                "Load testing passed",
                "Security review completed",
                "Operational procedures documented"
            ],
            rollback_plan="Maintain existing deployment infrastructure during transition"
        )
        
        # Phase 3: Service Extraction (Strangler Fig)
        phase3_tasks = [
            MigrationTask(
                id="implement_first_service",
                name="Implement First Microservice",
                description="Extract the first service using Strangler Fig pattern",
                category="development",
                estimated_hours=120,
                prerequisites=["Infrastructure ready", "Service boundaries defined"],
                deliverables=["Microservice implementation", "Database schema", "API implementation"],
                acceptance_criteria=[
                    "Service functionality matches monolith",
                    "API contracts implemented",
                    "Unit and integration tests passing"
                ],
                assigned_roles=["Backend Developer", "Database Administrator"],
                tools_required=["Programming framework", "Database tools", "Testing frameworks"],
                risks=["Feature parity issues", "Data consistency problems"],
                mitigation_strategies=["Comprehensive testing", "Gradual traffic migration"]
            ),
            MigrationTask(
                id="implement_traffic_routing",
                name="Implement Traffic Routing",
                description="Configure routing to gradually shift traffic to new service",
                category="infrastructure",
                estimated_hours=24,
                prerequisites=["Microservice deployed", "API Gateway configured"],
                deliverables=["Traffic routing rules", "Feature flags", "Monitoring dashboards"],
                acceptance_criteria=[
                    "Traffic can be routed to both old and new service",
                    "Feature flags control traffic distribution",
                    "Real-time monitoring of both services"
                ],
                assigned_roles=["DevOps Engineer", "Backend Developer"],
                tools_required=["Feature flag service", "Load balancer", "Monitoring tools"],
                risks=["Traffic routing failures", "Service inconsistencies"],
                mitigation_strategies=["Gradual rollout", "Automated rollback triggers"]
            ),
            MigrationTask(
                id="migrate_data",
                name="Migrate Service Data",
                description="Migrate data from monolithic database to service-specific database",
                category="data_migration",
                estimated_hours=40,
                prerequisites=["Service database designed", "Data migration scripts"],
                deliverables=["Migrated data", "Data validation reports", "Synchronization mechanisms"],
                acceptance_criteria=[
                    "All data successfully migrated",
                    "Data integrity verified",
                    "Synchronization working during transition"
                ],
                assigned_roles=["Database Administrator", "Backend Developer"],
                tools_required=["Database migration tools", "Data validation scripts"],
                risks=["Data loss", "Data inconsistency", "Downtime"],
                mitigation_strategies=["Comprehensive backups", "Dual-write pattern", "Rollback procedures"]
            )
        ]
        
        phase3 = MigrationPhase(
            phase_number=3,
            name="Service Extraction",
            description="Extract first microservice using Strangler Fig pattern",
            duration_weeks=8,
            objectives=[
                "Implement first microservice",
                "Migrate service data",
                "Route traffic gradually",
                "Verify service functionality"
            ],
            tasks=phase3_tasks,
            success_criteria=[
                "First service handling production traffic",
                "Data migration successful",
                "Performance meets requirements"
            ],
            exit_criteria=[
                "100% traffic routed to new service",
                "Old code removed from monolith",
                "Monitoring confirms service health"
            ],
            rollback_plan="Route traffic back to monolith and disable new service"
        )
        
        # Phase 4: Iteration and Optimization
        phase4_tasks = [
            MigrationTask(
                id="extract_additional_services",
                name="Extract Additional Services",
                description="Apply lessons learned to extract remaining services",
                category="development",
                estimated_hours=200,
                prerequisites=["First service successfully migrated", "Operational procedures established"],
                deliverables=["Additional microservices", "Updated documentation", "Operational runbooks"],
                acceptance_criteria=[
                    "All planned services extracted",
                    "Services operating independently",
                    "Inter-service communication functional"
                ],
                assigned_roles=["Development Team", "DevOps Team"],
                tools_required=["Development frameworks", "Deployment tools", "Monitoring"],
                risks=["Service sprawl", "Operational complexity"],
                mitigation_strategies=["Service governance", "Operational excellence practices"]
            ),
            MigrationTask(
                id="optimize_performance",
                name="Optimize Performance",
                description="Tune performance of microservices architecture",
                category="optimization",
                estimated_hours=60,
                prerequisites=["All services operational", "Performance baseline established"],
                deliverables=["Performance optimization report", "Tuned configurations", "Performance tests"],
                acceptance_criteria=[
                    "Performance meets or exceeds monolith",
                    "Response times within SLA",
                    "Resource utilization optimized"
                ],
                assigned_roles=["Performance Engineer", "Site Reliability Engineer"],
                tools_required=["Performance testing tools", "Profiling tools", "Monitoring"],
                risks=["Performance degradation", "Increased latency"],
                mitigation_strategies=["Comprehensive performance testing", "Caching strategies"]
            )
        ]
        
        phase4 = MigrationPhase(
            phase_number=4,
            name="Iteration and Optimization",
            description="Complete migration and optimize the microservices architecture",
            duration_weeks=12,
            objectives=[
                "Extract remaining services",
                "Optimize performance",
                "Establish operational excellence",
                "Knowledge transfer"
            ],
            tasks=phase4_tasks,
            success_criteria=[
                "All services migrated successfully",
                "Performance optimized",
                "Team fully trained"
            ],
            exit_criteria=[
                "Monolith fully decommissioned",
                "Performance SLAs met",
                "Operational procedures mature"
            ],
            rollback_plan="Not applicable - migration complete"
        )
        
        return MigrationWorkflow(
            workflow_id="monolith_to_microservices",
            name="Monolith to Microservices Migration",
            description="Comprehensive workflow for migrating monolithic applications to microservices architecture",
            migration_type=MigrationType.MONOLITH_TO_MICROSERVICES,
            complexity=MigrationComplexity.HIGH,
            total_duration_weeks=30,
            phases=[phase1, phase2, phase3, phase4],
            prerequisites=[
                "Stakeholder buy-in for migration",
                "Dedicated migration team",
                "Comprehensive test coverage",
                "Clear business domain understanding",
                "Infrastructure budget approved"
            ],
            success_metrics=[
                "Independent service deployments",
                "Improved deployment frequency",
                "Reduced time to market",
                "Improved system resilience",
                "Team autonomy achieved"
            ],
            common_pitfalls=[
                "Creating too many small services (nano-services)",
                "Ignoring data consistency requirements",
                "Insufficient monitoring and observability",
                "Poor service boundary definition",
                "Underestimating operational complexity"
            ],
            best_practices=[
                "Start with the Strangler Fig pattern",
                "Invest heavily in automation and tooling",
                "Implement comprehensive monitoring early",
                "Use Domain-Driven Design for service boundaries",
                "Practice database-per-service pattern",
                "Implement circuit breakers and retry mechanisms",
                "Plan for distributed system challenges"
            ],
            required_skills=[
                "Microservices architecture patterns",
                "Container orchestration (Kubernetes)",
                "API design and management",
                "Distributed systems concepts",
                "DevOps and CI/CD practices",
                "Monitoring and observability",
                "Domain-driven design"
            ],
            tools_and_technologies=[
                "Container orchestration: Kubernetes, Docker Swarm",
                "API Gateway: Kong, NGINX, AWS API Gateway",
                "Service mesh: Istio, Linkerd",
                "Monitoring: Prometheus, Grafana, Jaeger",
                "CI/CD: Jenkins, GitLab CI, GitHub Actions",
                "Message brokers: RabbitMQ, Apache Kafka",
                "Databases: PostgreSQL, MongoDB, Redis"
            ]
        )
    
    def _create_database_migration_workflow(self) -> MigrationWorkflow:
        """Create database migration workflow"""
        # Similar detailed structure for database migration
        # This is a simplified version for brevity
        return MigrationWorkflow(
            workflow_id="database_migration",
            name="Database-per-Service Migration",
            description="Migrate from shared database to service-specific databases",
            migration_type=MigrationType.DATABASE_MIGRATION,
            complexity=MigrationComplexity.HIGH,
            total_duration_weeks=16,
            phases=[],  # Would be populated with detailed phases
            prerequisites=[
                "Clear data ownership boundaries",
                "Data migration strategy approved",
                "Database expertise available"
            ],
            success_metrics=[
                "Data integrity maintained",
                "Service independence achieved",
                "Performance improvements"
            ],
            common_pitfalls=[
                "Data consistency issues",
                "Complex data synchronization",
                "Transaction boundary challenges"
            ],
            best_practices=[
                "Use database-per-service pattern",
                "Implement eventual consistency",
                "Plan for data synchronization"
            ],
            required_skills=[
                "Database administration",
                "Data modeling",
                "ETL processes",
                "Eventual consistency patterns"
            ],
            tools_and_technologies=[
                "Database migration tools",
                "ETL frameworks",
                "Data validation tools",
                "Message queues for synchronization"
            ]
        )
    
    def _create_cloud_migration_workflow(self) -> MigrationWorkflow:
        """Create cloud migration workflow"""
        return MigrationWorkflow(
            workflow_id="cloud_migration",
            name="Cloud Migration",
            description="Migrate applications to cloud infrastructure",
            migration_type=MigrationType.CLOUD_MIGRATION,
            complexity=MigrationComplexity.MEDIUM,
            total_duration_weeks=12,
            phases=[],
            prerequisites=[
                "Cloud platform selected",
                "Security requirements defined",
                "Migration strategy approved"
            ],
            success_metrics=[
                "Application running in cloud",
                "Performance maintained",
                "Cost targets met"
            ],
            common_pitfalls=[
                "Vendor lock-in",
                "Security misconfigurations",
                "Cost overruns"
            ],
            best_practices=[
                "Use infrastructure as code",
                "Implement proper security controls",
                "Monitor costs continuously"
            ],
            required_skills=[
                "Cloud platform expertise",
                "Infrastructure as code",
                "Cloud security",
                "Cost optimization"
            ],
            tools_and_technologies=[
                "Cloud platforms: AWS, Azure, GCP",
                "Infrastructure as code: Terraform, CloudFormation",
                "Containerization: Docker, Kubernetes",
                "Monitoring: CloudWatch, Azure Monitor"
            ]
        )
    
    def _create_legacy_modernization_workflow(self) -> MigrationWorkflow:
        """Create legacy system modernization workflow"""
        return MigrationWorkflow(
            workflow_id="legacy_modernization",
            name="Legacy System Modernization",
            description="Modernize legacy applications with current technologies",
            migration_type=MigrationType.LEGACY_MODERNIZATION,
            complexity=MigrationComplexity.HIGH,
            total_duration_weeks=24,
            phases=[],
            prerequisites=[
                "Legacy system analysis completed",
                "Modern technology stack selected",
                "Business requirements understood"
            ],
            success_metrics=[
                "Modern technology stack implemented",
                "Improved maintainability",
                "Enhanced performance"
            ],
            common_pitfalls=[
                "Big-bang approach",
                "Insufficient legacy system understanding",
                "Poor migration planning"
            ],
            best_practices=[
                "Use incremental migration approach",
                "Maintain system functionality",
                "Comprehensive testing strategy"
            ],
            required_skills=[
                "Legacy system expertise",
                "Modern development practices",
                "Migration patterns",
                "System integration"
            ],
            tools_and_technologies=[
                "Modern frameworks",
                "Migration tools",
                "Testing frameworks",
                "Integration platforms"
            ]
        )
    
    def _create_framework_migration_workflow(self) -> MigrationWorkflow:
        """Create framework migration workflow"""
        return MigrationWorkflow(
            workflow_id="framework_migration",
            name="Framework Migration",
            description="Migrate applications to newer framework versions or different frameworks",
            migration_type=MigrationType.FRAMEWORK_MIGRATION,
            complexity=MigrationComplexity.MEDIUM,
            total_duration_weeks=8,
            phases=[],
            prerequisites=[
                "Target framework selected",
                "Compatibility analysis completed",
                "Migration path defined"
            ],
            success_metrics=[
                "Framework successfully migrated",
                "All features working",
                "Performance maintained"
            ],
            common_pitfalls=[
                "Breaking changes not addressed",
                "Insufficient testing",
                "Performance regression"
            ],
            best_practices=[
                "Incremental migration approach",
                "Comprehensive testing",
                "Performance monitoring"
            ],
            required_skills=[
                "Framework expertise",
                "Migration patterns",
                "Testing strategies",
                "Performance optimization"
            ],
            tools_and_technologies=[
                "Migration tools",
                "Testing frameworks",
                "Performance monitoring",
                "Code analysis tools"
            ]
        )
    
    def _create_architecture_refactoring_workflow(self) -> MigrationWorkflow:
        """Create architecture refactoring workflow"""
        return MigrationWorkflow(
            workflow_id="architecture_refactoring",
            name="Architecture Refactoring",
            description="Refactor application architecture for better maintainability and scalability",
            migration_type=MigrationType.ARCHITECTURE_REFACTORING,
            complexity=MigrationComplexity.MEDIUM,
            total_duration_weeks=10,
            phases=[],
            prerequisites=[
                "Architecture assessment completed",
                "Refactoring goals defined",
                "Team training completed"
            ],
            success_metrics=[
                "Improved code maintainability",
                "Better separation of concerns",
                "Enhanced testability"
            ],
            common_pitfalls=[
                "Over-engineering",
                "Breaking existing functionality",
                "Insufficient testing"
            ],
            best_practices=[
                "Incremental refactoring",
                "Maintain test coverage",
                "Regular code reviews"
            ],
            required_skills=[
                "Software architecture",
                "Refactoring techniques",
                "Design patterns",
                "Testing strategies"
            ],
            tools_and_technologies=[
                "Refactoring tools",
                "Static analysis tools",
                "Testing frameworks",
                "Code quality tools"
            ]
        )


if __name__ == "__main__":
    # Example usage
    generator = MigrationWorkflowGenerator()
    
    # Generate monolith to microservices workflow
    workflow = generator.generate_workflow(
        MigrationType.MONOLITH_TO_MICROSERVICES,
        MigrationComplexity.HIGH
    )
    
    print(f"Workflow: {workflow.name}")
    print(f"Duration: {workflow.total_duration_weeks} weeks")
    print(f"Phases: {len(workflow.phases)}")
    
    for phase in workflow.phases:
        print(f"\nPhase {phase.phase_number}: {phase.name}")
        print(f"Duration: {phase.duration_weeks} weeks")
        print(f"Tasks: {len(phase.tasks)}")
        
        for task in phase.tasks[:2]:  # Show first 2 tasks
            print(f"  - {task.name} ({task.estimated_hours}h)")
    
    print(f"\nPrerequisites:")
    for prereq in workflow.prerequisites:
        print(f"- {prereq}")
    
    print(f"\nBest Practices:")
    for practice in workflow.best_practices:
        print(f"- {practice}")