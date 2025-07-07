# 🚀 MicroK8s Deployment Guide

This guide will help you deploy the K8s Test App to your MicroK8s cluster.

## Prerequisites
- MicroK8s installed and running
- Docker installed (for building images)
- kubectl or microk8s.kubectl access

## Quick Deployment Steps

### Step 1: Enable MicroK8s Addons
```bash
# On your MicroK8s server
microk8s enable ingress
microk8s enable metrics-server

# Optional: Enable monitoring
# microk8s enable prometheus
```

### Step 2: Build and Push Docker Image

#### Option A: Build on the same server as MicroK8s
```bash
# Clone/copy the project to your MicroK8s server
cd /path/to/k8s-test
docker build -t localhost:32000/k8s-test-app:latest .
docker push localhost:32000/k8s-test-app:latest
```

#### Option B: Build locally and transfer
```bash
# On your local machine
docker build -t localhost:32000/k8s-test-app:latest .
docker save localhost:32000/k8s-test-app:latest | gzip > k8s-test-app.tar.gz

# Transfer to server
scp k8s-test-app.tar.gz user@your-server:~

# On MicroK8s server
gunzip -c k8s-test-app.tar.gz | docker load
docker push localhost:32000/k8s-test-app:latest
```

### Step 3: Deploy to Kubernetes
```bash
# Apply all manifests
microk8s kubectl apply -f k8s/

# Wait for deployment to be ready
microk8s kubectl wait --for=condition=available --timeout=300s deployment/k8s-test-app
```

### Step 4: Verify Deployment
```bash
# Check pods
microk8s kubectl get pods

# Check services
microk8s kubectl get services

# Check ingress
microk8s kubectl get ingress

# View logs
microk8s kubectl logs -l app=k8s-test-app
```

### Step 5: Access the Application

#### Option A: Port Forward (Easiest)
```bash
microk8s kubectl port-forward service/k8s-test-service 8080:80
```
Then access: http://localhost:8080

#### Option B: Ingress (More realistic)
1. Add to your hosts file (`/etc/hosts` or `C:\Windows\System32\drivers\etc\hosts`):
   ```
   <YOUR_SERVER_IP> k8s-test.local
   ```
2. Access: http://k8s-test.local

#### Option C: NodePort (If ingress doesn't work)
```bash
# Edit the service to use NodePort
microk8s kubectl patch service k8s-test-service -p '{"spec":{"type":"NodePort"}}'

# Get the NodePort
microk8s kubectl get service k8s-test-service
```
Then access: http://<YOUR_SERVER_IP>:<NODEPORT>

## Test Endpoints

Once deployed, test these endpoints:

- **Health**: `/health`
- **API Docs**: `/docs`
- **Metrics**: `/metrics`
- **Ping**: `/ping`
- **Blue Deployment**: `/deployment/blue`
- **Load Test**: `/load-test/info`
- **Auth Login**: POST `/auth/login` with `{"username": "testuser", "password": "testpassword"}`

## Blue/Green Deployment Testing

### Deploy Green Version
```bash
# Deploy green version
microk8s kubectl apply -f k8s/green-deployment.yaml

# Switch traffic to green (edit ingress or service selector)
microk8s kubectl patch service k8s-test-service -p '{"spec":{"selector":{"version":"green"}}}'

# Test green deployment
curl http://k8s-test.local/deployment/green
```

### Switch Back to Blue
```bash
microk8s kubectl patch service k8s-test-service -p '{"spec":{"selector":{"app":"k8s-test-app"}}}'
```

## Monitoring and Debugging

### View Logs
```bash
# All pods
microk8s kubectl logs -l app=k8s-test-app

# Specific pod
microk8s kubectl logs <pod-name>

# Follow logs
microk8s kubectl logs -f -l app=k8s-test-app
```

### Debug Pod Issues
```bash
# Describe pod
microk8s kubectl describe pod <pod-name>

# Get events
microk8s kubectl get events --sort-by=.metadata.creationTimestamp

# Check resource usage
microk8s kubectl top pods
```

### Access Pod Shell
```bash
microk8s kubectl exec -it <pod-name> -- /bin/sh
```

## Load Testing

### Simple Load Test
```bash
# Install hey if not available
# go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 http://k8s-test.local/load-test/cpu
```

### Test Auto-scaling
```bash
# Generate load to trigger HPA
for i in {1..10}; do
  curl http://k8s-test.local/load-test/cpu &
done

# Watch HPA
microk8s kubectl get hpa -w
```

## Cleanup
```bash
# Remove all resources
microk8s kubectl delete -f k8s/

# Or remove everything in default namespace
microk8s kubectl delete all --all
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Ensure image is pushed to MicroK8s registry: `localhost:32000`
   - Check registry: `curl http://localhost:32000/v2/_catalog`

2. **Ingress Not Working**
   - Ensure ingress addon is enabled
   - Check ingress controller: `microk8s kubectl get pods -n ingress`

3. **Pods Not Starting**
   - Check events: `microk8s kubectl get events`
   - Check pod logs: `microk8s kubectl logs <pod-name>`

4. **Service Not Accessible**
   - Verify service endpoints: `microk8s kubectl get endpoints`
   - Check if pods are ready: `microk8s kubectl get pods`

### Useful Commands
```bash
# Get cluster info
microk8s kubectl cluster-info

# Get all resources
microk8s kubectl get all

# Check resource usage
microk8s kubectl top nodes
microk8s kubectl top pods

# Port forward for debugging
microk8s kubectl port-forward <pod-name> 8080:8000
```

Happy testing! 🎉
