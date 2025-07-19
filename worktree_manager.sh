#!/bin/bash

# Git Worktree Manager for Multi-Agent Coordination System
# This script manages git worktrees for parallel agent execution

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_BASE_DIR="$(dirname "$REPO_ROOT")"

# Function to display usage
usage() {
    echo -e "${CYAN}Git Worktree Manager for Agent Coordination${NC}"
    echo -e "${GREEN}Usage:${NC} $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${BLUE}create <agent>${NC}     Create a worktree for the specified agent"
    echo -e "  ${BLUE}remove <agent>${NC}     Remove the worktree for the specified agent"
    echo -e "  ${BLUE}list${NC}               List all agent worktrees"
    echo -e "  ${BLUE}status <agent>${NC}     Show status of agent's worktree"
    echo -e "  ${BLUE}clean${NC}              Remove all agent worktrees"
    echo -e "  ${BLUE}setup-all${NC}          Create worktrees for all configured agents"
    echo -e "  ${BLUE}sync <agent>${NC}       Sync agent's worktree with main branch"
    exit 1
}

# Function to get agent list from config
get_configured_agents() {
    if [[ -f "$REPO_ROOT/agent_config.json" ]]; then
        local current_theme=$(jq -r '.current_theme' "$REPO_ROOT/agent_config.json")
        local agent_count=$(jq -r '.agent_count' "$REPO_ROOT/agent_config.json")
        jq -r ".themes[\"$current_theme\"].agents[:$agent_count][]" "$REPO_ROOT/agent_config.json"
    else
        echo -e "${RED}Error: agent_config.json not found${NC}" >&2
        exit 1
    fi
}

# Function to create a worktree for an agent
create_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    local branch_name="agent/$agent"
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    # Check if worktree already exists
    if git worktree list | grep -q "$worktree_path"; then
        echo -e "${YELLOW}Worktree for agent '$agent' already exists at: $worktree_path${NC}"
        return 0
    fi
    
    # Check if branch exists
    if git branch --list "$branch_name" | grep -q "$branch_name"; then
        echo -e "${BLUE}Using existing branch: $branch_name${NC}"
        git worktree add "$worktree_path" "$branch_name"
    else
        echo -e "${GREEN}Creating new branch and worktree for agent '$agent'${NC}"
        git worktree add -b "$branch_name" "$worktree_path" main
    fi
    
    echo -e "${GREEN}✓ Worktree created for agent '$agent' at: $worktree_path${NC}"
    
    # Copy agent-specific files to worktree
    local agent_upper=$(echo "$agent" | tr '[:lower:]' '[:upper:]')
    if [[ -f "$REPO_ROOT/AGENT_${agent_upper}_PROMPT.md" ]]; then
        cp "$REPO_ROOT/AGENT_${agent_upper}_PROMPT.md" "$worktree_path/"
    fi
    
    # Create agent-specific status file in worktree
    mkdir -p "$worktree_path/agent_status"
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        cp "$REPO_ROOT/agent_status/${agent}_status.json" "$worktree_path/agent_status/"
    fi
    
    # Update agent status with worktree info
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        jq --arg path "$worktree_path" --arg branch "$branch_name" \
            '. + {"worktree": {"path": $path, "branch": $branch}}' \
            "$REPO_ROOT/agent_status/${agent}_status.json" > \
            "$REPO_ROOT/agent_status/${agent}_status.json.tmp" && \
        mv "$REPO_ROOT/agent_status/${agent}_status.json.tmp" \
           "$REPO_ROOT/agent_status/${agent}_status.json"
    fi
}

# Function to remove a worktree
remove_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    if ! git worktree list | grep -q "$worktree_path"; then
        echo -e "${YELLOW}No worktree found for agent '$agent'${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}Removing worktree for agent '$agent'...${NC}"
    git worktree remove --force "$worktree_path" 2>/dev/null || true
    
    # Update agent status to remove worktree info
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        jq 'del(.worktree)' "$REPO_ROOT/agent_status/${agent}_status.json" > \
            "$REPO_ROOT/agent_status/${agent}_status.json.tmp" && \
        mv "$REPO_ROOT/agent_status/${agent}_status.json.tmp" \
           "$REPO_ROOT/agent_status/${agent}_status.json"
    fi
    
    echo -e "${GREEN}✓ Worktree removed for agent '$agent'${NC}"
}

