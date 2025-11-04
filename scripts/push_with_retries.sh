#!/bin/bash
# Push Docker image with automatic retries on failure

IMAGE="kaspamontana/ugc-faceswapper:v2"
MAX_RETRIES=5

echo "🚀 Starting push of $IMAGE with retry logic..."

for i in $(seq 1 $MAX_RETRIES); do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Attempt $i of $MAX_RETRIES"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    /Applications/Docker.app/Contents/Resources/bin/docker push "$IMAGE"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Image pushed to Docker Hub"
        echo ""
        echo "Next steps:"
        echo "1. cd scripts"
        echo "2. ./update_endpoint.sh"
        echo "3. ./test_endpoint.sh VIDEO_URL AVATAR_URL"
        exit 0
    else
        echo "❌ Attempt $i failed"
        if [ $i -lt $MAX_RETRIES ]; then
            echo "⏳ Waiting 30 seconds before retry..."
            sleep 30
        fi
    fi
done

echo ""
echo "❌ All $MAX_RETRIES attempts failed"
echo "Consider using Option 2 or 3 from the guide"
exit 1
