# UGC Face Swapper System - Business Overview (Anti-Detection Enhanced)

## What This System Does

Takes ONE creator video and turns it into MULTIPLE videos with different faces—automatically, with built-in anti-detection variations.

**Input:** 1 video (30 seconds) + 20 avatar images  
**Output:** 20 UNIQUE videos with different faces AND randomized fingerprints  
**Time:** 3-4 minutes per video (fully automated)  
**Cost:** $0.018 per video when processing in batches

**Critical Enhancement:** Each output video has randomized visual, audio, and metadata fingerprints to prevent platform pattern detection.

---

## The Business Case

### Traditional UGC Creation:
- Pay 20 creators × $50-200 each = $1,000-4,000
- Wait days for delivery
- Inconsistent quality/messaging
- Manual coordination hell

### This System:
- Pay 1 creator once = $50-200
- Get 20 variations in ~1 hour
- Identical script/demo, different faces
- **Built-in anti-detection:** Each video is unique at pixel/audio/metadata level
- Zero coordination after initial video

**Use Cases:**
- Test which face/demographic converts best on paid ads
- Scale one winning video across multiple TikTok accounts
- Localize content (different ethnicities for different markets)
- Rapid creative testing without burning creator budgets

---

## How The System Works (Non-Technical)

### Video Structure (Hardcoded)
Every video MUST follow this exact format:

```
0-5 seconds:    Person talking (FACE-SWAPPED)
5-15 seconds:   Product demo (KEPT ORIGINAL)
15-20 seconds:  Person talking (FACE-SWAPPED)
20-30 seconds:  Product demo (KEPT ORIGINAL)
```

The system automatically knows to swap the talking head segments and preserve the product demo footage.

---

## Anti-Detection Features (Automated)

### What Makes Each Video Unique:

**1. Visual Variations (Applied Post-Swap):**
- Random zoom: 95-105% per video
- Random crop position: ±10-15 pixels
- Playback speed variation: 0.97-1.03x (imperceptible to humans)
- Random color grading adjustments: ±5% brightness/contrast
- Segment timing micro-shifts: ±0.2-0.5 seconds on transitions

**2. Audio Fingerprint Randomization:**
- Voice pitch shift: ±2-5% (maintains natural sound)
- Playback speed variance: 0.98-1.02x (synced with video)
- Background ambient layer: subtle noise/cafe sounds at 5-10% volume
- Audio bitrate variation: 128-192 kbps per video

**3. Metadata Randomization:**
- File creation timestamps: randomized within 24-hour window
- Video bitrate: 2800-4200 kbps (random per video)
- Encoding settings: H.264 profile variations
- Container metadata: randomized encoder version strings
- File naming: UUID-based unique identifiers

**Why This Matters:**
TikTok's AI flags videos with identical:
- Frame timing patterns
- Audio waveform signatures  
- File metadata clusters
- Upload pattern correlation

This system breaks ALL these fingerprints automatically—no manual work required.

---

## Airtable Structure (Two-Tab System)

Your Airtable base has **2 main tabs** where videos flow through automatically:

### **Tab 1: Content Generation** (Processing Queue)
Where you upload raw inputs. System processes them automatically.

### **Tab 2: Content Management** (Distribution Dashboard)  
Where completed videos appear ready for download, caption writing, and TikTok deployment.

---

### Tab 1: Content Generation (Processing Queue)

**Purpose:** Upload raw videos/avatars here. Track GPU processing status.

| Field Name | Type | What It Does |
|------------|------|--------------|
| `Video_ID` | Autonumber | Unique identifier (auto-generated) |
| `Original_Video_URL` | URL | Source UGC video link |
| `Avatar_Generation_Mode` | Single Select | "Manual URL" / "Higgsfield API" (choose method) |
| `Avatar_Image_URL` | URL | AI avatar image link (if Manual mode) |
| `Higgsfield_Prompt_Template` | Long Text | Avatar generation prompt (if Higgsfield mode) |
| `Higgsfield_Character_ID` | Single Line Text | Character ID from Higgsfield API (auto-populated) |
| `Generated_Avatar_URL` | URL | Auto-populated by system if Higgsfield used |
| `Batch_ID` | Single Line Text | Group identifier (e.g., "2025-10-29-batch1") |
| `Variation_Preset` | Single Select | Light / Medium / Heavy perturbation |
| `Processing_Status` | Single Select | Pending → Processing → Complete → Failed |
| `Output_Video_URL` | URL | Populated when Complete |
| `Processing_Error` | Long Text | Error details if Failed |
| `Perturbation_Log` | Long Text | Auto-logged variations applied |
| `Avatar_Source` | Single Line Text | "Midjourney_v6" / "Stock_Pexels" / "SD_XL" |
| `Avatar_Batch_ID` | Single Line Text | Avatar group ID for reuse tracking |
| `Avatar_Reuse_Count` | Number | Times this avatar URL was used |
| `Last_Avatar_Use_Date` | Date | When avatar was last processed |
| `Date_Submitted` | Created Time | Auto-generated timestamp |
| `Date_Processed` | Last Modified Time | Auto-updated when Complete |
| `GPU_Instance_ID` | Single Line Text | Runpod instance reference |
| `Creator_Name` | Single Line Text | Original video creator |
| `Face_Swap_Segments` | Formula | Displays "0-5s, 15-20s swapped" |
| `Notes` | Long Text | Internal QA notes |

