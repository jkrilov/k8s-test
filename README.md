# FastAPI Kubernetes Testing Application

A comprehensive FastAPI application designed for testing various Kubernetes features including load balancing, authentication, blue/green deployments, and observability.

## Features

- **Health & Basic Endpoints**: Root, ping, health checks, version info
- **Authentication**: JWT-based authentication with protected endpoints
- **Blue/Green Testing**: Simulation of blue/green deployments
- **Load Balancing**: CPU intensive tasks, memory usage, async request handling
- **Monitoring**: Prometheus metrics, logging, tracing endpoints
- **Error Testing**: Simulated 500/404 errors and timeout scenarios
- **Observability**: Structured logging and trace generation

## API Endpoints

### Health & Basic
- `GET /` - Root endpoint with basic information
- `GET /ping` - Simple connectivity test
- `GET /health` - Comprehensive health check
- `GET /version` - Application version information

### Authentication
- `POST /auth/login` - User authentication (username: `testuser`, password: `testpassword`)
- `GET /auth/protected` - Protected endpoint requiring JWT token

### Blue/Green Deployment Testing
- `GET /deployment/version` - Current deployment version
- `GET /deployment/blue` - Blue deployment endpoint
- `GET /deployment/green` - Green deployment endpoint

### Load Balancing Tests
- `GET /load-test/info` - Instance information for load testing
- `GET /load-test/cpu` - CPU intensive task
- `GET /load-test/memory` - Memory usage information
- `GET /load-test/async` - Async task handling

### Monitoring & Observability
- `GET /metrics` - Prometheus metrics
- `GET /observability/logs` - Generate test logs
- `GET /observability/trace` - Distributed tracing simulation

### Error Testing
- `GET /error/500` - Always returns 500 error
- `GET /error/404` - Always returns 404 error
- `GET /error/timeout` - Simulates timeout (30 seconds)

## Quick Start

### Prerequisites
- Python 3.9+
- [UV](https://github.com/astral-sh/uv) package manager
- Docker (optional)
- Kubernetes cluster (for deployment)

### Installation & Running

```bash
# Clone the repository
git clone <repository-url>
cd k8s-test

# Install dependencies with UV
uv sync

# Run the application
uv run src/main.py

# Or run with uvicorn directly
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_main.py -v
```

### Authentication Testing

1. Login to get JWT token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword"}'
```

2. Use the token to access protected endpoints:
```bash
curl -X GET "http://localhost:8000/auth/protected" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Docker

```bash
# Build image
docker build -t k8s-test-app .

# Run container
docker run -p 8000:8000 k8s-test-app
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

## API Endpoints

### Health & Basic
- `GET /` - Root endpoint
- `GET /ping` - Simple ping test
- `GET /health` - Health check with detailed info
- `GET /version` - Application version info

### Authentication
- `POST /auth/login` - Get JWT token
- `GET /auth/protected` - Protected endpoint (requires token)

### Blue/Green Testing
- `GET /deployment/version` - Get current deployment version
- `GET /deployment/blue` - Blue deployment endpoint
- `GET /deployment/green` - Green deployment endpoint

### Load Balancing
- `GET /load-test/info` - Get instance information
- `GET /load-test/cpu` - CPU intensive task
- `GET /load-test/memory` - Memory usage info

### Monitoring
- `GET /metrics` - Prometheus metrics
- `GET /observability/logs` - Generate test logs

## Environment Variables

- `APP_VERSION` - Application version (default: "1.0.0")
- `APP_ENVIRONMENT` - Environment (default: "development")
- `SECRET_KEY` - JWT secret key
- `LOG_LEVEL` - Logging level (default: "INFO")

## Kubernetes Deployment

See the `k8s/` directory for example Kubernetes manifests.

## Development

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```
