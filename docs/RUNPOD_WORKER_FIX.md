# Fix RunPod IN_QUEUE Issue - No Workers Available

## The Problem

**Job Status:** `IN_QUEUE`
**Job ID:** `95e0673d-910f-4b4d-817e-49752bd62d05-e2`

**This means:** RunPod received your job but has NO WORKERS to process it.

---

## The Fix (5 minutes)

### Step 1: Configure Workers

1. Go to: https://www.runpod.io/console/serverless
2. Click on endpoint: **eaj61xejeec2iw**
3. Look for the **"Workers"** section or **"Configuration"** tab

### Step 2: Set Worker Configuration

You need to configure:

**Active Workers:**
- Minimum: `0` (to save money when idle)
- Maximum: `3` (or more if you need high throughput)

**GPU Type:**
- Select a GPU that can run the model
- Recommended: **RTX A4000** or **RTX 4090** (good balance of speed/cost)
- Budget: **RTX 3090** works too

**Container Disk:**
- Set to: **20-50 GB**

**Worker Configuration:**
```
Min Workers: 0
Max Workers: 3
GPU: RTX A4000 (or RTX 4090)
Container Disk: 20 GB
Idle Timeout: 5 seconds
```

### Step 3: Check Network Volume is Attached

**Critical:** Make sure the network volume is attached!

In the endpoint settings, look for:
- **Network Volume:** Should show `faceswap-models` (or your volume name)
- If it says "None" or empty → **Attach it!**

---

## Common Configurations

### Option A: Cost-Optimized (Recommended)
```
Min Workers: 0 (no cost when idle)
Max Workers: 1
GPU: RTX 3090
Idle Timeout: 5 seconds
```
**Cost:** ~$0.50-1.00 per video, $0 when idle

### Option B: Performance
```
Min Workers: 1 (always ready)
Max Workers: 3
GPU: RTX A4000
Idle Timeout: 30 seconds
```
**Cost:** ~$0.30/hour idle + per-video cost

### Option C: Budget
```
Min Workers: 0
Max Workers: 1
GPU: RTX 3070
Idle Timeout: 5 seconds
```
**Cost:** ~$0.30-0.60 per video, $0 when idle

---

## After Configuring Workers

### The job will start processing:

1. RunPod spins up a worker (2-3 min first time)
2. Worker loads the model from network volume (1-2 min)
3. Processes video (2-5 min depending on length)
4. Uploads to S3 and sends webhook
5. Airtable updates with video URL

**Total time:** 5-10 minutes for first run, 3-5 min after that

---

## Check if it's Working

### Monitor the job status:

**Option 1: RunPod Console**
- Go to endpoint → Requests tab
- Click on your job ID
- Status should change: `IN_QUEUE` → `IN_PROGRESS` → `COMPLETED`

**Option 2: API Query**
```bash
curl -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  https://api.runpod.ai/v2/eaj61xejeec2iw/status/95e0673d-910f-4b4d-817e-49752bd62d05-e2
```

### What to expect:

**First time (cold start):**
- 2-3 min: Worker starting up
- 1-2 min: Loading model from network volume
- 2-5 min: Processing video
- **Total:** 5-10 minutes

**Subsequent runs (warm):**
- Worker already running
- Model already loaded
- **Total:** 2-5 minutes

---

## Troubleshooting

### If still IN_QUEUE after 5 minutes:

**Check:**
1. Did you set Max Workers > 0?
2. Is GPU selected?
3. Is network volume attached?
4. Are there available GPUs in that region?

**Try:**
- Change to different GPU type
- Increase Max Workers to 1
- Check RunPod status page for GPU availability

### If worker starts but fails:

**Check logs in RunPod console:**
- Look for errors about missing model
- Check if MODEL_PATH is correct: `/runpod-volume/models/Wan2.2-Animate-14B`
- Verify network volume has the model

---

## Expected Costs

| Configuration | Idle Cost | Per-Video Cost | Total/Month (10 videos) |
|--------------|-----------|----------------|-------------------------|
| Min=0, Max=1 | $0/hour | ~$0.50-1.00 | ~$5-10 + $20 storage |
| Min=1, Max=1 | ~$0.30/hour | ~$0.50-1.00 | ~$220-250 + storage |

**Recommended:** Min=0, Max=1 (only pay when processing)

---

## Quick Checklist

Before the job will process, verify:

- [ ] Max Workers > 0
- [ ] GPU type selected
- [ ] Network volume `faceswap-models` is attached
- [ ] Container disk >= 20GB
- [ ] Environment variables set (MODEL_PATH, AWS credentials, etc.)

**Once all checked → Save → Job should start processing!**

---

## Need Help?

After configuring workers, tell me:
1. What GPU did you select?
2. What's your Min/Max worker config?
3. Is network volume attached?

Then we'll monitor if the job starts processing.
