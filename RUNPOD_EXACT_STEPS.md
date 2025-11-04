# EXACT RUNPOD DEPLOYMENT STEPS (From Official Docs)

## ⚠️ CRITICAL REQUIREMENT

**Runpod serverless REQUIRES your Docker image to be in a registry (Docker Hub, GitHub Container Registry, etc.)**

There is NO "build from GitHub" option for serverless endpoints. You MUST push the image first.

---

## THE REAL PROBLEM WE NEED TO SOLVE

**We have a 67GB Docker image that won't push from your local machine.**

---

## SOLUTION: Use Docker Hub Automated Builds

Docker Hub can build your image on THEIR servers and push automatically.

### Step-by-Step (20 minutes setup, 90 min build):

#### 1. Link GitHub to Docker Hub

1. Go to: https://hub.docker.com/
2. Login with username: `kaspamontana`
3. Click your profile → **Account Settings**
4. Go to **Linked Accounts**
5. Click **Connect** next to GitHub
6. Authorize Docker Hub to access your GitHub

#### 2. Create Automated Build

1. Go to: https://hub.docker.com/repositories
2. Click **Create Repository**
3. Name: `ugc-faceswapper`
4. Visibility: **Public** (or Private if you have Pro)
5. Click **Create**

6. Go to **Builds** tab
7. Click **Configure Automated Builds**
8. Select: `antoniamontana/faceswapper-runpod`
9. Configure:
   - **Source:** `main` branch
   - **Dockerfile location:** `/docker/Dockerfile.runpod-optimized`
   - **Build context:** `/docker`
   - **Tag:** `v2`

10. Click **Save and Build**

**Docker Hub will:**
- Clone your GitHub repo
- Build on their servers (no disk limits!)
- Push to `kaspamontana/ugc-faceswapper:v2`
- Take 60-90 minutes

#### 3. Monitor Build

Go to: https://hub.docker.com/r/kaspamontana/ugc-faceswapper/builds

Watch for:
- ✅ "Success" = Image ready
- ❌ "Failed" = Check logs, fix Dockerfile

---

## ONCE IMAGE IS ON DOCKER HUB

### Step 4: Create Runpod Endpoint

1. **Login to Runpod**
   - Go to: https://www.runpod.io/console/serverless
   - Login with your account

2. **Create New Endpoint**
   - Click **"Serverless"** in sidebar
   - Click **"+ New Endpoint"**

3. **Configure Endpoint**

   **Container Image:**
   ```
   kaspamontana/ugc-faceswapper:v2
   ```

   **GPU Configuration:**
   - Select: `NVIDIA RTX A4000` or `A5000` (good balance of power/cost)
   - VRAM needed: 16GB+ for Wan2.2 model

   **Compute:**
   - Active Workers: `0` (pay-per-use)
   - Max Workers: `3`
   - GPUs per Worker: `1`
   - Idle Timeout: `5` seconds

   **Advanced Settings:**
   - Container Disk: `50 GB` (for model + temp files)
   - Environment Variables:
     ```
     MODEL_PATH=/models/Wan2.2-Animate-14B
     CUDA_VISIBLE_DEVICES=0
     AWS_ACCESS_KEY_ID=<your-key>
     AWS_SECRET_ACCESS_KEY=<your-secret>
     AWS_REGION=us-east-1
     S3_BUCKET=faceswap-outputs-kasparas
     WEBHOOK_URL=https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy
     ```

4. **Click "Deploy"**

   Runpod will:
   - Pull your Docker image
   - Start a worker
   - Run health checks
   - Show endpoint ID (you already have: `eaj61xejeec2iw`)

---

## Step 5: Test Your Endpoint

Use the Runpod API:

```bash
curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/run" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "record_id": "test001",
      "source_video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
      "avatar_image_url": "https://randomuser.me/api/portraits/men/32.jpg",
      "webhook_url": "https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy"
    }
  }'
```

This returns a job ID. Check status:

```bash
curl "https://api.runpod.ai/v2/eaj61xejeec2iw/status/JOB_ID" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk"
```

---

## Step 6: Verify Results

1. **Check S3 Bucket:** `faceswap-outputs-kasparas`
   - Should see: `test001_output.mp4`

2. **Check Webhook:** Make.com scenario
   - Should receive completion notification

3. **Download and watch output video**

---

## ALTERNATIVE: Skip Docker Hub Entirely

### Use GitHub Container Registry (ghcr.io)

**Advantages:**
- Free
- Unlimited private repos
- Better integration with GitHub Actions

**Setup:**
1. GitHub Actions can build and push to ghcr.io
2. Use in Runpod: `ghcr.io/antoniamontana/faceswapper-runpod:v2`

**Update `.github/workflows/docker-build-push.yml`:**

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: ./docker
    file: ./docker/Dockerfile.runpod-optimized
    push: true
    tags: ghcr.io/antoniamontana/faceswapper-runpod:v2
```

Then use `ghcr.io/antoniamontana/faceswapper-runpod:v2` in Runpod.

---

## FASTEST PATH TO SUCCESS (My Recommendation)

1. **Fix GitHub Actions to use ghcr.io** (5 min)
2. **Let it build** (20 min, will succeed now with smaller image)
3. **Deploy to Runpod** (5 min)
4. **Test** (5 min)
5. **DONE** in 35 minutes

Do you want me to:
A) Set up Docker Hub automated builds
B) Fix GitHub Actions to push to ghcr.io (GitHub Container Registry)
C) Try something else
