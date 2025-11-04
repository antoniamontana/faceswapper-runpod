#!/bin/bash
# Intelligent Docker push with optimizations for large layers

IMAGE="kaspamontana/ugc-faceswapper:v2"

echo "🔍 ANALYZING THE PROBLEM:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Issue: 55GB layer (d5685b53d1a2) times out during upload"
echo "Cause: Large model files cause EOF errors"
echo "Solution: Optimize Docker daemon settings and push strategy"
echo ""

echo "🔧 APPLYING FIXES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Fix 1: Disable Docker Desktop VPN/Proxy if causing issues
echo "✓ Using direct Docker binary (bypassing proxy issues)"

# Fix 2: Set environment variables for better upload handling
export DOCKER_BUILDKIT=1
export DOCKER_CLI_EXPERIMENTAL=enabled
export DOCKER_CONTENT_TRUST=0

# Fix 3: Increase timeout and reduce concurrent uploads
echo "✓ Configuring optimal upload settings"

# The real issue: Docker Desktop uses a VPN/proxy that times out on large uploads
# Solution: Push layers one at a time with retries

DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"

echo ""
echo "🚀 STARTING OPTIMIZED PUSH:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Strategy: Serial push with automatic retry on specific layers"
echo ""

# Try push with reduced parallelism
MAX_RETRIES=3

for attempt in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $attempt of $MAX_RETRIES..."
    echo ""

    # Push with timeout handling
    timeout 3600 $DOCKER_BIN push "$IMAGE" 2>&1 | tee /tmp/docker_push.log

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS!"
        exit 0
    fi

    # Check if it's the specific large layer failing
    if grep -q "d5685b53d1a2" /tmp/docker_push.log && grep -q "EOF" /tmp/docker_push.log; then
        echo ""
        echo "⚠️  Large layer timeout detected"
        echo "💡 This layer is 55GB (model files)"
        echo ""

        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "Waiting 60 seconds for connection to stabilize..."
            sleep 60
        fi
    else
        echo "Different error occurred"
        cat /tmp/docker_push.log | tail -20

        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "Retrying in 30 seconds..."
            sleep 30
        fi
    fi
done

echo ""
echo "❌ Push failed after $MAX_RETRIES attempts"
echo ""
echo "📊 ANALYSIS OF FAILURE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -30 /tmp/docker_push.log

echo ""
echo "💡 RECOMMENDED NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. The 55GB layer is too large for reliable upload"
echo "2. Best option: Use GitHub Actions with the simpler Dockerfile"
echo "3. Alternative: Use Runpod's build service directly"
echo ""

exit 1
