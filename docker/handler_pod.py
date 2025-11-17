"""
FastAPI Handler for Runpod GPU Pods (NOT serverless)
Runs as persistent HTTP server to receive jobs from Make.com
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import logging
import os
from process_simple import process_single_video

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration from environment
CONFIG = {
    'processing': {
        'model_path': os.environ.get('MODEL_PATH', '/workspace/faceswap-datacenter/models/Wan2.2-Animate-14B')
    },
    'storage': {
        's3_access_key': os.environ.get('AWS_ACCESS_KEY_ID'),
        's3_secret_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        's3_region': os.environ.get('AWS_REGION', 'eu-north-1'),
        's3_bucket': os.environ.get('S3_BUCKET', 'faceswap-outputs-kasparas'),
        's3_output_prefix': os.environ.get('S3_OUTPUT_PREFIX', 'outputs/')
    }
}

logger.info("FastAPI Pod Handler initialized")
logger.info(f"Model path: {CONFIG['processing']['model_path']}")
logger.info(f"S3 bucket: {CONFIG['storage']['s3_bucket']}")

class JobRequest(BaseModel):
    record_id: str
    source_video_url: str
    avatar_image_url: str
    webhook_url: str = None

def process_job_background(job_id: str, video_url: str, avatar_url: str, webhook_url: str = None):
    """Background task to process video"""
    try:
        logger.info(f"Background processing started for {job_id}")
        result = process_single_video(
            job_id=job_id,
            video_url=video_url,
            avatar_url=avatar_url,
            config=CONFIG,
            webhook_url=webhook_url
        )
        logger.info(f"Background processing completed for {job_id}: {result}")
    except Exception as e:
        logger.error(f"Background processing failed for {job_id}: {e}")

@app.post("/process")
async def create_job(job: JobRequest, background_tasks: BackgroundTasks):
    """
    Accept face-swap job from Make.com

    Request body:
    {
        "record_id": "recXXXXX",
        "source_video_url": "https://...",
        "avatar_image_url": "https://...",
        "webhook_url": "https://hook.make.com/..." (optional)
    }

    Returns immediately with job accepted status.
    Processing happens in background, webhook notifies when complete.
    """
    logger.info(f"Job received: {job.record_id}")

    # Add to background tasks
    background_tasks.add_task(
        process_job_background,
        job.record_id,
        job.source_video_url,
        job.avatar_image_url,
        job.webhook_url
    )

    return {
        "status": "accepted",
        "job_id": job.record_id,
        "message": "Job queued for processing"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_path": CONFIG['processing']['model_path'],
        "model_exists": os.path.exists(CONFIG['processing']['model_path'])
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "faceswap-pod",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "process": "/process (POST)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
