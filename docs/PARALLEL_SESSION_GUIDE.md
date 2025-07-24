# Parallel Claude Code Sessions Guide

This guide shows how to run multiple Claude Code agents in parallel using Git worktrees, based on [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees) and [Git worktree documentation](https://git-scm.com/docs/git-worktree).

## Overview

The Multi-Agent Coordination System leverages Git worktrees to enable true parallel execution of multiple Claude Code instances. Each agent works in complete isolation, preventing merge conflicts and enabling concurrent work on the same files.

## Key Benefits

### 1. True Parallelism
- Each agent runs in a separate Claude Code session
- Agents can modify the same files simultaneously without conflicts
- No waiting for other agents to complete their work
- Maximum efficiency with concurrent execution

### 2. Clean Integration
- Each agent works on their own branch (`agent/<name>`)
- Changes are isolated until ready to merge
- Pull requests enable code review before integration
- Main branch remains stable during agent work

### 3. Resource Efficiency
- Shared repository objects reduce disk usage
- No need for multiple full clones
- Efficient Git operations across worktrees
- Minimal overhead for parallel execution

## Setting Up Parallel Sessions

### Prerequisites
```bash
# Check Git version (2.28+ recommended)
git --version

# Ensure Claude Code is installed
claude --version
```

### Initial Setup
```bash
# 1. Configure agents
./manage_agents.sh set-theme programming_languages
./manage_agents.sh set-count 6

# 2. Generate agent files
./generate_agents_dynamic.sh

# 3. Create worktrees for all agents
./worktree_manager_enhanced.sh setup-all

# 4. Verify setup
./worktree_manager_enhanced.sh health-check
```

## Enhanced Worktree Features

### Worktree Locking
Prevent accidental removal of active worktrees:
```bash
# Lock a worktree
./worktree_manager_enhanced.sh lock python "Critical production work"

# Check lock status
./worktree_manager_enhanced.sh list

# Unlock when done
./worktree_manager_enhanced.sh unlock python
```

### Health Monitoring
Ensure worktrees are in good state:
```bash
# Check all worktrees
./worktree_manager_enhanced.sh health-check

# Repair corrupted worktree
./worktree_manager_enhanced.sh repair python

# Clean up stale references
./worktree_manager_enhanced.sh prune
```

### Agent-Specific Configuration
Each agent gets isolated Git configuration:
```bash
# Configure worktree
./worktree_manager_enhanced.sh config python

# Each agent automatically gets:
# - user.name: "Agent Python"
# - user.email: "agent-python@coordination.local"
# - Isolated merge settings
```

## Parallel Workflow

### 1. Start Multiple Agents Simultaneously
```bash
# Terminal 1
./start_agent_python.sh

# Terminal 2
./start_agent_javascript.sh

# Terminal 3
./start_agent_java.sh

# Or use tmux/screen for better management
tmux new-session -d -s agent-python './start_agent_python.sh'
tmux new-session -d -s agent-javascript './start_agent_javascript.sh'
tmux new-session -d -s agent-java './start_agent_java.sh'
```

### 2. Monitor Agent Work
```bash
# Watch all agents
./coordination_manager.sh watch

# Check specific worktree
./worktree_manager_enhanced.sh status python

# View agent activities
tail -f agent_status/python_status.json
```

### 3. Sync and Merge Work
```bash
# Sync agent with main
./worktree_manager_enhanced.sh sync python

# Or manually in agent worktree
cd ../agent-python
git fetch origin main
git merge origin/main

# Push changes
git push origin agent/python
```

### 4. Integration Strategies

#### Pull Request Workflow
```bash
# From agent worktree
cd ../agent-python
git push origin agent/python

# Create PR using GitHub CLI
gh pr create --title "Python: Implement security module" \
  --body "Security enhancements as per deployment plan"
```

#### Direct Merge Workflow
```bash
# From main repository
cd /path/to/agentCoordination
git merge agent/python
git merge agent/javascript
git merge agent/java
```

## Advanced Parallel Patterns

### Dependency Management
When agents have dependencies:
```bash
# Agent Python completes core module
cd ../agent-python
git add .
git commit -m "Python: Core module complete"
git push origin agent/python

# Signal completion to dependent agents
python3 coordination_system/update_agent_status.py python \
  --task "Core module complete" \
  --progress 100 \
  --resolve-blocker "Core module dependency"
```

### Conflict Resolution
When multiple agents modify the same file:
```bash
# Each agent works on their branch
# No conflicts during work!

# At merge time, handle conflicts:
git merge agent/python
git merge agent/javascript  # May have conflicts

# Resolve conflicts
git mergetool
git commit
```

### Staggered Integration
Merge agents in priority order:
```bash
# 1. Merge critical path work first
git merge agent/python

# 2. Test and validate
pytest

# 3. Merge next priority
git merge agent/javascript

# 4. Continue until all integrated
```

## Performance Optimization

### Parallel Startup Script
Create a script to launch all agents:
```bash
#!/bin/bash
# start_all_agents.sh

agents=("python" "javascript" "java" "typescript" "go" "rust")

for agent in "${agents[@]}"; do
    echo "Starting agent $agent..."
    tmux new-session -d -s "agent-$agent" "./start_agent_$agent.sh"
    sleep 2  # Stagger startup
done

echo "All agents started. Use 'tmux ls' to see sessions."
```

### Resource Management
```bash
# Monitor resource usage
htop  # or top

# Check worktree disk usage
du -sh ../agent-*

# Clean up completed worktrees
for agent in python javascript java; do
    if [ -f "agent_status/${agent}_status.json" ]; then
        status=$(jq -r '.progress' "agent_status/${agent}_status.json")
        if [ "$status" == "100" ]; then
            ./worktree_manager_enhanced.sh remove "$agent"
        fi
    fi
done
```

## Best Practices

### 1. Regular Sync
Keep agents up to date with main:
```bash
# Daily sync routine
for agent in $(./worktree_manager_enhanced.sh list | grep agent- | awk '{print $2}'); do
    ./worktree_manager_enhanced.sh sync "$agent"
done
```

### 2. Clean Commits
Encourage agents to make atomic commits:
```bash
# In agent prompt files
"Make small, focused commits with clear messages"
"Commit frequently to avoid large changesets"
"Use conventional commit format: type(scope): description"
```

### 3. Worktree Hygiene
Regular maintenance:
```bash
# Weekly cleanup
./worktree_manager_enhanced.sh prune
./worktree_manager_enhanced.sh health-check

# Remove inactive worktrees
for worktree in $(git worktree list --porcelain | grep "prunable" -B1 | grep "worktree" | cut -d' ' -f2); do
    agent=$(basename "$worktree" | sed 's/agent-//')
    ./worktree_manager_enhanced.sh remove "$agent" --force
done
```

### 4. Communication Patterns
Ensure agents coordinate effectively:
```bash
# Agent Python signals completion
python3 -c "
from coordination_system.agent_communication import CommunicationChannel, Message, MessageType
channel = CommunicationChannel('python')
msg = Message(
    from_id='python',
    to_id='javascript',
    msg_type=MessageType.STATUS_UPDATE,
    payload={'message': 'API endpoints ready for frontend integration'}
)
channel.send_message(msg)
"
```

## Troubleshooting

### Common Issues

#### Worktree Not Found
```bash
# Verify worktree exists
git worktree list

# Repair if needed
./worktree_manager_enhanced.sh repair python
```

#### Agent Can't Push Changes
```bash
# Check branch tracking
cd ../agent-python
git branch -vv

# Set upstream if needed
git push -u origin agent/python
```

#### Merge Conflicts
```bash
# Use 3-way merge for better context
git config merge.conflictStyle diff3

# Or use merge tool
git mergetool --tool=vimdiff
```

#### Performance Issues
```bash
# Check for large files
find ../agent-* -type f -size +10M

# Enable Git performance features
git config core.preloadindex true
git config core.fscache true
git config gc.auto 256
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Multi-Agent Integration

on:
  push:
    branches: [ 'agent/*' ]

jobs:
  integrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Setup worktrees
        run: |
          ./worktree_manager_enhanced.sh setup-all
      
      - name: Run tests
        run: |
          pytest tests/
      
      - name: Merge to main
        if: success()
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          git checkout main
          git merge ${{ github.ref }}
          git push origin main
```

## Security Considerations

### Access Control
```bash
# Each agent uses isolated credentials
git -C ../agent-python config user.email "agent-python@coordination.local"

# No shared SSH keys between agents
# Each worktree maintains separate Git config
```

### Code Review
```bash
# Enforce PR reviews before merge
# Use branch protection rules
# Require status checks to pass
```

## Quick Reference

### Essential Commands
```bash
# Setup all agents
./worktree_manager_enhanced.sh setup-all

# Start agent
./start_agent_<name>.sh

# Check health
./worktree_manager_enhanced.sh health-check

# Lock/unlock
./worktree_manager_enhanced.sh lock <agent> "reason"
./worktree_manager_enhanced.sh unlock <agent>

# Sync with main
./worktree_manager_enhanced.sh sync <agent>

# Clean up
./worktree_manager_enhanced.sh remove <agent>
```

### Monitoring Commands
```bash
# Watch all agents
./coordination_manager.sh watch

# List worktrees
./worktree_manager_enhanced.sh list

# Check specific agent
./worktree_manager_enhanced.sh status <agent>
```

### Maintenance Commands
```bash
# Repair worktree
./worktree_manager_enhanced.sh repair <agent>

# Prune stale references
./worktree_manager_enhanced.sh prune

# Configure worktree
./worktree_manager_enhanced.sh config <agent>
```

## Conclusion

Git worktrees enable true parallel execution of Claude Code agents, maximizing efficiency and preventing conflicts. The enhanced worktree manager provides safety features, health monitoring, and configuration isolation to ensure smooth parallel operations.

Key takeaways:
- Each agent works in complete isolation
- No merge conflicts during development
- Clean integration through branches
- Enhanced features for production use
- Scalable from 1 to 24+ agents

For more information:
- [Claude Code Parallel Sessions](https://docs.anthropic.com/en/docs/claude-code/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees)
- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Multi-Agent Coordination System](./CLAUDE.md)