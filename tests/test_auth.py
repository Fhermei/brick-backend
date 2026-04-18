"""
Test authentication endpoints - Login only
"""

import pytest
import requests


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_login_success(self):
        """Test successful login with existing credentials"""
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        
        response = requests.post(f"{self.BASE_URL}/auth/login", json=login_data)
        
        print(f"\nLogin response status: {response.status_code}")
        print(f"Login response: {response.json()}")
        
        assert response.status_code == 200
        assert "Login successful" in response.json()["message"]
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
    
    def test_login_wrong_password(self):
        """Test login with incorrect password"""
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "WrongPassword123"
        }
        
        response = requests.post(f"{self.BASE_URL}/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_wrong_email(self):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Fatunbi11."
        }
        
        response = requests.post(f"{self.BASE_URL}/auth/login", json=login_data)
        
        assert response.status_code == 401
        # Security: should not reveal if email exists
        assert "email" in response.json()["detail"].lower() or "password" in response.json()["detail"].lower()
    
    def test_get_current_user(self, session):
        """Test getting current user info after login"""
        response = session.get(f"{self.BASE_URL}/auth/me")
        
        assert response.status_code == 200
        assert response.json()["email"] == "oyewoleoluwafemidavid1@gmail.com"
        assert "name" in response.json()
        assert "id" in response.json()
    
    def test_get_current_user_unauthenticated(self):
        """Test getting current user without authentication"""
        response = requests.get(f"{self.BASE_URL}/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_logout(self, session):
        """Test logout functionality"""
        response = session.post(f"{self.BASE_URL}/auth/logout")
        
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]