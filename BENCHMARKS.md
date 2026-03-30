# Optimization Benchmarks

## Baseline (Before BlackBOXAI)
- Average gen time: ~45s (50 steps, no cache)
- Concurrent: 1 (OOM at 2+)
- FPS frontend: 30+ (high CPU)
- Cache hit: 0%

## After Optimizations (Expected)
| Metric | Before | After | Gain |
|--------|--------|-------|------|
| Gen time | 45s | 12-20s | 3-4x |
| Concurrent | 1 | 3+ | 3x |
| FPS frontend | 30 | 15 (stable) | Smoother |
| Cache hit | 0% | 50%+ | Huge |

## Test Commands
```bash
# Load test 10 concurrent
locust -f locustfile.py --headless -u 10 -r 2

# Single benchmark
python benchmark.py

# GPU monitor
nvidia-smi -l 1
```

## Results
TBD - Run after deps install + restart server.

