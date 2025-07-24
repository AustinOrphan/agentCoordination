# Plan Integration Guide

This guide shows how to use external deployment plans (Markdown, XML, JSON) with the agentCoordination system's dynamic agent generator.

## Overview

The plan integration system allows you to:
- **Import deployment plans** from external projects (MD/XML/JSON formats)
- **Automatically assign plans** to agents based on current theme
- **Generate enhanced agent prompts** with specialized instructions
- **Maintain dynamic coordination** while following specific deployment workflows

## Quick Start

### Using HooksDev Deployment Plans
```bash
# Generate agents with HooksDev plans integrated
./generate_agents_with_plans.sh --plans /Users/austinorphan/Downloads/HooksDev/Hooks/deployment-plans

# Or with start_project.sh (enhanced)
./start_project.sh existing /path/to/project --plans /path/to/deployment-plans
```

### Using Any External Plans
```bash
# Standard dynamic agents (no external plans)
./generate_agents_dynamic.sh

# Enhanced agents with external plans
./generate_agents_with_plans.sh --plans /path/to/your/deployment-plans

# Dry run to see what would be generated
./generate_agents_with_plans.sh --plans /path/to/plans --dry-run
```

## Supported Plan Formats

### 1. Markdown Plans (.md)
```markdown
# Security Enhancement Agent

## Agent Role
Security Specialist responsible for enhancing code security

## Responsibilities
- Implement security validations
- Review authentication mechanisms
- Enhance input sanitization

## Tasks
### Task 1: Security Analysis
Analyze current security implementations

**Subtasks:**
- Scan for vulnerabilities
- Review authentication flows
- Test input validation

## Success Criteria
- ✅ 90% security coverage achieved
- ✅ All critical vulnerabilities addressed
- ✅ Security tests pass

## Timeline
45 minutes implementation + 30 minutes testing

## Dependencies
- Core system analysis complete
- Test framework available
```

### 2. XML Plans (.xml)
```xml
<deployment_plan>
    <title>API Integration Agent</title>
    <agent_role>API Integration Specialist</agent_role>
    
    <responsibilities>
        <item>Integrate external APIs</item>
        <item>Handle API authentication</item>
        <item>Implement rate limiting</item>
    </responsibilities>
    
    <tasks>
        <task>
            <description>GitHub API Integration</description>
            <subtasks>
                <subtask>Set up API credentials</subtask>
                <subtask>Implement issue tracking</subtask>
                <subtask>Add error handling</subtask>
            </subtasks>
        </task>
    </tasks>
    
    <success_criteria>
        <criterion>GitHub API fully functional</criterion>
        <criterion>Error handling robust</criterion>
        <criterion>Performance meets targets</criterion>
    </success_criteria>
    
    <timeline>2 hours</timeline>
    
    <dependencies>
        <dependency>GitHub API access configured</dependency>
        <dependency>Test environment ready</dependency>
    </dependencies>
</deployment_plan>
```

### 3. JSON Plans (.json)
```json
{
    "title": "Testing Infrastructure Agent",
    "agent_role": "Testing Specialist",
    "responsibilities": [
        "Implement comprehensive testing",
        "Set up CI/CD pipelines",
        "Ensure test coverage targets"
    ],
    "tasks": [
        {
            "description": "Test Framework Setup",
            "subtasks": [
                "Configure pytest framework",
                "Set up coverage reporting",
                "Implement test utilities"
            ]
        }
    ],
    "success_criteria": [
        "90% test coverage achieved",
        "All tests pass in CI/CD",
        "Performance benchmarks met"
    ],
    "timeline": "2.5 hours",
    "dependencies": [
        "Core system ready",
        "Development environment configured"
    ]
}
```

## How Plan Integration Works

### 1. Plan Discovery
The system automatically discovers plan files in the specified directory:
```bash
deployment-plans/
├── 01-security-enhancement.md
├── 02-testing-infrastructure.md
├── 03-api-integration.xml
├── 04-code-analysis.json
└── 05-documentation.md
```

### 2. Plan Parsing
Each plan is parsed to extract:
- **Agent Role**: Specialized role definition
- **Responsibilities**: Key areas of ownership
- **Tasks**: Specific work items with subtasks
- **Success Criteria**: Completion requirements
- **Timeline**: Estimated duration
- **Dependencies**: Prerequisites and coordination needs

### 3. Agent Assignment
Plans are assigned to agents based on:
- **Current theme**: Uses agent names from selected theme (greek_letters, programming_languages, etc.)
- **Agent count**: Distributes plans across available agents
- **Plan priority**: Earlier numbered plans get higher priority agents

### 4. Prompt Enhancement
The base dynamic agent template is enhanced with plan-specific content:

