#!/bin/bash

# Backend Deployment Script for Render
echo "🚀 Starting backend deployment..."

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Build the Docker image locally to test
echo "🔨 Building Docker image locally..."
docker build -t bos-backend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Commit and push your changes to Git"
    echo "2. Render will automatically detect the new Dockerfile location"
    echo "3. Monitor the deployment in your Render dashboard"
    echo ""
    echo "🔗 Your Render service: https://dashboard.render.com/web/bos-solution-backend"
else
    echo "❌ Docker build failed. Please check the error messages above."
    exit 1
fi
