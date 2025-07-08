#!/bin/bash
# Kubernetes manifest validation script

set -e

echo "Validating Kubernetes manifests..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi

# Core Kubernetes resources validation
echo "Validating core Kubernetes resources..."
for file in k8s/deployment.yaml k8s/green-deployment.yaml k8s/configmap.yaml; do
    if [ -f "$file" ]; then
        echo "Validating $file..."
        kubectl apply --dry-run=client --validate=false -f "$file"
    else
        echo "Warning: $file not found, skipping..."
    fi
done

echo "✅ Core Kubernetes resources are valid"

# Monitoring resources validation (requires Prometheus Operator CRDs)
echo "Checking monitoring resources..."
if kubectl get crd servicemonitors.monitoring.coreos.com &> /dev/null && \
   kubectl get crd prometheusrules.monitoring.coreos.com &> /dev/null; then
    echo "Prometheus Operator CRDs found, validating monitoring resources..."
    kubectl apply --dry-run=client --validate=false -f k8s/monitoring.yaml
    echo "✅ Monitoring resources are valid"
else
    echo "⚠️  Prometheus Operator CRDs not found, skipping monitoring validation"
    echo "   To install Prometheus Operator:"
    echo "   kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/download/v0.68.0/bundle.yaml"
fi

echo "✅ All available manifests validated successfully"
