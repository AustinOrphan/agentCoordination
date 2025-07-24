#!/usr/bin/env python3
"""
Project Analyzer - Analyzes codebases to detect technologies, patterns, and generate workflow templates
"""

import os
import json
import re
import subprocess
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class ProjectType(Enum):
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    ML_PROJECT = "ml_project"
    DATA_PIPELINE = "data_pipeline"
    MICROSERVICE = "microservice"
    MONOREPO = "monorepo"
    GAME_DEV = "game_dev"
    BLOCKCHAIN = "blockchain"

@dataclass
class TechnologyStack:
    languages: List[str]
    frameworks: List[str]
    databases: List[str]
    cloud_services: List[str]
    build_tools: List[str]
    testing_frameworks: List[str]
    deployment_tools: List[str]
    package_managers: List[str]
    confidence_scores: Dict[str, float] = None  # Technology -> confidence score

@dataclass
class ProjectStructure:
    has_tests: bool
    has_docs: bool
    has_ci_cd: bool
    has_docker: bool
    has_api: bool
    has_frontend: bool
    has_backend: bool
    has_database: bool
    entry_points: List[str]
    config_files: List[str]

@dataclass
class AnalysisResult:
    project_type: ProjectType
    confidence: float
    tech_stack: TechnologyStack
    structure: ProjectStructure
    detected_patterns: List[str]
    suggested_workflow: str
    estimated_complexity: str  # low, medium, high
    team_size_recommendation: int

