"""
Integration tests for complete workflows
"""

import pytest
import uuid
import requests


class TestIntegration:
    """Test complete user workflows"""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    @classmethod
    def setup_class(cls):
        """Setup authenticated session and ensure we have an organization"""
        cls.session = requests.Session()
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        response = cls.session.post(f"{cls.BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        print("\n✅ Integration tests authenticated")
        
        # Get or create an organization
        org_response = cls.session.get(f"{cls.BASE_URL}/organizations/mine")
        
        if org_response.status_code == 200:
            orgs = org_response.json().get("organizations", [])
            if orgs:
                cls.test_org_id = orgs[0]["id"]
                cls.test_org_name = orgs[0]["name"]
                print(f"✅ Using existing organization: {cls.test_org_name} ({cls.test_org_id})")
            else:
                # Create a test organization
                org_data = {
                    "name": f"Integration Test Org {uuid.uuid4().hex[:8]}",
                    "industry": "Integration Testing",
                    "currency": "USD",
                    "timezone": "Africa/Lagos"
                }
                create_response = cls.session.post(f"{cls.BASE_URL}/organizations/", json=org_data)
                if create_response.status_code == 201:
                    cls.test_org_id = create_response.json()["id"]
                    cls.test_org_name = create_response.json()["name"]
                    print(f"✅ Created test organization: {cls.test_org_name} ({cls.test_org_id})")
                else:
                    cls.test_org_id = None
                    print(f"❌ Failed to create organization: {create_response.status_code}")
        else:
            cls.test_org_id = None
            print(f"❌ Failed to get organizations: {org_response.status_code}")
    
    def test_complete_workflow(self):
        """Test complete workflow from login to dashboard"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. Please create an organization first.")
        
        print("\n" + "="*50)
        print("Starting Complete Workflow Test")
        print("="*50)
        
        # Step 1: Verify we're logged in
        print("\n1. Verifying authentication...")
        me_response = self.session.get(f"{self.BASE_URL}/auth/me")
        assert me_response.status_code == 200
        user_email = me_response.json()["email"]
        print(f"   ✅ Logged in as: {user_email}")
        
        # Step 2: List organizations
        print("\n2. Listing organizations...")
        list_orgs_response = self.session.get(f"{self.BASE_URL}/organizations/mine")
        assert list_orgs_response.status_code == 200
        print(f"   ✅ Found {list_orgs_response.json()['total']} organizations")
        
        # Step 3: Create a new project
        print("\n3. Creating a new project...")
        unique_title = f"Integration Test Project {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Testing complete workflow",
            "emoji": "🎯",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 1000000,
            "currency": "USD"
        }
        
        project_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        assert project_response.status_code == 201, f"Failed to create project: {project_response.status_code}"
        project_id = project_response.json()["id"]
        print(f"   ✅ Created project: {unique_title} (ID: {project_id})")
        
        # Step 4: Get the created project
        print("\n4. Retrieving project details...")
        get_project_response = self.session.get(f"{self.BASE_URL}/projects/{project_id}")
        assert get_project_response.status_code == 200
        assert get_project_response.json()["title"] == unique_title
        print(f"   ✅ Project retrieved successfully")
        
        # Step 5: List all projects
        print("\n5. Listing all projects...")
        list_projects_response = self.session.get(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}"
        )
        assert list_projects_response.status_code == 200
        print(f"   ✅ Found {list_projects_response.json()['total']} total projects")
        
        # Step 6: Get dashboard stats
        print("\n6. Fetching dashboard statistics...")
        dashboard_response = self.session.get(
            f"{self.BASE_URL}/dashboard/stats?org_id={self.test_org_id}"
        )
        assert dashboard_response.status_code == 200
        print(f"   ✅ Dashboard loaded successfully")
        print(f"      - Organization: {dashboard_response.json()['organization_name']}")
        print(f"      - Total Budget: ${dashboard_response.json()['budget_stats']['total_budget']:,.2f}")
        print(f"      - BUR: {dashboard_response.json()['budget_stats']['bur']}%")
        print(f"      - Average KAR: {dashboard_response.json()['kpi_stats']['average_kar']}%")
        
        # Step 7: Update project
        print("\n7. Updating project...")
        update_data = {"title": f"Updated {unique_title}"}
        update_response = self.session.patch(
            f"{self.BASE_URL}/projects/{project_id}",
            json=update_data
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == f"Updated {unique_title}"
        print(f"   ✅ Project updated successfully")
        
        # Step 8: Clean up - delete project
        print("\n8. Cleaning up - deleting test project...")
        delete_response = self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
        assert delete_response.status_code == 200
        print(f"   ✅ Test project deleted")
        
        print("\n" + "="*50)
        print("✅ COMPLETE WORKFLOW TEST PASSED!")
        print("="*50)
    
    def test_organization_and_projects_linking(self):
        """Test that projects are properly linked to organizations"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. Please create an organization first.")
        
        print("\n" + "="*50)
        print("Testing Organization-Project Linking")
        print("="*50)
        
        # First create a test project
        unique_title = f"Linking Test Project {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Testing organization-project linking",
            "emoji": "🔗",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 500000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        assert create_response.status_code == 201, f"Failed to create project: {create_response.status_code}"
        project_id = create_response.json()["id"]
        print(f"\n✅ Created test project: {unique_title}")
        
        # Get all projects for the organization
        projects_response = self.session.get(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}"
        )
        assert projects_response.status_code == 200
        
        projects = projects_response.json()["projects"]
        print(f"Found {len(projects)} projects in organization")
        
        # Verify the created project belongs to the correct organization
        found = False
        for project in projects:
            if project["id"] == project_id:
                found = True
                print(f"   ✅ Project '{project['title']}' found in organization")
                
                # Verify project details
                project_detail = self.session.get(f"{self.BASE_URL}/projects/{project_id}")
                assert project_detail.status_code == 200
                assert project_detail.json()["org_id"] == self.test_org_id
                print(f"   ✅ Project correctly linked to organization ID: {self.test_org_id}")
                break
        
        assert found, f"Created project {project_id} not found in organization projects list"
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
        print(f"\n✅ Test project deleted")
        
        print("\n✅ All projects correctly linked to organization!")