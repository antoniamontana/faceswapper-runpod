# Discovery Answers

Based on the UGC_FaceSwapper_MVP_SOP.md documentation:

## Q1: Will users interact with this face swapper through a web-based interface?
**Answer:** No - Users interact through Airtable (spreadsheet interface) for uploading videos and tracking processing status. There is no custom web UI.

## Q2: Should the application support real-time face swapping (via webcam/video)?
**Answer:** No - This is batch processing of pre-recorded 30-second UGC videos. Videos are uploaded to Airtable and processed asynchronously on GPU servers.

## Q3: Will this application need to handle multiple faces in a single image?
**Answer:** No - The system specifically requires single-face avatar images and single-person talking head segments. Multi-face detection causes failures.

## Q4: Should users be able to save and download their face-swapped results?
**Answer:** Yes - Processed videos are automatically uploaded to AWS S3 storage. Users download final videos via URLs populated in Airtable.

## Q5: Will this require user authentication and personal storage?
**Answer:** Yes - Users need:
- Airtable Pro account ($20/month) for database/API access
- AWS S3 account for video storage
- Make.com account ($29/month) for automation
- Runpod account for GPU processing

## Additional Context from MVP:
- **Processing architecture:** Airtable → Make.com → Runpod GPU → S3 Storage
- **Video structure:** Hardcoded segments (0-5s, 15-20s face-swapped; 5-15s, 20-30s original)
- **Model:** Wan2.2-Animate-14B for face-swapping
- **V1 scope:** NO automatic perturbations, NO Higgsfield API integration, NO Tab 2 content management
- **Manual steps:** Users generate avatars in Higgsfield manually, create variants externally


