"""
Run all tests against the running server
"""

import pytest
import sys
import requests

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Brick Backend API Tests")
    print("=" * 60)
    
    # Check if server is running
    print("\nChecking if server is running on http://localhost:8000...")
    if not check_server():
        print("\n❌ ERROR: Server is not running!")
        print("Please start your backend server first:")
        print("  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        print("\nThen run this script again.")
        sys.exit(1)
    
    print("✅ Server is running!\n")
    
    # Run tests
    args = [
        "tests/",
        "-v",
        "-s",
        "--tb=short",
        "--disable-warnings"
    ]
    
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
    
    sys.exit(exit_code)