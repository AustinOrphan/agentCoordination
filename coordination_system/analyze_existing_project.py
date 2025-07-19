#!/usr/bin/env python3
"""
Analyze an existing codebase to prepare it for multi-agent coordination.
This tool examines project structure, identifies improvement areas, and suggests task assignments.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
from collections import defaultdict

class ProjectAnalyzer:
    def __init__(self, project_path):
        self.project_path = Path(project_path).resolve()
        self.analysis = {
            "project_info": {},
            "structure": {},
            "technologies": {},
            "quality_metrics": {},
            "suggested_tasks": [],
            "agent_assignments": {}
        }
    
    def run_analysis(self):
        """Run complete project analysis."""
        print(f"🔍 Analyzing project at: {self.project_path}")
        
        self.analyze_project_info()
        self.analyze_structure()
        self.detect_technologies()
        self.analyze_code_quality()
        self.identify_improvement_areas()
        self.suggest_agent_tasks()
        
        return self.analysis
    
    def analyze_project_info(self):
        """Extract basic project information."""
        print("📊 Gathering project information...")
        
        # Check for git repository
        is_git_repo = (self.project_path / '.git').exists()
        
        # Get project name
        project_name = self.project_path.name
        
        # Count files and size
        total_files = 0
        total_size = 0
        file_types = defaultdict(int)
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and common ignored paths
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'dist', 'build']]
            
            for file in files:
                if not file.startswith('.'):
                    total_files += 1
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                        ext = file_path.suffix.lower()
                        if ext:
                            file_types[ext] += 1
                    except:
                        pass
        
        self.analysis["project_info"] = {
            "name": project_name,
            "path": str(self.project_path),
            "is_git_repo": is_git_repo,
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10])
        }
        
        # Get git info if available
        if is_git_repo:
            try:
                # Get current branch
                branch = subprocess.check_output(
                    ['git', 'branch', '--show-current'],
                    cwd=self.project_path,
                    text=True
                ).strip()
                
                # Get last commit
                last_commit = subprocess.check_output(
                    ['git', 'log', '-1', '--pretty=%h - %s (%ar)'],
                    cwd=self.project_path,
                    text=True
                ).strip()
                
                # Count commits
                commit_count = subprocess.check_output(
                    ['git', 'rev-list', '--count', 'HEAD'],
                    cwd=self.project_path,
                    text=True
                ).strip()
                
                self.analysis["project_info"]["git"] = {
                    "branch": branch,
                    "last_commit": last_commit,
                    "total_commits": int(commit_count)
                }
            except:
                pass
    
    def analyze_structure(self):
        """Analyze project structure and organization."""
        print("🗂️  Analyzing project structure...")
        
        structure = {
            "directories": {},
            "key_files": [],
            "entry_points": []
        }
        
        # Map common directories
        common_dirs = {
            "src": "Source code",
            "lib": "Libraries",
            "test": "Tests",
            "tests": "Tests",
            "spec": "Tests",
            "docs": "Documentation",
            "config": "Configuration",
            "scripts": "Scripts",
            "api": "API code",
            "frontend": "Frontend code",
            "backend": "Backend code",
            "components": "UI Components",
            "models": "Data models",
            "controllers": "Controllers",
            "views": "Views",
            "services": "Services",
            "utils": "Utilities",
            "helpers": "Helper functions"
        }
        
        # Check which directories exist
        for dir_name, description in common_dirs.items():
            for root, dirs, _ in os.walk(self.project_path):
                if dir_name in dirs:
                    rel_path = Path(root) / dir_name
                    structure["directories"][dir_name] = {
                        "path": str(rel_path.relative_to(self.project_path)),
                        "description": description
                    }
                    break
        
        # Look for key files
        key_files = [
            "README.md", "readme.md", "README.rst",
            "package.json", "requirements.txt", "Pipfile", "poetry.lock",
            "Gemfile", "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
            "Makefile", "Dockerfile", "docker-compose.yml",
            ".env.example", "config.json", "settings.py"
        ]
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file in key_files:
                    rel_path = Path(root) / file
                    structure["key_files"].append(str(rel_path.relative_to(self.project_path)))
        
        # Identify entry points
        entry_patterns = [
            "main.py", "app.py", "index.js", "server.js", "main.go",
            "Main.java", "main.rs", "index.html", "index.php"
        ]
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file in entry_patterns:
                    rel_path = Path(root) / file
                    structure["entry_points"].append(str(rel_path.relative_to(self.project_path)))
        
        self.analysis["structure"] = structure
    
    def detect_technologies(self):
        """Detect technologies and frameworks used."""
        print("🔧 Detecting technologies...")
        
        tech = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
            "package_managers": []
        }
        
        # Language detection based on file extensions
        lang_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".cpp": "C++",
            ".c": "C",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".r": "R"
        }
        
        detected_langs = set()
        for ext, count in self.analysis["project_info"]["file_types"].items():
            if ext in lang_extensions and count > 0:
                detected_langs.add(lang_extensions[ext])
        
        tech["languages"] = list(detected_langs)
        
        # Framework detection based on config files and imports
        framework_indicators = {
            "package.json": {
                "react": "React",
                "vue": "Vue.js",
                "angular": "Angular",
                "express": "Express.js",
                "next": "Next.js",
                "gatsby": "Gatsby",
                "svelte": "Svelte"
            },
            "requirements.txt": {
                "django": "Django",
                "flask": "Flask",
                "fastapi": "FastAPI",
                "pyramid": "Pyramid",
                "tornado": "Tornado"
            },
            "Gemfile": {
                "rails": "Ruby on Rails",
                "sinatra": "Sinatra"
            },
            "go.mod": {
                "gin": "Gin",
                "echo": "Echo",
                "fiber": "Fiber"
            }
        }
        
        # Check for frameworks
        for config_file, frameworks in framework_indicators.items():
            file_path = self.project_path / config_file
            if file_path.exists():
                try:
                    content = file_path.read_text().lower()
                    for keyword, framework in frameworks.items():
                        if keyword in content:
                            tech["frameworks"].append(framework)
                except:
                    pass
        
        # Database detection
        db_indicators = {
            "postgresql": ["psycopg2", "pg", "postgresql"],
            "mysql": ["mysql", "mysqlclient", "mysql2"],
            "mongodb": ["mongodb", "mongoose", "pymongo"],
            "redis": ["redis", "ioredis"],
            "sqlite": ["sqlite3", "sqlite"],
            "elasticsearch": ["elasticsearch", "elastic"]
        }
        
        # Check various config files for database indicators
        config_files = ["package.json", "requirements.txt", "Gemfile", "go.mod", "pom.xml"]
        for config_file in config_files:
            file_path = self.project_path / config_file
            if file_path.exists():
                try:
                    content = file_path.read_text().lower()
                    for db, keywords in db_indicators.items():
                        if any(keyword in content for keyword in keywords):
                            tech["databases"].append(db.capitalize())
                except:
                    pass
        
        # Package manager detection
        pm_files = {
            "package.json": "npm/yarn",
            "requirements.txt": "pip",
            "Pipfile": "pipenv",
            "poetry.lock": "poetry",
            "Gemfile": "bundler",
            "go.mod": "go modules",
            "Cargo.toml": "cargo",
            "pom.xml": "maven",
            "build.gradle": "gradle"
        }
        
        for pm_file, pm_name in pm_files.items():
            if (self.project_path / pm_file).exists():
                tech["package_managers"].append(pm_name)
        
        # Build tools
        build_files = {
            "Makefile": "Make",
            "Dockerfile": "Docker",
            "docker-compose.yml": "Docker Compose",
            ".github/workflows": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            "Jenkinsfile": "Jenkins",
            ".travis.yml": "Travis CI"
        }
        
        for build_file, tool in build_files.items():
            if (self.project_path / build_file).exists():
                tech["tools"].append(tool)
        
        self.analysis["technologies"] = tech
    
    def analyze_code_quality(self):
        """Analyze code quality indicators."""
        print("📈 Analyzing code quality indicators...")
        
        quality = {
            "has_tests": False,
            "has_ci": False,
            "has_linting": False,
            "has_documentation": False,
            "has_type_checking": False,
            "test_coverage": "Unknown",
            "code_smells": []
        }
        
        # Check for tests
        test_dirs = ["test", "tests", "spec", "__tests__"]
        test_files = []
        for root, dirs, files in os.walk(self.project_path):
            # Check for test directories
            if any(test_dir in dirs for test_dir in test_dirs):
                quality["has_tests"] = True
            
            # Check for test files
            for file in files:
                if any(pattern in file.lower() for pattern in ["test_", "_test", ".test.", ".spec."]):
                    test_files.append(file)
        
        if test_files:
            quality["has_tests"] = True
            quality["test_file_count"] = len(test_files)
        
        # Check for CI/CD
        ci_files = [
            ".github/workflows", ".gitlab-ci.yml", "Jenkinsfile",
            ".travis.yml", ".circleci/config.yml", "azure-pipelines.yml"
        ]
        
        for ci_file in ci_files:
            if (self.project_path / ci_file).exists():
                quality["has_ci"] = True
                break
        
        # Check for linting configuration
        lint_files = [
            ".eslintrc", ".eslintrc.js", ".eslintrc.json",
            ".pylintrc", "pyproject.toml", "setup.cfg",
            ".rubocop.yml", "tslint.json", ".flake8"
        ]
        
        for lint_file in lint_files:
            if (self.project_path / lint_file).exists():
                quality["has_linting"] = True
                break
        
        # Check for documentation
        doc_indicators = ["README.md", "docs/", "documentation/", "wiki/"]
        for indicator in doc_indicators:
            if (self.project_path / indicator).exists():
                quality["has_documentation"] = True
                break
        
        # Check for type checking (TypeScript, Python type hints, etc.)
        if ".ts" in self.analysis["project_info"]["file_types"]:
            quality["has_type_checking"] = True
        elif "mypy" in str(self.project_path / "requirements.txt") if (self.project_path / "requirements.txt").exists() else "":
            quality["has_type_checking"] = True
        
        # Identify potential code smells
        large_files = []
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cs', '.cpp')):
                    file_path = Path(root) / file
                    try:
                        size = file_path.stat().st_size
                        if size > 100000:  # Files larger than 100KB
                            large_files.append(str(file_path.relative_to(self.project_path)))
                    except:
                        pass
        
        if large_files:
            quality["code_smells"].append({
                "type": "Large files",
                "description": f"Found {len(large_files)} files larger than 100KB",
                "files": large_files[:5]  # Show first 5
            })
        
        # Check for TODO/FIXME comments
        todo_count = 0
        fixme_count = 0
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cs', '.go', '.rb')):
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text()
                        todo_count += content.upper().count('TODO')
                        fixme_count += content.upper().count('FIXME')
                    except:
                        pass
        
        if todo_count > 20:
            quality["code_smells"].append({
                "type": "Accumulated TODOs",
                "description": f"Found {todo_count} TODO comments",
                "severity": "medium"
            })
        
        if fixme_count > 10:
            quality["code_smells"].append({
                "type": "Unresolved FIXMEs",
                "description": f"Found {fixme_count} FIXME comments",
                "severity": "high"
            })
        
        self.analysis["quality_metrics"] = quality
    
    def identify_improvement_areas(self):
        """Identify areas that need improvement."""
        print("🎯 Identifying improvement areas...")
        
        improvements = []
        
        # Based on quality metrics
        quality = self.analysis["quality_metrics"]
        
        if not quality["has_tests"]:
            improvements.append({
                "area": "Testing",
                "priority": "high",
                "description": "No test suite detected",
                "suggested_actions": [
                    "Set up testing framework",
                    "Write unit tests for core functionality",
                    "Add integration tests"
                ]
            })
        elif quality.get("test_file_count", 0) < 5:
            improvements.append({
                "area": "Test Coverage",
                "priority": "medium",
                "description": "Limited test coverage detected",
                "suggested_actions": [
                    "Increase test coverage",
                    "Add tests for edge cases",
                    "Set up coverage reporting"
                ]
            })
        
        if not quality["has_ci"]:
            improvements.append({
                "area": "CI/CD",
                "priority": "high",
                "description": "No continuous integration detected",
                "suggested_actions": [
                    "Set up CI pipeline",
                    "Add automated testing to CI",
                    "Configure deployment automation"
                ]
            })
        
        if not quality["has_linting"]:
            improvements.append({
                "area": "Code Quality",
                "priority": "medium",
                "description": "No linting configuration found",
                "suggested_actions": [
                    "Set up code linter",
                    "Define coding standards",
                    "Add pre-commit hooks"
                ]
            })
        
        if not quality["has_documentation"]:
            improvements.append({
                "area": "Documentation",
                "priority": "medium",
                "description": "Missing or minimal documentation",
                "suggested_actions": [
                    "Create comprehensive README",
                    "Add API documentation",
                    "Write developer guides"
                ]
            })
        
        # Based on structure
        structure = self.analysis["structure"]
        
        if not structure["directories"].get("tests") and not structure["directories"].get("test"):
            improvements.append({
                "area": "Project Structure",
                "priority": "medium",
                "description": "No dedicated test directory",
                "suggested_actions": [
                    "Create test directory structure",
                    "Organize tests by module"
                ]
            })
        
        # Based on technologies
        tech = self.analysis["technologies"]
        
        if "Docker" not in tech["tools"]:
            improvements.append({
                "area": "Containerization",
                "priority": "low",
                "description": "No containerization detected",
                "suggested_actions": [
                    "Create Dockerfile",
                    "Add docker-compose for local development",
                    "Document container setup"
                ]
            })
        
        if not tech["databases"] and any(lang in tech["languages"] for lang in ["Python", "JavaScript", "Java", "Ruby"]):
            improvements.append({
                "area": "Data Persistence",
                "priority": "info",
                "description": "No database configuration detected",
                "suggested_actions": [
                    "Evaluate data storage needs",
                    "Set up database if needed",
                    "Add data models"
                ]
            })
        
        # Security considerations
        if (self.project_path / ".env").exists() and not (self.project_path / ".env.example").exists():
            improvements.append({
                "area": "Security",
                "priority": "high",
                "description": ".env file found without .env.example",
                "suggested_actions": [
                    "Create .env.example with dummy values",
                    "Ensure .env is in .gitignore",
                    "Document environment variables"
                ]
            })
        
        self.analysis["improvements"] = improvements
    
    def suggest_agent_tasks(self):
        """Suggest specific tasks for agents based on analysis."""
        print("🤖 Generating agent task suggestions...")
        
        tasks = []
        agent_roles = [
            "Critical Path Lead",
            "Migration Specialist",
            "Dashboard Developer",
            "DevOps Engineer",
            "Security Engineer",
            "UX Engineer"
        ]
        
        # Generate tasks based on improvements
        for improvement in self.analysis["improvements"]:
            if improvement["priority"] in ["high", "medium"]:
                # Determine best agent for this task
                agent_role = None
                
                if improvement["area"] in ["Testing", "Test Coverage"]:
                    agent_role = "Critical Path Lead"
                elif improvement["area"] in ["CI/CD", "Containerization"]:
                    agent_role = "DevOps Engineer"
                elif improvement["area"] == "Security":
                    agent_role = "Security Engineer"
                elif improvement["area"] == "Documentation":
                    agent_role = "Migration Specialist"
                elif improvement["area"] in ["Code Quality", "Project Structure"]:
                    agent_role = "Critical Path Lead"
                
                if agent_role:
                    for action in improvement["suggested_actions"]:
                        tasks.append({
                            "task": action,
                            "area": improvement["area"],
                            "priority": improvement["priority"],
                            "suggested_agent_role": agent_role,
                            "estimated_effort": "medium",
                            "dependencies": []
                        })
        
        # Add technology-specific tasks
        tech = self.analysis["technologies"]
        
        # Frontend tasks
        if any(fw in tech["frameworks"] for fw in ["React", "Vue.js", "Angular"]):
            tasks.extend([
                {
                    "task": "Audit and optimize frontend performance",
                    "area": "Frontend",
                    "priority": "medium",
                    "suggested_agent_role": "UX Engineer",
                    "estimated_effort": "medium",
                    "dependencies": []
                },
                {
                    "task": "Implement responsive design improvements",
                    "area": "Frontend",
                    "priority": "low",
                    "suggested_agent_role": "UX Engineer",
                    "estimated_effort": "medium",
                    "dependencies": []
                }
            ])
        
        # Backend tasks
        if any(fw in tech["frameworks"] for fw in ["Django", "Flask", "Express.js", "FastAPI"]):
            tasks.extend([
                {
                    "task": "Optimize API endpoints and database queries",
                    "area": "Backend",
                    "priority": "medium",
                    "suggested_agent_role": "Migration Specialist",
                    "estimated_effort": "high",
                    "dependencies": []
                },
                {
                    "task": "Implement API versioning and documentation",
                    "area": "Backend",
                    "priority": "medium",
                    "suggested_agent_role": "Migration Specialist",
                    "estimated_effort": "medium",
                    "dependencies": []
                }
            ])
        
        # Database tasks
        if tech["databases"]:
            tasks.append({
                "task": "Audit database schema and add indexes for performance",
                "area": "Database",
                "priority": "medium",
                "suggested_agent_role": "Migration Specialist",
                "estimated_effort": "medium",
                "dependencies": []
            })
        
        # Security tasks
        tasks.extend([
            {
                "task": "Conduct security audit and fix vulnerabilities",
                "area": "Security",
                "priority": "high",
                "suggested_agent_role": "Security Engineer",
                "estimated_effort": "high",
                "dependencies": []
            },
            {
                "task": "Implement authentication and authorization improvements",
                "area": "Security",
                "priority": "medium",
                "suggested_agent_role": "Security Engineer",
                "estimated_effort": "high",
                "dependencies": ["Conduct security audit and fix vulnerabilities"]
            }
        ])
        
        # Full-stack tasks
        if tech["frameworks"]:
            tasks.append({
                "task": "Create comprehensive developer dashboard",
                "area": "Full-stack",
                "priority": "low",
                "suggested_agent_role": "Dashboard Developer",
                "estimated_effort": "high",
                "dependencies": []
            })
        
        self.analysis["suggested_tasks"] = tasks
        
        # Create agent assignments
        assignments = defaultdict(list)
        
        # Distribute tasks among agents
        for i, task in enumerate(tasks):
            role = task["suggested_agent_role"]
            # Find which agent number gets this role (cycles through 6 roles)
            role_index = agent_roles.index(role)
            agent_number = role_index + 1  # 1-indexed
            
            # Map to actual agent name based on current theme
            # This will be determined at runtime
            assignments[f"Agent_{agent_number}_{role}"].append(task)
        
        self.analysis["agent_assignments"] = dict(assignments)
    
    def save_analysis(self, output_path=None):
        """Save analysis results to file."""
        if not output_path:
            output_path = Path.cwd() / "project_analysis.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {output_path}")
        return output_path
    
    def generate_report(self):
        """Generate human-readable report."""
        report = f"""# 📊 Project Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 Project Information
