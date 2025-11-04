# UGC Face Swapper V1 MVP - Setup Guide

**Time to complete:** 90-120 minutes (mostly waiting for account approvals)

---

## Prerequisites Checklist

Before starting, have these ready:
- [ ] Credit card for service signups
- [ ] Email address for account creation
- [ ] Budget: ~$150/month for all services
- [ ] Initial credit: $50 for Runpod

---

## Phase 1: Create Accounts (30 minutes)

### 1.1 Airtable Account
1. Go to [airtable.com](https://airtable.com)
2. Sign up with email
3. **Upgrade to Pro plan** ($20/month) - Required for API access
4. Click your profile → Developer hub
5. Click "Create token"
   - Name: `FaceSwap Automation`
   - Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
6. **SAVE THIS TOKEN** → `patXXXXXXXXXXXXXXXX`

**⚠️ DO NOT SHARE THIS TOKEN**

---

### 1.2 AWS Account + S3 Setup
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Sign up (requires credit card, but free tier available)
3. Navigate to **S3** service
4. Click **Create bucket**:
   - Bucket name: `faceswap-outputs-[yourname]` (must be unique globally)
   - Region: `us-east-1` (US East N. Virginia)
   - **UNCHECK** "Block all public access" ⚠️
   - Confirm: "I acknowledge that the current settings might result in this bucket and the objects within becoming public"
   - Click **Create bucket**

5. Configure bucket policy:
   - Click on your bucket → **Permissions** tab
   - Scroll to **Bucket policy** → Click **Edit**
   - Paste this (replace `YOUR-BUCKET-NAME`):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
     }]
   }
   ```
   - Click **Save changes**

6. Create IAM user for API access:
   - Search **IAM** in AWS console
   - Click **Users** → **Create user**
   - Username: `faceswap-uploader`
   - Click **Next**
   - Select **Attach policies directly**
   - Search and select: `AmazonS3FullAccess`
   - Click **Next** → **Create user**

7. Generate access keys:
   - Click on the user you just created
   - Go to **Security credentials** tab
   - Click **Create access key**
   - Select: **Application running outside AWS**
   - Click **Next** → **Create access key**
   - **SAVE THESE IMMEDIATELY:**
     - Access key ID: `AKIAXXXXXXXXXX`
     - Secret access key: `wJalXXXXXXXXXXXXXXXXXX`

**⚠️ YOU CANNOT SEE THE SECRET KEY AGAIN**

---

### 1.3 Make.com Account
1. Go to [make.com](https://make.com)
2. Sign up with email
3. **Upgrade to Core plan** ($29/month) - Required for sufficient operations
4. Complete the quick tutorial (5 minutes)

---

### 1.4 Runpod Account
1. Go to [runpod.io](https://runpod.io)
2. Sign up with email
3. Go to **Billing** → Add **$50 credit**
4. Go to **Settings** → **API Keys**
5. Click **Create API Key**
   - Name: `faceswap-automation`
6. **SAVE THIS KEY:** `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**⚠️ DO NOT SHARE THIS KEY**

---

## Phase 2: Airtable Base Setup (15 minutes)

### 2.1 Create Base
1. In Airtable, click **Create a base**
2. Name: `UGC Face Swap Pipeline`
3. Click to open the base

### 2.2 Configure Table
1. Rename the default table to: `Processing Queue`
2. Delete all default columns except the first one
3. Rename first column to: `Video_ID`
4. Change type to: **Autonumber**

### 2.3 Add Columns
Click **+** to add each column with exact settings:

| Column Name | Type | Settings |
|-------------|------|----------|
| `Source_Video_URL` | URL | - |
| `Avatar_Image_URL` | URL | - |
| `Batch_ID` | Single line text | - |
| `Status` | Single select | Options: `Pending`, `Processing`, `Complete`, `🚩 Failed` (Default: `Pending`) |
| `Output_Video_URL` | URL | - |
| `Error_Log` | Long text | - |
| `GPU_Instance_ID` | Single line text | - |
| `Date_Submitted` | Created time | - |
| `Date_Completed` | Last modified time | - |

**⚠️ Column names are case-sensitive. Copy exactly as shown.**

