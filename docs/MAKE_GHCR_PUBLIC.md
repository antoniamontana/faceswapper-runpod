# Make GitHub Container Registry Image Public

## The Problem

**Error:** `error pulling image: ... unauthorized`

**Cause:** Your Docker image on GitHub Container Registry (ghcr.io) is **PRIVATE** by default. RunPod can't pull it.

---

## Quick Fix (2 minutes)

### Step 1: Go to GitHub Packages

**Direct link:**
https://github.com/users/antoniamontana/packages/container/faceswapper-runpod/settings

**Or navigate manually:**
1. Go to: https://github.com/antoniamontana
2. Click **"Packages"** tab (top of page)
3. Find package: **faceswapper-runpod**
4. Click on it
5. Click **"Package settings"** (right sidebar)

### Step 2: Change Visibility to Public

1. Scroll down to **"Danger Zone"** section
2. Find **"Change package visibility"**
3. Click **"Change visibility"**
4. Select **"Public"**
5. Type the package name to confirm: `faceswapper-runpod`
6. Click **"I understand, change package visibility"**

**Done!** The image is now publicly accessible.

---

## After Making It Public

### Go Back to RunPod:

1. https://www.runpod.io/console/serverless
2. Click endpoint: `eaj61xejeec2iw`
3. Find the stuck workers (in Workers section)
4. **Terminate/Stop all stuck workers**
5. New workers will spawn automatically and pull the image successfully

**Or wait 2-3 minutes** - workers may auto-retry and succeed.

---

## Verify It's Working

**Check worker logs again:**
- Should see: "Pulling image..." → "Starting container..." → "Handler ready"
- No more "unauthorized" errors

**Check job status:**
- Should change from `IN_QUEUE` → `IN_PROGRESS`

---

## Alternative: Use Docker Hub

If you don't want to make it public on GitHub:

1. Push image to Docker Hub (public by default)
2. Update RunPod endpoint to use: `yourusername/faceswapper-runpod:latest`

**But making GHCR public is faster** (2 min vs 15 min).

---

## Why This Happened

GitHub Container Registry makes packages **private by default**. You need to manually change visibility to public for public access.

RunPod can pull from:
- ✅ Public registries (Docker Hub, GHCR)
- ❌ Private registries (without credentials)

**Making it public = simplest solution.**

---

**After changing visibility, workers will start successfully!**
