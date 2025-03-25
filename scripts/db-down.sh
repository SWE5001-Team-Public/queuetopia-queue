#!/bin/bash
set -e

DB_CONTAINER="queue-svc-db"
DB_IMAGE="queuetopia-queue-svc-db"
COMPOSE_FILE="scripts/docker-compose-db.yml"
VOLUME_NAME="queuetopia_queue_postgres_data"

echo "Stopping and removing the PostgreSQL container..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$COMPOSE_FILE" down -v
else
    docker compose -f "$COMPOSE_FILE" down -v
fi

# Stop and remove the database container if it exists
FOUND_CONTAINER=$(docker ps -a --format '{{.Names}}' | grep "^$DB_CONTAINER$" || true)

if [[ -n "$FOUND_CONTAINER" ]]; then
    docker stop "$DB_CONTAINER"
    docker rm "$DB_CONTAINER"
    echo "✅ Removed container: $DB_CONTAINER"
else
    echo "⚠️ Container $DB_CONTAINER not found."
fi

# Remove the PostgreSQL image if it exists
if [[ -n $(docker images -q "$DB_IMAGE") ]]; then
    docker rmi -f "$DB_IMAGE"
    echo "✅ Removed image: $DB_IMAGE"
else
    echo "⚠️ Image $DB_IMAGE not found."
fi

echo "Cleaning up unused Docker resources..."
docker image prune -af --filter "label=project=queuetopia-queue-svc" || echo "No unused images to remove."

# Ensure Buildx images are also cleaned up (for multi-arch support)
docker buildx prune -af || echo "No Buildx cache to clear."

# Remove the volume only if it exists
if docker volume inspect "$VOLUME_NAME" > /dev/null 2>&1; then
    docker volume rm "$VOLUME_NAME"
    echo "✅ Removed volume: $VOLUME_NAME"
else
    echo "⚠️ Volume $VOLUME_NAME not found or already removed."
fi

echo "✅ PostgreSQL container, image, and volume removed!"
