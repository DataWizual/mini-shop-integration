#!/bin/bash
echo "🚀 LOCAL DEPLOYMENT SCRIPT"
echo "=========================="

# Stop running containers
echo "🛑 Stopping current containers..."
docker compose down

# Pull latest images
echo "📥 Pulling latest images from DockerHub..."
docker pull $DOCKER_USERNAME/devops-app:latest

# Start services
echo "🔄 Starting services..."
docker compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check system status
echo "📊 Checking system status..."
./control_panel.sh

echo "✅ Local deployment completed!"
