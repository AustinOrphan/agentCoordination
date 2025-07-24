#!/usr/bin/env python3
"""
Plan Integrator for Multi-Agent Coordination System

Integrates external deployment plans (MD/XML) with the dynamic agent generator.
Supports parsing deployment plans and injecting them into agent prompts.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import argparse

class PlanParser:
    """Parses deployment plans from various formats"""
    
    def __init__(self):
        self.supported_formats = ['.md', '.xml', '.json']
    
    def parse_markdown_plan(self, file_path: str) -> Dict:
        """Parse a Markdown deployment plan"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        plan = {
            'title': self._extract_title(content),
            'agent_role': self._extract_agent_role(content),
            'responsibilities': self._extract_responsibilities(content),
            'tasks': self._extract_tasks(content),
            'success_criteria': self._extract_success_criteria(content),
            'timeline': self._extract_timeline(content),
            'dependencies': self._extract_dependencies(content),
            'full_content': content,
            'source_file': file_path
        }
        
        return plan
    
    def parse_xml_plan(self, file_path: str) -> Dict:
        """Parse an XML deployment plan"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        plan = {
            'title': self._get_xml_text(root, 'title', ''),
            'agent_role': self._get_xml_text(root, 'agent_role', ''),
            'responsibilities': self._get_xml_list(root, 'responsibilities/item'),
            'tasks': self._get_xml_tasks(root),
            'success_criteria': self._get_xml_list(root, 'success_criteria/criterion'),
            'timeline': self._get_xml_text(root, 'timeline', ''),
            'dependencies': self._get_xml_list(root, 'dependencies/dependency'),
            'full_content': ET.tostring(root, encoding='unicode'),
            'source_file': file_path
        }
        
        return plan
    
    def parse_json_plan(self, file_path: str) -> Dict:
        """Parse a JSON deployment plan"""
        with open(file_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        plan['source_file'] = file_path
        return plan
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        return title_match.group(1).strip() if title_match else "Deployment Plan"
    
    def _extract_agent_role(self, content: str) -> str:
        """Extract agent role from markdown content"""
        role_patterns = [
            r'##\s+Agent\s+Role[:\s]*(.+?)(?=##|\n\n|\Z)',
            r'##\s+Role[:\s]*(.+?)(?=##|\n\n|\Z)',
            r'\*\*Agent[:\s]*(.+?)(?=\*\*|\n|\Z)',
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Multi-Agent Specialist"
    
    def _extract_responsibilities(self, content: str) -> List[str]:
        """Extract responsibilities from markdown content"""
        resp_match = re.search(r'##\s+Responsibilities[:\s]*(.+?)(?=##|\Z)', content, 
                              re.MULTILINE | re.DOTALL | re.IGNORECASE)
        
        if not resp_match:
            return []
        
        resp_text = resp_match.group(1).strip()
        responsibilities = []
        
        # Extract bullet points
        for line in resp_text.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')):
                responsibilities.append(line[2:].strip())
            elif re.match(r'^\d+\.\s+', line):
                responsibilities.append(re.sub(r'^\d+\.\s+', '', line).strip())
        
        return responsibilities
    
    def _extract_tasks(self, content: str) -> List[Dict]:
        """Extract tasks from markdown content"""
        tasks = []
        
        # Look for task sections
        task_patterns = [
            r'##\s+Tasks?[:\s]*(.+?)(?=##|\Z)',
            r'##\s+Implementation[:\s]*(.+?)(?=##|\Z)',
            r'##\s+Phase\s+\d+[:\s]*(.+?)(?=##|\Z)'
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip()
                task = {
                    'description': task_text,
                    'subtasks': self._extract_subtasks(task_text)
                }
                tasks.append(task)
        
        return tasks
    
    def _extract_subtasks(self, task_text: str) -> List[str]:
        """Extract subtasks from task text"""
        subtasks = []
        for line in task_text.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')):
                subtasks.append(line[2:].strip())
            elif re.match(r'^\d+\.\s+', line):
                subtasks.append(re.sub(r'^\d+\.\s+', '', line).strip())
        return subtasks
    
    def _extract_success_criteria(self, content: str) -> List[str]:
        """Extract success criteria from markdown content"""
        criteria_match = re.search(r'##\s+Success\s+Criteria[:\s]*(.+?)(?=##|\Z)', content, 
                                  re.MULTILINE | re.DOTALL | re.IGNORECASE)
        
        if not criteria_match:
            return []
        
        criteria_text = criteria_match.group(1).strip()
        criteria = []
        
        for line in criteria_text.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ', '✅')):
                criteria.append(line[2:].strip() if not line.startswith('✅') else line[2:].strip())
        
        return criteria
    
    def _extract_timeline(self, content: str) -> str:
        """Extract timeline from markdown content"""
        timeline_match = re.search(r'##\s+Timeline[:\s]*(.+?)(?=##|\n\n|\Z)', content, 
                                  re.MULTILINE | re.DOTALL | re.IGNORECASE)
        return timeline_match.group(1).strip() if timeline_match else ""
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from markdown content"""
        dep_match = re.search(r'##\s+Dependencies[:\s]*(.+?)(?=##|\Z)', content, 
                             re.MULTILINE | re.DOTALL | re.IGNORECASE)
        
        if not dep_match:
            return []
        
        dep_text = dep_match.group(1).strip()
        dependencies = []
        
        for line in dep_text.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')):
                dependencies.append(line[2:].strip())
        
        return dependencies
    
    def _get_xml_text(self, root: ET.Element, path: str, default: str = "") -> str:
        """Get text content from XML element"""
        element = root.find(path)
        return element.text if element is not None and element.text else default
    
    def _get_xml_list(self, root: ET.Element, path: str) -> List[str]:
        """Get list of text content from XML elements"""
        elements = root.findall(path)
        return [elem.text for elem in elements if elem.text]
    
    def _get_xml_tasks(self, root: ET.Element) -> List[Dict]:
        """Get tasks from XML structure"""
        tasks = []
        task_elements = root.findall('tasks/task')
        
        for task_elem in task_elements:
            task = {
                'description': self._get_xml_text(task_elem, 'description'),
                'subtasks': self._get_xml_list(task_elem, 'subtasks/subtask')
            }
            tasks.append(task)
        
        return tasks

