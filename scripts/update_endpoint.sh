#!/bin/bash
# Update Runpod endpoint to use v2 image

curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/update" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk" \
  -H "Content-Type: application/json" \
  -d '{"imageName": "kaspamontana/ugc-faceswapper:v2"}'
