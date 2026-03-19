import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from clai.memory import (
    scan_project, save_memory, load_memory,
    memory_exists
)

console = Console()

def run(
    path: str = typer.Argument(".", help="Project path to scan (default: current folder)"),
    update: bool = typer.Option(False, "--update", "-u", help="Force update existing memory"),
    show: bool = typer.Option(False, "--show", "-s", help="Show current memory summary")
):
    """Build or update project memory for smarter AI answers."""

    project_path = os.path.abspath(path)

    # ── Show existing memory ─────────────────────────────────────────────
    if show:
        if not memory_exists(project_path):
            console.print("[yellow]No memory found for this project.[/yellow]")
            console.print("Run [bold cyan]clai remember[/bold cyan] first to build it.")
            raise typer.Exit()

        memory = load_memory(project_path)
        display_memory_summary(memory)
        return

    # ── Check if memory already exists ───────────────────────────────────
    if memory_exists(project_path) and not update:
        console.print("\n[yellow]Memory already exists for this project.[/yellow]")
        console.print("Use [bold]clai remember --update[/bold] to refresh it.")
        console.print("Use [bold]clai remember --show[/bold] to view it.\n")
        raise typer.Exit()

    # ── Scan the project ─────────────────────────────────────────────────
    action = "Updating" if update else "Building"
    console.print(
        f"\n[bold cyan]CLAI:[/bold cyan] {action} project memory...\n"
        f"[dim]Scanning: {project_path}[/dim]\n"
    )

    with console.status("[bold green]Scanning all files..."):
        memory = scan_project(project_path)

    # ── Save memory ──────────────────────────────────────────────────────
    save_memory(memory, project_path)

    # ── Show results ─────────────────────────────────────────────────────
    display_memory_summary(memory)

    console.print(Panel(
        "[green]Memory saved to .clai_memory.json[/green]\n"
        "[dim]CLAI will now use this memory for smarter, project-specific answers.[/dim]",
        border_style="green"
    ))


def display_memory_summary(memory: dict):
    """Display a clean summary table of what CLAI found in the project."""

    # ── Main summary table ───────────────────────────────────────────────
    table = Table(title="Project Memory Summary", border_style="cyan")
    table.add_column("Property",       style="bold white", min_width=20)
    table.add_column("Value",          style="green")

    table.add_row("Project Name",    memory.get("project_name", "unknown"))
    table.add_row("Project Type",    memory.get("project_type", "unknown"))
    table.add_row("Last Updated",    memory.get("last_updated", "unknown"))
    table.add_row("Total Files",     str(len(memory.get("files", []))))
    table.add_row("Summary",         memory.get("summary", ""))
    console.print(table)

    # ── Language breakdown table ─────────────────────────────────────────
    lang_table = Table(title="Language Breakdown", border_style="blue")
    lang_table.add_column("Language",  style="bold white", min_width=15)
    lang_table.add_column("Functions / Elements", style="cyan",  min_width=22)
    lang_table.add_column("Classes / Selectors",  style="yellow",min_width=22)

    rows = [
        ("Python",      "python_functions", "python_classes"),
        ("JavaScript",  "js_functions",     "js_classes"),
        ("Java",        "java_functions",   "java_classes"),
        ("C / C++",     "c_functions",      "c_classes"),
        ("HTML",        "html_elements",    None),
        ("CSS",         "css_selectors",    None),
    ]

    for lang, fn_key, cls_key in rows:
        fn_count  = len(memory.get(fn_key,  []))
        cls_count = len(memory.get(cls_key, [])) if cls_key else 0

        # Only show languages that actually have something
        if fn_count > 0 or cls_count > 0:
            lang_table.add_row(
                lang,
                str(fn_count),
                str(cls_count) if cls_key else "N/A"
            )

    console.print(lang_table)