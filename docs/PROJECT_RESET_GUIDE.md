# Project Reset Guide

This guide covers the project reset functionality in the Multi-Agent Coordination System, including safety features, usage examples, and best practices.

## Table of Contents

1. [Overview](#overview)
2. [Safety Features](#safety-features)
3. [Quick Start](#quick-start)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)
6. [Shell Commands](#shell-commands)
7. [Challenge Types](#challenge-types)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

The project reset functionality allows you to clear all project data while preserving the project structure. This is particularly useful for:

- **Testing**: Quickly reset test environments between test runs
- **Development**: Clear temporary data during development
- **Recovery**: Reset a project that has gotten into an inconsistent state

### What Gets Reset

When you reset a project, the following data is cleared:

- `agent_status/` - All agent status JSON files
- `agent_communication/` - All agent communication channels (inbox/outbox)
- `task_assignments/` - Task queues and assignments
- `agent_prompts/` - Generated agent prompt files
- `worktrees/` - Git worktree references
- `logs/` - All log files

### What Is Preserved

- Project configuration (`config.json`)
- Project directory structure
- Project metadata (with reset tracking)

## Safety Features

The system implements multiple layers of safety to prevent accidental data loss:

### 1. Test vs. Production Projects

**Test Projects** (instant reset, no confirmation):
- Projects with "test" in the name (case-insensitive)
- Projects explicitly marked as test projects
- Can be reset without any confirmation

**Production Projects** (multiple confirmations required):
- All projects not identified as test projects
- Require `--confirm` flag
- Require completing a challenge-response

### 2. Challenge-Response System

Production projects require users to complete one of four randomly selected challenges:

1. Type the project name in UPPERCASE
2. Type "RESET" followed by the first 3 letters of the project name
3. Type the first 8 characters of the project ID
4. Type "DELETE ALL DATA"

This ensures users understand the consequences of their action.

### 3. Detailed Warnings

Before resetting a production project, the system displays:
- What will be deleted
- What will be preserved
- Number of files that will be removed
- Confirmation prompt

### 4. Mark-as-Test Protection

Marking a production project as a test project requires confirmation since it enables unrestricted resets:
- Production projects require `--confirm` flag to mark as test
- Shows security warning about enabling unrestricted resets
- Requires pressing ENTER to continue (with option to cancel)
- Already test projects can be marked/unmarked without confirmation

## Quick Start

### Reset a Test Project

```bash
# Instant reset - no confirmation needed
./project_manager.sh reset "My Test Project"
```

### Reset a Production Project

```bash
# Requires confirmation and challenge
./project_manager.sh reset "Production Project" --confirm

# You'll see a warning and then a challenge like:
# Challenge: Type the project name in UPPERCASE to confirm reset: Production Project
# Your response: PRODUCTION PROJECT
```

### Mark a Project as Test

```bash
# Mark as test project (requires --confirm for production projects)
./project_manager.sh mark-test "Development Project" --confirm

# Unmark as test (make it production - no confirmation needed)
./project_manager.sh mark-test "Development Project" --unmark
```

### Reset All Test Projects

```bash
# Reset all projects marked as test
./project_manager.sh reset-tests
```

## Usage Examples

### Example 1: Development Workflow

```bash
# Create a development project
./project_manager.sh create "Feature Dev Test" /path/to/code -d "Testing new feature" -a 4

# Mark it as a test project
./project_manager.sh mark-test "Feature Dev Test"

# Work on your feature...

# Quick reset when needed
./project_manager.sh reset "Feature Dev Test"
# ✅ Test project "Feature Dev Test" reset successfully
```

### Example 2: Safe Production Reset

```bash
# Attempt reset without confirmation
./project_manager.sh reset "Customer Portal"
# ❌ Error: Production project requires --confirm flag

# Reset with confirmation
./project_manager.sh reset "Customer Portal" --confirm

# See warning message:
# ═══════════════════════════════════════════════════════
# ⚠️  PRODUCTION PROJECT RESET WARNING ⚠️
# ═══════════════════════════════════════════════════════
# You are about to reset: Customer Portal
# This will DELETE:
#   • All agent status files
#   • All agent communication data
#   • All task assignments
#   • All agent prompts
#   • All worktree references
#   • All logs
# 
# Project configuration will be preserved.
# ═══════════════════════════════════════════════════════
# Press ENTER to continue or Ctrl+C to cancel...

# Then complete the challenge:
# Challenge: Type 'DELETE ALL DATA' to confirm reset of Customer Portal:
# Your response: DELETE ALL DATA
# ✅ Project reset successfully
```

### Example 4: Safe Test Project Marking

```bash
# Attempt to mark production project as test without confirmation
./project_manager.sh mark-test "Customer Portal"
# ❌ Error: Marking production project 'Customer Portal' as test requires --confirm flag
# This enables unrestricted resets and is a significant security change.
# Usage: project_manager.sh mark-test "Customer Portal" --confirm

# Mark with confirmation
./project_manager.sh mark-test "Customer Portal" --confirm

# See security warning:
# ⚠️  SECURITY WARNING: Marking Production Project as Test ⚠️
# Project: Customer Portal
# This will enable unrestricted resets without confirmation.
# This is a significant security change for production projects.
# ════════════════════════════════════════════════════════
# Press ENTER to continue or Ctrl+C to cancel...

# After pressing ENTER:
# ✅ Marked 'Customer Portal' as test project
```

### Example 3: Bulk Test Reset

```bash
# Reset all test projects at once
./project_manager.sh reset-tests

# Output:
# Resetting test projects...
# ✅ Reset test project: Unit Test Suite
# ✅ Reset test project: Integration Tests
# ✅ Reset test project: Feature Dev Test
# 
# Successfully reset 3 test projects
```

## API Reference

### Python Methods

#### `reset_project(project_id: str, is_test: bool = False, skip_challenge: bool = False) -> bool`

Reset a project to its initial state.

**Parameters:**
- `project_id` (str): The ID of the project to reset
- `is_test` (bool): If True, skip confirmation and reset immediately
- `skip_challenge` (bool): If True, skip interactive challenge (for CLI with pre-validation)

**Returns:**
- `bool`: True if reset successful, False otherwise

**Example:**
```python
from coordination_system.project_manager import ProjectManager

manager = ProjectManager()

# Reset a test project
success = manager.reset_project("proj_12345678", is_test=True)

# Reset with challenge (interactive)
success = manager.reset_project("proj_87654321", is_test=False)
```

#### `reset_all_test_projects() -> int`

Reset all projects marked as test projects.

**Returns:**
- `int`: Number of projects successfully reset

**Example:**
```python
count = manager.reset_all_test_projects()
print(f"Reset {count} test projects")
```

#### `mark_as_test_project(project_id: str, is_test: bool = True) -> bool`

Mark or unmark a project as a test project.

**Parameters:**
- `project_id` (str): The ID of the project
- `is_test` (bool): True to mark as test, False to unmark

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
# Mark as test
manager.mark_as_test_project("proj_12345678", is_test=True)

# Unmark (make production)
manager.mark_as_test_project("proj_12345678", is_test=False)
```

#### `generate_reset_challenge(project_id: str) -> Optional[Tuple[str, str]]`

Generate a challenge for resetting a production project.

**Returns:**
- `Optional[Tuple[str, str]]`: Tuple of (challenge_text, expected_response) or None

**Example:**
```python
challenge = manager.generate_reset_challenge("proj_12345678")
if challenge:
    prompt, expected = challenge
    print(f"Challenge: {prompt}")
    response = input("Your response: ")
    if response == expected:
        print("Challenge passed!")
```

## Shell Commands

### `reset` Command

Reset a single project.

**Syntax:**
```bash
./project_manager.sh reset <project_name> [--confirm] [--test]
```

**Options:**
- `--confirm`: Required for production projects
- `--test`: Force treat as test project (skip confirmations)

### `reset-tests` Command

Reset all test projects.

**Syntax:**
```bash
./project_manager.sh reset-tests
```

### `mark-test` Command

Mark or unmark a project as a test project.

**Syntax:**
```bash
./project_manager.sh mark-test <project_name> [--unmark] [--confirm]
```

**Options:**
- `--unmark`: Remove test project marking (no confirmation needed)
- `--confirm`: Required when marking production projects as test

## Challenge Types

The system randomly selects one of four challenge types for production resets:

### 1. Uppercase Project Name
```
Challenge: Type the project name in UPPERCASE to confirm reset: My Project
Expected: MY PROJECT
```

### 2. RESET Prefix
```
Challenge: Type 'RESET MYP' to confirm:
Expected: RESET MYP
```
(Uses first 3 letters of project name in uppercase)

### 3. Project ID
```
Challenge: Type the first 8 characters of the project ID (proj_1234) to confirm:
Expected: proj_1234
```

### 4. DELETE ALL DATA
```
Challenge: Type 'DELETE ALL DATA' to confirm reset of My Project:
Expected: DELETE ALL DATA
```

## Best Practices

### 1. Use Test Projects for Development

Always mark development and testing projects as test projects:

```bash
# Good practice
./project_manager.sh create "Feature Test" /path/to/code
./project_manager.sh mark-test "Feature Test"
```

### 2. Double-Check Before Production Resets

- Read the warning message carefully
- Ensure you have backups if needed
- Complete the challenge accurately (case-sensitive)

### 3. Use Descriptive Project Names

Include "test" in test project names for automatic detection:

```bash
# Automatically detected as test projects:
"Unit Test Suite"
"Integration Testing"
"test-feature-branch"
```

### 4. Regular Test Cleanup

Use bulk reset for test projects:

```bash
# Clean up all test projects after test suite
./run_tests.sh && ./project_manager.sh reset-tests
```

## Troubleshooting

### Reset Fails with "Permission Denied"

**Problem**: Cannot delete files due to permissions

**Solution**: Check file ownership and permissions
```bash
# Check permissions
ls -la projects/proj_*/

# Fix permissions if needed
chmod -R u+w projects/proj_*/
```

### Challenge Response Not Accepted

**Problem**: Challenge response is rejected even when correct

**Common Causes**:
- Extra spaces in response
- Wrong case (challenges are case-sensitive)
- Copied/pasted with hidden characters

**Solution**: Type the response manually, exactly as shown

### Project Not Found

**Problem**: Reset command says project doesn't exist

**Solution**: List projects to check exact name
```bash
./project_manager.sh list
```

### Reset Hangs or Takes Too Long

**Problem**: Reset operation doesn't complete

**Possible Causes**:
- Large log files
- Many agent communication files
- File system issues

**Solution**: Check disk space and file system
```bash
# Check disk space
df -h

# Check number of files
find projects/proj_*/ -type f | wc -l
```

## Security Considerations

1. **No Password Storage**: The system uses challenge-response, not passwords
2. **No Sensitive Data in Challenges**: Challenges use project metadata only
3. **Audit Trail**: All resets are logged with timestamps
4. **Metadata Tracking**: Reset count and last reset time are preserved

## Summary

The project reset functionality provides a safe and efficient way to clear project data while preventing accidental data loss. Test projects can be reset instantly for rapid development cycles, while production projects require deliberate confirmation through a challenge-response system.

Remember:
- Mark development projects as test projects
- Read warnings carefully before production resets
- Use bulk reset for cleaning multiple test projects
- Complete challenges exactly as shown (case-sensitive)

For additional help, see the main documentation or run:
```bash
./project_manager.sh --help
```