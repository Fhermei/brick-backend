"""
Pytest configuration for testing running server
"""

import pytest
from tests.global_session import get_global_session, BASE_URL


@pytest.fixture(scope="session")
def session():
    """Authenticated session for all tests"""
    return get_global_session()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API"""
    return BASE_URL


@pytest.fixture(scope="session")
def test_org_id(base_url):
    """Get or create a test organization ID (session scope)"""
    session = get_global_session()
    
    # First try to get existing orgs
    response = session.get(f"{base_url}/organizations/mine")
    
    if response.status_code == 200:
        orgs = response.json().get("organizations", [])
        if orgs:
            org_id = orgs[0]["id"]
            print(f"\n✅ Using existing organization: {org_id}")
            return org_id
    
    # Create new org if none exists
    org_data = {
        "name": "Test Organization",
        "industry": "Technology",
        "currency": "USD",
        "timezone": "Africa/Lagos"
    }
    
    create_response = session.post(f"{base_url}/organizations/", json=org_data)
    
    if create_response.status_code == 201:
        org_id = create_response.json()["id"]
        print(f"\n✅ Created test organization: {org_id}")
        return org_id
    
    pytest.skip("Could not create or find test organization")
    return None