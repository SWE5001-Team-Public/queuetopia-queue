#!/bin/bash
set -e

# Default compose file
COMPOSE_FILE="scripts/docker-compose-db.yml"

echo "Starting the PostgreSQL container..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$COMPOSE_FILE" -p queuetopia_template up -d template-svc-postgres
else
    docker compose -f "$COMPOSE_FILE" -p queuetopia_template up -d template-svc-postgres
fi

# Identify the correct PostgreSQL container name
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep 'template-svc-db' || true)

if [[ -z "$DB_CONTAINER" ]]; then
    echo "❌ Error: PostgreSQL container not found!"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL ($DB_CONTAINER) to start..."
until docker exec "$DB_CONTAINER" pg_isready -U postgres > /dev/null 2>&1; do
    sleep 2
    echo "PostgreSQL ($DB_CONTAINER) is still starting..."
done

echo "✅ PostgreSQL ($DB_CONTAINER) is up and running!"
