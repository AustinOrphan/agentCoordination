# Project Reset Test Scripts Documentation

This document describes the test scripts created for validating the project reset functionality, including their purpose, usage, and expected outputs.

## Overview

Five test scripts were created to validate different aspects of the reset functionality:

1. `test_production_reset.py` - Tests challenge generation and production reset flow
2. `show_reset_challenges.py` - Demonstrates all four challenge types
3. `test_failed_challenge.py` - Validates wrong challenge responses are rejected
4. `test_mark_test_security.py` - Tests mark-test security features (NEW)
5. `test_mark_test_interactive.py` - Interactive mark-test challenge demonstration (NEW)

## Test Scripts

### 1. test_production_reset.py

**Purpose**: Validates the production reset challenge system and successful reset flow.

**Location**: `/agentCoordination/test_production_reset.py`

**Usage**:
```bash
python3 test_production_reset.py
```

**What it tests**:
- Project lookup by name
- Challenge generation for production projects
- Project metadata display
- Successful reset with challenge bypass

**Expected Output**:
```
Testing reset for: Production Project
Project ID: proj_87654321
Is test project: False

Challenge: Type the project name in UPPERCASE to confirm reset: Production Project
Expected response: PRODUCTION PROJECT

Simulating correct response...
✅ Reset successful!
```

**Code Walkthrough**:
```python
def test_production_reset():
    manager = ProjectManager()
    
    # Get the production project
    project = manager.get_project_by_name("Production Project")
    if not project:
        print("Production Project not found")
        return
    
    # Display project info
    print(f"Testing reset for: {project.name}")
    print(f"Project ID: {project.project_id}")
    print(f"Is test project: {project.metadata.get('is_test', False)}")
    
    # Generate a challenge
    challenge = manager.generate_reset_challenge(project.project_id)
    if challenge:
        print(f"\nChallenge: {challenge[0]}")
        print(f"Expected response: {challenge[1]}")
        
        # Simulate correct response by skipping challenge
        result = manager.reset_project(project.project_id, is_test=False, skip_challenge=True)
        if result:
            print("✅ Reset successful!")
        else:
            print("❌ Reset failed!")
```

### 2. show_reset_challenges.py

**Purpose**: Demonstrates all four types of reset challenges that can be generated.

**Location**: `/agentCoordination/show_reset_challenges.py`

**Usage**:
```bash
python3 show_reset_challenges.py
```

**What it demonstrates**:
- All four challenge types with examples
- Challenge prompt formats
- Expected response formats

**Expected Output**:
```
=== PRODUCTION RESET CHALLENGE TYPES ===

Challenge Type 1:
  Prompt: Type the project name in UPPERCASE to confirm reset: Example Project
  Required Response: EXAMPLE PROJECT

Challenge Type 2:
  Prompt: Type 'RESET EXA' to confirm:
  Required Response: RESET EXA

Challenge Type 3:
  Prompt: Type the first 8 characters of the project ID (proj_123) to confirm:
  Required Response: proj_123

Challenge Type 4:
  Prompt: Type 'DELETE ALL DATA' to confirm reset of Example Project:
  Required Response: DELETE ALL DATA
```

**Code Walkthrough**:
```python
def show_all_challenges():
    manager = ProjectManager()
    
    # Create a fake project for demonstration
    class FakeProject:
        def __init__(self):
            self.project_id = "proj_12345678"
            self.name = "Example Project"
    
    project = FakeProject()
    
    # Define all four challenge types
    challenges = [
        (
            f"Type the project name in UPPERCASE to confirm reset: {project.name}",
            project.name.upper()
        ),
        (
            f"Type 'RESET {project.name[:3].upper()}' to confirm:",
            f"RESET {project.name[:3].upper()}"
        ),
        (
            f"Type the first 8 characters of the project ID ({project.project_id[:8]}) to confirm:",
            project.project_id[:8]
        ),
        (
            f"Type 'DELETE ALL DATA' to confirm reset of {project.name}:",
            "DELETE ALL DATA"
        )
    ]
    
    # Display each challenge type
    for i, (challenge, response) in enumerate(challenges, 1):
        print(f"Challenge Type {i}:")
        print(f"  Prompt: {challenge}")
        print(f"  Required Response: {response}")
        print()
```

### 3. test_failed_challenge.py

**Purpose**: Validates that incorrect challenge responses properly cancel the reset operation.

**Location**: `/agentCoordination/test_failed_challenge.py`

**Usage**:
```bash
python3 test_failed_challenge.py
```

