# Redis Enterprise Database Web Application

A comprehensive Flask web application that connects to a Redis Enterprise Database with TLS encryption and provides an intuitive interface for generating and managing different Redis data structures.

## 🚀 Features

- **Multiple Data Types**: Generate strings, hashes, sets, lists, and sorted sets
- **TLS Security**: Secure connection to Redis Enterprise with client certificate authentication
- **Real-time Stats**: Monitor database statistics and performance
- **Beautiful UI**: Modern, responsive web interface with interactive buttons
- **LoadBalancer**: Exposed via Kubernetes LoadBalancer for external access
- **Random Data**: Generates realistic random data with unique keys

## 📋 Prerequisites

- Kubernetes cluster with Redis Enterprise Operator installed
- `kubectl` configured to access your cluster
- Redis Enterprise Cluster (REC) deployed
- Basic knowledge of Kubernetes and Redis

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   LoadBalancer  │────│  Flask App Pod   │────│ Redis Enterprise DB │
│  (External IP)  │    │   (Python)       │    │   (TLS + mTLS)      │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## 📁 Project Structure

```
redis-enterprise-web-app/
├── README.md
├── redis-app.py                 # Main Flask application
├── templates/
│   └── index.html              # Web interface template
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container image definition
├── kubernetes/
│   ├── mydb-second.yaml        # Redis Enterprise Database
│   ├── python-redis-pod.yaml   # Application pod
│   └── redis-app-service.yaml  # LoadBalancer service
└── certificates/
    ├── client_cert.pem         # Client certificate for mTLS
    └── client_key.pem          # Client private key
```

## 🔧 Step-by-Step Installation

### Step 1: Create Kubernetes Namespace

Create a dedicated namespace for your application:

```bash
kubectl create namespace app-naresh
```

### Step 2: Deploy Redis Enterprise Database

1. **Create the database configuration:**

```yaml
# mydb-second.yaml
apiVersion: app.redislabs.com/v1alpha1
kind: RedisEnterpriseDatabase
metadata:
  name: mydbsecond
  namespace: rec-naresh
spec:
  memorySize: 1GB
  shardCount: 1
  tlsMode: enabled
  replication: false
  redisEnterpriseCluster:
    name: my-rec
  defaultUser: true
  modulesList:
    - name: search
    - name: ReJSON
```

2. **Deploy the database:**

```bash
kubectl apply -f mydb-second.yaml
```

3. **Wait for database to be active:**

```bash
kubectl get redisenterprisedatabase mydbsecond -n rec-naresh
```

### Step 3: Get Database Connection Details

1. **Retrieve the auto-generated secret:**

```bash
kubectl get secret redb-mydbsecond -n rec-naresh -o yaml
```

2. **Decode the connection details:**

```bash
# Get password
kubectl get secret redb-mydbsecond -n rec-naresh -o jsonpath='{.data.password}' | base64 -d

# Get port
kubectl get secret redb-mydbsecond -n rec-naresh -o jsonpath='{.data.port}' | base64 -d

# Get service name
kubectl get secret redb-mydbsecond -n rec-naresh -o jsonpath='{.data.service_name}' | base64 -d
```

### Step 4: Set Up TLS Certificates

1. **Check if client certificate exists:**

```bash
kubectl get secret redb-client-cert -n rec-naresh
```

2. **If certificates don't exist, create them:**

```bash
# Generate client certificate and key
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -subj "/CN=redis-client/O=Demo" \
  -keyout client_key.pem -out client_cert.pem

# Create Kubernetes secret
kubectl create secret generic redb-client-cert \
  --from-literal=cert="$(cat client_cert.pem)" \
  -n rec-naresh
```

### Step 5: Create Application Pod

1. **Deploy the Python pod:**

```yaml
# python-redis-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: python-redis-pod
  namespace: app-naresh
  labels:
    app: python-redis
spec:
  containers:
  - name: python-redis-container
    image: python:3.11-slim
    command: ["/bin/bash"]
    args: ["-c", "apt-get update && apt-get install -y redis-server openssl && redis-server --daemonize yes && tail -f /dev/null"]
    ports:
    - containerPort: 8000
      name: python-app
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"
  restartPolicy: Always
```

```bash
kubectl apply -f python-redis-pod.yaml
```

### Step 6: Install Application Dependencies

1. **Copy application files to the pod:**

```bash
# Create app directory
kubectl exec -n app-naresh python-redis-pod -- mkdir -p /app/templates

# Copy Python application
kubectl cp redis-app.py app-naresh/python-redis-pod:/app/redis-app.py

# Copy HTML template
kubectl cp templates/index.html app-naresh/python-redis-pod:/app/templates/index.html

# Copy requirements
kubectl cp requirements.txt app-naresh/python-redis-pod:/app/requirements.txt

# Copy certificates
kubectl cp client_cert.pem app-naresh/python-redis-pod:/app/client_cert.pem
kubectl cp client_key.pem app-naresh/python-redis-pod:/app/client_key.pem
```

