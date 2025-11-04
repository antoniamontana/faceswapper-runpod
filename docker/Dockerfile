# Use EXISTING Wan2.2 image that already works!
FROM ghcr.io/lum3on/wan22-runpod:latest

WORKDIR /app

# Install ONLY what we need for our handler
RUN pip install --no-cache-dir runpod boto3 requests PyYAML

# Copy our handler code
COPY handler.py process.py utils.py config.yaml ./

# Wan2.2 and model are ALREADY in the base image at /comfyui/models/
ENV MODEL_PATH=/comfyui/models/
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["python", "-u", "handler.py"]
