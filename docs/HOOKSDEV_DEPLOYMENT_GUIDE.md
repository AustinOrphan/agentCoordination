# HooksDev Project Deployment Guide

This guide documents how to deploy the agentCoordination system to work on the HooksDev project using the existing deployment plans.

## Overview

The HooksDev project contains comprehensive deployment plans for 5 specialized agents to enhance Claude Code hooks. This guide shows how to use agentCoordination's automated deployment system to execute these plans with coordinated agents.

## Prerequisites

- agentCoordination repository (this repo) properly set up
- HooksDev project available at `/Users/austinorphan/Downloads/HooksDev`
- Python 3.x and required dependencies installed
- Git worktree support available

## One-Command Deployment

The simplest way to deploy is using the automated `start_project.sh` script:

```bash
cd /path/to/agentCoordination
./start_project.sh existing /Users/austinorphan/Downloads/HooksDev -n "HooksDev Enhancement"
```

### What This Command Does

1. **Project Analysis** 📊
   - Automatically scans the HooksDev project structure
   - Identifies files, technologies, and dependencies
   - Generates `project_analysis.json` and `project_analysis_report.md`

2. **System Initialization** 🚀
   - Creates dynamic agent assignments based on project needs
   - Initializes coordination system with authorities and communication channels
   - Sets up git worktrees for parallel agent execution

3. **Auto-start Services** ⚡
   - Launches lifecycle daemon (`manage_agents.sh auto`)
   - Opens monitoring dashboard (`coordination_manager.sh watch`)
   - Agents become ready to receive and execute tasks

4. **Agent File Generation** 🤖
   - Creates `AGENT_*_PROMPT.md` files with dynamic templates
   - Sets up agent communication infrastructure
   - Configures agent-specific git worktrees

## Post-Deployment Setup

### 1. Copy HooksDev Deployment Plans

After the automated setup completes, you need to integrate the HooksDev deployment plans with the generated agent prompts:

```bash
# Navigate to HooksDev deployment plans
cd /Users/austinorphan/Downloads/HooksDev/Hooks/deployment-plans

# Copy/append plans to corresponding agent prompts
# Map the 5 HooksDev agents to your generated agents:

# Example mapping (adjust based on your theme):
cat 01-SECURITY-ENHANCEMENT-AGENT.md >> /path/to/agentCoordination/AGENT_PYTHON_PROMPT.md
cat 02-TESTING-INFRASTRUCTURE-AGENT.md >> /path/to/agentCoordination/AGENT_JAVASCRIPT_PROMPT.md
cat 03-API-INTEGRATION-AGENT.md >> /path/to/agentCoordination/AGENT_JAVA_PROMPT.md
cat 04-CODE-ANALYSIS-ENHANCEMENT-AGENT.md >> /path/to/agentCoordination/AGENT_TYPESCRIPT_PROMPT.md
cat 05-DOCUMENTATION-MONITORING-AGENT.md >> /path/to/agentCoordination/AGENT_GO_PROMPT.md
```

### 2. Agent Role Mapping

The HooksDev deployment plans define 5 specialized agents:

| HooksDev Agent | Responsibilities | Target Readiness | Estimated Time |
|----------------|------------------|------------------|----------------|
| **Security Enhancement** | prompt-enhancer.py, post-code-write.py security | 90% | 45 min |
| **Testing Infrastructure** | All 26 hooks testing framework | 90% | 2.5 hours |
| **API Integration** | github-issue-tracker.py, performance-analyzer.py | 85% | 45 min |
| **Code Analysis Enhancement** | typescript-safety.py, fastapi-validator.py, prisma-validator.py | 85% | 1 hour |
| **Documentation & Monitoring** | All 5 monitoring hooks documentation | 80% | 1 hour |

### 3. Monitor Execution

The system automatically opens a monitoring dashboard. You can also check status manually:

```bash
# Check overall system status
./coordination_manager.sh show-all

# Check lifecycle daemon
./manage_agents.sh lifecycle status

# View real-time logs
tail -f lifecycle_daemon.log

# Check individual agent status
ls -la agent_status/
```

### 4. Agent Execution Workflow

Agents will automatically:

