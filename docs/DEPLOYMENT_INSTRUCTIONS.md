# Complete Deployment Instructions

## Current Status

Local Docker push is failing due to network issues with large layers (67.7GB image).

**Solution:** Use GitHub Actions to build and push from GitHub's servers.

## Step-by-Step Deployment Guide

### Step 1: Push Code to GitHub (5 minutes)

```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030"

# Git repo is already initialized
# Create first commit
git commit -m "Face swapper Runpod deployment - initial commit

Includes:
- Docker configuration with v1 and v2 builds
- Runpod serverless handler
- Test scripts for endpoint validation
- GitHub Actions workflow for reliable Docker push"

# Create GitHub repo (choose one method):

# Method A: Using GitHub Web UI
# 1. Go to https://github.com/new
# 2. Name: faceswapper-deployment
# 3. Visibility: PRIVATE (recommended - contains deployment config)
# 4. Do NOT initialize with README
# 5. Click "Create repository"
# 6. Then run:
git remote add origin https://github.com/YOUR_USERNAME/faceswapper-deployment.git
git branch -M main
git push -u origin main

# Method B: Using GitHub Desktop
# 1. Open GitHub Desktop
# 2. File > Add Local Repository
# 3. Choose this folder
# 4. Publish Repository (make it private)
```

### Step 2: Configure Docker Hub Secrets (2 minutes)

1. Get your Docker Hub access token:
   - Go to https://hub.docker.com/settings/security
   - Click "New Access Token"
   - Description: "GitHub Actions - Face Swapper"
   - Access permissions: Read, Write, Delete
   - Click "Generate"
   - **COPY THE TOKEN** (you can't see it again!)

2. Add secrets to GitHub:
   - Go to: https://github.com/YOUR_USERNAME/faceswapper-deployment/settings/secrets/actions
   - Click "New repository secret"
   - Add two secrets:
     1. Name: `DOCKER_USERNAME` / Value: `kaspamontana`
     2. Name: `DOCKER_PASSWORD` / Value: `[paste the token from step 1]`

### Step 3: Trigger GitHub Actions Build (1 minute)

GitHub Actions will automatically start when you push, but you can also trigger manually:

1. Go to: https://github.com/YOUR_USERNAME/faceswapper-deployment/actions
2. Click "Build and Push Docker Image" workflow
3. Click "Run workflow" button
4. Select "main" branch
5. Click "Run workflow"

**Build time:** 60-90 minutes on GitHub's servers

Monitor progress at: https://github.com/YOUR_USERNAME/faceswapper-deployment/actions

### Step 4: Update Runpod Endpoint (30 seconds)

Once GitHub Actions completes successfully:

```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/scripts"

# Update endpoint to use v2
./update_endpoint.sh

# Expected output:
# {"id":"eaj61xejeec2iw","imageName":"kaspamontana/ugc-faceswapper:v2",...}
```

### Step 5: Test with Sample Video (5 minutes)

You need two publicly accessible URLs:
1. Source video (MP4, MOV, AVI)
2. Avatar/face image (JPG, PNG)

```bash
cd scripts

# Test the endpoint
./test_endpoint.sh "https://YOUR_VIDEO_URL.mp4" "https://YOUR_AVATAR_URL.jpg"

# This returns a job ID like: {"id":"abc123-xyz-456","status":"IN_QUEUE"}
# Save the job ID!

# Check job status
./check_status.sh "abc123-xyz-456"
```

### Step 6: Monitor Results

**Runpod Processing Time:** 2-5 minutes per video (depending on length)

**Check S3 Bucket:**
- Bucket: `faceswap-outputs-kasparas`
- Output file: `{record_id}_output.mp4`

**Check Make.com Webhook:**
- URL: https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy
- Should receive POST with completion status

### Step 7: Validate Output

1. Download output video from S3
2. Verify face swap quality
3. Check video plays correctly
4. Confirm webhook notification received

## Troubleshooting

### GitHub Actions Fails
- Check secrets are set correctly (DOCKER_USERNAME, DOCKER_PASSWORD)
- Verify v1 image exists: https://hub.docker.com/r/kaspamontana/ugc-faceswapper/tags
- Check Actions logs for specific error

### Runpod Endpoint Update Fails
- Verify API key is valid: `rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk`
- Check endpoint exists in Runpod dashboard
- Ensure budget has funds ($10 remaining)

### Video Processing Fails
- Verify video URL is publicly accessible (try in browser)
- Check avatar image URL is publicly accessible
- Review Runpod logs in dashboard
- Verify S3 permissions for writing

### No Webhook Notification
- Check Make.com scenario is active
- Verify webhook URL in handler.py matches Make.com
- Check Make.com execution history

## Cost Estimates

**GitHub Actions:**
- Free for public repos
- Private repos: ~90 min build = ~1.5 hours of 2000 free minutes/month
- Cost: $0

**Runpod:**
- ~$0.10-0.50 per video (depending on length)
- Budget: $10 remaining
- Capacity: 20-100 videos

**Total first video:** ~$0 (GitHub free tier) + ~$0.25 (Runpod) = **$0.25**

## Success Criteria

- [ ] GitHub Actions build completes successfully
- [ ] Docker image kaspamontana/ugc-faceswapper:v2 visible on Docker Hub
- [ ] Runpod endpoint updated to v2
- [ ] Test video processes successfully
- [ ] Output appears in S3 bucket
- [ ] Webhook notification received
- [ ] Face swap quality is acceptable

## Next Steps After Success

1. Integrate with production workflow
2. Monitor costs and usage
3. Add error handling and retries
4. Set up monitoring/alerting
5. Document API for team

## Quick Reference

**GitHub Repo:** https://github.com/YOUR_USERNAME/faceswapper-deployment
**Docker Hub:** https://hub.docker.com/r/kaspamontana/ugc-faceswapper
**Runpod Dashboard:** https://www.runpod.io/console/serverless
**Endpoint ID:** eaj61xejeec2iw
**S3 Bucket:** faceswap-outputs-kasparas
**Webhook:** https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy
