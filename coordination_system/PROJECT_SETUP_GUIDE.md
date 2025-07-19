# 📚 Multi-Agent Coordination System - Project Setup Guide

## 🎯 Overview

This guide explains how to use the Multi-Agent Coordination System as a template for any software development project. The system orchestrates multiple AI agents working collaboratively with automatic lifecycle management, dependency tracking, and real-time monitoring.

The framework supports both:
- **New Projects**: Starting from scratch with coordinated development
- **Existing Projects**: Analyzing and improving existing codebases

## 🚀 Quick Start

### For New Projects

### 1. Initialize a New Project

```bash
# Basic initialization
python3 coordination_system/init_new_project.py "My Awesome Project"

# With description and deadline
python3 coordination_system/init_new_project.py "E-commerce Platform" \
  -d "Building a scalable online marketplace" \
  --deadline "2025-12-31"
```

### 2. Configure Theme and Agent Count (Optional)

```bash
# View available themes
./manage_agents.sh themes

# Change theme (e.g., to Marvel superheroes)
./manage_agents.sh set-theme marvel

# Set number of agents (1-24)
./manage_agents.sh set-count 8

# Generate agent files for new configuration
./generate_agents.sh
```

### 3. Start the System

```bash
# Terminal 1: Start automatic lifecycle management
./manage_agents.sh auto

# Terminal 2: Start monitoring dashboard
./coordination_manager.sh watch
```

### For Existing Projects

### 1. Analyze the Existing Codebase

```bash
# Analyze a project (generates project_analysis.json and report)
python3 coordination_system/analyze_existing_project.py /path/to/your/project -r

# Example
python3 coordination_system/analyze_existing_project.py ~/projects/my-web-app -r
```

This generates:
- `project_analysis.json`: Detailed analysis data
- `project_analysis_report.md`: Human-readable report

### 2. Review the Analysis Report

The report includes:
- Technology stack detection
- Code quality metrics
- Identified improvement areas
- Suggested tasks for agents
- Priority recommendations

### 3. Initialize Coordination from Analysis

```bash
# Initialize using the analysis
python3 coordination_system/init_existing_project.py project_analysis.json

# With custom name and deadline
python3 coordination_system/init_existing_project.py project_analysis.json \
  -n "My Web App v2.0" \
  --deadline "2025-06-30"
```

### 4. Start the System

```bash
# Same as new projects
./manage_agents.sh auto
./coordination_manager.sh watch
```

## 📋 Project Workflow

### Step 1: Define Tasks

Break your project into parallel tasks. Each agent can handle:
- Frontend development
- Backend services
- Database design
- API development
- Testing & QA
- DevOps & deployment
- Security implementation
- Documentation

### Step 2: Assign Tasks to Agents

```bash
# Update agent with a task
./coordination_manager.sh update alpha \
  --task "Design and implement user authentication system" \
  --progress 0

# Add dependencies
python3 coordination_system/update_agent_status.py beta \
  --task "Create user dashboard" \
  --add-dependency "alpha"
```

### Step 3: Agents Work Automatically

- Agents start when dependencies are met
- Agents pause when blocked
- Agents restart when blockers are resolved
- Progress updates happen in real-time

### Step 4: Monitor Progress

The watch dashboard shows:
- Current agent status (🔵 Ready, 🟡 In Progress, 🟢 Completed, 🔴 Blocked)
- Task progress percentages
- Dependencies and blockers
- Recent activities
- Overall project progress

## 🛠️ Common Operations

### Managing Agent Tasks

```bash
# Update progress
./coordination_manager.sh update gamma --progress 75

# Add an activity log
python3 coordination_system/update_agent_status.py gamma \
  --add-activity "Completed database schema design"

# Report a blocker
python3 coordination_system/update_agent_status.py delta \
  --add-blocker "Waiting for API specifications from Alpha"

# Resolve a blocker
python3 coordination_system/update_agent_status.py delta \
  --resolve-blocker "Waiting for API specifications from Alpha"
```

### Inter-Agent Communication

Agents communicate asynchronously through message channels:

```bash
# Send a message from one agent to another
echo '{"from": "alpha", "to": "beta", "message": "API endpoints ready"}' \
  > agent_communication/beta/input/inbox.json
```

### Viewing Status

```bash
# Show all agent statuses
./coordination_manager.sh show-all

# View specific agent details
cat agent_status/alpha_status.json | jq .

# Check lifecycle daemon status
./manage_agents.sh lifecycle status
```

## 📁 Project Structure

```
your_project/
├── coordination_system/        # Core framework files
│   ├── init_new_project.py    # Project initialization
│   ├── clean_coordination.py  # Reset to template state
│   └── update_agent_status.py # Status management
├── agent_status/              # Individual agent JSON files
├── agent_communication/       # Message channels
├── AGENT_COORDINATION.md      # Human-readable status
├── AGENT_COORDINATION_MASTER.json  # Machine-readable status
└── AGENT_*_PROMPT.md         # Agent instructions
```

