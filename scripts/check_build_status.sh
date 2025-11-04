#!/bin/bash
# Check GitHub Actions build status

REPO="antoniamontana/faceswapper-runpod"

echo "🔍 Checking GitHub Actions build status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Repository: $REPO"
echo "URL: https://github.com/$REPO/actions"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To check build progress:"
echo "1. Visit: https://github.com/$REPO/actions"
echo "2. Click on the latest workflow run"
echo "3. Click 'build-and-push' job"
echo "4. Expand steps to see live logs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Expected stages (60-90 min total):"
echo "  [2 min]  ✓ Checkout code"
echo "  [5 min]  ⏳ Pull PyTorch base image"
echo "  [2 min]  ⏳ Install git + ffmpeg"
echo "  [15 min] ⏳ Install Python packages"
echo "  [2 min]  ⏳ Clone Wan2.2 repo"
echo "  [40 min] ⏳ Download Wan2.2 model (LONGEST STEP)"
echo "  [15 min] ⏳ Push to Docker Hub"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Try to get status via API
echo "Fetching latest run status via API..."
curl -s "https://api.github.com/repos/$REPO/actions/runs?per_page=1" | \
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('workflow_runs'):
        run = data['workflow_runs'][0]
        print(f\"Status: {run['status']}\")
        print(f\"Conclusion: {run.get('conclusion', 'N/A')}\")
        print(f\"Started: {run['created_at']}\")
        print(f\"URL: {run['html_url']}\")
    else:
        print('No runs found')
except:
    print('Could not parse API response')
" 2>/dev/null || echo "API check not available - use web URL above"

echo ""
