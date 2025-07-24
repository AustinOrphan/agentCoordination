#!/usr/bin/env python3
"""
Codebase Cleanup Script
Organizes files into proper directories for better project structure
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class CodebaseCleanup:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.cleanup_plan = {
            "archive": {
                "description": "Old versions, backups, and deprecated files",
                "patterns": [
                    "*_old*", "*_backup*", "*_original*", "*_2.py",
                    "cleanup_review*", "start_agent_*.sh", 
                    "AGENT_*_PROMPT.md", "authority_*", "conflict_*",
                    "*_template*", "enhanced_*", "agent_updates.log"
                ]
            },
            "docs": {
                "description": "All documentation files",
                "patterns": [
                    "*.md", "docs/*", "TROUBLESHOOTING_GUIDE.md",
                    "*_GUIDE.md", "*_SUMMARY.md", "*_README.md"
                ]
            },
            "test_artifacts": {
                "description": "Test outputs, coverage reports, and test data",
                "patterns": [
                    "htmlcov/*", "*.coverage", "test_*.py", 
                    "*_test.py", "pytest.ini", "requirements-test.txt",
                    "project_analysis_accuracy_report.json",
                    "performance_reports/*", "metrics/*"
                ]
            },
            "development": {
                "description": "Development scripts, temporary files, and utilities",
                "patterns": [
                    "*.log", "*.pid", "demo_*.sh", "show_*.py",
                    "init_*.py", "agent_*.py", "load_balancer.py",
                    "metrics_collector.py", "performance_profiler.py",
                    "work_tracking_system.py", "plan_integrator.py",
                    "emergency_protocol_framework.py"
                ]
            },
            "runtime": {
                "description": "Runtime data, agent communication, and project instances",
                "patterns": [
                    "agent_communication/*", "agent_status/*", 
                    "projects/*", "logs/*", "lifecycle_daemon.*",
                    "*.json", "templates/*", "project_templates/*"
                ]
            }
        }
        
        # Core files that should stay in root
        self.core_files = {
            "CLAUDE.md",
            "README.md", 
            "requirements.txt",
            "agent_config.json",
            "coordination_manager.sh",
            "manage_agents.sh",
            "generate_agents.sh",
            "worktree_manager.sh",
            "coordination_system/",
            "tests/",
            "features/"
        }
    
    def analyze_current_state(self):
        """Analyze current directory structure"""
        print("🔍 Analyzing current codebase structure...")
        
        total_files = 0
        file_types = {}
        large_files = []
        
        for item in self.root.rglob("*"):
            if item.is_file():
                total_files += 1
                ext = item.suffix or "no_extension"
                file_types[ext] = file_types.get(ext, 0) + 1
                
                size_mb = item.stat().st_size / (1024 * 1024)
                if size_mb > 1:  # Files larger than 1MB
                    large_files.append((item, size_mb))
        
        print(f"📊 Current State:")
        print(f"   Total files: {total_files}")
        print(f"   File types: {dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10])}")
        
        if large_files:
            print(f"   Large files (>1MB):")
            for file_path, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
                print(f"     {file_path.relative_to(self.root)}: {size:.1f}MB")
    
    def create_directory_structure(self):
        """Create organized directory structure"""
        print("\n📁 Creating organized directory structure...")
        
        for folder_name, info in self.cleanup_plan.items():
            folder_path = self.root / folder_name
            folder_path.mkdir(exist_ok=True)
            
            # Create README for each folder
            readme_path = folder_path / "README.md"
            if not readme_path.exists():
                readme_path.write_text(f"# {folder_name.title()}\n\n{info['description']}\n\n"
                                     f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"   ✅ {folder_name}/ - {info['description']}")
    
    def move_files_by_category(self, dry_run: bool = True):
        """Move files to appropriate directories"""
        print(f"\n🚀 {'[DRY RUN] ' if dry_run else ''}Moving files to organized structure...")
        
        moved_files = {}
        
        for category, info in self.cleanup_plan.items():
            moved_files[category] = []
            target_dir = self.root / category
            
            for pattern in info['patterns']:
                for file_path in self.root.glob(pattern):
                    if file_path.is_file() and file_path.name not in self.core_files:
                        relative_path = file_path.relative_to(self.root)
                        
                        # Skip if already in target directory
                        if str(relative_path).startswith(category):
                            continue
                        
                        target_path = target_dir / file_path.name
                        
                        # Handle name conflicts
                        counter = 1
                        while target_path.exists():
                            stem = file_path.stem
                            suffix = file_path.suffix
                            target_path = target_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        print(f"   📦 {relative_path} → {category}/{target_path.name}")
                        moved_files[category].append((str(relative_path), str(target_path.relative_to(self.root))))
                        
                        if not dry_run:
                            shutil.move(str(file_path), str(target_path))
        
        return moved_files
    
    def consolidate_documentation(self, dry_run: bool = True):
        """Consolidate scattered documentation"""
        print(f"\n📚 {'[DRY RUN] ' if dry_run else ''}Consolidating documentation...")
        
        docs_dir = self.root / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different doc types
        subdirs = {
            "guides": "User guides and how-to documentation",
            "development": "Development and technical documentation", 
            "architecture": "System architecture and design docs",
            "api": "API documentation and references"
        }
        
        for subdir, description in subdirs.items():
            subdir_path = docs_dir / subdir
            subdir_path.mkdir(exist_ok=True)
            
            readme_path = subdir_path / "README.md"
            if not readme_path.exists():
                readme_path.write_text(f"# {subdir.title()}\n\n{description}\n")
        
        # Move docs based on content/naming patterns
        doc_patterns = {
            "guides": ["*_GUIDE.md", "STARTUP_*.md", "SHUTDOWN_*.md"],
            "development": ["*_SUMMARY.md", "TDD_*.md", "TEST_*.md"],
            "architecture": ["DYNAMIC_*.md", "COORDINATION_*.md", "MULTI_*.md"],
            "api": ["*_CLI*.md", "INTERACTIVE_*.md"]
        }
        
        moved_docs = 0
        for category, patterns in doc_patterns.items():
            for pattern in patterns:
                for doc_file in self.root.glob(pattern):
                    if doc_file.is_file():
                        target_path = docs_dir / category / doc_file.name
                        print(f"   📖 {doc_file.name} → docs/{category}/")
                        moved_docs += 1
                        
                        if not dry_run:
                            shutil.move(str(doc_file), str(target_path))
        
        print(f"   ✅ Moved {moved_docs} documentation files")
    
    def clean_duplicate_files(self, dry_run: bool = True):
        """Identify and handle duplicate files"""
        print(f"\n🧹 {'[DRY RUN] ' if dry_run else ''}Cleaning duplicate files...")
        
        # Find potential duplicates by name patterns
        duplicates = []
        
        for file_path in self.root.rglob("*"):
            if file_path.is_file():
                name = file_path.name.lower()
                
                # Check for obvious duplicates
                if any(pattern in name for pattern in ["_old", "_backup", "_original", "_2.", "_copy"]):
                    # Find potential original
                    clean_name = name
                    for pattern in ["_old", "_backup", "_original", "_2", "_copy"]:
                        clean_name = clean_name.replace(pattern, "")
                    
                    # Look for original file
                    potential_originals = list(self.root.glob(f"**/{clean_name}"))
                    if potential_originals:
                        duplicates.append((file_path, potential_originals[0]))
        
        if duplicates:
            print(f"   🗂️ Found {len(duplicates)} potential duplicate files:")
            for duplicate, original in duplicates[:10]:  # Show first 10
                print(f"     {duplicate.name} (duplicate of {original.name})")
            
            if not dry_run:
                archive_duplicates = self.root / "archive" / "duplicates"
                archive_duplicates.mkdir(exist_ok=True)
                
                for duplicate, original in duplicates:
                    target_path = archive_duplicates / duplicate.name
                    shutil.move(str(duplicate), str(target_path))
                    print(f"   📦 Moved {duplicate.name} to archive/duplicates/")
        else:
            print("   ✅ No obvious duplicates found")
    
    def generate_cleanup_report(self, moved_files: dict):
        """Generate cleanup report"""
        report_path = self.root / "CLEANUP_REPORT.md"
        
        report_content = f"""# Codebase Cleanup Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

