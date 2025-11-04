# CRITICAL DEPLOYMENT BLOCKERS

**DEPLOYMENT STATUS: NO-GO - 8 CRITICAL BLOCKERS**

---

## IMMEDIATE ACTION REQUIRED

### BLOCKER 1: DOCKER IMAGE DOES NOT EXIST
**Severity:** CRITICAL
**Impact:** Runpod endpoint will fail to start
**Evidence:** `curl -s "https://hub.docker.com/v2/repositories/kaspamontana/ugc-faceswapper/tags/v2"` returns 404

**ACTION REQUIRED:**
```bash
# 1. Build the image (this will take 30-60 minutes)
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/docker"
docker build -t kaspamontana/ugc-faceswapper:v2 -f Dockerfile .

# 2. Push to Docker Hub
docker login
docker push kaspamontana/ugc-faceswapper:v2

# 3. Verify it exists
curl -s "https://hub.docker.com/v2/repositories/kaspamontana/ugc-faceswapper/tags/v2"
```

**ESTIMATED TIME:** 1-2 hours

---

### BLOCKER 2: EXPOSED CREDENTIALS IN 24 FILES
**Severity:** CRITICAL SECURITY
**Impact:** AWS keys, Runpod API keys, Airtable keys are publicly exposed
**Evidence:** Grep found hardcoded credentials in 24 files

**COMPROMISED CREDENTIALS:**
```
AWS Access Key: AKIAQPFMTVPPQLCI6X3X
AWS Secret Key: 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
Runpod API Key: rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk
Airtable API Key: patlwJxGENTnKmGeF.48b68649086330d63c1496993b1fd91697eb7f41bc5887d08a00e45c63845395
```

**ACTION REQUIRED:**
1. IMMEDIATELY rotate all credentials:
   - AWS: Create new IAM user, delete old one
   - Runpod: Generate new API key
   - Airtable: Regenerate API token
2. Add to .gitignore:
   ```
   config.yaml
   docker/config.yaml
   config/config.yaml
   .env
   *.env
   ```
3. If git repository exists, remove from history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch docker/config.yaml" \
     --prune-empty --tag-name-filter cat -- --all
   ```

**ESTIMATED TIME:** 1 hour

---

### BLOCKER 3: NO TESTS EXIST
**Severity:** CRITICAL
**Impact:** Cannot validate functionality, face-swap may fail in production
**Evidence:** `find . -name "*test*.py"` returns no results

**ACTION REQUIRED:**
Create minimum viable tests:

1. **End-to-End Test:**
```python
# tests/test_e2e.py
import requests
import time

def test_full_pipeline():
    """Test complete face-swap pipeline with real video"""

    # Use public test URLs
    payload = {
        "input": {
            "record_id": "test_e2e_001",
            "source_video_url": "https://example.com/test-30s-video.mp4",
            "avatar_image_url": "https://example.com/test-face.jpg",
            "webhook_url": "https://webhook.site/your-test-url"
        }
    }

    # Call endpoint
    response = requests.post(
        "https://api.runpod.ai/v2/eaj61xejeec2iw/run",
        headers={"Authorization": "Bearer YOUR_KEY"},
        json=payload
    )

    assert response.status_code == 200
    job_id = response.json()["id"]

    # Poll for completion (max 15 minutes)
    for i in range(90):  # 90 * 10s = 15 minutes
        status = requests.get(
            f"https://api.runpod.ai/v2/eaj61xejeec2iw/status/{job_id}",
            headers={"Authorization": "Bearer YOUR_KEY"}
        ).json()

        if status["status"] == "COMPLETED":
            assert "output_url" in status["output"]
            assert status["output"]["status"] == "success"
            print(f"✅ Output URL: {status['output']['output_url']}")
            return

        time.sleep(10)

    raise TimeoutError("Job did not complete in 15 minutes")
```

2. **S3 Upload Test:**
```python
# tests/test_s3.py
import boto3
from process import upload_to_s3

def test_s3_upload():
    """Test S3 upload with real credentials"""

    # Create test file
    with open('/tmp/test_video.mp4', 'wb') as f:
        f.write(b'test data')

    config = {
        's3_bucket': 'faceswap-outputs-kasparas',
        's3_region': 'us-east-1',
        's3_access_key': 'YOUR_KEY',
        's3_secret_key': 'YOUR_SECRET',
        's3_output_prefix': 'test-outputs/'
    }

    url = upload_to_s3('/tmp/test_video.mp4', 'test_001', config)

    assert url is not None
    assert 's3.us-east-1.amazonaws.com' in url

    # Verify file is accessible
    import requests
    response = requests.head(url)
    assert response.status_code == 200
