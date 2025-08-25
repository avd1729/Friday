import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import pyfiglet 
from friday.llm_integration.base_client import AgentClient

console = Console()

def driver(client: AgentClient):

    ascii_title = pyfiglet.figlet_format("Friday", font="slant")
    console.print(Panel.fit(ascii_title, border_style="blue"))

    while True:
        user_input = Prompt.ask("\n[bold cyan]Friday [/bold cyan]")

        if user_input.lower() in ["quit", "exit", "q"]:
            console.print("[bold red]Byee...[/bold red]")
            break

        response = client.handle_input(user_input)

        console.print(Panel(response, title="Response", border_style="green"))