class PlanIntegrator:
    """Integrates parsed plans with the dynamic agent system"""
    
    def __init__(self, agent_config_path: str = "agent_config.json"):
        self.agent_config_path = agent_config_path
        self.parser = PlanParser()
    
    def integrate_plans(self, plan_directory: str, agent_count: Optional[int] = None) -> Dict:
        """Integrate plans from a directory with the dynamic agent system"""
        
        # Discover plan files
        plan_files = self._discover_plans(plan_directory)
        
        if not plan_files:
            raise ValueError(f"No valid plan files found in {plan_directory}")
        
        # Parse all plans
        parsed_plans = []
        for plan_file in plan_files:
            plan = self._parse_plan_file(plan_file)
            parsed_plans.append(plan)
        
        # Get current agent configuration
        current_config = self._load_agent_config()
        
        # Determine agent assignment
        if agent_count is None:
            agent_count = min(len(parsed_plans), current_config.get('agent_count', 6))
        
        # Assign plans to agents
        agent_assignments = self._assign_plans_to_agents(parsed_plans, agent_count, current_config)
        
        return {
            'parsed_plans': parsed_plans,
            'agent_assignments': agent_assignments,
            'agent_count': agent_count,
            'plan_directory': plan_directory
        }
    
    def generate_enhanced_prompts(self, integration_result: Dict) -> Dict[str, str]:
        """Generate enhanced agent prompts with integrated plans"""
        
        agent_assignments = integration_result['agent_assignments']
        enhanced_prompts = {}
        
        for agent_id, assignment in agent_assignments.items():
            base_prompt = self._load_base_dynamic_prompt()
            
            # Inject plan-specific content
            enhanced_prompt = self._enhance_prompt_with_plan(base_prompt, assignment)
            
            enhanced_prompts[agent_id] = enhanced_prompt
        
        return enhanced_prompts
    
    def _discover_plans(self, directory: str) -> List[str]:
        """Discover plan files in directory"""
        plan_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file.lower().endswith(ext) for ext in self.parser.supported_formats):
                    plan_files.append(file_path)
        
        # Sort by filename for consistent ordering
        return sorted(plan_files)
    
    def _parse_plan_file(self, file_path: str) -> Dict:
        """Parse a single plan file based on its extension"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.md':
            return self.parser.parse_markdown_plan(file_path)
        elif ext == '.xml':
            return self.parser.parse_xml_plan(file_path)
        elif ext == '.json':
            return self.parser.parse_json_plan(file_path)
        else:
            raise ValueError(f"Unsupported plan format: {ext}")
    
    def _load_agent_config(self) -> Dict:
        """Load current agent configuration"""
        try:
            with open(self.agent_config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'current_theme': 'greek_letters', 'agent_count': 6}
    
    def _assign_plans_to_agents(self, plans: List[Dict], agent_count: int, config: Dict) -> Dict:
        """Assign plans to agents based on current configuration"""
        
        # Get agent names from current theme
        theme_name = config.get('current_theme', 'greek_letters')
        themes = config.get('themes', {})
        
        if theme_name in themes:
            agent_names = themes[theme_name].get('agents', [])[:agent_count]
        else:
            # Fallback to generic names
            agent_names = [f"agent_{i+1}" for i in range(agent_count)]
        
        assignments = {}
        
        # Assign plans to agents (round-robin if more agents than plans)
        for i, agent_name in enumerate(agent_names):
            if i < len(plans):
                assignments[agent_name] = plans[i]
            else:
                # If more agents than plans, assign to master coordination role
                assignments[agent_name] = {
                    'title': f'Support Agent {agent_name}',
                    'agent_role': 'Support Specialist',
                    'responsibilities': ['Support other agents', 'Handle overflow tasks'],
                    'tasks': [{'description': 'Assist with coordination and overflow work'}],
                    'success_criteria': ['All team goals achieved'],
                    'timeline': 'As needed',
                    'dependencies': ['Primary agents']
                }
        
        return assignments
    
    def _load_base_dynamic_prompt(self) -> str:
        """Load the base dynamic prompt template"""
        # This would be the content from generate_agents_dynamic.sh template
        return """# Agent {{AGENT_NAME}}

