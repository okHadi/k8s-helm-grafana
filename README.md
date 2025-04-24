# Flask Redis Counter Application

A simple web application that increments a counter in Redis and displays it on a webpage. This repository demonstrates how to deploy the application both standalone and using Kubernetes with Helm charts.

## Application Overview

This application consists of two main components:
- A Flask web application that serves a simple webpage
- A Redis database that stores a counter value

Every time you refresh the webpage, the counter increments by one.

## Running Standalone

If you want to run the application without Kubernetes, follow these steps:

```bash
# Start Redis in a Docker container
docker run -d --name redis -p 6379:6379 redis

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask redis

# Run the Flask app
python3 app.py
```

Visit: http://localhost:5000

Every refresh will increment the Redis counter and show the updated count in the browser.

## Kubernetes and Helm: Explained in Simple Terms

### What is Kubernetes?
Kubernetes (often shortened to K8s) is a platform that automates the management of containerized applications. It helps you deploy, scale, and manage your applications across multiple servers. Think of Kubernetes as an operating system for the cloud, where you can run many applications without worrying about which server they're on.

### Key Kubernetes Concepts

#### Pod
A Pod is the smallest and simplest unit in Kubernetes. It's basically a wrapper around one or more containers (usually just one). If a container is a single running application, a Pod adds some extra information about how to run that application in Kubernetes.

#### Deployment
A Deployment is a way to tell Kubernetes how to create or modify instances of Pods. It ensures a specific number of identical Pods are running at all times. If a Pod crashes or is deleted, the Deployment automatically creates a new one to replace it.

#### Service
A Service is a way to expose an application running on a set of Pods as a network service. Since Pods can be created and destroyed at any time, a Service provides a stable "address" that doesn't change even when the underlying Pods do.

#### Node
A Node is a physical or virtual machine in the Kubernetes cluster. It's simply a worker machine where containers are launched by Kubernetes.

### What is Helm?
Helm is a package manager for Kubernetes, similar to how apt is for Ubuntu or npm is for JavaScript. It helps you install, upgrade, and manage applications on your Kubernetes cluster. A Helm Chart is a pre-configured package of Kubernetes resources that can be easily deployed.

## Deploying with Kubernetes and Helm

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) - A platform that packages your application into containers
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) - A tool that runs a single-node Kubernetes cluster on your laptop
- [kubectl](https://kubernetes.io/docs/tasks/tools/) - Command line tool for interacting with Kubernetes
- [Helm](https://helm.sh/docs/intro/install/) - Package manager for Kubernetes

### Step 1: Start Minikube

This creates a mini Kubernetes cluster on your machine:

```bash
minikube start
```

### Step 2: Build the Docker Image

First, configure your terminal to use Minikube's Docker environment:

```bash
eval $(minikube docker-env)
```

Then build the Docker image:

```bash
docker build -t flask-redis-app:latest .
```

### Step 3: Deploy with Helm

This installs your application on the Kubernetes cluster:

```bash
helm install flask-redis ./flask-redis-chart
```

### Step 4: Access the Application

This opens your application in a browser:

```bash
minikube service flask
```

## Understanding the Kubernetes Configuration

### Helm Chart Structure

A Helm chart is a collection of files that describe Kubernetes resources:

```
flask-redis-chart/               # Main directory of the chart
  ├── Chart.yaml                 # Information about the chart
  ├── values.yaml                # Default configuration values
  └── templates/                 # Where the Kubernetes YAML files live
      ├── flask-deployment.yaml  # How to deploy the Flask app
      ├── flask-service.yaml     # How to expose the Flask app
      ├── redis-deployment.yaml  # How to deploy Redis
      └── redis-service.yaml     # How to expose Redis internally
```

### Exploring the Configuration Files

#### values.yaml
This file contains the default values that will be used in your templates:

```yaml
flask:
  image: flask-redis-app    # Which Docker image to use for Flask
  port: 5000                # Which port Flask runs on
  nodePort: 30007           # Which port to expose outside the cluster
  replicas: 1               # How many copies of the Flask app to run

redis:
  image: redis              # Which Docker image to use for Redis
  port: 6379                # Which port Redis runs on
```

#### flask-deployment.yaml
This file tells Kubernetes how to run your Flask application:

```yaml
apiVersion: apps/v1
kind: Deployment                # This is a Deployment resource
metadata:
  name: flask                   # Name of the deployment
spec:
  replicas: {{ .Values.flask.replicas }}   # How many copies to run
  selector:
    matchLabels:
      app: flask                # Label to identify this app
  template:
    metadata:
      labels:
        app: flask              # Label for the pod
    spec:
      containers:
        - name: flask
          image: {{ .Values.flask.image }}   # Docker image to use
          imagePullPolicy: Never             # Don't try to download it
          ports:
            - containerPort: {{ .Values.flask.port }}   # Port inside container
          env:
            - name: REDIS_HOST
              value: redis      # Connect to redis service by name
```

#### flask-service.yaml
This file creates a network service to access your Flask app:

```yaml
apiVersion: v1
kind: Service                 # This is a Service resource
metadata:
  name: flask                 # Name of the service
spec:
  type: NodePort              # Type of service (exposed outside cluster)
  selector:
    app: flask                # Which pods to route traffic to
  ports:
    - port: {{ .Values.flask.port }}            # Port on the service
      targetPort: {{ .Values.flask.port }}      # Port on the pod
      nodePort: {{ .Values.flask.nodePort }}    # Port exposed outside
```

## Customizing the Deployment

You can customize how your application runs by changing values when installing:

### Change the external port

```bash
helm install flask-redis ./flask-redis-chart --set flask.nodePort=30008
```

### Scale the Flask application (run multiple copies)

```bash
helm install flask-redis ./flask-redis-chart --set flask.replicas=3
```

### Update an existing deployment

```bash
helm upgrade flask-redis ./flask-redis-chart --set flask.replicas=2
```

## Troubleshooting

### Check if your pods are running

This shows all running pods (containers):

```bash
kubectl get pods
```

The output looks like:
```
NAME                     READY   STATUS    RESTARTS   AGE
flask-1234567890-abcde   1/1     Running   0          5m
redis-1234567890-abcde   1/1     Running   0          5m
```

- NAME: Unique identifier for the pod
- READY: How many containers in the pod are ready (format: ready/total)
- STATUS: Current state of the pod (Running, Pending, Error, etc.)
- RESTARTS: How many times the pod has been restarted
- AGE: How long the pod has been running

### View logs

```bash
kubectl logs $(kubectl get pods | grep flask | awk '{print $1}')
```

### Remove the application from Kubernetes

```bash
helm uninstall flask-redis
```

## Common Issues and Solutions

### Pods stuck in "Pending" state
This often means Kubernetes doesn't have enough resources to run your pod.

### Pods in "CrashLoopBackOff" state
This means your application is crashing. Check the logs to see what's wrong.

### "ImagePullBackOff" error
This means Kubernetes can't find your Docker image. Make sure it's built correctly.

### Service not accessible
Make sure your application is listening on the right port and interface (0.0.0.0).

## Next Steps: What to Learn After Understanding This Project

1. **Persistent Storage**: How to make Redis data survive pod restarts
2. **ConfigMaps and Secrets**: How to store configuration and sensitive data
3. **Ingress**: More advanced ways to expose your services
4. **Kubernetes Dashboard**: A web UI for your Kubernetes cluster

## Learn More

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