2. **Install Python dependencies:**

```bash
kubectl exec -n app-naresh python-redis-pod -- pip install -r /app/requirements.txt
```

3. **Install Redis tools for testing:**

```bash
kubectl exec -n app-naresh python-redis-pod -- apt-get update
kubectl exec -n app-naresh python-redis-pod -- apt-get install -y redis-tools
```

### Step 7: Test Redis Connection

1. **Test with redis-cli:**

```bash
kubectl exec -n app-naresh python-redis-pod -- redis-cli \
  -h mydbsecond-headless.rec-naresh.svc.cluster.local \
  -p 18777 \
  --tls \
  --sni mydbsecond-headless.rec-naresh.svc.cluster.local \
  --cert /app/client_cert.pem \
  --key /app/client_key.pem \
  --insecure \
  --user default \
  -a 'YOUR_PASSWORD' \
  PING
```

Expected output: `PONG`

### Step 8: Configure Application

Update the Redis connection details in `redis-app.py`:

```python
# Redis connection configuration for TLS-enabled database
REDIS_HOST = "mydbsecond-headless.rec-naresh.svc.cluster.local"
REDIS_PORT = 18777  # Your actual port
REDIS_USERNAME = "default"
REDIS_PASSWORD = "YOUR_DECODED_PASSWORD"  # From step 3
```

### Step 9: Start the Application

```bash
kubectl exec -n app-naresh python-redis-pod -- bash -c "cd /app && python redis-app.py &"
```

### Step 10: Expose with LoadBalancer

1. **Create LoadBalancer service:**

```yaml
# redis-app-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-app-loadbalancer
  namespace: app-naresh
  labels:
    app: redis-app
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: python-redis
```

```bash
kubectl apply -f redis-app-service.yaml
```

2. **Get external IP:**

```bash
kubectl get service redis-app-loadbalancer -n app-naresh
```

## 🌐 Accessing the Application

Once the LoadBalancer is provisioned, access your application at:

```
http://YOUR_EXTERNAL_IP
```

## 🎯 Application Features

### Data Generation Buttons

- **📝 Generate 10 Strings**: Creates random string key-value pairs
- **🗂️ Generate 10 Hashes**: Creates hash objects with user data
- **🎯 Generate 10 Sets**: Creates sets with random members
- **📋 Generate 10 Lists**: Creates lists with random items
- **🏆 Generate 10 Sorted Sets**: Creates sorted sets with scores
- **📊 Get Database Stats**: Shows Redis statistics
- **🗑️ Clear All Data**: Removes all keys from database

### Sample Generated Data

**Strings:**
```
Key: string:a1b2c3d4
Value: "RandomString123ABC"
```

**Hashes:**
```
Key: hash:e5f6g7h8
Value: {
  "name": "Alice",
  "age": 25,
  "city": "New York",
  "score": 85
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if Redis database is active
   - Verify connection details (host, port, password)
   - Ensure certificates are properly copied

2. **TLS Errors**
   - Verify client certificates are valid
   - Check if TLS is enabled on database
   - Ensure certificate paths are correct

3. **Pod Not Starting**
   - Check pod logs: `kubectl logs python-redis-pod -n app-naresh`
   - Verify resource limits
   - Check if namespace exists

### Debugging Commands

```bash
# Check pod status
kubectl get pods -n app-naresh

# View pod logs
kubectl logs python-redis-pod -n app-naresh

# Check database status
kubectl get redisenterprisedatabase -n rec-naresh

# Test Redis connection
kubectl exec -n app-naresh python-redis-pod -- redis-cli --version
```

## 📊 Monitoring

Monitor your application using:

- **Database Stats**: Built-in statistics page
- **Kubernetes Dashboard**: Pod and service metrics
- **Redis Enterprise UI**: Database performance metrics

## 🔒 Security Considerations

- **TLS Encryption**: All Redis connections use TLS
- **Client Certificates**: mTLS authentication enabled
- **Network Policies**: Consider implementing network policies
- **RBAC**: Use proper Kubernetes RBAC for access control

## 🚀 Production Deployment

For production environments:

1. **Use proper SSL certificates** (not self-signed)
2. **Implement proper secret management**
3. **Set up monitoring and alerting**
4. **Configure backup strategies**
5. **Use Ingress instead of LoadBalancer** for better control
6. **Implement proper logging**

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check Redis Enterprise documentation
- Review Kubernetes troubleshooting guides

---

**Built with ❤️ using Redis Enterprise, Kubernetes, and Flask**