This report documents the cleanup and reorganization of the codebase for better maintainability.

## Directory Structure

The codebase has been organized into the following directories:

"""
        
        for category, info in self.cleanup_plan.items():
            report_content += f"### {category}/\n{info['description']}\n\n"
            
            if category in moved_files:
                report_content += f"Files moved: {len(moved_files[category])}\n\n"
                if moved_files[category]:
                    report_content += "**Moved files:**\n"
                    for original, new in moved_files[category][:10]:  # Show first 10
                        report_content += f"- `{original}` → `{new}`\n"
                    
                    if len(moved_files[category]) > 10:
                        report_content += f"- ... and {len(moved_files[category]) - 10} more files\n"
                    report_content += "\n"
        
        report_content += """
## Core Files Kept in Root

The following essential files remain in the root directory:
- `CLAUDE.md` - Project instructions
- `requirements.txt` - Python dependencies  
- `coordination_manager.sh` - Main coordination script
- `manage_agents.sh` - Agent management
- `coordination_system/` - Core Python modules
- `tests/` - Test suite

## Next Steps

1. Review the organized structure
2. Update any hardcoded file paths in scripts
3. Update documentation references
4. Remove any files from `archive/` that are no longer needed
5. Update `.gitignore` to exclude development artifacts

## Rollback

