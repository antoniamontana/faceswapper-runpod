"""
Runpod Serverless Handler for UGC Face Swapper
Receives requests from Make.com and processes face-swap videos
"""

import runpod
import os
import logging
import traceback
from process_simple import process_single_video

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - all params come from event or environment variables
CONFIG = {
    'webhook': {
        'completion_url': None  # Will use webhook_url from event
    },
    'processing': {
        'segments': {
            'swap_1_start': 0,
            'swap_1_end': 5,
            'original_1_start': 5,
            'original_1_end': 15,
            'swap_2_start': 15,
            'swap_2_end': 20,
            'original_2_start': 20,
            'original_2_end': 30
        },
        'model_path': os.environ.get('MODEL_PATH', '/runpod-volume/models/Wan2.2-Animate-14B')
    },
    'storage': {
        's3_access_key': os.environ.get('AWS_ACCESS_KEY_ID'),
        's3_secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        's3_region': os.environ.get('AWS_REGION', 'eu-north-1'),
        's3_bucket': os.environ.get('S3_BUCKET', 'faceswap-outputs-kasparas'),
        's3_output_prefix': os.environ.get('S3_OUTPUT_PREFIX', 'outputs/')
    }
}
logger.info("Handler initialized - config comes from event/env vars")

def handler(event):
    """
    Runpod serverless handler function

    Expected input format:
    {
        "input": {
            "record_id": "recXXXXXXX",
            "source_video_url": "https://...",
            "avatar_image_url": "https://...",
            "webhook_url": "https://hook.make.com/..."
        }
    }

    Returns:
    {
        "status": "success" | "failed",
        "output_url": "https://s3...",
        "error": "error message if failed"
    }
    """

    try:
        # Extract input data
        input_data = event.get("input", {})

        # Get parameters (support both naming conventions)
        record_id = input_data.get("record_id")
        video_url = input_data.get("source_video_url") or input_data.get("video_url")
        avatar_url = input_data.get("avatar_image_url") or input_data.get("avatar_url")
        webhook_url = input_data.get("webhook_url") or CONFIG.get('webhook', {}).get('completion_url')

        # Validate required fields
        if not record_id:
            return {"status": "failed", "error": "Missing record_id"}
        if not video_url:
            return {"status": "failed", "error": "Missing video URL"}
        if not avatar_url:
            return {"status": "failed", "error": "Missing avatar URL"}

        logger.info(f"Starting processing for record: {record_id}")
        logger.info(f"Video URL: {video_url}")
        logger.info(f"Avatar URL: {avatar_url}")

        # Process video with simplified processor (no segmentation!)
        result = process_single_video(
            job_id=record_id,
            video_url=video_url,
            avatar_url=avatar_url,
            config=CONFIG,
            webhook_url=webhook_url
        )

        if result.get('status') == 'success':
            logger.info(f"Processing completed successfully for {record_id}")
            return {
                "status": "success",
                "output_url": result.get('output_url'),
                "record_id": record_id
            }
        else:
            logger.error(f"Processing failed for {record_id}: {result.get('error')}")
            return {
                "status": "failed",
                "error": result.get('error'),
                "record_id": record_id
            }

    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")

        return {
            "status": "failed",
            "error": error_msg,
            "traceback": traceback.format_exc()
        }

# Start Runpod serverless worker
if __name__ == "__main__":
    logger.info("Starting Runpod serverless worker...")
    runpod.serverless.start({"handler": handler})