# Function to list all worktrees
list_worktrees() {
    echo -e "${CYAN}Agent Worktrees:${NC}"
    echo -e "${BLUE}=================${NC}"
    
    # Get all worktrees
    git worktree list --porcelain | awk '
        /^worktree/ { 
            path = $2
            # Check if this is an agent worktree
            if (match(path, /agent-([a-zA-Z]+)/, m)) {
                agent = m[1]
                worktrees[agent] = path
            }
        }
        /^HEAD/ && agent {
            heads[agent] = $2
        }
        /^branch/ && agent {
            branches[agent] = $2
            agent = ""
        }
        END {
            for (a in worktrees) {
                printf "Agent: %-10s Path: %-40s Branch: %s\n", 
                       toupper(a), worktrees[a], branches[a]
            }
        }
    ' | while read line; do
        echo -e "${GREEN}$line${NC}"
    done
    
    # Count worktrees
    local count=$(git worktree list | grep -c "agent-" || echo "0")
    echo -e "\n${YELLOW}Total agent worktrees: $count${NC}"
}

# Function to show worktree status
show_status() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    if ! git worktree list | grep -q "$worktree_path"; then
        echo -e "${RED}No worktree found for agent '$agent'${NC}"
        exit 1
    fi
    
    echo -e "${CYAN}Status for Agent $agent:${NC}"
    echo -e "${BLUE}=====================${NC}"
    
    # Show worktree info
    git worktree list | grep "$worktree_path" | while read line; do
        echo -e "${GREEN}Worktree: $line${NC}"
    done
    
    # Show branch status
    echo -e "\n${YELLOW}Branch Status:${NC}"
    cd "$worktree_path"
    git status --short --branch
    
    # Show recent commits
    echo -e "\n${YELLOW}Recent Commits:${NC}"
    git log --oneline -5
}

# Function to clean all worktrees
clean_all_worktrees() {
    echo -e "${RED}Warning: This will remove all agent worktrees!${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git worktree list --porcelain | grep "^worktree.*agent-" | cut -d' ' -f2 | while read path; do
            agent=$(basename "$path" | sed 's/agent-//')
            remove_worktree "$agent"
        done
        echo -e "${GREEN}✓ All agent worktrees removed${NC}"
    else
        echo -e "${YELLOW}Operation cancelled${NC}"
    fi
}

# Function to setup worktrees for all configured agents
setup_all_worktrees() {
    echo -e "${CYAN}Setting up worktrees for all configured agents...${NC}"
    
    local agents=($(get_configured_agents))
    local total=${#agents[@]}
    local count=0
    
    for agent in "${agents[@]}"; do
        ((count++))
        echo -e "\n${BLUE}[$count/$total] Creating worktree for agent: $agent${NC}"
        create_worktree "$agent"
    done
    
    echo -e "\n${GREEN}✓ All worktrees created successfully!${NC}"
    list_worktrees
}

# Function to sync worktree with main branch
sync_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    local branch_name="agent/$agent"
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    if ! git worktree list | grep -q "$worktree_path"; then
        echo -e "${RED}No worktree found for agent '$agent'${NC}"
        exit 1
    fi
    
    echo -e "${CYAN}Syncing worktree for agent '$agent' with main branch...${NC}"
    
    # Save current directory
    local current_dir=$(pwd)
    
    # Switch to worktree
    cd "$worktree_path"
    
    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo -e "${YELLOW}Warning: Uncommitted changes in worktree${NC}"
        git status --short
        read -p "Stash changes and continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash push -m "Auto-stash before sync"
        else
            echo -e "${RED}Sync cancelled${NC}"
            cd "$current_dir"
            return 1
        fi
    fi
    
    # Fetch latest changes
    git fetch origin main
    
    # Merge or rebase
    echo -e "${BLUE}Merging main into $branch_name...${NC}"
    if git merge origin/main; then
        echo -e "${GREEN}✓ Successfully synced with main${NC}"
    else
        echo -e "${RED}Merge conflicts detected. Please resolve manually.${NC}"
        cd "$current_dir"
        return 1
    fi
    
    # Return to original directory
    cd "$current_dir"
}

# Main command handling
case "$1" in
    create)
        create_worktree "$2"
        ;;
    remove)
        remove_worktree "$2"
        ;;
    list)
        list_worktrees
        ;;
    status)
        show_status "$2"
        ;;
    clean)
        clean_all_worktrees
        ;;
    setup-all)
        setup_all_worktrees
        ;;
    sync)
        sync_worktree "$2"
        ;;
    *)
        usage
        ;;
esac