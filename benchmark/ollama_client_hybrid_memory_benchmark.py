from friday.llm_integration.ollama_client import OllamaClient
from friday.memory.hybrid_conversation_memory import HybridConversationMemory
from friday.utils.benchmark import benchmark_function
import os
from datetime import datetime

def run_agent_with_memory(memory_backend, prompt: str):
    client = OllamaClient(memory=memory_backend)
    return client.handle_input(prompt)

if __name__ == "__main__":
    prompts = [
        "Explain quantum entanglement in simple terms",
        "Could you explain if there is any concerns or mistakes in base_client.py implementation?",
        "Provide a contrast on in_memory_conversation_memory.py and sqlite_conversation_memory.py"
    ]
    hybrid_memory = HybridConversationMemory()

    results = benchmark_function(run_agent_with_memory, prompts, hybrid_memory)

    # Save results
    benchmark_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(benchmark_dir, exist_ok=True)
    filename = os.path.join(benchmark_dir, f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    with open(filename, "w") as f:
        f.write("Hybrid Memory Ollama Client Benchmark Results:\n\n")
        for stats in results:
            f.write(f"Prompt: {stats['prompt']}\n")
            f.write(f"  Time taken: {stats['time_taken']:.4f}s\n")
            f.write(f"  Result: {stats['result']}\n\n")

    print(f"Benchmark results saved to {filename}")
