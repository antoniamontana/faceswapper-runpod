# UGC Face Swapper V1 MVP - Requirements Specification

## 1. Problem Statement

**Business Problem:**
Creating UGC (User Generated Content) videos at scale is expensive and time-consuming. Hiring 20 different creators costs $1,000-4,000 per batch and takes days. Brands need a way to test different faces/demographics quickly and cheaply.

**Solution:**
Automated face-swapping system that takes 1 source video + 20 avatars → outputs 20 unique videos with different faces. Process runs automatically via Airtable → Make.com → GPU → Cloud Storage pipeline.

**V1 MVP Scope:**
- Core face-swapping automation only
- Manual avatar generation (no Higgsfield API integration)
- Manual variant creation (no anti-detection perturbations)
- Single processing queue table (no content management dashboard)
- One video per GPU instance (no batch optimization)

**Out of Scope (V2):**
- Automatic avatar generation via Higgsfield API
- Anti-detection perturbations (zoom, crop, speed, audio, metadata)
- Content management dashboard (Tab 2)
- TikTok account management
- Avatar reuse tracking
- Performance metrics

---

## 2. User Persona & Workflow

**User Profile:**
- Non-technical / mediocre developer
- Wants "vibe code" simplicity - minimal interaction with code
- Prefers Airtable spreadsheet interface over custom UI
- Budget-conscious (wants to minimize GPU costs)
- Processing volume: 50-100 videos/day

**Daily Workflow:**
1. **Morning (30 min):** Manually generate 20 avatars in Higgsfield.ai, upload to S3/Imgur, copy URLs
2. **Upload (5 min):** Add 20 rows to Airtable with video URL + avatar URLs, set Status = "Pending"
3. **Processing (60-90 min):** System auto-processes, updates Status to "Complete"
4. **Download (10 min):** Download completed videos from Output_Video_URL
5. **Variants (external):** Create perturbations manually in Contentflow or similar software
6. **Deploy (external):** Upload to TikTok manually

---

## 3. System Architecture

### Component Stack:
```
User Interaction Layer:    Airtable (Processing Queue table)
                                    ↓
Automation Layer:           Make.com (2 scenarios - watch & webhook)
                                    ↓
Processing Layer:           Runpod GPU (Docker with Wan2.2-Animate)
                                    ↓
Storage Layer:              AWS S3 (public bucket for outputs)
```

### Data Flow:
```
1. User adds row to Airtable → Status: Pending
2. Make.com watches (every 5 min) → detects Pending
3. Make.com calls Runpod API → spins up GPU
4. GPU downloads video + avatar
5. GPU segments video → face-swaps segments 1 & 3 → stitches
6. GPU uploads to S3 → calls webhook
7. Webhook updates Airtable → Status: Complete, Output_Video_URL populated
8. Webhook terminates GPU instance
```

---

## 4. Functional Requirements

### FR-1: Airtable Database
**Must have:**
- Base name: "UGC Face Swap Pipeline"
- Table name: "Processing Queue"
- Fields (exact names, case-sensitive):
  - `Video_ID` (Autonumber, primary key)
  - `Source_Video_URL` (URL, required)
  - `Avatar_Image_URL` (URL, required)
  - `Batch_ID` (Single line text, optional)
  - `Status` (Single select: Pending, Processing, Complete, 🚩 Failed)
  - `Output_Video_URL` (URL, auto-populated)
  - `Error_Log` (Long text, auto-populated on failure)
  - `GPU_Instance_ID` (Single line text, auto-populated)
  - `Date_Submitted` (Created time, auto)
  - `Date_Completed` (Last modified time, auto)

**Acceptance Criteria:**
- User can add rows manually via Airtable UI
- Status defaults to "Pending" on new row creation
- Failed status shows red flag emoji 🚩 for easy visual scanning
- All auto-fields remain empty until processing starts

### FR-2: Video Processing Logic
**Must have:**
- **Hardcoded segment timestamps:**
  - Segment 1 (0-5s): Face-swap with avatar
  - Segment 2 (5-15s): Keep original (product demo)
  - Segment 3 (15-20s): Face-swap with avatar
  - Segment 4 (20-30s): Keep original (product demo)
- **Model:** Wan2.2-Animate-14B (pre-installed in Docker image)
- **Resolution:** Output 1080p (downscale if source is 4K+)
- **Face detection confidence:** 0.6 threshold
- **Failure handling:** If face not detected → immediate failure (no retries)

