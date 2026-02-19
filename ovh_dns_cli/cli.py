import sys
import os
from pathlib import Path

import click
import ovh
from rich.console import Console
from rich.table import Table

console = Console()


def get_client():
    try:
        return ovh.Client()
    except Exception as e:
        console.print(f"[red]Auth error:[/red] {e}")
        console.print("Run [bold]ovh-dns setup[/bold] to configure credentials.")
        sys.exit(1)


@click.group()
def cli():
    """CLI to manage OVH DNS records."""


@cli.command()
def zones():
    """List all DNS zones on the account."""
    client = get_client()
    zone_list = client.get("/domain/zone")
    table = Table(title="DNS Zones")
    table.add_column("Zone", style="cyan")
    for z in sorted(zone_list):
        table.add_row(z)
    console.print(table)


@cli.command("list")
@click.argument("zone")
@click.option("--type", "-t", "record_type", default=None, help="Filter by record type (A, AAAA, CNAME, MX, TXT...)")
def list_records(zone, record_type):
    """List DNS records for a zone."""
    client = get_client()
    params = {}
    if record_type:
        params["fieldType"] = record_type
    record_ids = client.get(f"/domain/zone/{zone}/record", **params)

    table = Table(title=f"Records for {zone}")
    table.add_column("ID", style="dim")
    table.add_column("Type", style="green")
    table.add_column("Subdomain", style="cyan")
    table.add_column("Target")
    table.add_column("TTL", style="dim")

    for rid in sorted(record_ids):
        r = client.get(f"/domain/zone/{zone}/record/{rid}")
        table.add_row(str(r["id"]), r["fieldType"], r.get("subDomain", ""), r["target"], str(r.get("ttl", "")))
    console.print(table)


@cli.command()
@click.argument("zone")
@click.argument("subdomain")
@click.argument("target")
@click.option("--type", "-t", "record_type", default="A", help="Record type (default: A)")
@click.option("--ttl", default=0, type=int, help="TTL in seconds (0 = zone default)")
def add(zone, subdomain, target, record_type, ttl):
    """Add a DNS record."""
    client = get_client()
    params = {
        "fieldType": record_type,
        "subDomain": subdomain,
        "target": target,
    }
    if ttl:
        params["ttl"] = ttl
    r = client.post(f"/domain/zone/{zone}/record", **params)
    client.post(f"/domain/zone/{zone}/refresh")
    console.print(f"[green]Created record #{r['id']}:[/green] {record_type} {subdomain}.{zone} → {target}")


@cli.command()
@click.argument("zone")
@click.argument("record_id", type=int)
@click.option("--target", default=None, help="New target value")
@click.option("--ttl", default=None, type=int, help="New TTL")
@click.option("--subdomain", default=None, help="New subdomain")
def edit(zone, record_id, target, ttl, subdomain):
    """Edit an existing DNS record by ID."""
    client = get_client()
    params = {}
    if target is not None:
        params["target"] = target
    if ttl is not None:
        params["ttl"] = ttl
    if subdomain is not None:
        params["subDomain"] = subdomain
    if not params:
        console.print("[yellow]Nothing to update. Use --target, --ttl, or --subdomain.[/yellow]")
        return
    client.put(f"/domain/zone/{zone}/record/{record_id}", **params)
    client.post(f"/domain/zone/{zone}/refresh")
    console.print(f"[green]Updated record #{record_id}[/green]")


@cli.command()
@click.argument("zone")
@click.argument("subdomain", required=False, default=None)
@click.option("--id", "record_id", default=None, type=int, help="Delete by record ID")
@click.option("--type", "-t", "record_type", default=None, help="Filter by type when deleting by subdomain")
@click.confirmation_option(prompt="Are you sure?")
def rm(zone, subdomain, record_id, record_type):
    """Remove DNS record(s) by subdomain or by ID."""
    client = get_client()

    if record_id:
        client.delete(f"/domain/zone/{zone}/record/{record_id}")
        client.post(f"/domain/zone/{zone}/refresh")
        console.print(f"[green]Deleted record #{record_id}[/green]")
        return

    if not subdomain:
        console.print("[red]Provide a subdomain or --id[/red]")
        sys.exit(1)

    params = {"subDomain": subdomain}
    if record_type:
        params["fieldType"] = record_type
    record_ids = client.get(f"/domain/zone/{zone}/record", **params)
    if not record_ids:
        console.print(f"[yellow]No records found for {subdomain}.{zone}[/yellow]")
        return

    for rid in record_ids:
        client.delete(f"/domain/zone/{zone}/record/{rid}")
        console.print(f"  Deleted #{rid}")
    client.post(f"/domain/zone/{zone}/refresh")
    console.print(f"[green]Deleted {len(record_ids)} record(s)[/green]")


@cli.command()
@click.argument("zone")
def export(zone):
    """Export zone as BIND-style text."""
    client = get_client()
    text = client.get(f"/domain/zone/{zone}/export")
    console.print(text)


@cli.command()
def setup():
    """Interactive setup for OVH API credentials."""
    console.print("[bold]OVH DNS CLI Setup[/bold]\n")
    console.print("1. Go to [link=https://eu.api.ovh.com/createApp/]https://eu.api.ovh.com/createApp/[/link]")
    console.print("2. Create an application and note your Application Key & Secret.\n")

    endpoint = click.prompt("Endpoint", default="ovh-eu", type=click.Choice(["ovh-eu", "ovh-ca", "ovh-us", "kimsufi-eu", "soyoustart-eu"]))
    app_key = click.prompt("Application Key")
    app_secret = click.prompt("Application Secret")

    console.print("\n[bold]Requesting consumer key...[/bold]")
    client = ovh.Client(endpoint=endpoint, application_key=app_key, application_secret=app_secret)
    ck = client.new_consumer_key_request()
    ck.add_recursive_rules(ovh.API_READ_WRITE, "/domain/zone")
    validation = ck.request()

    console.print(f"\n3. Validate the token here: [link={validation['validationUrl']}]{validation['validationUrl']}[/link]")
    click.pause("Press Enter after validating in your browser...")

    conf_path = Path.home() / ".ovh.conf"
    conf_content = f"""[default]
endpoint={endpoint}

[{endpoint}]
application_key={app_key}
application_secret={app_secret}
consumer_key={validation['consumerKey']}
"""
    conf_path.write_text(conf_content)
    console.print(f"\n[green]Config saved to {conf_path}[/green]")
    console.print("You can now use [bold]ovh-dns zones[/bold] to test.")
