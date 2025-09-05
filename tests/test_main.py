"""Tests for the main CLI application."""

from typer.testing import CliRunner

from soundcloud_organizer.main import app

runner = CliRunner()


def test_organize_command_has_debug_flag():
    """Tests that the --debug flag is available on the 'organize' command."""
    # Set a wide terminal width to prevent rich/typer from truncating help text
    result = runner.invoke(app, ["organize", "--help"], env={"COLUMNS": "120"})
    assert result.exit_code == 0
    assert "--debug" in result.stdout
    assert "Enable debug logging to the console." in result.stdout
