# Daily Operations Guide

## Morning Workflow (30 minutes setup, then automatic)

### Step 1: Generate Avatars
**Time:** 20-30 minutes

1. Open Higgsfield.ai or Midjourney
2. Generate 20 unique avatars:
   - Vary demographics: age, ethnicity, gender
   - Requirements:
     - Size: 1024x1024 or higher
     - Format: PNG or JPG
     - Single face, front-facing
     - Well-lit, clear features
     - Plain background (recommended)

**Prompt examples:**
- "Professional headshot of 30 year old Asian female, studio lighting, confident smile, plain background"
- "Headshot of 25 year old Hispanic male, natural lighting, friendly expression, white background"
- "Portrait of 40 year old Black female, soft lighting, professional look, gray background"

3. Download all 20 images to local folder

### Step 2: Upload Avatars to Storage
**Time:** 5-10 minutes

**Option A: Upload to S3**
1. Go to AWS S3 console
2. Open your bucket: `faceswap-outputs-[yourname]`
3. Create folder: `avatars/batch-[TODAY'S-DATE]/`
4. Upload all 20 images
5. Copy URLs for each image

**Option B: Upload to Imgur**
1. Go to imgur.com/upload
2. Drag and drop all 20 images
3. Copy direct image URLs (right-click image → Copy image address)

**✅ Pro tip:** Use S3 if you want to keep avatars private until you're ready. Use Imgur for quick testing.

### Step 3: Bulk Add to Airtable
**Time:** 5 minutes

1. Open Airtable → `UGC Face Swap Pipeline` → `Processing Queue`
2. Add 20 new rows (you can copy/paste to speed this up):

   **For each row:**
   - **Source_Video_URL:** Same video URL for all 20 rows
   - **Avatar_Image_URL:** Different avatar URL for each row
   - **Batch_ID:** Type today's date (e.g., `2025-10-30`)
   - **Status:** Select `Pending`

3. Save

**✅ Pro tip:** Use Airtable's bulk import feature:
   - Create CSV with columns: Source_Video_URL, Avatar_Image_URL, Batch_ID, Status
   - Fill 20 rows
   - Import to Airtable
   - Saves 5 minutes!

---

## Monitoring Processing (Automatic)

### What Happens Next (No Action Needed)
1. **Within 5 minutes:** Make.com detects pending videos
2. **Status changes to `Processing`:** GPU spins up
3. **3-4 minutes per video:** Face-swap processing
4. **Status changes to `Complete`:** Video ready to download
5. **Total time for 20 videos:** 60-90 minutes

### How to Monitor
1. Keep Airtable open in browser
2. Refresh every 10 minutes (or enable auto-refresh)
3. Watch Status column:
   - ⏳ `Pending` → Waiting for pickup
   - 🔄 `Processing` → GPU working on it
   - ✅ `Complete` → Ready to download
   - 🚩 `Failed` → Check Error_Log

---

## Downloading Outputs

### Step 4: Download Completed Videos
**Time:** 10 minutes

1. In Airtable, filter view: `Status = Complete`
2. For each completed row:
   - Click `Output_Video_URL`
   - Video downloads automatically
   - Save to folder: `Face-Swapped-Videos/[Batch_ID]/`

**✅ Pro tip:** Right-click each URL → "Save link as..." for batch downloading

### Step 5: Quality Check (Recommended)
**Time:** 5 minutes

Spot-check 2-3 videos:
- ✅ Segments 0-5s and 15-20s: Face-swapped with avatar
- ✅ Segments 5-15s and 20-30s: Original product demo
- ✅ No visible glitches or artifacts
- ✅ Audio synced properly

**If issues found:** Note patterns and adjust avatar quality next time

---

## Post-Processing (External to This System)

### Step 6: Create Variants (Manual)
**Tool:** Contentflow, Premiere Pro, or similar

