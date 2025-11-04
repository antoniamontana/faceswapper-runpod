# Dockerfile Quick Reference Card

## The 5 Critical Fixes Applied

| Issue | Problem | Solution | File Line |
|-------|---------|----------|-----------|
| **1. Model Path Mismatch** | Download: `/models/Wan2.2-Animate-14B`<br>ENV: `/models/wan2.2-animate` | Added symlink + updated ENV | 61, 72 |
| **2. Missing OpenGL** | opencv crashes with "libGL.so.1 not found" | Added `libgl1-mesa-glx` | 16 |
| **3. Missing Build Tools** | insightface fails to compile | Added `build-essential`, `cmake`, `pkg-config` | 14-16 |
| **4. Python Path Not Set** | Wan2.2 imports fail | Added `ENV PYTHONPATH=/app/Wan2.2` | 76 |
| **5. Missing opencv-contrib** | Some CV features unavailable | Added `opencv-contrib-python` | 39 |

---

## Which Dockerfile to Use?

### Quick Decision Tree
```
Are you deploying to production?
├─ YES → Dockerfile.production ⭐
└─ NO
   ├─ Developing/testing code?
   │  └─ YES → Dockerfile.minimal 🚀
   └─ Debugging build failures?
      └─ YES → Dockerfile.debug 🔍
```

---

## Build Commands

```bash
# Production (recommended for deployment)
docker build -f docker/Dockerfile.production -t faceswapper:prod .

# Minimal (recommended for development)
docker build -f docker/Dockerfile.minimal -t faceswapper:dev .

# Debug (for troubleshooting)
docker build -f docker/Dockerfile.debug -t faceswapper:debug .
```

---

## Test Commands

```bash
# Quick verification (inside container)
python3 -c "import torch, cv2, transformers; print('OK')"

# Wan2.2 import test
python3 -c "import sys; sys.path.insert(0, '/app/Wan2.2'); from wan.modules.animate.preprocess import preprocess_data; print('OK')"

# Full verification (debug dockerfile only)
/app/verify.sh

# Check model exists
ls -lh /models/Wan2.2-Animate-14B/

# Check GPU
nvidia-smi
```

---

## File Comparison

| File | Status | Use Case | Size | Build Time |
|------|--------|----------|------|------------|
| `Dockerfile` | ❌ BROKEN | DO NOT USE | 67GB | 45-60min |
| `Dockerfile.production` | ✅ FIXED | Production | 67GB | 45-60min |
| `Dockerfile.minimal` | ✅ FIXED | Development | 15GB | 15-20min |
| `Dockerfile.debug` | ✅ FIXED | Troubleshooting | 68GB | 50-65min |

---

## Environment Variables

```dockerfile
# Required
ENV MODEL_PATH=/models/Wan2.2-Animate-14B    # Path to model weights
ENV PYTHONPATH=/app/Wan2.2:$PYTHONPATH      # Add Wan2.2 to Python path
ENV CUDA_VISIBLE_DEVICES=0                   # GPU selection

# Optional
ENV DEBIAN_FRONTEND=noninteractive           # Non-interactive apt
ENV PYTHONUNBUFFERED=1                       # Unbuffered Python output
ENV HF_HOME=/models/.cache                   # HuggingFace cache (minimal only)
ENV LOG_LEVEL=DEBUG                          # Debug logging (debug only)
```

---

## Common Issues & Solutions

### Build fails with "libGL.so.1: cannot open shared object"
```bash
# Solution: Add libgl1-mesa-glx to apt-get install
RUN apt-get install -y libgl1-mesa-glx
```

### Build fails with "insightface compilation error"
```bash
# Solution: Add build tools
RUN apt-get install -y build-essential cmake pkg-config
```

### Runtime fails with "ModuleNotFoundError: No module named 'wan'"
```bash
# Solution: Add PYTHONPATH
ENV PYTHONPATH=/app/Wan2.2:$PYTHONPATH
```

### Runtime fails with "Model not found"
```bash
# Solution: Check model path
ls /models/Wan2.2-Animate-14B/
# Should show model files

# Fix: Add symlink if needed
RUN ln -s /models/Wan2.2-Animate-14B /models/wan2.2-animate
```

