# Quick Deployment Guide

This guide provides the essential commands to quickly deploy the Redis Enterprise Web Application.

## Prerequisites Checklist

- [ ] Kubernetes cluster running
- [ ] Redis Enterprise Operator installed
- [ ] Redis Enterprise Cluster (REC) deployed
- [ ] `kubectl` configured and working

## Quick Commands

### 1. Create Namespace
```bash
kubectl create namespace app-naresh
```

### 2. Deploy Redis Database
```bash
kubectl apply -f kubernetes/mydb-second.yaml
```

### 3. Wait for Database
```bash
kubectl get redisenterprisedatabase mydbsecond -n rec-naresh -w
```

### 4. Get Connection Details
```bash
# Get password
kubectl get secret redb-mydbsecond -n rec-naresh -o jsonpath='{.data.password}' | base64 -d

# Get port
kubectl get secret redb-mydbsecond -n rec-naresh -o jsonpath='{.data.port}' | base64 -d
```

### 5. Deploy Application Pod
```bash
kubectl apply -f kubernetes/python-redis-pod.yaml
```

### 6. Copy Files to Pod
```bash
kubectl exec -n app-naresh python-redis-pod -- mkdir -p /app/templates

kubectl cp redis-app.py app-naresh/python-redis-pod:/app/redis-app.py
kubectl cp templates/index.html app-naresh/python-redis-pod:/app/templates/index.html
kubectl cp requirements.txt app-naresh/python-redis-pod:/app/requirements.txt
kubectl cp certificates/client_cert.pem app-naresh/python-redis-pod:/app/client_cert.pem
kubectl cp certificates/client_key.pem app-naresh/python-redis-pod:/app/client_key.pem
```

### 7. Install Dependencies
```bash
kubectl exec -n app-naresh python-redis-pod -- pip install -r /app/requirements.txt
kubectl exec -n app-naresh python-redis-pod -- apt-get update
kubectl exec -n app-naresh python-redis-pod -- apt-get install -y redis-tools
```

### 8. Update Configuration
Edit `redis-app.py` with your actual connection details:
- REDIS_HOST
- REDIS_PORT  
- REDIS_PASSWORD

### 9. Start Application
```bash
kubectl exec -n app-naresh python-redis-pod -- bash -c "cd /app && python redis-app.py &"
```

### 10. Expose with LoadBalancer
```bash
kubectl apply -f kubernetes/redis-app-service.yaml
```

### 11. Get External IP
```bash
kubectl get service redis-app-loadbalancer -n app-naresh
```

## Verification

### Test Redis Connection
```bash
kubectl exec -n app-naresh python-redis-pod -- redis-cli \
  -h mydbsecond-headless.rec-naresh.svc.cluster.local \
  -p YOUR_PORT \
  --tls --insecure \
  --cert /app/client_cert.pem \
  --key /app/client_key.pem \
  --user default \
  -a 'YOUR_PASSWORD' \
  PING
```

### Check Application Status
```bash
kubectl logs python-redis-pod -n app-naresh
kubectl get pods -n app-naresh
kubectl get services -n app-naresh
```

## Troubleshooting

### Common Issues
1. **Database not ready**: Wait for status to be "active"
2. **Connection failed**: Check password and port from secret
3. **Pod not starting**: Check resource limits and node capacity
4. **LoadBalancer pending**: Wait for cloud provider to provision IP

### Debug Commands
```bash
# Check all resources
kubectl get all -n app-naresh
kubectl get all -n rec-naresh

# View logs
kubectl logs python-redis-pod -n app-naresh

# Exec into pod
kubectl exec -it python-redis-pod -n app-naresh -- bash
```

## Clean Up

```bash
kubectl delete -f kubernetes/redis-app-service.yaml
kubectl delete -f kubernetes/python-redis-pod.yaml
kubectl delete -f kubernetes/mydb-second.yaml
kubectl delete namespace app-naresh
```
