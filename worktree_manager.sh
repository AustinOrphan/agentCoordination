#!/bin/bash

# Enhanced Git Worktree Manager for Multi-Agent Coordination System
# This script manages git worktrees for parallel agent execution with advanced features
# Based on best practices from git-scm.com/docs/git-worktree

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_BASE_DIR="$(dirname "$REPO_ROOT")"

# Check git version for worktree support
check_git_version() {
    local git_version=$(git --version | awk '{print $3}')
    local min_version="2.28.0"
    
    if [ "$(printf '%s\n' "$min_version" "$git_version" | sort -V | head -n1)" != "$min_version" ]; then
        echo -e "${YELLOW}Warning: Git version $git_version detected. Recommended: 2.28+${NC}"
        echo -e "${YELLOW}Some worktree features may not be available.${NC}"
    fi
}

# Function to display usage
usage() {
    echo -e "${CYAN}Enhanced Git Worktree Manager for Agent Coordination${NC}"
    echo -e "${GREEN}Usage:${NC} $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${BLUE}create <agent>${NC}     Create a worktree for the specified agent"
    echo -e "  ${BLUE}remove <agent>${NC}     Remove the worktree for the specified agent"
    echo -e "  ${BLUE}list${NC}               List all agent worktrees with detailed status"
    echo -e "  ${BLUE}status <agent>${NC}     Show detailed status of agent's worktree"
    echo -e "  ${BLUE}clean${NC}              Remove all agent worktrees"
    echo -e "  ${BLUE}setup-all${NC}          Create worktrees for all configured agents"
    echo -e "  ${BLUE}sync <agent>${NC}       Sync agent's worktree with main branch"
    echo -e "  ${BLUE}lock <agent>${NC}       Lock worktree to prevent removal"
    echo -e "  ${BLUE}unlock <agent>${NC}     Unlock worktree to allow removal"
    echo -e "  ${BLUE}repair <agent>${NC}     Repair worktree if moved or corrupted"
    echo -e "  ${BLUE}prune${NC}              Clean up stale worktree references"
    echo -e "  ${BLUE}config <agent>${NC}     Configure worktree-specific settings"
    echo -e "  ${BLUE}health-check${NC}       Check health of all worktrees"
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

# Check if worktree is clean (no uncommitted changes)
is_worktree_clean() {
    local worktree_path=$1
    
    if [[ ! -d "$worktree_path" ]]; then
        return 1
    fi
    
    # Check for uncommitted changes
    if git -C "$worktree_path" diff --quiet && git -C "$worktree_path" diff --cached --quiet; then
        # Check for untracked files
        if [[ -z $(git -C "$worktree_path" ls-files --others --exclude-standard) ]]; then
            return 0
        fi
    fi
    
    return 1
}

# Function to create a worktree for an agent with enhanced features
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
    
    # Enable worktree config if supported
    if git config --get extensions.worktreeConfig >/dev/null 2>&1 || git config extensions.worktreeConfig true; then
        echo -e "${BLUE}Enabling worktree-specific configuration${NC}"
        
        # Set agent-specific git config
        git -C "$worktree_path" config user.name "Agent $agent"
        git -C "$worktree_path" config user.email "agent-$agent@coordination.local"
    fi
    
    # Copy agent-specific files to worktree
    local agent_upper=$(echo "$agent" | tr '[:lower:]' '[:upper:]')
    if [[ -f "$REPO_ROOT/AGENT_${agent_upper}_PROMPT.md" ]]; then
        cp "$REPO_ROOT/AGENT_${agent_upper}_PROMPT.md" "$worktree_path/"
        echo -e "${GREEN}✓ Copied agent prompt file${NC}"
    fi
    
    # Create agent-specific directories
    mkdir -p "$worktree_path/agent_workspace"
    mkdir -p "$worktree_path/agent_logs"
    
    # Create initial README for the agent
    cat > "$worktree_path/agent_workspace/README.md" << EOF
# Agent $agent Workspace

This is the dedicated workspace for Agent $agent.

## Branch: $branch_name
## Created: $(date)

## Agent Information
- Worktree Path: $worktree_path
- Branch: $branch_name
- Status: Active

## Usage
This workspace is managed by the Multi-Agent Coordination System.
All agent-specific work should be performed in this directory.
EOF
    
    # Update agent status with worktree info
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        jq --arg path "$worktree_path" \
           --arg branch "$branch_name" \
           --arg created "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
            '. + {"worktree": {"path": $path, "branch": $branch, "created": $created, "locked": false}}' \
            "$REPO_ROOT/agent_status/${agent}_status.json" > \
            "$REPO_ROOT/agent_status/${agent}_status.json.tmp" && \
        mv "$REPO_ROOT/agent_status/${agent}_status.json.tmp" \
           "$REPO_ROOT/agent_status/${agent}_status.json"
    fi
    
    # Initialize dependencies if package.json exists
    if [[ -f "$REPO_ROOT/package.json" ]]; then
        echo -e "${BLUE}Installing dependencies in worktree...${NC}"
        cp "$REPO_ROOT/package.json" "$worktree_path/" 2>/dev/null || true
        cp "$REPO_ROOT/package-lock.json" "$worktree_path/" 2>/dev/null || true
        
        if command -v npm &> /dev/null; then
            (cd "$worktree_path" && npm install --quiet) &
            echo -e "${YELLOW}Note: Dependencies installing in background${NC}"
        fi
    fi
}