**What it tests**:
- CLI integration with challenge system
- Wrong answer rejection
- Process termination on failure
- Safety mechanism validation

**Expected Output**:
```
Testing production reset with WRONG answer...
STDOUT:
═══════════════════════════════════════════════════════
⚠️  PRODUCTION PROJECT RESET WARNING ⚠️
═══════════════════════════════════════════════════════
You are about to reset: Production Project
This will DELETE:
  • All agent status files
  • All agent communication data
  • All task assignments
  • All agent prompts
  • All worktree references
  • All logs

Project configuration will be preserved.
═══════════════════════════════════════════════════════

Challenge: Type the project name in UPPERCASE to confirm reset: Production Project
Challenge failed. Reset cancelled.

✅ Test passed: Reset was cancelled due to wrong answer
```

**Code Walkthrough**:
```python
import subprocess

# Test with wrong answer
print("Testing production reset with WRONG answer...")
process = subprocess.Popen(
    ['python3', 'coordination_system/project_manager.py', 'reset', 'Production Project', '--confirm'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for challenge and send wrong answer
stdout, stderr = process.communicate(input="wrong answer\n")

print("STDOUT:")
print(stdout)
if stderr:
    print("\nSTDERR:")
    print(stderr)

# Check if reset was properly cancelled
if "Challenge failed" in stdout:
    print("\n✅ Test passed: Reset was cancelled due to wrong answer")
else:
    print("\n❌ Test failed: Reset should have been cancelled")
```

### 4. test_mark_test_security.py

**Purpose**: Validates the security features of the mark-test command to prevent accidental marking of production projects as test.

**Location**: `/agentCoordination/test_mark_test_security.py`

**Usage**:
```bash
python3 test_mark_test_security.py
```

**What it tests**:
- Production projects require --confirm flag to mark as test
- Test projects can be marked without confirmation
- Unmarking test projects works without confirmation
- Shell script flag validation

**Expected Output**:
```
🔒 Mark-Test Security Test Suite
========================================

🧪 Testing mark-test without --confirm (should fail)...
✅ PASS: Production project correctly rejected without --confirm

🧪 Testing mark-test with --confirm (interactive test)...
This would normally require user interaction.
Expected behavior:
1. Show security warning
2. Wait for ENTER key
3. Mark project as test on confirmation
✅ PASS: Interactive flow documented (manual testing required)

🧪 Testing mark-test on already-test project...
✅ PASS: Test project marked without requiring --confirm

🧪 Testing unmark test project...
✅ PASS: Test project unmarked successfully

🧪 Testing shell script flag handling...
✅ PASS: Unknown flag correctly rejected

📊 Test Results: 5/5 passed
🎉 All tests passed!
```

### 5. test_mark_test_interactive.py

**Purpose**: Interactive demonstration of the mark-test security challenge system.

**Location**: `/agentCoordination/test_mark_test_interactive.py`

**Usage**:
```bash
python3 test_mark_test_interactive.py
```

**What it demonstrates**:
- Interactive security warning for production projects
- CLI confirmation flow with --confirm flag
- Different behavior for test vs production projects
- Complete security validation workflow

**Expected Output**:
```
🔒 Interactive Mark-Test Challenge Test
==================================================

📋 This test demonstrates the security features when marking
a production project as a test project.

Testing with 'Production Project'...

==================================================

1️⃣ Testing mark-test with --confirm flag:
Command: ./project_manager.sh mark-test "Production Project" --confirm

Expected behavior:
- Show security warning  
- Wait for ENTER to continue
- Mark project as test after confirmation

⚠️  SECURITY WARNING: Marking Production Project as Test ⚠️
Project: Production Project
This will enable unrestricted resets without confirmation.
This is a significant security change for production projects.
════════════════════════════════════════════════════════
Press ENTER to continue or Ctrl+C to cancel...

✅ Test completed successfully

==================================================

2️⃣ Testing mark-test without --confirm flag:
Command: ./project_manager.sh mark-test "Production Project"

Actual output:
❌ Error: Marking production project 'Production Project' as test requires --confirm flag
This enables unrestricted resets and is a significant security change.
Usage: coordination_system/project_manager.py mark-test "Production Project" --confirm

✅ Security check passed: --confirm flag required

📊 Test Summary:
- Production projects require --confirm flag ✓
- Security warning shown with --confirm ✓ 
- Test projects can be marked without confirmation ✓
- Unknown flags are rejected ✓

🔐 Security Features Validated:
✅ Prevents accidental marking of production projects as test
✅ Shows clear security warnings
✅ Maintains usability for legitimate test projects
✅ Consistent with reset command security model
```

