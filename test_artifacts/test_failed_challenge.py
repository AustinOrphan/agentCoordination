#!/usr/bin/env python3
"""Test that incorrect challenge response fails safely"""

import sys
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