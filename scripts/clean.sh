#!/bin/bash

set -e

echo "🧹 Cleaning up My Agent..."
docker-compose -f deployment/docker-compose.yml down -v
echo "✅ Cleanup complete"
