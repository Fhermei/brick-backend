"""
Test all organization endpoints
"""

import pytest
import uuid
import requests


class TestOrganizationEndpoints:
    """Test suite for organization endpoints"""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    @classmethod
    def setup_class(cls):
        """Setup authenticated session once for this class"""
        cls.session = requests.Session()
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        response = cls.session.post(f"{cls.BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        print("\n✅ Organization tests authenticated")
    
    def test_list_my_organizations(self):
        """Test listing user's organizations"""
        response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        
        print(f"\nList orgs response status: {response.status_code}")
        
        assert response.status_code == 200
        assert "total" in response.json()
        assert "organizations" in response.json()
        print(f"\nFound {response.json()['total']} organizations")
    
    def test_get_single_organization(self):
        """Test getting a single organization by ID"""
        # First get an organization ID
        list_response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        assert list_response.status_code == 200
        orgs = list_response.json().get("organizations", [])
        
        if not orgs:
            pytest.skip("No organizations found to test")
        
        org_id = orgs[0]["id"]
        response = self.session.get(f"{self.BASE_URL}/organizations/{org_id}")
        
        print(f"\nGet org response status: {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()["id"] == org_id
        assert "name" in response.json()
        assert "industry" in response.json()
        assert "currency" in response.json()
    
    def test_create_organization(self):
        """Test creating a new organization"""
        unique_name = f"Test Org {uuid.uuid4().hex[:8]}"
        
        org_data = {
            "name": unique_name,
            "industry": "Software Development",
            "currency": "USD",
            "timezone": "Africa/Lagos"
        }
        
        response = self.session.post(f"{self.BASE_URL}/organizations/", json=org_data)
        
        print(f"\nCreate org response status: {response.status_code}")
        
        assert response.status_code == 201
        assert response.json()["name"] == unique_name
        assert response.json()["industry"] == "Software Development"
        assert "id" in response.json()
        assert response.json()["member_count"] == 1
        
        # Clean up - delete the test organization
        org_id = response.json()["id"]
        delete_response = self.session.delete(f"{self.BASE_URL}/organizations/{org_id}")
        print(f"Delete org response status: {delete_response.status_code}")
    
    def test_update_organization(self):
        """Test updating organization details"""
        # First create a test organization
        unique_name = f"Update Test Org {uuid.uuid4().hex[:8]}"
        org_data = {
            "name": unique_name,
            "industry": "Original Industry",
            "currency": "USD",
            "timezone": "Africa/Lagos"
        }
        
        create_response = self.session.post(f"{self.BASE_URL}/organizations/", json=org_data)
        assert create_response.status_code == 201
        org_id = create_response.json()["id"]
        
        # Update the organization
        update_data = {
            "name": f"Updated Org {uuid.uuid4().hex[:8]}",
            "industry": "Updated Industry"
        }
        
        response = self.session.patch(
            f"{self.BASE_URL}/organizations/{org_id}",
            json=update_data
        )
        
        print(f"\nUpdate org response status: {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]
        assert response.json()["industry"] == update_data["industry"]
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/organizations/{org_id}")
    
    def test_get_organization_members(self):
        """Test getting organization members"""
        # First get an organization ID
        list_response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        assert list_response.status_code == 200
        orgs = list_response.json().get("organizations", [])
        
        if not orgs:
            pytest.skip("No organizations found to test")
        
        org_id = orgs[0]["id"]
        response = self.session.get(f"{self.BASE_URL}/organizations/{org_id}/members")
        
        print(f"\nGet members response status: {response.status_code}")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)