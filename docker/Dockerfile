# Use existing working base (already has PyTorch + system deps)
FROM ghcr.io/lum3on/wan22-runpod:latest

WORKDIR /app

# Install Python dependencies (minimal - Wan2.2 is pre-installed in base image)
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    requests \
    PyYAML

# Clone Wan2.2
RUN git clone https://github.com/Wan-Video/Wan2.2.git /app/Wan2.2

# Copy our handler code
COPY handler.py process_simple.py utils.py ./

# Environment
ENV MODEL_PATH=/runpod-volume/models/Wan2.2-Animate-14B
ENV PYTHONPATH=/app:/app/Wan2.2:$PYTHONPATH

CMD ["python", "-u", "handler.py"]
