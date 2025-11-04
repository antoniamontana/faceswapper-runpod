#!/bin/bash
# Monitor Docker push progress

echo "Monitoring Docker push to Docker Hub..."
echo "Image: kaspamontana/ugc-faceswapper:v2"
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
  clear
  echo "=== Docker Push Status ==="
  echo "Timestamp: $(date)"
  echo ""

  # Check if process is still running
  if pgrep -f "docker push kaspamontana/ugc-faceswapper:v2" > /dev/null; then
    echo "Status: PUSHING..."
    echo ""

    # Show recent docker activity
    docker images | grep ugc-faceswapper | head -3
  else
    echo "Status: COMPLETED or STOPPED"
    echo ""

    # Verify image on Docker Hub
    echo "Verifying image on Docker Hub..."
    docker manifest inspect kaspamontana/ugc-faceswapper:v2 > /dev/null 2>&1

    if [ $? -eq 0 ]; then
      echo "SUCCESS: Image is available on Docker Hub!"
      exit 0
    else
      echo "FAILED: Image not found on Docker Hub"
      exit 1
    fi
  fi

  sleep 10
done
