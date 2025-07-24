#!/bin/bash
# Agent Octopus Startup Script with Git Worktree Support

# Agent configuration
AGENT_NAME="octopus"
AGENT_UPPER="OCTOPUS"
AGENT_ROLE="DevOps Engineer"

# Color codes
GREEN='[0;32m'
YELLOW='[1;33m'
BLUE='[0;34m'
NC='[0m'

# Get directories
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_BASE_DIR="$(dirname "$REPO_ROOT")"
WORKTREE_PATH="$WORKTREE_BASE_DIR/agent-$AGENT_NAME"

echo -e "${BLUE}🚀 Starting Agent $AGENT_UPPER ($AGENT_ROLE)${NC}"

# Check if worktree exists, create if not
if ! git worktree list | grep -q "$WORKTREE_PATH"; then
    echo -e "${YELLOW}Creating worktree for Agent $AGENT_UPPER...${NC}"
    "$REPO_ROOT/worktree_manager.sh" create "$AGENT_NAME"
fi

echo -e "${GREEN}✓ Using worktree at: $WORKTREE_PATH${NC}"
echo "Reading prompt from: AGENT_${AGENT_UPPER}_PROMPT.md"
echo "Opening new terminal window..."
echo ""

# Open in new terminal window with worktree directory
# Use exec to minimize shell initialization and reduce grep errors
osascript <<EOFSCRIPT
tell application "Terminal"
    do script "exec /bin/bash -c 'cd \"$WORKTREE_PATH\" 2>/dev/null && echo \"Working in worktree: $WORKTREE_PATH\" && echo \"Branch: agent/$AGENT_NAME\" && echo \"\" && exec /Users/austinorphan/.claude/local/claude \"You are Agent $AGENT_UPPER, the $AGENT_ROLE. Please read your complete instructions from AGENT_${AGENT_UPPER}_PROMPT.md in your current directory. You are working in a git worktree specific to your agent, allowing you to work independently without conflicts with other agents.\"'"
end tell
EOFSCRIPT
