#!/usr/bin/env python3
"""
Agent Theme Manager - Manages agent themes and configurations
"""

import json
import os
import sys
from typing import List, Dict, Optional
import argparse
from pathlib import Path

class AgentThemeManager:
    def __init__(self, config_file: str = "agent_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            print(f"Error: Configuration file {self.config_file} not found")
            sys.exit(1)
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.config.get('current_theme', 'greek_letters')
    
    def get_agent_count(self) -> int:
        """Get the current agent count"""
        return self.config.get('agent_count', 6)
    
    def get_agent_names(self, theme: Optional[str] = None, count: Optional[int] = None) -> List[str]:
        """Get agent names for a theme"""
        theme = theme or self.get_current_theme()
        count = count or self.get_agent_count()
        
        if theme not in self.config['themes']:
            print(f"Error: Theme '{theme}' not found")
            return []
        
        agents = self.config['themes'][theme]['agents']
        if count > len(agents):
            print(f"Warning: Requested {count} agents but theme '{theme}' only has {len(agents)}")
            count = len(agents)
        
        return agents[:count]
    
    def get_agent_emojis(self, theme: Optional[str] = None, count: Optional[int] = None) -> List[str]:
        """Get agent emojis for a theme"""
        theme = theme or self.get_current_theme()
        count = count or self.get_agent_count()
        
        if theme not in self.config['themes']:
            return []
        
        theme_data = self.config['themes'][theme]
        if 'agent_emojis' not in theme_data:
            # Return generic emoji if not defined
            return [theme_data.get('emoji', '🤖')] * count
        
        emojis = theme_data['agent_emojis']
        if count > len(emojis):
            count = len(emojis)
        
        return emojis[:count]
    
    def get_theme_emoji(self, theme: Optional[str] = None) -> str:
        """Get the emoji for a theme"""
        theme = theme or self.get_current_theme()
        
        if theme not in self.config['themes']:
            return '🤖'
        
        return self.config['themes'][theme].get('emoji', '🤖')
    
    def list_themes(self) -> List[str]:
        """List all available themes"""
        return list(self.config['themes'].keys())
    
    def set_theme(self, theme: str):
        """Set the current theme"""
        if theme not in self.config['themes']:
            print(f"Error: Theme '{theme}' not found")
            return False
        
        self.config['current_theme'] = theme
        self.save_config()
        print(f"Theme changed to: {self.config['themes'][theme]['name']}")
        return True
    
    def set_agent_count(self, count: int):
        """Set the number of agents"""
        if count < 1:
            print("Error: Agent count must be at least 1")
            return False
        
        max_agents = len(self.config['themes'][self.get_current_theme()]['agents'])
        if count > max_agents:
            print(f"Warning: Current theme only supports up to {max_agents} agents")
            count = max_agents
        
        self.config['agent_count'] = count
        self.save_config()
        print(f"Agent count set to: {count}")
        return True
    
    def add_theme(self, theme_id: str, theme_name: str, agents: List[str]):
        """Add a new theme"""
        if theme_id in self.config['themes']:
            print(f"Error: Theme '{theme_id}' already exists")
            return False
        
        self.config['themes'][theme_id] = {
            'name': theme_name,
            'agents': agents
        }
        self.save_config()
        print(f"Theme '{theme_name}' added successfully")
        return True
    
    def get_agent_info(self, index: int) -> Optional[Dict[str, str]]:
        """Get information about a specific agent by index"""
        agents = self.get_agent_names()
        if index < 0 or index >= len(agents):
            return None
        
        emojis = self.get_agent_emojis()
        return {
            'name': agents[index],
            'emoji': emojis[index] if index < len(emojis) else '🤖',
            'index': index,
            'theme': self.get_current_theme(),
            'display_name': agents[index].replace('_', ' ').title()
        }
    
    def show_theme_info(self):
        """Show current theme configuration"""
        theme = self.get_current_theme()
        theme_name = self.config['themes'][theme]['name']
        theme_emoji = self.get_theme_emoji()
        agent_count = self.get_agent_count()
        agents = self.get_agent_names()
        emojis = self.get_agent_emojis()
        
        print(f"\n{theme_emoji} Current Theme Configuration")
        print(f"{'=' * 40}")
        print(f"Theme: {theme_name} ({theme})")
        print(f"Active Agents: {agent_count}")
        print(f"\nAgent Names:")
        for i, (agent, emoji) in enumerate(zip(agents, emojis), 1):
            print(f"  {i}. {emoji} {agent.upper()}")
        
        print(f"\n📊 Available Themes: {len(self.list_themes())}")
        print(f"Maximum Agents in Current Theme: {len(self.config['themes'][theme]['agents'])}")
    
    def display_all_themes(self):
        """Display all available themes with their agents"""
        print("\n🎭 All Available Themes")
        print("=" * 60)
        
        for theme_id, theme_data in self.config['themes'].items():
            current = " (CURRENT)" if theme_id == self.get_current_theme() else ""
            theme_emoji = theme_data.get('emoji', '🤖')
            print(f"\n{theme_emoji} {theme_data['name']}{current}")
            print(f"ID: {theme_id}")
            print(f"Available Agents ({len(theme_data['agents'])}): ", end="")
            
            # Show first 6 agents with emojis
            agent_emojis = theme_data.get('agent_emojis', [])
            for i in range(min(6, len(theme_data['agents']))):
                agent = theme_data['agents'][i]
                emoji = agent_emojis[i] if i < len(agent_emojis) else theme_emoji
                print(f"{emoji} {agent}", end="")
                if i < min(5, len(theme_data['agents']) - 1):
                    print(", ", end="")
            
            if len(theme_data['agents']) > 6:
                print(f", ... (+{len(theme_data['agents']) - 6} more)")
            else:
                print()

def main():
    parser = argparse.ArgumentParser(description='Manage agent themes and configurations')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List themes
    subparsers.add_parser('list-themes', help='List all available themes')
    
    # Show current configuration
    subparsers.add_parser('show', help='Show current configuration')
    
    # Set theme
    set_theme_parser = subparsers.add_parser('set-theme', help='Set the current theme')
    set_theme_parser.add_argument('theme', help='Theme ID')
    
    # Set agent count
    set_count_parser = subparsers.add_parser('set-count', help='Set the number of agents')
    set_count_parser.add_argument('count', type=int, help='Number of agents')
    
    # Get agent names
    get_agents_parser = subparsers.add_parser('get-agents', help='Get agent names')
    get_agents_parser.add_argument('--theme', help='Theme to use (default: current)')
    get_agents_parser.add_argument('--count', type=int, help='Number of agents (default: configured)')
    
    # Get agent count
    get_count_parser = subparsers.add_parser('get-count', help='Get current agent count')
    
    # Get specific agent
    get_agent_parser = subparsers.add_parser('get-agent', help='Get specific agent info')
    get_agent_parser.add_argument('index', type=int, help='Agent index (0-based)')
    
    args = parser.parse_args()
    
    manager = AgentThemeManager()
    
    if args.command == 'list-themes':
        manager.display_all_themes()
    
    elif args.command == 'show':
        manager.show_theme_info()
    
    elif args.command == 'set-theme':
        manager.set_theme(args.theme)
    
    elif args.command == 'set-count':
        manager.set_agent_count(args.count)
    
    elif args.command == 'get-agents':
        agents = manager.get_agent_names(args.theme, args.count)
        for agent in agents:
            print(agent)
    
    elif args.command == 'get-count':
        print(manager.get_agent_count())
    
    elif args.command == 'get-agent':
        info = manager.get_agent_info(args.index)
        if info:
            print(json.dumps(info, indent=2))
        else:
            print(f"Error: Invalid agent index {args.index}")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()