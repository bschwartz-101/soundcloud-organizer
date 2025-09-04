import typer
from rich.console import Console

from soundcloud_organizer import auth
from soundcloud_organizer.config import load_settings, save_settings

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


def main():
    app()
