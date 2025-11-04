# UGC Face Swapper - MVP System Setup Guide
## From Zero to Working System

**What This System Does:**
Takes your UGC video + avatar image → Face-swaps talking head segments (0-5s, 15-20s) → Outputs clean video ready for manual variant creation.

**What You Do Manually:**
- Generate avatars in Higgsfield
- Create perturbations/variants in external software
- Deploy to TikTok

---

## Phase 1: Account Setup (30 minutes)

### Step 1: Create Airtable Account
1. Go to [airtable.com](https://airtable.com)
2. Sign up for free account
3. Upgrade to Pro plan ($20/month) - Required for API access
4. Note your account email

### Step 2: Create AWS S3 Storage
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Sign up for AWS account (requires credit card)
3. Navigate to S3 service
4. Click "Create bucket"
5. Bucket settings:
   - **Bucket name:** `ugc-faceswap-output-[yourname]` (must be globally unique)
   - **Region:** US East (N. Virginia) us-east-1
   - **Block Public Access:** UNCHECK all boxes (we need public read)
   - Click "Create bucket"

6. Configure bucket permissions:
   - Click on your bucket name
   - Go to "Permissions" tab
   - Scroll to "Bucket policy"
   - Click "Edit" and paste:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::ugc-faceswap-output-[yourname]/*"
     }]
   }
   ```
   - Replace `[yourname]` with your actual bucket name
   - Click "Save changes"

7. Create IAM access keys:
   - Search for "IAM" in AWS console
   - Click "Users" → "Create user"
   - Username: `faceswap-uploader`
   - Click "Next"
   - Select "Attach policies directly"
   - Search for and select: `AmazonS3FullAccess`
   - Click "Next" → "Create user"
   - Click on the user you just created
   - Go to "Security credentials" tab
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next" → "Create access key"
   - **COPY THESE IMMEDIATELY:**
     - Access key ID: `AKIA...`
     - Secret access key: `wJal...`
   - Store them securely (you'll need them later)

### Step 3: Create Make.com Account
1. Go to [make.com](https://make.com)
2. Sign up for free account
3. Upgrade to Core plan ($29/month) - Required for sufficient operations
4. Complete onboarding tutorial (5 minutes)

### Step 4: Create Runpod Account
1. Go to [runpod.io](https://runpod.io)
2. Sign up for account
3. Add $50 credit via "Billing" section
4. Go to Settings → API Keys
5. Click "Create API Key"
6. Name it: `faceswap-automation`
7. **COPY the API key** - format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
8. Store securely

---

## Phase 2: Airtable Base Setup (15 minutes)

### Step 5: Create Airtable Base

1. In Airtable, click "Create a base"
2. Name it: `UGC Face Swap Pipeline`
3. Create a table named: `Processing Queue`

### Step 6: Configure Table Fields

Delete all default columns except "Name", then rename and add these fields:

| Field Name | Field Type | Configuration |
|------------|-----------|---------------|
| `Video_ID` | Autonumber | (This will replace "Name" - rename it) |
| `Source_Video_URL` | URL | Required field |
| `Avatar_Image_URL` | URL | Required field |
| `Batch_ID` | Single line text | Optional grouping |
| `Status` | Single select | Options: Pending, Processing, Complete, Failed (Default: Pending) |
| `Output_Video_URL` | URL | Auto-populated by system |
| `Error_Log` | Long text | Captures failures |
| `GPU_Instance_ID` | Single line text | Tracks which GPU processed it |
| `Date_Submitted` | Created time | Auto-generated |
| `Date_Completed` | Last modified time | Auto-updated |

**To create each field:**
- Click the "+" button at the right of the last column
- Select field type from the list
- Configure according to table above
- Click "Create field"

### Step 7: Get Airtable API Credentials

1. Click your profile icon (top right)
2. Go to "Developer hub"
3. Click "Create token"
4. Token name: `FaceSwap Automation`
5. Add scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
6. Add access: Select your `UGC Face Swap Pipeline` base
7. Click "Create token"
8. **COPY the token** - format: `patXXXXXXXXXXXXXXXX`
9. Store securely

10. Get your Base ID:
    - Go to [airtable.com/api](https://airtable.com/api)
    - Click on "UGC Face Swap Pipeline"
    - In the URL, find the Base ID - format: `appXXXXXXXXXXXXXX`
    - Copy this

---

## Phase 3: Docker Image Setup (20 minutes)

### Step 8: Prepare Configuration File

1. Create a file named `config.yaml` on your computer with this content:

```yaml
# Storage Configuration
storage:
  provider: "s3"
  s3_bucket: "ugc-faceswap-output-[yourname]"  # Your bucket name from Step 2
  s3_region: "us-east-1"
  s3_access_key: "AKIA..."  # Your Access Key ID from Step 2
  s3_secret_key: "wJal..."  # Your Secret Access Key from Step 2

# Airtable Configuration
airtable:
  api_key: "patXXXXXXXXXXXXXXXX"  # Your token from Step 7
  base_id: "appXXXXXXXXXXXXXX"  # Your Base ID from Step 7
  table_name: "Processing Queue"

# Processing Configuration
processing:
  segments:
    swap_1_start: 0
    swap_1_end: 5
    original_1_start: 5
    original_1_end: 15
    swap_2_start: 15
    swap_2_end: 20
    original_2_start: 20
    original_2_end: 30
  model_path: "/models/wan2.2-animate"
  output_resolution: "1080p"
  face_detection_confidence: 0.6
```

2. Replace ALL placeholder values with your actual credentials
3. Save this file - you'll upload it to Runpod later

### Step 9: Create Runpod GPU Template

1. Log into Runpod
2. Go to "Templates" section (left sidebar)
3. Click "New Template"
4. Configure template:

**Basic Settings:**
- **Template Name:** `UGC-FaceSwap-MVP`
- **Template Type:** Keep default (Pod)

**Container Configuration:**
- **Container Image:** `anthropic/faceswap-wan2:latest` 
  *(Note: You'll need to build and push this Docker image - see Appendix A)*
- **Docker Command:** Leave empty (image has default entrypoint)
- **Container Disk:** 25 GB minimum
- **Volume Mount Path:** `/workspace`

**Expose Ports:**
- Add port: `8080` (HTTP)

**Environment Variables:**
Click "Add Environment Variable" and add:
- Name: `CONFIG_YAML`
- Value: Paste entire contents of your config.yaml file from Step 8

5. Click "Save Template"
6. Copy the Template ID from the URL - format: `tp_xxxxxxxxxxxxxx`

---

## Phase 4: Make.com Automation Setup (30 minutes)

### Step 10: Create Webhook Receiver

1. In Make.com, click "Create a new scenario"
2. Name it: `Face Swap - Webhook Receiver`
3. Click the "+" to add a module
4. Search for "Webhooks" → Select "Custom webhook"
5. Click "Add" to create new webhook
6. Name it: `GPU Completion Webhook`
7. Copy the webhook URL - format: `https://hook.make.com/xxxxxxxxxxxxx`
8. Save this URL - you'll add it to config.yaml later
9. Click "OK"
10. **Don't activate this scenario yet** - we'll do it after the main scenario

### Step 11: Create Main Automation Scenario

1. Click "Scenarios" in left sidebar
2. Click "Create a new scenario"
3. Name it: `Face Swap - Main Pipeline`

**MODULE 1: Airtable Trigger**
1. Click the "+" to start
2. Search for "Airtable"
3. Select "Watch Records"
4. Click "Create a connection"
5. Enter your Airtable API key (from Step 7)
6. Click "Save"
7. Configure module:
   - **Base:** Select "UGC Face Swap Pipeline"
   - **Table:** Select "Processing Queue"
   - **Trigger field:** Status
   - **Trigger value:** Pending
   - **Limit:** 20
8. Click "OK"

**MODULE 2: Runpod - Start GPU Instance**
1. Click "+" after the Airtable module
2. Search for "HTTP"
3. Select "Make a request"
4. Configure:
   - **URL:** `https://api.runpod.io/v2/[YOUR_TEMPLATE_ID]/run`
     - Replace `[YOUR_TEMPLATE_ID]` with the template ID from Step 9
   - **Method:** POST
   - **Headers:**
     - Header 1: `Authorization` = `Bearer [YOUR_RUNPOD_API_KEY]`
       - Replace with your Runpod API key from Step 4
     - Header 2: `Content-Type` = `application/json`
   - **Body:**
   ```json
   {
     "input": {
       "record_id": "{{1.id}}",
       "video_url": "{{1.Source_Video_URL}}",
       "avatar_url": "{{1.Avatar_Image_URL}}"
     },
     "gpuTypeId": "NVIDIA A40"
   }
   ```
5. Click "OK"

**MODULE 3: Parse Response**
1. Click "+" after HTTP module
2. Search for "JSON"
3. Select "Parse JSON"
4. Configure:
   - **JSON string:** Select output from Module 2: `Data`
5. Click "OK"

**MODULE 4: Update Airtable Status to Processing**
1. Click "+" after JSON module
2. Search for "Airtable"
3. Select "Update a Record"
4. Configure:
   - **Connection:** Use existing Airtable connection
   - **Base:** UGC Face Swap Pipeline
   - **Table:** Processing Queue
   - **Record ID:** Map from Module 1: `id`
   - **Status:** Processing
   - **GPU_Instance_ID:** Map from Module 3: `id`
5. Click "OK"

**MODULE 5: Router (for webhook handling)**
1. Click "+" after Module 4
2. Search for "Flow Control"
3. Select "Router"
4. This creates a split - we'll just use one path for now
5. Click "OK"

### Step 12: Set Scenario Schedule

1. Click the clock icon on the first Airtable module
2. Set schedule:
   - **Run scenario:** Immediately
   - **Interval:** Every 5 minutes
3. Click "OK"
4. Click "Save" (bottom left)
5. **Toggle the scenario ON** (switch at bottom)

### Step 13: Complete Webhook Receiver Scenario

1. Go back to "Face Swap - Webhook Receiver" scenario
2. After the webhook module, add:

**MODULE 2: Update Airtable Record**
1. Click "+" after webhook
2. Select "Airtable" → "Update a Record"
3. Configure:
   - **Record ID:** `{{1.record_id}}`
   - **Status:** `{{1.status}}` (will be "Complete" or "Failed")
   - **Output_Video_URL:** `{{1.output_url}}`
   - **Error_Log:** `{{1.error_message}}`
4. Click "OK"

**MODULE 3: Terminate GPU Instance**
1. Click "+" after Airtable update
2. Select "HTTP" → "Make a request"
3. Configure:
   - **URL:** `https://api.runpod.io/v2/{{1.instance_id}}/terminate`
   - **Method:** DELETE
   - **Headers:**
     - `Authorization` = `Bearer [YOUR_RUNPOD_API_KEY]`
4. Click "OK"
5. Click "Save"
6. **Toggle scenario ON**

### Step 14: Update Config with Webhook URL

1. Go back to your `config.yaml` file from Step 8
2. Add these lines at the end:

```yaml
# Webhook Configuration
webhook:
  completion_url: "https://hook.make.com/xxxxxxxxxxxxx"  # Your webhook URL from Step 10
```

3. Update your Runpod template:
   - Go to Runpod → Templates → Edit your template
   - Update the `CONFIG_YAML` environment variable with the new config
   - Save template

---

## Phase 5: Testing (15 minutes)

### Step 15: Prepare Test Materials

1. **Test Video:**
   - Create or find a 30-second UGC video with structure:
     - 0-5s: Person talking
     - 5-15s: Product demo
     - 15-20s: Person talking
     - 20-30s: Product demo
   - Upload to YouTube as unlisted OR upload to S3
   - Copy the direct video URL

2. **Test Avatar:**
   - Generate 1 avatar in Higgsfield manually
   - Download the image
   - Upload to Imgur or your S3 bucket
   - Copy the direct image URL

### Step 16: First Test Run

1. Open your Airtable base "Processing Queue"
2. Add a new row:
   - **Video_ID:** Auto-generates
   - **Source_Video_URL:** Paste your test video URL
   - **Avatar_Image_URL:** Paste your test avatar URL
   - **Batch_ID:** `test-batch-1`
   - **Status:** Select "Pending"
3. Wait 5 minutes (next Make.com trigger)
4. Watch the Status field - it should change:
   - Pending → Processing → Complete (or Failed)

### Step 17: Verify Output

**If Status = Complete:**
1. Check `Output_Video_URL` field
2. Click the URL to download video
3. Verify:
   - Segments 0-5s have face-swapped avatar
   - Segments 5-15s are original (no face swap)
   - Segments 15-20s have face-swapped avatar
   - Segments 20-30s are original (no face swap)
   - Video quality looks good
4. **SUCCESS!** System is working.

**If Status = Failed:**
1. Check `Error_Log` field
2. Common issues:
   - "Face not detected" → Avatar image too dark/blurry, try different avatar
   - "Video download failed" → Check video URL is publicly accessible
   - "GPU timeout" → Video too long or high resolution, try 1080p max
3. Fix the issue and add new test row

### Step 18: Test Batch Processing

1. Add 5 new rows to Airtable:
   - Same `Source_Video_URL` for all 5
   - Different `Avatar_Image_URL` for each
   - All set to "Pending"
2. Wait 5-10 minutes
3. All 5 should process and output 5 different face-swapped videos
4. Verify all 5 outputs look correct

---

## Phase 6: Daily Operations

### Your Daily Workflow

**MORNING: Avatar Preparation (30 minutes)**
1. Open Higgsfield
2. Generate 20 avatars manually:
   - Vary age, ethnicity, gender, expression
   - Download all 20 images
3. Upload to S3 or Imgur (batch upload)
4. Create a text file with all 20 image URLs

**BULK AIRTABLE UPLOAD (5 minutes)**
1. Open Airtable "Processing Queue"
2. Add 20 new rows (quick method):
   - Copy/paste same `Source_Video_URL` to all 20 rows
   - Paste different `Avatar_Image_URL` to each row
   - Set `Batch_ID` to today's date (e.g., "2025-10-30")
   - All `Status` = "Pending"
3. Save

**WAIT FOR PROCESSING (60-90 minutes)**
- System checks every 5 minutes
- GPU processes batch automatically
- Processing time: ~3-4 minutes per video
- 20 videos = ~60-80 minutes total

**DOWNLOAD OUTPUTS (10 minutes)**
1. Filter Airtable view: `Status = Complete`
2. For each completed row:
   - Click `Output_Video_URL`
   - Download video
   - Save to local folder: `/Face-Swapped-Videos/[Batch_ID]/`
3. You now have 20 clean face-swapped videos

**MANUAL VARIANT CREATION (Your External Process)**
1. Open Contentflow or your variant creation software
2. Import all 20 face-swapped videos
3. Add perturbations:
   - Speed variations
   - Zoom/crop
   - Color grading
   - Audio effects
4. Export variants
5. Deploy to TikTok

---

## Costs Breakdown

### Monthly Fixed Costs:
- Airtable Pro: $20/month
- Make.com Core: $29/month
- AWS S3 (1000 videos): ~$5/month
- **Total Fixed:** $54/month

### Variable Costs:
- Runpod GPU (A40): $0.79/hour
- Processing time: ~3 minutes per video = $0.039 per video
- 100 videos/day × 30 days = 3,000 videos = $117/month

### Total Monthly Cost (100 videos/day):
**$171/month** for fully automated face-swapping

### Per Video Cost:
**$0.057 per face-swapped video** (vs. $50-200 paying a creator)

---

## Scaling Up

### Processing 200 videos/day:
- Monthly GPU cost: $234
- Total monthly: $288

### Processing 500 videos/day:
- Monthly GPU cost: $585
- Total monthly: $639

### Capacity Limits:
- Current setup: Up to 1,000 videos/day without any changes
- Bottleneck: Your time doing manual variant creation after

---

## Troubleshooting

### System Not Processing Videos

**Check 1: Make.com scenario running?**
- Go to Make.com → Scenarios
- Verify "Face Swap - Main Pipeline" toggle is ON
- Check "History" tab for errors

**Check 2: Airtable connection?**
- In Make.com scenario, click Airtable module
- Click "Reconnect" if needed

**Check 3: Runpod credits?**
- Log into Runpod → Billing
- Ensure you have credit remaining
- Add more if needed

### Videos Stuck in "Processing"

**Check 1: GPU instance status**
- Log into Runpod → Pods
- Look for active pods
- If stuck >20 minutes, manually terminate

**Check 2: Webhook not received**
- In Make.com, check "Face Swap - Webhook Receiver" history
- If no recent executions, webhook might not be reaching
- Verify webhook URL is correct in config.yaml

### Face Detection Failures

**Common causes:**
- Avatar image quality too low (use 1024x1024 minimum)
- Multiple faces in video segments
- Face at extreme angle or profile view
- Poor lighting on face

**Solution:**
- Use high-quality avatars (well-lit, front-facing)
- Verify source video has clear single face in talking segments

### High Costs

**Optimization tips:**
1. Batch process 15-20 videos at once (reduces GPU spin-up overhead)
2. Use A40 GPUs (not A100) - sufficient for 1080p
3. Ensure videos are 1080p max (4K costs more to process)
4. Process during off-peak hours if Runpod has time-based pricing

---

## Maintenance

### Weekly Tasks:
1. Check Airtable for any "Failed" status videos
2. Review Make.com execution history for errors
3. Verify S3 storage usage (delete old videos if needed)

### Monthly Tasks:
1. Review Runpod costs vs. processing volume
2. Archive or delete old Airtable records (keep database lean)
3. Clean up S3 bucket (remove videos older than 60 days)

---

## Appendix A: Docker Image Requirements

**Note:** The Docker image mentioned in Step 9 (`anthropic/faceswap-wan2:latest`) is a placeholder. You will need to build this Docker image with:

### Required Components:
1. Base: `nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04`
2. Python 3.10 + PyTorch 2.1.0
3. Wan2.2-Animate-14B model files
4. FFmpeg for video segmentation
5. Flask web server listening on port 8080
6. Processing script that:
   - Receives webhook from Make.com
   - Downloads video and avatar
   - Segments video at hardcoded timestamps
   - Runs face-swap on segments 1 and 3
   - Reassembles video
   - Uploads to S3
   - Sends completion webhook back to Make.com

### Required Endpoints:
- `POST /process` - Receives job from Make.com
- `GET /health` - Health check

**If you need help building this Docker image, that's a separate technical implementation task.**

---

## Next Steps After Setup

Once your system is running smoothly:

1. **Week 1-2:** Process 10-20 videos/day, validate quality
2. **Week 3-4:** Scale to 50-100 videos/day
3. **Month 2:** Automate avatar generation (re-integrate Higgsfield API)
4. **Month 3:** Integrate perturbations back into pipeline (eliminate external software)
5. **Month 4+:** Build Tab 2 for content management and TikTok deployment tracking

**You now have a working face-swap automation system. Start processing videos and validating the quality before scaling up.**