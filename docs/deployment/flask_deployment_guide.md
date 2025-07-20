# Science Data Kit Flask Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Science Data Kit Flask application in various environments. It covers containerized deployment with Docker and Singularity, as well as cloud deployment options.

## Prerequisites

Before deploying the Science Data Kit, ensure you have the following prerequisites installed:

- **For Docker deployment**:
  - Docker Engine (version 20.10.0 or higher)
  - Docker Compose (version 2.0.0 or higher)

- **For Singularity deployment**:
  - Singularity (version 3.8.0 or higher)

- **For all deployments**:
  - Git
  - Bash shell

## Deployment Options

The Science Data Kit can be deployed in various environments:

### 1. Docker Deployment

Docker provides an easy way to deploy the Science Data Kit with all its dependencies in containers.

#### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/science_data_kit.git
cd science_data_kit

# Run the deployment script
./scripts/deploy.sh --env=docker --mode=full
```

This will:
1. Build the Docker images
2. Start all containers (Flask app, Neo4j, Redis, etc.)
3. Make the application available at http://localhost:5001

#### Deployment Modes

The Docker deployment supports three modes:

- **Full Mode** (`--mode=full`): Deploys the complete stack including:
  - Flask web application
  - Neo4j database
  - Redis for caching
  - Jupyter Lab for interactive analysis
  - NeoDash for Neo4j dashboard visualization
  - Ollama for LLM capabilities
  - Celery worker for background tasks

- **App-Only Mode** (`--mode=app-only`): Deploys only the Flask web application and its essential dependencies:
  - Flask web application
  - Neo4j database
  - Redis for caching

- **Minimal Mode** (`--mode=minimal`): Deploys only the Flask web application:
  - Flask web application

#### Custom Configuration

You can customize the deployment by editing the Docker Compose files in the `docker/` directory:

- `docker-compose-full.yml`: Configuration for full deployment
- `docker-compose.yml`: Configuration for app-only deployment
- `docker-compose-minimal.yml`: Configuration for minimal deployment

### 2. Singularity Deployment

Singularity is ideal for deploying the Science Data Kit in HPC (High-Performance Computing) environments.

#### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/science_data_kit.git
cd science_data_kit

# Run the deployment script
./scripts/deploy.sh --env=singularity
```

This will:
1. Build the Singularity image
2. Start the Singularity instance
3. Make the application available at http://localhost:5001

#### Manual Deployment

If you prefer to deploy manually:

```bash
# Build the Singularity image
singularity build science_data_kit.sif singularity/science_data_kit.def

# Run the container
singularity run science_data_kit.sif
```

#### Environment Variables

You can customize the Singularity deployment with environment variables:

```bash
# Set custom port
PORT=8080 singularity run science_data_kit.sif

# Connect to external Neo4j database
NEO4J_URI=bolt://neo4j.example.com:7687 \
NEO4J_USER=neo4j \
NEO4J_PASSWORD=password \
singularity run science_data_kit.sif
```

### 3. Cloud Deployment

The Science Data Kit can be deployed to various cloud platforms.

#### AWS Deployment

To deploy to AWS:

```bash
# Deploy to AWS
./scripts/deploy.sh --env=aws
```

For manual deployment to AWS:

1. **Using AWS Elastic Beanstalk**:
   - Create a new Elastic Beanstalk application
   - Choose Python as the platform
   - Upload a ZIP file containing your application code
   - Configure environment variables in the Elastic Beanstalk console

2. **Using AWS ECS (Elastic Container Service)**:
   - Push your Docker image to Amazon ECR (Elastic Container Registry)
   - Create an ECS cluster
   - Define a task definition that uses your Docker image
   - Create a service to run your task

#### Azure Deployment

To deploy to Azure:

```bash
# Deploy to Azure
./scripts/deploy.sh --env=azure
```

For manual deployment to Azure:

1. **Using Azure App Service**:
   - Create a new App Service
   - Choose Python as the runtime stack
   - Deploy your code using Git, GitHub, or Azure DevOps
   - Configure environment variables in the App Service settings

2. **Using Azure Container Instances**:
   - Push your Docker image to Azure Container Registry
   - Create a Container Instance that uses your Docker image
   - Configure networking and environment variables

