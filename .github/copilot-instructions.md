<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# K8s Test App - Copilot Instructions

This is a FastAPI application designed specifically for testing Kubernetes features. When working with this codebase, please follow these guidelines:

## Project Structure
- `src/main.py` - Main FastAPI application with all endpoints
- `tests/` - Unit tests using pytest
- `k8s/` - Kubernetes deployment manifests
- `pyproject.toml` - Project configuration using UV package manager
- `Dockerfile` - Container image using UV instead of pip

## API Endpoints Categories
1. **Health & Basic**: `/`, `/ping`, `/health`, `/version`
2. **Authentication**: `/auth/login`, `/auth/protected`
3. **Blue/Green Testing**: `/deployment/version`, `/deployment/blue`, `/deployment/green`
4. **Load Balancing**: `/load-test/info`, `/load-test/cpu`, `/load-test/memory`, `/load-test/async`
5. **Monitoring**: `/metrics`, `/observability/logs`, `/observability/trace`
6. **Error Testing**: `/error/500`, `/error/404`, `/error/timeout`

## Key Features
- JWT authentication using python-jose
- Prometheus metrics integration
- Comprehensive health checks
- Blue/green deployment simulation
- Load testing endpoints
- Error simulation for testing
- Async request handling
- CORS enabled for testing

## Dependencies
- FastAPI with uvicorn
- Pydantic for data validation
- python-jose for JWT tokens
- bcrypt for password hashing
- prometheus-client for metrics
- psutil for system information
- httpx for HTTP client functionality

## Testing
- Uses pytest with asyncio support
- TestClient for FastAPI testing
- Mock authentication for testing
- Coverage reporting configured
- Async test support

## Docker & Kubernetes
- Dockerfile uses UV package manager
- Multi-stage builds for optimization
- Non-root user for security
- Health checks configured
- Kubernetes manifests include:
  - Basic deployment with blue/green variants
  - Services and ingress
  - ConfigMaps and secrets
  - HPA and PDB for scaling
  - Monitoring with ServiceMonitor and PrometheusRule

## Development Guidelines
- Use UV for package management instead of pip
- Follow FastAPI best practices
- Include proper error handling
- Add comprehensive logging
- Use environment variables for configuration
- Include proper security measures
- Write tests for all endpoints
- Use type hints throughout the code

## Environment Variables
- `APP_VERSION` - Application version
- `APP_ENVIRONMENT` - Environment (dev/prod)
- `DEPLOYMENT_VERSION` - Blue/green deployment version
- `SECRET_KEY` - JWT secret key
- `LOG_LEVEL` - Logging level

When suggesting code changes or additions, ensure they align with the Kubernetes testing purpose and maintain the existing patterns and structure.
