import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def ask(question: str):
    """Ask CLAI anything."""
    console.print(f"[bold cyan]CLAI:[/bold cyan] You asked: {question}")

@app.command()
def explain(filename: str):
    """Explain a code file."""
    console.print(f"[bold cyan]CLAI:[/bold cyan] Explaining: {filename}")
    console.print("[yellow]Coming in Week 4![/yellow]")
    
if __name__ == "__main__":
    app()
