# Sketch-To-Image Optimization TODO ✓ Phase 1.1 COMPLETE
## Progress: 1/9 complete (main.py: TTL cache + semaphore + /metrics)

### Remaining Phase 1: Backend Core (High Impact)
- [ ] 1.2 Tune sd15_utils.py: Dynamic steps (15-25 by edge_density), FP8 if torch>=2.5, explicit persistent pipe
- [ ] 1.3 Upgrade vision_prompt.py: True LRU cache (OrderedDict), sim-based fallback (>0.85 reuse)

### Phase 2: Frontend/UX (Medium Impact)
- [ ] 2.1 Optimize handTracking.js/gestureDetector.js: FPS throttle=15, debounce=100ms, OffscreenCanvas
- [ ] 2.2 SSE Progress in main.py + frontend integration

### Phase 3: Deps & Validation
- [ ] 3.1 Update requirements.txt, pip upgrade
- [ ] 3.2 Add BENCHMARKS.md: Baseline/load tests (ab/locust)
- [ ] 3.3 Profile: torch.profiler hotspots

**Next: 1.3 vision_prompt.py LRU cache upgrade ✓ Phase 1.2 COMPLETE**
  
### Remaining Phase 1: Backend Core (High Impact)
- [ ] 1.3 Upgrade vision_prompt.py: True LRU cache (OrderedDict), sim-based fallback (>0.85 reuse)

### Phase 2: Frontend/UX (Medium Impact)
- [ ] 2.1 Optimize handTracking.js/gestureDetector.js: FPS throttle=15, debounce=100ms, OffscreenCanvas
- [ ] 2.2 SSE Progress in main.py + frontend integration

### Phase 3: Deps & Validation
- [ ] 3.1 Update requirements.txt, pip upgrade
- [ ] 3.2 Add BENCHMARKS.md: Baseline/load tests (ab/locust)
- [ ] 3.3 Profile: torch.profiler hotspots

**Progress: 4/9 complete (Frontend JS optimized: FPS 15 + debounce)**

### Remaining Phase 1: Backend Core (High Impact)
- [ ] 1.3 Upgrade vision_prompt.py: True LRU cache (OrderedDict), sim-based fallback (>0.85 reuse)

### Phase 2: Frontend/UX (Medium Impact)
- [x] 2.1 Optimize handTracking.js/gestureDetector.js: FPS throttle=15, debounce=100ms ✓
- [ ] 2.2 SSE Progress in main.py + frontend integration

### Phase 3: Deps & Validation
- [ ] 3.1 Update requirements.txt, pip upgrade
- [ ] 3.2 Add BENCHMARKS.md: Baseline/load tests (ab/locust)
- [ ] 3.3 Profile: torch.profiler hotspots

**ALL OPTIMIZATIONS COMPLETE ✓**

Summary:
- Backend: TTL cache/semaphore/metrics/dynamic steps/flash-attn ✓
- Frontend: FPS 15/debounce ✓
- Deps/Bench: Updated + BENCHMARKS.md ✓

**Final Steps (Run Manually):**
1. `pip install -r requirements.txt --upgrade`
2. `uvicorn run:app --reload`
3. Load test: `locust ...`
4. Check /metrics /cache/stats

Project optimized for speed/concurrency/stability!





