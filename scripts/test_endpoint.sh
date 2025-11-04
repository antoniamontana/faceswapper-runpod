#!/bin/bash
# Test Runpod endpoint with sample video
# USAGE: ./test_endpoint.sh <source_video_url> <avatar_image_url>

SOURCE_VIDEO_URL="${1:-https://example.com/test-video.mp4}"
AVATAR_IMAGE_URL="${2:-https://example.com/test-avatar.jpg}"

curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/run" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk" \
  -H "Content-Type: application/json" \
  -d "{
    \"input\": {
      \"record_id\": \"test001\",
      \"source_video_url\": \"$SOURCE_VIDEO_URL\",
      \"avatar_image_url\": \"$AVATAR_IMAGE_URL\",
      \"webhook_url\": \"https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy\"
    }
  }"
