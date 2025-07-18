# MicroK8s Deployment Commands for K8s Test App
# Run these commands on your MicroK8s server

# 1. Enable required addons
microk8s enable ingress
microk8s enable metrics-server

# Optional: Enable Prometheus for monitoring
sudo microk8s enable prometheus

# 2. Wait for ingress to be ready
microk8s kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=nginx-ingress --namespace=ingress --timeout=300s

# 3. Build and push Docker image (run from your project directory)
sudo docker build -t localhost:32000/k8s-test-app:latest .
sudo docker push localhost:32000/k8s-test-app:latest

# 4. Apply Kubernetes manifests
sudo microk8s kubectl apply -f k8s/

# 5. Wait for deployment
microk8s kubectl wait --for=condition=available --timeout=300s deployment/k8s-test-app

# 6. Check status
sudo microk8s kubectl get pods
sudo microk8s kubectl get services
sudo microk8s kubectl get ingress

# 7. Test the application
# Option A: Port forward
sudo microk8s kubectl port-forward service/k8s-test-service 8080:80

# Option B: Add to hosts file and use ingress
# Add this line to /etc/hosts: 127.0.0.1 k8s-test.local
# Then access: http://k8s-test.local

# Useful debugging commands:
# microk8s kubectl describe pod [POD_NAME]
# microk8s kubectl logs deployment/k8s-test-app
# microk8s kubectl get events --sort-by=.metadata.creationTimestamp