1. **Initialize** in their git worktrees (`../agent-<name>`)
2. **Receive assignments** through the coordination system
3. **Execute deployment plans** following the 5-phase structure:
   - Setup & Prerequisites (30 min)
   - Research & Analysis (45 min) 
   - Implementation (varies: 45 min - 2.5 hours)
   - Testing & Validation (30 min)
   - Documentation & Handoff (15 min)
4. **Report progress** through status updates
5. **Create pull requests** when work is complete

## Manual Deployment (Alternative)

If you prefer more control, you can deploy manually:

```bash
# 1. Initialize coordination system
./coordination_manager.sh init

# 2. Configure theme and agents
./manage_agents.sh set-theme programming_languages
./manage_agents.sh set-count 6

# 3. Generate dynamic agent files
./generate_agents_dynamic.sh

# 4. Set up git worktrees
./worktree_manager.sh setup-all

# 5. Copy deployment plans to agent prompts
# (Same as post-deployment step above)

# 6. Start system
./manage_agents.sh auto
./coordination_manager.sh watch  # In separate terminal
```

## Expected Timeline

Based on the HooksDev deployment plan estimates:

- **Setup & Initialization**: 5-10 minutes
- **Agent Assignment & Planning**: 30 minutes per agent (parallel)
- **Implementation Phase**: 45 minutes - 2.5 hours per agent (parallel)
- **Testing & Validation**: 30 minutes per agent (parallel)
- **Total Project Time**: 6-8 hours (with 5+ agents working in parallel)

## Success Criteria

### Individual Agent Success
- ✅ Security Enhancement: 90% production readiness
- ✅ Testing Infrastructure: 90% test coverage across all 26 hooks
- ✅ API Integration: 85% readiness for GitHub and performance APIs
- ✅ Code Analysis: 85% readiness for TypeScript, FastAPI, and Prisma validation
- ✅ Documentation & Monitoring: 80% coverage of all monitoring hooks

### System-Level Success
- ✅ All hooks pass comprehensive testing
- ✅ No performance regressions introduced
- ✅ Security scans show no new vulnerabilities
- ✅ Documentation updated for all enhanced hooks
- ✅ Integration testing passes end-to-end

## Troubleshooting

### Common Issues

**Agents not starting automatically:**
```bash
# Check lifecycle daemon status
./manage_agents.sh lifecycle status

# Restart if needed
./manage_agents.sh lifecycle restart
```

**Git worktree conflicts:**
```bash
# Check worktree status
./worktree_manager.sh list

# Recreate if needed
./worktree_manager.sh remove <agent_name>
./worktree_manager.sh create <agent_name>
```

**Agent communication issues:**
```bash
# Check communication channels
ls -la agent_communication/*/

# Restart agent communication
python3 coordination_system/agent_communication.py --reset
```

## Files and Directories

### Key Files Created
- `AGENT_*_PROMPT.md` - Agent-specific instructions with HooksDev plans
- `start_agent_*.sh` - Agent startup scripts
- `project_analysis.json` - HooksDev project analysis results
- `project_analysis_report.md` - Human-readable analysis report

### Key Directories
- `agent_communication/` - Agent inbox/outbox message channels
- `agent_status/` - Agent status tracking JSON files
- `../agent-*/` - Individual agent git worktrees
- `logs/` - System and agent logs

## Advanced Usage

### Custom Agent Assignments
You can manually modify agent assignments by editing the generated `AGENT_*_PROMPT.md` files to change which agent works on which HooksDev deployment plan.

### Adding More Agents
```bash
# Increase agent count and regenerate
./manage_agents.sh set-count 8
./generate_agents_dynamic.sh
```

### Emergency Procedures
If agents encounter issues, they have emergency authority protocols built into the dynamic system. Check `99-ROLLBACK-RECOVERY-PROCEDURES.md` in the HooksDev deployment plans.

## References

- **HooksDev Deployment Plans**: `/Users/austinorphan/Downloads/HooksDev/Hooks/deployment-plans/`
- **agentCoordination Documentation**: `CLAUDE.md`
- **Dynamic Authority System**: `DYNAMIC_AUTHORITY_SYSTEM.md`
- **Project Setup Guide**: `coordination_system/PROJECT_SETUP_GUIDE.md`

---

**Quick Start Summary:**
```bash
./start_project.sh existing /Users/austinorphan/Downloads/HooksDev -n "HooksDev Enhancement"
# Follow prompts, copy deployment plans to agent prompts, monitor dashboard
```