"""
UGC Face Swapper V1 MVP - Video Processing Logic
Handles video segmentation, face-swapping, and upload
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

def segment_video(video_path, segments_config):
    """
    Segment video into 4 parts using FFmpeg
    Returns list of segment file paths
    """
    try:
        segments = []
        video_dir = Path(video_path).parent

        # Extract each segment using FFmpeg
        segment_configs = [
            ('swap_1', segments_config['swap_1_start'], segments_config['swap_1_end']),
            ('original_1', segments_config['original_1_start'], segments_config['original_1_end']),
            ('swap_2', segments_config['swap_2_start'], segments_config['swap_2_end']),
            ('original_2', segments_config['original_2_start'], segments_config['original_2_end'])
        ]

        for name, start, end in segment_configs:
            duration = end - start
            output_path = video_dir / f"segment_{name}.mp4"

            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-ss', str(start),
                '-t', str(duration),
                '-c', 'copy',  # Copy without re-encoding for speed
                '-y',  # Overwrite output
                str(output_path)
            ]

            logger.info(f"Extracting segment {name} ({start}s - {end}s)")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None

            segments.append(str(output_path))

        logger.info(f"Video segmented into {len(segments)} parts")
        return segments

    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
        return None

def face_swap_segment(segment_path, avatar_path, model_config):
    """
    Perform face-swap on a video segment using Wan2.2-Animate in replacement mode

    This uses a 2-step process:
    1. Preprocessing: prepare video and avatar image
    2. Generation: run the face-swap model
    """
    try:
        logger.info(f"Face-swapping segment: {segment_path} with avatar: {avatar_path}")

        output_path = segment_path.replace('.mp4', '_swapped.mp4')
        temp_process_dir = f"/tmp/processing/wan_process_{os.path.basename(segment_path)}"
        os.makedirs(temp_process_dir, exist_ok=True)

        # Step 1: Preprocessing
        logger.info("Running Wan2.2-Animate preprocessing...")
        preprocess_cmd = [
            'python3', '/app/Wan2.2/wan/modules/animate/preprocess/preprocess_data.py',
            '--ckpt_path', '/models/Wan2.2-Animate-14B/process_checkpoint',
            '--video_path', segment_path,
            '--refer_path', avatar_path,
            '--save_path', temp_process_dir,
            '--resolution_area', '1280', '720',
            '--iterations', '3',
            '--k', '7',
            '--w_len', '1',
            '--h_len', '1',
            '--replace_flag'
        ]

        result = subprocess.run(preprocess_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise Exception(f"Preprocessing failed: {result.stderr}")

        logger.info("Preprocessing complete")

        # Step 2: Generation (face-swap)
        logger.info("Running Wan2.2-Animate generation...")
        generate_cmd = [
            'python3', '/app/Wan2.2/generate.py',
            '--task', 'animate-14B',
            '--ckpt_dir', '/models/Wan2.2-Animate-14B/',
            '--src_root_path', temp_process_dir,
            '--refert_num', '1',
            '--replace_flag',
            '--use_relighting_lora'
        ]

        result = subprocess.run(generate_cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise Exception(f"Generation failed: {result.stderr}")

        logger.info("Generation complete")

        # Find and move output video
        # Wan2.2 typically saves output in the process directory
        generated_video = None
        for file in os.listdir(temp_process_dir):
            if file.endswith('.mp4') and 'output' in file.lower():
                generated_video = os.path.join(temp_process_dir, file)
                break

        if not generated_video or not os.path.exists(generated_video):
            # Fallback: look for any new mp4 that's not the input
            for file in os.listdir(temp_process_dir):
                if file.endswith('.mp4'):
                    potential_output = os.path.join(temp_process_dir, file)
                    if potential_output != segment_path:
                        generated_video = potential_output
                        break

        if not generated_video:
            raise Exception("Could not find generated output video")

        # Move output to expected location
        import shutil
        shutil.move(generated_video, output_path)
        logger.info(f"Face-swapped segment saved to: {output_path}")

        # Cleanup temporary processing directory
        shutil.rmtree(temp_process_dir, ignore_errors=True)

        return output_path

    except Exception as e:
        logger.error(f"Face-swap failed: {e}")
        return None

def stitch_segments(segment_paths, output_path):
    """Combine video segments into single video using FFmpeg"""
    try:
        # Create concat file for FFmpeg
        concat_file = output_path.replace('.mp4', '_concat.txt')

        with open(concat_file, 'w') as f:
            for path in segment_paths:
                f.write(f"file '{path}'\n")

        cmd = [
            'ffmpeg', '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_path
        ]

        logger.info(f"Stitching {len(segment_paths)} segments")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg stitching error: {result.stderr}")
            return False

        logger.info(f"Video stitched successfully: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Stitching failed: {e}")
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

def process_video_job(record_id, video_url, avatar_url, config, webhook_url=None):
    """
    Main processing pipeline
    Returns dict with status, output_url, and error message
    """
    temp_dir = None

    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp(prefix='faceswap_')
        logger.info(f"Processing record {record_id} in {temp_dir}")

        # Download video and avatar
        video_path = os.path.join(temp_dir, 'input_video.mp4')
        avatar_path = os.path.join(temp_dir, 'avatar.jpg')

        if not download_file(video_url, video_path):
            raise Exception("Failed to download video")

        if not download_file(avatar_url, avatar_path):
            raise Exception("Failed to download avatar")

        # Segment video
        segments = segment_video(video_path, config['processing']['segments'])
        if not segments:
            raise Exception("Video segmentation failed")

        # Face-swap segments 1 and 3 (indices 0 and 2)
        logger.info("Face-swapping segment 1 (0-5s)")
        swapped_seg1 = face_swap_segment(segments[0], avatar_path, config['processing'])
        if not swapped_seg1:
            raise Exception("Face-swap failed on segment 1")

        logger.info("Face-swapping segment 3 (15-20s)")
        swapped_seg3 = face_swap_segment(segments[2], avatar_path, config['processing'])
        if not swapped_seg3:
            raise Exception("Face-swap failed on segment 3")

        # Combine segments: swapped1, original2, swapped3, original4
        final_segments = [swapped_seg1, segments[1], swapped_seg3, segments[3]]
        output_path = os.path.join(temp_dir, 'final_output.mp4')

        if not stitch_segments(final_segments, output_path):
            raise Exception("Video stitching failed")

        # Upload to S3
        output_url = upload_to_s3(output_path, record_id, config['storage'])
        if not output_url:
            raise Exception("S3 upload failed")

        # Send success webhook
        result = {
            'status': 'Complete',
            'record_id': record_id,
            'output_url': output_url,
            'error_message': ''
        }

        if webhook_url:
            send_webhook(webhook_url, result)

        # Cleanup
        cleanup_temp_files(temp_dir)

        return {
            'status': 'success',
            'output_url': output_url
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Processing failed: {error_msg}\n{traceback.format_exc()}")

        # Send failure webhook
        result = {
            'status': '🚩 Failed',
            'record_id': record_id,
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
