# Deploy Face Swapper to Runpod - START HERE

## Quick Status

Your code is ready to deploy! All files are configured and committed to git.

Local Docker push failed due to network issues with 67.7GB upload.
**Solution: Use GitHub Actions** (reliable, fast GitHub servers)

## Deploy in 3 Steps (15 minutes + 90 min build time)

### Step 1: Push to GitHub (5 min)

```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030"

# Check what's ready
git status
git log --oneline

# Create GitHub repo
# Go to: https://github.com/new
# Name: faceswapper-runpod
# Visibility: PRIVATE (recommended)
# Do NOT initialize with README
# Click "Create repository"

# Push your code
git remote add origin https://github.com/YOUR_USERNAME/faceswapper-runpod.git
git push -u origin main
```

### Step 2: Set Up Docker Hub Secrets (3 min)

**Get Docker Hub Token:**
1. Go to: https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: "GitHub Actions - Face Swapper"
4. Permissions: Read, Write, Delete
5. Generate and **COPY** the token

**Add to GitHub:**
1. Go to: https://github.com/YOUR_USERNAME/faceswapper-runpod/settings/secrets/actions
2. Click "New repository secret"
3. Add these:
   - Name: `DOCKER_USERNAME` / Value: `kaspamontana`
   - Name: `DOCKER_PASSWORD` / Value: `[paste token]`

### Step 3: Trigger Build (1 min)

1. Go to: https://github.com/YOUR_USERNAME/faceswapper-runpod/actions
2. Click "Build and Push Docker Image"
3. Click "Run workflow" > Select "main" > Click "Run workflow"

**Build time:** 60-90 minutes
**Monitor:** https://github.com/YOUR_USERNAME/faceswapper-runpod/actions

## After Build Completes

### Update Runpod (30 sec)
```bash
cd scripts
./update_endpoint.sh
```

### Test (5 min)
```bash
# Need two public URLs: video + avatar image
./test_endpoint.sh "VIDEO_URL" "AVATAR_URL"

# Get job ID, then check status
./check_status.sh "JOB_ID"
```

### Verify Results
- Check S3 bucket: `faceswap-outputs-kasparas`
- Check webhook: https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy

## What's Configured

- Docker build (Wan2.2-Animate-14B model)
- Runpod serverless handler
- S3 upload integration
- Webhook notifications
- Test scripts
- GitHub Actions workflow

## Files to Review

- `docker/Dockerfile` - Full image build
- `docker/handler.py` - Runpod serverless handler
- `.github/workflows/docker-build-push.yml` - GitHub Actions
- `scripts/` - Test and deployment scripts
- `docs/DEPLOYMENT_INSTRUCTIONS.md` - Full guide

## Credentials Needed

**Already configured:**
- Runpod API Key: rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk
- Runpod Endpoint: eaj61xejeec2iw
- S3 Bucket: faceswap-outputs-kasparas
- Webhook: https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy

**You need to provide:**
- Docker Hub username: kaspamontana
- Docker Hub token: (generate in step 2)

## Cost Estimate

- GitHub Actions: FREE (using free tier)
- Runpod: ~$0.25 per video
- Budget remaining: $10

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Docker secrets configured
- [ ] GitHub Actions build running
- [ ] Build completes successfully
- [ ] Image on Docker Hub: kaspamontana/ugc-faceswapper:v2
- [ ] Runpod endpoint updated
- [ ] Test video processed
- [ ] Output in S3
- [ ] Webhook received

## Need Help?

See `docs/DEPLOYMENT_INSTRUCTIONS.md` for detailed troubleshooting.

## Why GitHub Actions?

Your local Docker push kept failing because:
- 67.7GB is too large for home/mobile connections
- Network timeouts on large layers
- Docker Desktop proxy issues

GitHub Actions:
- Fast datacenter network
- Reliable, automatic retries
- Free for this use case
- Easy to monitor and debug

---

**READY TO START?** Follow Step 1 above!
