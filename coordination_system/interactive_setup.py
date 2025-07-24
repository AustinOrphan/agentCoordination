#!/usr/bin/env python3
"""
Interactive Project Setup CLI
Provides guided project initialization using workflow templates and analysis
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.markdown import Markdown

from .project_analyzer import ProjectAnalyzer, ProjectType
from .auto_task_generator import AutoTaskGenerator
from .migration_analyzer import MigrationAnalyzer
from .migration_workflows import MigrationWorkflowGenerator


@dataclass
class SetupChoice:
    """Represents a setup choice option"""

    id: str
    name: str
    description: str
    category: str
    templates: List[str]


class InteractiveSetup:
    """Interactive CLI for guided project setup"""

    def __init__(self):
        self.console = Console()
        self.analyzer = ProjectAnalyzer()
        self.task_generator = AutoTaskGenerator()
        self.migration_analyzer = MigrationAnalyzer()
        self.migration_workflows = MigrationWorkflowGenerator()

        # Setup choices for different project types
        self.setup_choices = {
            "new_project": [
                SetupChoice(
                    id="react_webapp",
                    name="React Web Application",
                    description="Modern React SPA with TypeScript, testing, and deployment",
                    category="Frontend",
                    templates=[
                        "react-typescript",
                        "testing-setup",
                        "deployment-vercel",
                    ],
                ),
                SetupChoice(
                    id="python_api",
                    name="Python API Service",
                    description="FastAPI service with database, authentication, and docs",
                    category="Backend",
                    templates=[
                        "fastapi-service",
                        "database-setup",
                        "auth-jwt",
                        "api-docs",
                    ],
                ),
                SetupChoice(
                    id="fullstack_app",
                    name="Full-Stack Application",
                    description="React frontend + Python backend with shared authentication",
                    category="Full-Stack",
                    templates=[
                        "react-frontend",
                        "python-backend",
                        "shared-auth",
                        "docker-compose",
                    ],
                ),
                SetupChoice(
                    id="ml_project",
                    name="ML/Data Science Project",
                    description="Python ML project with notebooks, data pipeline, and MLOps",
                    category="ML/AI",
                    templates=[
                        "ml-structure",
                        "jupyter-setup",
                        "data-pipeline",
                        "mlops",
                    ],
                ),
                SetupChoice(
                    id="mobile_app",
                    name="Mobile Application",
                    description="React Native app with navigation, state management, and testing",
                    category="Mobile",
                    templates=[
                        "react-native",
                        "navigation",
                        "state-management",
                        "mobile-testing",
                    ],
                ),
            ],
            "existing_project": [
                SetupChoice(
                    id="analyze_enhance",
                    name="Analyze & Enhance",
                    description="Analyze existing project and suggest improvements",
                    category="Enhancement",
                    templates=["analysis", "gap-filling", "best-practices"],
                ),
                SetupChoice(
                    id="migration_planning",
                    name="Migration Planning",
                    description="Plan migration to modern architecture (microservices, cloud, etc.)",
                    category="Migration",
                    templates=[
                        "migration-analysis",
                        "modernization-plan",
                        "risk-assessment",
                    ],
                ),
                SetupChoice(
                    id="add_features",
                    name="Add New Features",
                    description="Add authentication, testing, CI/CD, monitoring, etc.",
                    category="Feature Addition",
                    templates=[
                        "feature-analysis",
                        "integration-planning",
                        "testing-strategy",
                    ],
                ),
            ],
        }

    def run(self):
        """Main entry point for interactive setup"""
        self.console.print(
            Panel.fit(
                "[bold blue]🚀 Interactive Project Setup[/bold blue]\n"
                "Let's get your project set up with best practices and workflows!",
                style="blue",
            )
        )

        try:
            # Step 1: Determine setup type
            setup_type = self._choose_setup_type()

            if setup_type == "new_project":
                self._handle_new_project()
            elif setup_type == "existing_project":
                self._handle_existing_project()
            else:
                self.console.print("❌ Invalid choice. Exiting.")
                return

        except KeyboardInterrupt:
            self.console.print("\n\n👋 Setup cancelled by user.")
        except Exception as e:
            self.console.print(f"\n❌ Error during setup: {e}")
            raise

    def _choose_setup_type(self) -> str:
        """Choose between new project or existing project setup"""
        return questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("🆕 Create a new project", "new_project"),
                questionary.Choice(
                    "🔧 Enhance an existing project", "existing_project"
                ),
                questionary.Choice("❌ Exit", "exit"),
            ],
        ).ask()

    def _handle_new_project(self):
        """Handle new project creation workflow"""
        self.console.print("\n[bold green]Creating New Project[/bold green]")

        # Choose project type
        project_choice = self._choose_project_type("new_project")
        if not project_choice:
            return

        # Get project details
        project_details = self._get_new_project_details()

        # Create project structure
        self._create_new_project(project_choice, project_details)

    def _handle_existing_project(self):
        """Handle existing project enhancement workflow"""
        self.console.print("\n[bold yellow]Enhancing Existing Project[/bold yellow]")

        # Get project path
        project_path = self._get_project_path()
        if not project_path:
            return

        # Analyze project
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Analyzing project...", total=None)
            analysis_result = self.analyzer.analyze_project(project_path)
            progress.update(task, description="Analysis complete!")

        # Display analysis results
        self._display_analysis_results(analysis_result)

        # Choose enhancement type
        enhancement_choice = self._choose_project_type("existing_project")
        if not enhancement_choice:
            return

        # Generate enhancement plan
        self._create_enhancement_plan(project_path, analysis_result, enhancement_choice)

    def _choose_project_type(self, category: str) -> Optional[SetupChoice]:
        """Choose specific project type from category"""
        choices = self.setup_choices[category]

        # Create questionary choices with rich descriptions
        questionary_choices = []
        for choice in choices:
            questionary_choices.append(
                questionary.Choice(
                    title=f"{choice.name} - {choice.description}", value=choice
                )
            )

        return questionary.select(
            f"Choose your {'project type' if category == 'new_project' else 'enhancement type'}:",
            choices=questionary_choices,
        ).ask()

    def _get_new_project_details(self) -> Dict[str, Any]:
        """Collect details for new project creation"""
        details = {}

        details["name"] = questionary.text(
            "Project name:",
            validate=lambda text: len(text) > 0 or "Project name cannot be empty",
        ).ask()

        details["description"] = (
            questionary.text("Project description (optional):").ask()
            or f"A new {details['name']} project"
        )

        details["directory"] = questionary.path(
            "Project directory:",
            default=f"./{details['name'].lower().replace(' ', '-')}",
        ).ask()

        details["git_init"] = questionary.confirm(
            "Initialize Git repository?", default=True
        ).ask()

        details["install_deps"] = questionary.confirm(
            "Install dependencies after setup?", default=True
        ).ask()

        return details

    def _get_project_path(self) -> Optional[str]:
        """Get path to existing project"""
        path = questionary.path(
            "Path to your existing project:", default=".", only_directories=True
        ).ask()

        if not path or not os.path.exists(path):
            self.console.print("❌ Invalid path. Please try again.")
            return None

        return path

    def _display_analysis_results(self, analysis_result):
        """Display project analysis results in a nice format"""
        self.console.print("\n[bold cyan]📊 Project Analysis Results[/bold cyan]")

        # Main details table
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="bold")
        table.add_column("Value")

        table.add_row("Project Type", str(analysis_result.project_type).split(".")[-1])
        table.add_row("Confidence", f"{analysis_result.confidence:.2f}")
        table.add_row("Complexity", analysis_result.estimated_complexity)
        table.add_row("Team Size", str(analysis_result.team_size_recommendation))

        self.console.print(table)

        # Technology stack
        if analysis_result.tech_stack:
            self.console.print("\n[bold cyan]🛠️ Technology Stack[/bold cyan]")

            tech_tree = Tree("Technologies")

            if analysis_result.tech_stack.languages:
                lang_branch = tech_tree.add("Languages")
                for lang in analysis_result.tech_stack.languages:
                    lang_branch.add(lang)

            if analysis_result.tech_stack.frameworks:
                fw_branch = tech_tree.add("Frameworks")
                for fw in analysis_result.tech_stack.frameworks:
                    fw_branch.add(fw)

            if analysis_result.tech_stack.databases:
                db_branch = tech_tree.add("Databases")
                for db in analysis_result.tech_stack.databases:
                    db_branch.add(db)

            if analysis_result.tech_stack.build_tools:
                build_branch = tech_tree.add("Build Tools")
                for tool in analysis_result.tech_stack.build_tools:
                    build_branch.add(tool)

            self.console.print(tech_tree)

        # Gaps and recommendations
        if (
            hasattr(analysis_result, "gaps_identified")
            and analysis_result.gaps_identified
        ):
            self.console.print("\n[bold red]⚠️ Identified Gaps[/bold red]")
            for gap in analysis_result.gaps_identified[:5]:  # Show top 5
                self.console.print(f"• {gap}")

    def _create_new_project(self, choice: SetupChoice, details: Dict[str, Any]):
        """Create new project structure based on choice"""
        self.console.print(f"\n[bold green]🏗️ Creating {choice.name}[/bold green]")

        project_path = Path(details["directory"])

        try:
            # Create directory
            project_path.mkdir(parents=True, exist_ok=True)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:

                # Step 1: Create basic structure
                task = progress.add_task("Creating project structure...", total=None)
                self._create_project_structure(choice, project_path, details)

                # Step 2: Initialize Git
                if details["git_init"]:
                    progress.update(task, description="Initializing Git repository...")
                    self._init_git_repo(project_path)

                # Step 3: Generate tasks and documentation
                progress.update(task, description="Generating project tasks...")
                self._generate_project_tasks(project_path, choice)

                # Step 4: Install dependencies
                if details["install_deps"]:
                    progress.update(task, description="Installing dependencies...")
                    self._install_dependencies(project_path, choice)

                progress.update(task, description="Project created successfully!")

            # Display success message with next steps
            self._display_project_success(project_path, choice)

        except Exception as e:
            self.console.print(f"❌ Error creating project: {e}")
            raise

    def _create_enhancement_plan(
        self, project_path: str, analysis_result, choice: SetupChoice
    ):
        """Create enhancement plan for existing project"""
        self.console.print(f"\n[bold yellow]📋 Creating Enhancement Plan[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:

            if choice.id == "migration_planning":
                # Migration analysis
                task = progress.add_task(
                    "Analyzing migration opportunities...", total=None
                )
                migration_assessment = (
                    self.migration_analyzer.analyze_migration_opportunities(
                        project_path
                    )
                )

                progress.update(task, description="Generating migration workflows...")
                workflows = self.migration_workflows.generate_workflow(
                    migration_assessment
                )

                self._display_migration_plan(migration_assessment, workflows)

            else:
                # General enhancement
                task = progress.add_task("Generating enhancement tasks...", total=None)
                tasks, report = self.task_generator.generate_tasks_from_project(
                    project_path
                )

                progress.update(task, description="Creating enhancement plan...")
                self._display_enhancement_plan(tasks, analysis_result)

        # Ask if user wants to proceed
        if questionary.confirm(
            "Would you like to save this plan and create tasks?"
        ).ask():
            self._save_enhancement_plan(project_path, choice)

    def _create_project_structure(
        self, choice: SetupChoice, project_path: Path, details: Dict[str, Any]
    ):
        """Create the actual project files and structure"""

        if choice.id == "react_webapp":
            self._create_react_structure(project_path, details)
        elif choice.id == "python_api":
            self._create_python_api_structure(project_path, details)
        elif choice.id == "fullstack_app":
            self._create_fullstack_structure(project_path, details)
        elif choice.id == "ml_project":
            self._create_ml_structure(project_path, details)
        elif choice.id == "mobile_app":
            self._create_mobile_structure(project_path, details)

    def _create_react_structure(self, project_path: Path, details: Dict[str, Any]):
        """Create React project structure"""
        # Package.json
        package_json = {
            "name": details["name"].lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "typescript": "^4.9.5",
                "@types/react": "^18.0.37",
                "@types/react-dom": "^18.0.11",
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject",
                "lint": "eslint src --ext .ts,.tsx",
                "format": "prettier --write src/**/*.{ts,tsx}",
            },
            "devDependencies": {
                "@typescript-eslint/eslint-plugin": "^5.57.1",
                "@typescript-eslint/parser": "^5.57.1",
                "eslint": "^8.38.0",
                "prettier": "^2.8.7",
            },
        }

        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))

        # TypeScript config
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "noFallthroughCasesInSwitch": True,
                "module": "esnext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
            },
            "include": ["src"],
        }

        (project_path / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

        # Create directories
        (project_path / "public").mkdir()
        (project_path / "src").mkdir()
        (project_path / "src" / "components").mkdir()
        (project_path / "src" / "hooks").mkdir()
        (project_path / "src" / "utils").mkdir()

        # Public files
        (project_path / "public" / "index.html").write_text(
            f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{details['description']}" />
    <title>{details['name']}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>"""
        )

        # Source files
        (project_path / "src" / "index.tsx").write_text(
            """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
        )

        (project_path / "src" / "App.tsx").write_text(
            f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{details['name']}</h1>
        <p>{details['description']}</p>
      </header>
    </div>
  );
}}

export default App;"""
        )

        (project_path / "src" / "App.css").write_text(
            """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}"""
        )

        (project_path / "src" / "index.css").write_text(
            """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}"""
        )

    def _create_python_api_structure(self, project_path: Path, details: Dict[str, Any]):
        """Create Python API project structure"""
        # Requirements.txt
        (project_path / "requirements.txt").write_text(
            """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
python-dotenv==1.0.0"""
        )

        # Create directories
        (project_path / "app").mkdir()
        (project_path / "app" / "api").mkdir()
        (project_path / "app" / "models").mkdir()
        (project_path / "app" / "schemas").mkdir()
        (project_path / "app" / "services").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "alembic").mkdir()

        # Main application
        (project_path / "app" / "__init__.py").write_text("")
        (project_path / "app" / "main.py").write_text(
            f'''"""
{details['name']} - FastAPI Application
{details['description']}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{details['name']}",
    description="{details['description']}",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "Welcome to {details['name']}"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)'''
        )

        # Configuration
        (project_path / "app" / "config.py").write_text(
            """import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    debug: bool = False
    database_url: Optional[str] = None
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()"""
        )

        # Environment file
        (project_path / ".env.example").write_text(
            """# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True"""
        )

        # Docker files
        (project_path / "Dockerfile").write_text(
            f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]"""
        )

        (project_path / "docker-compose.yml").write_text(
            f"""version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
    depends_on:
      - db
    volumes:
      - .:/app
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:"""
        )

    def _create_ml_structure(self, project_path: Path, details: Dict[str, Any]):
        """Create ML project structure"""
        # Requirements
        (project_path / "requirements.txt").write_text(
            """numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
