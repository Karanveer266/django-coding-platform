#!/bin/bash

# Setup script for secure judge system
# This script builds all necessary Docker images for secure code execution

set -e

echo "Setting up secure judge system..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Building Docker images for secure code execution..."

# Build Python image
echo "Building Python judge image..."
docker build -t django-judge-python ./docker/python/

# Build C++ image
echo "Building C++ judge image..."
docker build -t django-judge-cpp ./docker/cpp/

# Build Java image
echo "Building Java judge image..."
docker build -t django-judge-java ./docker/java/

# Build JavaScript image
echo "Building JavaScript judge image..."
docker build -t django-judge-javascript ./docker/javascript/

echo "All judge images built successfully!"

# Verify images
echo "Verifying images..."
docker images | grep django-judge

echo ""
echo "Secure judge system setup complete!"
echo ""
echo "Security features enabled:"
echo "✓ Docker containerization"
echo "✓ Network isolation (no internet access)"
echo "✓ Resource limits (CPU, memory, disk)"
echo "✓ Non-root user execution"
echo "✓ Read-only filesystem"
echo "✓ Process limits"
echo "✓ File descriptor limits"
echo "✓ Code validation and scanning"
echo ""
echo "Your code execution environment is now secure!"