**Acceptance Criteria:**
- Face-swapped segments look natural (no visible artifacts)
- Original segments remain untouched
- Video quality preserved (no noticeable degradation)
- Processing time: 3-4 minutes per video on A40 GPU
- GPU auto-terminates after completion

### FR-3: Make.com Automation
**Must have:**

**Scenario 1: Main Pipeline**
- Trigger: Watch Airtable "Processing Queue" table (every 5 minutes)
- Filter: Status = "Pending"
- Action 1: Call Runpod API to start GPU instance
- Action 2: Update Airtable Status → "Processing"
- Action 3: Store GPU instance ID in Airtable

**Scenario 2: Webhook Receiver**
- Trigger: Webhook from GPU (custom URL)
- Action 1: Update Airtable record with results (Status, Output_Video_URL, Error_Log)
- Action 2: Call Runpod API to terminate GPU instance

**Acceptance Criteria:**
- Scenarios run automatically without manual intervention
- Processing starts within 5 minutes of setting Status = "Pending"
- Failed videos update Airtable with error details
- GPU instances never left running after completion

### FR-4: GPU Docker Container
**Must have:**
- **Base image:** nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
- **Pre-installed:** Wan2.2-Animate-14B model (~15GB, baked into image)
- **Python 3.10** + PyTorch 2.1.0
- **FFmpeg** for video segmentation/stitching
- **Flask web server** on port 8080
- **Endpoints:**
  - `POST /process` - Receives job data (record_id, video_url, avatar_url)
  - `GET /health` - Health check

**Processing script must:**
1. Receive webhook from Make.com with job data
2. Download video from Source_Video_URL
3. Download avatar from Avatar_Image_URL
4. Segment video using FFmpeg
5. Run face-swap on segments 1 & 3 using Wan2.2-Animate
6. Keep segments 2 & 4 unchanged
7. Stitch segments back together
8. Upload final video to S3
9. Call Make.com webhook with results
10. Exit (container terminates)

**Acceptance Criteria:**
- Container spins up in <60 seconds
- Processing completes in 3-4 minutes per video
- Uploads work reliably to S3
- Webhook callback includes all required data

### FR-5: Configuration Management
**Must have:**
- Single `config.yaml` file with:
  - S3 credentials (bucket, region, access keys)
  - Airtable credentials (API token, base ID, table name)
  - Processing settings (segment timestamps, model path, resolution)
  - Webhook URL for completion callback
- Passed to Runpod via environment variable `CONFIG_YAML`

**Acceptance Criteria:**
- User only edits config.yaml once during setup
- No hardcoded credentials in code
- Clear comments for each config section

### FR-6: Error Handling
**Must have:**
- **Face detection failure:** Set Status = "🚩 Failed", Error_Log = "Face not detected in avatar or video segments"
- **Video download failure:** Set Status = "🚩 Failed", Error_Log = "Unable to download video from URL"
- **GPU timeout (>15 min):** Set Status = "🚩 Failed", Error_Log = "Processing timeout - video may be too large"
- **S3 upload failure:** Set Status = "🚩 Failed", Error_Log = "Unable to upload to S3"

**Acceptance Criteria:**
- All failures update Airtable immediately
- Error messages are clear and actionable
- GPU terminates even on failure (no resource leaks)
- No automatic retries (user fixes and resubmits)

---

## 5. Technical Requirements

