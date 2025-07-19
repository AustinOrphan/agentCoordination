#!/bin/bash
# Agent Gamma Activation Script

echo "🚀 Starting Agent Gamma (Dashboard Developer)"
echo "Task: 3.1 - Advanced Dashboard"
echo "Reading prompt from: AGENT_GAMMA_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"

# Open in new terminal window
osascript <<EOF
tell application "Terminal"
    do script "cd '$CURRENT_DIR' && /Users/austinorphan/.claude/local/claude 'You are Agent Gamma, the Dashboard Developer. Please read your complete instructions from AGENT_GAMMA_PROMPT.md and begin Task 3.1 - Advanced Dashboard. Agent Alpha has completed core integration, you can now proceed.'"
end tell
EOF