#!/bin/bash
# MicroK8s Deployment Script for K8s Test App

set -e

echo "🚀 Deploying K8s Test App to MicroK8s..."

# Enable required addons
echo "📦 Enabling MicroK8s addons..."
microk8s enable ingress
microk8s enable metrics-server
microk8s enable prometheus  # Optional: for monitoring

# Wait for addons to be ready
echo "⏳ Waiting for addons to be ready..."
microk8s kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=nginx-ingress --namespace=ingress -w --timeout=300s

# Build and push image to MicroK8s registry
echo "🐳 Building Docker image..."
docker build -t localhost:32000/k8s-test-app:latest .

echo "📤 Pushing image to MicroK8s registry..."
docker push localhost:32000/k8s-test-app:latest

# Apply Kubernetes manifests
echo "⚙️  Applying Kubernetes manifests..."
microk8s kubectl apply -f k8s/

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
microk8s kubectl wait --for=condition=available --timeout=300s deployment/k8s-test-app

# Get service information
echo "🔍 Getting service information..."
microk8s kubectl get services
microk8s kubectl get ingress

# Get pod information
echo "📋 Getting pod information..."
microk8s kubectl get pods -o wide

echo "✅ Deployment completed!"
echo ""
echo "🌐 Access your application:"
echo "   - Add '127.0.0.1 k8s-test.local' to your /etc/hosts file (or C:\\Windows\\System32\\drivers\\etc\\hosts on Windows)"
echo "   - Then access: http://k8s-test.local"
echo ""
echo "📊 Useful commands:"
echo "   - Check pods: microk8s kubectl get pods"
echo "   - Check logs: microk8s kubectl logs deployment/k8s-test-app"
echo "   - Port forward: microk8s kubectl port-forward service/k8s-test-service 8080:80"