**Your Action (Two Options):**

**Option A: Manual Avatar Upload**
1. Add new row with Original_Video_URL
2. Set `Avatar_Generation_Mode`: "Manual URL"
3. Paste `Avatar_Image_URL` (your pre-generated avatar)
4. Select `Variation_Preset`
5. Status auto-sets to "Pending"

**Option B: Automatic Avatar Generation (Recommended for Bulk)**
1. Add new row with Original_Video_URL
2. Set `Avatar_Generation_Mode`: "Higgsfield API"
3. Enter `Higgsfield_Prompt_Template`: "Professional {age} year old {ethnicity} {gender}, {lighting}, headshot"
4. Select `Variation_Preset`
5. Status auto-sets to "Pending"
6. System auto-generates unique avatar during processing
7. `Generated_Avatar_URL` auto-populates when complete

**Walk away—system handles everything including avatar generation.**

---

### Tab 2: Content Management (Distribution Dashboard)

**Purpose:** Your command center. Completed videos appear here automatically. Write captions, assign accounts, track deployment.

| Field Name | Type | What It Does |
|------------|------|--------------|
| `Video_Asset_ID` | Linked Record | Links to Content Generation record |
| `Batch_ID` | Lookup | From linked Content Generation record |
| `Final_Video_URL` | URL | **Ready-to-download processed video** |
| `Avatar_Used` | Attachment | Avatar image thumbnail |
| `Original_Creator` | Lookup | From linked record |
| `Variation_Applied` | Lookup | Light/Medium/Heavy used |
| `Assigned_TikTok_Account` | Single Select | Which account posts this (dropdown) |
| `TikTok_Username` | Lookup | From Account Reference table |
| `Device_Container_ID` | Single Select | Which device/VM/emulator |
| `Market_Region` | Single Select | US / ES / MX / UK / etc. |
| `Language` | Single Select | EN / ES / etc. |
| `Upload_Status` | Single Select | Ready → Scheduled → Posted → Failed |
| `Scheduled_Upload_Time` | Date/Time | When you plan to post |
| `Actual_Upload_Time` | Date/Time | When actually posted |
| `Caption_Text` | Long Text | **TikTok caption (you write here)** |
| `Hashtags` | Long Text | **Hashtags for this post** |
| `Profile_Link` | URL | Direct TikTok profile link |
| `Video_Metadata_Hash` | Formula | SHA hash for duplicate detection |
| `Views` | Number | Manual entry after posting |
| `Likes` | Number | Manual entry |
| `Comments_Count` | Number | Manual entry |
| `Conversion_Events` | Number | Clicks/sales tracking |
| `Performance_Notes` | Long Text | "High retention" / "Flagged" / etc. |
| `Moderation_Status` | Single Select | Live / Shadowbanned / Removed |
| `Date_Added` | Created Time | When video appeared here |
| `Last_Updated` | Last Modified Time | Track status changes |

**Your Action:**
1. Video appears automatically when processing completes
2. **Write caption and hashtags** in this tab
3. **Assign TikTok account** from dropdown
4. **Select device and schedule time**
5. **Download video** from Final_Video_URL
6. **Deploy to TikTok** (outside system)
7. **Track performance** manually in this tab

---

### Tab 3: TikTok Account Reference (Supporting Table)

**Purpose:** Master list of all TikTok accounts. Powers dropdown selection in Content Management.

| Field Name | Type | What It Does |
|------------|------|--------------|
| `Account_ID` | Autonumber | Internal reference |
| `Account_Name` | Single Line Text | Nickname (e.g., "TT_US_Female_01") |
| `TikTok_Username` | Single Line Text | @handle |
| `Device_Container_ID` | Single Line Text | Which device this account uses |
| `Market_Assigned` | Single Select | US / ES / MX / etc. |
| `Account_Status` | Single Select | Active / Banned / Warming / Recycled |
| `Registration_Date` | Date | Account creation date |
| `Last_Posted_Date` | Date | Last upload timestamp |
| `Total_Videos_Posted` | Number | Lifetime post count |
| `Daily_Video_Quota` | Number | Max posts per day (default: 1-2) |
| `Videos_Today` | Rollup | Count of today's posts |
| `Quota_Warning` | Formula | Shows "⚠️ OVER QUOTA" if exceeded |
| `Proxy_IP` | Single Line Text | Assigned residential proxy |
| `Phone_Number` | Single Line Text | Registration phone |
| `Email` | Email | Registration email |
| `Notes` | Long Text | Account history/flags |

**Your Action:**
- Add all TikTok accounts to this table
- System pulls from this for account assignment
- Prevents double-posting via quota tracking

---

### How Videos Flow Between Tabs (Automated)