jupyter==1.0.0
jupyterlab==4.0.5
mlflow==2.6.0
dvc==3.15.2
pytest==7.4.0
black==23.7.0
flake8==6.0.0"""
        )

        # Create directories
        directories = [
            "data/raw",
            "data/processed",
            "data/external",
            "notebooks/exploratory",
            "notebooks/modeling",
            "src/data",
            "src/features",
            "src/models",
            "src/visualization",
            "models",
            "reports/figures",
            "tests",
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True)

        # Configuration files
        (project_path / "setup.py").write_text(
            f"""from setuptools import find_packages, setup

setup(
    name="{details['name'].lower().replace(' ', '_')}",
    packages=find_packages(),
    version="0.1.0",
    description="{details['description']}",
    author="Your Name",
    license="MIT",
)"""
        )

        # DVC config
        (project_path / "dvc.yaml").write_text(
            """stages:
  data_preparation:
    cmd: python src/data/make_dataset.py
    deps:
    - data/raw
    outs:
    - data/processed
  
  train:
    cmd: python src/models/train_model.py
    deps:
    - data/processed
    - src/models/train_model.py
    outs:
    - models/model.pkl
    metrics:
    - metrics.json
"""
        )

        # Sample Python modules
        (project_path / "src" / "__init__.py").write_text("")
        (project_path / "src" / "data" / "__init__.py").write_text("")
        (project_path / "src" / "data" / "make_dataset.py").write_text(
            f'''"""
