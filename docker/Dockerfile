# Use EXISTING Wan2.2 image that already works!
FROM ghcr.io/lum3on/wan22-runpod:latest

WORKDIR /app

# Install ONLY what we need for our handler
RUN pip install --no-cache-dir runpod boto3 requests PyYAML

# Clone Wan2.2 standalone code (lum3on has it in ComfyUI, we need standalone)
RUN git clone https://github.com/Wan-Video/Wan2.2.git /app/Wan2.2 && \
    ls -la /app/Wan2.2 && \
    echo "Verifying critical files..." && \
    test -f /app/Wan2.2/wan/modules/animate/preprocess/preprocess_data.py && \
    echo "✅ preprocess_data.py found" || echo "❌ preprocess_data.py NOT FOUND"

# Install Wan2.2 dependencies if needed
WORKDIR /app/Wan2.2
RUN pip install --no-cache-dir -r requirements_animate.txt || echo "Warning: requirements_animate.txt install had issues"

# Copy our handler code
WORKDIR /app
COPY handler.py process.py utils.py ./

# Model will be on network volume
ENV MODEL_PATH=/runpod-volume/models/Wan2.2-Animate-14B
ENV PYTHONPATH=/app:/app/Wan2.2:$PYTHONPATH

CMD ["python", "-u", "handler.py"]
