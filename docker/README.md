# Docker Image Build Instructions

## Overview
This Docker image contains the GPU processing environment for face-swapping videos using Wan2.2-Animate model.

## Prerequisites
- Docker installed
- NVIDIA Docker runtime installed
- Access to Wan2.2-Animate model weights
- Docker Hub account (for pushing image)

## Build Instructions

### Step 1: Obtain Wan2.2-Animate Model
The model is ~15GB and needs to be downloaded before building.

**Option A: Direct Download (if available)**
```bash
cd models/
# Download model files here
# This step depends on where the model is hosted
```

**Option B: From Hugging Face/GitHub**
```bash
# Install git-lfs if needed
git lfs install

# Clone model repository
cd models/
git clone https://huggingface.co/path/to/wan2-animate
# OR
git clone https://github.com/path/to/wan2-model
```

**NOTE:** The exact download method depends on Wan2.2-Animate distribution.
Check the official repository for instructions.

### Step 2: Build Docker Image
```bash
# From project root
cd docker/

# Build image (this will take 30-60 minutes due to model size)
docker build -t ugc-faceswapper:v1 .

# Tag for Docker Hub
docker tag ugc-faceswapper:v1 YOUR_DOCKERHUB_USERNAME/ugc-faceswapper:v1
```

### Step 3: Test Locally (Optional)
```bash
# Run container locally
docker run --gpus all -p 8080:8080 \
  -e CONFIG_YAML="$(cat ../config/config.yaml)" \
  ugc-faceswapper:v1

# Test health endpoint
curl http://localhost:8080/health

# Expected response:
# {"status":"healthy","service":"ugc-faceswapper-v1","config_loaded":true}
```

### Step 4: Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Push image
docker push YOUR_DOCKERHUB_USERNAME/ugc-faceswapper:v1
```

## Runpod Deployment

### Step 1: Create Template
1. Log into Runpod.io
2. Go to **Templates** → **New Template**
3. Configure:
   - **Name:** ugc-faceswapper-v1
   - **Image:** YOUR_DOCKERHUB_USERNAME/ugc-faceswapper:v1
   - **Container Disk:** 30 GB
   - **Expose HTTP Ports:** 8080
   - **Environment Variables:**
     - Name: `CONFIG_YAML`
     - Value: (Paste entire contents of config/config.yaml)

### Step 2: Update Make.com with Template ID
1. Copy Template ID from Runpod (format: `tp_xxxxxxxxxxxxxx`)
2. Open Make.com → FaceSwap - Main Pipeline
3. Edit HTTP module (Module 2)
4. Update URL: `https://api.runpod.io/v2/[TEMPLATE_ID]/run`
5. Save scenario

## Testing Complete Pipeline

1. Add test row to Airtable with Status = Pending
2. Wait 5 minutes for Make.com to trigger
3. Check Runpod dashboard for active pod
4. Monitor Airtable for status updates
5. Download output from S3 URL

## Troubleshooting

### Build fails with "CUDA not found"
- Ensure NVIDIA Docker runtime is installed
- Verify GPU is accessible: `docker run --gpus all nvidia/cuda:11.8.0-base nvidia-smi`

### Image too large (>20GB)
- This is expected due to CUDA runtime + model
- Use Docker layer caching for faster rebuilds
- Consider using Runpod's persistent storage for model

### Model loading fails at runtime
- Verify model files are in /models/wan2.2-animate/
- Check file permissions
- Review Flask logs in Runpod console

### S3 upload fails
- Verify AWS credentials in config.yaml
- Check S3 bucket policy allows PutObject
- Test credentials with AWS CLI first

## Model Integration TODO

**CRITICAL:** The current implementation uses placeholder face-swap logic.
To complete the integration:

1. Review Wan2.2-Animate documentation
2. Update `process.py` → `face_swap_segment()` function
3. Add model loading in `app.py` startup
4. Test with sample video/avatar

**Reference:**
- Wan2.2-Animate repository (link TBD)
- InsightFace for face detection
- PyTorch for model inference

## Cost Optimization

- **Image size:** ~18GB (acceptable for GPU workload)
- **Build time:** 30-60 min (one-time cost)
- **Spin-up time:** 45-60 seconds (model pre-loaded)
- **Processing time:** 3-4 min per video

**Tips:**
- Use Runpod spot instances for 50% savings
- Cache Docker layers during development
- Keep template updated to avoid rebuilds
