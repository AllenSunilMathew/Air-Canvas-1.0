import time
from collections import deque
import torch
from sd15_utils import device as sd_device

class OptimizerMetrics:
    def __init__(self):
        self.request_times = deque(maxlen=100)
        self.cache_hits = 0
        self.total_requests = 0
        self.gpu_util_history = deque(maxlen=50)
    
    def record_request(self, duration, hit=False):
        self.request_times.append(duration)
        self.total_requests += 1
        if hit:
            self.cache_hits += 1
    
    def get_stats(self):
        times = list(self.request_times)
        if not times:
            return {"p50": 0, "p95": 0, "cache_hit_rate": 0, "throughput": 0}
        
        return {
            "p50": round(sorted(times)[len(times)//2], 2),
            "p95": round(sorted(times)[int(0.95*len(times))], 2),
            "cache_hit_rate": round(self.cache_hits / max(self.total_requests, 1) * 100, 1),
            "throughput": round(len(times) / max(time.time() - list(self.request_times)[-1], 1), 2) if times else 0,
            "active_requests": len(self.request_times)
        }

metrics = OptimizerMetrics()

