#!/usr/bin/env python3
"""
Migration Analyzer - Analyzes projects for migration opportunities and generates migration strategies
"""

import os
import json
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

class MigrationType(Enum):
    MONOLITH_TO_MICROSERVICES = "monolith_to_microservices"
    LEGACY_MODERNIZATION = "legacy_modernization"
    DATABASE_MIGRATION = "database_migration"
    CLOUD_MIGRATION = "cloud_migration"
    FRAMEWORK_MIGRATION = "framework_migration"
    ARCHITECTURE_REFACTORING = "architecture_refactoring"

class MigrationComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DomainBoundary:
    """Represents a potential domain boundary for microservices extraction"""
    name: str
    files: List[str]
    dependencies: List[str]
    external_dependencies: List[str]
    cohesion_score: float
    coupling_score: float
    size_estimate: int  # lines of code
    extraction_difficulty: str

@dataclass
class DatabaseDependency:
    """Represents database usage patterns"""
    database_type: str
    table_access_patterns: Dict[str, List[str]]  # table -> accessing modules
    transaction_boundaries: List[str]
    data_consistency_requirements: List[str]

@dataclass
class MigrationOpportunity:
    """Represents a specific migration opportunity"""
    migration_type: MigrationType
    name: str
    description: str
    business_value: str
    technical_benefits: List[str]
    complexity: MigrationComplexity
    estimated_effort_weeks: int
    prerequisites: List[str]
    risks: List[str]
    success_metrics: List[str]

@dataclass
class MigrationAssessment:
    """Complete migration assessment for a project"""
    project_path: str
    current_architecture: str
    migration_readiness_score: float  # 0-100
    opportunities: List[MigrationOpportunity]
    domain_boundaries: List[DomainBoundary]
    database_dependencies: List[DatabaseDependency]
    technical_debt_blockers: List[str]
    organizational_considerations: List[str]
    recommended_approach: str
    migration_roadmap: List[Dict[str, Any]]