For each face-swapped video, create variations:
1. **Speed variations:** 0.95x, 1.0x, 1.05x
2. **Zoom variations:** 100%, 102%, 105%
3. **Crop variations:** Shift frame by 5-10 pixels
4. **Color grading:** Adjust brightness ±5%
5. **Audio tweaks:** Pitch shift ±2%

**Output:** 3-5 variants per face-swapped video → 60-100 total unique videos

### Step 7: Deploy to TikTok (Manual)
**Tool:** TikTok mobile app or automation software

1. Assign each variant to different TikTok account
2. Write unique caption for each
3. Add hashtags
4. Schedule uploads 3-12 hours apart
5. Track performance in separate spreadsheet

---

## Cost Tracking

### Daily Cost Estimate (20 videos)
- GPU processing: 20 videos × $0.039 = **$0.78**
- S3 storage: ~**$0.02**
- Total: **$0.80 per day**

### Monthly Cost (100 videos/day)
- GPU: 3,000 videos × $0.039 = **$117**
- S3: **~$5**
- Airtable: **$20**
- Make.com: **$29**
- **Total: $171/month**

**ROI:** $171/month vs. $3,000+ paying creators = **$2,829 saved**

---

## Troubleshooting Quick Reference

### ⚠️ Status stuck on "Pending" for >10 minutes
**Check:**
1. Make.com scenario is toggled ON
2. Airtable connection in Make.com is valid
3. Make.com execution history for errors

### 🚩 Multiple videos showing "Failed"
**Common causes:**
1. **"Face not detected"** → Avatar quality too low
   - **Fix:** Use higher resolution avatars (1024x1024+)
   - **Fix:** Ensure front-facing, well-lit faces

2. **"Video download failed"** → URL not accessible
   - **Fix:** Make sure video URL is public
   - **Fix:** Test URL in browser first

3. **"Processing timeout"** → Video too large
   - **Fix:** Use 1080p max resolution
   - **Fix:** Compress video before uploading

### 💰 GPU costs higher than expected
**Check:**
1. GPU instances terminating properly (check Runpod dashboard)
2. Processing time per video (should be 3-4 min)
3. Are videos 4K? (Downscale to 1080p)

### ⏰ Processing taking too long (>5 min per video)
**Possible causes:**
1. Source video is 4K → System downscales automatically (adds time)
2. GPU queue is busy → Wait or try different time
3. Large file size → Compress video before uploading

---

## Best Practices

### ✅ DO:
- Generate fresh avatars for each batch (don't reuse)
- Test first video before uploading full batch
- Keep batches to 20 videos max
- Use consistent video format (1080p MP4, 30fps)
- Track which avatars used in which batch (use Batch_ID)

### ❌ DON'T:
- Upload 4K videos (waste GPU time on downscaling)
- Reuse same 20 avatars across multiple days
- Process more than 50 videos at once (can overwhelm system)
- Delete completed Airtable rows (keep for tracking)
- Share your API keys or config.yaml

---

## Weekly Maintenance (5 minutes)

1. **Review failed videos:**
   - Filter Airtable: `Status = 🚩 Failed`
   - Read Error_Log for patterns
   - Adjust avatar generation process if needed

2. **Check Runpod costs:**
   - Log into Runpod → Billing
   - Verify per-video cost is ~$0.039
   - Add credit if running low

3. **Clean up S3:**
   - Delete videos older than 30 days (optional)
   - Keep storage costs low

4. **Archive old Airtable records:**
   - Export rows with Date_Completed > 30 days ago
   - Delete from table to keep it fast

---

## Scaling Up

### Processing 50 videos/day:
- Same workflow, just more rows in Airtable
- Cost: ~$2/day = $60/month GPU
- Total monthly: $114

### Processing 100 videos/day:
- Consider batch processing optimization (V2 feature)
- Cost: ~$4/day = $120/month GPU
- Total monthly: $174

### Processing 200+ videos/day:
- Upgrade Make.com to Pro plan ($39/month)
- Consider multiple GPU instances (V2 feature)
- Cost scales linearly: $0.039 per video

---

**Questions? Check troubleshooting section or review Error_Log in Airtable for specific error messages.**
