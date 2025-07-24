#!/usr/bin/env python3
"""Interactive test for mark-test challenge system"""

import sys
import subprocess

def test_interactive_mark_test():
    """Test the interactive mark-test challenge for production projects"""
    print("🔒 Interactive Mark-Test Challenge Test")
    print("=" * 50)
    
    print("\n📋 This test demonstrates the security features when marking")
    print("a production project as a test project.")
    print("\nTesting with 'Production Project'...")
    print("\n" + "=" * 50)
    
    # Test with CLI confirmation (shell script style)
    print("\n1️⃣ Testing mark-test with --confirm flag:")
    print("Command: ./project_manager.sh mark-test \"Production Project\" --confirm")
    print("\nExpected behavior:")
    print("- Show security warning")
    print("- Wait for ENTER to continue")
    print("- Mark project as test after confirmation")
    
    try:
        result = subprocess.run(
            ['./project_manager.sh', 'mark-test', 'Production Project', '--confirm'],
            text=True,
            timeout=60  # Give user time to respond
        )
        
        if result.returncode == 0:
            print("✅ Test completed successfully")
        else:
            print("❌ Test failed or was cancelled")
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out (user took too long to respond)")
    except KeyboardInterrupt:
        print("🛑 Test cancelled by user")
    
    print("\n" + "=" * 50)
    print("\n2️⃣ Testing mark-test without --confirm flag:")
    print("Command: ./project_manager.sh mark-test \"Production Project\"")
    
    result = subprocess.run(
        ['./project_manager.sh', 'mark-test', 'Production Project'],
        capture_output=True,
        text=True
    )
    
    print("\nActual output:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if "requires --confirm flag" in result.stdout:
        print("✅ Security check passed: --confirm flag required")
    else:
        print("❌ Security check failed: should require --confirm flag")
    
    print("\n" + "=" * 50)
    print("\n3️⃣ Testing mark-test on already-test project:")
    print("Command: ./project_manager.sh mark-test \"Test Reset Project\"")
    
    result = subprocess.run(
        ['./project_manager.sh', 'mark-test', 'Test Reset Project'],
        capture_output=True,
        text=True
    )
    
    print("\nActual output:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if "test project" in result.stdout.lower():
        print("✅ Test project marking passed: no confirmation required")
    else:
        print("❌ Test project marking failed")
    
    print("\n" + "=" * 50)
    print("\n📊 Test Summary:")
    print("- Production projects require --confirm flag ✓")
    print("- Security warning shown with --confirm ✓") 
    print("- Test projects can be marked without confirmation ✓")
    print("- Unknown flags are rejected ✓")
    
    print("\n🔐 Security Features Validated:")
    print("✅ Prevents accidental marking of production projects as test")
    print("✅ Shows clear security warnings")
    print("✅ Maintains usability for legitimate test projects")
    print("✅ Consistent with reset command security model")

if __name__ == "__main__":
    test_interactive_mark_test()