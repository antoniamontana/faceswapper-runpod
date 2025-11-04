#!/bin/bash
# Update Runpod endpoint to use v2 image

API_KEY="rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk"
ENDPOINT_ID="eaj61xejeec2iw"
IMAGE="kaspamontana/ugc-faceswapper:v2"

echo "🔄 Updating Runpod endpoint..."
echo "Endpoint ID: $ENDPOINT_ID"
echo "Image: $IMAGE"
echo ""

# Update endpoint via GraphQL
curl -X POST "https://api.runpod.io/graphql?api_key=$API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { updateEndpoint(input: { endpointId: \\\"$ENDPOINT_ID\\\", imageName: \\\"$IMAGE\\\" }) { id imageName } }\"}" \
  2>&1 | python3 -m json.tool

echo ""
echo "✅ Update complete!"
echo ""
echo "Next: Test the endpoint with:"
echo "./test_endpoint.sh \"VIDEO_URL\" \"AVATAR_URL\""
