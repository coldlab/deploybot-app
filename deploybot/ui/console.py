from rich.console import Console
from rich.status import Status
from typing import Dict, Any

class ConsoleUI:
    def __init__(self):
        self.console = Console()

    def print_header(self, version: str = "v0.1"):
        self.console.print(f"[bold blue]🚀 DeployBot {version} - Deploy infrastructure in seconds[/bold blue]")

    def print_stack_info(self, stack, target_instance):
        self.console.print(f"[bold green]🔍 Selected stack: {stack.name}[/bold green]")
        self.console.print(f"[bold cyan]☁️ Cloud provider: {target_instance.name.upper()}[/bold cyan]")
        if getattr(target_instance, 'region', None):
            self.console.print(f"[bold purple]🌎 Region: {target_instance.region}[/bold purple]")

    def print_outputs(self, outputs: Dict[str, Any]):
        for key, value in outputs.items():
            if key == "app_url":
                self.console.print(f"[bold magenta]🌐 App URL: {value}[/bold magenta]")
            elif key == "ssh_access":
                self.console.print(f"[bold yellow]🔒 SSH Access: {value}[/bold yellow]")
            else:
                self.console.print(f"[bold white]{key}: {value}[/bold white]")

    def print_success(self, message: str):
        self.console.print(f"[bold green]{message}[/bold green]")

    def print_error(self, message: str):
        self.console.print(f"[bold red]❌ {message}[/bold red]")

    def print_time(self, seconds: int):
        self.console.print(f"[bold white]Total time: {seconds} seconds[/bold white]")

    def spinner(self, message: str, spinner: str = "aesthetic"):
        return Status(message, spinner=spinner, console=self.console)