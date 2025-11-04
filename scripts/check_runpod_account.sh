#!/bin/bash
# Check Runpod account and list endpoints

API_KEY="rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk"

echo "🔍 Checking Runpod account..."
echo ""

# List endpoints
curl -X POST "https://api.runpod.io/graphql?api_key=$API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { myself { serverlessDiscount { discountFactor } endpoints { id name templateId } } }"}' \
  2>&1 | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