- **Name**: {self.analysis['project_info']['name']}
- **Path**: {self.analysis['project_info']['path']}
- **Total Files**: {self.analysis['project_info']['total_files']:,}
- **Total Size**: {self.analysis['project_info']['total_size_mb']} MB
- **Git Repository**: {'Yes' if self.analysis['project_info']['is_git_repo'] else 'No'}
"""
        
        if self.analysis['project_info'].get('git'):
            git_info = self.analysis['project_info']['git']
            report += f"""- **Current Branch**: {git_info['branch']}
- **Last Commit**: {git_info['last_commit']}
- **Total Commits**: {git_info['total_commits']:,}
"""
        
        # Technologies
        tech = self.analysis['technologies']
        report += f"""
## 🛠️ Technologies Detected
- **Languages**: {', '.join(tech['languages']) or 'None detected'}
- **Frameworks**: {', '.join(tech['frameworks']) or 'None detected'}
- **Databases**: {', '.join(tech['databases']) or 'None detected'}
- **Build Tools**: {', '.join(tech['tools']) or 'None detected'}
- **Package Managers**: {', '.join(tech['package_managers']) or 'None detected'}

## 📈 Code Quality Metrics
"""
        
        quality = self.analysis['quality_metrics']
        report += f"""- **Has Tests**: {'✅ Yes' if quality['has_tests'] else '❌ No'}