```markdown
# Agent Python

You are Agent Python, part of a dynamic multi-agent coordination system.

## Your Specialized Assignment

### Your Role: Security Enhancement Specialist

### Responsibilities:
- Implement security validations
- Review authentication mechanisms
- Enhance input sanitization

### Tasks:

#### Task 1: Security Analysis
Analyze current security implementations

**Subtasks:**
- Scan for vulnerabilities
- Review authentication flows
- Test input validation

### Success Criteria:
- ✅ 90% security coverage achieved
- ✅ All critical vulnerabilities addressed
- ✅ Security tests pass

### Timeline: 45 minutes implementation + 30 minutes testing

### Dependencies:
- Core system analysis complete
- Test framework available

## Authority Protocol
[Standard dynamic authority content...]

## Collaboration Framework
[Standard communication protocol...]
```

## Integration Commands

### Basic Integration
```bash
# Generate agents with plans
./generate_agents_with_plans.sh --plans /path/to/deployment-plans

# Check what would be generated (dry run)
./generate_agents_with_plans.sh --plans /path/to/deployment-plans --dry-run
```

### Advanced Integration
```bash
# Use specific theme with plans
./manage_agents.sh set-theme programming_languages
./manage_agents.sh set-count 8
./generate_agents_with_plans.sh --plans /path/to/deployment-plans

# Direct plan integration (without shell script)
python3 plan_integrator.py /path/to/deployment-plans --agent-count 6 --output-dir .
```

### Full Project Deployment with Plans
```bash
# Enhanced start_project.sh (future enhancement)
./start_project.sh existing /path/to/project --plans /path/to/deployment-plans -n "Project with Plans"
```

## Plan Integration Workflow

### 1. Prepare Plans
Organize your deployment plans in a directory:
```
my-deployment-plans/
├── 01-MASTER-COORDINATION.md
├── 02-SECURITY-ENHANCEMENT.md
├── 03-TESTING-INFRASTRUCTURE.xml
├── 04-API-INTEGRATION.json
└── 05-DOCUMENTATION.md
```

### 2. Configure Agent System
```bash
# Set desired theme and count
./manage_agents.sh set-theme programming_languages
./manage_agents.sh set-count 5  # Match number of plans
```

### 3. Generate Enhanced Agents
```bash
# Generate with plan integration
./generate_agents_with_plans.sh --plans ./my-deployment-plans
```

### 4. Verify Generated Files
```bash
# Check generated agent prompts
ls -la AGENT_*_PROMPT.md

# Verify plan integration
head -50 AGENT_PYTHON_PROMPT.md  # Should show specialized assignment
```

### 5. Deploy and Monitor
```bash
# Start coordination system
./coordination_manager.sh init
./manage_agents.sh auto
./coordination_manager.sh watch
```

## Agent-to-Plan Mapping

The system maps agents to plans based on theme and count:

| Theme | Agent 1 | Agent 2 | Agent 3 | Agent 4 | Agent 5 |
|-------|---------|---------|---------|---------|---------|
| **programming_languages** | python | javascript | java | typescript | go |
| **greek_letters** | alpha | beta | gamma | delta | epsilon |
| **ocean_creatures** | shark | dolphin | whale | octopus | jellyfish |

Plans are assigned in order:
- **Plan 01** → **Agent 1** (python/alpha/shark)
- **Plan 02** → **Agent 2** (javascript/beta/dolphin)
- **Plan 03** → **Agent 3** (java/gamma/whale)
- etc.

## Best Practices

### Plan Structure
- **Use clear titles** that indicate the agent's specialized role
- **Define specific responsibilities** rather than vague objectives
- **Break down tasks** into actionable subtasks
- **Include measurable success criteria** (percentages, metrics)
- **Estimate realistic timelines** for coordination purposes

### File Organization
```bash
deployment-plans/
├── 00-MASTER-COORDINATION.md      # Master oversight role
├── 01-CORE-FEATURE-A.md           # Primary feature work
├── 02-CORE-FEATURE-B.md           # Secondary feature work
├── 03-TESTING-VALIDATION.md       # Testing and quality
├── 04-DOCUMENTATION.md            # Documentation and cleanup
└── 99-ROLLBACK-PROCEDURES.md      # Emergency procedures
```

### Plan Content Guidelines
```markdown
# Agent Title Should Match Role

## Agent Role
[Specific, actionable role description]

## Responsibilities
- [Concrete, measurable responsibility]
- [Clear ownership boundaries]
- [Integration points with other agents]

## Tasks
### Task 1: [Specific Task Name]
[Clear description of what needs to be done]

**Subtasks:**
- [Actionable subtask with clear completion criteria]
- [Dependencies and prerequisites clearly stated]

## Success Criteria
- ✅ [Measurable outcome with specific targets]
- ✅ [Testable validation criteria]
- ✅ [Integration success requirements]

## Timeline
[Realistic estimates: "2 hours implementation + 30 minutes testing"]

## Dependencies
- [What must be completed by other agents first]
- [External prerequisites and requirements]
```

