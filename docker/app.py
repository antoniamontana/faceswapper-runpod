"""
UGC Face Swapper V1 MVP - Flask Web Server
Receives processing jobs from Make.com and executes face-swap pipeline
"""

import os
import yaml
import logging
from flask import Flask, request, jsonify
from process import process_video_job
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
def load_config():
    """Load configuration from environment variable CONFIG_YAML"""
    config_yaml = os.getenv('CONFIG_YAML')
    if not config_yaml:
        logger.error("CONFIG_YAML environment variable not set")
        return None

    try:
        config = yaml.safe_load(config_yaml)
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to parse CONFIG_YAML: {e}")
        return None

CONFIG = load_config()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Runpod"""
    return jsonify({
        'status': 'healthy',
        'service': 'ugc-faceswapper-v1',
        'config_loaded': CONFIG is not None
    }), 200

@app.route('/process', methods=['POST'])
def process():
    """
    Main processing endpoint
    Expects JSON payload:
    {
        "record_id": "recXXXXXXXXXX",
        "video_url": "https://...",
        "avatar_url": "https://...",
        "webhook_url": "https://hook.make.com/..."
    }
    """
    if not CONFIG:
        return jsonify({
            'status': 'error',
            'message': 'Configuration not loaded'
        }), 500

    try:
        # Parse request
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400

        # Validate required fields
        required_fields = ['record_id', 'video_url', 'avatar_url']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        logger.info(f"Starting processing for record: {data['record_id']}")

        # Extract data
        record_id = data['record_id']
        video_url = data['video_url']
        avatar_url = data['avatar_url']
        webhook_url = data.get('webhook_url') or CONFIG.get('webhook', {}).get('completion_url')

        if not webhook_url:
            logger.warning("No webhook URL provided, skipping callback")

        # Process video (this runs synchronously)
        result = process_video_job(
            record_id=record_id,
            video_url=video_url,
            avatar_url=avatar_url,
            config=CONFIG,
            webhook_url=webhook_url
        )

        if result['status'] == 'success':
            logger.info(f"Processing completed successfully for record: {record_id}")
            return jsonify(result), 200
        else:
            logger.error(f"Processing failed for record: {record_id} - {result.get('error')}")
            return jsonify(result), 200  # Still return 200 so Runpod doesn't retry

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")

        return jsonify({
            'status': 'error',
            'message': error_msg,
            'traceback': traceback.format_exc()
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint showing current processing info"""
    return jsonify({
        'service': 'ugc-faceswapper-v1',
        'version': '1.0.0',
        'model': 'wan2.2-animate-14b',
        'gpu': os.getenv('CUDA_VISIBLE_DEVICES', 'not set'),
        'config_loaded': CONFIG is not None
    }), 200

if __name__ == '__main__':
    if not CONFIG:
        logger.error("Cannot start server: Configuration not loaded")
        exit(1)

    # Run Flask with gunicorn in production
    # For development, use: app.run(host='0.0.0.0', port=8080, debug=False)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)
