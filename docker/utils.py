"""
UGC Face Swapper V1 MVP - Utility Functions
Helper functions for face detection and video processing
"""

import cv2
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def detect_face_in_image(image_path, confidence_threshold=0.6):
    """
    Detect face in image using OpenCV
    Returns True if face detected with sufficient confidence
    """
    try:
        # Load image
        img = cv2.imread(str(image_path))
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return False

        # Load pre-trained face detection model
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        if len(faces) == 0:
            logger.warning(f"No face detected in {image_path}")
            return False

        if len(faces) > 1:
            logger.warning(f"Multiple faces detected in {image_path} ({len(faces)} faces)")
            # For V1, we still return True but log warning

        logger.info(f"Face detected in {image_path}")
        return True

    except Exception as e:
        logger.error(f"Face detection failed: {e}")
        return False

def validate_video_format(video_path):
    """
    Validate video format and duration
    Returns (is_valid, error_message)
    """
    try:
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            return False, "Cannot open video file"

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cap.release()

        logger.info(f"Video properties: {width}x{height}, {fps}fps, {duration:.1f}s")

        # Validate duration (should be ~30 seconds)
        if duration < 25 or duration > 35:
            return False, f"Video duration {duration:.1f}s is outside expected range (25-35s)"

        # Validate resolution (warn if > 1080p)
        if height > 1080:
            logger.warning(f"Video resolution {height}p exceeds 1080p, will be downscaled")

        return True, ""

    except Exception as e:
        return False, str(e)

def get_video_info(video_path):
    """Get detailed video information"""
    try:
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            return None

        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
        }

        cap.release()
        return info

    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        return None

def downscale_video_if_needed(video_path, max_height=1080):
    """
    Downscale video to max_height if larger
    Returns path to processed video (original or downscaled)
    """
    try:
        info = get_video_info(video_path)
        if not info:
            return video_path

        if info['height'] <= max_height:
            logger.info(f"Video height {info['height']}p is within limit")
            return video_path

        # Calculate new dimensions maintaining aspect ratio
        scale_factor = max_height / info['height']
        new_width = int(info['width'] * scale_factor)
        new_height = max_height

        # Ensure width is even (required for some codecs)
        if new_width % 2 != 0:
            new_width -= 1

        output_path = video_path.replace('.mp4', '_downscaled.mp4')

        logger.info(f"Downscaling video from {info['height']}p to {new_height}p")

        import subprocess
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Downscaling failed: {result.stderr}")
            return video_path

        logger.info(f"Video downscaled successfully to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Downscaling error: {e}")
        return video_path
