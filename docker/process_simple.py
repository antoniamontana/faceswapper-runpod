"""
Simplified Face Swapper - Single Video Processing
No segmentation, no stitching - processes entire video with Wan2.2 in one pass
"""

import os
import requests
import logging
import subprocess
import tempfile
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import traceback

logger = logging.getLogger(__name__)


# ============================================
# HELPER FUNCTIONS (Reused from process.py)
# ============================================

def download_file(url, output_path):
    """Download file from URL to local path"""
    try:
        logger.info(f"Downloading from {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Downloaded to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def upload_to_s3(file_path, record_id, s3_config):
    """Upload video to S3 and return public URL"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=s3_config['s3_access_key'],
            aws_secret_access_key=s3_config['s3_secret_key'],
            region_name=s3_config['s3_region']
        )

        bucket = s3_config['s3_bucket']
        key = f"{s3_config['s3_output_prefix']}{record_id}.mp4"

        logger.info(f"Uploading to S3: {bucket}/{key}")

        s3_client.upload_file(
            file_path,
            bucket,
            key,
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'}
        )

        url = f"https://{bucket}.s3.{s3_config['s3_region']}.amazonaws.com/{key}"
        logger.info(f"Uploaded successfully: {url}")

        return url

    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        return None


def send_webhook(webhook_url, payload):
    """Send completion webhook to Make.com"""
    try:
        logger.info(f"Sending webhook to {webhook_url}")
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Webhook sent successfully")
        return True
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return False


def cleanup_temp_files(temp_dir):
    """Delete temporary processing files"""
    try:
        import shutil
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temp directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")


# ============================================
# NEW SIMPLIFIED FACE-SWAP LOGIC
# ============================================

def face_swap_full_video(video_path, avatar_path, job_id, model_path):
    """
    Use Wan2.2-Animate to face-swap the ENTIRE video in one pass

    This replaces the complex segmentation/stitching logic with a single
    face-swap operation on the complete video.

    Args:
        video_path: Path to input video
        avatar_path: Path to avatar image
        job_id: Unique job identifier
        model_path: Path to Wan2.2 model (from env var)

    Returns:
        Path to face-swapped video, or None if failed
    """
    try:
        logger.info(f"Starting Wan2.2 face-swap for job {job_id}")
        logger.info(f"Video: {video_path}")
        logger.info(f"Avatar: {avatar_path}")
        logger.info(f"Model: {model_path}")

        # Create processing directory
        process_dir = f"/tmp/wan_process_{job_id}"
        os.makedirs(process_dir, exist_ok=True)
        logger.info(f"Processing directory: {process_dir}")

        # Step 1: Preprocessing with Wan2.2
        logger.info("Step 1/2: Running Wan2.2 preprocessing...")
        preprocess_cmd = [
            'python3', '/app/Wan2.2/wan/modules/animate/preprocess/preprocess_data.py',
            '--ckpt_path', f'{model_path}/process_checkpoint',
            '--video_path', video_path,
            '--refer_path', avatar_path,
            '--save_path', process_dir,
            '--resolution_area', '1280', '720',
            '--iterations', '3',
            '--k', '7',
            '--w_len', '1',
            '--h_len', '1',
            '--replace_flag'  # CRITICAL: Enables face replacement mode
        ]

        logger.info(f"Running: {' '.join(preprocess_cmd)}")
        result = subprocess.run(
            preprocess_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for preprocessing
        )

        if result.returncode != 0:
            logger.error(f"Preprocessing failed with code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            logger.error(f"STDOUT: {result.stdout}")
            raise Exception(f"Wan2.2 preprocessing failed: {result.stderr}")

        logger.info("Preprocessing completed successfully")

        # Step 2: Generation (face-swap)
        logger.info("Step 2/2: Running Wan2.2 generation (face-swap)...")
        generate_cmd = [
            'python3', '/app/Wan2.2/generate.py',
            '--task', 'animate-14B',
            '--ckpt_dir', model_path,
            '--src_root_path', process_dir,
            '--refer_num', '1',
            '--replace_flag',  # Face replacement mode
            '--use_relighting_lora'  # Better lighting match
        ]

        logger.info(f"Running: {' '.join(generate_cmd)}")
        result = subprocess.run(
            generate_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for generation
        )

        if result.returncode != 0:
            logger.error(f"Generation failed with code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            logger.error(f"STDOUT: {result.stdout}")
            raise Exception(f"Wan2.2 generation failed: {result.stderr}")

        logger.info("Generation completed successfully")

        # Step 3: Find output video
        logger.info("Locating generated output video...")
        output_video = None

        # Look for output video (Wan2.2 typically creates files with 'output' in name)
        for file in os.listdir(process_dir):
            if file.endswith('.mp4') and 'output' in file.lower():
                output_video = os.path.join(process_dir, file)
                logger.info(f"Found output video: {output_video}")
                break

        # Fallback: Find any new mp4 that's not the input
        if not output_video:
            logger.warning("No 'output' file found, searching for any new mp4...")
            for file in os.listdir(process_dir):
                if file.endswith('.mp4'):
                    potential_output = os.path.join(process_dir, file)
                    if potential_output != video_path:
                        output_video = potential_output
                        logger.info(f"Found video file: {output_video}")
                        break

        if not output_video or not os.path.exists(output_video):
            # List directory contents for debugging
            logger.error(f"Directory contents: {os.listdir(process_dir)}")
            raise Exception("Generated output video not found in processing directory")

        # Verify output video is valid
        if os.path.getsize(output_video) == 0:
            raise Exception("Generated output video is empty (0 bytes)")

        logger.info(f"Face-swap complete! Output: {output_video} ({os.path.getsize(output_video)} bytes)")
        return output_video

    except subprocess.TimeoutExpired:
        logger.error("Wan2.2 processing timed out")
        return None
    except Exception as e:
        logger.error(f"Face-swap failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


# ============================================
# MAIN PROCESSING PIPELINE (Simplified)
# ============================================

def process_single_video(job_id, video_url, avatar_url, config=None, webhook_url=None):
    """
    Simplified processing pipeline - no segmentation, no stitching

    Flow:
    1. Download video and avatar
    2. Face-swap ENTIRE video with Wan2.2 (one pass)
    3. Upload result to S3
    4. Send webhook notification
    5. Cleanup

    Args:
        job_id: Unique job identifier (e.g., record_id or job_123)
        video_url: URL to source video
        avatar_url: URL to avatar image
        config: Configuration dict (optional, uses env vars as fallback)
        webhook_url: URL for completion webhook (optional)

    Returns:
        {
            'status': 'success' | 'failed',
            'output_url': 'https://...' (if success),
            'error': 'error message' (if failed)
        }
    """
    temp_dir = None

    try:
        logger.info(f"=" * 60)
        logger.info(f"Starting processing for job: {job_id}")
        logger.info(f"Video URL: {video_url}")
        logger.info(f"Avatar URL: {avatar_url}")
        logger.info(f"=" * 60)

        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp(prefix=f'faceswap_{job_id}_')
        logger.info(f"Temp directory: {temp_dir}")

        # Get configuration (use env vars if config not provided)
        if config:
            s3_config = config.get('storage', {})
            model_path = config.get('processing', {}).get('model_path')
        else:
            # Fallback to environment variables
            s3_config = {
                's3_access_key': os.environ.get('AWS_ACCESS_KEY_ID'),
                's3_secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
                's3_region': os.environ.get('AWS_REGION', 'eu-north-1'),
                's3_bucket': os.environ.get('S3_BUCKET', 'faceswap-outputs-kasparas'),
                's3_output_prefix': os.environ.get('S3_OUTPUT_PREFIX', 'outputs/')
            }
            model_path = os.environ.get('MODEL_PATH', '/runpod-volume/models/Wan2.2-Animate-14B')

        logger.info(f"S3 Bucket: {s3_config['s3_bucket']}")
        logger.info(f"S3 Region: {s3_config['s3_region']}")
        logger.info(f"Model Path: {model_path}")

        # Step 1: Download inputs
        logger.info("Step 1/4: Downloading inputs...")
        video_path = os.path.join(temp_dir, 'input_video.mp4')
        avatar_path = os.path.join(temp_dir, 'avatar.png')

        if not download_file(video_url, video_path):
            raise Exception("Failed to download video")

        if not download_file(avatar_url, avatar_path):
            raise Exception("Failed to download avatar")

        logger.info("Downloads complete")

        # Step 2: Face-swap ENTIRE video (no segmentation!)
        logger.info("Step 2/4: Face-swapping entire video...")
        output_path = face_swap_full_video(
            video_path=video_path,
            avatar_path=avatar_path,
            job_id=job_id,
            model_path=model_path
        )

        if not output_path:
            raise Exception("Face-swap processing failed")

        logger.info(f"Face-swap complete: {output_path}")

        # Step 3: Upload to S3
        logger.info("Step 3/4: Uploading to S3...")
        output_url = upload_to_s3(output_path, job_id, s3_config)

        if not output_url:
            raise Exception("S3 upload failed")

        logger.info(f"Upload complete: {output_url}")

        # Step 4: Send success webhook
        result = {
            'status': 'Complete',
            'record_id': job_id,
            'output_url': output_url,
            'error_message': ''
        }

        if webhook_url:
            logger.info("Step 4/4: Sending webhook notification...")
            send_webhook(webhook_url, result)

        # Cleanup
        cleanup_temp_files(temp_dir)

        logger.info(f"=" * 60)
        logger.info(f"SUCCESS! Job {job_id} completed")
        logger.info(f"Output URL: {output_url}")
        logger.info(f"=" * 60)

        return {
            'status': 'success',
            'output_url': output_url
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"=" * 60)
        logger.error(f"FAILED! Job {job_id} error: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"=" * 60)

        # Send failure webhook
        result = {
            'status': '🚩 Failed',
            'record_id': job_id,
            'output_url': '',
            'error_message': error_msg
        }

        if webhook_url:
            send_webhook(webhook_url, result)

        # Cleanup on failure
        if temp_dir:
            cleanup_temp_files(temp_dir)

        return {
            'status': 'failed',
            'error': error_msg
        }