Data processing pipeline for {details['name']}
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_raw_data(input_path: str) -> pd.DataFrame:
    """Load raw data from input path"""
    # Implement your data loading logic here
    pass


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess the data"""
    # Implement your data cleaning logic here
    return df


def main():
    """Main data processing pipeline"""
    input_path = "data/raw"
    output_path = "data/processed"
    
    # Create output directory
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    print("Data processing completed!")


if __name__ == "__main__":
    main()'''
        )

    def _init_git_repo(self, project_path: Path):
        """Initialize Git repository"""
        try:
            subprocess.run(
                ["git", "init"], cwd=project_path, check=True, capture_output=True
            )

            # Create .gitignore
            gitignore_content = self._get_gitignore_content()
            (project_path / ".gitignore").write_text(gitignore_content)

            # Initial commit
            subprocess.run(
                ["git", "add", "."], cwd=project_path, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            self.console.print("⚠️ Git initialization failed (git may not be installed)")

    def _get_gitignore_content(self) -> str:
        """Get appropriate .gitignore content"""
        return """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment
.env
.env.local
.env.production
.venv/
venv/

# Build outputs
dist/
build/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# ML specific
models/*.pkl
data/raw/*
!data/raw/.gitkeep
.mlflow/

# Jupyter
.ipynb_checkpoints/
"""

    def _generate_project_tasks(self, project_path: Path, choice: SetupChoice):
        """Generate initial project tasks"""
        try:
            tasks = self.task_generator.generate_tasks_from_project(str(project_path))

            # Save tasks to file
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

            with open(project_path / "PROJECT_TASKS.json", "w") as f:
                json.dump(tasks_data, f, indent=2)

        except Exception as e:
            self.console.print(f"⚠️ Could not generate tasks: {e}")

    def _install_dependencies(self, project_path: Path, choice: SetupChoice):
        """Install project dependencies"""
        try:
            if (project_path / "package.json").exists():
                subprocess.run(
                    ["npm", "install"],
                    cwd=project_path,
                    check=True,
                    capture_output=True,
                )
            elif (project_path / "requirements.txt").exists():
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    cwd=project_path,
                    check=True,
                    capture_output=True,
                )
        except subprocess.CalledProcessError:
            self.console.print(
                "⚠️ Dependency installation failed - you may need to install them manually"
            )

    def _display_project_success(self, project_path: Path, choice: SetupChoice):
        """Display success message with next steps"""
        self.console.print(
            Panel.fit(
                f"[bold green]✅ Project Created Successfully![/bold green]\n\n"
                f"📁 Location: {project_path.absolute()}\n"
                f"🎯 Type: {choice.name}\n\n"
                f"[bold cyan]Next Steps:[/bold cyan]\n"
                f"1. cd {project_path.name}\n"
                f"2. Review PROJECT_TASKS.json for recommended tasks\n"
                f"3. Check README.md for setup instructions\n"
                f"4. Start development! 🚀",
                style="green",
            )
        )

    def _display_migration_plan(self, assessment, workflows):
        """Display migration assessment and plan"""
        self.console.print("\n[bold cyan]🔄 Migration Analysis[/bold cyan]")

        # Display readiness score
        table = Table(show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Score")

        table.add_row("Migration Readiness", f"{assessment.readiness_score}/100")
        table.add_row("Recommended Migration", assessment.recommended_migration_type)
        table.add_row(
            "Estimated Duration", f"{assessment.estimated_duration_weeks} weeks"
        )

        self.console.print(table)

        # Display identified services
        if assessment.identified_services:
            self.console.print("\n[bold cyan]🎯 Identified Services[/bold cyan]")
            for service in assessment.identified_services[:5]:
                self.console.print(f"• {service.name} - {service.description}")

    def _display_enhancement_plan(self, tasks, analysis_result):
        """Display enhancement plan with generated tasks"""
        self.console.print("\n[bold cyan]📋 Enhancement Plan[/bold cyan]")

        # Group tasks by category
        task_categories = {}
        for task in tasks:
            if task.category not in task_categories:
                task_categories[task.category] = []
            task_categories[task.category].append(task)

        # Display tasks by category
        for category, category_tasks in task_categories.items():
            self.console.print(f"\n[bold yellow]{category}[/bold yellow]")
            for task in category_tasks[:3]:  # Show top 3 per category
                self.console.print(f"• {task.title} ({task.estimated_hours}h)")

    def _save_enhancement_plan(self, project_path: str, choice: SetupChoice):
        """Save enhancement plan to project"""
        # Generate and save tasks
        tasks, report = self.task_generator.generate_tasks_from_project(project_path)

        plan_data = {
            "enhancement_type": choice.name,
            "created_at": "now",
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "category": task.category,
                    "priority": task.priority,
                    "estimated_hours": task.estimated_hours,
                }
                for task in tasks
            ],
        }

        plan_path = Path(project_path) / "ENHANCEMENT_PLAN.json"
        with open(plan_path, "w") as f:
            json.dump(plan_data, f, indent=2)

        self.console.print(f"\n✅ Enhancement plan saved to {plan_path}")


def main():
    """CLI entry point"""
    setup = InteractiveSetup()
    setup.run()


if __name__ == "__main__":
    main()
