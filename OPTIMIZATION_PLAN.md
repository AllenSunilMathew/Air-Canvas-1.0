# Optimization Plan - Sketch-to-Image Generator

## Information Gathered

### Project Overview:
- **Type**: AI-powered sketch-to-image desktop application
- **Architecture**: FastAPI backend + HTML/JS frontend
- **Core AI Pipeline**: 
  1. User sketch → 2. Preprocessing → 3. BLIP Caption → 4. Color Analysis → 5. Prompt Enhancement → 6. Stable Diffusion + ControlNet → 7. Output

### Current Implementation Issues:

#### 1. **sd15_utils.py** (Image Generation)
- Uses `float16` - can use `int8` quantization for faster inference
- No `torch.compile()` optimization
- No xformers attention (faster attention mechanism)
- No VAE slicing enabled
- Uses basic Canny edge detection - could use better preprocessing
- Inference steps are high (35-50) - could use better scheduler for fewer steps
- No model caching/warming

#### 2. **vision_prompt.py** (Caption Generation)
- Uses base BLIP model - could use smaller quantized model
- No GPU memory optimization
- Runs on every request - could be cached for similar images
- max_new_tokens=40 is high - could reduce

#### 3. **color_analyzer.py** 
- Basic K-means - simple but functional
- Could add caching for repeated colors

#### 4. **main.py** 
- No request queuing - multiple requests could overwhelm GPU
- No response caching
- No streaming support for progress updates

#### 5. **Frontend**
- result.html uses basic polling - could use WebSocket
- No progress updates during generation

---

## Optimization Plan

### Phase 1: Core Performance Optimizations (High Impact)

#### 1.1 Optimize Stable Diffusion Pipeline
- **Add xformers attention** for 2-3x faster inference
- **Enable VAE slicing** for lower memory usage
- **Add torch.compile()** for JIT optimization
- **Use DDIM or UniPC scheduler** - faster convergence than default
- **Reduce inference steps** with better scheduler (25 steps instead of 50)
- **Add model warmup** on startup

#### 1.2 Optimize BLIP Caption Model
- **Use quantized BLIP** (bnb int8) for faster inference
- **Reduce max_new_tokens** to 20-25 (sufficient for sketches)
- **Add caching** for similar image captions

#### 1.3 Optimize Image Preprocessing
- **Use adaptive thresholding** instead of fixed Canny
- **Add image denoising** before edge detection
- **Resize smarter** - use LANCZOS for quality

### Phase 2: API & System Optimizations (Medium Impact)

#### 2.1 Add Request Optimization
- **Add request queue** to prevent GPU overload
- **Implement response caching** for identical requests
- **Add request batching** if applicable

#### 2.2 Add Progress Streaming
- **Use Server-Sent Events (SSE)** for progress updates
- **Send intermediate images** (optional)

### Phase 3: Frontend Optimizations (Low-Medium Impact)

#### 3.1 Real-time Updates
- **Replace polling with SSE** or WebSocket
- **Add generation progress bar** with actual progress

---

## Dependent Files to be Edited

1. **backend/sd15_utils.py** - Main SD pipeline optimization
2. **backend/vision_prompt.py** - BLIP model optimization  
3. **backend/color_analyzer.py** - Minor improvements
4. **backend/main.py** - Add caching, SSE, warmup
5. **requirements.txt** - Add new dependencies (bitsandbytes, xformers)

---

## Followup Steps

1. Install optimized dependencies
2. Test each component individually
3. Benchmark before/after performance
4. Fine-tune parameters based on results

---

## Expected Performance Improvements

| Optimization | Expected Speedup |
|--------------|------------------|
| xformers attention | 2-3x faster |
| Better scheduler | 1.5-2x faster |
| torch.compile | 1.2-1.5x faster |
| Reduced steps | 1.5-2x faster |
| Quantized BLIP | 2x faster caption |
| **Total Expected** | **5-10x faster** |

---

## Implementation Priority

1. ✅ Phase 1.1 (SD Pipeline) - HIGHEST IMPACT
2. ✅ Phase 1.2 (BLIP) - MEDIUM IMPACT  
3. ✅ Phase 1.3 (Preprocessing) - LOW IMPACT
4. ✅ Phase 2 (API) - MEDIUM IMPACT
5. ✅ Phase 3 (Frontend) - OPTIONAL

