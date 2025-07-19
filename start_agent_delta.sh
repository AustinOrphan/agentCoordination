#!/bin/bash
# Agent Delta Activation Script

echo "🚀 Starting Agent Delta (DevOps Engineer)"
echo "Task: 2.2 - CI/CD Pipeline"
echo "Reading prompt from: AGENT_DELTA_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"

# Open in new terminal window
osascript <<EOF
tell application "Terminal"
    do script "cd '$CURRENT_DIR' && /Users/austinorphan/.claude/local/claude 'You are Agent Delta, the DevOps Engineer. Please read your complete instructions from AGENT_DELTA_PROMPT.md and begin Task 2.2 - CI/CD Pipeline. Agent Alpha has completed core integration, you can now proceed.'"
end tell
EOF