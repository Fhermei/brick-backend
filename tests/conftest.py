"""
Pytest configuration file with shared fixtures for testing
"""

import pytest
import requests
import uuid
import time

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "oyewoleoluwafemidavid1@gmail.com"
TEST_PASSWORD = "Fatunbi11."


@pytest.fixture(scope="session")
def auth_session():
    """Create authenticated session for all tests"""
    session = requests.Session()
    
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.status_code} - {response.text}")
    
    # Verify cookies are set
    if not session.cookies.get("access_token"):
        pytest.fail("Access token cookie not set after login")
    
    return session


@pytest.fixture(scope="session")
def test_org(auth_session):
    """Get or create test organization"""
    response = auth_session.get(f"{BASE_URL}/organizations/mine")
    
    if response.status_code != 200:
        pytest.fail(f"Could not fetch organizations: {response.status_code} - {response.text}")
    
    orgs = response.json().get("organizations", [])
    
    if orgs:
        return orgs[0]
    
    # Create new org if none exists
    org_data = {
        "name": f"Test NGO Organization {uuid.uuid4().hex[:8]}",
        "industry": "NGO / Non-profit",
        "currency": "USD",
        "timezone": "Africa/Lagos"
    }
    
    response = auth_session.post(f"{BASE_URL}/organizations/", json=org_data)
    
    if response.status_code != 201:
        pytest.fail(f"Could not create organization: {response.status_code} - {response.text}")
    
    return response.json()


@pytest.fixture(scope="session")
def test_project(auth_session, test_org):
    """Create test project"""
    project_data = {
        "title": f"Test NGO Project {uuid.uuid4().hex[:8]}",
        "description": "Providing clean water to rural communities",
        "status": "active",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "total_budget": 5000000,
        "currency": "USD"
    }
    
    response = auth_session.post(
        f"{BASE_URL}/projects?org_id={test_org['id']}",
        json=project_data
    )
    
    if response.status_code != 201:
        pytest.fail(f"Could not create project: {response.status_code} - {response.text}")
    
    return response.json()


@pytest.fixture(scope="session")
def test_task(auth_session, test_project):
    """Create test task"""
    task_data = {
        "title": f"Conduct community needs assessment {uuid.uuid4().hex[:8]}",
        "description": "Survey households for water needs",
        "type": "research",
        "priority": "high",
        "due_date": "2026-06-30",
        "budget_allocated": 500000
    }
    
    response = auth_session.post(
        f"{BASE_URL}/tasks?project_id={test_project['id']}",
        json=task_data
    )
    
    if response.status_code != 201:
        pytest.fail(f"Could not create task: {response.status_code} - {response.text}")
    
    return response.json()