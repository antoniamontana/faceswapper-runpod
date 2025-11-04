#!/bin/bash
# Upload test files to S3 and get public URLs

BUCKET="faceswap-outputs-kasparas"
REGION="us-east-1"  # Update if your bucket is in a different region

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not installed"
    echo "Install with: brew install awscli"
    exit 1
fi

# Check if files provided
if [ $# -lt 2 ]; then
    echo "Usage: ./upload_test_files.sh <video_file> <avatar_image>"
    echo "Example: ./upload_test_files.sh ~/Downloads/test.mp4 ~/Downloads/avatar.jpg"
    exit 1
fi

VIDEO_FILE="$1"
AVATAR_FILE="$2"

# Check files exist
if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ Video file not found: $VIDEO_FILE"
    exit 1
fi

if [ ! -f "$AVATAR_FILE" ]; then
    echo "❌ Avatar file not found: $AVATAR_FILE"
    exit 1
fi

# Generate unique filenames
VIDEO_NAME="test-video-$(date +%s).mp4"
AVATAR_NAME="test-avatar-$(date +%s).jpg"

echo "📤 Uploading files to S3..."
echo ""

# Upload video with public-read ACL
echo "Uploading video: $VIDEO_FILE"
aws s3 cp "$VIDEO_FILE" "s3://$BUCKET/$VIDEO_NAME" \
    --acl public-read \
    --content-type "video/mp4"

VIDEO_URL="https://$BUCKET.s3.amazonaws.com/$VIDEO_NAME"

# Upload avatar with public-read ACL
echo "Uploading avatar: $AVATAR_FILE"
aws s3 cp "$AVATAR_FILE" "s3://$BUCKET/$AVATAR_NAME" \
    --acl public-read \
    --content-type "image/jpeg"

AVATAR_URL="https://$BUCKET.s3.amazonaws.com/$AVATAR_NAME"

echo ""
echo "✅ Upload complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📹 Video URL:"
echo "$VIDEO_URL"
echo ""
echo "🖼️  Avatar URL:"
echo "$AVATAR_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Test with:"
echo "./test_endpoint.sh \"$VIDEO_URL\" \"$AVATAR_URL\""
echo ""
