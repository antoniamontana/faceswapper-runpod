#!/bin/bash
set -e

export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

echo "=== UGC Face Swapper Docker Build ==="
echo "Starting at $(date)"

# Function to retry commands
retry_command() {
    local max_attempts=5
    local attempt=1
    local delay=10

    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts..."
        if "$@"; then
            return 0
        fi

        if [ $attempt -lt $max_attempts ]; then
            echo "Failed. Retrying in ${delay}s..."
            sleep $delay
            delay=$((delay * 2))  # Exponential backoff
        fi
        attempt=$((attempt + 1))
    done

    echo "Command failed after $max_attempts attempts"
    return 1
}

cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/docker"

# Step 1: Pull base image with retries (handles network issues)
echo ""
echo "Step 1: Pulling NVIDIA CUDA base image..."
retry_command docker pull --platform linux/amd64 nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Step 2: Build image
echo ""
echo "Step 2: Building Docker image (this will take 2-3 hours)..."
docker build --platform linux/amd64 -t kaspamontana/ugc-faceswapper:v1 .

# Step 3: Push to Docker Hub
echo ""
echo "Step 3: Pushing to Docker Hub..."
retry_command docker push kaspamontana/ugc-faceswapper:v1

echo ""
echo "=== BUILD COMPLETE ==="
echo "Finished at $(date)"
echo "Image: kaspamontana/ugc-faceswapper:v1"
echo "Ready for Runpod deployment!"
