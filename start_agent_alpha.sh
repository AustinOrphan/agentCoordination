#!/bin/bash
# Agent Alpha Activation Script

echo "🚀 Starting Agent Alpha (Critical Path Lead)"
echo "Task: 1.1 - Core Integration"
echo "Reading prompt from: AGENT_ALPHA_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Get current directory
CURRENT_DIR="$(pwd)"

# Open in new terminal window
osascript <<EOF
tell application "Terminal"
    do script "cd '$CURRENT_DIR' && /Users/austinorphan/.claude/local/claude 'You are Agent Alpha, the Critical Path Lead. Please read your complete instructions from AGENT_ALPHA_PROMPT.md and begin Task 1.1 - Core Integration immediately. Your work is critical path and blocks other agents.'"
end tell
EOF