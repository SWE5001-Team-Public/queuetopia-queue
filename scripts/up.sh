#!/bin/bash
set -e

# Move to the project root (where Dockerfile is located)
cd "$(dirname "$0")/.." || exit

# Run down.sh first to stop and clean up existing containers
echo "Stopping existing containers before starting fresh..."
bash scripts/down.sh

# Check for --dev flag
if [[ "$1" == "--dev" ]]; then
    COMPOSE_FILE="scripts/docker-compose-dev.yml"
    echo "Using development docker-compose file: $COMPOSE_FILE"
else
    COMPOSE_FILE="scripts/docker-compose.yml"
    echo "Using production docker-compose file: $COMPOSE_FILE"
fi

# Check if a default Buildx builder exists, otherwise create one
if ! docker buildx inspect default &>/dev/null; then
    echo "Creating a new Buildx builder..."
    docker buildx create --name mybuilder --use
else
    echo "Using existing Buildx builder."
    docker buildx use default
fi

# Detect system architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    PLATFORM="linux/arm64"
else
    PLATFORM="linux/amd64"
fi

echo "Detected architecture: $ARCH"
echo "Building the Docker image for platform: $PLATFORM"

# Build the Docker image using Buildx for correct platform
docker buildx build --platform "$PLATFORM" -t template-svc . --load

echo "Starting the Docker container with $COMPOSE_FILE..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$COMPOSE_FILE" -p queuetopia_template up -d --build
else
    docker compose -f "$COMPOSE_FILE" -p queuetopia_template up -d --build
fi

echo "Checking running containers..."
docker ps
