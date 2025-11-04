#!/bin/bash
# Continuous GitHub Actions monitoring

REPO="antoniamontana/faceswapper-runpod"
CHECK_COUNT=0
MAX_CHECKS=180  # 180 checks x 1 min = 3 hours

echo "🔄 CONTINUOUS BUILD MONITORING STARTED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Repository: $REPO"
echo "Max monitoring time: 3 hours"
echo "Check interval: 60 seconds"
echo ""

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Check #$CHECK_COUNT"

    # Get latest run status
    RESPONSE=$(curl -s "https://api.github.com/repos/$REPO/actions/runs?per_page=1")

    # Parse with Python
    STATUS=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('workflow_runs') and len(data['workflow_runs']) > 0:
        run = data['workflow_runs'][0]
        print(f'{run[\"status\"]}:{run.get(\"conclusion\", \"running\")}:{run[\"html_url\"]}')
    else:
        print('no_runs:::')
except:
    print('error:::')
" 2>&1)

    IFS=':' read -r BUILD_STATUS CONCLUSION URL <<< "$STATUS"

    echo "  Status: $BUILD_STATUS"
    echo "  Conclusion: $CONCLUSION"

    if [ "$BUILD_STATUS" = "completed" ]; then
        if [ "$CONCLUSION" = "success" ]; then
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "✅ BUILD SUCCESSFUL!"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Image: kaspamontana/ugc-faceswapper:v2"
            echo "URL: $URL"
            echo ""
            echo "NEXT STEPS:"
            echo "1. cd scripts"
            echo "2. ./update_endpoint.sh"
            echo "3. ./test_endpoint.sh VIDEO_URL AVATAR_URL"
            exit 0
        else
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "❌ BUILD FAILED"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Conclusion: $CONCLUSION"
            echo "URL: $URL"
            echo ""
            echo "Check the logs at: $URL"
            exit 1
        fi
    elif [ "$BUILD_STATUS" = "in_progress" ] || [ "$BUILD_STATUS" = "queued" ]; then
        echo "  ⏳ Build is running..."
    elif [ "$BUILD_STATUS" = "no_runs" ]; then
        echo "  ⏸️  No runs found - build may be starting..."
    else
        echo "  ⚠️  Unknown status: $BUILD_STATUS"
    fi

    echo ""
    sleep 60
done

echo "⏱️  Monitoring timeout after $MAX_CHECKS checks"
echo "Check manually at: https://github.com/$REPO/actions"
