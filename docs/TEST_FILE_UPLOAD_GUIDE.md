# Test File Upload Guide - Getting Public URLs

You need publicly accessible URLs for testing the face swapper. Here are your options:

## OPTION 1: Use Your S3 Bucket (EASIEST for you)

You already have S3 bucket: `faceswap-outputs-kasparas`

### Quick Upload with Script

```bash
cd scripts

# Upload your test files
./upload_test_files.sh ~/Downloads/test-video.mp4 ~/Downloads/test-avatar.jpg

# Returns public URLs you can use immediately
```

### Manual AWS CLI Upload

```bash
# Install AWS CLI if needed
brew install awscli

# Configure AWS credentials (one-time setup)
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1 (or your bucket's region)
# Default output format: json

# Upload video
aws s3 cp ~/Downloads/test.mp4 s3://faceswap-outputs-kasparas/test-video.mp4 \
    --acl public-read

# Upload avatar
aws s3 cp ~/Downloads/avatar.jpg s3://faceswap-outputs-kasparas/test-avatar.jpg \
    --acl public-read

# Get public URLs:
# Video: https://faceswap-outputs-kasparas.s3.amazonaws.com/test-video.mp4
# Avatar: https://faceswap-outputs-kasparas.s3.amazonaws.com/test-avatar.jpg
```

### S3 Bucket Policy (if public-read doesn't work)

If you get permission errors, update bucket policy at:
https://s3.console.aws.amazon.com/s3/buckets/faceswap-outputs-kasparas?tab=permissions

Add this policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::faceswap-outputs-kasparas/*"
        }
    ]
}
```

---

## OPTION 2: Free/Easy Alternatives (No AWS Setup)

### A. Cloudflare R2 (FREE, S3-compatible)

1. Sign up: https://dash.cloudflare.com/sign-up
2. Create R2 bucket
3. Upload files via dashboard
4. Get public URLs

**Pros:** Free up to 10GB storage, S3-compatible
**Cons:** Requires Cloudflare account

### B. Imgur (Images Only - for avatar)

1. Go to: https://imgur.com/upload
2. Upload avatar image
3. Right-click → Copy image address
4. Get direct URL like: `https://i.imgur.com/xxxxx.jpg`

**Pros:** Super simple, no account needed
**Cons:** Images only (not videos)

### C. File.io (Temporary - Good for Testing)

```bash
# Upload video (expires after 1 download or 14 days)
curl -F "file=@~/Downloads/test.mp4" https://file.io

# Returns: {"success":true,"link":"https://file.io/xxxxx"}

# Upload avatar
curl -F "file=@~/Downloads/avatar.jpg" https://file.io
```

**Pros:** No signup, super fast
**Cons:** Files expire quickly

### D. Transfer.sh (Temporary)

```bash
# Upload and get URL
curl --upload-file ~/Downloads/test.mp4 https://transfer.sh/test.mp4

# Returns direct URL
```

**Pros:** Simple, no account
**Cons:** Files deleted after 14 days

### E. Dropbox Public Links

1. Upload to Dropbox
2. Right-click → Share → Create link
3. Change `?dl=0` to `?dl=1` in URL for direct link

**Example:**
- Shared: `https://www.dropbox.com/s/abc123/test.mp4?dl=0`
- Direct: `https://www.dropbox.com/s/abc123/test.mp4?dl=1`

### F. Google Drive Public Links

1. Upload to Google Drive
2. Right-click → Share → Anyone with link
3. Get file ID from share link
4. Use: `https://drive.google.com/uc?export=download&id=FILE_ID`

**Note:** Can be rate-limited for large files

---

## RECOMMENDED FOR YOU: Option 1 (Your S3 Bucket)

**Why:**
1. You already have the bucket
2. Already configured in your handler
3. Permanent URLs (don't expire)
4. Fast for testing
5. Same region as Runpod (probably)

**Steps:**
```bash
# 1. Install AWS CLI (if not installed)
brew install awscli

# 2. Configure credentials (one time)
aws configure

# 3. Use the upload script
cd scripts
./upload_test_files.sh ~/path/to/video.mp4 ~/path/to/avatar.jpg

# 4. Copy the URLs and test
./test_endpoint.sh "VIDEO_URL" "AVATAR_URL"
```

---

## Quick Test Files

If you don't have test files ready:

### Sample Video URLs (public domain):
```
https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4
https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

### Sample Avatar Images:
```
https://randomuser.me/api/portraits/men/1.jpg
https://randomuser.me/api/portraits/women/1.jpg
https://thispersondoesnotexist.com/ (refresh for new face)
```

---

## Testing Checklist

- [ ] Upload or find test video URL
- [ ] Upload or find test avatar URL
- [ ] Verify URLs are publicly accessible (test in browser)
- [ ] GitHub Actions build completed
- [ ] Runpod endpoint updated
- [ ] Ready to test!

---

## Need Help?

**AWS CLI not working?**
- Check credentials: `aws sts get-caller-identity`
- Check bucket access: `aws s3 ls s3://faceswap-outputs-kasparas`

**Files not public?**
- Add `--acl public-read` flag
- Or update bucket policy (see Option 1)

**Want simplest option?**
- Use sample URLs above for quick test
- Or use file.io for one-time upload