#### Google Cloud Platform Deployment

To deploy to GCP:

```bash
# Deploy to GCP
./scripts/deploy.sh --env=gcp
```

For manual deployment to GCP:

1. **Using Google App Engine**:
   - Create an `app.yaml` file for your application
   - Deploy using the Google Cloud SDK:
     ```bash
     gcloud app deploy
     ```

2. **Using Google Cloud Run**:
   - Push your Docker image to Google Container Registry
   - Create a Cloud Run service that uses your Docker image
   - Configure memory, CPU, and environment variables

## Configuration

### Environment Variables

The Science Data Kit Flask application can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | The port to run the Flask application on | `5001` |
| `FLASK_APP` | The Flask application module | `science_data_kit.web.app` |
| `FLASK_ENV` | The Flask environment (production, development) | `production` |
| `NEO4J_URI` | The URI for connecting to Neo4j | `bolt://localhost:7687` |
| `NEO4J_USER` | The Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | The Neo4j password | `password` |

### Configuration Files

For more advanced configuration, you can modify the following files:

- `science_data_kit/web/config.py`: Flask application configuration
- `docker/docker-compose-full.yml`: Docker Compose configuration for full deployment
- `singularity/science_data_kit.def`: Singularity definition file

## Health Checks and Monitoring

### Health Checks

The Flask application provides a health check endpoint at `/health` that returns a 200 OK response if the application is running correctly.

You can use this endpoint for monitoring and load balancing:

```bash
curl http://localhost:5001/health
```

### Monitoring

For production deployments, consider setting up monitoring using:

- Prometheus for metrics collection
- Grafana for visualization
- ELK stack (Elasticsearch, Logstash, Kibana) for log management

## Troubleshooting

### Common Issues

1. **Application fails to start**:
   - Check if the required ports are available
   - Verify that Neo4j is running and accessible
   - Check the application logs for error messages

2. **Database connection issues**:
   - Verify that Neo4j is running
   - Check the Neo4j connection settings (URI, username, password)
   - Ensure that the Neo4j database is accessible from the application container

3. **Performance issues**:
   - Check resource utilization (CPU, memory)
   - Consider scaling the application horizontally
   - Optimize database queries

### Logs

To view logs in Docker deployment:

```bash
# View Flask application logs
docker logs sdk-app

# View Neo4j logs
docker logs sdk-neo4j

# View Redis logs
docker logs sdk-redis
```

To view logs in Singularity deployment:

```bash
# View application logs
singularity instance logs sdk
```

## Scaling Considerations

### Horizontal Scaling

For high-traffic deployments, consider horizontal scaling:

1. **Load Balancing**:
   - Use a load balancer (e.g., NGINX, HAProxy) to distribute traffic
   - Configure health checks to ensure traffic is only sent to healthy instances

2. **Stateless Design**:
   - Ensure the application is stateless
   - Use Redis for session storage
   - Store user files in a shared storage system

3. **Database Scaling**:
   - Use Neo4j clustering for high availability
   - Consider read replicas for read-heavy workloads

### Vertical Scaling

For compute-intensive workloads:

1. **Resource Allocation**:
   - Increase CPU and memory allocation
   - Use instance types optimized for compute-intensive workloads

2. **Parallel Processing**:
   - Configure the number of workers based on available CPU cores
   - Monitor memory usage to avoid out-of-memory errors

## Security Considerations

### Authentication and Authorization

1. **User Authentication**:
   - Use HTTPS for all communications
   - Implement secure authentication mechanisms
   - Store passwords securely (hashed and salted)

2. **API Security**:
   - Use API keys or OAuth for API authentication
   - Implement rate limiting
   - Validate and sanitize all input

### Data Protection

1. **Data Encryption**:
   - Encrypt sensitive data at rest and in transit
   - Use secure protocols (HTTPS, SSH) for data transfer
   - Implement proper key management

2. **Backup and Recovery**:
   - Regularly back up Neo4j data
   - Test backup restoration process
   - Implement a disaster recovery plan

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Science Data Kit Flask application in various environments. By following these guidelines, you can ensure a reliable, scalable, and secure deployment.

For specific questions or issues, please refer to the troubleshooting section or contact the Science Data Kit support team.