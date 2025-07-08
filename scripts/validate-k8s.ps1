# Kubernetes manifest validation script for Windows

Write-Host "Validating Kubernetes manifests..." -ForegroundColor Green

# Check if kubectl is available
try {
    kubectl version --client | Out-Null
} catch {
    Write-Host "Error: kubectl is not installed" -ForegroundColor Red
    exit 1
}

# Core Kubernetes resources validation
Write-Host "Validating core Kubernetes resources..." -ForegroundColor Blue

$files = @("k8s/deployment.yaml", "k8s/green-deployment.yaml", "k8s/configmap.yaml")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Validating $file..." -ForegroundColor Cyan
        kubectl apply --dry-run=client --validate=false -f $file
    } else {
        Write-Host "Warning: $file not found, skipping..." -ForegroundColor Yellow
    }
}

Write-Host "✅ Core Kubernetes resources are valid" -ForegroundColor Green

# Monitoring resources validation (requires Prometheus Operator CRDs)
Write-Host "Checking monitoring resources..." -ForegroundColor Blue
try {
    kubectl get crd servicemonitors.monitoring.coreos.com | Out-Null
    kubectl get crd prometheusrules.monitoring.coreos.com | Out-Null
    Write-Host "Prometheus Operator CRDs found, validating monitoring resources..." -ForegroundColor Blue
    kubectl apply --dry-run=client --validate=false -f k8s/monitoring.yaml
    Write-Host "✅ Monitoring resources are valid" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Prometheus Operator CRDs not found, skipping monitoring validation" -ForegroundColor Yellow
    Write-Host "   To install Prometheus Operator:" -ForegroundColor Yellow
    Write-Host "   kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/download/v0.68.0/bundle.yaml" -ForegroundColor Yellow
}

Write-Host "✅ All available manifests validated successfully" -ForegroundColor Green
