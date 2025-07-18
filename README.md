# FastAPI Kubernetes Testing Application

[![CI](https://github.com/jkrilov/k8s-test/actions/workflows/ci.yml/badge.svg)](https://github.com/jkrilov/k8s-test/actions/workflows/ci.yml)

[![Release](https://github.com/jkrilov/k8s-test/actions/workflows/release.yml/badge.svg)](https://github.com/jkrilov/k8s-test/actions/workflows/release.yml)

[![codecov](https://codecov.io/github/jkrilov/k8s-test/graph/badge.svg?token=DJENLUL7E6)](https://codecov.io/github/jkrilov/k8s-test)

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
- Python 3.11+
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

## Docker & Kubernetes Deployment

### 🐳 Docker

**Build and run locally**:
```bash
# Build image
docker build -t k8s-test-app:latest .

# Run container
docker run -p 8000:8000 k8s-test-app:latest

# Test container
curl http://localhost:8000/health
```

**Pull from GitHub Container Registry**:
```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/k8s-test:latest

# Run from registry
docker run -p 8000:8000 ghcr.io/YOUR_USERNAME/k8s-test:latest
```

### ☸️ Kubernetes

**Quick deployment**:
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=k8s-test-app

# Get service URL
kubectl get svc k8s-test-service
```

**Available manifests in `k8s/`**:
- `deployment.yaml` - Main application deployment (blue)
- `green-deployment.yaml` - Green deployment for blue/green testing
- `configmap.yaml` - Configuration management
- `monitoring.yaml` - Prometheus ServiceMonitor and PrometheusRule

**MicroK8s deployment**:
```bash
# See detailed MicroK8s deployment guide
cat MICROK8S_DEPLOY.md

# Quick MicroK8s deployment
./deploy-microk8s.sh      # Linux
./deploy-windows.ps1      # Windows
```

### 🌐 Environment Variables

- `APP_VERSION` - Application version (default: "1.1.0")
- `APP_ENVIRONMENT` - Environment (default: "development")
- `DEPLOYMENT_VERSION` - Blue/green deployment version (default: "blue")
- `SECRET_KEY` - JWT secret key (change in production!)
- `LOG_LEVEL` - Logging level (default: "INFO")

## CI/CD & Automation

This project includes comprehensive GitHub Actions workflows for automated testing, building, and deployment:

### 🚀 Continuous Integration (`.github/workflows/ci.yml`)
**Triggers**: Push to `main`/`develop`, Pull Requests

**Jobs**:
- **Multi-Python Testing**: Runs tests on Python 3.11 and 3.12
- **Code Quality Checks**: 
  - Black code formatting validation
  - isort import sorting verification
- **Test Coverage**: pytest execution with coverage reporting to Codecov
- **Security Scanning**: Bandit security vulnerability analysis
- **Docker Build**: Container image build and health check validation
- **Kubernetes Validation**: Manifest validation using kubeval

### 🏷️ Release Automation (`.github/workflows/release.yml`)
**Triggers**: Git tags (`v*`), Manual dispatch

**Features**:
- **Automated Releases**: Creates GitHub releases with changelog
- **Container Registry**: Publishes to GitHub Container Registry (`ghcr.io`)
- **Multi-arch Support**: Cross-platform Docker builds
- **Version Management**: Semantic versioning with multiple tag formats
- **Release Notes**: Auto-generated release documentation

### 🔄 Dependency Management (`.github/workflows/dependency-updates.yml`)
**Triggers**: Weekly schedule (Mondays 2 AM UTC), Manual dispatch

**Features**:
- **Automated Updates**: Weekly dependency updates using UV
- **Automated PRs**: Creates pull requests for dependency updates
- **Test Validation**: Ensures updates don't break functionality
- **Conflict Resolution**: Handles dependency conflicts automatically

### 🏃‍♂️ Local Development

**Pre-commit Hooks**: Install with `pre-commit install`
- Code formatting (Black, isort)
- Security scanning (Bandit)
- Type checking (mypy)
- YAML/TOML validation

**Local CI Testing**:
```bash
# Linux/macOS
./scripts/ci-local.sh

# Windows PowerShell
./scripts/ci-local.ps1
```

**Kubernetes Validation**:
```bash
# Linux/macOS
./scripts/validate-k8s.sh

# Windows PowerShell
./scripts/validate-k8s.ps1
```

### 📊 Quality Metrics

The CI pipeline provides comprehensive quality metrics:
- **Code Coverage**: Tracked via Codecov (optional, requires `CODECOV_TOKEN` secret)
- **Security Scanning**: Bandit analysis with custom rules
- **Type Safety**: mypy static type checking
- **Code Quality**: Black formatting and isort import organization

**Setting up Codecov** (optional):
1. Sign up at [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. Add `CODECOV_TOKEN` to your GitHub repository secrets
4. The coverage badge will start working after the first successful upload

### 🔄 Workflow Status

## Development

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Security scan
uv run bandit -r src/ -s B104
```

## 📁 Project Structure

```
k8s-test/
├── .github/
│   ├── workflows/           # GitHub Actions CI/CD workflows
│   └── copilot-instructions.md
├── k8s/                     # Kubernetes manifests
│   ├── deployment.yaml      # Main application deployment
│   ├── green-deployment.yaml # Blue/green deployment
│   ├── configmap.yaml       # Configuration
│   └── monitoring.yaml      # Prometheus monitoring
├── scripts/                 # Utility scripts
│   ├── ci-local.sh          # Local CI testing (Linux/macOS)
│   ├── ci-local.ps1         # Local CI testing (Windows)
│   ├── deploy-microk8s.sh   # MicroK8s deployment
│   └── deploy-windows.ps1   # Windows deployment
├── src/                     # Source code
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_main.py         # Unit tests
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .bandit                  # Security scanning config
├── Dockerfile               # Container image
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── Makefile                 # Build automation
└── README.md                # This file
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Install dependencies**: `uv sync --all-extras --dev`
4. **Install pre-commit hooks**: `pre-commit install`
5. **Make your changes**
6. **Run tests**: `uv run pytest`
7. **Run local CI**: `./scripts/ci-local.sh` or `./scripts/ci-local.ps1`
8. **Commit changes**: `git commit -m 'Add amazing feature'`
9. **Push to branch**: `git push origin feature/amazing-feature`
10. **Create Pull Request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for modern Python web APIs
- Uses [UV](https://github.com/astral-sh/uv) for fast Python package management
- Kubernetes manifests for cloud-native deployment
- Comprehensive CI/CD with GitHub Actions
- Security scanning with [Bandit](https://bandit.readthedocs.io/)
- Code quality with [Black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/)
