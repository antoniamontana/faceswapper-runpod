# Pre-Deployment Checklist
## Face Swapper Runpod Deployment

**Last Updated:** 2025-11-04
**Status:** NOT READY - 8 critical blockers

---

## CRITICAL BLOCKERS (Must be completed)

- [ ] **1. Docker Image Built and Pushed**
  - [ ] Image built: `docker build -t kaspamontana/ugc-faceswapper:v2 -f docker/Dockerfile .`
  - [ ] Image pushed: `docker push kaspamontana/ugc-faceswapper:v2`
  - [ ] Verified on Docker Hub: `curl -s "https://hub.docker.com/v2/repositories/kaspamontana/ugc-faceswapper/tags/v2"`
  - [ ] Image size reasonable (15-25GB expected)

- [ ] **2. Credentials Secured**
  - [ ] AWS IAM user rotated (new access key created, old deleted)
  - [ ] Runpod API key regenerated
  - [ ] Airtable API token regenerated
  - [ ] `config.yaml` added to `.gitignore`
  - [ ] All credentials removed from git history (if git repo)
  - [ ] Scripts updated with new credentials

- [ ] **3. S3 Bucket Verified**
  - [ ] Bucket exists: `aws s3 ls s3://faceswap-outputs-kasparas/`
  - [ ] Credentials have PutObject permission
  - [ ] Credentials have PutObjectAcl permission
  - [ ] Test upload successful
  - [ ] Public-read ACL allowed

- [ ] **4. Wan2.2-Animate Integration Tested**
  - [ ] Docker container runs: `docker run -it --gpus all kaspamontana/ugc-faceswapper:v2 /bin/bash`
  - [ ] Model downloaded: `ls /models/Wan2.2-Animate-14B/`
  - [ ] Wan2.2 repo exists: `ls /app/Wan2.2/`
  - [ ] Preprocessing script exists: `ls /app/Wan2.2/wan/modules/animate/preprocess/preprocess_data.py`
  - [ ] Generation script exists: `ls /app/Wan2.2/generate.py`
  - [ ] Face-swap tested on single segment
  - [ ] Output video produced

- [ ] **5. End-to-End Test Created and Passed**
  - [ ] Test file created: `tests/test_e2e.py`
  - [ ] Test uses real video URL (30 seconds)
  - [ ] Test uses real avatar image URL
  - [ ] Test calls Runpod endpoint
  - [ ] Test waits for completion
  - [ ] Test verifies S3 output URL
  - [ ] Test verifies webhook delivery
  - [ ] Test PASSED

- [ ] **6. Performance Benchmarked**
  - [ ] Single segment processing time measured
  - [ ] Full pipeline processing time measured
  - [ ] Total time < 900s (15 minute timeout)
  - [ ] Memory usage acceptable
  - [ ] GPU utilization monitored

- [ ] **7. Error Recovery Tested**
  - [ ] Invalid video URL handled
  - [ ] Invalid avatar URL handled
  - [ ] S3 upload failure handled
  - [ ] Temp files cleaned up on failure
  - [ ] Webhook sent on failure
  - [ ] Error messages are descriptive

- [ ] **8. Health Check Added**
  - [ ] Health check endpoint in handler.py
  - [ ] Returns config loaded status
  - [ ] Returns model path status
  - [ ] Returns ffmpeg availability
  - [ ] Returns S3 configuration status

---

## DEPLOYMENT STEPS

- [ ] **9. Update Runpod Endpoint**
  - [ ] Run: `./scripts/update_endpoint.sh`
  - [ ] Verify GraphQL response shows success
  - [ ] Wait 2-3 minutes for endpoint update

- [ ] **10. Verify Endpoint Health**
  - [ ] Call health check endpoint
  - [ ] Verify all components healthy
  - [ ] Check worker logs for errors

- [ ] **11. Run Test Job**
  - [ ] Run: `./scripts/test_endpoint.sh <video_url> <avatar_url>`
  - [ ] Monitor job status
  - [ ] Verify job completes
  - [ ] Check S3 for output video
  - [ ] Verify webhook received

- [ ] **12. Production Validation**
  - [ ] Send real job through Make.com
  - [ ] Monitor processing progress
  - [ ] Verify output video quality
  - [ ] Verify face-swap quality
  - [ ] Verify webhook delivery

---

## POST-DEPLOYMENT MONITORING

- [ ] **13. Monitor First 10 Jobs**
  - [ ] Check success rate
  - [ ] Monitor processing times
  - [ ] Check for errors in logs
  - [ ] Verify S3 uploads
  - [ ] Verify webhook delivery

- [ ] **14. Performance Metrics**
  - [ ] Average processing time
  - [ ] Success rate
  - [ ] Error rate
  - [ ] S3 upload success rate
  - [ ] Webhook delivery rate

---

## ROLLBACK PLAN

- [ ] **15. Rollback Procedure (if needed)**
  - [ ] Document current working state
  - [ ] Keep old endpoint configuration
  - [ ] Keep old Docker image tag
  - [ ] Test rollback before deployment

---

## VALIDATION SUMMARY

**Critical Blockers:** 8
**Deployment Steps:** 4
**Monitoring Tasks:** 2
**Rollback Plan:** 1

**Total Tasks:** 15
**Completed:** 0
**Remaining:** 15

**PROGRESS: 0%**

**DEPLOYMENT DECISION: NO-GO**

---

## QUICK COMMANDS

### Build and Push Docker Image
```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/docker"
docker build -t kaspamontana/ugc-faceswapper:v2 -f Dockerfile .
docker login
docker push kaspamontana/ugc-faceswapper:v2
```

### Verify Docker Image
```bash
curl -s "https://hub.docker.com/v2/repositories/kaspamontana/ugc-faceswapper/tags/v2" | python3 -m json.tool
```

### Test S3 Upload
```bash
aws s3 cp /tmp/test.mp4 s3://faceswap-outputs-kasparas/outputs/test.mp4 --acl public-read --region us-east-1
```

### Update Runpod Endpoint
```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/scripts"
./update_endpoint.sh
```

### Test Endpoint
```bash
cd "/Users/kasparas/Library/Mobile Documents/com~apple~CloudDocs/dev/2025/faceswapper-20251030/scripts"
./test_endpoint.sh "https://example.com/video.mp4" "https://example.com/avatar.jpg"
```

### Check Job Status
```bash
curl -X GET "https://api.runpod.ai/v2/eaj61xejeec2iw/status/JOB_ID" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk"
```

---

## NEXT STEPS

1. **Start with credentials** - This is a security issue and must be fixed first
2. **Build Docker image** - Nothing works without this
3. **Test locally** - Verify Wan2.2 integration before deploying
4. **Create E2E test** - Validate end-to-end before production
5. **Deploy to Runpod** - Only after all tests pass
6. **Monitor closely** - Watch first jobs carefully

**ESTIMATED TIME TO PRODUCTION: 11-16 hours**