You are Agent {{AGENT_NAME}}, part of a dynamic multi-agent coordination system.

## Your Identity
- **Agent Name**: {{AGENT_NAME}}
- **Agent ID**: {{AGENT_ID}}
- **System Status**: Active agents will be communicated to you

## Your Specialized Assignment

{{PLAN_CONTENT}}

## Authority Protocol

### Using Your Authority
1. **Verify First**: Check that your action falls within your granted authorities
2. **Document Decisions**: Record authority used for all significant decisions
3. **Stay in Scope**: Only use authority within your assigned domain

### When You Need Authority You Don't Have
1. **Check Authority Pool**: See which agent currently holds needed authority
2. **Request Collaboration**: Initiate joint decision with authority holder
3. **Emergency Override**: Only for critical issues with no response

## Collaboration Framework

### Communication Protocol
- **Inbox**: `agent_communication/{{AGENT_ID}}/input/inbox.json`
- **Outbox**: `agent_communication/{{AGENT_ID}}/output/outbox.json`
- **Check Frequency**: Every 30 seconds
- **Heartbeat**: Send status every 30 seconds

## Git Worktree
You operate in your own git worktree:
- **Location**: `../agent-{{AGENT_ID}}`
- **Branch**: `agent/{{AGENT_ID}}`
- **Purpose**: Isolated workspace for parallel execution

## Initial Actions

1. **Initialize Communication**: Set up your communication channel
2. **Send Heartbeat**: Announce you're online
3. **Check Inbox**: Look for pending assignments
4. **Report Status**: Update your current state
5. **Begin Work**: Start on your specialized assignment

Remember: You are part of a flexible, adaptive team working on your specialized assignment while coordinating with others.
"""
    
    def _enhance_prompt_with_plan(self, base_prompt: str, plan: Dict) -> str:
        """Enhance base prompt with plan-specific content"""
        
        # Generate plan-specific content section
        plan_content = f"""### Your Role: {plan.get('agent_role', 'Specialist')}

### Responsibilities:
"""
        
        for resp in plan.get('responsibilities', []):
            plan_content += f"- {resp}\n"
        
        plan_content += "\n### Tasks:\n"
        for i, task in enumerate(plan.get('tasks', []), 1):
            plan_content += f"\n#### Task {i}:\n{task.get('description', '')}\n"
            
            if task.get('subtasks'):
                plan_content += "\n**Subtasks:**\n"
                for subtask in task['subtasks']:
                    plan_content += f"- {subtask}\n"
        
        if plan.get('success_criteria'):
            plan_content += "\n### Success Criteria:\n"
            for criterion in plan['success_criteria']:
                plan_content += f"- ✅ {criterion}\n"
        
        if plan.get('timeline'):
            plan_content += f"\n### Timeline: {plan['timeline']}\n"
        
        if plan.get('dependencies'):
            plan_content += "\n### Dependencies:\n"
            for dep in plan['dependencies']:
                plan_content += f"- {dep}\n"
        
        # Insert plan content into base prompt
        enhanced_prompt = base_prompt.replace('{{PLAN_CONTENT}}', plan_content)
        
        return enhanced_prompt

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Integrate external deployment plans with agent system')
    parser.add_argument('plan_directory', help='Directory containing deployment plans')
    parser.add_argument('--agent-count', type=int, help='Number of agents to generate')
    parser.add_argument('--output-dir', default='.', help='Output directory for enhanced prompts')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    integrator = PlanIntegrator()
    
    try:
        # Integrate plans
        print(f"🔍 Discovering plans in {args.plan_directory}...")
        integration_result = integrator.integrate_plans(args.plan_directory, args.agent_count)
        
        print(f"✅ Found {len(integration_result['parsed_plans'])} plans")
        print(f"🤖 Assigning to {integration_result['agent_count']} agents")
        
        # Generate enhanced prompts
        print("📝 Generating enhanced agent prompts...")
        enhanced_prompts = integrator.generate_enhanced_prompts(integration_result)
        
        if args.dry_run:
            print("\n🔍 DRY RUN - Would generate:")
            for agent_id in enhanced_prompts.keys():
                print(f"  - AGENT_{agent_id.upper()}_PROMPT.md")
        else:
            # Write enhanced prompts
            for agent_id, prompt_content in enhanced_prompts.items():
                output_file = os.path.join(args.output_dir, f"AGENT_{agent_id.upper()}_PROMPT.md")
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Replace placeholders
                    final_prompt = prompt_content.replace('{{AGENT_NAME}}', agent_id.title())
                    final_prompt = final_prompt.replace('{{AGENT_ID}}', agent_id)
                    f.write(final_prompt)
                
                print(f"✅ Generated: {output_file}")
        
        print(f"\n🎉 Plan integration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()