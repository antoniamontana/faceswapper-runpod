# Troubleshooting Checklist - Output Video URL Not Appearing

## Diagnostic Questions

### 1. Check Airtable Status

**What does the Status field show?**
- [ ] Still "Pending" → Make.com didn't trigger
- [ ] "Processing" → RunPod is working or stuck
- [ ] "Failed" → Check Error_Log field
- [ ] "Complete" but no URL → S3 upload issue

**What does the Error_Log field say?**
- Write down exact error message:

---

## 2. Check Make.com Execution History

**Go to:** https://make.com/scenarios

**Check "Face Swap - Main Pipeline":**
1. Click the scenario name
2. Click "History" tab
3. Look at recent executions (last 30 minutes)

**Questions:**
- [ ] Did it run at all?
- [ ] Did it show any errors?
- [ ] Did it successfully call RunPod?
- [ ] What was the response from RunPod?

**If you see errors, write them here:**

---

## 3. Check RunPod Endpoint Status

**Go to:** https://www.runpod.io/console/serverless

**Find endpoint:** eaj61xejeec2iw

**Check:**
- [ ] Is endpoint "Active"?
- [ ] Are there any workers running?
- [ ] Click "Logs" - what do you see?
- [ ] Click "Requests" - do you see your request?

**If you see errors in logs, write them here:**

---

## 4. Check RunPod Endpoint Configuration

**Verify settings:**

**Container Image:**
- Should be: `ghcr.io/antoniamontana/faceswapper-runpod:v2` or similar
- Current value: _________________

**Network Volume:**
- Should be: `faceswap-models` (or your volume name)
- Current value: _________________
- Is it attached? Yes / No

**Environment Variables - Check these exist:**
- [ ] MODEL_PATH
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY
- [ ] AWS_REGION
- [ ] S3_BUCKET
- [ ] WEBHOOK_URL

---

## 5. Test RunPod Endpoint Directly

Let's bypass Make.com and test RunPod directly.

**Copy your RunPod endpoint URL and API key:**
- Endpoint ID: `eaj61xejeec2iw`
- API Key: (from RunPod settings)

**Then run this test:**

```bash
curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -d '{
    "input": {
      "avatar_url": "https://faceswap-outputs-kasparas.s3.us-east-1.amazonaws.com/test-inputs/avatar-test-ESP.png",
      "video_url": "https://faceswap-outputs-kasparas.s3.us-east-1.amazonaws.com/test-inputs/test-ugc-ESP.mp4",
      "batch_id": "direct-test-001"
    }
  }'
```

**What happened?**
- Response: _________________

---

## 6. Common Issues & Solutions

### Issue: Status Stays "Pending"
**Cause:** Make.com scenario not triggering
**Fix:**
1. Make sure scenarios are ON
2. Try manually running the scenario in Make.com
3. Check Airtable connection in Make.com

### Issue: Status "Processing" for >20 minutes
**Cause:** RunPod worker stuck or not available
**Fix:**
1. Check RunPod endpoint has workers configured
2. Check if network volume is attached correctly
3. Look at RunPod logs for errors

### Issue: Status "Failed" with Error
**Cause:** Depends on error message
**Common errors:**
- "No workers available" → Need to configure workers in RunPod
- "Model not found" → Network volume not attached or model not downloaded
- "Face not detected" → Image quality issue
- "S3 upload failed" → Check AWS credentials

### Issue: Status "Complete" but No URL
**Cause:** S3 upload failed but webhook succeeded
**Fix:**
1. Check AWS credentials in RunPod env vars
2. Check S3 bucket name is correct
3. Check IAM permissions for S3 upload

---

## Next Steps

Based on what you find above, we'll:
1. Fix the specific issue
2. Re-test with a new row in Airtable
3. Monitor until we see the output video URL

---

## Quick Win Test

If everything above looks confusing, let's do this:

**Option A: Test RunPod Directly**
I can give you a simple curl command to test just the RunPod endpoint, bypassing Make.com entirely.

**Option B: Check Make.com Logs**
Share what you see in Make.com History tab - I can decode the errors.

**Option C: Check RunPod Logs**
Share what you see in RunPod Logs - I can identify the issue.

Which would you like to do first?