```

**ESTIMATED TIME:** 4-6 hours

---

### BLOCKER 4: WAN2.2-ANIMATE INTEGRATION UNVERIFIED
**Severity:** CRITICAL
**Impact:** Face-swap may fail, unknown if model paths are correct
**Evidence:** No tests, Dockerfile downloads model but doesn't verify

**ACTION REQUIRED:**

1. **Verify model download:**
```bash
# Run Docker container interactively
docker run -it --gpus all kaspamontana/ugc-faceswapper:v2 /bin/bash

# Inside container, check:
ls -lh /models/Wan2.2-Animate-14B/
ls -lh /app/Wan2.2/
python3 -c "import sys; sys.path.append('/app/Wan2.2'); import wan"
```

2. **Test face-swap on single segment:**
```bash
# Inside container
cd /app
python3 << 'EOF'
from process import face_swap_segment
import requests

# Download test files
video_url = "https://example.com/test-segment.mp4"
avatar_url = "https://example.com/test-face.jpg"

with open('/tmp/test_video.mp4', 'wb') as f:
    f.write(requests.get(video_url).content)

with open('/tmp/test_avatar.jpg', 'wb') as f:
    f.write(requests.get(avatar_url).content)

# Test face-swap
result = face_swap_segment(
    '/tmp/test_video.mp4',
    '/tmp/test_avatar.jpg',
    {'model_path': '/models/wan2.2-animate'}
)

print(f"Result: {result}")
assert result is not None
EOF
```

**ESTIMATED TIME:** 2-3 hours

---

### BLOCKER 5: S3 BUCKET ACCESSIBILITY UNKNOWN
**Severity:** CRITICAL
**Impact:** Video uploads will fail, webhook will report failure
**Evidence:** Cannot test S3 from local environment

**ACTION REQUIRED:**

1. **Verify bucket exists:**
```bash
aws s3 ls s3://faceswap-outputs-kasparas/ --region us-east-1
```

2. **Test upload from Runpod container:**
```python
import boto3

s3 = boto3.client(
    's3',
    aws_access_key_id='AKIAQPFMTVPPQLCI6X3X',
    aws_secret_access_key='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',
    region_name='us-east-1'
)

# Test upload
with open('/tmp/test.mp4', 'wb') as f:
    f.write(b'test')

s3.upload_file(
    '/tmp/test.mp4',
    'faceswap-outputs-kasparas',
    'outputs/test.mp4',
    ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'}
)

# Verify URL
url = "https://faceswap-outputs-kasparas.s3.us-east-1.amazonaws.com/outputs/test.mp4"
print(f"Test URL: {url}")
```

3. **Verify IAM permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::faceswap-outputs-kasparas/outputs/*"
        }
    ]
}
```

**ESTIMATED TIME:** 30 minutes

---

### BLOCKER 6: NO PROCESSING TIME VALIDATION
**Severity:** HIGH
**Impact:** May timeout (900s limit), unknown performance
**Evidence:** No benchmarks exist

**ACTION REQUIRED:**

1. **Benchmark face-swap time:**
```python
import time

segments = [
    "5-second video",
    "10-second video",
    "15-second video"
]

for duration in [5, 10, 15]:
    start = time.time()

    # Face-swap segment
    result = face_swap_segment(
        f'/tmp/test_{duration}s.mp4',
        '/tmp/avatar.jpg',
        config
    )

    elapsed = time.time() - start
    print(f"{duration}s video: {elapsed:.1f}s processing time")

    # Check if within timeout
    estimated_total = elapsed * 4  # 4 operations per job
    print(f"Estimated total for full job: {estimated_total:.1f}s")
    assert estimated_total < 900, "Will timeout!"
```

2. **Expected timeline:**
```
Download video + avatar:     10-30s
Segment video:               5-10s
Face-swap segment 1:         60-180s (UNKNOWN)
Face-swap segment 3:         60-180s (UNKNOWN)
Stitch segments:             10-20s
Upload to S3:                20-60s
Send webhook:                1-2s

TOTAL: 166-462s (2.7-7.7 minutes)
TIMEOUT: 900s (15 minutes)
```