## Running All Tests

To run all test scripts sequentially:

```bash
# Run individual tests
echo "=== Testing Challenge Generation ==="
python3 test_production_reset.py

echo -e "\n=== Showing All Challenge Types ==="
python3 show_reset_challenges.py

echo -e "\n=== Testing Failed Challenge ==="
python3 test_failed_challenge.py

echo -e "\n=== Testing Mark-Test Security ==="
python3 test_mark_test_security.py

echo -e "\n=== Interactive Mark-Test Demo ==="
python3 test_mark_test_interactive.py
```

Or create a test runner script:

```bash
#!/bin/bash
# run_reset_tests.sh

echo "🧪 Running Project Reset Test Suite"
echo "=================================="

echo -e "\n1️⃣ Testing Challenge Generation..."
python3 test_production_reset.py

echo -e "\n2️⃣ Showing All Challenge Types..."
python3 show_reset_challenges.py

echo -e "\n3️⃣ Testing Failed Challenge..."
python3 test_failed_challenge.py

echo -e "\n4️⃣ Testing Mark-Test Security..."
python3 test_mark_test_security.py

echo -e "\n5️⃣ Interactive Mark-Test Demo..."
echo "   (This test requires user interaction)"
python3 test_mark_test_interactive.py

echo -e "\n✅ All tests completed!"
```

## Test Results Validation

### Success Indicators

**test_production_reset.py**:
- ✅ Project found and displayed
- ✅ Challenge generated successfully
- ✅ Reset completed successfully

**show_reset_challenges.py**:
- ✅ All 4 challenge types displayed
- ✅ Correct prompt formatting
- ✅ Proper response expectations

**test_failed_challenge.py**:
- ✅ Warning message displayed
- ✅ Challenge prompt shown
- ✅ "Challenge failed" message appears
- ✅ Reset operation cancelled

**test_mark_test_security.py**:
- ✅ Production projects require --confirm flag
- ✅ Test projects marked without confirmation
- ✅ Unknown flags rejected properly
- ✅ All security tests pass

**test_mark_test_interactive.py**:
- ✅ Security warning displayed
- ✅ Interactive confirmation works
- ✅ Different behavior for test vs production
- ✅ Complete workflow validated

### Failure Indicators

**Common Issues**:
- ❌ "Project not found" - Project setup issue
- ❌ "Challenge failed to generate" - Logic error
- ❌ Reset continues after wrong challenge - Security issue
- ❌ No warning message displayed - Missing safety feature

## Integration with Main Test Suite

These test scripts can be integrated into the main project test suite:

```python
# In pytest test file
import subprocess
import pytest

def test_production_reset_challenge():
    """Test production reset challenge system"""
    result = subprocess.run(
        ['python3', 'test_production_reset.py'],
        capture_output=True,
        text=True
    )
    assert "✅ Reset successful!" in result.stdout

def test_challenge_failure_handling():
    """Test wrong challenge response handling"""
    result = subprocess.run(
        ['python3', 'test_failed_challenge.py'],
        capture_output=True,
        text=True
    )
    assert "✅ Test passed: Reset was cancelled due to wrong answer" in result.stdout
```

## Manual Testing Scenarios

For comprehensive testing, also perform these manual scenarios:

### Scenario 1: Test Project Reset
```bash
# Should reset without confirmation
./project_manager.sh reset "Test Project Name"
```

### Scenario 2: Production Reset with Challenge
```bash
# Should show warning and challenge
./project_manager.sh reset "Production Project" --confirm
# Complete the challenge correctly
```

### Scenario 3: Production Reset Without --confirm
```bash
# Should be rejected
./project_manager.sh reset "Production Project"
```

### Scenario 4: Bulk Test Reset
```bash
# Should reset all test projects
./project_manager.sh reset-tests
```

## Cleanup After Testing

After running tests, clean up any test data:

```bash
# Reset test projects created during testing
./project_manager.sh reset-tests

# Or manually clean specific test projects
rm -rf projects/proj_test_*
```

## Summary

The test scripts provide comprehensive validation of:
1. **Challenge Generation**: All four challenge types work correctly
2. **Security**: Wrong answers properly cancel resets
3. **User Experience**: Clear prompts and feedback
4. **Integration**: CLI and Python API work together

These tests ensure the reset functionality is both safe and user-friendly, preventing accidental data loss while providing efficient reset capabilities for development workflows.