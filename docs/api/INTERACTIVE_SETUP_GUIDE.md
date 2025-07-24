# Interactive Project Setup Guide

This guide covers the Interactive Project Setup system that provides guided project initialization using workflow templates and analysis.

## Overview

The interactive setup system helps developers:
- **Create new projects** with best practices and modern tooling
- **Enhance existing projects** with analysis-driven recommendations
- **Plan migrations** to modern architectures (microservices, cloud, etc.)
- **Generate tasks** automatically based on project analysis

## Features

### 🆕 New Project Creation
Create modern, well-structured projects with:
- **React Web Applications** - TypeScript, testing, deployment ready
- **Python API Services** - FastAPI with authentication, database, docs
- **Full-Stack Applications** - Integrated frontend/backend with shared auth
- **ML/Data Science Projects** - Jupyter, MLOps, data pipelines
- **Mobile Applications** - React Native with navigation and state management

### 🔧 Existing Project Enhancement
Analyze and improve existing projects with:
- **Analyze & Enhance** - Gap analysis and improvement recommendations
- **Migration Planning** - Modern architecture migration workflows
- **Add New Features** - Authentication, testing, CI/CD, monitoring

### 🤖 Intelligent Analysis
- Automatic project type detection (90%+ accuracy)
- Technology stack identification
- Code quality analysis and technical debt detection
- Migration readiness assessment
- Task generation based on best practices

## Quick Start

### Installation Requirements

```bash
# Install Python dependencies
pip install questionary rich click pathlib

# Optional: Install Node.js for React projects
# npm install -g create-react-app

# Optional: Install Docker for containerized projects
# docker --version
```

### Command Line Interface

```bash
# Interactive setup (recommended)
python coordination_system/cli.py setup

# Analyze existing project
python coordination_system/cli.py analyze .

# Generate tasks for project
python coordination_system/cli.py generate-tasks .

# Migration analysis
python coordination_system/cli.py migration . --workflow

# Smart project creation
python coordination_system/cli.py create-smart
```

### Direct Python Usage

```python
from coordination_system.interactive_setup import InteractiveSetup

# Launch interactive setup
setup = InteractiveSetup()
setup.run()
```

## Detailed Usage

### Creating a New React Project

1. **Launch Setup**:
   ```bash
   python coordination_system/cli.py setup
   ```

2. **Select "Create a new project"**

3. **Choose "React Web Application"**

4. **Provide Details**:
   - Project name: `my-awesome-app`
   - Description: `A modern React application`
   - Directory: `./my-awesome-app`
   - Initialize Git: `Yes`
   - Install dependencies: `Yes`

5. **Generated Structure**:
   ```
   my-awesome-app/
   ├── package.json          # Dependencies and scripts
   ├── tsconfig.json         # TypeScript configuration
   ├── src/
   │   ├── App.tsx          # Main app component
   │   ├── index.tsx        # Entry point
   │   ├── components/      # Reusable components
   │   ├── hooks/           # Custom hooks
   │   └── utils/           # Utility functions
   ├── public/
   │   └── index.html       # HTML template
   ├── PROJECT_TASKS.json   # Generated tasks
   └── .gitignore          # Git ignore rules
   ```

### Enhancing an Existing Project

1. **Launch Setup**:
   ```bash
   python coordination_system/cli.py setup
   ```

2. **Select "Enhance an existing project"**

3. **Provide Project Path**: `/path/to/your/project`

4. **View Analysis Results**:
   - Project type detection
   - Technology stack identification
   - Identified gaps and recommendations

5. **Choose Enhancement Type**:
   - **Analyze & Enhance**: General improvements
   - **Migration Planning**: Architecture modernization
   - **Add New Features**: Specific feature additions

6. **Review Generated Plan**:
   - Categorized tasks with time estimates
   - Priority levels and dependencies
   - Implementation recommendations

### Migration Planning

For legacy system modernization:

1. **Run Migration Analysis**:
   ```bash
   python coordination_system/cli.py migration /path/to/legacy/project --workflow
   ```

2. **Review Assessment**:
   - Migration readiness score (0-100)
   - Recommended migration type
   - Identified service boundaries
   - Blocking factors

3. **Generated Artifacts**:
   - **Migration workflow** with detailed phases
   - **Risk assessment** and mitigation strategies
   - **Service boundary analysis**
   - **Technical debt analysis**

## Project Templates

### React Web Application
- **TypeScript** configuration
- **ESLint & Prettier** for code quality
- **Testing** setup with Jest
- **Modern React** patterns (hooks, functional components)
- **Build optimization** configuration

