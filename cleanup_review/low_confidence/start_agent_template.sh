#!/bin/bash
# Template for Agent Startup Scripts with Git Worktree Support

# Get agent name from script name
SCRIPT_NAME=$(basename "$0")
AGENT_NAME=$(echo "$SCRIPT_NAME" | sed 's/start_agent_//;s/.sh$//')

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get directories
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_BASE_DIR="$(dirname "$REPO_ROOT")"
WORKTREE_PATH="$WORKTREE_BASE_DIR/agent-$AGENT_NAME"

# Get agent details from config
AGENT_UPPER=$(echo "$AGENT_NAME" | tr '[:lower:]' '[:upper:]')
AGENT_CONFIG=$(jq -r ".themes[.current_theme].agents[] | select(. == \"$AGENT_NAME\")" "$REPO_ROOT/agent_config.json" 2>/dev/null || echo "$AGENT_NAME")

# Determine agent role based on position
AGENT_INDEX=$(jq -r ".themes[.current_theme].agents | to_entries | .[] | select(.value == \"$AGENT_NAME\") | .key" "$REPO_ROOT/agent_config.json" 2>/dev/null || echo "0")
ROLES=("Critical Path Lead" "Migration Specialist" "Dashboard Developer" "DevOps Engineer" "Security Engineer" "UX Engineer")
AGENT_ROLE="${ROLES[$((AGENT_INDEX % 6))]}"

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
osascript <<EOF
tell application "Terminal"
    do script "cd '$WORKTREE_PATH' && echo 'Working in worktree: $WORKTREE_PATH' && echo 'Branch: agent/$AGENT_NAME' && echo '' && /Users/austinorphan/.claude/local/claude 'You are Agent $AGENT_UPPER, the $AGENT_ROLE. Please read your complete instructions from AGENT_${AGENT_UPPER}_PROMPT.md in your current directory. You are working in a git worktree specific to your agent, allowing you to work independently without conflicts with other agents.'"
end tell
EOF