# Enhanced remove function with safety checks
remove_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    local force=false
    
    if [[ "$2" == "--force" ]]; then
        force=true
    fi
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    if ! git worktree list | grep -q "$worktree_path"; then
        echo -e "${YELLOW}No worktree found for agent '$agent'${NC}"
        return 0
    fi
    
    # Check if worktree is locked
    if git worktree list --porcelain | grep -A1 "$worktree_path" | grep -q "locked"; then
        echo -e "${RED}Error: Worktree for agent '$agent' is locked${NC}"
        echo -e "${YELLOW}Use 'unlock' command first or --force flag${NC}"
        if [[ "$force" != true ]]; then
            exit 1
        fi
    fi
    
    # Check if worktree is clean
    if ! is_worktree_clean "$worktree_path" && [[ "$force" != true ]]; then
        echo -e "${RED}Error: Worktree has uncommitted changes${NC}"
        echo -e "${YELLOW}Please commit or stash changes first, or use --force${NC}"
        git -C "$worktree_path" status --short
        exit 1
    fi
    
    echo -e "${YELLOW}Removing worktree for agent '$agent'...${NC}"
    
    if [[ "$force" == true ]]; then
        git worktree remove --force "$worktree_path" 2>/dev/null || true
    else
        git worktree remove "$worktree_path"
    fi
    
    # Update agent status to remove worktree info
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        jq 'del(.worktree)' "$REPO_ROOT/agent_status/${agent}_status.json" > \
            "$REPO_ROOT/agent_status/${agent}_status.json.tmp" && \
        mv "$REPO_ROOT/agent_status/${agent}_status.json.tmp" \
           "$REPO_ROOT/agent_status/${agent}_status.json"
    fi
    
    echo -e "${GREEN}✓ Worktree removed for agent '$agent'${NC}"
}

# Lock worktree to prevent removal
lock_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    local reason="${2:-Locked by coordination system}"
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    if ! git worktree list | grep -q "$worktree_path"; then
        echo -e "${RED}No worktree found for agent '$agent'${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Locking worktree for agent '$agent'...${NC}"
    git worktree lock "$worktree_path" --reason "$reason"
    
    # Update agent status
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        jq --arg reason "$reason" \
            '.worktree.locked = true | .worktree.lock_reason = $reason' \
            "$REPO_ROOT/agent_status/${agent}_status.json" > \
            "$REPO_ROOT/agent_status/${agent}_status.json.tmp" && \
        mv "$REPO_ROOT/agent_status/${agent}_status.json.tmp" \
           "$REPO_ROOT/agent_status/${agent}_status.json"
    fi
    
    echo -e "${GREEN}✓ Worktree locked for agent '$agent'${NC}"
}