```
[You Upload to Tab 1] 
       ↓
[System Processes]
       ↓
[Status = "Complete"]
       ↓
[Video AUTO-APPEARS in Tab 2]
       ↓
[You Write Caption]
       ↓
[You Assign Account]
       ↓
[You Download & Deploy]
       ↓
[You Track Performance]
```

**Key Insight:** You upload once to Tab 1. Video automatically appears in Tab 2 when ready. All deployment work happens in Tab 2.

---

## Summary: Two-Tab Workflow at a Glance

**Tab 1 (Content Generation) = Processing Queue**
- You upload: Videos + Avatars
- System processes: Face-swap + perturbations  
- Status tracking: Pending → Complete
- **You never download videos from here**

**Tab 2 (Content Management) = Your Distribution Dashboard**
- Videos appear automatically when ready
- You write: Captions + hashtags
- You assign: TikTok accounts + devices + schedule times
- You download: Final videos from here
- You track: Deployment status + performance metrics
- **This is your daily workspace**

**Complete Flow:**
```
Morning: Upload to Tab 1 → Walk away
Afternoon: Videos appear in Tab 2 → Write captions & assign accounts
Evening: Download videos → Deploy to TikTok → Update status
Next Day: Enter performance data → Analyze winners
```

---

## The Workflow (User Perspective)

