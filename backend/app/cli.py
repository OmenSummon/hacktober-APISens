from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from app.models.traffic import TrafficRequest
from app.routes.scan import execute_scan
from app.services.demo_data import DEMO_OPENAPI_SPEC, DEMO_TRAFFIC_REQUESTS
from app.services.openapi_parser import OpenAPIParser
from app.services.traffic_service import traffic_service

cli = typer.Typer(
    name="api-sentinel",
    help="AI-Powered API Drift & Shadow Endpoint Detector CLI",
)
console = Console()


@cli.command("scan")
def scan_command(
    spec: Path = typer.Option(None, "--spec", "-s", help="Path to OpenAPI YAML/JSON file"),
    traffic: Path = typer.Option(None, "--traffic", "-t", help="Path to traffic JSON file"),
    demo: bool = typer.Option(False, "--demo", "-d", help="Run with demo data"),
):
    """
    Scans an API specification against observed traffic for shadow endpoints and drift.
    """
    console.print("\n[bold cyan]🛡️  API Sentinel — Security & Drift Intelligence[/bold cyan]\n")

    if demo or (not spec and not traffic):
        console.print("[yellow]Loading pre-configured demo dataset...[/yellow]")
        parsed_spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
        reqs = [TrafficRequest(**item) for item in DEMO_TRAFFIC_REQUESTS]
    else:
        if not spec or not spec.exists():
            console.print(f"[red]Error: OpenAPI spec file not found at '{spec}'[/red]")
            raise typer.Exit(code=1)
        if not traffic or not traffic.exists():
            console.print(f"[red]Error: Traffic file not found at '{traffic}'[/red]")
            raise typer.Exit(code=1)

        spec_content = spec.read_text(encoding="utf-8")
        parsed_spec = OpenAPIParser.parse(spec_content)
        traffic_content = traffic.read_text(encoding="utf-8")
        reqs = traffic_service.parse_from_json(traffic_content)

    results = execute_scan(parsed_spec, reqs)

    # Print Summary Card
    console.print(
        f"[bold]Summary:[/bold] "
        f"Documented: [green]{results.summary.total_documented_endpoints}[/green] | "
        f"Observed: [blue]{results.summary.total_observed_endpoints}[/blue] | "
        f"Shadow: [red]{results.summary.shadow_endpoints}[/red] | "
        f"Schema Drifts: [yellow]{results.summary.schema_drifts}[/yellow] | "
        f"Risk Score: [bold red]{results.summary.risk_score}/100 ({results.summary.risk_level})[/bold red]\n"
    )

    # Print Inventory Table
    table = Table(title="Endpoint Inventory")
    table.add_column("Method", style="bold")
    table.add_column("Endpoint")
    table.add_column("Doc", justify="center")
    table.add_column("Obs", justify="center")
    table.add_column("Status")
    table.add_column("Risk")

    for item in results.inventory:
        status_color = (
            "red" if item.status == "SHADOW"
            else "yellow" if item.status == "DRIFT"
            else "green" if item.status == "HEALTHY"
            else "dim"
        )
        table.add_row(
            item.method,
            item.endpoint,
            "✅" if item.documented else "❌",
            "✅" if item.observed else "❌",
            f"[{status_color}]{item.status}[/{status_color}]",
            item.risk,
        )

    console.print(table)
    console.print("\n[bold]Findings:[/bold]")
    for idx, f in enumerate(results.findings, 1):
        console.print(
            f" {idx}. [{f.severity.value}] [bold]{f.title}[/bold] ({f.endpoint})\n"
            f"    {f.description}\n"
        )


if __name__ == "__main__":
    cli()
