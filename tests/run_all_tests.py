"""
Run all tests and generate comprehensive report
"""

import subprocess
import sys
import os

def run_command(command):
    """Run shell command and return output"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def main():
    print("=" * 70)
    print("BRICK SPMES - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Check if server is running
    print("\n[1] Checking backend server status...")
    import requests
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("    Server is running")
        else:
            print("    Server is not responding correctly")
    except:
        print("    ERROR: Backend server is not running!")
        print("    Please start the server first: uvicorn src.main:app --reload")
        sys.exit(1)
    
    # Run unit tests
    print("\n[2] Running Unit Tests...")
    print("-" * 50)
    stdout, stderr, code = run_command("pytest tests/ -v --tb=short")
    print(stdout)
    if stderr:
        print(stderr)
    
    # Run with coverage
    print("\n[3] Running Tests with Coverage...")
    print("-" * 50)
    stdout, stderr, code = run_command("pytest tests/ -v --cov=src --cov-report=term-missing")
    print(stdout)
    
    # Generate HTML report
    print("\n[4] Generating HTML Test Report...")
    print("-" * 50)
    run_command("pytest tests/ -v --html=test_report.html --self-contained-html")
    print("    Report saved to: test_report.html")
    
    print("\n" + "=" * 70)
    print("TEST EXECUTION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()