class MigrationAnalyzer:
    def __init__(self):
        self.architecture_patterns = self._load_architecture_patterns()
        self.migration_strategies = self._load_migration_strategies()
        
    def _load_architecture_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns that indicate different architectural styles"""
        return {
            "monolithic": {
                "indicators": [
                    "single large database",
                    "shared data models across modules",
                    "synchronous communication only",
                    "single deployment unit",
                    "tight coupling between components"
                ],
                "file_patterns": [
                    "large controllers (>500 LOC)",
                    "god objects",
                    "shared utilities everywhere",
                    "no clear module boundaries"
                ]
            },
            "microservices": {
                "indicators": [
                    "service-specific databases",
                    "API-based communication", 
                    "independent deployments",
                    "domain-driven boundaries",
                    "distributed tracing"
                ],
                "file_patterns": [
                    "service directories",
                    "API gateway",
                    "message queues",
                    "docker-compose with multiple services"
                ]
            },
            "modular_monolith": {
                "indicators": [
                    "clear module boundaries",
                    "internal APIs",
                    "shared database with module ownership",
                    "single deployment with modules"
                ]
            }
        }
    
    def _load_migration_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load migration strategies and their applicability"""
        return {
            "strangler_fig": {
                "name": "Strangler Fig Pattern",
                "description": "Gradually replace parts of the monolith with microservices",
                "best_for": ["large monoliths", "high-risk migrations", "continuous operation"],
                "phases": [
                    "Identify extraction candidate",
                    "Create microservice with same interface",
                    "Route traffic to new service",
                    "Remove old code from monolith"
                ],
                "complexity": "medium",
                "duration_weeks": 12
            },
            "database_per_service": {
                "name": "Database-per-Service Migration",
                "description": "Split shared database into service-specific databases",
                "best_for": ["data-heavy applications", "clear data ownership", "scaling bottlenecks"],
                "phases": [
                    "Analyze data dependencies",
                    "Identify data ownership boundaries", 
                    "Create service-specific schemas",
                    "Implement data synchronization",
                    "Migrate data access patterns"
                ],
                "complexity": "high",
                "duration_weeks": 16
            },
            "api_gateway": {
                "name": "API Gateway Introduction",
                "description": "Add API gateway to manage external communication",
                "best_for": ["client-facing applications", "security requirements", "cross-cutting concerns"],
                "phases": [
                    "Design API contracts",
                    "Implement gateway service",
                    "Add authentication/authorization",
                    "Implement rate limiting and monitoring",
                    "Migrate client applications"
                ],
                "complexity": "medium",
                "duration_weeks": 8
            },
            "event_driven": {
                "name": "Event-Driven Architecture Migration", 
                "description": "Introduce asynchronous messaging between services",
                "best_for": ["loose coupling", "scalability", "eventual consistency acceptable"],
                "phases": [
                    "Identify business events",
                    "Design event schemas",
                    "Implement message broker",
                    "Add event publishers",
                    "Implement event consumers"
                ],
                "complexity": "high",
                "duration_weeks": 20
            }
        }
    
    def analyze_migration_opportunities(self, project_path: str) -> MigrationAssessment:
        """Analyze a project for migration opportunities"""
        project_path = Path(project_path).resolve()
        
        # Analyze current architecture
        current_arch = self._analyze_current_architecture(project_path)
        
        # Identify domain boundaries
        domain_boundaries = self._identify_domain_boundaries(project_path)
        
        # Analyze database dependencies
        db_dependencies = self._analyze_database_dependencies(project_path)
        
        # Assess migration readiness
        readiness_score = self._calculate_migration_readiness(project_path, current_arch)
        
        # Identify specific opportunities
        opportunities = self._identify_migration_opportunities(
            project_path, current_arch, domain_boundaries, db_dependencies
        )
        
        # Generate migration roadmap
        roadmap = self._generate_migration_roadmap(opportunities, domain_boundaries)
        
        # Identify blockers
        blockers = self._identify_technical_debt_blockers(project_path)
        
        # Organizational considerations
        org_considerations = self._assess_organizational_readiness(project_path, opportunities)
        
        # Recommend approach
        recommended_approach = self._recommend_migration_approach(
            current_arch, opportunities, readiness_score
        )
        
        return MigrationAssessment(
            project_path=str(project_path),
            current_architecture=current_arch,
            migration_readiness_score=readiness_score,
            opportunities=opportunities,
            domain_boundaries=domain_boundaries,
            database_dependencies=db_dependencies,
            technical_debt_blockers=blockers,
            organizational_considerations=org_considerations,
            recommended_approach=recommended_approach,
            migration_roadmap=roadmap
        )
    
    def _analyze_current_architecture(self, project_path: Path) -> str:
        """Determine the current architectural style"""
        indicators = {
            "monolithic": 0,
            "microservices": 0,
            "modular_monolith": 0
        }
        
        # Check for microservices indicators
        if (project_path / "docker-compose.yml").exists():
            compose_content = (project_path / "docker-compose.yml").read_text()
            service_count = len(re.findall(r'^\s*\w+:', compose_content, re.MULTILINE))
            if service_count > 3:
                indicators["microservices"] += 0.4
        
        # Check for service directories
        service_dirs = 0
        for item in project_path.iterdir():
            if item.is_dir() and item.name in ['services', 'microservices', 'api', 'gateway']:
                service_dirs += 1
                indicators["microservices"] += 0.2
        
        # Check for API gateway
        api_gateway_files = ['gateway.py', 'api-gateway.js', 'proxy.conf', 'nginx.conf']
        for file_name in api_gateway_files:
            if (project_path / file_name).exists():
                indicators["microservices"] += 0.2
                break
        
        # Check for monolithic indicators
        large_files = 0
        total_files = 0
        for file_path in project_path.rglob("*.py"):
            total_files += 1
            if file_path.stat().st_size > 10000:  # Large files
                large_files += 1
        
        if total_files > 0:
            large_file_ratio = large_files / total_files
            if large_file_ratio > 0.3:
                indicators["monolithic"] += 0.3
        
        # Check for shared database patterns
        if self._has_shared_database_patterns(project_path):
            indicators["monolithic"] += 0.2
        
        # Check for modular patterns
        if self._has_modular_structure(project_path):
            indicators["modular_monolith"] += 0.3
        
        # Determine architecture based on highest score
        max_score = max(indicators.values())
        if max_score < 0.3:
            return "unclear"
        
        return max(indicators.items(), key=lambda x: x[1])[0]
    
    def _has_shared_database_patterns(self, project_path: Path) -> bool:
        """Check if project has shared database patterns"""
        # Look for single database config
        config_files = ['settings.py', 'config.py', 'database.yml', '.env']
        
        for config_file in config_files:
            config_path = project_path / config_file
            if config_path.exists():
                content = config_path.read_text()
                # Single database URL/connection
                db_connections = len(re.findall(r'DATABASE_URL|DB_HOST|connection.*string', content, re.IGNORECASE))
                if db_connections == 1:
                    return True
        
        return False
    
    def _has_modular_structure(self, project_path: Path) -> bool:
        """Check if project has clear modular structure"""
        modules = []
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if directory has init file (Python) or main file
                if (item / '__init__.py').exists() or (item / 'index.js').exists():
                    modules.append(item.name)
        
        return len(modules) >= 3  # At least 3 clear modules
    
    def _identify_domain_boundaries(self, project_path: Path) -> List[DomainBoundary]:
        """Identify potential domain boundaries for microservices extraction"""
        boundaries = []
        
        # Analyze directory structure for domain hints
        domain_dirs = []
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if self._is_domain_directory(item):
                    domain_dirs.append(item)
        
        for domain_dir in domain_dirs:
            files = list(domain_dir.rglob("*.py")) + list(domain_dir.rglob("*.js"))
            
            # Calculate metrics
            cohesion = self._calculate_cohesion(domain_dir)
            coupling = self._calculate_coupling(domain_dir, project_path)
            size = sum(f.stat().st_size for f in files if f.exists())
            
            # Determine extraction difficulty
            difficulty = "low"
            if coupling > 0.7:
                difficulty = "high"
            elif coupling > 0.5:
                difficulty = "medium"
            
            boundary = DomainBoundary(
                name=domain_dir.name,
                files=[str(f.relative_to(project_path)) for f in files],
                dependencies=self._find_dependencies(domain_dir, project_path),
                external_dependencies=self._find_external_dependencies(domain_dir),
                cohesion_score=cohesion,
                coupling_score=coupling,
                size_estimate=size,
                extraction_difficulty=difficulty
            )
            boundaries.append(boundary)
        
        return boundaries
    
    def _is_domain_directory(self, directory: Path) -> bool:
        """Check if directory represents a domain"""
        domain_indicators = [
            'user', 'auth', 'order', 'payment', 'product', 'inventory', 
            'notification', 'report', 'admin', 'api', 'service'
        ]
        
        dir_name = directory.name.lower()
        has_domain_name = any(indicator in dir_name for indicator in domain_indicators)
        has_substantial_code = len(list(directory.rglob("*.py"))) > 3
        
        return has_domain_name and has_substantial_code
    
    def _calculate_cohesion(self, directory: Path) -> float:
        """Calculate internal cohesion of a directory"""
        files = list(directory.rglob("*.py"))
        if len(files) < 2:
            return 1.0
        
        # Simple heuristic: shared imports/classes indicate cohesion
        all_imports = set()
        file_imports = {}
        
        for file_path in files:
            try:
                content = file_path.read_text()
                imports = re.findall(r'from\s+(\w+)', content) + re.findall(r'import\s+(\w+)', content)
                file_imports[file_path] = set(imports)
                all_imports.update(imports)
            except:
                continue
        
        if not all_imports:
            return 0.5
        
        # Calculate shared imports ratio
        shared_imports = 0
        for imp in all_imports:
            files_using = sum(1 for imports in file_imports.values() if imp in imports)
            if files_using > 1:
                shared_imports += 1
        
        return min(1.0, shared_imports / len(all_imports))
    
    def _calculate_coupling(self, directory: Path, project_root: Path) -> float:
        """Calculate external coupling of a directory"""
        files = list(directory.rglob("*.py"))
        if not files:
            return 0.0
        
        internal_modules = {f.stem for f in files}
        external_deps = 0
        total_deps = 0
        
        for file_path in files:
            try:
                content = file_path.read_text()
                imports = re.findall(r'from\s+([^.\s]+)', content) + re.findall(r'import\s+([^.\s]+)', content)
                
                for imp in imports:
                    total_deps += 1
                    if imp not in internal_modules:
                        external_deps += 1
            except:
                continue
        
        if total_deps == 0:
            return 0.0
        
        return external_deps / total_deps
    
    def _find_dependencies(self, directory: Path, project_root: Path) -> List[str]:
        """Find internal dependencies of a directory"""
        dependencies = set()
        files = list(directory.rglob("*.py"))
        
        for file_path in files:
            try:
                content = file_path.read_text()
                # Look for imports from other parts of the project
                relative_imports = re.findall(r'from\s+\.+([^.\s]+)', content)
                absolute_imports = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)', content)
                
                for imp in relative_imports + absolute_imports:
                    if not imp.startswith(('os', 'sys', 'json', 're', 'datetime')):
                        dependencies.add(imp)
            except:
                continue
        
        return list(dependencies)
    
    def _find_external_dependencies(self, directory: Path) -> List[str]:
        """Find external package dependencies"""
        dependencies = set()
        files = list(directory.rglob("*.py"))
        
        common_packages = {
            'requests', 'flask', 'django', 'sqlalchemy', 'pandas', 'numpy',
            'pytest', 'unittest', 'asyncio', 'aiohttp', 'celery', 'redis'
        }
        
        for file_path in files:
            try:
                content = file_path.read_text()
                imports = re.findall(r'import\s+([^.\s]+)', content) + re.findall(r'from\s+([^.\s]+)', content)
                
                for imp in imports:
                    if imp in common_packages:
                        dependencies.add(imp)
            except:
                continue
        
        return list(dependencies)
    
    def _analyze_database_dependencies(self, project_path: Path) -> List[DatabaseDependency]:
        """Analyze database usage patterns"""
        dependencies = []
        
        # Look for database configuration
        db_configs = self._find_database_configs(project_path)
        
        for db_type, config in db_configs.items():
            # Analyze table access patterns
            table_access = self._analyze_table_access_patterns(project_path)
            
            # Find transaction boundaries  
            transactions = self._find_transaction_boundaries(project_path)
            
            # Identify consistency requirements
            consistency_reqs = self._identify_consistency_requirements(project_path)
            
            dependency = DatabaseDependency(
                database_type=db_type,
                table_access_patterns=table_access,
                transaction_boundaries=transactions,
                data_consistency_requirements=consistency_reqs
            )
            dependencies.append(dependency)
        
        return dependencies
    
    def _find_database_configs(self, project_path: Path) -> Dict[str, str]:
        """Find database configurations in the project"""
        configs = {}
        
        # Check common config files
        config_files = ['settings.py', 'config.py', 'database.yml', '.env', 'docker-compose.yml']
        
        for config_file in config_files:
            config_path = project_path / config_file
            if config_path.exists():
                content = config_path.read_text().lower()
                
                if 'postgresql' in content or 'postgres' in content:
                    configs['postgresql'] = 'detected'
                elif 'mysql' in content:
                    configs['mysql'] = 'detected'
                elif 'mongodb' in content or 'mongo' in content:
                    configs['mongodb'] = 'detected'
                elif 'sqlite' in content:
                    configs['sqlite'] = 'detected'
        
        return configs
    
    def _analyze_table_access_patterns(self, project_path: Path) -> Dict[str, List[str]]:
        """Analyze which modules access which tables/collections"""
        table_access = defaultdict(list)
        
        # Look for ORM models or SQL queries
        python_files = list(project_path.rglob("*.py"))
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                # Look for Django/SQLAlchemy model definitions
                models = re.findall(r'class\s+(\w+).*Model', content)
                for model in models:
                    table_access[model.lower()].append(str(file_path.relative_to(project_path)))
                
                # Look for table names in queries
                queries = re.findall(r'SELECT.*FROM\s+(\w+)', content, re.IGNORECASE)
                queries += re.findall(r'INSERT\s+INTO\s+(\w+)', content, re.IGNORECASE)
                queries += re.findall(r'UPDATE\s+(\w+)', content, re.IGNORECASE)
                queries += re.findall(r'DELETE\s+FROM\s+(\w+)', content, re.IGNORECASE)
                
                for table in queries:
                    table_access[table.lower()].append(str(file_path.relative_to(project_path)))
                    
            except:
                continue
        
        return dict(table_access)
    
    def _find_transaction_boundaries(self, project_path: Path) -> List[str]:
        """Find transaction boundaries in the code"""
        transactions = []
        python_files = list(project_path.rglob("*.py"))
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                
                # Look for transaction decorators/context managers
                if '@transaction' in content or 'with transaction' in content:
                    transactions.append(str(file_path.relative_to(project_path)))
                elif 'BEGIN' in content and 'COMMIT' in content:
                    transactions.append(str(file_path.relative_to(project_path)))
                    
            except:
                continue
        
        return transactions
    
    def _identify_consistency_requirements(self, project_path: Path) -> List[str]:
        """Identify data consistency requirements"""
        requirements = []
        
        # Look for ACID requirements, foreign keys, etc.
        python_files = list(project_path.rglob("*.py"))
        
        consistency_indicators = [
            'foreign.*key', 'references', 'cascade', 'atomic', 'consistency',
            'integrity', 'constraint', 'unique.*together'
        ]
        
        for file_path in python_files:
            try:
                content = file_path.read_text().lower()
                
                for indicator in consistency_indicators:
                    if re.search(indicator, content):
                        requirements.append(f"{indicator} in {file_path.relative_to(project_path)}")
                        break
                        
            except:
                continue
        
        return requirements
    
    def _calculate_migration_readiness(self, project_path: Path, current_arch: str) -> float:
        """Calculate a migration readiness score (0-100)"""
        score = 50.0  # Base score
        
        # Architecture factor
        if current_arch == "monolithic":
            score += 20  # Good candidate for migration
        elif current_arch == "modular_monolith":
            score += 30  # Best candidate
        elif current_arch == "microservices":
            score -= 30  # Already migrated
        
        # Test coverage factor
        test_files = list(project_path.rglob("test_*.py")) + list(project_path.rglob("*_test.py"))
        source_files = list(project_path.rglob("*.py"))
        
        if source_files:
            test_coverage_ratio = len(test_files) / len(source_files)
            score += min(20, test_coverage_ratio * 40)  # Up to 20 points for good test coverage
        
        # Documentation factor
        doc_files = list(project_path.rglob("*.md")) + list(project_path.rglob("*.rst"))
        if doc_files:
            score += 10
        
        # CI/CD factor
        ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci']
        has_ci = any((project_path / ci_file).exists() for ci_file in ci_files)
        if has_ci:
            score += 10
        
        # Containerization factor
        has_docker = (project_path / 'Dockerfile').exists() or (project_path / 'docker-compose.yml').exists()
        if has_docker:
            score += 10
        
        # Code quality factor (inverse of complexity)
        avg_file_size = self._calculate_average_file_size(project_path)
        if avg_file_size < 200:  # Smaller files are better
            score += 10
        elif avg_file_size > 1000:  # Very large files are problematic
            score -= 10
        
        return min(100.0, max(0.0, score))
    
    def _calculate_average_file_size(self, project_path: Path) -> float:
        """Calculate average file size in lines"""
        python_files = list(project_path.rglob("*.py"))
        if not python_files:
            return 0
        
        total_lines = 0
        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                continue
        
        return total_lines / len(python_files)
    
    def _identify_migration_opportunities(self, project_path: Path, current_arch: str, 
                                        domain_boundaries: List[DomainBoundary],
                                        db_dependencies: List[DatabaseDependency]) -> List[MigrationOpportunity]:
        """Identify specific migration opportunities"""
        opportunities = []
        
        # Only suggest microservices migration for monoliths
        if current_arch == "monolithic":
            # Strangler Fig opportunity
            if domain_boundaries:
                best_boundary = min(domain_boundaries, key=lambda x: x.coupling_score)
                opportunities.append(MigrationOpportunity(
                    migration_type=MigrationType.MONOLITH_TO_MICROSERVICES,
                    name=f"Extract {best_boundary.name} Service",
                    description=f"Extract the {best_boundary.name} domain as a microservice using Strangler Fig pattern",
                    business_value="Independent scaling and deployment of core domain functionality",
                    technical_benefits=[
                        "Reduced coupling",
                        "Independent scaling",
                        "Technology diversity",
                        "Team autonomy"
                    ],
                    complexity=MigrationComplexity.MEDIUM if best_boundary.coupling_score < 0.5 else MigrationComplexity.HIGH,
                    estimated_effort_weeks=12 if best_boundary.coupling_score < 0.5 else 20,
                    prerequisites=[
                        "Comprehensive test coverage",
                        "Clear API boundaries",
                        "Monitoring infrastructure"
                    ],
                    risks=[
                        "Data consistency challenges",
                        "Increased operational complexity",
                        "Performance overhead"
                    ],
                    success_metrics=[
                        "Service independence verification",
                        "Performance benchmarks maintained",
                        "Zero-downtime migration"
                    ]
                ))
        
        # Database migration opportunities
        if len(db_dependencies) == 1 and len(domain_boundaries) > 1:
            opportunities.append(MigrationOpportunity(
                migration_type=MigrationType.DATABASE_MIGRATION,
                name="Database Per Service Migration",
                description="Split shared database into service-specific databases",
                business_value="Improved data ownership, scalability, and service independence",
                technical_benefits=[
                    "Service data ownership",
                    "Independent scaling",
                    "Technology optimization",
                    "Reduced contention"
                ],
                complexity=MigrationComplexity.HIGH,
                estimated_effort_weeks=16,
                prerequisites=[
                    "Clear data ownership boundaries",
                    "Data migration strategy",
                    "Backup and recovery plan"
                ],
                risks=[
                    "Data consistency issues",
                    "Complex data synchronization", 
                    "Transaction boundary challenges"
                ],
                success_metrics=[
                    "Data integrity maintained",
                    "Service independence achieved",
                    "Performance improvements"
                ]
            ))
        
        # API Gateway opportunity
        if current_arch in ["monolithic", "modular_monolith"]:
            opportunities.append(MigrationOpportunity(
                migration_type=MigrationType.ARCHITECTURE_REFACTORING,
                name="API Gateway Implementation",
                description="Introduce API Gateway for centralized request handling",
                business_value="Improved security, monitoring, and client experience",
                technical_benefits=[
                    "Centralized authentication",
                    "Rate limiting",
                    "Request/response transformation",
                    "Centralized monitoring"
                ],
                complexity=MigrationComplexity.MEDIUM,
                estimated_effort_weeks=8,
                prerequisites=[
                    "API documentation",
                    "Authentication strategy",
                    "Monitoring requirements"
                ],
                risks=[
                    "Single point of failure",
                    "Performance bottleneck",
                    "Increased complexity"
                ],
                success_metrics=[
                    "Centralized request handling",
                    "Security improvements",
                    "Client satisfaction"
                ]
            ))
        
        # Cloud migration opportunity
        has_docker = (project_path / 'Dockerfile').exists()
        if not has_docker:
            opportunities.append(MigrationOpportunity(
                migration_type=MigrationType.CLOUD_MIGRATION,
                name="Containerization and Cloud Migration",
                description="Containerize application and migrate to cloud infrastructure",
                business_value="Improved scalability, reliability, and operational efficiency",
                technical_benefits=[
                    "Consistent deployment environments",
                    "Auto-scaling capabilities",
                    "Improved disaster recovery",
                    "Cost optimization"
                ],
                complexity=MigrationComplexity.MEDIUM,
                estimated_effort_weeks=10,
                prerequisites=[
                    "Application configuration externalization",
                    "Cloud platform selection",
                    "Security review"
                ],
                risks=[
                    "Vendor lock-in",
                    "Cost overruns",
                    "Security concerns"
                ],
                success_metrics=[
                    "Successful container deployment",
                    "Performance benchmarks met",
                    "Cost targets achieved"
                ]
            ))
        
        return opportunities
    
    def _identify_technical_debt_blockers(self, project_path: Path) -> List[str]:
        """Identify technical debt that would block migration"""
        blockers = []
        
        # Check for very large files
        large_files = []
        for file_path in project_path.rglob("*.py"):
            try:
                if file_path.stat().st_size > 50000:  # Very large files
                    large_files.append(str(file_path.relative_to(project_path)))
            except:
                continue
        
        if large_files:
            blockers.append(f"Large files need refactoring: {', '.join(large_files[:3])}")
        
        # Check for missing tests
        test_files = list(project_path.rglob("test_*.py"))
        if len(test_files) < 3:
            blockers.append("Insufficient test coverage - add comprehensive tests before migration")
        
        # Check for hard-coded configurations
        config_files = list(project_path.rglob("*.py"))
        hardcoded_configs = 0
        for file_path in config_files[:10]:  # Sample first 10 files
            try:
                content = file_path.read_text()
                if re.search(r'localhost|127\.0\.0\.1|password.*=.*["\']', content):
                    hardcoded_configs += 1
            except:
                continue
        
        if hardcoded_configs > 2:
            blockers.append("Hard-coded configurations found - externalize configuration")
        
        # Check for missing documentation
        readme_exists = (project_path / 'README.md').exists() or (project_path / 'README.rst').exists()
        if not readme_exists:
            blockers.append("Missing project documentation - add README and architecture docs")
        
        return blockers
    
    def _assess_organizational_readiness(self, project_path: Path, 
                                       opportunities: List[MigrationOpportunity]) -> List[str]:
        """Assess organizational considerations for migration"""
        considerations = []
        
        # Team size implications
        if any(opp.migration_type == MigrationType.MONOLITH_TO_MICROSERVICES for opp in opportunities):
            considerations.append("Team structure: Consider Conway's Law - service boundaries should align with team boundaries")
            considerations.append("DevOps capabilities: Ensure team can handle increased operational complexity")
            considerations.append("Monitoring and observability: Distributed systems require sophisticated monitoring")
        
        # Skill requirements
        considerations.append("Training needs: Team may need training on microservices patterns and tools")
        considerations.append("Operational overhead: Consider increased complexity of managing multiple services")
        
        # Change management
        considerations.append("Stakeholder alignment: Ensure business stakeholders understand migration timeline and impacts")
        considerations.append("Risk tolerance: Migration introduces short-term risk for long-term benefits")
        
        return considerations
    
    def _recommend_migration_approach(self, current_arch: str, opportunities: List[MigrationOpportunity],
                                    readiness_score: float) -> str:
        """Recommend the best migration approach"""
        if readiness_score < 60:
            return "Focus on improving migration readiness before attempting major architectural changes"
        
        if current_arch == "microservices":
            return "Architecture already migrated - focus on optimization and operational excellence"
        
        if current_arch == "monolithic":
            if readiness_score > 80:
                return "Strangler Fig Pattern - gradually extract services starting with least coupled domains"
            else:
                return "Modular Monolith approach - improve internal boundaries before service extraction"
        
        if current_arch == "modular_monolith":
            return "Database-per-Service migration combined with API Gateway implementation"
        
        return "Further analysis needed - unclear architecture detected"
    
    def _generate_migration_roadmap(self, opportunities: List[MigrationOpportunity],
                                  domain_boundaries: List[DomainBoundary]) -> List[Dict[str, Any]]:
        """Generate a phased migration roadmap"""
        roadmap = []
        
        # Phase 1: Foundation (weeks 1-4)
        roadmap.append({
            "phase": 1,
            "name": "Foundation",
            "duration_weeks": 4,
            "objectives": [
                "Improve test coverage",
                "Externalize configuration",
                "Add monitoring and logging",
                "Documentation review"
            ],
            "deliverables": [
                "Comprehensive test suite",
                "Configuration management system",
                "Monitoring dashboard",
                "Updated architecture documentation"
            ]
        })
        
        # Phase 2: Preparation (weeks 5-8)
        roadmap.append({
            "phase": 2,
            "name": "Preparation", 
            "duration_weeks": 4,
            "objectives": [
                "Identify service boundaries",
                "Design APIs",
                "Set up CI/CD pipeline",
                "Choose technology stack"
            ],
            "deliverables": [
                "Service boundary documentation",
                "API specifications",
                "Deployment pipeline",
                "Technology decisions document"
            ]
        })
        
        # Phase 3: Initial Migration (weeks 9-16)
        if opportunities:
            first_opportunity = opportunities[0]
            roadmap.append({
                "phase": 3,
                "name": "Initial Migration",
                "duration_weeks": first_opportunity.estimated_effort_weeks,
                "objectives": [
                    f"Implement {first_opportunity.name}",
                    "Set up service infrastructure",
                    "Establish operational procedures",
                    "Monitor and optimize"
                ],
                "deliverables": [
                    "First extracted service",
                    "Service infrastructure",
                    "Operational runbooks",
                    "Performance baselines"
                ]
            })
        
        # Phase 4: Iteration (weeks 17+)
        roadmap.append({
            "phase": 4,
            "name": "Iteration",
            "duration_weeks": 12,
            "objectives": [
                "Extract additional services",
                "Optimize performance",
                "Improve operational maturity",
                "Team training and knowledge transfer"
            ],
            "deliverables": [
                "Additional microservices",
                "Performance optimizations",
                "Operational excellence",
                "Team upskilling"
            ]
        })
        
        return roadmap


if __name__ == "__main__":
    # Example usage
    analyzer = MigrationAnalyzer()
    
    # Analyze current project
    assessment = analyzer.analyze_migration_opportunities(".")
    
    print(f"Migration Assessment for: {assessment.project_path}")
    print(f"Current Architecture: {assessment.current_architecture}")
    print(f"Migration Readiness Score: {assessment.migration_readiness_score:.1f}/100")
    print(f"\nOpportunities Found: {len(assessment.opportunities)}")
    
    for opp in assessment.opportunities:
        print(f"\n- {opp.name}")
        print(f"  Type: {opp.migration_type.value}")
        print(f"  Complexity: {opp.complexity.value}")
        print(f"  Effort: {opp.estimated_effort_weeks} weeks")
        print(f"  Business Value: {opp.business_value}")
    
    print(f"\nRecommended Approach: {assessment.recommended_approach}")
    
    if assessment.technical_debt_blockers:
        print(f"\nTechnical Debt Blockers:")
        for blocker in assessment.technical_debt_blockers:
            print(f"- {blocker}")