# Getting Started with Multi-Agent Coordination System

This guide will help you integrate the Multi-Agent Coordination System into your existing project.

## Prerequisites

- Python 3.8 or higher
- Git (for worktree functionality)
- Claude CLI installed (`claude` command available)
- Unix-like environment (macOS, Linux, WSL)

## Quick Start (5 minutes)

### 1. Clone the Coordination System

```bash
# Clone to a tools directory in your project
cd /path/to/your/project
git clone <coordination-system-repo> tools/agent-coordination

# Or copy the files if not using git
cp -r /path/to/agentCoordination tools/agent-coordination
```

### 2. Install Dependencies

```bash
cd tools/agent-coordination
pip install -r requirements.txt
```

### 3. Initialize the System

```bash
# Run the initialization
./coordination_manager.sh init

# Set your preferred theme (optional)
./manage_agents.sh set-theme marvel  # or greek_letters, ocean_creatures, etc.

# Set number of agents (default is 6)
./manage_agents.sh set-count 4  # Start with fewer agents for testing

# Generate agent files
./generate_agents.sh
```

### 4. Create Your First Project

```bash
# Create a project pointing to your code
./project_manager.sh create "My Project" /path/to/your/project/src \
    --description "Main development project" \
    --agents 4
```

### 5. Start the Agents

```bash
# Start automatic agent management
./manage_agents.sh auto

# Or start specific agents manually
./manage_agents.sh start ironman
./manage_agents.sh start captainamerica
```

## Integration Guide

### Option 1: Standalone Tool (Recommended for First Use)

Keep the coordination system as a separate tool:

```bash
your-project/
├── src/                 # Your project code
├── tests/
├── docs/
└── tools/
    └── agent-coordination/  # Multi-agent system
```

**Advantages:**
- No interference with your project structure
- Easy to update or remove
- Can be shared across multiple projects

### Option 2: Integrated Deployment

Integrate directly into your project:

```bash
your-project/
├── src/                    # Your project code
├── tests/
├── agent_coordination/     # Coordination scripts
├── agent_status/          # Agent status tracking
└── coordination_system/   # Core coordination code
```

**Steps:**
1. Copy core directories to your project root
2. Update paths in scripts if needed
3. Add to your project's `.gitignore`:
   ```
   agent_status/*.json
   agent_communication/
   runtime/
   *.log
   *.pid
   __pycache__/
   .coverage
   ```

## Workflow Examples

### Example 1: Code Review and Refactoring

```bash
# Create a refactoring project
./project_manager.sh create "Refactoring Sprint" ./src \
    --description "Refactor authentication module" \
    --agents 3

# Assign specific tasks
./coordination_system/task_communicator.py \
    --task "Review auth module for security issues" \
    --priority high \
    --assign-to ironman

./coordination_system/task_communicator.py \
    --task "Refactor database connections to use connection pooling" \
    --priority medium \
    --assign-to captainamerica

# Monitor progress
./coordination_manager.sh watch
```

### Example 2: Feature Development

```bash
# Set up for feature development
./manage_agents.sh set-theme programming_languages
./manage_agents.sh set-count 6
./generate_agents.sh

# Create feature branch worktrees
./worktree_manager.sh create python feature/user-dashboard
./worktree_manager.sh create javascript feature/user-dashboard-ui

# Start agents with specific prompts
cat > CUSTOM_TASK.md << EOF
# User Dashboard Feature

## Backend Tasks (Python Agent)
- Design REST API endpoints for dashboard data
- Implement data aggregation service
- Add caching layer for performance

## Frontend Tasks (JavaScript Agent)
- Create React components for dashboard
- Implement real-time data updates
- Add responsive design
EOF

# Launch agents with custom task
./start_agent_python.sh  # Will read the custom task
```

### Example 3: Migration Analysis

```bash
# Analyze your project for migration opportunities
cd tools/agent-coordination
python3 coordination_system/migration_cli.py analyze /path/to/your/project

# Generate a migration workflow
python3 coordination_system/migration_cli.py workflow \
    --type monolith_to_microservices \
    --complexity medium \
    --output migration-plan.json

# Create migration project
./project_manager.sh import migration-plan.json
```

## Configuration Tips

### 1. Customize Agent Roles

Edit `agent_config.json` to match your team structure:

```json
{
  "current_theme": "custom_roles",
  "themes": {
    "custom_roles": {
      "agents": ["backend_lead", "frontend_dev", "qa_engineer", "devops"]
    }
  }
}
```

### 2. Set Up Agent Specializations

```python
# Configure agent expertise
python3 coordination_system/configure_specializations.py \
    --agent backend_lead --specialization "python,django,postgresql" \
    --agent frontend_dev --specialization "react,typescript,css"
```

### 3. Create Project Templates

Save common project configurations:

```bash
# Export current project as template
./project_manager.sh export "My Project" > templates/web-app-template.json

# Use template for new projects
./project_manager.sh import templates/web-app-template.json \
    --name "New Web App"
```

## Best Practices

### 1. Start Small
- Begin with 2-3 agents to understand the workflow
- Use simple themes like `greek_letters` initially
- Focus on one project at a time

### 2. Use Git Worktrees
- Enable parallel development without conflicts
- Each agent works in isolated branch
- Merge changes through pull requests

### 3. Monitor and Adjust
- Watch agent performance: `./coordination_manager.sh watch`
- Check logs for issues: `tail -f logs/*.log`
- Adjust agent count based on workload

### 4. Leverage Authority System
- Agents automatically handle decision-making
- Emergency protocols for critical issues
- Load balancing prevents bottlenecks

## Common Use Cases

### 1. Large Refactoring Projects
```bash
# Distribute refactoring tasks across agents
# Each agent handles specific modules
# Coordination prevents conflicts
```

### 2. Multi-Service Development
```bash
# Assign agents to different services
# Automatic dependency management
# Synchronized deployments
```

### 3. Code Analysis and Documentation
```bash
# Agents analyze different aspects
# Generate comprehensive reports
# Update documentation in parallel
```

### 4. Testing and QA
```bash
# Distribute test writing across agents
# Parallel test execution
# Automated bug assignment
```

## Troubleshooting

### Agents Not Starting
```bash
# Check daemon status
./lifecycle_daemon.sh status

# View logs
tail -20 lifecycle_daemon.log

# Restart daemon
./lifecycle_daemon.sh restart
```

### Communication Issues
```bash
# Check agent communication
ls -la agent_communication/*/inbox/

# Clear stale messages
./coordination_system/clear_communication.py --stale
```

### Performance Problems
```bash
# Reduce agent count
./manage_agents.sh set-count 3

# Check resource usage
./coordination_system/monitor_resources.py
```

## Next Steps

1. **Explore Themes**: Try different agent themes to find what works for your team
2. **Customize Prompts**: Create agent prompts specific to your project needs
3. **Integrate CI/CD**: Add coordination system to your build pipeline
4. **Scale Up**: Gradually increase agents as you get comfortable

## Support

- Check `CLAUDE.md` for detailed system documentation
- Run `./manage_agents.sh help` for command reference
- Review logs in `logs/` directory for debugging

Remember: The system is designed to augment your development workflow, not replace it. Start simple and expand as needed.