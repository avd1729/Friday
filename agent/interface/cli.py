import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from agent.llm_integration.ollama_client import OllamaClient

console = Console()
client = OllamaClient()

def main():
    console.print(Panel.fit("[bold green]Friday[/bold green]", border_style="blue"))

    while True:
        console.print("\n[cyan]Choose an action:[/cyan]")
        console.print("[1] Ask a question")
        console.print("[2] Read a file")
        console.print("[3] Quit")

        choice = IntPrompt.ask("Enter choice", choices=["1", "2", "3"])

        if choice == 1:
            question = Prompt.ask("[bold yellow]Enter your question[/bold yellow]")
            response = client.generate_action(question)
            console.print(Panel(response, title="Model Response", border_style="green"))

        elif choice == 2:
            file_path = Prompt.ask("[bold yellow]Enter file path[/bold yellow]")
            question = Prompt.ask("[bold yellow]What do you want to know about this file?[/bold yellow]")
            response = client.read_file(question, file_path)
            console.print(Panel(response, title="File Analysis", border_style="magenta"))

        elif choice == 3:
            console.print("[bold red]Exiting...[/bold red]")
            break

if __name__ == "__main__":
    main()
