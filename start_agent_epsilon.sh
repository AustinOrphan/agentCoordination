#!/bin/bash
# Agent Epsilon Activation Script

echo "🚀 Starting Agent Epsilon (Security Engineer)"
echo "Task: 1.3 - Security Review"
echo "Reading prompt from: AGENT_EPSILON_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"

# Open in new terminal window
osascript <<EOF
tell application "Terminal"
    do script "cd '$CURRENT_DIR' && /Users/austinorphan/.claude/local/claude 'You are Agent Epsilon, the Security Engineer. Please read your complete instructions from AGENT_EPSILON_PROMPT.md and begin Task 1.3 - Security Review. Wait for Agent Alpha to complete Task 1.1 before starting.'"
end tell
EOF