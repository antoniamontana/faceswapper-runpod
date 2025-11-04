FROM runpod/base:0.4.0-cuda11.8.0

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    torch torchvision \
    diffusers transformers \
    opencv-python-headless \
    Pillow numpy \
    boto3 requests PyYAML \
    huggingface-hub

# Clone Wan2.2 repo
RUN git clone https://github.com/Wan-Video/Wan2.2.git /app/Wan2.2
ENV PYTHONPATH=/app/Wan2.2:$PYTHONPATH

# Copy application code
COPY handler.py process.py utils.py config.yaml ./

# Download model DURING BUILD (one-time, ~30 min)
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('Wan-AI/Wan2.2-Animate-14B', local_dir='/app/models/Wan2.2-Animate-14B')"

# Set model path
ENV MODEL_PATH=/app/models/Wan2.2-Animate-14B
ENV CUDA_VISIBLE_DEVICES=0

CMD ["python", "-u", "handler.py"]
