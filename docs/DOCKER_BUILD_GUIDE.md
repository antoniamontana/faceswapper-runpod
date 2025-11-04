# Docker Build & Deployment Guide

## Prerequisites

**Required:**
- Docker installed and running
- Docker Hub account (free)
- At least 30GB free disk space
- Stable internet connection (will download ~20GB)

**Estimated Time:** 2-3 hours (mostly automated)

---

## Step 1: Prepare Docker Hub (5 minutes)

### 1.1 Create Docker Hub Account
1. Go to: https://hub.docker.com/signup
2. Sign up (free account is fine)
3. Verify email

### 1.2 Login to Docker Hub
```bash
docker login
# Enter your Docker Hub username and password
```

### 1.3 Choose Your Image Name
Format: `yourusername/ugc-faceswapper:v1`

Example: `kasparas/ugc-faceswapper:v1`

---

## Step 2: Build Docker Image (120-180 minutes)

**⚠️ Warning:** This will download ~14GB model and take 2-3 hours!

### 2.1 Navigate to Docker Directory
```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/docker"
```

### 2.2 Build the Image
```bash
docker build -t yourusername/ugc-faceswapper:v1 .
```

Replace `yourusername` with your Docker Hub username.

**What happens during build:**
1. Installs Python and dependencies (10 min)
2. Clones Wan2.2 repository (2 min)
3. Downloads Wan2.2-Animate-14B model (~14GB) (30-60 min)
4. Installs Wan2.2 dependencies (10 min)
5. Copies application code (1 min)

**Expected Output:**
- Total build time: 2-3 hours
- Final image size: ~25GB
- You'll see: `Successfully tagged yourusername/ugc-faceswapper:v1`

### 2.3 Verify Image Built Successfully
```bash
docker images | grep ugc-faceswapper
```

You should see your image listed with size ~25GB.

---

## Step 3: Test Image Locally (Optional but Recommended)

### 3.1 Create Test Config
Create `/tmp/test_config.yaml`:
```yaml
storage:
  s3_bucket: "faceswap-outputs-kasparas"
  s3_access_key: "AKIAQPFMTVPPQLCI6X3X"
  s3_secret_key: "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"

airtable:
  api_key: "patlwJxGENTnKmGeF.48b68649086330d63c1496993b1fd91697eb7f41bc5887d08a00e45c63845395"
  base_id: "appHjohuWApnPJvd3"

webhook:
  completion_url: "https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy"
```

### 3.2 Run Container Locally
```bash
docker run --rm -p 8080:8080 \
  -v /tmp/test_config.yaml:/app/config.yaml:ro \
  --gpus all \
  yourusername/ugc-faceswapper:v1
```

**Note:** `--gpus all` requires NVIDIA GPU. If you don't have one, skip local testing.

### 3.3 Test Health Endpoint
```bash
curl http://localhost:8080/health
```

Should return: `{"status": "healthy"}`

**Press Ctrl+C to stop the container**

---

## Step 4: Push to Docker Hub (30-60 minutes)

### 4.1 Push Image
```bash
docker push yourusername/ugc-faceswapper:v1
```

**This uploads ~25GB - will take 30-60 minutes depending on internet speed.**

### 4.2 Verify Upload
1. Go to: https://hub.docker.com/
2. Login
3. You should see `yourusername/ugc-faceswapper` in your repositories
4. Click on it → Tags → You should see `v1` tag

---

## Step 5: Create Runpod Template (10 minutes)

### 5.1 Go to Runpod
1. Login to: https://www.runpod.io/
2. Click **Serverless** in sidebar
3. Click **+ New Endpoint**

### 5.2 Configure Template

**Container Image:**
```
yourusername/ugc-faceswapper:v1
```

**Container Disk:** `50 GB` (model is ~25GB)

**Environment Variables - Add these:**
```
CONFIG_YAML=/app/config.yaml
```

**Advanced Configuration:**
- **Container Start Command:** Leave empty (uses CMD from Dockerfile)
- **Idle Timeout:** `60` seconds
- **Max Workers:** `1`

**GPU Selection:**
- Select: **NVIDIA A40** (24GB VRAM)
- Or: **NVIDIA A100** (if A40 unavailable)

### 5.3 Create Endpoint
1. Click **Deploy**
2. Wait for initialization (~2-3 minutes)
3. **Copy the Endpoint ID** - looks like: `abc123def456`

---

## Step 6: Update Make.com Scenario 2 (5 minutes)

### 6.1 Get Full Endpoint URL
Format: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run`

Example: `https://api.runpod.ai/v2/abc123def456/run`

### 6.2 Update Make.com
1. Go to: https://www.make.com/
2. Open **Scenario 2: Main Pipeline**
3. Click on the **HTTP module**
4. Update **URL** to: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run`
5. Verify **Authorization** header still has: `Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk`
6. Click **OK**
7. **Save scenario**
8. Toggle scenario **ON**

---

## Step 7: End-to-End Test (10 minutes)

### 7.1 Add Test Row to Airtable
1. Go to: https://airtable.com/appHjohuWApnPJvd3
2. Add a new row:
   - **Source_Video_URL:** Use a public 30-second video URL
   - **Avatar_Image_URL:** Use a public image URL (JPEG/PNG of a face)
   - **Status:** `Pending`
   - **Batch_ID:** `test-001`

### 7.2 Wait and Monitor
- Make.com checks every 5 minutes
- After 5 min: Status should change to `Processing`
- After 8-12 min: Status should change to `Complete`
- **Output_Video_URL** field should be populated

### 7.3 Verify Output
1. Click the URL in **Output_Video_URL**
2. Video should open from S3
3. Segments 1 & 3 should have face-swapped with your avatar
4. Segments 2 & 4 should be original

---

## Troubleshooting

### Build Fails: "flash-attn install failed"
**Solution:** This is expected and okay. The Dockerfile continues without it.

### Build Fails: "No space left on device"
**Solution:**
```bash
docker system prune -a --volumes
# Free up at least 30GB
```

### Push Takes Forever
**Solution:** Use faster internet or leave running overnight.

### Runpod Pod Fails to Start
**Solution:**
- Check Container Disk is at least 50GB
- Verify Docker image name is correct
- Check Runpod logs for errors

### Make.com Scenario Never Triggers
**Solution:**
- Verify Scenario 2 is **ON**
- Check scheduling is set to **every 5 minutes**
- Verify Airtable has row with Status = "Pending"

---

## Cost Breakdown

**One-time:**
- Docker Hub: Free
- Build time: Your computer's electricity (~$0.50)

**Per Video:**
- Runpod GPU (A40): ~$0.04-0.06 per video (3-5 min processing)
- S3 storage: ~$0.001 per video
- Make.com: Included in $29/month plan

**Total per video: ~$0.05**

---

## Next Steps After Successful Test

1. Process more videos!
2. Monitor costs in Runpod dashboard
3. Optimize segment timestamps if needed (config.yaml)
4. Scale up: Add more rows to Airtable

---

**System is now PRODUCTION READY! 🚀**