# Unlock worktree to allow removal
unlock_worktree() {
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
    
    echo -e "${BLUE}Unlocking worktree for agent '$agent'...${NC}"
    git worktree unlock "$worktree_path"
    
    # Update agent status
    if [[ -f "$REPO_ROOT/agent_status/${agent}_status.json" ]]; then
        jq '.worktree.locked = false | del(.worktree.lock_reason)' \
            "$REPO_ROOT/agent_status/${agent}_status.json" > \
            "$REPO_ROOT/agent_status/${agent}_status.json.tmp" && \
        mv "$REPO_ROOT/agent_status/${agent}_status.json.tmp" \
           "$REPO_ROOT/agent_status/${agent}_status.json"
    fi
    
    echo -e "${GREEN}✓ Worktree unlocked for agent '$agent'${NC}"
}

# Enhanced list function with detailed status
list_worktrees() {
    echo -e "${CYAN}Agent Worktrees Status:${NC}"
    echo -e "${BLUE}========================${NC}"
    
    # Header
    printf "${YELLOW}%-12s %-35s %-20s %-8s %-10s${NC}\n" "AGENT" "PATH" "BRANCH" "LOCKED" "STATUS"
    echo -e "${BLUE}------------------------------------------------------------------------${NC}"
    
    # Get all worktrees with details
    git worktree list --porcelain | awk -v red="$RED" -v green="$GREEN" -v yellow="$YELLOW" -v nc="$NC" '
        /^worktree/ { 
            path = $2
            # Check if this is an agent worktree
            if (match(path, /agent-([a-zA-Z_]+)/, m)) {
                agent = m[1]
                worktrees[agent] = path
            }
        }
        /^HEAD/ && agent {
            heads[agent] = substr($2, 1, 8)
        }
        /^branch/ && agent {
            branches[agent] = $2
        }
        /^locked/ && agent {
            locked[agent] = "Yes"
            getline
            if (/^reason/) {
                lock_reasons[agent] = substr($0, 8)
            }
        }
        /^prunable/ && agent {
            prunable[agent] = "Stale"
        }
        /^detached/ && agent {
            detached[agent] = "Detached"
        }
        END {
            for (a in worktrees) {
                # Determine status color
                status = "Active"
                color = green
                if (prunable[a]) {
                    status = prunable[a]
                    color = red
                } else if (detached[a]) {
                    status = detached[a]
                    color = yellow
                }
                
                lock_status = locked[a] ? locked[a] : "No"
                lock_color = locked[a] ? yellow : green
                
                # Truncate path if too long
                path_display = worktrees[a]
                if (length(path_display) > 33) {
                    path_display = "..." substr(path_display, length(path_display) - 30)
                }
                
                branch_display = branches[a] ? branches[a] : heads[a]
                if (length(branch_display) > 18) {
                    branch_display = substr(branch_display, 1, 15) "..."
                }
                
                printf "%-12s %-35s %-20s %s%-8s%s %s%-10s%s\n", 
                       toupper(a), path_display, branch_display, 
                       lock_color, lock_status, nc,
                       color, status, nc
                       
                if (lock_reasons[a]) {
                    printf "%-12s   Reason: %s\n", "", lock_reasons[a]
                }
            }
        }
    '
    
    # Summary statistics
    echo -e "\n${CYAN}Summary:${NC}"
    local total=$(git worktree list | grep -c "agent-" || echo "0")
    local locked=$(git worktree list --porcelain | grep -B1 "^locked" | grep -c "agent-" || echo "0")
    local active=$((total - locked))
    
    echo -e "${GREEN}Total worktrees: $total${NC}"
    echo -e "${GREEN}Active: $active${NC}"
    echo -e "${YELLOW}Locked: $locked${NC}"
}

