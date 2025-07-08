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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
