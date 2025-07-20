#!/bin/bash
# Science Data Kit Deployment Script
# This script automates the deployment of the Science Data Kit in different environments.

set -e

# Default values
DEPLOY_ENV="docker"
DEPLOY_MODE="full"
DEPLOY_DIR="$(pwd)"
BUILD_ONLY=false
HELP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --env=*)
      DEPLOY_ENV="${1#*=}"
      shift
      ;;
    --mode=*)
      DEPLOY_MODE="${1#*=}"
      shift
      ;;
    --dir=*)
      DEPLOY_DIR="${1#*=}"
      shift
      ;;
    --build-only)
      BUILD_ONLY=true
      shift
      ;;
    --help)
      HELP=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Display help
if [ "$HELP" = true ]; then
  echo "Science Data Kit Deployment Script"
  echo ""
  echo "Usage: ./deploy.sh [options]"
  echo ""
  echo "Options:"
  echo "  --env=<environment>    Deployment environment (docker, singularity, aws, azure, gcp)"
  echo "                         Default: docker"
  echo "  --mode=<mode>          Deployment mode (full, app-only, minimal)"
  echo "                         Default: full"
  echo "  --dir=<directory>      Directory to deploy to"
  echo "                         Default: current directory"
  echo "  --build-only           Build containers but don't start them"
  echo "  --help                 Display this help message"
  echo ""
  echo "Examples:"
  echo "  ./deploy.sh --env=docker --mode=full"
  echo "  ./deploy.sh --env=singularity --mode=app-only"
  echo "  ./deploy.sh --env=aws --mode=minimal"
  exit 0
fi

# Validate environment
case $DEPLOY_ENV in
  docker|singularity|aws|azure|gcp)
    echo "Deploying to $DEPLOY_ENV environment"
    ;;
  *)
    echo "Error: Invalid environment '$DEPLOY_ENV'"
    echo "Valid environments: docker, singularity, aws, azure, gcp"
    exit 1
    ;;
esac

# Validate mode
case $DEPLOY_MODE in
  full|app-only|minimal)
    echo "Using $DEPLOY_MODE deployment mode"
    ;;
  *)
    echo "Error: Invalid mode '$DEPLOY_MODE'"
    echo "Valid modes: full, app-only, minimal"
    exit 1
    ;;
esac

# Create deployment directory if it doesn't exist
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Deploy based on environment
case $DEPLOY_ENV in
  docker)
    deploy_docker
    ;;
  singularity)
    deploy_singularity
    ;;
  aws)
    deploy_aws
    ;;
  azure)
    deploy_azure
    ;;
  gcp)
    deploy_gcp
    ;;
esac

# Docker deployment function
deploy_docker() {
  echo "Deploying Science Data Kit using Docker..."
  
  # Copy necessary files
  cp -r "$SCRIPT_DIR/../docker" .
  
  # Choose Docker Compose file based on mode
  case $DEPLOY_MODE in
    full)
      COMPOSE_FILE="docker/docker-compose-full.yml"
      ;;
    app-only)
      COMPOSE_FILE="docker/docker-compose.yml"
      ;;
    minimal)
      COMPOSE_FILE="docker/docker-compose-minimal.yml"
      ;;
  esac
  
  # Build Docker images
  echo "Building Docker images..."
  docker-compose -f "$COMPOSE_FILE" build
  
  # Start containers if not build-only
  if [ "$BUILD_ONLY" = false ]; then
    echo "Starting containers..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    echo "Deployment complete!"
    echo "Access the application at http://localhost:5001"
  else
    echo "Build complete. Use the following command to start the containers:"
    echo "docker-compose -f $COMPOSE_FILE up -d"
  fi
}

# Singularity deployment function
deploy_singularity() {
  echo "Deploying Science Data Kit using Singularity..."
  
  # Copy necessary files
  cp -r "$SCRIPT_DIR/../singularity" .
  
  # Build Singularity image
  echo "Building Singularity image..."
  singularity build science_data_kit.sif singularity/science_data_kit.def
  
  # Start container if not build-only
  if [ "$BUILD_ONLY" = false ]; then
    echo "Starting Singularity container..."
    singularity instance start science_data_kit.sif sdk
    
    echo "Deployment complete!"
    echo "Access the application at http://localhost:5001"
  else
    echo "Build complete. Use the following command to start the container:"
    echo "singularity instance start science_data_kit.sif sdk"
  fi
}

# AWS deployment function
deploy_aws() {
  echo "Deploying Science Data Kit to AWS..."
  
  # Implementation depends on specific AWS services being used
  echo "AWS deployment is not fully implemented yet."
  echo "Please refer to the deployment documentation for manual AWS deployment steps."
}

# Azure deployment function
deploy_azure() {
  echo "Deploying Science Data Kit to Azure..."
  
  # Implementation depends on specific Azure services being used
  echo "Azure deployment is not fully implemented yet."
  echo "Please refer to the deployment documentation for manual Azure deployment steps."
}

# GCP deployment function
deploy_gcp() {
  echo "Deploying Science Data Kit to Google Cloud Platform..."
  
  # Implementation depends on specific GCP services being used
  echo "GCP deployment is not fully implemented yet."
  echo "Please refer to the deployment documentation for manual GCP deployment steps."
}

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call the appropriate deployment function
case $DEPLOY_ENV in
  docker)
    deploy_docker
    ;;
  singularity)
    deploy_singularity
    ;;
  aws)
    deploy_aws
    ;;
  azure)
    deploy_azure
    ;;
  gcp)
    deploy_gcp
    ;;
esac

echo "Deployment process completed."