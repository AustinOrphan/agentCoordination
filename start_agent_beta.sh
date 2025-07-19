#!/bin/bash
# Agent Beta Activation Script

echo "🚀 Starting Agent Beta (Migration Specialist)"
echo "Task: 2.1 - Advanced Migration Tools"
echo "Reading prompt from: AGENT_BETA_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"

# Open in new terminal window
osascript <<EOF
tell application "Terminal"
    do script "cd '$CURRENT_DIR' && /Users/austinorphan/.claude/local/claude 'You are Agent Beta, the Migration Specialist. Please read your complete instructions from AGENT_BETA_PROMPT.md and begin Task 2.1 - Advanced Migration Tools. Agent Alpha has completed core integration, you can now proceed.'"
end tell
EOF