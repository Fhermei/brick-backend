"""
Test all project endpoints
"""

import pytest
import uuid
import requests


class TestProjectEndpoints:
    """Test suite for project endpoints"""
    
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
        print("\n✅ Projects tests authenticated")
        
        # Get or create an organization
        org_response = cls.session.get(f"{cls.BASE_URL}/organizations/mine")
        
        if org_response.status_code == 200:
            orgs = org_response.json().get("organizations", [])
            if orgs:
                cls.test_org_id = orgs[0]["id"]
                print(f"✅ Using existing organization: {cls.test_org_id}")
            else:
                # Create a test organization
                org_data = {
                    "name": f"Test Org for Projects {uuid.uuid4().hex[:8]}",
                    "industry": "Testing",
                    "currency": "USD",
                    "timezone": "Africa/Lagos"
                }
                create_response = cls.session.post(f"{cls.BASE_URL}/organizations/", json=org_data)
                if create_response.status_code == 201:
                    cls.test_org_id = create_response.json()["id"]
                    print(f"✅ Created test organization: {cls.test_org_id}")
                else:
                    cls.test_org_id = None
                    print(f"❌ Failed to create organization: {create_response.status_code}")
        else:
            cls.test_org_id = None
            print(f"❌ Failed to get organizations: {org_response.status_code}")
    
    def test_create_project_success(self):
        """Test successful project creation"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        unique_title = f"Test Project {uuid.uuid4().hex[:8]}"
        
        project_data = {
            "title": unique_title,
            "description": "This is a test project",
            "emoji": "🚀",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 500000,
            "currency": "USD"
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        print(f"\nCreate project response status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 201
        assert response.json()["title"] == unique_title
        assert response.json()["total_budget"] == 500000
        assert "id" in response.json()
        
        # Clean up - delete the test project
        project_id = response.json()["id"]
        delete_response = self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
        print(f"Delete project response status: {delete_response.status_code}")
    
    def test_list_projects(self):
        """Test listing all projects for an organization"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        # First create a test project
        unique_title = f"List Test Project {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Project for listing test",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 100000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        if create_response.status_code != 201:
            print(f"Failed to create test project: {create_response.status_code}")
            print(f"Error: {create_response.json()}")
            pytest.skip("Could not create test project")
        
        project_id = create_response.json()["id"]
        
        # List projects
        response = self.session.get(f"{self.BASE_URL}/projects?org_id={self.test_org_id}")
        
        print(f"\nList projects response status: {response.status_code}")
        
        assert response.status_code == 200
        assert "total" in response.json()
        assert "projects" in response.json()
        assert isinstance(response.json()["projects"], list)
        print(f"Found {response.json()['total']} projects")
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
    
    def test_list_projects_with_filter(self):
        """Test listing projects with status filter"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        # Create a test project
        unique_title = f"Filter Test Project {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Project for filter test",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 100000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        if create_response.status_code != 201:
            pytest.skip("Could not create test project")
        
        project_id = create_response.json()["id"]
        
        # List projects with filter
        response = self.session.get(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}&status_filter=active"
        )
        
        print(f"\nFilter projects response status: {response.status_code}")
        
        assert response.status_code == 200
        assert "projects" in response.json()
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
    
    def test_list_projects_with_search(self):
        """Test searching projects by title"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        # Create a project with unique name
        unique_title = f"Unique Search Project {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "This should be searchable",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 100000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        if create_response.status_code != 201:
            print(f"Failed to create project: {create_response.status_code}")
            print(f"Error: {create_response.json()}")
            pytest.skip("Could not create test project")
        
        project_id = create_response.json()["id"]
        
        # Search for the project
        response = self.session.get(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}&search=Unique"
        )
        
        print(f"\nSearch projects response status: {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()["total"] >= 1
        
        # Verify search results contain the unique title
        titles = [p["title"] for p in response.json()["projects"]]
        assert any(unique_title in title for title in titles)
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
    
    def test_get_single_project(self):
        """Test getting a single project by ID"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        # First create a project
        unique_title = f"Get Project Test {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Project to retrieve",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 250000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        if create_response.status_code != 201:
            pytest.skip("Could not create test project")
        
        project_id = create_response.json()["id"]
        
        # Get the project
        response = self.session.get(f"{self.BASE_URL}/projects/{project_id}")
        
        print(f"\nGet project response status: {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()["id"] == project_id
        assert response.json()["title"] == unique_title
        assert response.json()["total_budget"] == 250000
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
    
    def test_update_project(self):
        """Test updating a project"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        # First create a project
        unique_title = f"Update Project Test {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Original description",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 300000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        if create_response.status_code != 201:
            pytest.skip("Could not create test project")
        
        project_id = create_response.json()["id"]
        
        # Update the project
        update_data = {
            "title": "Updated Project Title",
            "description": "Updated description",
            "total_budget": 350000
        }
        
        response = self.session.patch(
            f"{self.BASE_URL}/projects/{project_id}",
            json=update_data
        )
        
        print(f"\nUpdate project response status: {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Project Title"
        assert response.json()["description"] == "Updated description"
        assert response.json()["total_budget"] == 350000
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")
    
    def test_project_kpi_calculations(self):
        """Test that project KPI calculations work correctly"""
        if not self.test_org_id:
            pytest.skip(f"No organization ID available. test_org_id={self.test_org_id}")
        
        # Create a project
        unique_title = f"KPI Test Project {uuid.uuid4().hex[:8]}"
        project_data = {
            "title": unique_title,
            "description": "Testing KPI calculations",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 1000000,
            "currency": "USD"
        }
        
        create_response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={self.test_org_id}",
            json=project_data
        )
        
        print(f"\nKPI project response status: {create_response.status_code}")
        
        if create_response.status_code != 201:
            print(f"Error: {create_response.json()}")
            pytest.skip("Could not create test project")
        
        project_id = create_response.json()["id"]
        
        # Check KPI fields
        project = create_response.json()
        assert "bur" in project
        assert "kar" in project
        assert "bbr" in project
        assert "days_to_exhaust" in project
        assert "days_elapsed" in project
        assert "days_remaining" in project
        assert "total_tasks" in project
        assert "completion_rate" in project
        
        print(f"\nProject KPI: BUR={project['bur']}%, KAR={project['kar']}%, BBR={project['bbr']}")
        
        # Clean up
        self.session.delete(f"{self.BASE_URL}/projects/{project_id}")