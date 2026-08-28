"""
===============================================================================
                     DRONE HUNTER 2D - LIGHTWEIGHT PROFILER
===============================================================================
High-performance, zero-overhead execution timer and entity counter for profiling
combat, rendering, particle simulation, and subsystem frame times.
"""

import time
from typing import Dict, List, Optional, Any


class FrameProfiler:
    """Lightweight in-engine timer and entity counter for performance analysis."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._timers: Dict[str, float] = {}
        self._start_times: Dict[str, float] = {}
        self._entity_counts: Dict[str, int] = {}
        self._frame_history: List[float] = []

    def start_timer(self, name: str):
        if self.enabled:
            self._start_times[name] = time.perf_counter()

    def stop_timer(self, name: str) -> float:
        if not self.enabled:
            return 0.0
        start = self._start_times.get(name)
        if start is not None:
            elapsed = (time.perf_counter() - start) * 1000.0  # ms
            self._timers[name] = self._timers.get(name, 0.0) + elapsed
            return elapsed
        return 0.0

    def record_entities(self, **counts: int):
        if self.enabled:
            self._entity_counts.update(counts)

    def record_frame_time(self, frame_time_ms: float):
        if self.enabled:
            self._frame_history.append(frame_time_ms)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "timers_ms": self._timers.copy(),
            "entity_counts": self._entity_counts.copy(),
            "frame_count": len(self._frame_history)
        }

    def get_summary_stats(self) -> Dict[str, float]:
        if not self._frame_history:
            return {"avg_ms": 0.0, "worst_ms": 0.0, "p95_ms": 0.0}

        sorted_frames = sorted(self._frame_history)
        n = len(sorted_frames)
        avg_ms = sum(sorted_frames) / n
        worst_ms = sorted_frames[-1]
        p95_idx = min(n - 1, int(n * 0.95))
        p95_ms = sorted_frames[p95_idx]

        return {
            "avg_ms": round(avg_ms, 3),
            "worst_ms": round(worst_ms, 3),
            "p95_ms": round(p95_ms, 3)
        }

    def reset_frame(self):
        self._timers.clear()
        self._start_times.clear()
        self._entity_counts.clear()

    def reset_all(self):
        self.reset_frame()
        self._frame_history.clear()
