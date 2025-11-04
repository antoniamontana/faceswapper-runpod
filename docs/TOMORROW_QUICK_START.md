# Tomorrow's Quick Start Guide

## What We Accomplished Today ✅

1. **Airtable Base** - Fully configured with all fields
2. **AWS S3** - Bucket created, IAM user set up, credentials saved
3. **Make.com Scenarios** - Both created (Scenario 1 ON, Scenario 2 OFF)
4. **Config File** - 90% complete, only missing Runpod API key

## Tomorrow's Tasks (10 Minutes)

### Task 1: Runpod Setup
1. Go to: https://www.runpod.io/
2. Sign up with email/Google
3. Profile → Billing → Add $50 credits
4. Profile → Settings → API Keys → Create key
5. Copy API key

### Task 2: Update System
1. Add Runpod API key to `config/config.yaml`
2. Update Make.com Scenario 2 HTTP module:
   - URL: `https://api.runpod.ai/v2/TEMPLATE_ID/run`
   - Authorization header: `Bearer YOUR_API_KEY`
3. Turn Scenario 2 ON

## After Runpod

### Next Big Task: Docker + Wan2.2-Animate Model
This is the CRITICAL blocker for production:
- Need to obtain Wan2.2-Animate model (~15GB)
- Need integration code for face-swapping
- Current `docker/process.py` has placeholder code
- Once model is integrated, build Docker image
- Push to Docker Hub
- Create Runpod template
- Then system is LIVE!

## Quick Reference

**Airtable:** https://airtable.com/appHjohuWApnPJvd3

**Make.com Scenarios:**
- Scenario 1: Webhook Receiver (ON)
- Scenario 2: Main Pipeline (OFF - waiting for Runpod)

**Config File:** `/config/config.yaml`

**Current Credentials:**
- All AWS, Airtable, Make.com credentials saved
- Only missing: Runpod API key

## System Flow (Once Complete)
1. Add row to Airtable with Status = "Pending"
2. Every 5 min, Make.com checks for Pending rows
3. Sends job to Runpod GPU
4. GPU processes video (3-4 min)
5. Uploads to S3
6. Calls webhook to update Airtable
7. Output URL appears in Airtable

---

**Estimated Time to Production:** 10 min (Runpod) + 2-3 hours (Docker/Model)
