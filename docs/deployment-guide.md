# Face Swapper Runpod Deployment Guide

## Current Deployment Status

**Image:** kaspamontana/ugc-faceswapper:v2 (67.7GB)
**Runpod Endpoint:** eaj61xejeec2iw
**API Key:** rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk
**S3 Bucket:** faceswap-outputs-kasparas
**Webhook:** https://hook.eu2.make.com/nckpkeky1n2utqu5mp4lu48ikfgxkovy

## Deployment Steps

### 1. Push Docker Image
```bash
# Already running in background
/Applications/Docker.app/Contents/Resources/bin/docker push kaspamontana/ugc-faceswapper:v2
```

Monitor progress with background bash ID: 619b9a

### 2. Update Runpod Endpoint
```bash
cd scripts
./update_endpoint.sh
```

Or manually:
```bash
curl -X POST "https://api.runpod.ai/v2/eaj61xejeec2iw/update" \
  -H "Authorization: Bearer rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk" \
  -H "Content-Type: application/json" \
  -d '{"imageName": "kaspamontana/ugc-faceswapper:v2"}'
```

### 3. Test with Sample Video
```bash
cd scripts
./test_endpoint.sh "https://your-video-url.mp4" "https://your-avatar-url.jpg"
```

This returns a job ID. Save it for status checking.

### 4. Check Job Status
```bash
cd scripts
./check_status.sh <job_id_from_step_3>
```

### 5. Monitor Results

**S3 Bucket:** Check `faceswap-outputs-kasparas` for output video
**Webhook:** Make.com will receive completion notification

## Handler Configuration

The Runpod handler (`docker/handler.py`) expects:

```json
{
  "input": {
    "record_id": "unique_id",
    "source_video_url": "https://...",
    "avatar_image_url": "https://...",
    "webhook_url": "https://hook.eu2.make.com/..."
  }
}
```

## Troubleshooting

### Docker Push Issues
- Check background process: `BashOutput` tool with ID 619b9a
- Verify WiFi connection stability
- Check Docker Hub login: `docker login`

### Runpod Issues
- Verify endpoint is active in Runpod dashboard
- Check budget remaining ($10 currently)
- Review handler logs in Runpod console

### Video Processing Issues
- Check S3 permissions
- Verify video URL is publicly accessible
- Check Make.com webhook logs

## Budget Management

Current budget: $10
Estimated cost per video: ~$0.10-0.50 (depending on length)
Expected capacity: 20-100 videos

Monitor spending in Runpod dashboard.
