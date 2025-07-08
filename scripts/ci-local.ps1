# Local CI test script for Windows

Write-Host "Running local CI tests..." -ForegroundColor Green

Write-Host "1. Installing dependencies..." -ForegroundColor Blue
uv sync --all-extras --dev

Write-Host "2. Running linting..." -ForegroundColor Blue
uv run black --check src/ tests/
uv run isort --check-only src/ tests/

Write-Host "3. Running tests..." -ForegroundColor Blue
uv run pytest tests/ -v --cov=src

Write-Host "4. Running security scan..." -ForegroundColor Blue
uv run bandit -r src/ -s B104

Write-Host "5. Testing Docker build..." -ForegroundColor Blue
docker build -t k8s-test-app:latest .

Write-Host "6. Validating Kubernetes manifests..." -ForegroundColor Blue
./scripts/validate-k8s.ps1

Write-Host "✅ All local CI tests passed!" -ForegroundColor Green
