# UGC Face Swapper V1 MVP

Automated face-swapping system for creating multiple UGC video variations from a single source video.

## What This Does

**Input:** 1 video (30 seconds) + 20 avatar images
**Output:** 20 unique videos with different faces
**Time:** 3-4 minutes per video (fully automated)
**Cost:** ~$0.05 per video

## Architecture

```
Airtable (UI) → Make.com (Automation) → Runpod GPU (Processing) → AWS S3 (Storage)
```

## Quick Start

### 1. Setup (90-120 minutes, one-time)
Follow the comprehensive guide in [`docs/01-setup-guide.md`](docs/01-setup-guide.md)

**Required accounts:**
- Airtable Pro ($20/month)
- AWS S3 (pay-per-use)
- Make.com Core ($29/month)
- Runpod ($50 initial credit)

### 2. Daily Operations
See [`docs/02-daily-operations.md`](docs/02-daily-operations.md) for workflow

**Morning:** Generate 20 avatars, upload to Airtable
**Afternoon:** System processes automatically
**Evening:** Download completed videos, create variants

## Project Structure

```
faceswapper-20251030/
├── README.md                          # This file
├── config/
│   └── config.yaml.template           # Configuration template (fill with your credentials)
├── docs/
│   ├── 01-setup-guide.md              # Detailed setup instructions
│   └── 02-daily-operations.md         # Daily workflow guide
├── docker/
│   ├── Dockerfile                     # GPU container definition
│   ├── requirements.txt               # Python dependencies
│   ├── app.py                         # Flask web server
│   ├── process.py                     # Video processing logic
│   ├── utils.py                       # Helper functions
│   └── README.md                      # Docker build instructions
└── requirements/
    └── 2025-10-30-1044-project-overview/   # Requirements gathering artifacts
```

## V1 MVP Scope

### ✅ Included:
- Automated face-swapping on hardcoded segments (0-5s, 15-20s)
- Airtable spreadsheet interface
- Make.com automation workflows
- GPU processing on Runpod
- S3 storage for outputs
- Error handling with visual indicators (🚩 Failed)

### ❌ Not Included (V2 features):
- Automatic avatar generation (Higgsfield API)
- Anti-detection perturbations
- Content management dashboard
- Batch optimization
- TikTok account management

## Key Features

- **No-code operation:** Manage everything via Airtable spreadsheet
- **Fully automated:** Add row → System processes → Download output
- **Cost-effective:** $0.05 per video vs. $50-200 per creator
- **Fast processing:** 3-4 minutes per video on GPU
- **Error resilience:** Clear error messages with 🚩 visual indicators

## Configuration

### Required Credentials (stored in config/config.yaml):
- AWS S3 access keys
- Airtable API token + Base ID
- Make.com webhook URL
- Runpod API key (set in Make.com)

**⚠️ NEVER commit config.yaml to Git**

## Video Requirements

- **Duration:** Exactly 30 seconds
- **Format:** MP4
- **Resolution:** 1080p (max, will downscale from 4K)
- **Structure:**
  - 0-5s: Person talking (face-swapped)
  - 5-15s: Product demo (kept original)
  - 15-20s: Person talking (face-swapped)
  - 20-30s: Product demo (kept original)

## Avatar Requirements

- **Size:** 1024x1024 or higher
- **Format:** PNG or JPG
- **Quality:** High-res, well-lit, front-facing
- **Faces:** Single face only
- **Background:** Plain (recommended)

## Cost Breakdown

### Monthly Fixed Costs:
- Airtable Pro: $20
- Make.com Core: $29
- **Total:** $49/month

### Variable Costs (100 videos/day):
- GPU processing: ~$120/month ($0.039 per video)
- S3 storage: ~$5/month
- **Total variable:** $125/month

### Total Monthly (100 videos/day): $174
### Per video: $0.058

**ROI:** $174/month vs. $3,000+ paying creators = **$2,826 saved**

## Troubleshooting

### Status stuck on "Pending"
- Check Make.com scenario is toggled ON
- Verify Airtable connection in Make.com

### Videos showing "🚩 Failed"
- Check `Error_Log` column for details
- Common issues:
  - Face not detected → Improve avatar quality
  - Video download failed → Check URL is public
  - Processing timeout → Downscale video to 1080p

### GPU costs higher than expected
- Verify GPU instances terminate after processing
- Check video resolution (4K adds processing time)
- Review Runpod dashboard for stuck instances

## Development Status

### ✅ Completed:
- Requirements gathering
- Infrastructure setup documentation
- Docker image structure
- Flask web server
- Video processing pipeline
- Make.com automation workflows
- Configuration management

### 🚧 TODO:
- [ ] Obtain Wan2.2-Animate model weights
- [ ] Integrate Wan2.2-Animate into face_swap_segment()
- [ ] Build and test Docker image
- [ ] Deploy to Runpod
- [ ] End-to-end testing with real videos

### 📝 Known Limitations:
- Face-swap currently uses placeholder (copies original segment)
- Needs actual Wan2.2-Animate model integration
- No local testing environment (GPU-only by design)

## Next Steps

1. **Obtain Wan2.2-Animate model:**
   - Check official repository for download links
   - Download ~15GB model files
   - Place in `docker/models/` directory

2. **Build Docker image:**
   - Follow instructions in `docker/README.md`
   - Push to Docker Hub
   - Create Runpod template

3. **Configure services:**
   - Follow `docs/01-setup-guide.md`
   - Fill in `config/config.yaml`
   - Test with 1-2 sample videos

4. **Production testing:**
   - Process 5-10 test videos
   - Validate output quality
   - Monitor costs and timing

5. **Scale to production:**
   - Process 20+ videos per batch
   - Optimize based on results
   - Plan V2 features (perturbations, Higgsfield API)

## Support

- **Setup issues:** Review `docs/01-setup-guide.md`
- **Daily operations:** See `docs/02-daily-operations.md`
- **Docker build:** Check `docker/README.md`
- **Error messages:** Look at `Error_Log` column in Airtable

## License

Private project - not for distribution

## Version

**V1 MVP** - Last updated: 2025-10-30