# Repair worktree if moved or corrupted
repair_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    local new_path="${2:-$worktree_path}"
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Repairing worktree for agent '$agent'...${NC}"
    
    # Try to repair
    if git worktree repair "$worktree_path" "$new_path" 2>/dev/null; then
        echo -e "${GREEN}✓ Worktree repaired successfully${NC}"
    else
        echo -e "${YELLOW}Standard repair failed, attempting manual repair...${NC}"
        
        # Manual repair by removing and recreating
        remove_worktree "$agent" --force
        create_worktree "$agent"
    fi
}

# Prune stale worktree references
prune_worktrees() {
    echo -e "${BLUE}Pruning stale worktree references...${NC}"
    
    # Dry run first
    echo -e "${YELLOW}Checking for stale worktrees:${NC}"
    git worktree list --porcelain | grep -B1 "^prunable" | grep "^worktree" | while read -r _ path; do
        echo -e "${RED}  - $path (stale)${NC}"
    done
    
    # Actual prune
    git worktree prune -v
    
    echo -e "${GREEN}✓ Worktree pruning complete${NC}"
}

# Configure worktree-specific settings
configure_worktree() {
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
    
    echo -e "${CYAN}Configuring worktree for agent '$agent'${NC}"
    
    # Enable worktree config
    git config extensions.worktreeConfig true
    
    # Set agent-specific configurations
    git -C "$worktree_path" config user.name "Agent $agent"
    git -C "$worktree_path" config user.email "agent-$agent@coordination.local"
    git -C "$worktree_path" config core.commentChar "#"
    git -C "$worktree_path" config merge.conflictStyle "diff3"
    
    # Set agent-specific hooks path if needed
    if [[ -d "$REPO_ROOT/.git/hooks" ]]; then
        mkdir -p "$worktree_path/.git/hooks"
        echo -e "${BLUE}Note: Hooks are shared across worktrees${NC}"
    fi
    
    echo -e "${GREEN}✓ Worktree configuration complete${NC}"
    
    # Show current config
    echo -e "\n${YELLOW}Current worktree-specific config:${NC}"
    git -C "$worktree_path" config --local --list | grep -E "^(user|core|merge)\."
}

# Health check for all worktrees
health_check() {
    echo -e "${CYAN}Performing health check on all agent worktrees...${NC}"
    echo -e "${BLUE}================================================${NC}"
    
    local agents=($(get_configured_agents))
    local healthy=0
    local unhealthy=0
    local missing=0
    
    for agent in "${agents[@]}"; do
        local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
        echo -e "\n${BLUE}Checking agent: $agent${NC}"
        
        # Check if worktree exists
        if ! git worktree list | grep -q "$worktree_path"; then
            echo -e "${RED}  ✗ Worktree missing${NC}"
            ((missing++))
            continue
        fi
        
        # Check if path exists
        if [[ ! -d "$worktree_path" ]]; then
            echo -e "${RED}  ✗ Worktree path missing (needs repair)${NC}"
            ((unhealthy++))
            continue
        fi
        
        # Check if git directory is valid
        if ! git -C "$worktree_path" rev-parse --git-dir >/dev/null 2>&1; then
            echo -e "${RED}  ✗ Invalid git directory (needs repair)${NC}"
            ((unhealthy++))
            continue
        fi
        
        # Check for uncommitted changes
        if is_worktree_clean "$worktree_path"; then
            echo -e "${GREEN}  ✓ Clean working directory${NC}"
        else
            echo -e "${YELLOW}  ⚠ Has uncommitted changes${NC}"
        fi
        
        # Check branch status
        local branch=$(git -C "$worktree_path" branch --show-current)
        if [[ -n "$branch" ]]; then
            echo -e "${GREEN}  ✓ On branch: $branch${NC}"
        else
            echo -e "${YELLOW}  ⚠ Detached HEAD state${NC}"
        fi
        
        # Check lock status
        if git worktree list --porcelain | grep -A1 "$worktree_path" | grep -q "locked"; then
            echo -e "${YELLOW}  ⚠ Worktree is locked${NC}"
        else
            echo -e "${GREEN}  ✓ Worktree is unlocked${NC}"
        fi
        
        ((healthy++))
    done
    
    # Summary
    echo -e "\n${CYAN}Health Check Summary:${NC}"
    echo -e "${GREEN}Healthy: $healthy${NC}"
    echo -e "${YELLOW}Unhealthy: $unhealthy${NC}"
    echo -e "${RED}Missing: $missing${NC}"
    
    if [[ $unhealthy -gt 0 ]]; then
        echo -e "\n${YELLOW}Run 'repair' command for unhealthy worktrees${NC}"
    fi
    
    if [[ $missing -gt 0 ]]; then
        echo -e "\n${YELLOW}Run 'setup-all' to create missing worktrees${NC}"
    fi
}

