# High Confidence Removal - Reasons

These files can be removed with high confidence because they have been replaced or are no longer needed.

## Files and Reasons

### AUTHORITY_MATRIX.md
- **Reason**: Replaced by DYNAMIC_AUTHORITY_SYSTEM.md
- **Details**: The old fixed 6-role authority system has been completely replaced by the dynamic task-based system

### update_agents_with_authority.py
- **Reason**: Replaced by dynamic_authority_manager.py
- **Details**: This script updated agents with fixed authority roles. No longer needed with dynamic assignment

### authority_role_mappings.json
- **Reason**: Obsolete with dynamic authority system
- **Details**: Contained fixed role-to-authority mappings that are now dynamically assigned

### authority_lifecycle_integration.py
- **Reason**: Functionality integrated into dynamic_authority_manager.py
- **Details**: The lifecycle integration is now handled by the dynamic system

### AGENT_PROMPT_TEMPLATE_WITH_AUTHORITY.md
- **Reason**: Replaced by AGENT_PROMPT_TEMPLATE_GENERIC.md
- **Details**: The new generic template handles all agents without fixed authorities

### manage_agents_original.sh
- **Reason**: Backup file of old version
- **Details**: This was kept as a backup when manage_agents.sh was updated

### Agent-specific prompt files (AGENT_*_PROMPT.md)
- **Reason**: Should be regenerated using generate_agents_dynamic.sh
- **Details**: These contain old fixed-role assignments and should be regenerated with the new system
- **Files**:
  - AGENT_SHARK_PROMPT.md
  - AGENT_DOLPHIN_PROMPT.md
  - AGENT_WHALE_PROMPT.md
  - AGENT_OCTOPUS_PROMPT.md
  - AGENT_SEAHORSE_PROMPT.md
  - AGENT_JELLYFISH_PROMPT.md