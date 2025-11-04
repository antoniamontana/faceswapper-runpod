# Complete Deployment Guide - Runpod Network Volume Approach

## Overview

This guide uses Runpod's Network Volume feature to separate the Docker image (code) from the model (14GB).

**Why this works:**
- Docker image: ~2GB (just code and dependencies)
- Model: 14GB (stored on persistent Runpod network volume)
- Total deployment time: ~60 minutes (mostly model download)

---

## Step 1: Create Runpod Network Volume (5 minutes)

1. Go to: https://www.runpod.io/console/user/storage
2. Click **"+ Network Volume"**
3. Configure:
   - **Name:** `faceswap-models`
   - **Size:** `100 GB` (allows room for model + temp files)
   - **Region:** Choose closest to your users (e.g., `US-West`, `EU-Central`)
4. Click **"Create"**
5. **IMPORTANT:** Note the **Volume ID** (looks like: `abc123xyz`)

**Cost:** ~$20/month for 100GB persistent storage

---

## Step 2: Push Docker Image (in progress)

The ultra-minimal Docker image is being built now:
- Image: `ghcr.io/antoniamontana/faceswapper-runpod:ultra-minimal`
- Size: ~2GB
- Contains: Handler code, Wan2.2 repo, basic dependencies

Once build completes, push to GitHub Container Registry:
```bash
docker push ghcr.io/antoniamontana/faceswapper-runpod:ultra-minimal
```

---

## Step 3: Download Model to Network Volume (ONE TIME - 40 minutes)

This is a ONE-TIME setup. After this, the model persists forever.

### 3.1 Create Temporary Pod

1. Go to: https://www.runpod.io/console/pods
2. Click **"+ Deploy"**
3. Configure:
   - **GPU:** Any cheap GPU (even RTX 3060 works - we're just downloading)
   - **Template:** Select "RunPod PyTorch"
   - **Network Volume:** Select `faceswap-models` (the volume you created)
   - **Container Disk:** 10GB (minimum needed for downloading)
4. Click **"Deploy On-Demand"**

### 3.2 Download Model via Terminal

1. Once pod is running, click **"Connect"** → **"Start Web Terminal"**

2. In the terminal, run these commands:

```bash
# Navigate to network volume mount point
cd /workspace

# Create models directory
mkdir -p models
cd models

# Download Wan2.2-Animate-14B from Hugging Face
# This will take ~30-40 minutes (14GB download)
huggingface-cli download Wan-AI/Wan2.2-Animate-14B \
  --local-dir ./Wan2.2-Animate-14B

# Verify download completed
ls -lh Wan2.2-Animate-14B/

# You should see model files totaling ~14GB
# Example output:
# total 14G
# -rw-r--r-- 1 root root 5.2G model-00001.safetensors
# -rw-r--r-- 1 root root 4.8G model-00002.safetensors
# ...
```

3. **IMPORTANT:** Once download completes, **STOP THE POD** (you don't need it anymore)
   - Go back to Pods console
   - Click "Stop" on your temporary pod
   - This saves money - you only pay for the ~40 minutes of download time

---

## Step 4: Configure Runpod Serverless Endpoint (2 minutes)

1. Go to: https://www.runpod.io/console/serverless
2. Find your endpoint: `eaj61xejeec2iw`
3. Click **"Edit"** or **"Settings"**

### 4.1 Update Container Image

```
ghcr.io/antoniamontana/faceswapper-runpod:ultra-minimal
```

(Or use `:latest` tag once we set that up)

### 4.2 Attach Network Volume

- **Network Volume:** Select `faceswap-models` from dropdown
- This mounts your volume at `/runpod-volume/` inside the container

### 4.3 Set Container Disk

```
20 GB
```

(Reduced from before since model is on network volume!)

### 4.4 Environment Variables

```bash
MODEL_PATH=/runpod-volume/models/Wan2.2-Animate-14B
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_REGION=us-east-1
S3_BUCKET=faceswap-outputs-kasparas
WEBHOOK_URL=https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy
```

### 4.5 GPU Configuration

- **GPU Types:** RTX 4090, A100 (or your preference)
- **Workers:** Min: 0, Max: 3
- **Idle Timeout:** 5 seconds

5. Click **"Save"** or **"Update Endpoint"**

---

## Step 5: Test Deployment (5 minutes)

Once the endpoint is configured, test it:

```bash
cd /Users/kasparas/Library/Mobile\ Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/scripts

./test_endpoint.sh \
  "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" \
  "https://randomuser.me/api/portraits/men/32.jpg"
```

**Expected behavior:**
1. First run: 2-5 minutes
   - Worker cold start: ~30 seconds
   - Model loads from network volume: ~20 seconds
   - Processing: 1-4 minutes
2. Subsequent runs: 1-3 minutes (model already loaded)

---

## Step 6: Monitor Results

### Check Runpod Logs
1. Go to: https://www.runpod.io/console/serverless
2. Click on your endpoint
3. Click "Logs" tab
4. Watch for:
   - "Model loaded successfully"
   - "Processing video..."
   - "Upload to S3 complete"

### Check S3 Bucket
1. Go to: https://s3.console.aws.amazon.com/s3/buckets/faceswap-outputs-kasparas
2. Look for newly created video files
3. Download and verify the face swap worked

### Check Make.com Webhook
1. Your webhook will receive:
```json
{
  "status": "success",
  "record_id": "...",
  "output_url": "https://faceswap-outputs-kasparas.s3.amazonaws.com/...",
  "processing_time": 123.45
}
```

---

## Troubleshooting

### Model Not Found Error
```
Error: Model not found at /runpod-volume/models/Wan2.2-Animate-14B
```

**Fix:**
- Verify network volume is attached to endpoint
- Check model was downloaded correctly: Create a temporary pod, attach volume, run `ls /workspace/models/`

### Out of Memory Error
```
CUDA out of memory
```

**Fix:**
- Increase GPU type (try A100 instead of RTX 4090)
- Reduce batch size in config.yaml

### Slow Processing
```
Processing takes >10 minutes
```

**Fix:**
- Check GPU type (should be RTX 4090 or A100)
- Verify model is loading from network volume, not downloading each time
- Check Runpod logs for "Model already loaded" vs "Loading model..."

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Network Volume | $20/month | 100GB persistent storage |
| Runpod Compute | $0.50-1.00/video | Pay per use, auto-scales to zero |
| S3 Storage | ~$0.023/GB/month | Output videos |
| S3 Transfer | ~$0.09/GB | Data transfer out |

**Example monthly cost (100 videos):**
- Network volume: $20
- Compute: $50-100 (100 videos × $0.50-1.00)
- S3: ~$5
- **Total: ~$75-125/month**

---

## Next Steps After Successful Test

1. **Update GitHub Actions** to automatically deploy new versions
2. **Set up monitoring** for failed jobs
3. **Optimize** worker configuration based on usage patterns
4. **Scale** by increasing max workers if needed

---

## Success Checklist

- [ ] Network volume created (100GB)
- [ ] Model downloaded to network volume (verify with `ls`)
- [ ] Docker image pushed to ghcr.io
- [ ] Endpoint configured with network volume
- [ ] Environment variables set
- [ ] Test video processed successfully
- [ ] Output appears in S3 bucket
- [ ] Webhook received in Make.com

---

**Once all boxes are checked, you're DONE!** 🎉
