import time
from typing import Callable, Any, Dict, List

def benchmark_function(func: Callable, prompts: List[str], memory_backend, *args, **kwargs) -> List[Dict[str, Any]]:
    results = []
    for prompt in prompts:
        start = time.perf_counter()
        result = func(memory_backend, prompt, *args, **kwargs)
        end = time.perf_counter()
        results.append({
            'function': func.__name__,
            'prompt': prompt,
            'time_taken': end - start,
            'result': result
        })
    return results
