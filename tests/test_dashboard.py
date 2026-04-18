"""
Test all dashboard endpoints
"""

import pytest
import requests


class TestDashboardEndpoints:
    """Test suite for dashboard endpoints"""
    
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
        print("\n✅ Dashboard tests authenticated")
    
    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        # First get an organization ID
        list_response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        assert list_response.status_code == 200
        orgs = list_response.json().get("organizations", [])
        
        if not orgs:
            pytest.skip("No organizations found to test")
        
        org_id = orgs[0]["id"]
        
        response = self.session.get(
            f"{self.BASE_URL}/dashboard/stats?org_id={org_id}"
        )
        
        print(f"\nDashboard stats response status: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "organization_id" in data
        assert "organization_name" in data
        assert "task_stats" in data
        assert "budget_stats" in data
        assert "kpi_stats" in data
        
        print(f"  Organization: {data['organization_name']}")
        print(f"  Total Budget: ${data['budget_stats']['total_budget']:,.2f}")
        print(f"  BUR: {data['budget_stats']['bur']}%")
        print(f"  Average KAR: {data['kpi_stats']['average_kar']}%")
    
    def test_get_recent_projects(self):
        """Test getting recent projects for dashboard"""
        # First get an organization ID
        list_response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        assert list_response.status_code == 200
        orgs = list_response.json().get("organizations", [])
        
        if not orgs:
            pytest.skip("No organizations found to test")
        
        org_id = orgs[0]["id"]
        
        response = self.session.get(
            f"{self.BASE_URL}/dashboard/recent-projects?org_id={org_id}&limit=5"
        )
        
        print(f"\nRecent projects response status: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "projects" in data
        assert "total" in data
        assert isinstance(data["projects"], list)
        print(f"Found {data['total']} recent projects")
    
    def test_get_recent_tasks(self):
        """Test getting recent tasks for dashboard"""
        # First get an organization ID
        list_response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        assert list_response.status_code == 200
        orgs = list_response.json().get("organizations", [])
        
        if not orgs:
            pytest.skip("No organizations found to test")
        
        org_id = orgs[0]["id"]
        
        response = self.session.get(
            f"{self.BASE_URL}/dashboard/recent-tasks?org_id={org_id}&limit=10"
        )
        
        print(f"\nRecent tasks response status: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)
        print(f"Found {data['total']} recent tasks")
    
    def test_dashboard_stats_unauthenticated(self):
        """Test dashboard stats without authentication"""
        # First get an organization ID
        list_response = requests.get(f"{self.BASE_URL}/organizations/mine")
        if list_response.status_code == 200:
            orgs = list_response.json().get("organizations", [])
            if orgs:
                org_id = orgs[0]["id"]
                response = requests.get(f"{self.BASE_URL}/dashboard/stats?org_id={org_id}")
                assert response.status_code == 401