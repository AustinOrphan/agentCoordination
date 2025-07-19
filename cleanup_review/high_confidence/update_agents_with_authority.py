#!/usr/bin/env python3
"""
Update agent prompt files to include authority information from the Authority Matrix.
"""

import json
import os
import glob

def load_authority_mappings():
    """Load the authority role mappings."""
    with open('authority_role_mappings.json', 'r') as f:
        return json.load(f)

def load_agent_config():
    """Load the current agent configuration."""
    with open('agent_config.json', 'r') as f:
        return json.load(f)

def get_position_authority(position):
    """Get authority information for a given position (1-6)."""
    mappings = load_authority_mappings()
    return mappings['role_authorities'].get(str(position), {})

def insert_authority_section(prompt_content, agent_name, position):
    """Insert authority section into agent prompt."""
    authority = get_position_authority(position)
    if not authority:
        return prompt_content
    
    # Create the authority section
    authority_section = f"""
## 🏛️ Your Authority Level

Based on your position as {authority['role']}, you have the following authorities:

### Primary Authorities
"""
    for auth in authority['primary_authorities']:
        authority_section += f"{auth}\n"
    
    authority_section += f"""
### Domain Authority
{authority['domain_authority']}

### Emergency Authority
{authority['emergency_authority']}

### Backup Responsibilities
"""
    for resp in authority['backup_responsibilities']:
        authority_section += f"{resp}\n"
    
    authority_section += """
### Decision Making Protocol
1. **Check Authority**: Before making any decision, verify you have the appropriate authority
2. **Document Source**: Always document your authority source (Primary/Backup/Emergency/Vote)
3. **Timeout Awareness**: Monitor for decisions requiring your backup authority
4. **Emergency Response**: Act immediately on domain emergencies within your authority

### Authority Documentation Format
```markdown
## Decision: [Title]
- **Decision ID**: DEC-2025-[XXX]
- **Authority Used**: [Primary/Backup-N/Emergency/Vote]
- **Authority Level**: [Strategic/Routine/Emergency/Domain]
- **Activation**: [Normal/Timeout/Emergency]
- **Rationale**: [Why this decision]
```
"""
    
    # Find insertion point after "Your Responsibilities" section
    lines = prompt_content.split('\n')
    insert_index = -1
    
    for i, line in enumerate(lines):
        if line.strip() == "## Your Responsibilities":
            # Find the next section or empty line
            for j in range(i+1, len(lines)):
                if lines[j].strip() == "" or lines[j].startswith("##"):
                    insert_index = j
                    break
            break
    
    if insert_index == -1:
        # If we couldn't find the right spot, insert after identity section
        for i, line in enumerate(lines):
            if "## Your Identity" in line:
                for j in range(i+1, len(lines)):
                    if lines[j].strip() == "" or lines[j].startswith("##"):
                        insert_index = j
                        break
                break
    
    if insert_index != -1:
        lines.insert(insert_index, authority_section)
        return '\n'.join(lines)
    
    return prompt_content

def update_agent_prompts():
    """Update all agent prompt files with authority information."""
    config = load_agent_config()
    current_theme = config['current_theme']
    agent_count = config['agent_count']
    theme_agents = config['themes'][current_theme]['agents']
    
    # Get the agents for the current count
    agents = theme_agents[:agent_count]
    
    updated_count = 0
    
    for i, agent_name in enumerate(agents):
        position = (i % 6) + 1  # Positions 1-6 cycle through roles
        agent_upper = agent_name.upper()
        
        prompt_file = f"AGENT_{agent_upper}_PROMPT.md"
        
        if os.path.exists(prompt_file):
            print(f"Updating {prompt_file} with authority for position {position}...")
            
            with open(prompt_file, 'r') as f:
                content = f.read()
            
            # Check if authority section already exists
            if "## 🏛️ Your Authority Level" in content:
                print(f"  Authority section already exists in {prompt_file}, skipping...")
                continue
            
            updated_content = insert_authority_section(content, agent_name, position)
            
            with open(prompt_file, 'w') as f:
                f.write(updated_content)
            
            updated_count += 1
            print(f"  ✓ Updated {prompt_file}")
    
    print(f"\nUpdated {updated_count} agent prompt files with authority information.")
    
    # Also update the generate_agents.sh script to include authority in future generations
    print("\nUpdating generate_agents.sh template...")
    update_generation_template()

def update_generation_template():
    """Update the agent generation template to include authority."""
    # Read the current generate_agents.sh
    with open('generate_agents.sh', 'r') as f:
        content = f.read()
    
    # Check if authority is already included
    if "Your Authority Level" in content:
        print("Authority already included in generation template.")
        return
    
    # Find the prompt generation section and add authority
    # This is a complex operation, so we'll create a marker for manual update
    marker_file = "UPDATE_GENERATE_AGENTS_MARKER.txt"
    with open(marker_file, 'w') as f:
        f.write("""Please manually update generate_agents.sh to include authority information.

Add the following after the "## Your Responsibilities" section in the agent prompt template:

## 🏛️ Your Authority Level

Based on your position as $agent_role, you have the following authorities:

[Authority information should be dynamically inserted based on position]

See AGENT_PROMPT_TEMPLATE_WITH_AUTHORITY.md for the complete template.
""")
    
    print(f"Created {marker_file} with instructions for updating generate_agents.sh")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    update_agent_prompts()