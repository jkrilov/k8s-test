# MetalLB and Autoscaling Updates

## Summary of Changes

This document outlines the improvements made to the Kubernetes testing setup based on your requirements.

## 1. MetalLB LoadBalancer Support

**Changed:** Both blue and green services now use LoadBalancer type instead of ClusterIP.

**Files Modified:**
- `k8s/deployment.yaml` - Service type changed to LoadBalancer
- `k8s/green-deployment.yaml` - Service type changed to LoadBalancer

**Before:**
```yaml
type: ClusterIP
```

**After:**
```yaml
type: LoadBalancer  # Changed from ClusterIP to LoadBalancer for MetalLB
```

**Benefits:**
- No more need for `kubectl port-forward`
- Direct external access via MetalLB assigned IP addresses
- More realistic production-like setup

## 2. OpenAPI Bearer Token Authentication

**Changed:** Updated FastAPI to properly support Bearer token authentication in the OpenAPI (Swagger) interface.

**Files Modified:**
- `src/main.py` - Added OpenAPI security scheme configuration

**Changes Made:**
- Added custom OpenAPI schema with BearerAuth security scheme
- Updated `/auth/protected` endpoint with OpenAPI security metadata
- Users can now use the "Authorize" button in Swagger UI to enter JWT tokens

**How to Use:**
1. Visit `/docs` (Swagger UI)
2. Click the "Authorize" button
3. Enter your JWT token in the format: `your-jwt-token-here`
4. Test the protected endpoints directly from the UI

## 3. Horizontal Pod Autoscaling (HPA)

**Changed:** Both deployments now have HPA with consistent scaling parameters.

**Files Modified:**
- `k8s/configmap.yaml` - Updated existing HPA for blue deployment
- `k8s/green-deployment.yaml` - Added new HPA for green deployment

**HPA Configuration:**
- **Minimum Replicas:** 1 (both deployments)
- **Maximum Replicas:** 3 (both deployments)
- **CPU Target:** 70% utilization
- **Memory Target:** 80% utilization

**HPA Resources:**
- `k8s-test-hpa` - For blue deployment (`k8s-test-app`)
- `k8s-test-hpa-green` - For green deployment (`k8s-test-app-green`)

## 4. Resource Consistency

**Changed:** Both deployments now have matching CPU and memory configurations.

**Standardized Resources:**
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

**Replica Changes:**
- Blue deployment: 2 → 1 initial replica
- Green deployment: 3 → 1 initial replica
- Both will auto-scale from 1 to 3 based on load

## 5. Additional Updates

**PodDisruptionBudget:**
- Updated minimum available pods from 2 to 1 to work with new replica counts

## Deployment Commands

### Apply the blue deployment:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/configmap.yaml
```

### Apply the green deployment:
```bash
kubectl apply -f k8s/green-deployment.yaml
```

### Check services and get LoadBalancer IPs:
```bash
kubectl get services
kubectl get hpa
```

### Monitor scaling:
```bash
# Generate load to test autoscaling
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh

# Inside the pod:
while true; do wget -q -O- http://k8s-test-service/load-test/cpu; done
```

## Testing the Updates

1. **MetalLB:** Services should get external IPs automatically
2. **OpenAPI:** Visit `/docs` and use the Authorize button
3. **Autoscaling:** Generate load and watch HPA scale pods
4. **Blue/Green:** Both deployments have consistent resource allocation

## Notes

- Ensure MetalLB is properly configured in your cluster
- HPA requires metrics-server to be running
- Both deployments can run simultaneously for blue/green testing
- Use `kubectl get hpa -w` to watch autoscaling in real-time
