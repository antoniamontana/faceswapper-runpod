# UGC Face Swapper V1 MVP - GPU Processing Container
# Simple, working approach - no conda, no complex apt logic
FROM --platform=linux/amd64 nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install packages with retries and better error handling
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    for i in 1 2 3; do \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            python3 python3-pip python3-dev \
            build-essential \
            ffmpeg \
            git \
            wget \
            curl \
            ca-certificates && \
        break || sleep 10; \
    done && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p /models /tmp/processing

# Install PyTorch first with CUDA support
RUN pip3 install --timeout=600 --retries=10 --no-cache-dir \
    torch==2.1.0 torchvision==0.16.0 \
    --extra-index-url https://download.pytorch.org/whl/cu118

# Copy and install other requirements (without PyTorch line)
COPY requirements.txt /app/
RUN grep -v "torch" /app/requirements.txt | grep -v "extra-index-url" > /app/requirements_filtered.txt && \
    pip3 install --timeout=600 --retries=10 --no-cache-dir -r /app/requirements_filtered.txt || \
    (sleep 30 && pip3 install --timeout=600 --retries=10 --no-cache-dir -r /app/requirements_filtered.txt)

RUN pip3 install --timeout=600 --retries=10 --no-cache-dir flash-attn --no-build-isolation || echo "flash-attn skipped"

RUN git clone https://github.com/Wan-Video/Wan2.2.git /app/Wan2.2
WORKDIR /app/Wan2.2

RUN grep -v "flash_attn" requirements.txt > requirements_filtered.txt && \
    pip3 install --timeout=600 --retries=10 --no-cache-dir -r requirements_filtered.txt || \
    (sleep 30 && pip3 install --timeout=600 --retries=10 --no-cache-dir -r requirements_filtered.txt)

RUN pip3 install --timeout=600 --retries=10 --no-cache-dir huggingface-hub && \
    huggingface-cli download Wan-AI/Wan2.2-Animate-14B --local-dir /models/Wan2.2-Animate-14B

WORKDIR /app
COPY config.yaml /app/config.yaml
COPY handler.py process.py utils.py /app/

ENV MODEL_PATH=/models/wan2.2-animate
ENV CUDA_VISIBLE_DEVICES=0

# No longer need EXPOSE or HEALTHCHECK for serverless
# Runpod manages container lifecycle

CMD ["python3", "/app/handler.py"]