### Step 1: Upload to Airtable (Tab 1: Content Generation)
You add a new row to the Content Generation tab:
- Column: Original_Video_URL (paste link)
- Column: Avatar_Image_URL (paste link)
- Column: Variation_Preset (select: "Light", "Medium", or "Heavy")
- Column: Batch_ID (type today's batch ID)
- Processing_Status auto-sets to "Pending"

**That's it.** No buttons to click. System watches this tab automatically.

### Step 2: Automation Kicks In (Background)
Every 5 minutes, the system checks for pending videos. When it finds them:
- Collects up to 20 pending videos (batch processing)
- Spins up a GPU server on Runpod
- Sends all videos to the GPU for processing

### Step 3: GPU Processing (Automatic + Anti-Detection + Avatar Generation)
The GPU server (you never touch it):
1. Checks `Avatar_Generation_Mode`
2. **IF "Higgsfield API":**
   - Calls Higgsfield `/character/create` endpoint with randomized prompt
   - Variables auto-randomized: {age}, {ethnicity}, {gender}, {lighting}, {expression}
   - Receives character ID and status "not_ready"
   - Polls `/character/{character_id}` endpoint every 5 seconds (max 60 seconds)
   - Waits for status "ready"
   - Extracts thumbnail_url from character response
   - Saves character ID and avatar URL to Airtable
   - Uses generated avatar for face-swap
3. **IF "Manual URL":**
   - Uses provided `Avatar_Image_URL` directly
4. Downloads video and avatar
5. Splits video into 4 segments (timestamps hardcoded)
6. Face-swaps segments 1 and 3 with avatar
7. Keeps segments 2 and 4 as original demo footage
8. **APPLIES RANDOM PERTURBATIONS:**
   - Zoom/crop variations
   - Speed adjustments
   - Audio modulation
   - Color grading shifts
9. **RANDOMIZES METADATA:**
   - File timestamps
   - Encoding settings
   - Bitrate variations
10. Stitches everything back together
11. Uploads final video to your S3 storage
12. Updates Airtable with download link + perturbation log
13. Shuts itself down

### Step 4: Video Appears in Tab 2 (Content Management)
When processing completes, video automatically appears in Content Management tab:
- Final_Video_URL: Ready for download
- Upload_Status: Shows "Ready"
- All other fields: Empty (waiting for you to fill)

**Your turn:**
1. **Write Caption_Text** for TikTok
2. **Add Hashtags** 
3. **Select Assigned_TikTok_Account** from dropdown
4. **Select Device_Container_ID** 
5. **Set Scheduled_Upload_Time**
6. **Download video** from Final_Video_URL
7. **Deploy to TikTok** manually (outside this system)
8. **Update Upload_Status** to "Posted"
9. **Enter performance metrics** later (views, likes, conversions)

**If face detection fails:** Status shows "Failed" with error message. Skip that video, move on.

---

## System Architecture (Simple View)

```
[You Upload] → [Airtable] → [Make.com Automation] → [GPU Server] → [S3 Storage] → [Final Video URL]
                    ↓                                       ↓
              [Triggers every 5min]         [Face-swap + Anti-Detection Layer]
                                            [Auto-terminates when done]
```

**Key Components:**
1. **Airtable** = Your control panel (spreadsheet interface)
2. **Make.com** = Automation glue (watches Airtable, talks to GPU)
3. **Runpod GPU** = Processing engine (face-swap + perturbations + avatar generation)
4. **Higgsfield.ai API** = Avatar generation service (optional, for automatic mode)
5. **S3 Storage** = Where finished videos live (permanent hosting)

---

## Docker Configuration (What Gets Edited)

The GPU Docker image requires a single `config.yaml` file that you edit once during setup:

```yaml
# Storage Configuration
storage:
  provider: "s3"
  s3_bucket: "your-bucket-name"
  s3_region: "us-east-1"
  s3_access_key: "YOUR_S3_ACCESS_KEY"
  s3_secret_key: "YOUR_S3_SECRET_KEY"

# Airtable Configuration
airtable:
  api_key: "YOUR_AIRTABLE_API_KEY"
  base_id: "YOUR_BASE_ID"
  table_name: "Content_Generation"

# Higgsfield API Configuration (Optional - only needed for automatic avatar generation)
higgsfield:
  api_key: "YOUR_HIGGSFIELD_API_KEY"
  base_url: "https://api.higgsfield.ai"
  create_character_endpoint: "/character/create"
  get_character_endpoint: "/character/{character_id}"
  polling_interval_seconds: 5
  max_polling_attempts: 12

# Processing Configuration
processing:
  segments:
    swap_1: [0, 5]
    original_1: [5, 15]
    swap_2: [15, 20]
    original_2: [20, 30]
  wan2_model_path: "/models/wan2.2-animate"
  output_resolution: "1080p"
  face_detection_confidence: 0.6

# Avatar Randomization Variables (for Higgsfield API prompt templates)
avatar_randomization:
  age_ranges: ["25-30", "30-35", "35-40", "40-50"]
  ethnicities: ["Caucasian", "Hispanic", "Asian", "Black", "Middle Eastern"]
  genders: ["male", "female"]
  lighting: ["studio lighting", "natural light", "soft lighting", "golden hour"]
  expressions: ["confident smile", "neutral", "friendly", "professional"]
```

**API Response Flow:**
1. POST `/character/create` with generated prompt → Returns character `id` + status "not_ready"
2. Poll GET `/character/{id}` every 5 seconds → Wait for status "ready"
3. Extract `thumbnail_url` from response → Use as avatar for face-swap
4. Store character `id` in Airtable for tracking

**You only edit:** API key. Everything else is pre-configured.

---

## What You Need To Get Started

### Accounts & Costs:
1. **Airtable** - $20/month (Pro plan)
2. **Make.com** - $29/month (Core plan for automation)
3. **Runpod** - $50 initial credit (pay-per-use GPU rental)
4. **AWS S3** - $46/month for 1,000 videos (storage + bandwidth)
5. **Higgsfield.ai** - API access for automatic avatar generation (pricing varies, ~$0.05-0.15 per avatar)

**Total Setup:** ~$145/month + GPU usage + Higgsfield avatar generation (if using API mode)

### One-Time Setup (1-2 hours):
1. Create Airtable base (copy provided template with Higgsfield fields)
2. Set up S3 bucket (follow 5-step guide)
3. Get Higgsfield.ai API key (if using automatic avatar generation)
4. Configure Make.com automation (drag-and-drop blueprint)
5. Edit config file with your API keys (S3, Airtable, Higgsfield)
6. Test with 3 sample videos (1 manual avatar, 2 auto-generated)

**After setup:** You never touch the system again. Just upload to Airtable.

---

## Processing Costs Breakdown

### Single Video Processing:
- GPU rental (A40): $0.036/video (includes anti-detection processing)
- **Avatar generation (if using Higgsfield API): $0.05-0.15/video**
- **Total with auto-avatar: $0.086-0.186/video**
- **Total with manual avatar: $0.036/video**

### Batch Processing (10-20 videos):
- GPU rental: $0.020/video (includes perturbations)
- Avatar generation (Higgsfield API): $0.10/video (average)
- **Total per video with auto-avatar: $0.120**
- **Total per video with manual avatar: $0.020**
- **Still 400x cheaper than hiring creators**

### Monthly Cost Example (100 videos/day):

**Option A: Manual Avatar Upload (You Generate in Higgsfield Manually)**
- 3,000 videos × $0.020 = $60 (GPU processing only)
- Avatar costs: Already paid separately in Higgsfield
- Storage & bandwidth = $46
- Airtable + Make.com = $49
- **Total: $155/month** (excluding your manual Higgsfield usage)

**Option B: Automatic Avatar Generation (Higgsfield API Integrated)**
- 3,000 videos × $0.020 = $60 (GPU)
- 3,000 avatars × $0.10 = $300 (Higgsfield API)
- Storage & bandwidth = $46
- Airtable + Make.com = $49
- **Total: $455/month**
- **Time saved: ~15 hours/month** (no manual avatar generation)

**Break-even:** If your time is worth $20/hour, automatic generation pays for itself at 100+ videos/day.

**Cost per video:** $0.052 (vs. $50-200 paying creators)

---

## Processing Time

### Single Video (With Anti-Detection):

**Manual Avatar Mode:**
- GPU spin-up: 45-60 seconds
- Face-swap processing: 180-240 seconds
- Perturbation layer: +30-45 seconds
- Metadata randomization: +5-10 seconds
- **Total: 4-5 minutes** per video

**Automatic Avatar Generation Mode:**
- GPU spin-up: 45-60 seconds
- Higgsfield character creation + polling: +15-30 seconds (async generation)
- Face-swap processing: 180-240 seconds
- Perturbation layer: +30-45 seconds
- Metadata randomization: +5-10 seconds
- **Total: 5-6.5 minutes** per video

### Batch of 20 Videos:

**Manual Avatar Mode:**
- GPU spin-up: 60 seconds (once)
- Processing: 20 videos × 4 min = 80 minutes
- **Total: ~85 minutes** for entire batch

**Automatic Avatar Generation Mode:**
- GPU spin-up: 60 seconds (once)
- Avatar generation: 20 characters × 20 seconds avg = 6-7 minutes (sequential polling)
- Processing: 20 videos × 4 min = 80 minutes
- **Total: ~95 minutes** for entire batch

**Time savings vs. manual avatar generation:** You save 30 minutes of manual clicking in Higgsfield, adds ~10 minutes to processing due to API polling overhead.

---

## Quality & Detection Resistance

### What Makes Output High-Quality:
- Uses Wan2.2-Animate-14B (state-of-the-art face-swap model)
- Preserves original video quality (no visible degradation)
- Maintains natural facial movements and expressions
- Original demo footage untouched (preserves authenticity)
- Perturbations are imperceptible to human viewers

### Platform Detection Resistance:

**VIDEO FINGERPRINT PROTECTION:**
- ✅ Unique pixel patterns per video (zoom/crop variations)
- ✅ Different frame timing (speed variations)
- ✅ Altered visual signatures (color grading)

**AUDIO FINGERPRINT PROTECTION:**
- ✅ Unique waveform per video (pitch/speed shifts)
- ✅ Different audio spectrum (background layers)
- ✅ Varied encoding (bitrate randomization)

**METADATA FINGERPRINT PROTECTION:**
- ✅ Unique file creation times
- ✅ Different encoding profiles
- ✅ Randomized technical fingerprints

**LIMITATIONS (You Must Handle Separately):**
- ⚠️ Account/device fingerprinting (use multi-device, multi-IP strategy)
- ⚠️ Posting patterns (stagger uploads manually)
- ⚠️ Caption/hashtag similarities (vary manually)
- ⚠️ Voiceprint similarities (all variants share base voice)

**Mitigation Strategy:**
System handles video-level uniqueness. You handle distribution-level anonymity:
- Never upload multiple variants from same device/account
- Space uploads 3-12 hours apart
- Rotate accounts and IPs manually

---

## Avatar Management (Critical for Scale)

### Two Avatar Generation Methods

**Method 1: Manual Upload (Maximum Control)**
- You generate avatars in Higgsfield.ai manually
- Download and upload to S3
- Paste URLs into Airtable
- **Best for:** Testing specific looks, high-value campaigns
- **Time cost:** ~30 minutes per 20-avatar batch

**Method 2: Higgsfield API Auto-Generation (Maximum Speed)**
- System calls Higgsfield API during processing
- Generates unique avatar per video automatically
- No manual downloading/uploading required
- **Best for:** Bulk processing, speed over curation
- **Time cost:** 0 minutes (fully automated)

---

### Higgsfield API Prompt Template System

When using `Avatar_Generation_Mode: "Higgsfield API"`, you provide a text prompt with variable placeholders:

**Example Template:**
```
Professional headshot of {age} year old {ethnicity} {gender}, {lighting}, {expression}, plain background
```

**System Auto-Randomizes Variables:**

Each video gets unique random selections from these pools:

- **{age}**: 25-30, 30-35, 35-40, 40-50
- **{ethnicity}**: Caucasian, Hispanic, Asian, Black, Middle Eastern
- **{gender}**: male, female
- **{lighting}**: studio lighting, natural light, soft lighting, golden hour
- **{expression}**: confident smile, neutral, friendly, professional

**Example Generated Prompts:**
1. "Professional headshot of 30-35 year old Hispanic female, studio lighting, confident smile, plain background"
2. "Professional headshot of 35-40 year old Asian male, natural light, professional, plain background"
3. "Professional headshot of 25-30 year old Black female, soft lighting, friendly, plain background"

**Result:** Each video gets a unique character created via Higgsfield API with completely different demographic combinations.

---

### Avatar Diversity Requirements

**Manual Upload Mode:**

**DO NOT:**
- ❌ Reuse the same 20 avatars across multiple batches
- ❌ Generate all avatars from same AI prompt/seed
- ❌ Use visually similar faces in one batch

**DO:**
- ✅ Generate fresh avatars for EACH new batch
- ✅ Mix avatar sources (Higgsfield + stock photos + Stable Diffusion)
- ✅ Vary facial expressions, angles, lighting in avatars
- ✅ Track which avatars used in which batch (Airtable logging)

**Higgsfield API Auto-Generation Mode:**

**Automatic Benefits:**
- ✅ Zero reuse risk (every avatar is API-generated fresh)
- ✅ Built-in randomization (system varies all parameters)
- ✅ No tracking needed (system logs all generated avatars)
- ✅ Infinite scalability (generate 1000+ unique avatars)

**You only need to:**
- Define prompt template once
- System handles all diversity automatically
- No manual tracking required

---

### Quick Comparison: Manual vs. Automatic Avatar Generation

| Factor | Manual Upload | Higgsfield API Automatic |
|--------|---------------|-------------------------|
| **Setup Time** | 30 min per batch | 2 min (write prompt once) |
| **Cost per Avatar** | Already paid in Higgsfield | $0.05-0.15 via API |
| **Quality Control** | Maximum (you curate) | High (AI-generated) |
| **Diversity Risk** | Medium (manual tracking needed) | Zero (always unique) |
| **Scalability** | Limited by your time | Unlimited |
| **Processing Overhead** | +0 seconds (pre-generated) | +15-30 seconds (API + polling) |
| **Best For** | Test campaigns, curation | Bulk scaling, speed |
| **Avatar Reuse Risk** | High (if not tracked) | Zero (impossible to reuse) |
| **Tracking Required** | Yes (manual) | No (character IDs auto-logged) |

**Recommendation:** Start with Manual for first 50 videos to validate creative. Switch to Automatic once you're scaling proven winners.

---

### Airtable Avatar Tracking

**New Columns Added:**
- `Avatar_Batch_ID`: Groups avatars used together
- `Avatar_Source`: "Midjourney_v6" / "Stock_Unsplash" / "SD_XL"
- `Avatar_Reuse_Count`: How many times this avatar image used
- `Last_Used_Date`: When avatar was last processed

**Auto-Warning System:**
If you try to upload an avatar URL that was used in last 30 days, Airtable formula flags:
- `Avatar_Status`: "⚠️ RECENTLY USED - Generate New Avatar"

### Avatar Generation Workflow

**Per Batch (20 videos):**
1. Generate 20 NEW avatar images
2. Mix sources: 10 from Midjourney, 5 from stock sites, 5 from Stable Diffusion
3. Vary prompts: different ages, ethnicities, expressions, lighting
4. Upload to separate folder in S3: `/avatars/batch_2025-10-29/`
5. Log all avatar URLs in Airtable before processing

**Never reuse avatar images across batches to prevent TikTok cross-correlation detection.**

---

## Perturbation Presets Explained

### Light Perturbation (Recommended Default)
**Use when:** Testing new creative, want minimal changes
- Zoom: 97-103%
- Crop: ±5 pixels
- Speed: 0.99-1.01x
- Audio pitch: ±2%
- Color: ±3% brightness
- **Detection risk:** Low (if combined with proper distribution strategy)

### Medium Perturbation (Recommended for Scale)
**Use when:** Scaling proven winners across 50+ accounts
- Zoom: 95-105%
- Crop: ±10 pixels
- Speed: 0.97-1.03x
- Audio pitch: ±5%
- Color: ±5% brightness/contrast
- Background audio: 5-8% volume
- **Detection risk:** Very Low

### Heavy Perturbation (Maximum Anonymity)
**Use when:** Aggressive scaling, high-risk markets, flagged content
- Zoom: 93-107%
- Crop: ±15 pixels
- Speed: 0.95-1.05x
- Audio pitch: ±8%
- Color: ±10% brightness/contrast/saturation
- Background audio: 8-12% volume
- Additional: Random blur/sharpen filters
- **Detection risk:** Minimal (videos may look slightly different to humans)
- **Trade-off:** Some quality degradation visible

**Select preset in Airtable Column C when uploading videos.**

---

## Error Handling

### Common Failures (Auto-Handled):

**Face Detection Fails:**
- Avatar photo too dark/blurry
- Multiple faces in talking segments
- **System Action:** Skips video, logs error, continues batch

**Higgsfield API Failures:**
- Character creation timeout (>60 seconds polling)
- API rate limit exceeded
- Invalid prompt/character generation failed
- **System Action:** Falls back to placeholder avatar (if configured) OR skips video, logs error

**GPU Out of Memory:**
- Source video resolution too high (4K+)
- **System Action:** Auto-downscales to 1080p, retries

**Network Timeout:**
- Video file too large (>500MB)
- **System Action:** Retries 3x, then marks failed

**Perturbation Processing Error:**
- Rare codec incompatibility
- **System Action:** Falls back to minimal perturbations, logs warning

### You Only Intervene When:
- Airtable shows "Failed" status
- Error log says "Manual review needed"
- Otherwise, system self-heals

---

## Operational Workflow (Daily Use)

### Morning Batch Prep (Two Methods):

---

**METHOD A: MANUAL AVATAR UPLOAD** (Maximum Control)

**1. Avatar Generation (30 minutes):**
- Generate 20 fresh avatars in Higgsfield.ai manually
- Mix demographics: vary age, ethnicity, expression, lighting
- Download all 20 images
- Upload to S3 folder: `/avatars/batch_[TODAY'S-DATE]/`
- Copy all 20 URLs

**2. Airtable Tab 1 Upload:**
- Add 20 new rows to Content Generation tab
- `Original_Video_URL`: Same source video for all 20 rows
- `Avatar_Generation_Mode`: Select "Manual URL"
- `Avatar_Image_URL`: Paste different avatar URL for each row
- `Variation_Preset`: Select "Medium"
- `Batch_ID`: Type today's date
- `Processing_Status`: Auto-sets to "Pending"

---

**METHOD B: AUTOMATIC AVATAR GENERATION** (Maximum Speed - Recommended for Bulk)

**1. Skip Manual Avatar Generation (0 minutes saved):**
- No Higgsfield clicking required
- No downloading/uploading

**2. Airtable Tab 1 Upload:**
- Add 20 new rows to Content Generation tab
- `Original_Video_URL`: Same source video for all 20 rows
- `Avatar_Generation_Mode`: Select "Higgsfield API"
- `Higgsfield_Prompt_Template`: Enter template once (applies to all rows):
  ```
  Professional headshot, {age} year old {ethnicity} {gender}, {lighting}, {expression}, plain background
  ```
- `Variation_Preset`: Select "Medium"
- `Batch_ID`: Type today's date
- `Processing_Status`: Auto-sets to "Pending"

**That's it. System generates 20 unique avatars automatically.**

---

### Afternoon - Processing & Preparation:
- **1:00 PM:** System automatically detects pending videos in Tab 1
- **1:05 PM:** GPU spins up, begins batch processing
- **2:30 PM:** All 20 videos show "Complete" status in Tab 1
- **2:31 PM:** All 20 videos AUTO-APPEAR in Tab 2 (Content Management)

**3. Airtable Tab 2 Work (Content Management Dashboard):**

For each completed video row in Tab 2:
- **Write Caption_Text:** Craft TikTok caption (hook + CTA)
- **Add Hashtags:** 5-10 relevant tags
- **Select Assigned_TikTok_Account:** Choose from dropdown
- **Select Device_Container_ID:** Match device to account
- **Set Market_Region:** US/ES/MX/etc.
- **Set Scheduled_Upload_Time:** Stagger 3-12 hours apart
- **Download video:** Click Final_Video_URL

**This prep work takes ~2 hours for 20 videos** (caption writing is the bottleneck)

### Evening - Deployment (You Handle Outside System):
- Upload videos to assigned TikTok accounts manually
- Use correct device/emulator per account
- Follow scheduled times (never batch-upload)
- **Update Tab 2 after each upload:**
  - Upload_Status: Change to "Posted"
  - Actual_Upload_Time: Log timestamp
  - Profile_Link: Add TikTok post URL

### Next Morning - Performance Tracking:
- Open Tab 2 (Content Management)
- For posted videos, enter metrics:
  - Views, Likes, Comments_Count
  - Conversion_Events (if tracking sales/clicks)
  - Performance_Notes ("High retention 85%" / "Flagged at 2K views")
- **Identify winners:** Which avatars/captions performed best
- **Do NOT reuse winning avatars** - analyze traits instead
- **Generate new avatars** with similar characteristics for next batch

---

## Scaling Strategy (Anti-Detection Focused)

### Phase 1: Test (Week 1) - 20 Videos
- Process 1 source video with 20 different avatars
- Use "Light" perturbation preset
- Deploy across 10-15 accounts (max 2 variants per account)
- Space uploads 6+ hours apart
- Track engagement per avatar demographic

### Phase 2: Scale Winners (Week 2-4) - 100-200 Videos
- Identify top 3 avatar demographics (e.g., "25-35 female, warm lighting")
- Generate 50 NEW avatars matching winning traits
- Process 5 different source videos × 20 avatars = 100 variants
- Use "Medium" perturbation preset
- Deploy across 50-80 accounts
- **Critical:** Never use same avatar twice

### Phase 3: Automation (Month 2+) - 500+ Videos
- Queue 500+ video variations
- Generate 500 unique avatars (reuse ZERO)
- Use "Medium" or "Heavy" presets
- System processes in batches automatically
- Focus shifts to:
  - Account management
  - Proxy rotation
  - Performance optimization

### Capacity & Limits:
- **Technical capacity:** 1,000+ videos/day
- **Safe deployment capacity:** 100-200 videos/day (limited by account availability)
- **Bottleneck:** Account farming, not processing power
- **Scaling rule:** 1 video per account per day maximum

---

## What This System Does vs. What You Do

**System Handles (Automatic):**
- ✅ Face-swapping automation at scale
- ✅ Video fingerprint randomization (visual/audio/metadata)
- ✅ Avatar tracking and reuse prevention
- ✅ Batch processing optimization
- ✅ Auto-populating Tab 2 with completed videos
- ✅ Status tracking across both tabs

**You Handle (In Tab 2 - Content Management):**
- ✏️ Writing captions and hashtags
- 👤 Assigning TikTok accounts to videos
- 📱 Selecting devices/emulators
- 📅 Setting upload schedules
- ⬇️ Downloading finished videos
- 📤 Uploading to TikTok manually
- 📊 Tracking performance metrics
- 🎯 Account/device/IP management (outside Airtable)

**You Handle (Outside System Entirely):**
- ❌ Creating original UGC video (hire creator)
- ❌ Generating AI avatar images (Midjourney/SD/stock)
- ❌ Multi-device posting (antidetect browser + emulators)
- ❌ IP rotation (residential proxies)
- ❌ TikTok upload automation (separate tools)
- ❌ Account farming/warming
- ❌ Posting cadence enforcement

**Clear Division:**
- **System:** Makes videos unique and tracks them
- **Tab 2 (You):** Manages deployment strategy and execution
- **External Tools (You):** Handles TikTok posting infrastructure

---

## Technical Requirements Summary

### Your Responsibilities:
- Upload video URLs and avatar URLs to Airtable
- Select perturbation preset per batch
- Generate fresh avatars for each batch (never reuse)
- Download finished videos
- Handle distribution (accounts, devices, IPs, timing)

### System Handles Automatically:
- GPU server provisioning
- Video segmentation
- Face-swap processing
- **Anti-detection perturbations (visual/audio/metadata)**
- Video reassembly
- Cloud storage uploads
- Avatar reuse tracking
- Status updates
- Cost optimization (batch processing)
- Server shutdown after completion

### Skills Needed:
- Basic spreadsheet usage (Airtable)
- Following setup guide (1-2 hours)
- Avatar generation (Midjourney/Stable Diffusion basic prompts)
- **No coding required**

---

## ROI Calculation

### Traditional Approach (20 videos):
- 20 creators × $100 = $2,000
- Coordination time = 10 hours
- Delivery time = 3-5 days
- Detection risk = Low (organic diversity)

### This System (20 videos):
- 1 creator × $100 = $100
- 20 avatars (fresh generation) = $2-5 (AI image costs)
- 20 videos × $0.020 = $0.40 (processing with anti-detection)
- Setup time = 45 minutes (avatar gen + Airtable upload)
- Delivery time = 1.5 hours
- Detection risk = Low (with proper distribution strategy)

**Savings per batch:** $1,895 + 9 hours  
**Breakeven:** First batch pays for entire monthly cost

**Hidden value:** Unlimited creative testing without creator burnout/coordination overhead.

---

## Critical Operating Rules (Anti-Detection)

### Avatar Generation Method Decision:

**Use Manual Upload When:**
- Testing specific demographics or looks
- High-value campaign requiring curation
- Need exact control over avatar quality
- Processing <50 videos/week
- Your time is not a bottleneck

**Use Higgsfield API Automatic When:**
- Bulk processing (100+ videos/batch)
- Speed is priority
- You already use Higgsfield regularly
- Processing >100 videos/week
- Want zero manual avatar work

**Hybrid Approach (Recommended):**
- Test campaigns: Manual (10-20 curated avatars)
- Scale winners: Automatic (100+ variants)
- Saves time on proven creative, maintains control for tests

---

### Avatar Management Rules:
1. **NEVER reuse avatar images across batches**
2. Generate 20 fresh avatars per batch minimum
3. Mix avatar sources (AI + stock photos)
4. Track all avatar usage in Airtable
5. If avatar performs well, generate NEW similar avatars (don't reuse)

### Distribution Rules (You Enforce):
1. **NEVER upload multiple variants from same device**
2. Max 1-2 videos per account per day
3. Space uploads 3-12 hours apart for similar content
4. Rotate IP addresses (residential proxies)
5. Match device region to target market

### Batch Processing Rules:
1. Minimum 10 videos per batch (cost efficiency)
2. Maximum 20 videos per batch (GPU timeout risk)
3. Use "Medium" perturbation for most use cases
4. Process only 1-2 batches per day (avoid bulk upload temptation)

### Performance Tracking:
1. Log which avatars used with which source videos
2. Track account performance per video variant
3. If flagged: Increase perturbation level, generate new avatars
4. Never re-upload exact same variant to different account

---

## Next Steps To Launch

### 1. Pre-Work (Before Building):
- Record 3 test videos in correct format (talking → demo → talking → demo)
- Generate 10 test avatar images (mix sources)
- Validate video structure with manual editing test

### 2. System Setup (2-3 Hours):
- Create Airtable base (copy template with avatar tracking)
- Configure S3 storage
- Set up Make.com automation
- Deploy GPU docker image to Runpod
- Configure perturbation presets in config file

### 3. Test Run:
- Process 5 videos total:
  - 2 videos with Manual Avatar Upload mode
  - 3 videos with Higgsfield API Automatic mode
- Verify output quality (perturbations imperceptible?)
- Confirm avatar tracking logs correctly
- Check `Generated_Avatar_URL` populates for API mode
- Validate costs match projections (GPU + Higgsfield API)
- Compare processing times between modes

### 4. First Production Batch:
- Generate 20 fresh avatars
- Queue 20 video variations
- Deploy across 10-15 test accounts
- Monitor for flags/performance
- Iterate based on results

**Estimated time to operational:** 3-4 hours (mostly waiting for accounts/approvals)

---

## Summary: What Changed vs. Standard Face-Swap

**Standard face-swap tools:**
- Swap face only
- Output videos are nearly identical (except face)
- Platform detection = HIGH risk at scale

**This system:**
- Swaps face PLUS randomizes everything else
- Each video unique at pixel/audio/metadata level
- Platform detection = LOW risk (if distribution handled correctly)
- Avatar tracking prevents reuse patterns
- Perturbation presets for different risk tolerances

**Key insight:** Face-swapping alone is insufficient for scale. Detection happens at video fingerprint + distribution pattern level. This system solves the fingerprint layer. You solve the distribution layer.