If needed, files can be restored from the archive directories.
"""
        
        report_path.write_text(report_content)
        print(f"\n📋 Cleanup report generated: {report_path}")
    
    def update_gitignore(self):
        """Update .gitignore to exclude development artifacts"""
        gitignore_path = self.root / ".gitignore"
        
        additional_ignores = [
            "\n# Development artifacts",
            "development/",
            "test_artifacts/",
            "runtime/agent_communication/",
            "runtime/projects/",
            "runtime/logs/",
            "*.log",
            "*.pid",
            ".coverage",
            "htmlcov/",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".pytest_cache/"
        ]
        
        if gitignore_path.exists():
            current_content = gitignore_path.read_text()
            new_content = current_content + "\n" + "\n".join(additional_ignores)
        else:
            new_content = "\n".join(additional_ignores)
        
        gitignore_path.write_text(new_content)
        print(f"📝 Updated .gitignore with development artifact exclusions")


def main():
    """Main cleanup function"""
    cleanup = CodebaseCleanup(".")
    
    print("🧹 Codebase Cleanup Tool")
    print("=" * 50)
    
    # Analyze current state
    cleanup.analyze_current_state()
    
    # Create directory structure
    cleanup.create_directory_structure()
    
    # Dry run first
    print("\n" + "=" * 50)
    print("🎯 DRY RUN - No files will be moved")
    print("=" * 50)
    
    moved_files = cleanup.move_files_by_category(dry_run=True)
    cleanup.consolidate_documentation(dry_run=True)
    cleanup.clean_duplicate_files(dry_run=True)
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    print("Do you want to proceed with the actual cleanup? (y/N): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        print("\n🚀 Executing cleanup...")
        moved_files = cleanup.move_files_by_category(dry_run=False)
        cleanup.consolidate_documentation(dry_run=False)
        cleanup.clean_duplicate_files(dry_run=False)
        cleanup.generate_cleanup_report(moved_files)
        cleanup.update_gitignore()
        
        print("\n✅ Cleanup completed successfully!")
        print("📋 Review CLEANUP_REPORT.md for details")
    else:
        print("\n❌ Cleanup cancelled by user")


if __name__ == "__main__":
    main()