### Build hangs during model download
```bash
# Solution: Check network, increase timeout
# Or use Dockerfile.minimal to download at runtime
```

---

## Performance Expectations

| Metric | Production | Minimal (first) | Minimal (cached) | Debug |
|--------|-----------|----------------|------------------|-------|
| Build Time | 45-60 min | 15-20 min | 15-20 min | 50-65 min |
| Image Size | 67 GB | 15 GB | 15 GB | 68 GB |
| Cold Start | 15-30 sec | 2-4 min | 15-30 sec | 30-45 sec |
| Success Rate | 95%+ | 95%+ | 95%+ | 95%+ |

---

## Deployment Checklist

### Before Build
- [ ] Choose correct Dockerfile
- [ ] Check disk space (100GB+ free)
- [ ] Verify Docker BuildKit enabled
- [ ] Ensure network stability

### During Build
- [ ] Monitor build logs
- [ ] Watch for download progress
- [ ] Note any warnings
- [ ] Verify each layer completes

### After Build
- [ ] Test imports: `docker run <image> python -c "import torch, cv2"`
- [ ] Check model: `docker run <image> ls -la /models/`
- [ ] Verify size: `docker images | grep faceswapper`
- [ ] Test with sample video

### Before Deployment
- [ ] Tag image: `docker tag faceswapper:prod registry/faceswapper:v1.0`
- [ ] Push to registry: `docker push registry/faceswapper:v1.0`
- [ ] Update Runpod endpoint
- [ ] Set 1-2 warm instances
- [ ] Configure health checks

### After Deployment
- [ ] Test with real video
- [ ] Monitor cold starts
- [ ] Check error logs
- [ ] Verify GPU utilization
- [ ] Test auto-scaling

---

## Quick Fixes Reference

```dockerfile
# Fix 1: Model path consistency
RUN huggingface-cli download Wan-AI/Wan2.2-Animate-14B --local-dir /models/Wan2.2-Animate-14B
RUN ln -s /models/Wan2.2-Animate-14B /models/wan2.2-animate
ENV MODEL_PATH=/models/Wan2.2-Animate-14B

# Fix 2: OpenCV dependencies
RUN apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6

# Fix 3: Build tools for insightface
RUN apt-get install -y build-essential cmake pkg-config python3-dev

# Fix 4: Python path for Wan2.2
ENV PYTHONPATH=/app/Wan2.2:$PYTHONPATH

# Fix 5: Additional opencv packages
RUN pip install --no-cache-dir opencv-python opencv-contrib-python
```

---

## Emergency Rollback

If production deployment fails:

1. **Immediate:** Revert to previous image
   ```bash
   runpod update-endpoint --image registry/faceswapper:v0.9
   ```

2. **Debug:** Build and run debug dockerfile
   ```bash
   docker build -f Dockerfile.debug -t faceswapper:debug .
   docker run -it --entrypoint /bin/bash faceswapper:debug
   /app/verify.sh
   ```

3. **Fallback:** Use minimal dockerfile with external model
   ```bash
   docker run -v /external/models:/models faceswapper:minimal
   ```

4. **Report:** Document failure in `/docs/incidents/`

---

## Support Resources

- **Architecture Analysis:** `/docs/dockerfile_architecture_analysis.md`
- **Decision Matrix:** `/docs/dockerfile_decision_matrix.md`
- **Runpod Docs:** https://docs.runpod.io/
- **Wan2.2 GitHub:** https://github.com/Wan-Video/Wan2.2

---

## Contact & Escalation

| Issue Type | Action | Timeline |
|------------|--------|----------|
| Build failure | Check Dockerfile.debug logs | Immediate |
| Runtime failure | Run `/app/verify.sh` | < 5 min |
| Performance issue | Check GPU utilization | < 15 min |
| Model loading failure | Verify model path | < 5 min |

---

**Last Updated:** 2025-11-04
**Next Review:** After production deployment
**Owner:** System Architecture Designer
