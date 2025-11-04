# Context Findings

## Project Overview
This is a **greenfield V1 MVP** for a UGC face swapper automation system. The full V2 system exists as a specification, but we're building a simplified V1 from scratch.

## Technology Stack (V1 MVP)

### Core Services
1. **Airtable** - Database and UI (Processing Queue table)
2. **Make.com** - Automation orchestration (scenario-based workflows)
3. **Runpod** - GPU compute (A40 instances for face-swapping)
4. **AWS S3** - Video storage (public bucket for outputs)
5. **Higgsfield.ai** - Avatar generation (manual, NOT API integrated in V1)

### Processing Technology
- **Face-swap model:** Wan2.2-Animate-14B (state-of-the-art)
- **Video processing:** FFmpeg for segmentation/reassembly
- **Runtime:** Docker container on Runpod GPU
- **API:** Flask server with /process and /health endpoints

## V1 MVP Scope (What We're Building)

### IN SCOPE:
✅ Airtable "Processing Queue" table with fields:
   - Video_ID, Source_Video_URL, Avatar_Image_URL, Batch_ID
   - Status, Output_Video_URL, Error_Log, GPU_Instance_ID
   - Date_Submitted, Date_Completed

✅ Make.com automation with 2 scenarios:
   - Main Pipeline: Airtable watch → Runpod GPU spin-up → Status updates
   - Webhook Receiver: GPU completion → Airtable update → GPU termination

✅ Docker image with:
   - Wan2.2-Animate-14B model
   - Video segmentation at hardcoded timestamps (0-5s, 5-15s, 15-20s, 20-30s)
   - Face-swap on segments 1 and 3 only
   - S3 upload capability
   - Webhook callback to Make.com

✅ Configuration via config.yaml:
   - S3 credentials
   - Airtable API credentials
   - Processing segment timestamps (hardcoded)
   - Webhook URL for completion

### OUT OF SCOPE (V2 features):
❌ Higgsfield API automatic avatar generation
❌ Anti-detection perturbations (zoom, crop, speed, audio, metadata)
❌ Tab 2 "Content Management" dashboard
❌ TikTok account management
❌ Avatar reuse tracking
❌ Performance metrics tracking
❌ Variation presets (Light/Medium/Heavy)

## Workflow (V1)

### User Journey:
1. **Manual avatar generation:**
   - Generate avatars in Higgsfield.ai manually
   - Download images
   - Upload to S3 or Imgur
   - Copy image URLs

2. **Airtable upload:**
   - Add row to "Processing Queue"
   - Paste Source_Video_URL
   - Paste Avatar_Image_URL
   - Set Status = "Pending"

3. **Automated processing:**
   - Make.com checks every 5 minutes for pending videos
   - Spins up Runpod GPU instance
   - GPU downloads video + avatar
   - Segments video, face-swaps segments 1 & 3
   - Uploads to S3
   - Updates Airtable with Output_Video_URL
   - Terminates GPU

4. **Manual variant creation:**
   - User downloads face-swapped video
   - Creates perturbations/variants in external software (Contentflow, etc.)
   - Deploys to TikTok manually

## Technical Implementation Needs

### 1. Airtable Setup
- Create base with exact schema from MVP SOP
- Generate API token with data.records:read and data.records:write
- Obtain Base ID

### 2. AWS S3 Setup
- Create public bucket with GetObject policy
- Create IAM user with S3FullAccess
- Generate access keys

### 3. Docker Image
- Base: nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
- Python 3.10 + PyTorch 2.1.0
- Wan2.2-Animate-14B model files
- Flask web server on port 8080
- Processing script with S3 and Airtable integration

### 4. Make.com Scenarios
- Main Pipeline: 5-minute polling schedule
- Webhook Receiver: Triggered by GPU completion
- HTTP modules for Runpod API interaction
- JSON parsing for responses

### 5. Configuration Management
- config.yaml with environment-specific credentials
- Passed via Runpod template environment variable
- Includes webhook URL for completion callbacks

## API Documentation References

### Higgsfield API (Not used in V1, but for context):
- POST /character/create - Generate avatar
- GET /character/{id} - Poll for completion
- Response includes thumbnail_url for avatar

### Runpod API:
- POST /v2/{template_id}/run - Start GPU instance
- DELETE /v2/{instance_id}/terminate - Stop GPU instance

### Airtable API:
- Watch Records (via Make.com integration)
- Update Record (via Make.com integration)

## Cost Structure (V1)

### Fixed Monthly:
- Airtable Pro: $20
- Make.com Core: $29
- AWS S3: ~$5 (for 1000 videos)
- **Total:** $54/month

### Variable:
- Runpod GPU A40: $0.79/hour
- Processing time: ~3 min/video = $0.039/video
- 100 videos/day × 30 days = $117/month

### Total (100 videos/day): $171/month
### Per video cost: $0.057

## Key Constraints

1. **Video format:** Must be exactly 30 seconds with specific structure
2. **Avatar requirements:** Single face, well-lit, front-facing, 1024x1024 minimum
3. **Segment timestamps:** Hardcoded (0-5s, 5-15s, 15-20s, 20-30s)
4. **No perturbations:** User must create variants manually in external software
5. **Manual avatar generation:** No API integration in V1
6. **Single table:** Only "Processing Queue" (no content management)

## Files to Create

### Configuration:
- `/config/config.yaml` - Service credentials and processing settings

### Documentation:
- `/docs/setup-guide.md` - User setup instructions
- `/docs/daily-operations.md` - Workflow guide

### Docker:
- `/docker/Dockerfile` - GPU processing container
- `/docker/requirements.txt` - Python dependencies
- `/docker/process.py` - Main processing script
- `/docker/app.py` - Flask web server

### Scripts:
- `/scripts/test-run.sh` - Testing helper
- `/scripts/validate-config.sh` - Config validation

## Integration with Airtable MCP

Per user request, we'll use the Airtable Claude Code MCP:
- GitHub: https://github.com/rashidazarang/airtable-mcp
- Enables direct Airtable manipulation from Claude Code
- Simplifies setup and testing workflow
