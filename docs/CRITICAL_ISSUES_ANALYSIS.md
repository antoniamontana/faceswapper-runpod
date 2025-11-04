# Critical System Analysis - First Principles Review

## 1. WHY ARE WE BUILDING THIS? (The Goal)

### Business Objective
Create an automated UGC (User Generated Content) face-swapping system where:
- Users submit: source video + their face photo
- System outputs: personalized video with user's face in specific segments
- Use case: Product demos where customer sees themselves using the product

### Success Criteria
- Fully automated pipeline (no manual intervention)
- Processing time: 3-5 minutes per video
- Cost: ~$0.05 per video
- Quality: Realistic face-swaps in segments 1 & 3

---

## 2. WHAT WE BUILT (Architecture Overview)

```
User → Airtable → Make.com (Scenario 1) → Make.com (Scenario 2) → Runpod GPU → S3 → User
           ↓                                         ↓
      Webhook Trigger                          Docker Container
                                              (Wan2.2 Face-Swap)
```

### Components:
1. **Airtable** - Job queue database
2. **Make.com Scenario 1** - Watches Airtable for new records (instant webhook)
3. **Make.com Scenario 2** - Calls Runpod API to process video
4. **Runpod Serverless** - GPU container that runs face-swapping
5. **Docker Image** - Contains Wan2.2 model + processing code
6. **S3** - Stores output videos

---

## 3. THE ACTUAL FLOW (What Should Happen)

1. User adds row to Airtable:
   - `Source_Video_URL`: https://...
   - `Avatar_Image_URL`: https://...
   - `Status`: Pending

2. Airtable webhook → Make.com Scenario 1

3. Scenario 1:
   - Updates Status → "Processing"
   - Triggers Scenario 2 with record data

4. Scenario 2:
   - Calls Runpod API: `POST https://api.runpod.ai/v2/eaj61xejeec2iw/run`
   - Sends: record_id, video URLs, webhook URL

5. Runpod:
   - Spins up Docker container (45-60 sec cold start)
   - Container runs our processing code

6. Container Processing:
   - Downloads video & avatar
   - Segments video (4 parts: 0-5s, 5-15s, 15-20s, 20-30s)
   - Face-swaps segments 1 & 3
   - Keeps segments 2 & 4 original
   - Stitches back together
   - Uploads to S3
   - Sends webhook to Make.com with result

7. Make.com receives webhook:
   - Updates Airtable Status → "Complete"
   - Adds Output_Video_URL

---

## 4. CRITICAL ISSUES DISCOVERED (The Problems)

### 🚨 ISSUE #1: Runpod Serverless vs Flask Server Mismatch
**Severity**: CRITICAL - System will not work at all

**What we built**:
```python
# app.py - Flask web server
app = Flask(__name__)
@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    # ...
```

**What Runpod Serverless expects**:
```python
# handler.py - Serverless function
def handler(event):
    # event contains input
    # must return output
    return {"status": "success", ...}
```

**Problem**:
- Runpod serverless calls `runpod.serverless.start({"handler": handler})`
- We built a Flask HTTP server
- These are incompatible architectures!

**Solution Needed**:
Rewrite to use Runpod handler pattern OR switch to Runpod Pods (not serverless)

---

### 🚨 ISSUE #2: API Field Name Mismatch
**Severity**: CRITICAL - Request will be rejected

**Make.com sends**:
```json
{
  "input": {
    "record_id": "recXXX",
    "source_video_url": "https://...",
    "avatar_image_url": "https://...",
    "webhook_url": "https://..."
  }
}
```

**Flask app expects** (app.py line 79-85):
```python
required_fields = ['record_id', 'video_url', 'avatar_url']
```

**Problems**:
1. Runpod wraps everything in `"input"` key
2. Field names don't match: `source_video_url` ≠ `video_url`
3. Field names don't match: `avatar_image_url` ≠ `avatar_url`

**Solution Needed**:
Fix field name mapping in app.py

---

### 🚨 ISSUE #3: Configuration Not Passed to Container
**Severity**: CRITICAL - Container will crash on startup

**app.py line 26**:
```python
config_yaml = os.getenv('CONFIG_YAML')
if not config_yaml:
    logger.error("CONFIG_YAML environment variable not set")
    return None
```

**Problem**:
- We have `config/config.yaml` locally
- It's NOT copied to Docker image
- Environment variable is NOT set in Dockerfile or Runpod template
- Container will fail to load config and crash

**Solution Needed**:
Either:
1. Copy config.yaml to Docker image and read from file
2. Pass config as environment variable to Runpod
3. Hardcode minimal config in container

---

### 🚨 ISSUE #4: Wan2.2 Model Commands Unverified
**Severity**: HIGH - Processing will likely fail

