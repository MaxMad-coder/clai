import typer
from rich.console import Console
from rich.table import Table
from clai.ai import send_to_llm
from clai.config import load_config, set_backend, set_gemini_key

app = typer.Typer()
console = Console()

@app.command()
def ask(question: str):
    """Ask CLAI anything."""
    with console.status("[bold green]Thinking..."):
        reply = send_to_llm(question)
    console.print(f"\n[bold cyan]CLAI:[/bold cyan] {reply}\n")

@app.command()
def config(
    backend: str = typer.Option(None, "--backend", "-b", help="Set backend: ollama or gemini"),
    set_key: str = typer.Option(None, "--set-key", "-k", help="Set your Gemini API key"),
    show: bool = typer.Option(False, "--show", "-s", help="Show current config")
):
    """Configure CLAI backend settings."""

    # Show current config
    if show or (backend is None and set_key is None):
        cfg = load_config()
        table = Table(title="CLAI Configuration", border_style="cyan")
        table.add_column("Setting", style="bold white")
        table.add_column("Value", style="green")
        table.add_row("Backend",        cfg["backend"])
        table.add_row("Ollama Model",   cfg["ollama_model"])
        table.add_row("Ollama URL",     cfg["ollama_url"])
        table.add_row("Gemini Model",   cfg["gemini_model"])
        key = cfg["gemini_api_key"]
        table.add_row("Gemini API Key", f"{key[:8]}..." if key else "Not set")
        console.print(table)
        return

    # Switch backend
    if backend:
        if backend not in ["ollama", "gemini"]:
            console.print("[red]Error: backend must be 'ollama' or 'gemini'[/red]")
            raise typer.Exit(1)
        set_backend(backend)
        console.print(f"[green]Backend switched to: {backend}[/green]")

    # Save Gemini API key
    if set_key:
        set_gemini_key(set_key)
        console.print("[green]Gemini API key saved successfully.[/green]")

@app.command()
def explain(filename: str):
    """Explain a code file."""
    console.print(f"[bold cyan]CLAI:[/bold cyan] Explaining: {filename}")
    console.print("[yellow]Coming in Week 4![/yellow]")

@app.command()
def fix(problem: str):
    """Fix a Linux permission error."""
    console.print(f"[bold cyan]CLAI:[/bold cyan] Looking at: {problem}")
    console.print("[yellow]Coming in Week 5![/yellow]")

@app.command()
def diagnose(logfile: str):
    """Diagnose an error log."""
    console.print(f"[bold cyan]CLAI:[/bold cyan] Diagnosing: {logfile}")
    console.print("[yellow]Coming in Week 6![/yellow]")

@app.command()
def remember():
    """Build project memory."""
    console.print("[bold cyan]CLAI:[/bold cyan] Building project memory...")
    console.print("[yellow]Coming in Week 3![/yellow]")

if __name__ == "__main__":
    app()
