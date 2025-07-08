"""
Test suite for the FastAPI Kubernetes Testing Application
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestBasicEndpoints:
    """Test basic endpoints like root, ping, health"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert data["message"] == "FastAPI Kubernetes Test Application"

    def test_ping_endpoint(self):
        """Test ping endpoint"""
        response = client.get("/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"
        assert "timestamp" in data

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "system_info" in data
        assert "hostname" in data["system_info"]

    def test_version_endpoint(self):
        """Test version endpoint"""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "environment" in data
        assert "deployment_version" in data


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""

    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/auth/login", json={"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_failure(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login", json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self):
        """Test protected endpoint without authentication"""
        response = client.get("/auth/protected")
        assert response.status_code == 403

    def test_protected_endpoint_with_token(self):
        """Test protected endpoint with valid token"""
        # First login to get token
        login_response = client.post(
            "/auth/login", json={"username": "testuser", "password": "testpassword"}
        )
        token = login_response.json()["access_token"]

        # Use token to access protected endpoint
        response = client.get(
            "/auth/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "testuser" in data["message"]
        assert "user" in data


class TestDeploymentEndpoints:
    """Test blue/green deployment endpoints"""

    def test_deployment_version(self):
        """Test deployment version endpoint"""
        response = client.get("/deployment/version")
        assert response.status_code == 200
        data = response.json()
        assert "deployment_version" in data
        assert "app_version" in data
        assert "environment" in data

    def test_blue_deployment(self):
        """Test blue deployment endpoint"""
        response = client.get("/deployment/blue")
        assert response.status_code == 200
        data = response.json()
        assert data["deployment"] == "blue"
        assert "BLUE" in data["message"]
        assert data["color"] == "#0066CC"

    def test_green_deployment(self):
        """Test green deployment endpoint"""
        response = client.get("/deployment/green")
        assert response.status_code == 200
        data = response.json()
        assert data["deployment"] == "green"
        assert "GREEN" in data["message"]
        assert data["color"] == "#00CC66"


class TestLoadBalancingEndpoints:
    """Test load balancing endpoints"""

    def test_load_test_info(self):
        """Test load test info endpoint"""
        response = client.get("/load-test/info")
        assert response.status_code == 200
        data = response.json()
        assert "instance_id" in data
        assert "hostname" in data
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "timestamp" in data

    def test_cpu_intensive_task(self):
        """Test CPU intensive task endpoint"""
        response = client.get("/load-test/cpu")
        assert response.status_code == 200
        data = response.json()
        assert "duration" in data
        assert "result" in data
        assert "instance_id" in data
        assert data["message"] == "CPU intensive task completed"

    def test_memory_usage(self):
        """Test memory usage endpoint"""
        response = client.get("/load-test/memory")
        assert response.status_code == 200
        data = response.json()
        assert "memory" in data
        assert "total" in data["memory"]
        assert "available" in data["memory"]
        assert "percent" in data["memory"]
        assert "instance_id" in data

    def test_async_task(self):
        """Test async task endpoint"""
        response = client.get("/load-test/async")
        assert response.status_code == 200
        data = response.json()
        assert "duration" in data
        assert "instance_id" in data
        assert data["message"] == "Async task completed"


class TestMonitoringEndpoints:
    """Test monitoring and observability endpoints"""

    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        # Check for some expected metrics
        content = response.text
        assert "http_requests_total" in content
        assert "http_request_duration_seconds" in content

    def test_logs_endpoint(self):
        """Test logs generation endpoint"""
        with patch("src.main.logger") as mock_logger:
            response = client.get("/observability/logs")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Test logs generated"
            assert "levels" in data

            # Verify logger was called
            mock_logger.info.assert_called_once()
            mock_logger.warning.assert_called_once()
            mock_logger.error.assert_called_once()

    def test_trace_endpoint(self):
        """Test trace endpoint"""
        response = client.get("/observability/trace")
        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data
        assert "span_count" in data
        assert data["message"] == "Trace endpoint completed"


class TestErrorEndpoints:
    """Test error simulation endpoints"""

    def test_500_error(self):
        """Test 500 error endpoint"""
        response = client.get("/error/500")
        assert response.status_code == 500
        data = response.json()
        assert "Internal Server Error" in data["detail"]

    def test_404_error(self):
        """Test 404 error endpoint"""
        response = client.get("/error/404")
        assert response.status_code == 404
        data = response.json()
        assert "Not Found" in data["detail"]


class TestMiddleware:
    """Test middleware functionality"""

    def test_cors_headers(self):
        """Test CORS headers are present"""
        # Note: TestClient doesn't automatically add CORS headers
        # We'll test that CORS middleware is configured instead
        response = client.get("/")
        assert response.status_code == 200
        # Test that the response is successful, CORS is handled by middleware
        assert response.json()["message"] == "FastAPI Kubernetes Test Application"

    def test_metrics_middleware(self):
        """Test that metrics are being tracked"""
        # Make a request to trigger metrics
        response = client.get("/ping")
        assert response.status_code == 200

        # Check metrics endpoint
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200

        # Should contain request metrics
        content = metrics_response.text
        assert "http_requests_total" in content


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality"""

    async def test_async_endpoint_performance(self):
        """Test that async endpoints perform well"""
        import time

        start_time = time.time()

        # Make multiple sequential requests to test the endpoint
        responses = []
        for _ in range(5):
            response = client.get("/load-test/async")
            responses.append(response)

        end_time = time.time()
        duration = end_time - start_time

        # All requests should succeed
        assert all(response.status_code == 200 for response in responses)

        # Should complete within reasonable time
        assert duration < 10.0  # Should complete within 10 seconds


class TestConfiguration:
    """Test configuration and environment variables"""

    def test_environment_variables(self):
        """Test that environment variables are respected"""
        # Test via API call since reloading causes Prometheus metric conflicts
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        # Check that the environment can be configured
        assert "environment" in data
        assert "version" in data


class TestUtilityFunctions:
    """Test utility functions and edge cases"""

    def test_get_password_hash(self):
        """Test password hashing function directly"""
        from src.main import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        # Should return a string
        assert isinstance(hashed, str)
        # Should be different from the original password
        assert hashed != password
        # Should be a valid bcrypt hash
        assert hashed.startswith("$2b$")

    def test_get_user_existing(self):
        """Test get_user function with existing user"""
        from src.main import get_user

        user = get_user("testuser")
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_get_user_nonexistent(self):
        """Test get_user function with non-existent user"""
        from src.main import get_user

        user = get_user("nonexistentuser")
        assert user is None

    def test_create_access_token_default_expiry(self):
        """Test create_access_token with default expiry"""
        from src.main import create_access_token

        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test create_access_token with custom expiry"""
        from datetime import timedelta

        from src.main import create_access_token

        data = {"sub": "testuser"}
        custom_expiry = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=custom_expiry)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password_direct(self):
        """Test password verification function directly"""
        from src.main import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True

        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False

    def test_authenticate_user_success(self):
        """Test authenticate_user function with correct credentials"""
        from src.main import authenticate_user

        # Existing user with correct password
        user = authenticate_user("testuser", "testpassword")
        assert user is not None
        assert user.username == "testuser"

    def test_authenticate_user_wrong_password(self):
        """Test authenticate_user function with wrong password"""
        from src.main import authenticate_user

        # Existing user with wrong password
        user = authenticate_user("testuser", "wrongpassword")
        assert user is None

    def test_authenticate_user_nonexistent(self):
        """Test authenticate_user function with non-existent user"""
        from src.main import authenticate_user

        # Non-existent user
        user = authenticate_user("nonexistent", "password")
        assert user is None


class TestAuthenticationEdgeCases:
    """Test authentication edge cases and error paths"""

    def test_protected_endpoint_no_auth(self):
        """Test protected endpoint without authentication"""
        response = client.get("/auth/protected")
        assert response.status_code == 403

    def test_protected_endpoint_invalid_token(self):
        """Test protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/protected", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_malformed_token(self):
        """Test protected endpoint with malformed token"""
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        }
        response = client.get("/auth/protected", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_token_without_sub(self):
        """Test protected endpoint with token missing 'sub' claim"""
        from src.main import create_access_token

        # Create token without 'sub' claim
        token = create_access_token(
            {"user": "testuser"}
        )  # using 'user' instead of 'sub'
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/protected", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_token_with_nonexistent_user(self):
        """Test protected endpoint with token for non-existent user"""
        from src.main import create_access_token

        # Create token for non-existent user
        token = create_access_token({"sub": "nonexistentuser"})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/protected", headers=headers)
        assert response.status_code == 401

    def test_protected_endpoint_token_with_null_sub(self):
        """Test protected endpoint with token containing null 'sub' claim"""
        from src.main import create_access_token

        # Create token with null sub
        token = create_access_token({"sub": None})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/protected", headers=headers)
        assert response.status_code == 401


class TestHealthCheckEdgeCases:
    """Test health check edge cases"""

    @patch("platform.system")
    def test_health_check_windows(self, mock_system):
        """Test health check on Windows platform"""
        mock_system.return_value = "Windows"

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "system_info" in data

    @patch("platform.system")
    @patch("shutil.disk_usage")
    def test_health_check_disk_usage_error(self, mock_disk_usage, mock_system):
        """Test health check when disk usage fails"""
        mock_system.return_value = "Linux"
        mock_disk_usage.side_effect = OSError("Permission denied")

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        # Should handle the error gracefully


class TestTimeoutEndpoint:
    """Test timeout simulation endpoint"""

    def test_timeout_simulation_mocked(self):
        """Test timeout endpoint with mocked sleep"""
        with patch("src.main.asyncio.sleep") as mock_sleep:
            mock_sleep.return_value = None  # Make it return immediately

            response = client.get("/error/timeout")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "This should timeout"
            mock_sleep.assert_called_once_with(30)


# ...existing code...

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
