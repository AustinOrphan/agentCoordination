#!/bin/bash
# Agent Runner - Handles both test simulator and real Claude Code execution

# Configuration
AGENT_NAME="$1"
AGENT_UPPER=$(echo "$AGENT_NAME" | tr '[:lower:]' '[:upper:]')
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check mode from environment or default to simulator
MODE="${AGENT_MODE:-simulator}"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🤖 Agent Runner for $AGENT_UPPER${NC}"
echo -e "${CYAN}Mode: $MODE${NC}"

# Initialize agent
python3 "$SCRIPT_DIR/coordination_system/initialize_agent.py" "$AGENT_NAME"

if [ "$MODE" = "simulator" ]; then
    echo -e "${YELLOW}Running in simulator mode...${NC}"
    python3 "$SCRIPT_DIR/test_agent_simulator.py" "$AGENT_NAME"
elif [ "$MODE" = "claude" ]; then
    echo -e "${YELLOW}Running Claude Code...${NC}"
    
    # Try different Claude command locations
    if command -v claude >/dev/null 2>&1; then
        # Claude is in PATH
        claude "You are Agent $AGENT_UPPER. Please read your complete instructions from AGENT_${AGENT_UPPER}_PROMPT.md in your current directory."
    elif [ -x "/Users/$USER/.claude/local/claude" ]; then
        # Try user-specific location
        /Users/$USER/.claude/local/claude "You are Agent $AGENT_UPPER. Please read your complete instructions from AGENT_${AGENT_UPPER}_PROMPT.md in your current directory."
    elif [ -x "/usr/local/bin/claude" ]; then
        # Try system location
        /usr/local/bin/claude "You are Agent $AGENT_UPPER. Please read your complete instructions from AGENT_${AGENT_UPPER}_PROMPT.md in your current directory."
    else
        echo -e "${RED}Error: Claude command not found!${NC}"
        echo "Please ensure Claude Code is installed and in your PATH"
        echo "Or set AGENT_MODE=simulator to use the test simulator"
        exit 1
    fi
else
    echo -e "${RED}Unknown mode: $MODE${NC}"
    echo "Valid modes: simulator, claude"
    exit 1
fi