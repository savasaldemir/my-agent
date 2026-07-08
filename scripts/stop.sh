#!/bin/bash

set -e

echo "🛑 Stopping My Agent services..."
docker-compose -f deployment/docker-compose.yml down
echo "✅ Services stopped"
