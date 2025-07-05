# Science Data Kit Kubernetes Deployment

This directory contains Kubernetes configuration files for deploying the Science Data Kit (SDK) in a Kubernetes cluster. These configurations provide a scalable, production-ready deployment of the SDK with all its components.

## Components

The Kubernetes deployment includes the following components:

1. **Neo4j Database**: For storing graph data and ontologies
2. **Redis**: For caching and as a message broker for Celery
3. **Science Data Kit Application**: The main application with Streamlit UI and Jupyter integration
4. **Celery Workers**: For background task processing
5. **Celery Beat**: For scheduled tasks

## Prerequisites

- Kubernetes cluster (v1.19+)
- kubectl command-line tool
- Storage class that supports ReadWriteOnce and ReadWriteMany access modes
- Ingress controller (e.g., NGINX Ingress Controller)

## Deployment Instructions

### 1. Create the Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Create ConfigMap and Secrets

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

Note: For production, you should replace the base64-encoded values in `secret.yaml` with your own secure passwords.

### 3. Deploy Neo4j and Redis

```bash
kubectl apply -f neo4j-deployment.yaml
kubectl apply -f redis-deployment.yaml
```

### 4. Deploy the Science Data Kit Application

```bash
kubectl apply -f sdk-deployment.yaml
```

### 5. Deploy Celery Workers and Beat

```bash
kubectl apply -f celery-deployment.yaml
```

### 6. Verify the Deployment

```bash
kubectl get pods -n science-data-kit
kubectl get services -n science-data-kit
kubectl get pvc -n science-data-kit
```

## Accessing the Application

The Science Data Kit application is exposed through an Ingress resource. By default, it's configured to be accessible at `sdk.example.com`. You'll need to:

1. Configure your DNS to point this domain to your Ingress controller's external IP
2. Or modify your local hosts file for testing

The application will be available at:
- Main UI: http://sdk.example.com/
- Jupyter: http://sdk.example.com/jupyter

## Configuration

### Scaling

You can scale the number of SDK application instances and Celery workers:

```bash
kubectl scale deployment science-data-kit -n science-data-kit --replicas=3
kubectl scale deployment celery-worker -n science-data-kit --replicas=5
```

### Resource Allocation

Resource requests and limits can be adjusted in the respective deployment files based on your workload requirements.

### Persistence

The deployment uses Persistent Volume Claims for:
- Neo4j data, logs, and plugins
- Redis data
- SDK application data

Make sure your Kubernetes cluster has sufficient storage resources.

## Troubleshooting

### Checking Logs

```bash
kubectl logs -n science-data-kit deployment/science-data-kit
kubectl logs -n science-data-kit deployment/neo4j
kubectl logs -n science-data-kit deployment/redis
kubectl logs -n science-data-kit deployment/celery-worker
```

### Common Issues

1. **PVC Pending**: Ensure your cluster has a storage class that supports the required access modes.
2. **Pod CrashLoopBackOff**: Check the logs for errors. Common issues include incorrect passwords or connection issues.
3. **Ingress Not Working**: Verify that your Ingress controller is properly configured and that the DNS or hosts file is set up correctly.

## Security Considerations

For production deployments, consider:

1. Using a proper secrets management solution instead of Kubernetes secrets
2. Enabling TLS for the Ingress
3. Implementing network policies to restrict pod-to-pod communication
4. Setting up proper authentication for Neo4j and Redis
5. Configuring resource quotas for the namespace

## Customization

You can customize the deployment by modifying the YAML files:

- Adjust resource requests and limits
- Change the number of replicas
- Modify environment variables in the ConfigMap
- Update the Ingress configuration for your domain