### 2.4 Get Base ID
1. Click your profile → **Developer hub**
2. Click **API documentation**
3. Select **UGC Face Swap Pipeline**
4. Look for Base ID in the URL: `app...`
5. **SAVE THIS:** `appXXXXXXXXXXXXXX`

---

## Phase 3: Make.com Automation (45 minutes)

### 3.1 Create Webhook Receiver (First)
1. In Make.com, click **Create a new scenario**
2. Name: `FaceSwap - Webhook Receiver`

**Module 1: Webhooks**
1. Click **+** → Search **Webhooks**
2. Select **Custom webhook**
3. Click **Add** → Name: `GPU Completion`
4. **COPY THIS URL** → `https://hook.make.com/xxxxxxxxxxxxx`
5. Click **OK**

**Module 2: Airtable Update**
1. Click **+** after webhook → Search **Airtable**
2. Select **Update a record**
3. Click **Create a connection**:
   - Paste your Airtable API token from 1.1
   - Click **Save**
4. Configure:
   - Base: `UGC Face Swap Pipeline`
   - Table: `Processing Queue`
   - Record ID: `{{1.record_id}}`
   - Status: `{{1.status}}`
   - Output_Video_URL: `{{1.output_url}}`
   - Error_Log: `{{1.error_message}}`
5. Click **OK**

**Module 3: Runpod Terminate**
1. Click **+** after Airtable → Search **HTTP**
2. Select **Make a request**
3. Configure:
   - URL: `https://api.runpod.io/v2/{{1.instance_id}}/terminate`
   - Method: `DELETE`
   - Headers:
     - Name: `Authorization` | Value: `Bearer [YOUR_RUNPOD_API_KEY]`
       (Replace with your Runpod API key from 1.4)
4. Click **OK**

**Save and activate:**
- Click **Save** (bottom left)
- Toggle **ON** (bottom switch)

---

### 3.2 Create Main Pipeline
1. Click **Scenarios** → **Create a new scenario**
2. Name: `FaceSwap - Main Pipeline`

**Module 1: Airtable Watch**
1. Click **+** → Search **Airtable**
2. Select **Watch Records**
3. Use existing Airtable connection
4. Configure:
   - Base: `UGC Face Swap Pipeline`
   - Table: `Processing Queue`
   - Trigger field: `Status`
   - Trigger value: `Pending`
   - Limit: `1` (one video at a time for V1)
5. Set schedule:
   - Click the clock icon on the module
   - Interval: `Every 5 minutes`
   - Click **OK**
6. Click **OK**

