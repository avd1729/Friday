import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from friday.llm_integration.ollama_client import OllamaClient

console = Console()
client = OllamaClient()

def driver():
    console.print(Panel.fit("[bold green]Friday[/bold green]", border_style="blue"))

    while True:
        user_input = Prompt.ask("\n[bold cyan]What do you want to do?[/bold cyan] (or type 'quit')")

        if user_input.lower() in ["quit", "exit", "q"]:
            console.print("[bold red]Exiting...[/bold red]")
            break

        response = client.handle_input(user_input)

        console.print(Panel(response, title="Friday Response", border_style="green"))