# Enhanced status function
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
    
    echo -e "${CYAN}Detailed Status for Agent $agent:${NC}"
    echo -e "${BLUE}===================================${NC}"
    
    # Worktree info
    echo -e "\n${YELLOW}Worktree Information:${NC}"
    git worktree list | grep "$worktree_path" | while read line; do
        echo -e "  $line"
    done
    
    # Lock status
    if git worktree list --porcelain | grep -A2 "$worktree_path" | grep -q "locked"; then
        echo -e "\n${YELLOW}Lock Status: LOCKED${NC}"
        local reason=$(git worktree list --porcelain | grep -A2 "$worktree_path" | grep "^reason" | cut -d' ' -f2-)
        [[ -n "$reason" ]] && echo -e "  Reason: $reason"
    else
        echo -e "\n${GREEN}Lock Status: Unlocked${NC}"
    fi
    
    # Git status
    echo -e "\n${YELLOW}Git Status:${NC}"
    git -C "$worktree_path" status --short --branch
    
    # Uncommitted changes
    local changes=$(git -C "$worktree_path" status --porcelain | wc -l)
    if [[ $changes -gt 0 ]]; then
        echo -e "\n${YELLOW}Uncommitted changes: $changes files${NC}"
    else
        echo -e "\n${GREEN}Working directory clean${NC}"
    fi
    
    # Recent commits
    echo -e "\n${YELLOW}Recent Commits:${NC}"
    git -C "$worktree_path" log --oneline --graph -5
    
    # Disk usage
    if command -v du &> /dev/null; then
        echo -e "\n${YELLOW}Disk Usage:${NC}"
        du -sh "$worktree_path" 2>/dev/null | awk '{print "  Total: " $1}'
    fi
    
    # Configuration
    echo -e "\n${YELLOW}Worktree Configuration:${NC}"
    git -C "$worktree_path" config --local --list | grep -E "^(user|core)\." | while read line; do
        echo -e "  $line"
    done
}