- **Has CI/CD**: {'✅ Yes' if quality['has_ci'] else '❌ No'}
- **Has Linting**: {'✅ Yes' if quality['has_linting'] else '❌ No'}
- **Has Documentation**: {'✅ Yes' if quality['has_documentation'] else '❌ No'}
- **Type Checking**: {'✅ Yes' if quality['has_type_checking'] else '❌ No'}
"""
        
        if quality['code_smells']:
            report += "\n### ⚠️ Code Smells Detected\n"
            for smell in quality['code_smells']:
                report += f"- **{smell['type']}**: {smell['description']}\n"
        
        # Improvements
        report += "\n## 🎯 Suggested Improvements\n"
        improvements_by_priority = defaultdict(list)
        for imp in self.analysis['improvements']:
            improvements_by_priority[imp['priority']].append(imp)
        
        for priority in ['high', 'medium', 'low', 'info']:
            if priority in improvements_by_priority:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢', 'info': 'ℹ️'}[priority]
                report += f"\n### {priority_emoji} {priority.capitalize()} Priority\n"
                for imp in improvements_by_priority[priority]:
                    report += f"\n**{imp['area']}**: {imp['description']}\n"
                    for action in imp['suggested_actions']:
                        report += f"- {action}\n"
        
        # Task suggestions
        report += "\n## 🤖 Suggested Agent Tasks\n"
        tasks_by_role = defaultdict(list)
        for task in self.analysis['suggested_tasks'][:15]:  # Show top 15 tasks
            tasks_by_role[task['suggested_agent_role']].append(task)
        
        for role, tasks in tasks_by_role.items():
            report += f"\n### {role}\n"
            for task in tasks:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[task['priority']]
                report += f"- {priority_emoji} {task['task']}\n"
                if task['dependencies']:
                    report += f"  - Dependencies: {', '.join(task['dependencies'])}\n"
        
        # Save report
        report_path = Path.cwd() / "project_analysis_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"📝 Report saved to: {report_path}")
        return report

def main():
    parser = argparse.ArgumentParser(
        description="Analyze existing project for multi-agent coordination"
    )
    parser.add_argument(
        "project_path",
        help="Path to the project to analyze"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path for analysis JSON",
        default=None
    )
    parser.add_argument(
        "-r", "--report",
        action="store_true",
        help="Generate human-readable report"
    )
    
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        return 1
    
    if not project_path.is_dir():
        print(f"❌ Error: Project path is not a directory: {project_path}")
        return 1
    
    # Run analysis
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.run_analysis()
    
    # Save results
    analyzer.save_analysis(args.output)
    
    # Generate report if requested
    if args.report:
        analyzer.generate_report()
    
    # Print summary
    print("\n✅ Analysis complete!")
    print(f"\n📊 Summary:")
    print(f"- Files analyzed: {analysis['project_info']['total_files']:,}")
    print(f"- Technologies found: {len(analysis['technologies']['languages'])} languages, {len(analysis['technologies']['frameworks'])} frameworks")
    print(f"- Improvement areas: {len(analysis['improvements'])}")
    print(f"- Suggested tasks: {len(analysis['suggested_tasks'])}")
    
    return 0

if __name__ == "__main__":
    exit(main())