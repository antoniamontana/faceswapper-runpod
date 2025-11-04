#!/bin/bash
# Self-healing Docker build monitor with automatic retry and push
# Runs until completion without manual intervention

set -e

LOG_FILE="/tmp/docker_build_final.log"
BUILD_CMD='cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/docker" && env PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" /Applications/Docker.app/Contents/Resources/bin/docker build --platform linux/amd64 -t kaspamontana/ugc-faceswapper:v1 .'
PUSH_CMD='env PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" /Applications/Docker.app/Contents/Resources/bin/docker push kaspamontana/ugc-faceswapper:v1'
MAX_RETRIES=10
RETRY_COUNT=0

echo "=== Docker Build Auto-Monitor Started ==="
echo "Log file: $LOG_FILE"
echo "Max retries: $MAX_RETRIES"
echo ""

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "[$(date)] Build attempt $((RETRY_COUNT + 1))/$MAX_RETRIES"

    # Clear log for this attempt
    > "$LOG_FILE"

    # Run build
    if eval "$BUILD_CMD" 2>&1 | tee -a "$LOG_FILE"; then
        # Verify image actually exists
        if ! env PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" /Applications/Docker.app/Contents/Resources/bin/docker image inspect kaspamontana/ugc-faceswapper:v1 &>/dev/null; then
            echo "[$(date)] ✗ Build reported success but image doesn't exist, retrying..."
            RETRY_COUNT=$((RETRY_COUNT + 1))
            sleep 10
            continue
        fi

        echo ""
        echo "[$(date)] ✓ BUILD SUCCESS!"
        echo "[$(date)] Starting Docker push to registry..."

        if eval "$PUSH_CMD" 2>&1 | tee -a "$LOG_FILE"; then
            echo ""
            echo "[$(date)] ✓ PUSH SUCCESS!"
            echo "[$(date)] ===================================="
            echo "[$(date)] COMPLETE! Image ready at:"
            echo "  kaspamontana/ugc-faceswapper:v1"
            echo "[$(date)] ===================================="
            exit 0
        else
            echo "[$(date)] ✗ Push failed, retrying build+push..."
            RETRY_COUNT=$((RETRY_COUNT + 1))
            sleep 10
            continue
        fi
    else
        # Build failed - check error type
        RETRY_COUNT=$((RETRY_COUNT + 1))

        if grep -q "ReadTimeoutError\|TimeoutError\|Connection.*timed out\|Hash Sum mismatch" "$LOG_FILE"; then
            echo "[$(date)] ✗ Network timeout detected, retrying in 10s..."
            sleep 10
        elif grep -q "error getting credentials" "$LOG_FILE"; then
            echo "[$(date)] ✗ Credentials error, retrying in 5s..."
            sleep 5
        else
            echo "[$(date)] ✗ Unknown error, retrying in 15s..."
            sleep 15
        fi
    fi
done

echo "[$(date)] ✗✗✗ FAILED after $MAX_RETRIES attempts"
echo "[$(date)] Last 50 lines of log:"
tail -50 "$LOG_FILE"
exit 1
