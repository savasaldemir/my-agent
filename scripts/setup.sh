#!/bin/bash

set -e

echo "🚀 Starting My Agent development environment..."

if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

mkdir -p logs
mkdir -p data

echo "📦 Building services..."
docker-compose -f deployment/docker-compose.yml build

echo "🔧 Starting services..."
docker-compose -f deployment/docker-compose.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Services started:"
echo "   - API Gateway: http://localhost:3000"
echo "   - Core Engine: http://localhost:8000"
echo "   - Web App: http://localhost:5173"
echo "   - PostgreSQL: localhost:5432"
echo "   - MongoDB: localhost:27017"
echo "   - Redis: localhost:6379"
echo ""
echo "📝 View logs with: docker-compose -f deployment/docker-compose.yml logs -f"
