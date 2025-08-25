import time
from typing import Callable, Any, Dict

def benchmark_function(func: Callable, *args, repeat: int = 3, **kwargs) -> Dict[str, Any]:
    """
    Benchmarks a function by running it multiple times and returning timing stats.
    Returns a dict with average, min, max, and all timings.
    """
    timings = []
    for _ in range(repeat):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        timings.append(end - start)
    return {
        'function': func.__name__,
        'repeat': repeat,
        'average_time': sum(timings) / repeat,
        'min_time': min(timings),
        'max_time': max(timings),
        'all_timings': timings,
        'last_result': result
    }


def compare_benchmarks(benchmarks: Dict[str, Dict[str, Any]]):
    print("Benchmark Results:")
    for name, stats in benchmarks.items():
        print(f"{name}: avg={stats['average_time']:.4f}s min={stats['min_time']:.4f}s max={stats['max_time']:.4f}s")
