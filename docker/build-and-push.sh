#!/bin/bash
set -e

# Add Docker to PATH so credential helper works
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

echo "Starting Docker build..."
docker build --platform linux/amd64 -t kaspamontana/ugc-faceswapper:v1 .

echo "Build completed! Now pushing to Docker Hub..."
docker push kaspamontana/ugc-faceswapper:v1

echo "All done! Image is ready on Docker Hub."