## Troubleshooting

### Common Issues

**Plans not being integrated:**
```bash
# Check plan directory exists
ls -la /path/to/deployment-plans

# Verify supported file formats
file /path/to/deployment-plans/*

# Test plan parsing
python3 plan_integrator.py /path/to/deployment-plans --dry-run
```

**Agent count mismatch:**
```bash
# Check current configuration
./agent_theme_manager.py show

# Adjust agent count to match plans
./manage_agents.sh set-count 6
```

**Generated prompts missing plan content:**
```bash
# Verify plan content extraction
python3 -c "
from plan_integrator import PlanParser
parser = PlanParser()
plan = parser.parse_markdown_plan('/path/to/plan.md')
print(plan['responsibilities'])
"
```

### Plan Format Issues

**Markdown parsing problems:**
- Ensure headers use `##` format
- Check for consistent bullet point formatting (`- `, `* `)
- Verify success criteria use checkboxes (`- ✅`)

**XML validation errors:**
- Validate XML syntax: `xmllint --noout plan.xml`
- Check required elements: `title`, `agent_role`, `responsibilities`

**JSON structure issues:**
- Validate JSON: `python3 -m json.tool plan.json`
- Ensure all required fields are present

## Examples

### HooksDev Integration Example
```bash
# Real-world example with HooksDev plans
cd /path/to/agentCoordination

# Configure for 5 agents (matching 5 HooksDev plans)
./manage_agents.sh set-theme programming_languages
./manage_agents.sh set-count 5

# Generate enhanced agents with HooksDev plans
./generate_agents_with_plans.sh --plans /Users/austinorphan/Downloads/HooksDev/Hooks/deployment-plans

# Result: 5 agents with specialized HooksDev assignments
# - python: Security Enhancement (01-SECURITY-ENHANCEMENT-AGENT.md)
# - javascript: Testing Infrastructure (02-TESTING-INFRASTRUCTURE-AGENT.md)
# - java: API Integration (03-API-INTEGRATION-AGENT.md)
# - typescript: Code Analysis (04-CODE-ANALYSIS-ENHANCEMENT-AGENT.md)
# - go: Documentation & Monitoring (05-DOCUMENTATION-MONITORING-AGENT.md)
```

### Custom Project Integration
```bash
# Create custom deployment plans
mkdir ./my-project-plans
cat > ./my-project-plans/01-frontend.md << 'EOF'
# Frontend Development Agent

## Agent Role
Frontend Specialist responsible for UI/UX implementation

## Responsibilities
- Implement React components
- Handle state management
- Ensure responsive design

## Tasks
### Task 1: Component Implementation
Build core UI components

**Subtasks:**
- Create reusable components
- Implement state management
- Add responsive styles

## Success Criteria
- ✅ All components render correctly
- ✅ State management functional
- ✅ Mobile-responsive design

## Timeline
4 hours

## Dependencies
- Design system ready
- API endpoints available
EOF

# Generate agents with custom plans
./generate_agents_with_plans.sh --plans ./my-project-plans
```

## Advanced Usage

### Custom Plan Templates
Create reusable plan templates for common agent roles:

```bash
# templates/security-agent-template.md
# templates/testing-agent-template.md
# templates/frontend-agent-template.md
```

### Plan Validation
```bash
# Validate all plans in directory
python3 plan_integrator.py /path/to/plans --dry-run --verbose
```

### Integration with CI/CD
```bash
# In your deployment pipeline
./generate_agents_with_plans.sh --plans ./deployment-plans
./start_project.sh existing . --no-watch
# Wait for agents to complete work
./coordination_manager.sh validate-completion
```

---

## Quick Reference

### Essential Commands
```bash
# Generate agents with external plans
./generate_agents_with_plans.sh --plans /path/to/deployment-plans

# Test plan integration
./generate_agents_with_plans.sh --plans /path/to/plans --dry-run

# Direct plan parsing
python3 plan_integrator.py /path/to/deployment-plans --agent-count 6

# Check generated agent prompts
ls -la AGENT_*_PROMPT.md
head -50 AGENT_PYTHON_PROMPT.md
```

### File Structure After Integration
```
agentCoordination/
├── AGENT_PYTHON_PROMPT.md        # Enhanced with Plan 01
├── AGENT_JAVASCRIPT_PROMPT.md    # Enhanced with Plan 02
├── AGENT_JAVA_PROMPT.md          # Enhanced with Plan 03
├── start_agent_python.sh         # Agent startup scripts
├── start_agent_javascript.sh
└── agent_communication/          # Agent communication channels
    ├── python/
    ├── javascript/
    └── java/
```

The plan integration system transforms generic agents into specialized workers while maintaining the dynamic coordination capabilities of the agentCoordination system.