# Enhanced sync function
sync_worktree() {
    local agent=$1
    local worktree_path="$WORKTREE_BASE_DIR/agent-$agent"
    local branch_name="agent/$agent"
    local strategy="${2:-merge}"  # merge or rebase
    
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
    if ! is_worktree_clean "$worktree_path"; then
        echo -e "${YELLOW}Warning: Uncommitted changes detected${NC}"
        git status --short
        
        read -p "Stash changes and continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash push -m "Auto-stash before sync at $(date)"
            echo -e "${GREEN}✓ Changes stashed${NC}"
        else
            echo -e "${RED}Sync cancelled${NC}"
            cd "$current_dir"
            return 1
        fi
    fi
    
    # Fetch latest changes
    echo -e "${BLUE}Fetching latest changes...${NC}"
    git fetch origin main
    
    # Show divergence
    local behind=$(git rev-list --count HEAD..origin/main)
    local ahead=$(git rev-list --count origin/main..HEAD)
    
    echo -e "${CYAN}Branch status:${NC}"
    echo -e "  Behind main: ${YELLOW}$behind${NC} commits"
    echo -e "  Ahead of main: ${GREEN}$ahead${NC} commits"
    
    if [[ $behind -eq 0 ]]; then
        echo -e "${GREEN}✓ Already up to date with main${NC}"
        cd "$current_dir"
        return 0
    fi
    
    # Perform sync based on strategy
    if [[ "$strategy" == "rebase" ]]; then
        echo -e "${BLUE}Rebasing onto main...${NC}"
        if git rebase origin/main; then
            echo -e "${GREEN}✓ Successfully rebased onto main${NC}"
        else
            echo -e "${RED}Rebase conflicts detected. Resolve manually and run:${NC}"
            echo -e "${YELLOW}  git rebase --continue${NC}"
            cd "$current_dir"
            return 1
        fi
    else
        echo -e "${BLUE}Merging main into $branch_name...${NC}"
        if git merge origin/main -m "Merge main into $branch_name"; then
            echo -e "${GREEN}✓ Successfully merged with main${NC}"
        else
            echo -e "${RED}Merge conflicts detected. Resolve manually and run:${NC}"
            echo -e "${YELLOW}  git commit${NC}"
            cd "$current_dir"
            return 1
        fi
    fi
    
    # Check if stash exists and offer to pop it
    if git stash list | grep -q "Auto-stash before sync"; then
        read -p "Pop stashed changes? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash pop
            echo -e "${GREEN}✓ Stashed changes restored${NC}"
        fi
    fi
    
    # Return to original directory
    cd "$current_dir"
}

# Enhanced setup all function
setup_all_worktrees() {
    echo -e "${CYAN}Setting up worktrees for all configured agents...${NC}"
    
    # Check git version first
    check_git_version
    
    local agents=($(get_configured_agents))
    local total=${#agents[@]}
    local count=0
    local success=0
    local failed=0
    
    echo -e "${BLUE}Found $total agents in configuration${NC}"
    
    for agent in "${agents[@]}"; do
        ((count++))
        echo -e "\n${BLUE}[$count/$total] Processing agent: $agent${NC}"
        
        if create_worktree "$agent"; then
            ((success++))
        else
            ((failed++))
            echo -e "${RED}  ✗ Failed to create worktree for $agent${NC}"
        fi
    done
    
    echo -e "\n${GREEN}Setup complete!${NC}"
    echo -e "${GREEN}Success: $success${NC}"
    [[ $failed -gt 0 ]] && echo -e "${RED}Failed: $failed${NC}"
    
    # Show final status
    echo ""
    list_worktrees
}

# Enhanced clean function
clean_all_worktrees() {
    echo -e "${RED}Warning: This will remove all agent worktrees!${NC}"
    
    # Show what will be removed
    echo -e "\n${YELLOW}The following worktrees will be removed:${NC}"
    git worktree list | grep "agent-" | while read line; do
        echo -e "  - $line"
    done
    
    read -p "Are you sure? (yes/N) " -r
    echo
    
    if [[ $REPLY == "yes" ]]; then
        local count=0
        git worktree list --porcelain | grep "^worktree.*agent-" | cut -d' ' -f2 | while read path; do
            agent=$(basename "$path" | sed 's/agent-//')
            echo -e "${YELLOW}Removing worktree for agent: $agent${NC}"
            
            # Force remove even if locked or has changes
            remove_worktree "$agent" --force
            ((count++))
        done
        
        # Prune any remaining references
        git worktree prune
        
        echo -e "${GREEN}✓ All agent worktrees removed${NC}"
    else
        echo -e "${YELLOW}Operation cancelled${NC}"
    fi
}

# Main command handling
check_git_version

case "$1" in
    create)
        create_worktree "$2"
        ;;
    remove)
        remove_worktree "$2" "$3"
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
        sync_worktree "$2" "$3"
        ;;
    lock)
        lock_worktree "$2" "$3"
        ;;
    unlock)
        unlock_worktree "$2"
        ;;
    repair)
        repair_worktree "$2" "$3"
        ;;
    prune)
        prune_worktrees
        ;;
    config)
        configure_worktree "$2"
        ;;
    health-check)
        health_check
        ;;
    *)
        usage
        ;;
esac