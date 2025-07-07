# Makefile for K8s Test App

.PHONY: help install test lint format run docker-build docker-run k8s-deploy k8s-cleanup

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies using UV"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo "  run          - Run the application locally"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  k8s-deploy   - Deploy to Kubernetes"
	@echo "  k8s-cleanup  - Clean up Kubernetes resources"

# Install dependencies
install:
	uv sync
	uv sync --group dev

# Run tests
test:
	uv run pytest -v --cov=src --cov-report=html --cov-report=term-missing

# Run linters
lint:
	uv run flake8 src/ tests/
	uv run mypy src/

# Format code
format:
	uv run black src/ tests/
	uv run isort src/ tests/

# Run application locally
run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
docker-build:
	docker build -t k8s-test-app:latest .

# Run Docker container
docker-run:
	docker run -p 8000:8000 --rm k8s-test-app:latest

# Deploy to Kubernetes
k8s-deploy:
	kubectl apply -f k8s/

# Clean up Kubernetes resources
k8s-cleanup:
	kubectl delete -f k8s/

# Load test endpoints
load-test:
	@echo "Running basic load test..."
	@for i in {1..10}; do \
		curl -s http://localhost:8000/load-test/info > /dev/null & \
	done
	@wait
	@echo "Load test completed"

# Test authentication
test-auth:
	@echo "Testing authentication..."
	@TOKEN=$$(curl -s -X POST http://localhost:8000/auth/login \
		-H "Content-Type: application/json" \
		-d '{"username": "testuser", "password": "testpassword"}' | \
		jq -r '.access_token'); \
	curl -H "Authorization: Bearer $$TOKEN" http://localhost:8000/auth/protected

# Test blue/green deployments
test-deployments:
	@echo "Testing blue deployment..."
	@curl -s http://localhost:8000/deployment/blue | jq
	@echo "Testing green deployment..."
	@curl -s http://localhost:8000/deployment/green | jq
