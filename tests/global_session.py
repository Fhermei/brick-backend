"""
Global authenticated session for all tests
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Global session object
_global_session = None

def get_global_session():
    """Get or create global authenticated session"""
    global _global_session
    
    if _global_session is None:
        _global_session = requests.Session()
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        
        response = _global_session.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} - {response.json()}")
        print("✅ Global authentication successful!")
    
    return _global_session


def get_first_org_id():
    """Helper to get first organization ID from seeded data"""
    session = get_global_session()
    response = session.get(f"{BASE_URL}/organizations/mine")
    
    if response.status_code == 200:
        orgs = response.json().get("organizations", [])
        if orgs:
            return orgs[0]["id"]
    
    return None