### TR-1: Development Tools
**Required:**
- Airtable MCP integration (https://github.com/rashidazarang/airtable-mcp)
- Claude Code for development assistance
- Direct GPU testing (no local dev environment)

### TR-2: File Structure
```
/
├── config/
│   └── config.yaml                 # Service credentials
├── docker/
│   ├── Dockerfile                  # GPU container definition
│   ├── requirements.txt            # Python dependencies
│   ├── app.py                      # Flask web server
│   ├── process.py                  # Main processing logic
│   └── models/                     # Wan2.2-Animate model files (15GB)
├── docs/
│   ├── setup-guide.md              # Initial setup instructions
│   ├── daily-operations.md         # User workflow guide
│   └── troubleshooting.md          # Common issues
└── scripts/
    ├── test-run.sh                 # Test helper
    └── validate-config.sh          # Config validation
```

### TR-3: Dependencies
**Docker image:**
- nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
- Python 3.10
- PyTorch 2.1.0 (CUDA 11.8)
- FFmpeg
- Flask
- boto3 (S3)
- requests (webhooks)
- Wan2.2-Animate-14B model

**External services:**
- Airtable Pro account ($20/month)
- Make.com Core plan ($29/month)
- AWS S3 (pay-per-use, ~$5/month for 1000 videos)
- Runpod (pay-per-use GPU, ~$0.039/video)

### TR-4: API Integrations

**Higgsfield API (NOT in V1, but for reference):**
- Docs: https://docs.higgsfield.ai/api-reference/character/create-character
- V2 will use this for automatic avatar generation

**Runpod API:**
- POST `/v2/{template_id}/run` - Start GPU instance
- DELETE `/v2/{instance_id}/terminate` - Stop GPU instance
- Headers: `Authorization: Bearer {api_key}`

**Airtable API (via MCP):**
- Used by Claude Code for setup and testing
- Make.com uses native Airtable integration (not raw API)

---

## 6. Implementation Hints

### IH-1: Docker Image Build
**Pattern to follow:**
```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip ffmpeg git

# Install Python packages
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

# Download and install Wan2.2-Animate model
# (Add download script here - model should be baked in)
COPY models/ /models/

# Copy application code
COPY app.py process.py /app/

# Expose port
EXPOSE 8080

# Set entrypoint
CMD ["python3", "/app/app.py"]
```

### IH-2: Face-Swap Processing Script
**Pattern to follow:**
```python
# process.py
import ffmpeg
import torch
from wan2 import Wan2Animate

def process_video(video_path, avatar_path, config):
    # 1. Segment video
    segments = segment_video(video_path, config['segments'])

    # 2. Load model (already in memory)
    model = load_model(config['model_path'])

    # 3. Face-swap segments 1 and 3
    seg1_swapped = model.swap_face(segments[0], avatar_path)
    seg3_swapped = model.swap_face(segments[2], avatar_path)

    # 4. Reassemble
    final_video = stitch_segments([
        seg1_swapped,
        segments[1],  # Original
        seg3_swapped,
        segments[3]   # Original
    ])

    return final_video
```

### IH-3: Make.com Scenario Configuration
**Use JSON body format for Runpod API call:**
```json
{
  "input": {
    "record_id": "{{airtable_module.id}}",
    "video_url": "{{airtable_module.Source_Video_URL}}",
    "avatar_url": "{{airtable_module.Avatar_Image_URL}}"
  },
  "gpuTypeId": "NVIDIA A40"
}
```

### IH-4: S3 Upload Pattern
**Use boto3 with public-read ACL:**
```python
import boto3

s3 = boto3.client('s3',
    aws_access_key_id=config['s3_access_key'],
    aws_secret_access_key=config['s3_secret_key']
)

s3.upload_file(
    local_path,
    config['s3_bucket'],
    f"outputs/{record_id}.mp4",
    ExtraArgs={'ACL': 'public-read'}
)

url = f"https://{config['s3_bucket']}.s3.amazonaws.com/outputs/{record_id}.mp4"
```

---

## 7. Acceptance Criteria

### AC-1: End-to-End Happy Path
**Given:** User has valid Airtable, S3, Make.com, and Runpod accounts set up
**When:** User adds a row with Source_Video_URL and Avatar_Image_URL, sets Status = "Pending"
**Then:**
- Within 5 minutes, Status changes to "Processing"
- Within 3-5 minutes, Status changes to "Complete"
- Output_Video_URL contains a valid S3 link
- Downloaded video shows face-swapped segments at 0-5s and 15-20s
- Product demo segments at 5-15s and 20-30s are unchanged
- Video quality is 1080p, no visible degradation

### AC-2: Error Handling Path
**Given:** User provides an avatar image with no detectable face
**When:** GPU attempts processing
**Then:**
- Status changes to "🚩 Failed" immediately (no retries)
- Error_Log shows: "Face not detected in avatar image"
- GPU instance terminates within 60 seconds
- User can see red flag emoji in Airtable for quick scanning

### AC-3: Cost Efficiency
**Given:** User processes 100 videos in one day
**When:** All processing completes
**Then:**
- Total GPU cost < $5 (avg $0.039 per video)
- No GPU instances left running after completion
- S3 storage cost negligible (<$0.10)

### AC-4: User Simplicity
**Given:** User is a "mediocre developer" who wants minimal code interaction
**When:** Following setup guide
**Then:**
- Setup completes in <2 hours (mostly waiting for account approvals)
- Only 1 file to edit: config.yaml
- All testing done via Airtable UI (no command line required)
- Airtable MCP enables Claude Code to assist with debugging

---

## 8. Assumptions

### Assumption 1: Video Format
**Assumption:** All source videos are exactly 30 seconds long, 1080p or lower, MP4 format
**Impact if wrong:** Videos longer than 30s will have segments cut off. 4K videos will be downscaled (longer processing time).
**Mitigation:** Document video requirements clearly in setup guide

### Assumption 2: Avatar Quality
**Assumption:** User provides high-quality avatars (1024x1024+, front-facing, well-lit, single face)
**Impact if wrong:** Face detection will fail, video marked as Failed
**Mitigation:** Provide avatar generation guidelines in docs

### Assumption 3: S3 Bucket Permissions
**Assumption:** User sets S3 bucket to public-read for objects
**Impact if wrong:** Output video URLs will return 403 Forbidden
**Mitigation:** Include exact S3 bucket policy in setup guide

### Assumption 4: Make.com Execution Limits
**Assumption:** Make.com Core plan allows sufficient operations (1,000/month = ~30 videos/day)
**Impact if wrong:** Automation stops working mid-month
**Mitigation:** User needs Pro plan ($39/month) if processing >50 videos/day

### Assumption 5: GPU Availability
**Assumption:** Runpod A40 GPUs are available on-demand
**Impact if wrong:** Processing delays or failures
**Mitigation:** User can configure fallback GPU types (A30, RTX 3090) in config.yaml

---

## 9. Success Metrics

### Metric 1: Time to First Successful Video
**Target:** <2 hours from starting setup to first completed video
**Measurement:** Track user feedback during onboarding

### Metric 2: Processing Success Rate
**Target:** >95% of videos complete successfully
**Measurement:** Count Complete vs. Failed in Airtable

### Metric 3: Cost Per Video
**Target:** <$0.05 per video (GPU + S3)
**Measurement:** Monthly Runpod bill ÷ total videos processed

### Metric 4: User Intervention Required
**Target:** <5% of videos require manual troubleshooting
**Measurement:** Count Failed videos with Error_Log entries

---

## 10. Next Steps (Post-Requirements)

### Phase 1: Infrastructure Setup (Week 1)
1. Set up Airtable base via MCP
2. Configure AWS S3 bucket
3. Create Make.com scenarios
4. Generate Runpod API keys

### Phase 2: Docker Development (Week 2)
1. Build base Docker image
2. Download and integrate Wan2.2-Animate model
3. Implement processing script
4. Test segmentation and face-swap locally

### Phase 3: Integration Testing (Week 3)
1. Deploy Docker image to Runpod
2. Test end-to-end with 5 sample videos
3. Validate webhook callbacks
4. Verify S3 uploads

### Phase 4: Documentation & Launch (Week 4)
1. Write setup guide
2. Create troubleshooting docs
3. Test with user following guide
4. Launch V1 MVP

### Phase 5: V2 Planning (Month 2)
1. Add Higgsfield API integration
2. Implement anti-detection perturbations
3. Build content management dashboard
4. Optimize batch processing

---

## 11. Open Questions (To Resolve Before Implementation)

**Q1:** Where to download Wan2.2-Animate-14B model?
**Status:** Need model download link or access credentials

**Q2:** What face-swap quality settings to use?
**Status:** Need to test different quality vs. speed trade-offs

**Q3:** Should S3 bucket use CloudFront CDN?
**Status:** Depends on bandwidth costs after launch

**Q4:** What video codecs to support beyond MP4?
**Status:** Test MOV, AVI compatibility

---

## 12. Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Wan2.2 model unavailable | High | Low | Use InsightFace fallback |
| GPU costs exceed budget | Medium | Medium | Monitor per-video costs daily |
| Face detection failure rate high | High | Medium | Improve avatar quality guidelines |
| Runpod GPU unavailable | Medium | Low | Add fallback GPU providers |
| User can't complete setup | High | Medium | Detailed setup guide + MCP assistance |

---

**Requirements gathering complete. Ready to proceed with implementation.**
