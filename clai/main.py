import typer
from rich.console import Console
from rich.table import Table
from clai.ai import send_to_llm
from clai.config import load_config, set_backend, set_gemini_key
from clai.commands import remember as remember_cmd

app = typer.Typer()
console = Console()

@app.command()
def ask(
    question: str = typer.Argument(..., help="Your question for CLAI"),
    project: str  = typer.Option(".", "--project", "-p", help="Path to project folder")
):
    """Ask CLAI anything. Uses project memory if available."""
    with console.status("[bold green]Thinking..."):
        reply = send_to_llm(question, project_path = project)
    console.print(f"\n[bold cyan]CLAI:[/bold cyan] {reply}\n")

@app.command()
def config(
    backend: str = typer.Option(None, "--backend", "-b", help="Set backend: ollama or gemini"),
    set_key: str = typer.Option(None, "--set-key", "-k", help="Set your Gemini API key"),
    show: bool   = typer.Option(False, "--show", "-s", help="Show current config")
):
    """Configure CLAI backend settings."""

    if show or (backend is None and set_key is None):
        cfg = load_config()
        table = Table(title="CLAI Configuration", border_style="cyan")
        table.add_column("Setting", style="bold white")
        table.add_column("Value",   style="green")
        table.add_row("Backend",        cfg["backend"])
        table.add_row("Ollama Model",   cfg["ollama_model"])
        table.add_row("Ollama URL",     cfg["ollama_url"])
        table.add_row("Gemini Model",   cfg["gemini_model"])
        key = cfg["gemini_api_key"]
        table.add_row("Gemini API Key", f"{key[:8]}..." if key else "Not set")
        console.print(table)
        return

    if backend:
        if backend not in ["ollama", "gemini"]:
            console.print("[red]Error: backend must be 'ollama' or 'gemini'[/red]")
            raise typer.Exit(1)
        set_backend(backend)
        console.print(f"[green]Backend switched to: {backend}[/green]")

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
def remember(
    path:   str  = typer.Argument(".", help="Path to scan (default: current folder)"),
    update: bool = typer.Option(False, "--update", "-u", help="Force update existing memory"),
    show:   bool = typer.Option(False, "--show",   "-s", help="Show current memory summary")
):
    """Build or update project memory for smarter AI answers."""
    remember_cmd.run(path=path, update=update, show=show)

if __name__ == "__main__":
    app()