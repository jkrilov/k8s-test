# PowerShell script for deploying to MicroK8s from Windows
# Run this script from the project directory

Write-Host "🚀 Deploying K8s Test App to MicroK8s..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Build Docker image
Write-Host "🐳 Building Docker image..." -ForegroundColor Yellow
docker build -t localhost:32000/k8s-test-app:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# Instructions for MicroK8s server
Write-Host ""
Write-Host "📋 Now run these commands on your MicroK8s server:" -ForegroundColor Cyan
Write-Host ""
Write-Host "# 1. Enable required addons" -ForegroundColor White
Write-Host "microk8s enable ingress" -ForegroundColor Gray
Write-Host "microk8s enable metrics-server" -ForegroundColor Gray
Write-Host ""
Write-Host "# 2. Save and push the Docker image" -ForegroundColor White
Write-Host "# From your Windows machine, save the image:" -ForegroundColor White
Write-Host "docker save localhost:32000/k8s-test-app:latest | gzip > k8s-test-app.tar.gz" -ForegroundColor Gray
Write-Host "# Copy to server and load:" -ForegroundColor White
Write-Host "# scp k8s-test-app.tar.gz user@server:" -ForegroundColor Gray
Write-Host "# gunzip -c k8s-test-app.tar.gz | docker load" -ForegroundColor Gray
Write-Host "# docker tag localhost:32000/k8s-test-app:latest localhost:32000/k8s-test-app:latest" -ForegroundColor Gray
Write-Host "# docker push localhost:32000/k8s-test-app:latest" -ForegroundColor Gray
Write-Host ""
Write-Host "# 3. Deploy the application" -ForegroundColor White
Write-Host "microk8s kubectl apply -f k8s/" -ForegroundColor Gray
Write-Host ""
Write-Host "# 4. Check deployment status" -ForegroundColor White
Write-Host "microk8s kubectl get pods" -ForegroundColor Gray
Write-Host "microk8s kubectl get services" -ForegroundColor Gray
Write-Host ""
Write-Host "# 5. Access the application" -ForegroundColor White
Write-Host "microk8s kubectl port-forward service/k8s-test-service 8080:80" -ForegroundColor Gray
Write-Host "# Then access: http://localhost:8080" -ForegroundColor Gray

Write-Host ""
Write-Host "✅ Local preparation complete!" -ForegroundColor Green