### Python API Service  
- **FastAPI** framework
- **Pydantic** for data validation
- **SQLAlchemy** for database ORM
- **Alembic** for database migrations
- **JWT authentication** setup
- **Docker** containerization
- **OpenAPI** documentation

### ML/Data Science Project
- **Jupyter** notebook environment
- **DVC** for data version control
- **MLflow** for experiment tracking
- **Standard directory** structure (data/, models/, notebooks/)
- **Data pipeline** templates
- **Testing framework** for ML code

### Full-Stack Application
- **React frontend** with TypeScript
- **Python backend** with FastAPI
- **Shared authentication** system
- **Docker Compose** for development
- **API integration** setup
- **Proxy configuration** for development

## Customization

### Adding New Project Types

1. **Define Setup Choice**:
   ```python
   new_choice = SetupChoice(
       id="my_project_type",
       name="My Project Type",
       description="Description of the project type",
       category="Custom",
       templates=["template1", "template2"]
   )
   ```

2. **Add to Setup Choices**:
   ```python
   self.setup_choices["new_project"].append(new_choice)
   ```

3. **Implement Structure Creator**:
   ```python
   def _create_my_project_structure(self, project_path: Path, details: Dict[str, Any]):
       # Create files and directories
       (project_path / "custom_file.txt").write_text("Content")
   ```

### Custom Task Generation

Extend the `AutoTaskGenerator` to add custom task types:

```python
from coordination_system.auto_task_generator import AutoTaskGenerator

class CustomTaskGenerator(AutoTaskGenerator):
    def _generate_custom_tasks(self, project_path: str) -> List[GeneratedTask]:
        # Custom task generation logic
        return tasks
```

## Integration

### With Existing Workflows

The interactive setup integrates with:
- **Git workflows** - Automatic repository initialization
- **CI/CD pipelines** - Generated configuration files
- **Package managers** - Dependency installation
- **Development tools** - Linting, formatting, testing setup

### With IDE/Editors

Generated projects work out-of-the-box with:
- **VS Code** - Settings and extension recommendations
- **PyCharm** - Python project configuration
- **IntelliJ** - Java/JavaScript project setup

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   pip install questionary rich click
   ```

2. **Git Not Found**:
   - Install Git: https://git-scm.com/downloads
   - Or disable Git initialization in project setup

3. **Node.js Not Found** (for React projects):
   - Install Node.js: https://nodejs.org/
   - Or skip dependency installation

4. **Permission Errors**:
   ```bash
   # Run with appropriate permissions
   sudo python coordination_system/cli.py setup
   ```

### Debug Mode

Enable detailed error messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run setup with debug info
setup = InteractiveSetup()
setup.run()
```

## Best Practices

### Project Structure
- Follow established conventions for each project type
- Use consistent naming patterns
- Include comprehensive documentation
- Set up development tools early

### Task Management
- Review generated tasks before implementation
- Prioritize based on project needs
- Track progress using generated task files
- Update estimates based on actual time

### Migration Planning
- Start with readiness assessment
- Address blocking factors first
- Use gradual migration approaches (Strangler Fig)
- Maintain thorough testing throughout

## Examples

### Example 1: React E-commerce App

```bash
# Create project
python coordination_system/cli.py setup

# Select: Create new project > React Web Application
# Name: "react-ecommerce"
# Description: "Modern e-commerce application"

# Generated structure includes:
# - TypeScript configuration
# - Component architecture
# - State management setup
# - Testing framework
# - Build optimization
```

### Example 2: Legacy System Migration

```bash
# Analyze legacy system
python coordination_system/cli.py migration /path/to/legacy/system --workflow

# Results:
# - Readiness Score: 75/100
# - Recommended: Monolith to Microservices
# - Duration: 45 weeks
# - Identified 8 potential services
# - Generated detailed migration workflow
```

### Example 3: Python API Enhancement

```bash
# Enhance existing API
python coordination_system/cli.py setup

# Select: Enhance existing project > Add New Features
# Path: "/path/to/existing/api"

# Generated tasks:
# - Add authentication system
# - Implement API documentation
# - Set up monitoring
# - Add comprehensive testing
# - Configure CI/CD pipeline
```

## Contributing

To extend the interactive setup system:

1. **Add new project types** in `interactive_setup.py`
2. **Create structure generators** for new project types  
3. **Extend analysis capabilities** in `project_analyzer.py`
4. **Add custom workflows** in migration system
5. **Test thoroughly** with various project structures

## Support

For issues or questions:
- Check troubleshooting section above
- Review generated project documentation
- Examine task files for implementation guidance
- Test with sample projects first

The interactive setup system is designed to accelerate development by providing opinionated, best-practice project structures and intelligent analysis-driven recommendations.