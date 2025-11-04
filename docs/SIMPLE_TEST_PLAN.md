# SIMPLE TEST PLAN - Start Here

## What You ACTUALLY Have Already

### ✅ DONE - Infrastructure
- **Airtable**: Base created, API token configured
- **AWS S3**: Bucket created, credentials configured
- **Runpod**: Endpoint created (`eaj61xejeec2iw`)
- **Config**: All credentials in `config.yaml`

### ✅ DONE - Docker
- **Old Docker Image**: `kaspamontana/ugc-faceswapper:v1` (built previously)
- **Old Runpod Template**: `w5a7rfn9y1`
- **New Docker Fix**: GitHub workflow fixed (building now)

---

## What's MISSING (The Gap)

### ❌ Make.com Scenarios
You need 2 simple Make.com scenarios to connect everything:

**Scenario 1: Watch Airtable → Call Runpod**
- Watches Airtable for `Status = Pending`
- Calls Runpod endpoint with video/avatar URLs
- Updates Status to `Processing`

**Scenario 2: Receive Webhook → Update Airtable**
- Receives callback from Runpod when done
- Updates Airtable with output URL
- Sets Status to `Complete`

---

## THE SIMPLE SETUP (15 minutes)

### Step 1: Create Make.com Scenarios

#### Scenario 1: Main Pipeline
1. Go to https://make.com
2. Create new scenario
3. Add modules:
   - **Airtable: Watch Records**
     - Table: `Processing Queue`
     - Filter: `Status = Pending`
   - **HTTP: Make Request**
     - URL: `https://api.runpod.ai/v2/eaj61xejeec2iw/run`
     - Method: POST
     - Headers:
       - `Authorization`: `Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk`
       - `Content-Type`: `application/json`
     - Body:
       ```json
       {
         "input": {
           "record_id": "{{airtable.id}}",
           "source_video_url": "{{airtable.Source_Video_URL}}",
           "avatar_image_url": "{{airtable.Avatar_Image_URL}}"
         }
       }
       ```
   - **Airtable: Update Record**
     - Record ID: `{{airtable.id}}`
     - Status: `Processing`

#### Scenario 2: Webhook Receiver
1. Create new scenario
2. Add modules:
   - **Webhooks: Custom Webhook** (copy the webhook URL)
   - **Airtable: Update Record**
     - Record ID: `{{webhook.record_id}}`
     - Status: `{{webhook.status}}`
     - Output_Video_URL: `{{webhook.output_url}}`
     - Error_Log: `{{webhook.error}}`

### Step 2: Test With Your Files

You ALREADY uploaded test files to S3:
- **Video**: `s3://faceswap-outputs-kasparas/test-inputs/test-ugc-ESP.mp4`
- **Avatar**: `s3://faceswap-outputs-kasparas/test-inputs/avatar-test-ESP.png`

Just add a row to Airtable:
1. Go to https://airtable.com/appHjohuWApnPJvd3
2. Add new record:
   - `Source_Video_URL`: Presigned URL or make files public
   - `Avatar_Image_URL`: Presigned URL or make files public
   - `Status`: `Pending`
3. Wait for Make.com to process (checks every 5 min)

---

## ALTERNATIVE: Direct Runpod Test (Skip Make.com)

You can test Runpod directly without Make.com:

```bash
curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/run" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "record_id": "test-001",
      "source_video_url": "https://...",
      "avatar_image_url": "https://..."
    }
  }'
```

Then check job status:
```bash
curl -X GET "https://api.runpod.ai/v2/eaj61xejeec2iw/status/{job_id}" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk"
```

---

## Why It Was Complex Before

I was testing Runpod directly (which works!) but you want the FULL FLOW:
**Airtable → Make.com → Runpod → Make.com → Airtable**

The ONLY missing piece is Make.com automation.

---

## Next Steps (Choose One)

### Option A: Set up Make.com (15 min)
- Follow Step 1 above
- Test with Airtable

### Option B: Just test Runpod works (5 min)
- Make your S3 files public or generate new presigned URLs
- Use curl command above
- Verify processing works

### Option C: Wait for GitHub build (10 min)
- Build should be done soon
- Then deploy new image to Runpod
- Then do Option A or B

---

## Questions?

Tell me which option you want and I'll help you complete it.