**Module 2: Runpod Start GPU**
1. Click **+** → Search **HTTP**
2. Select **Make a request**
3. Configure:
   - URL: `https://api.runpod.io/v2/run`
     (We'll update this with template ID later)
   - Method: `POST`
   - Headers:
     - Name: `Authorization` | Value: `Bearer [YOUR_RUNPOD_API_KEY]`
     - Name: `Content-Type` | Value: `application/json`
   - Request content:
     - Type: Select **Raw**
     - Content type: `JSON (application/json)`
     - Request content:
     ```json
     {
       "input": {
         "record_id": "{{1.id}}",
         "video_url": "{{1.Source_Video_URL}}",
         "avatar_url": "{{1.Avatar_Image_URL}}",
         "webhook_url": "YOUR_WEBHOOK_URL_FROM_STEP_3.1"
       }
     }
     ```
     (Replace `YOUR_WEBHOOK_URL_FROM_STEP_3.1` with the webhook URL from step 3.1)
4. Click **OK**

**Module 3: Parse JSON**
1. Click **+** → Search **JSON**
2. Select **Parse JSON**
3. Configure:
   - JSON string: Select from Module 2 dropdown → `Data`
4. Click **OK**

**Module 4: Update Airtable to Processing**
1. Click **+** → Search **Airtable**
2. Select **Update a record**
3. Configure:
   - Base: `UGC Face Swap Pipeline`
   - Table: `Processing Queue`
   - Record ID: Map from Module 1 → `id`
   - Status: Type manually → `Processing`
   - GPU_Instance_ID: Map from Module 3 → `id`
4. Click **OK**

**Save and activate:**
- Click **Save**
- Toggle **ON**

**⚠️ IMPORTANT:** Save the webhook URL from step 3.1. You'll need it for config.yaml.

---

## Phase 4: Configuration File (5 minutes)

### 4.1 Create config.yaml
I've already created a template at `config/config.yaml.template` in your project directory.

**Fill in these values:**
1. Open `config/config.yaml.template`
2. Replace all `YOUR_XXX` placeholders with your actual credentials:
   - `YOUR_BUCKET_NAME` → Your S3 bucket name from 1.2
   - `YOUR_S3_ACCESS_KEY` → Access key ID from 1.2
   - `YOUR_S3_SECRET_KEY` → Secret access key from 1.2
   - `YOUR_AIRTABLE_TOKEN` → API token from 1.1
   - `YOUR_BASE_ID` → Base ID from 2.4
   - `YOUR_WEBHOOK_URL` → Webhook URL from 3.1
3. Save as `config/config.yaml` (remove `.template`)

**⚠️ NEVER commit config.yaml to Git. It contains secrets.**

---

## Phase 5: Docker Image (Handled Separately)

The Docker image with Wan2.2-Animate model will be built separately. This requires:
- Downloading the 15GB model
- Building and pushing to Docker Hub
- Creating Runpod template

**This will be done in a separate setup phase.**

---

## Phase 6: Test Run (After Docker is ready)

### 6.1 Prepare Test Materials
1. **Test video (30 seconds):**
   - Record or find a video with structure:
     - 0-5s: Person talking
     - 5-15s: Product demo
     - 15-20s: Person talking
     - 20-30s: Product demo
   - Upload to YouTube (unlisted) OR upload to your S3 bucket
   - Copy direct video URL

2. **Test avatar:**
   - Generate 1 avatar in Higgsfield or Midjourney
   - Requirements: 1024x1024+, front-facing, well-lit, single face
   - Upload to S3 or Imgur
   - Copy direct image URL

### 6.2 Run First Test
1. Open Airtable → `Processing Queue` table
2. Add new row:
   - Source_Video_URL: Paste video URL
   - Avatar_Image_URL: Paste avatar URL
   - Batch_ID: `test-batch-1`
   - Status: Select `Pending`
3. Wait 5 minutes (Make.com check interval)
4. Watch Status change: `Pending` → `Processing` → `Complete`
5. Click `Output_Video_URL` to download
6. Verify:
   - Segments 0-5s and 15-20s have face-swapped avatar
   - Segments 5-15s and 20-30s are original
   - Quality looks good

**If Status = 🚩 Failed:**
- Check `Error_Log` for details
- Common issues:
  - "Face not detected" → Avatar image quality too low
  - "Video download failed" → URL not publicly accessible
  - "Processing timeout" → Video too large/high resolution

---

## Credentials Summary

Keep this information secure. You'll need it throughout the project:

```
# Airtable
API Token: patXXXXXXXXXXXXXXXX
Base ID: appXXXXXXXXXXXXXX
Table Name: Processing Queue

# AWS S3
Bucket Name: faceswap-outputs-[yourname]
Region: us-east-1
Access Key ID: AKIAXXXXXXXXXX
Secret Access Key: wJalXXXXXXXXXXXXXXXXXX

# Make.com
Webhook URL: https://hook.make.com/xxxxxxxxxxxxx
(No API keys needed, using UI automation)

# Runpod
API Key: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Template ID: (Will be provided after Docker build)
```

**⚠️ Store these in a password manager, NOT in the repository.**

---

## Troubleshooting

### "Airtable connection failed in Make.com"
- Regenerate Airtable API token
- Ensure scopes include `data.records:read` and `data.records:write`
- Reconnect in Make.com

### "S3 upload returns 403 Forbidden"
- Check bucket policy allows public `GetObject`
- Verify IAM user has `AmazonS3FullAccess`
- Test S3 credentials with AWS CLI

### "Runpod GPU not starting"
- Check Runpod credit balance
- Verify API key is correct
- Try different GPU type (A40 → A30)

### "Make.com scenario not running"
- Verify scenario is toggled ON
- Check execution history for errors
- Ensure Airtable has records with Status = Pending

---

## Next Steps

After completing this setup:
1. Wait for Docker image to be built
2. Update Runpod template ID in Make.com Module 2
3. Run first test video
4. Process 5-10 test videos to validate
5. Scale to production (20+ videos/batch)

**Setup complete! You're ready for Phase 2: Docker Development.**