class ProjectAnalyzer:
    def __init__(self):
        self.file_patterns = self._load_file_patterns()
        self.technology_indicators = self._load_tech_indicators()
        self.workflow_templates = self._load_workflow_templates()

    def _load_file_patterns(self) -> Dict[str, List[str]]:
        """Load file patterns that indicate specific technologies or project types"""
        return {
            # Language indicators
            "python": ["*.py", "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "javascript": ["*.js", "*.jsx", "package.json", "yarn.lock", "npm-shrinkwrap.json"],
            "typescript": ["*.ts", "*.tsx", "tsconfig.json"],
            "java": ["*.java", "pom.xml", "build.gradle", "gradle.properties"],
            "csharp": ["*.cs", "*.csproj", "*.sln", "packages.config"],
            "go": ["*.go", "go.mod", "go.sum"],
            "rust": ["*.rs", "Cargo.toml", "Cargo.lock"],
            "php": ["*.php", "composer.json", "composer.lock"],
            "ruby": ["*.rb", "Gemfile", "Gemfile.lock"],
            "swift": ["*.swift", "Package.swift", "*.xcodeproj"],
            "solidity": ["*.sol", "contracts/", "migrations/"],
            
            # Framework indicators (more specific patterns)
            "react": ["src/App.js", "src/App.tsx", "src/index.js", "src/index.tsx"],
            "vue": ["src/App.vue", "vue.config.js", "src/main.js"],
            "angular": ["angular.json", "src/app/app.module.ts"],
            "django": ["manage.py", "settings.py", "urls.py", "wsgi.py"],
            "flask": ["app.py", "application.py"],
            "fastapi": ["app.py", "api.py"],
            "spring": ["pom.xml", "application.properties", "application.yml"],
            "express": ["server.js", "app.js"],
            "nextjs": ["next.config.js", "pages/"],
            "gatsby": ["gatsby-config.js", "gatsby-node.js"],
            
            # Game Development frameworks
            "unity": ["Assets/", "ProjectSettings/", "*.unity", "*.prefab"],
            "unreal": ["*.uproject", "Source/", "Content/", "Config/"],
            "godot": ["project.godot", "*.tscn", "*.tres", "*.gd"],
            "pygame": ["pygame", "game.py", "sprites/"],
            "phaser": ["phaser.js", "game.js", "assets/"],
            
            # Blockchain frameworks
            "truffle": ["truffle-config.js", "truffle.js", "migrations/"],
            "hardhat": ["hardhat.config.js", "hardhat.config.ts"],
            "web3": ["web3.js", "web3.py"],
            "ethers": ["ethers.js"],
            "anchor": ["Anchor.toml", "programs/"],
            "substrate": ["runtime/", "pallets/", "node/"],
            
            # Database indicators
            "postgresql": ["*.sql", "migrations/", "alembic/", "db/"],
            "mysql": ["*.sql", "migrations/", "database/"],
            "mongodb": ["*.js", "models/", "schemas/"],
            "redis": ["redis.conf", "dump.rdb"],
            
            # Cloud/Deployment indicators
            "docker": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
            "kubernetes": ["*.yaml", "*.yml", "kustomization.yaml"],
            "aws": ["serverless.yml", "template.yml", "cloudformation/"],
            "terraform": ["*.tf", "terraform.tfvars"],
            
            # CI/CD indicators
            "github_actions": [".github/workflows/"],
            "gitlab_ci": [".gitlab-ci.yml"],
            "jenkins": ["Jenkinsfile"],
            "circleci": [".circleci/config.yml"],
            
            # Testing indicators
            "pytest": ["test_*.py", "*_test.py", "tests/", "pytest.ini"],
            "jest": ["*.test.js", "*.test.ts", "jest.config.js"],
            "unittest": ["test_*.py", "tests/"],
            "mocha": ["test/", "*.test.js", "mocha.opts"],
        }

    def _load_tech_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Load technology indicators with metadata"""
        return {
            "web_app": {
                "required": ["javascript", "html", "css"],
                "optional": ["react", "vue", "angular"],
                "files": ["index.html", "src/", "public/"],
                "complexity_weight": 1.2
            },
            "api_service": {
                "required": ["python", "java", "javascript", "go"],
                "optional": ["flask", "django", "fastapi", "express", "spring"],
                "files": ["api/", "routes/", "controllers/", "endpoints/"],
                "complexity_weight": 1.0
            },
            "mobile_app": {
                "required": ["swift", "kotlin", "java", "javascript"],
                "optional": ["react_native", "flutter", "xamarin"],
                "files": ["*.xcodeproj", "*.xcworkspace", "android/", "ios/"],
                "complexity_weight": 1.5
            },
            "ml_project": {
                "required": ["python"],
                "optional": ["jupyter", "tensorflow", "pytorch", "sklearn"],
                "files": ["*.ipynb", "models/", "data/", "notebooks/"],
                "complexity_weight": 1.3
            },
            "data_pipeline": {
                "required": ["python", "sql"],
                "optional": ["airflow", "spark", "kafka"],
                "files": ["etl/", "pipelines/", "dags/", "jobs/"],
                "complexity_weight": 1.4
            },
            "game_dev": {
                "required": ["csharp", "cpp", "javascript", "python"],
                "optional": ["unity", "unreal", "godot", "pygame", "phaser"],
                "files": ["Assets/", "Scripts/", "Scenes/", "Resources/", "*.unity", "*.uproject"],
                "complexity_weight": 1.6
            },
            "blockchain": {
                "required": ["solidity", "javascript", "rust"],
                "optional": ["truffle", "hardhat", "web3", "ethers", "anchor", "substrate"],
                "files": ["contracts/", "migrations/", "test/", "*.sol", "scripts/"],
                "complexity_weight": 1.5
            }
        }

    def _load_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load workflow templates for different project types"""
        return {
            "web_app": {
                "name": "Web Application Development",
                "phases": [
                    {
                        "name": "Setup & Configuration",
                        "tasks": [
                            "Set up development environment",
                            "Configure build tools and bundlers",
                            "Set up package management",
                            "Configure linting and formatting",
                            "Set up testing framework"
                        ]
                    },
                    {
                        "name": "Frontend Development",
                        "tasks": [
                            "Create component architecture",
                            "Implement routing system",
                            "Build user interface components", 
                            "Add responsive design",
                            "Implement state management",
                            "Add accessibility features"
                        ]
                    },
                    {
                        "name": "Backend Integration",
                        "tasks": [
                            "Set up API client",
                            "Implement authentication",
                            "Add data fetching logic",
                            "Handle error states",
                            "Add loading states"
                        ]
                    },
                    {
                        "name": "Testing & Quality",
                        "tasks": [
                            "Write unit tests",
                            "Add integration tests",
                            "Perform end-to-end testing",
                            "Add performance testing",
                            "Code review and refactoring"
                        ]
                    },
                    {
                        "name": "Deployment",
                        "tasks": [
                            "Set up CI/CD pipeline",
                            "Configure production environment",
                            "Add monitoring and analytics",
                            "Performance optimization",
                            "Deploy to production"
                        ]
                    }
                ],
                "estimated_weeks": 8,
                "team_size": 3
            },
            "api_service": {
                "name": "API Service Development",
                "phases": [
                    {
                        "name": "Architecture & Design",
                        "tasks": [
                            "Design API architecture",
                            "Define data models",
                            "Plan database schema",
                            "Design authentication system",
                            "Create API documentation"
                        ]
                    },
                    {
                        "name": "Core Implementation",
                        "tasks": [
                            "Set up project structure",
                            "Implement database models",
                            "Create API endpoints",
                            "Add authentication middleware",
                            "Implement business logic"
                        ]
                    },
                    {
                        "name": "Data & Persistence",
                        "tasks": [
                            "Set up database connections",
                            "Create migration scripts",
                            "Implement data validation",
                            "Add caching layer",
                            "Optimize database queries"
                        ]
                    },
                    {
                        "name": "Testing & Documentation",
                        "tasks": [
                            "Write unit tests",
                            "Add integration tests",
                            "Create API documentation",
                            "Add performance tests",
                            "Security testing"
                        ]
                    },
                    {
                        "name": "Deployment & Monitoring",
                        "tasks": [
                            "Containerize application",
                            "Set up CI/CD pipeline", 
                            "Configure monitoring",
                            "Add logging and metrics",
                            "Deploy to production"
                        ]
                    }
                ],
                "estimated_weeks": 6,
                "team_size": 2
            },
            "ml_project": {
                "name": "Machine Learning Project",
                "phases": [
                    {
                        "name": "Data Exploration",
                        "tasks": [
                            "Collect and analyze datasets",
                            "Perform exploratory data analysis",
                            "Identify data quality issues",
                            "Define success metrics",
                            "Create data visualizations"
                        ]
                    },
                    {
                        "name": "Data Preparation",
                        "tasks": [
                            "Clean and preprocess data",
                            "Handle missing values",
                            "Feature engineering",
                            "Data augmentation",
                            "Split datasets"
                        ]
                    },
                    {
                        "name": "Model Development",
                        "tasks": [
                            "Select appropriate algorithms",
                            "Train baseline models",
                            "Hyperparameter tuning",
                            "Cross-validation",
                            "Model ensemble techniques"
                        ]
                    },
                    {
                        "name": "Evaluation & Validation",
                        "tasks": [
                            "Evaluate model performance",
                            "Statistical significance testing",
                            "Bias and fairness analysis",
                            "Model interpretability",
                            "Error analysis"
                        ]
                    },
                    {
                        "name": "Deployment & Monitoring",
                        "tasks": [
                            "Create model serving infrastructure",
                            "Implement A/B testing",
                            "Set up model monitoring",
                            "Create prediction API",
                            "Deploy to production"
                        ]
                    }
                ],
                "estimated_weeks": 12,
                "team_size": 2
            },
            "game_dev": {
                "name": "Game Development Project",
                "phases": [
                    {
                        "name": "Concept & Design",
                        "tasks": [
                            "Define game concept and mechanics",
                            "Create game design document",
                            "Design level architecture",
                            "Create art style guide",
                            "Plan audio requirements",
                            "Define target platforms"
                        ]
                    },
                    {
                        "name": "Prototype Development",
                        "tasks": [
                            "Set up game engine project",
                            "Implement core mechanics",
                            "Create basic player controls",
                            "Build prototype levels",
                            "Test gameplay loops",
                            "Iterate on mechanics"
                        ]
                    },
                    {
                        "name": "Asset Creation",
                        "tasks": [
                            "Create character models/sprites",
                            "Design environment assets",
                            "Implement animations",
                            "Create sound effects",
                            "Compose background music",
                            "Design UI elements"
                        ]
                    },
                    {
                        "name": "Core Development",
                        "tasks": [
                            "Implement game systems",
                            "Create enemy AI",
                            "Build level progression",
                            "Add save/load system",
                            "Implement multiplayer (if applicable)",
                            "Optimize performance"
                        ]
                    },
                    {
                        "name": "Polish & Release",
                        "tasks": [
                            "Playtesting and balancing",
                            "Bug fixing and optimization",
                            "Add achievements/rewards",
                            "Platform-specific builds",
                            "Store listing preparation",
                            "Launch and marketing"
                        ]
                    }
                ],
                "estimated_weeks": 16,
                "team_size": 4
            },
            "blockchain": {
                "name": "Blockchain/Smart Contract Development",
                "phases": [
                    {
                        "name": "Architecture & Design",
                        "tasks": [
                            "Define token economics",
                            "Design smart contract architecture",
                            "Plan security model",
                            "Create technical whitepaper",
                            "Define integration points",
                            "Choose blockchain platform"
                        ]
                    },
                    {
                        "name": "Smart Contract Development",
                        "tasks": [
                            "Set up development environment",
                            "Write core smart contracts",
                            "Implement token standards (ERC20/721/1155)",
                            "Add access controls",
                            "Implement business logic",
                            "Write upgrade mechanisms"
                        ]
                    },
                    {
                        "name": "Testing & Security",
                        "tasks": [
                            "Write comprehensive unit tests",
                            "Perform integration testing",
                            "Conduct security audit",
                            "Test gas optimization",
                            "Simulate attack scenarios",
                            "Fix vulnerabilities"
                        ]
                    },
                    {
                        "name": "Frontend Development",
                        "tasks": [
                            "Build web3 integration",
                            "Create wallet connection",
                            "Implement transaction UI",
                            "Add contract interaction",
                            "Handle blockchain events",
                            "Create admin dashboard"
                        ]
                    },
                    {
                        "name": "Deployment & Launch",
                        "tasks": [
                            "Deploy to testnet",
                            "Conduct beta testing",
                            "Deploy to mainnet",
                            "Verify contracts",
                            "Set up monitoring",
                            "Launch and community building"
                        ]
                    }
                ],
                "estimated_weeks": 10,
                "team_size": 3
            }
        }

    def analyze_project(self, project_path: str) -> AnalysisResult:
        """Analyze a project and return comprehensive analysis results"""
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        # Scan project structure
        file_list = self._scan_project_files(project_path)
        
        # Detect technologies
        tech_stack = self._detect_technologies(file_list, project_path)
        
        # Analyze project structure
        structure = self._analyze_structure(file_list, project_path)
        
        # Determine project type
        project_type, confidence = self._classify_project_type(tech_stack, structure, file_list)
        
        # Detect patterns
        patterns = self._detect_patterns(file_list, project_path)
        
        # Suggest workflow
        workflow = self._suggest_workflow(project_type, tech_stack, structure)
        
        # Estimate complexity
        complexity = self._estimate_complexity(tech_stack, structure, len(file_list))
        
        # Recommend team size
        team_size = self._recommend_team_size(complexity, project_type, tech_stack)

        return AnalysisResult(
            project_type=project_type,
            confidence=confidence,
            tech_stack=tech_stack,
            structure=structure,
            detected_patterns=patterns,
            suggested_workflow=workflow,
            estimated_complexity=complexity,
            team_size_recommendation=team_size
        )

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

    def _detect_technologies(self, file_list: List[str], project_path: Path) -> TechnologyStack:
        """Detect technologies based on file patterns and content with confidence scoring"""
        languages = set()
        frameworks = set()
        databases = set()
        cloud_services = set()
        build_tools = set()
        testing_frameworks = set()
        deployment_tools = set()
        package_managers = set()
        
        # Track confidence scores for each detected technology
        confidence_scores = {}

        # Check file patterns with confidence scoring
        for tech, patterns in self.file_patterns.items():
            if self._matches_patterns(file_list, patterns):
                confidence = self._calculate_pattern_confidence(tech, file_list, patterns)
                confidence_scores[tech] = confidence
                
                # Different confidence thresholds for different categories
                if tech in ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'php', 'ruby', 'swift', 'csharp', 'solidity']:
                    # Lower threshold for languages (more important to detect)
                    if confidence >= 0.5:
                        self._categorize_technology(
                            tech, languages, frameworks, databases, cloud_services,
                            build_tools, testing_frameworks, deployment_tools, package_managers
                        )
                elif tech in ['unity', 'unreal', 'godot', 'pygame', 'phaser', 'truffle', 'hardhat', 'web3', 'ethers', 'anchor', 'substrate']:
                    # Medium threshold for game/blockchain frameworks (important domain indicators)
                    if confidence >= 0.5:
                        self._categorize_technology(
                            tech, languages, frameworks, databases, cloud_services,
                            build_tools, testing_frameworks, deployment_tools, package_managers
                        )
                else:
                    # Higher threshold for general frameworks/tools to reduce false positives
                    if confidence >= 0.8:
                        self._categorize_technology(
                            tech, languages, frameworks, databases, cloud_services,
                            build_tools, testing_frameworks, deployment_tools, package_managers
                        )

        # Check file contents for additional indicators with higher confidence
        content_technologies = self._analyze_file_contents_with_confidence(
            project_path, file_list, languages, frameworks, databases,
            cloud_services, build_tools, testing_frameworks, deployment_tools, confidence_scores
        )

        return TechnologyStack(
            languages=sorted(list(languages)),
            frameworks=sorted(list(frameworks)),
            databases=sorted(list(databases)),
            cloud_services=sorted(list(cloud_services)),
            build_tools=sorted(list(build_tools)),
            testing_frameworks=sorted(list(testing_frameworks)),
            deployment_tools=sorted(list(deployment_tools)),
            package_managers=sorted(list(package_managers)),
            confidence_scores=confidence_scores
        )

    def _matches_patterns(self, file_list: List[str], patterns: List[str]) -> bool:
        """Check if any files match the given patterns with improved accuracy"""
        import fnmatch
        
        for pattern in patterns:
            for file_path in file_list:
                # Use exact matching for specific files, pattern matching for wildcards
                if '*' in pattern:
                    if fnmatch.fnmatch(file_path, pattern):
                        return True
                else:
                    # Handle directory patterns (ending with /) and exact file matches
                    if pattern.endswith('/'):
                        # Directory pattern - check if any file is in this directory
                        if file_path.startswith(pattern):
                            return True
                    else:
                        # Exact file match
                        if pattern == file_path or file_path.endswith('/' + pattern):
                            return True
        return False

    def _calculate_pattern_confidence(self, tech: str, file_list: List[str], patterns: List[str]) -> float:
        """Calculate confidence score for pattern-based technology detection"""
        matched_patterns = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            for file_path in file_list:
                if '*' in pattern:
                    import fnmatch
                    if fnmatch.fnmatch(file_path, pattern):
                        matched_patterns += 1
                        break
                else:
                    # Handle directory patterns (ending with /) and exact file matches
                    if pattern.endswith('/'):
                        # Directory pattern - check if any file is in this directory
                        if file_path.startswith(pattern):
                            matched_patterns += 1
                            break
                    else:
                        # Exact file match
                        if pattern == file_path or file_path.endswith('/' + pattern):
                            matched_patterns += 1
                            break
        
        base_confidence = matched_patterns / total_patterns
        
        # Special handling for languages - count actual source files
        language_extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'go': '.go',
            'rust': '.rs',
            'php': '.php',
            'ruby': '.rb',
            'csharp': '.cs',
            'solidity': '.sol'
        }
        
        if tech in language_extensions:
            ext = language_extensions[tech]
            source_files = [f for f in file_list if f.endswith(ext)]
            if source_files:
                # High confidence if we have source files
                return 0.9
        
        # Boost confidence for strong indicators
        strong_indicators = {
            'react': ['src/App.js', 'src/App.tsx', 'src/index.js'],
            'vue': ['src/App.vue', 'vue.config.js'],
            'angular': ['angular.json', 'src/app/app.module.ts'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'requirements.txt'],
            'fastapi': ['app.py', 'requirements.txt']
        }
        
        if tech in strong_indicators:
            strong_matches = sum(1 for indicator in strong_indicators[tech]
                               if any(indicator == f or f.endswith('/' + indicator) for f in file_list))
            if strong_matches >= 2:
                base_confidence *= 1.3  # Boost confidence for multiple strong indicators
        
        return min(1.0, base_confidence)

    def _categorize_technology(self, tech: str, languages: set, frameworks: set, 
                             databases: set, cloud_services: set, build_tools: set,
                             testing_frameworks: set, deployment_tools: set, 
                             package_managers: set):
        """Categorize detected technology into appropriate category"""
        language_techs = {
            "python", "javascript", "typescript", "java", "csharp", 
            "go", "rust", "php", "ruby", "swift", "kotlin", "solidity"
        }
        framework_techs = {
            "react", "vue", "angular", "django", "flask", "fastapi",
            "spring", "express", "nextjs", "gatsby", "laravel",
            # Game development frameworks
            "unity", "unreal", "godot", "pygame", "phaser",
            # Blockchain frameworks
            "truffle", "hardhat", "web3", "ethers", "anchor", "substrate"
        }
        database_techs = {
            "postgresql", "mysql", "mongodb", "redis", "sqlite", "elasticsearch"
        }
        cloud_techs = {
            "aws", "azure", "gcp", "heroku", "vercel", "netlify"
        }
        build_techs = {
            "webpack", "vite", "rollup", "gradle", "maven", "cmake"
        }
        test_techs = {
            "pytest", "jest", "unittest", "mocha", "jasmine", "phpunit"
        }
        deploy_techs = {
            "docker", "kubernetes", "terraform", "ansible"
        }
        package_techs = {
            "npm", "yarn", "pip", "composer", "cargo", "gem"
        }

        if tech in language_techs:
            languages.add(tech)
        elif tech in framework_techs:
            frameworks.add(tech)
        elif tech in database_techs:
            databases.add(tech)
        elif tech in cloud_techs:
            cloud_services.add(tech)
        elif tech in build_techs:
            build_tools.add(tech)
        elif tech in test_techs:
            testing_frameworks.add(tech)
        elif tech in deploy_techs:
            deployment_tools.add(tech)
        elif tech in package_techs:
            package_managers.add(tech)

    def _analyze_file_contents_with_confidence(self, project_path: Path, file_list: List[str],
                             languages: set, frameworks: set, databases: set,
                             cloud_services: set, build_tools: set, testing_frameworks: set,
                             deployment_tools: set, confidence_scores: Dict[str, float]):
        """Analyze file contents for technology indicators with confidence scoring"""
        # Analyze package.json for JavaScript/Node.js projects
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    
                dependencies = {}
                dependencies.update(package_data.get('dependencies', {}))
                dependencies.update(package_data.get('devDependencies', {}))
                
                # More precise dependency matching to reduce false positives
                for dep in dependencies:
                    dep_lower = dep.lower()
                    # Exact matches for major frameworks with high confidence
                    if dep_lower in ['react', 'react-dom']:
                        frameworks.add('react')
                        confidence_scores['react'] = 0.95  # High confidence for package.json detection
                    elif dep_lower in ['vue', '@vue/cli']:
                        frameworks.add('vue')
                        confidence_scores['vue'] = 0.95
                    elif dep_lower.startswith('@angular/'):
                        frameworks.add('angular')
                        confidence_scores['angular'] = 0.95
                    elif dep_lower == 'express':
                        frameworks.add('express')
                        confidence_scores['express'] = 0.90
                    elif dep_lower in ['next', 'next.js']:
                        frameworks.add('nextjs')
                        confidence_scores['nextjs'] = 0.95
                    elif dep_lower in ['jest', '@jest/core']:
                        testing_frameworks.add('jest')
                        confidence_scores['jest'] = 0.90
                    elif dep_lower == 'mocha':
                        testing_frameworks.add('mocha')
                        confidence_scores['mocha'] = 0.90
                    elif dep_lower == 'webpack':
                        build_tools.add('webpack')
                        confidence_scores['webpack'] = 0.90
                    elif dep_lower == 'vite':
                        build_tools.add('vite')
                        confidence_scores['vite'] = 0.90
                    # Database drivers
                    elif dep_lower in ['pg', 'postgres', 'postgresql']:
                        databases.add('postgresql')
                        confidence_scores['postgresql'] = 0.85
                    elif dep_lower in ['mysql', 'mysql2']:
                        databases.add('mysql')
                        confidence_scores['mysql'] = 0.85
                    elif dep_lower in ['mongodb', 'mongoose']:
                        databases.add('mongodb')
                        confidence_scores['mongodb'] = 0.85
                    elif dep_lower in ['redis', 'ioredis']:
                        databases.add('redis')
                        confidence_scores['redis'] = 0.85
            except Exception:
                pass

        # Analyze requirements.txt for Python projects with better precision
        requirements_path = project_path / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, 'r') as f:
                    requirements_content = f.read()
                    # Parse each line to avoid partial matches
                    for line in requirements_content.split('\n'):
                        line = line.strip().lower()
                        if not line or line.startswith('#'):
                            continue
                        # Extract package name (before ==, >=, etc.)
                        package_name = re.split(r'[=<>!]', line)[0].strip()
                        
                        # Framework detection with confidence scores
                        if package_name == 'django':
                            frameworks.add('django')
                            confidence_scores['django'] = 0.95
                        elif package_name == 'flask':
                            frameworks.add('flask')
                            confidence_scores['flask'] = 0.95
                        elif package_name == 'fastapi':
                            frameworks.add('fastapi')
                            confidence_scores['fastapi'] = 0.95
                        elif package_name == 'pytest':
                            testing_frameworks.add('pytest')
                            confidence_scores['pytest'] = 0.90
                        # ML libraries should not be considered frameworks for project classification
                        # They are dependencies but don't define the project structure
                        # Commented out to prevent false framework detection in ML projects
                        # elif package_name in ['tensorflow', 'tensorflow-gpu']:
                        #     frameworks.add('tensorflow')
                        #     confidence_scores['tensorflow'] = 0.95
                        # elif package_name in ['torch', 'pytorch']:
                        #     frameworks.add('pytorch')
                        #     confidence_scores['pytorch'] = 0.95
                        # elif package_name in ['scikit-learn', 'sklearn']:
                        #     frameworks.add('sklearn')
                        #     confidence_scores['sklearn'] = 0.90
                        # Database drivers
                        elif package_name in ['psycopg2', 'psycopg2-binary']:
                            databases.add('postgresql')
                            confidence_scores['postgresql'] = 0.90
                        elif package_name in ['mysql-connector-python', 'pymysql']:
                            databases.add('mysql')
                            confidence_scores['mysql'] = 0.90
                        elif package_name == 'pymongo':
                            databases.add('mongodb')
                            confidence_scores['mongodb'] = 0.90
                        elif package_name == 'redis':
                            databases.add('redis')
                            confidence_scores['redis'] = 0.85
            except Exception:
                pass
        
        # Analyze specific configuration files for more accurate detection
        self._analyze_config_files(project_path, file_list, frameworks, databases, cloud_services)
        
        return confidence_scores

    def _analyze_config_files(self, project_path: Path, file_list: List[str], 
                             frameworks: set, databases: set, cloud_services: set):
        """Analyze configuration files for more precise technology detection"""
        
        # Check for React-specific files
        if any(f in file_list for f in ['src/App.js', 'src/App.tsx', 'src/index.js', 'src/index.tsx']):
            if 'package.json' in file_list:
                frameworks.add('react')
        
        # Check for Vue-specific files
        if any(f in file_list for f in ['src/App.vue', 'vue.config.js', 'src/main.js']):
            frameworks.add('vue')
        
        # Check for Angular-specific files
        if 'angular.json' in file_list or any(f.endswith('app.module.ts') for f in file_list):
            frameworks.add('angular')
        
        # Check for Next.js specific files
        if 'next.config.js' in file_list or any(f.startswith('pages/') for f in file_list):
            frameworks.add('nextjs')
        
        # Check for Django-specific files
        if any(f in file_list for f in ['manage.py', 'settings.py', 'urls.py', 'wsgi.py']):
            frameworks.add('django')
        
        # Check for Flask-specific patterns
        if any(f in ['app.py', 'application.py', 'run.py'] for f in file_list) and 'python' in {
            self._detect_language_from_files(file_list)
        }:
            # Only add Flask if we find Flask-specific imports in Python files
            try:
                for file_path in file_list:
                    if file_path.endswith('.py'):
                        full_path = project_path / file_path
                        if full_path.exists():
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(1000)  # Read first 1000 chars
                                if 'from flask import' in content or 'import flask' in content:
                                    frameworks.add('flask')
                                    break
            except Exception:
                pass
        
        # Check for FastAPI-specific patterns
        try:
            for file_path in file_list:
                if file_path.endswith('.py'):
                    full_path = project_path / file_path
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(1000)
                            if 'from fastapi import' in content or 'import fastapi' in content:
                                frameworks.add('fastapi')
                                break
        except Exception:
            pass
        
        # Database configuration detection
        config_files = [f for f in file_list if 'config' in f.lower() or f.endswith(('.env', '.ini', '.conf'))]
        for config_file in config_files:
            try:
                config_path = project_path / config_file
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if 'postgresql' in content or 'postgres' in content:
                            databases.add('postgresql')
                        if 'mysql' in content:
                            databases.add('mysql')
                        if 'mongodb' in content or 'mongo' in content:
                            databases.add('mongodb')
                        if 'redis' in content:
                            databases.add('redis')
            except Exception:
                pass

    def _detect_language_from_files(self, file_list: List[str]) -> str:
        """Detect primary language from file list"""
        extensions = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', 
                     '.java': 'java', '.go': 'go', '.rs': 'rust'}
        
        for file_path in file_list:
            for ext, lang in extensions.items():
                if file_path.endswith(ext):
                    return lang
        return 'unknown'

    def _analyze_structure(self, file_list: List[str], project_path: Path) -> ProjectStructure:
        """Analyze project structure characteristics"""
        has_tests = any(
            'test' in file_path.lower() or file_path.endswith(('.test.js', '.test.py', '_test.py'))
            for file_path in file_list
        )
        
        has_docs = any(
            file_path.startswith(('docs/', 'documentation/')) or 
            file_path.lower() in ('readme.md', 'readme.txt', 'readme.rst')
            for file_path in file_list
        )
        
        has_ci_cd = any(
            file_path.startswith(('.github/workflows/', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci/'))
            for file_path in file_list
        )
        
        has_docker = any(
            file_path in ('Dockerfile', 'docker-compose.yml', '.dockerignore')
            for file_path in file_list
        )
        
        has_api = any(
            'api' in file_path.lower() or 'routes' in file_path.lower() or
            'endpoints' in file_path.lower() or 'controllers' in file_path.lower()
            for file_path in file_list
        )
        
        has_frontend = any(
            file_path.startswith(('src/', 'public/', 'assets/')) or
            file_path.endswith(('.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue'))
            for file_path in file_list
        )
        
        has_backend = any(
            'server' in file_path.lower() or 'backend' in file_path.lower() or
            file_path.endswith(('.py', '.java', '.go', '.rs', '.php'))
            for file_path in file_list
        )
        
        has_database = any(
            'models' in file_path.lower() or 'schema' in file_path.lower() or
            'migrations' in file_path.lower() or file_path.endswith('.sql')
            for file_path in file_list
        )
        
        # Find entry points
        entry_points = []
        common_entry_files = [
            'main.py', 'app.py', 'server.py', 'index.js', 'app.js', 'server.js',
            'main.go', 'main.rs', 'Main.java', 'Program.cs', 'index.html'
        ]
        for entry_file in common_entry_files:
            if entry_file in file_list:
                entry_points.append(entry_file)
        
        # Find configuration files
        config_files = []
        config_patterns = [
            'config.json', 'config.yml', 'config.yaml', '.env', 'settings.py',
            'application.properties', 'tsconfig.json', 'webpack.config.js',
            'vite.config.js', 'next.config.js', 'nuxt.config.js'
        ]
        for config_file in config_patterns:
            if config_file in file_list:
                config_files.append(config_file)

        return ProjectStructure(
            has_tests=has_tests,
            has_docs=has_docs,
            has_ci_cd=has_ci_cd,
            has_docker=has_docker,
            has_api=has_api,
            has_frontend=has_frontend,
            has_backend=has_backend,
            has_database=has_database,
            entry_points=entry_points,
            config_files=config_files
        )

    def _classify_project_type(self, tech_stack: TechnologyStack, 
                             structure: ProjectStructure, 
                             file_list: List[str]) -> Tuple[ProjectType, float]:
        """Classify project type based on analysis"""
        scores = {}
        
        # Web App indicators
        web_score = 0
        if structure.has_frontend and any(fw in tech_stack.frameworks for fw in ['react', 'vue', 'angular']):
            web_score += 0.4
        if 'javascript' in tech_stack.languages or 'typescript' in tech_stack.languages:
            web_score += 0.2
        if any(file_path.endswith('.html') for file_path in file_list):
            web_score += 0.2
        if structure.has_api:
            web_score += 0.2
        scores[ProjectType.WEB_APP] = web_score
        
        # API Service indicators
        api_score = 0
        if structure.has_api and structure.has_backend and not structure.has_frontend:
            api_score += 0.5
        if any(fw in tech_stack.frameworks for fw in ['flask', 'fastapi', 'express', 'spring']):
            api_score += 0.3
        if structure.has_database:
            api_score += 0.2
        scores[ProjectType.API_SERVICE] = api_score
        
        # ML Project indicators
        ml_score = 0
        if 'python' in tech_stack.languages:
            ml_score += 0.2
        if any(file_path.endswith('.ipynb') for file_path in file_list):
            ml_score += 0.3
        if any('tensorflow' in fw or 'pytorch' in fw or 'sklearn' in fw for fw in tech_stack.frameworks):
            ml_score += 0.4
        if any('data' in file_path.lower() or 'models' in file_path.lower() for file_path in file_list):
            ml_score += 0.1
        scores[ProjectType.ML_PROJECT] = ml_score
        
        # Mobile App indicators
        mobile_score = 0
        if 'swift' in tech_stack.languages or any(file_path.endswith('.xcodeproj') for file_path in file_list):
            mobile_score += 0.5
        if any('android' in file_path.lower() or 'ios' in file_path.lower() for file_path in file_list):
            mobile_score += 0.3
        if 'react_native' in tech_stack.frameworks or 'flutter' in tech_stack.frameworks:
            mobile_score += 0.4
        scores[ProjectType.MOBILE_APP] = mobile_score
        
        # CLI Tool indicators
        cli_score = 0
        if len(structure.entry_points) == 1 and not structure.has_frontend:
            cli_score += 0.3
        if any('cli' in file_path.lower() or 'command' in file_path.lower() for file_path in file_list):
            cli_score += 0.4
        if not structure.has_api and not structure.has_frontend:
            cli_score += 0.2
        scores[ProjectType.CLI_TOOL] = cli_score
        
        # Library indicators  
        lib_score = 0
        if any(file_path in ['setup.py', 'package.json', 'Cargo.toml', 'pom.xml'] for file_path in file_list):
            lib_score += 0.3
        if structure.has_tests and not structure.has_frontend and not structure.has_api:
            lib_score += 0.4
        if any('lib' in file_path.lower() or 'src' in file_path.lower() for file_path in file_list):
            lib_score += 0.2
        scores[ProjectType.LIBRARY] = lib_score
        
        # Game Development indicators
        game_score = 0
        if any(engine in tech_stack.frameworks for engine in ['unity', 'unreal', 'godot', 'pygame', 'phaser']):
            game_score += 0.5
        if any(file_path.endswith(('.unity', '.uproject', '.godot', '.tscn')) for file_path in file_list):
            game_score += 0.4
        if any(folder in file_list for folder in ['Assets/', 'Resources/', 'Scenes/', 'Scripts/Game/']):
            game_score += 0.2
        if 'csharp' in tech_stack.languages and any('unity' in file_path.lower() for file_path in file_list):
            game_score += 0.3
        if any(keyword in str(file_list).lower() for keyword in ['player', 'enemy', 'level', 'sprite', 'shader']):
            game_score += 0.1
        scores[ProjectType.GAME_DEV] = game_score
        
        # Blockchain/Smart Contract indicators
        blockchain_score = 0
        if 'solidity' in tech_stack.languages:
            blockchain_score += 0.5
        if any(file_path.endswith('.sol') for file_path in file_list):
            blockchain_score += 0.4
        if any(fw in tech_stack.frameworks for fw in ['truffle', 'hardhat', 'web3', 'ethers']):
            blockchain_score += 0.3
        if any(folder in file_list for folder in ['contracts/', 'migrations/', 'test/']):
            blockchain_score += 0.2
        if any(keyword in str(file_list).lower() for keyword in ['blockchain', 'smart_contract', 'defi', 'nft', 'token']):
            blockchain_score += 0.1
        if 'rust' in tech_stack.languages and any('substrate' in fw or 'anchor' in fw for fw in tech_stack.frameworks):
            blockchain_score += 0.3
        scores[ProjectType.BLOCKCHAIN] = blockchain_score

        # Find best match
        if not scores or max(scores.values()) < 0.3:
            # Default fallback logic
            if structure.has_frontend:
                return ProjectType.WEB_APP, 0.5
            elif structure.has_api:
                return ProjectType.API_SERVICE, 0.5
            else:
                return ProjectType.CLI_TOOL, 0.3
        
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        return best_type, confidence

    def _detect_patterns(self, file_list: List[str], project_path: Path) -> List[str]:
        """Detect common development patterns"""
        patterns = []
        
        # Architecture patterns
        if any('mvc' in file_path.lower() for file_path in file_list):
            patterns.append("MVC Architecture")
        if any('components' in file_path.lower() for file_path in file_list):
            patterns.append("Component-Based Architecture")
        if any('microservices' in file_path.lower() or 'services' in file_path.lower() for file_path in file_list):
            patterns.append("Microservices")
        
        # Development patterns
        if any('test' in file_path.lower() for file_path in file_list):
            patterns.append("Test-Driven Development")
        if any(file_path.startswith('.github/workflows/') for file_path in file_list):
            patterns.append("CI/CD Pipeline")
        if any(file_path in ['Dockerfile', 'docker-compose.yml'] for file_path in file_list):
            patterns.append("Containerization")
        
        # Data patterns
        if any('api' in file_path.lower() for file_path in file_list):
            patterns.append("RESTful API")
        if any('graphql' in file_path.lower() for file_path in file_list):
            patterns.append("GraphQL")
        if any('migrations' in file_path.lower() for file_path in file_list):
            patterns.append("Database Migrations")
        
        return patterns

    def _suggest_workflow(self, project_type: ProjectType, tech_stack: TechnologyStack, 
                         structure: ProjectStructure) -> str:
        """Suggest appropriate workflow template"""
        if project_type in self.workflow_templates:
            return self.workflow_templates[project_type]["name"]
        else:
            return "Custom Development Workflow"

    def _estimate_complexity(self, tech_stack: TechnologyStack, structure: ProjectStructure, 
                           file_count: int) -> str:
        """Estimate project complexity"""
        complexity_score = 0
        
        # File count factor
        if file_count > 500:
            complexity_score += 3
        elif file_count > 100:
            complexity_score += 2
        elif file_count > 50:
            complexity_score += 1
        
        # Technology factor
        complexity_score += len(tech_stack.languages) * 0.5
        complexity_score += len(tech_stack.frameworks) * 0.3
        complexity_score += len(tech_stack.databases) * 0.4
        
        # Structure factor
        if structure.has_frontend and structure.has_backend:
            complexity_score += 2
        if structure.has_database:
            complexity_score += 1
        if structure.has_api:
            complexity_score += 1
        if structure.has_docker:
            complexity_score += 0.5
        
        if complexity_score >= 6:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"

    def _recommend_team_size(self, complexity: str, project_type: ProjectType, 
                           tech_stack: TechnologyStack) -> int:
        """Recommend team size based on project characteristics"""
        base_size = {
            "low": 1,
            "medium": 2,
            "high": 4
        }.get(complexity, 2)
        
        # Adjust based on project type
        if project_type == ProjectType.WEB_APP:
            base_size += 1
        elif project_type == ProjectType.ML_PROJECT:
            base_size += 1
        elif project_type == ProjectType.MOBILE_APP:
            base_size += 2
        
        # Adjust based on technology stack complexity
        total_technologies = (len(tech_stack.languages) + len(tech_stack.frameworks) + 
                            len(tech_stack.databases) + len(tech_stack.cloud_services))
        if total_technologies > 10:
            base_size += 1
        elif total_technologies > 15:
            base_size += 2
        
        return min(base_size, 8)  # Cap at 8 team members

    def generate_project_report(self, analysis: AnalysisResult, project_path: str) -> str:
        """Generate a comprehensive project analysis report"""
        report = f"""
# Project Analysis Report

**Project Path:** {project_path}
**Analysis Date:** {json.dumps(None, default=str)}

## Project Classification
- **Type:** {analysis.project_type.value.replace('_', ' ').title()}
- **Confidence:** {analysis.confidence:.2%}
- **Estimated Complexity:** {analysis.estimated_complexity.title()}
- **Recommended Team Size:** {analysis.team_size_recommendation} developers

## Technology Stack

### Languages
{chr(10).join(f"- {lang.title()}" for lang in analysis.tech_stack.languages)}

### Frameworks & Libraries
{chr(10).join(f"- {fw.title()}" for fw in analysis.tech_stack.frameworks)}

### Databases
{chr(10).join(f"- {db.title()}" for db in analysis.tech_stack.databases)}

### Development Tools
{chr(10).join(f"- {tool.title()}" for tool in analysis.tech_stack.build_tools)}

### Testing Frameworks
{chr(10).join(f"- {test.title()}" for test in analysis.tech_stack.testing_frameworks)}

## Project Structure Analysis

- **Has Tests:** {"✅" if analysis.structure.has_tests else "❌"}
- **Has Documentation:** {"✅" if analysis.structure.has_docs else "❌"}
- **Has CI/CD:** {"✅" if analysis.structure.has_ci_cd else "❌"}
- **Has Docker:** {"✅" if analysis.structure.has_docker else "❌"}
- **Has API:** {"✅" if analysis.structure.has_api else "❌"}
- **Has Frontend:** {"✅" if analysis.structure.has_frontend else "❌"}
- **Has Backend:** {"✅" if analysis.structure.has_backend else "❌"}
- **Has Database:** {"✅" if analysis.structure.has_database else "❌"}

### Entry Points
{chr(10).join(f"- {ep}" for ep in analysis.structure.entry_points) if analysis.structure.entry_points else "- None detected"}

### Configuration Files
{chr(10).join(f"- {cf}" for cf in analysis.structure.config_files) if analysis.structure.config_files else "- None detected"}

## Detected Patterns
{chr(10).join(f"- {pattern}" for pattern in analysis.detected_patterns) if analysis.detected_patterns else "- No specific patterns detected"}

## Recommended Workflow
**{analysis.suggested_workflow}**

This analysis suggests using the {analysis.suggested_workflow.lower()} template for optimal development workflow organization.

## Next Steps
1. Review the suggested workflow template
2. Set up the recommended team structure
3. Configure development environment based on detected technologies
4. Implement missing infrastructure (CI/CD, testing, documentation) as identified
"""
        return report

def main():
    """Command-line interface for project analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze project structure and suggest workflows")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file for analysis results")
    parser.add_argument("--format", choices=["json", "report"], default="report", 
                       help="Output format")
    
    args = parser.parse_args()
    
    analyzer = ProjectAnalyzer()
    
    try:
        analysis = analyzer.analyze_project(args.project_path)
        
        if args.format == "json":
            output = json.dumps(asdict(analysis), indent=2, default=str)
        else:
            output = analyzer.generate_project_report(analysis, args.project_path)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Analysis written to {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error analyzing project: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())