## 🎨 Customization

### Agent Roles

The system cycles through 6 standard roles:
1. **Critical Path Lead** - Senior Developer
2. **Migration Specialist** - Backend Developer
3. **Dashboard Developer** - Fullstack Developer
4. **DevOps Engineer**
5. **Security Engineer**
6. **UX Engineer** - Frontend Developer

### Available Themes

- `greek_letters`: Alpha, Beta, Gamma... (Α, Β, Γ...)
- `nato_phonetic`: Alpha, Bravo, Charlie... (🅰️, 🅱️, ©️...)
- `marvel`: Iron Man, Captain America... (🤖, 🛡️, ⚡...)
- `greek_mythology`: Zeus, Athena... (⚡, 🦉, 🔱...)
- `vegetables`: Carrot, Broccoli... (🥕, 🥦, 🥬...)
- `programming_languages`: Python, JavaScript... (🐍, 📜, ☕...)
- And more! Run `./manage_agents.sh themes` to see all 11 themes.

## ⚡ Best Practices

1. **Start Small**: Begin with 4-6 agents for most projects
2. **Clear Dependencies**: Define task dependencies upfront
3. **Regular Updates**: Keep agent progress updated for accurate tracking
4. **Use Blockers**: Report blockers immediately to pause blocked agents
5. **Modular Tasks**: Break work into independent, parallel tasks
6. **Review Dashboard**: Check the monitoring dashboard regularly

## 🔧 Troubleshooting

### Agent Won't Start
- Check dependencies are met
- Ensure no active blockers
- Verify lifecycle daemon is running

### Communication Issues
- Check message format in inbox.json
- Ensure agent names match configuration
- Verify file permissions

### Reset Everything
```bash
# Clean all project data
python3 coordination_system/clean_coordination.py

# Or manually
./manage_agents.sh lifecycle stop
rm -rf agent_communication/
python3 coordination_system/clean_coordination.py
```

## 🚦 Example: Starting a Web App Project

```bash
# 1. Initialize project
python3 coordination_system/init_new_project.py "SaaS Dashboard" \
  -d "Multi-tenant analytics platform" \
  --deadline "2025-06-30"

# 2. Assign initial tasks
./coordination_manager.sh update alpha --task "Design database schema"
./coordination_manager.sh update beta --task "Create REST API framework"
./coordination_manager.sh update gamma --task "Build React component library"

# 3. Set dependencies
python3 coordination_system/update_agent_status.py beta \
  --add-dependency "alpha"

# 4. Start the system
./manage_agents.sh auto

# 5. Monitor progress
./coordination_manager.sh watch
```

## 🔧 Example: Improving an Existing Project

```bash
# 1. Analyze the existing codebase
python3 coordination_system/analyze_existing_project.py ~/projects/legacy-app -r

# 2. Review the generated report
cat project_analysis_report.md

# 3. Initialize with the analysis
python3 coordination_system/init_existing_project.py project_analysis.json \
  -n "Legacy App Modernization"

# 4. Agents are automatically assigned tasks based on analysis:
#    - Alpha: Set up testing framework (HIGH priority)
#    - Beta: Implement CI/CD pipeline (HIGH priority)
#    - Gamma: Refactor large files (MEDIUM priority)
#    - Delta: Add API documentation (MEDIUM priority)
#    - Epsilon: Conduct security audit (HIGH priority)
#    - Zeta: Implement responsive design (LOW priority)

# 5. Start the system
./manage_agents.sh auto

# 6. Monitor progress
./coordination_manager.sh watch
```

## 📊 Understanding Project Analysis

The analysis tool examines:

### Technology Detection
- Programming languages (by file extensions)
- Frameworks (from package files)
- Databases (from dependencies)
- Build tools and package managers

### Code Quality Metrics
- Test coverage presence
- CI/CD configuration
- Linting setup
- Documentation status
- Type checking

### Improvement Suggestions
- **High Priority**: Critical issues (no tests, no CI, security concerns)
- **Medium Priority**: Quality improvements (linting, documentation)
- **Low Priority**: Nice-to-haves (containerization, optimizations)

### Automatic Task Assignment
Based on the analysis, agents are assigned tasks matching their roles:
- **Critical Path Lead**: Core functionality, testing
- **Migration Specialist**: Backend improvements, database optimization
- **Dashboard Developer**: Full-stack features
- **DevOps Engineer**: CI/CD, containerization
- **Security Engineer**: Security audits, authentication
- **UX Engineer**: Frontend improvements, responsive design

## 📞 Getting Help

- Check `CLAUDE.md` for detailed command reference
- Review agent logs in `coordination_system/logs/`
- Examine `lifecycle_daemon.log` for automation issues
- Each agent's prompt file contains their specific instructions

---

Remember: This framework handles the orchestration - you just need to define the tasks and dependencies!