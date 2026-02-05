"""CLI entry point for the Infograph service."""

from __future__ import annotations

import click
import uvicorn

from infograph.svc.api_service import create_app


@click.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Host to bind the server to.")
@click.option("--port", default=8000, show_default=True, type=int, help="Port to bind the server to.")
@click.option("--log-level", default="info", show_default=True, help="Uvicorn log level.")
def main(host: str, port: int, log_level: str) -> None:
    """Start the Infograph FastAPI service."""

    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level=log_level)
