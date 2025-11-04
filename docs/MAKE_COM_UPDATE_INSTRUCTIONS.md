# Make.com Scenario 2 Update Instructions

## SUCCESS! Docker Build Complete

**Docker Image**: `kaspamontana/ugc-faceswapper:v1` (67.7GB)
**Runpod Template ID**: `w5a7rfn9y1`
**Template Name**: UGC FaceSwapper V1

---

## Next Step: Update Make.com Scenario 2

### Instructions:

1. **Go to Make.com**
   - URL: https://www.make.com/
   - Login if needed

2. **Open Scenario 2: Main Pipeline**
   - Find "Scenario 2: Main Pipeline" in your scenarios list
   - Click to open

3. **Click on the HTTP Module**
   - This is the module that calls Runpod API
   - Should be labeled "Make an HTTP Request" or similar

4. **Update the URL field**
   - Current URL: `https://api.runpod.ai/v2/{template_id}/run`
   - **New URL**: `https://api.runpod.ai/v2/w5a7rfn9y1/run`

5. **Verify Authorization Header**
   - Header name: `Authorization`
   - Header value: `Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk`
   - (Should already be set from initial setup)

6. **Save and Enable**
   - Click **OK** to save module
   - Click **Save** to save scenario
   - Toggle scenario **ON**

---

## What's Ready:

- ✅ Docker image built and pushed to Docker Hub
- ✅ Runpod template created (ID: w5a7rfn9y1)
- ✅ Config file updated with template ID
- ✅ Make.com Scenario 1 (Watch Records) already ON
- ⏳ Make.com Scenario 2 needs URL update (manual step above)

---

## After Make.com Update:

The system will be ready for end-to-end testing:

1. Add test row to Airtable (https://airtable.com/appHjohuWApnPJvd3):
   - **Source_Video_URL**: Public 30-sec video URL
   - **Avatar_Image_URL**: Public face image URL
   - **Status**: `Pending`
   - **Batch_ID**: `test-001`

2. Monitor progress:
   - Make.com checks Airtable instantly (webhook trigger)
   - Status → `Processing` (within 1 minute)
   - Runpod spins up container (45-60 sec)
   - Processing completes (3-5 min)
   - Status → `Complete`
   - Output_Video_URL populated with S3 link

3. Verify output video has face-swapped segments

---

## Technical Details:

**Runpod Template Configuration:**
- Container Image: kaspamontana/ugc-faceswapper:v1
- Container Disk: 80 GB
- Volume: 0 GB (models pre-installed in image)
- Exposed Port: 8080/http
- Environment Variables:
  - MODEL_PATH=/models/wan2.2-animate
  - CUDA_VISIBLE_DEVICES=0
- Mode: Serverless (on-demand)

**API Endpoint:**
- POST `https://api.runpod.ai/v2/w5a7rfn9y1/run`
- Authorization: `Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk`
- Content-Type: `application/json`

---

## Questions?

All configuration values are stored in:
`config/config.yaml`

No code changes needed - just update Make.com URL and you're ready to test!
