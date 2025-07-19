#!/bin/bash
# Agent Zeta Activation Script

echo "🚀 Starting Agent Zeta (UX Engineer)"
echo "Task: 3.4 - Enhanced CLI Interface"
echo "Reading prompt from: AGENT_ZETA_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"

# Open in new terminal window
osascript <<EOF
tell application "Terminal"
    do script "cd '$CURRENT_DIR' && /Users/austinorphan/.claude/local/claude 'You are Agent Zeta, the UX Engineer. Please read your complete instructions from AGENT_ZETA_PROMPT.md and begin Task 3.4 - Enhanced CLI Interface. Wait for Agent Gamma to complete Task 3.2 before starting.'"
end tell
EOF