**process.py assumes** (lines 98-134):
```python
# Preprocessing
'/app/Wan2.2/wan/modules/animate/preprocess/preprocess_data.py'
'--ckpt_path', '/models/Wan2.2-Animate-14B/process_checkpoint'
'--replace_flag'

# Generation
'/app/Wan2.2/generate.py'
'--task', 'animate-14B'
'--replace_flag'
```

**Problems**:
1. We never verified these scripts exist in Wan2.2 repo
2. We never verified they accept these flags
3. We never verified `--replace_flag` does face-swapping
4. Model path `/models/Wan2.2-Animate-14B/process_checkpoint` might not exist
5. We never tested this locally or in Docker

**Solution Needed**:
1. Read Wan2.2 documentation
2. Verify correct commands
3. Test in Docker container before deployment

---

### 🚨 ISSUE #5: Production Server Not Used
**Severity**: MEDIUM - Performance and stability issues

**Dockerfile line 143**:
```python
app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)
```

**Problem**:
- Using Flask development server
- Not production-ready
- Single-threaded (can only handle 1 request at a time)
- No process management

**Solution Needed**:
Replace with Gunicorn:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "900", "app:app"]
```

---

### ⚠️ ISSUE #6: Model Download Size Unknown
**Severity**: MEDIUM - May exceed container disk

**Dockerfile line 33-34**:
```dockerfile
RUN huggingface-cli download Wan-AI/Wan2.2-Animate-14B --local-dir /models/Wan2.2-Animate-14B
```

**Problems**:
1. Don't know actual model size (claimed 14B parameters)
2. May be 20-50GB compressed
3. Container disk set to 80GB (might not be enough)
4. Download takes hours and we never verified it completed successfully

**Solution Needed**:
Verify model downloaded correctly in Docker image

---

### ⚠️ ISSUE #7: S3 Credentials in Config File
**Severity**: MEDIUM - Security risk

**config.yaml** contains:
```yaml
s3_access_key: "AKIAQPFMTVPPQLCI6X3X"
s3_secret_key: "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"
```

**Problem**:
- Credentials are in plain text config file
- Config is not in Docker image
- Will fail when trying to upload to S3

**Solution Needed**:
Pass credentials via environment variables

---

### ⚠️ ISSUE #8: No Error Recovery in Make.com
**Severity**: LOW - User experience issue

**Current flow**:
- If processing fails, webhook sends error
- Make.com updates Status to "Failed"
- User has no way to retry

**Solution Needed**:
Add retry logic or manual retry button

---

## 5. FUNDAMENTAL ARCHITECTURE QUESTION

### The Big Decision: Serverless vs Pods

**Option A: Runpod Serverless** (What we chose)
- Pros: Only pay when processing, auto-scales
- Cons: Requires handler.py pattern, 45-60s cold start, complex

**Option B: Runpod Pods** (Traditional VMs)
- Pros: Flask server works as-is, always warm, simpler
- Cons: Always running = always paying, manual scaling

**Current Status**:
We built Flask server (Pods architecture) but deployed to Serverless endpoint (incompatible)

**Decision Needed**:
1. Rewrite for Serverless pattern, OR
2. Switch to Pods deployment

---

## 6. WHAT WE NEED TO FIX (Priority Order)

### Priority 1: CRITICAL - System Won't Work
1. ✅ Create proper Runpod handler OR switch to Pods
2. ✅ Fix API field name mapping (input.source_video_url → video_url)
3. ✅ Pass configuration to container
4. ✅ Verify Wan2.2 commands are correct
5. ✅ Test Docker image locally before deploying

### Priority 2: HIGH - Will Likely Fail
6. ⚠️ Verify model downloaded correctly in image
7. ⚠️ Add S3 credentials to container
8. ⚠️ Switch to Gunicorn for production

### Priority 3: MEDIUM - Should Fix
9. Add error logging to Runpod
10. Add retry mechanism
11. Add processing timeout safeguards

---

## 7. RECOMMENDED ACTION PLAN

### Immediate (Before Testing):
1. **Verify Wan2.2 Model**:
   - Check model downloaded in Docker image
   - Test commands work
   - Verify face-swap actually works

2. **Fix Architecture**:
   - EITHER: Rewrite app.py as Runpod handler
   - OR: Switch to Runpod Pods (easier)

3. **Fix Configuration**:
   - Add config to Docker image OR
   - Pass as environment variables

4. **Fix API Mapping**:
   - Update app.py to handle `input.source_video_url` format

### After Fixes (Testing):
5. Test Docker image locally
6. Test on Runpod with sample video
7. Test end-to-end from Airtable

---

## 8. THE REAL QUESTION

**Do we want Serverless or Pods?**

My recommendation: **Switch to Runpod Pods** because:
- Flask server already works
- Simpler architecture
- Faster (no cold start)
- Easier debugging
- Only downside: Costs ~$0.30/hour = $216/month if running 24/7
- Can manually start/stop when needed

**OR** stick with Serverless but rewrite everything.

What do you prefer?
