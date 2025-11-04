#!/bin/bash
# Check Runpod job status
# USAGE: ./check_status.sh <job_id>

JOB_ID="${1}"

if [ -z "$JOB_ID" ]; then
  echo "Error: Job ID required"
  echo "Usage: ./check_status.sh <job_id>"
  exit 1
fi

curl -X GET "https://api.runpod.ai/v2/eaj61xejeec2iw/status/$JOB_ID" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk"