**ESTIMATED TIME:** 1-2 hours

---

### BLOCKER 7: NO ERROR RECOVERY TESTING
**Severity:** HIGH
**Impact:** Failed jobs may leave temp files, partial uploads
**Evidence:** Cleanup only happens on success or known failure

**ACTION REQUIRED:**

Test error scenarios:

1. **Invalid video URL:**
```python
result = process_video_job(
    record_id="test_invalid_url",
    video_url="https://example.com/nonexistent.mp4",
    avatar_url="https://example.com/avatar.jpg",
    config=CONFIG
)

assert result['status'] == 'failed'
assert 'error' in result
# Verify temp files cleaned up
assert not os.path.exists('/tmp/faceswap_*')
```

2. **Video download timeout:**
```python
# Test with very large file
result = process_video_job(
    record_id="test_timeout",
    video_url="https://example.com/huge-video.mp4",  # 5GB file
    avatar_url="https://example.com/avatar.jpg",
    config=CONFIG
)

assert result['status'] == 'failed'
```

3. **S3 upload failure:**
```python
# Use invalid credentials
bad_config = CONFIG.copy()
bad_config['storage']['s3_access_key'] = 'INVALID'

result = process_video_job(
    record_id="test_s3_fail",
    video_url=valid_video,
    avatar_url=valid_avatar,
    config=bad_config
)

assert result['status'] == 'failed'
assert 'S3 upload failed' in result['error']
```

**ESTIMATED TIME:** 2-3 hours

---

### BLOCKER 8: NO RUNPOD HEALTH CHECK
**Severity:** MEDIUM
**Impact:** Cannot verify deployment success
**Evidence:** No health endpoint in handler.py

**ACTION REQUIRED:**

Add health check to handler.py:

```python
def handler(event):
    """Runpod serverless handler"""

    # Health check
    if event.get("input", {}).get("health_check"):
        return {
            "status": "healthy",
            "config_loaded": CONFIG is not None,
            "model_path": os.path.exists("/models/Wan2.2-Animate-14B"),
            "ffmpeg": os.system("which ffmpeg") == 0,
            "s3_configured": CONFIG.get('storage', {}).get('s3_bucket') is not None
        }

    # ... rest of handler
```

Test health check:
```bash
curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/run" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"health_check": true}}'
```

**ESTIMATED TIME:** 30 minutes

---

## SUMMARY OF REQUIRED ACTIONS

| Blocker | Action | Time | Priority |
|---------|--------|------|----------|
| 1. Docker image | Build and push | 1-2h | P0 |
| 2. Credentials | Rotate all secrets | 1h | P0 |
| 3. Tests | Create E2E test | 4-6h | P0 |
| 4. Wan2.2 | Verify integration | 2-3h | P0 |
| 5. S3 | Test accessibility | 30m | P0 |
| 6. Performance | Benchmark timing | 1-2h | P1 |
| 7. Error recovery | Test failures | 2-3h | P1 |
| 8. Health check | Add endpoint | 30m | P2 |

**TOTAL TIME TO RESOLVE: 12-18 hours**

---

## DEPLOYMENT WORKFLOW

### Phase 1: CRITICAL (Must complete before deployment)
1. Rotate all credentials (1h)
2. Build and push Docker image (1-2h)
3. Verify S3 bucket (30m)
4. Add health check (30m)
5. **Total: 3-4 hours**

### Phase 2: VALIDATION (Must complete before production)
1. Test Wan2.2 integration locally (2-3h)
2. Create E2E test (4-6h)
3. Run performance benchmarks (1-2h)
4. **Total: 7-11 hours**

### Phase 3: DEPLOYMENT (Can proceed after Phase 1+2)
1. Update Runpod endpoint (5m)
2. Run health check (5m)
3. Execute E2E test on Runpod (15m)
4. Monitor first production job (30m)
5. **Total: 1 hour**

**MINIMUM TIME TO PRODUCTION: 11-16 hours**

---

## FINAL RECOMMENDATION

**DO NOT DEPLOY** until:
1. Docker image exists on Docker Hub
2. All credentials rotated and secured
3. At least one successful E2E test completed
4. S3 upload verified
5. Wan2.2 face-swap verified

**CURRENT STATUS: 0/5 requirements met**
