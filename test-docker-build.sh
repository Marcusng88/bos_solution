#!/bin/bash

echo "🐳 Testing Docker build locally..."
echo "================================"

# Build the Docker image
echo "Building Docker image..."
docker build -t bos-solution-backend:test .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    echo ""
    echo "🧪 Testing container startup..."
    
    # Test running the container
    docker run --rm -d --name test-container -p 8000:8000 bos-solution-backend:test
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "⏳ Waiting for service to be ready..."
        sleep 10
        
        # Test health endpoint
        echo "🏥 Testing health endpoint..."
        curl -f http://localhost:8000/health
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Health check passed!"
            echo "🎉 Docker build and container test successful!"
        else
            echo ""
            echo "❌ Health check failed!"
        fi
        
        # Clean up
        echo "🧹 Cleaning up test container..."
        docker stop test-container
        docker rm test-container
    else
        echo "❌ Container failed to start!"
    fi
else
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "🚀 Ready to deploy to Render!"
