# TEST NOW - Simple 3-Step Process

## What You Have
✅ Make.com scenarios already created (2025-10-30)
✅ Test files uploaded to S3
✅ Airtable base ready
✅ Runpod endpoint configured

## Step 1: Make Sure Make.com Scenarios Are ON

Go to https://make.com and check:

1. **Face Swap - Main Pipeline** → Toggle should be **ON** ✓
2. **Face Swap - Webhook Receiver** → Toggle should be **ON** ✓

If either is OFF, click the toggle to turn it ON.

## Step 2: Add Test Row to Airtable

Go to your Airtable base:
👉 https://airtable.com/appHjohuWApnPJvd3

Add a new record with these EXACT values:

### Avatar Image URL:
```
https://faceswap-outputs-kasparas.s3.us-east-1.amazonaws.com/test-inputs/avatar-test-ESP.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQPFMTVPPQLCI6X3X%2F20251104%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251104T124726Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=ac492efbaa9c37843f0e948a7c0e89c5ae2b5b4045ecf2acdd0ec7df1c237888
```

### Source Video URL:
```
https://faceswap-outputs-kasparas.s3.us-east-1.amazonaws.com/test-inputs/test-ugc-ESP.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAQPFMTVPPQLCI6X3X%2F20251104%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251104T124726Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=a10f1cd94468647a1f2a2b92331b946b45cfb3c3d55f30522d123f45b56b546f
```

### Other Fields:
- **Batch_ID**: `test-esp-001`
- **Status**: Select `Pending`

## Step 3: Watch It Process

### Timeline:
- **0-5 minutes**: Make.com checks Airtable (runs every 5 min or on webhook)
- **Status changes to**: `Processing`
- **5-15 minutes**: Runpod spins up worker and processes video
- **Status changes to**: `Complete` (or `Failed`)
- **Output_Video_URL**: Will be populated with S3 link

### What to Watch:
1. Refresh Airtable every minute
2. Watch the Status field change: `Pending` → `Processing` → `Complete`
3. Once Complete, click the `Output_Video_URL` to download your face-swapped video

## If It Fails:

Check the `Error_Log` field in Airtable for details.

Common issues:
- **"No workers available"**: Runpod endpoint might not have workers configured
- **"Face not detected"**: Avatar image quality issue
- **"Timeout"**: Video too long/large

## Troubleshooting:

### If Status Stays "Pending" After 5 Minutes:
- Check Make.com → "Face Swap - Main Pipeline" → History tab for errors
- Verify the scenario is ON
- Check if Airtable connection is valid

### If Status Stuck at "Processing":
- Go to Runpod → Endpoints → eaj61xejeec2iw
- Check if workers are active
- Check if endpoint is configured correctly

### If You Get "Failed" Status:
- Read the Error_Log field
- The error message will tell you exactly what went wrong

---

## That's It!

No coding, no terminal commands, no complexity.

Just:
1. Turn ON scenarios
2. Add row to Airtable
3. Wait and watch

Your test video will be face-swapped automatically.

## Next Test:

Once this works, you can add MORE rows to Airtable with different avatars, and they'll all process automatically!

---

**Questions?** Let me know what you see happening in Airtable.
