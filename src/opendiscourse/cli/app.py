"""OpenDiscourse command-line interface."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from opendiscourse import __version__
from opendiscourse.config.settings import load_settings
from opendiscourse.domain.models import DiscoveryRequest
from opendiscourse.sources.fixture import FixtureSourceAdapter
from opendiscourse.storage.content_addressed import ContentAddressedStorage

app = typer.Typer(no_args_is_help=True, help="OpenDiscourse government data platform.")
config_app = typer.Typer(no_args_is_help=True, help="Inspect validated configuration.")
fixture_app = typer.Typer(no_args_is_help=True, help="Exercise the deterministic fixture source.")
app.add_typer(config_app, name="config")
app.add_typer(fixture_app, name="fixture")
console = Console()


@app.command()
def version() -> None:
    """Print the installed OpenDiscourse version."""
    console.print(__version__)


@config_app.command("show")
def show_config(
    config_file: Annotated[Path, typer.Option(exists=False, dir_okay=False)] = Path(
        "config/default.toml"
    ),
) -> None:
    """Validate configuration and print a redacted representation."""
    settings = load_settings(config_file)
    console.print_json(json.dumps(settings.redacted_dict()))


@app.command()
def doctor(
    config_file: Annotated[Path, typer.Option(exists=False, dir_okay=False)] = Path(
        "config/default.toml"
    ),
) -> None:
    """Validate local configuration and required writable directories."""
    settings = load_settings(config_file)
    storage = ContentAddressedStorage(settings.storage.root, settings.storage.temp_root)
    asyncio.run(storage.initialize())

    table = Table(title="OpenDiscourse doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("configuration", "ok")
    table.add_row("storage root", str(storage.root))
    table.add_row("temporary root", str(storage.temp_root))
    table.add_row("environment", settings.environment)
    console.print(table)


@fixture_app.command("sync")
def fixture_sync(
    config_file: Annotated[Path, typer.Option(exists=False, dir_okay=False)] = Path(
        "config/default.toml"
    ),
) -> None:
    """Run the complete fixture discovery, download, and extraction cycle."""

    async def run() -> None:
        settings = load_settings(config_file)
        store = ContentAddressedStorage(settings.storage.root, settings.storage.temp_root)
        adapter = FixtureSourceAdapter()
        records = 0
        async for asset in adapter.discover(DiscoveryRequest(all_data=True)):
            artifact = await adapter.download(asset, store)
            async for _record in adapter.extract(asset, artifact):
                records += 1
        report = await adapter.verify()
        console.print(
            {
                "discovered": report.discovered,
                "stored": report.stored,
                "extracted": records,
                "complete": report.is_complete,
            }
        )

    asyncio.run(run())


def main() -> None:
    app()
