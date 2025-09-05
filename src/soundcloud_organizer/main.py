import typer
from rich.console import Console

from soundcloud_organizer import auth
from soundcloud_organizer.client import SoundCloudClient
from soundcloud_organizer.config import load_settings, save_settings
from soundcloud_organizer.logging_config import setup_logging
from soundcloud_organizer.processor import TrackLengthFilter, process_stream

app = typer.Typer()
console = Console()


@app.command()
def login(
    client_id: str = typer.Option(..., prompt=True, help="Your SoundCloud Client ID"),
    client_secret: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Your SoundCloud Client Secret"
    ),
):
    """Authorize the application with your SoundCloud account."""
    setup_logging(debug=False)
    console.print("Starting SoundCloud authentication...", style="bold yellow")
    try:
        token = auth.get_token(client_id, client_secret)
        settings = load_settings()
        settings.client_id = client_id
        settings.client_secret = client_secret
        settings.token = token
        save_settings(settings)
        console.print(
            "✅ Authentication successful! Your credentials have been saved.",
            style="bold green",
        )
    except Exception as e:
        console.print(
            f"❌ An error occurred during authentication: {e}", style="bold red"
        )
        raise typer.Exit(code=1)


@app.command()
def organize(
    length_filter: TrackLengthFilter = typer.Option(
        TrackLengthFilter.ALL,
        "--length-filter",
        "-f",
        case_sensitive=False,
        help="Filter tracks by length.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what tracks would be organized without making any changes.",
    ),
    scope: str | None = typer.Option(
        None,
        "--scope",
        "-s",
        help="Filter by time interval. E.g., 'last-month', 'ytd', '2023', '2023-01'.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging to the console.",
    ),
):
    """Fetch, filter, and organize tracks from your SoundCloud stream."""
    setup_logging(debug=debug)
    if dry_run:
        console.print(
            "🚀 Starting SoundCloud Organizer in [bold yellow]dry-run[/bold yellow] mode...",
            style="bold magenta",
        )
    else:
        console.print("🚀 Starting SoundCloud Organizer...", style="bold magenta")

    settings = load_settings()

    if not settings.token:
        console.print(
            "❌ You are not logged in. Please run 'soundcloud-organizer login' first.",
            style="bold red",
        )
        raise typer.Exit(code=1)

    try:
        session = auth.get_authenticated_session(settings)
        client = SoundCloudClient(session)
        process_stream(client, length_filter, console, dry_run, scope)
    except ValueError as e:
        console.print(
            f"❌ Error processing scope: {e}",
            style="bold red",
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"❌ An unexpected error occurred: {e}", style="bold red")
        raise typer.Exit(code=1)


def main():
    app()
