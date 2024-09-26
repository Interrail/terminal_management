#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to check if deployment is ready
check_deployment() {
    echo "Checking deployment status..."
    kubectl rollout status deployment/terminal-management
}

# Build Docker image with a special tag
# Replace 'your-image-name' with your actual image name
# The tag will be the current date and time
IMAGE_NAME="docker.interrail.uz:7007/terminal_management"
TAG="latest"

echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${TAG} .

# Push the Docker image
echo "Pushing Docker image..."
docker push ${IMAGE_NAME}:${TAG}

# Update the deployment
echo "Updating Kubernetes deployment..."
kubectl rollout restart deployment/terminal-management

# Check deployment status
check_deployment

echo "Deployment process completed."
