"""Handles SoundCloud OAuth2 authentication flow."""

import http.server
import socketserver
import threading
import webbrowser
from typing import Optional
from urllib.parse import parse_qs, urlparse

from loguru import logger
from requests_oauthlib import OAuth2Session

from soundcloud_organizer.config import Settings, Token, save_settings

# SoundCloud API OAuth2 URLs
AUTHORIZATION_URL = "https://secure.soundcloud.com/authorize"
TOKEN_URL = "https://secure.soundcloud.com/oauth/token"

# Local server settings for the redirect
REDIRECT_URI = "http://127.0.0.1:8080/"


def get_token(client_id: str, client_secret: str) -> Token:
    """
    Guides the user through the OAuth2 flow to get an access token.

    This function will:
    1. Generate a SoundCloud authorization URL.
    2. Open the URL in the user's web browser.
    3. Start a temporary local web server to catch the redirect.
    4. Exchange the received authorization code for an access token.

    Args:
        client_id: The SoundCloud application client ID.
        client_secret: The SoundCloud application client secret.

    Returns:
        A Token object containing the access token and other details.
    """
    auth_code: Optional[str] = None

    # Use a threading.Event to signal when the code is received
    code_received = threading.Event()

    class AuthHandler(http.server.SimpleHTTPRequestHandler):
        """A simple handler to capture the OAuth2 authorization code."""

        def do_GET(self) -> None:
            nonlocal auth_code
            query_components = parse_qs(urlparse(self.path).query)
            if "code" in query_components:
                auth_code = query_components["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authentication successful!</h1><p>You can close this window.</p>"
                )
                code_received.set()  # Signal that the code has been received
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(
                    b"<h1>Error</h1><p>Could not find authorization code in the request.</p>"
                )

    with socketserver.TCPServer(("", 8080), AuthHandler) as httpd:
        # Start the server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Enable PKCE (Proof Key for Code Exchange) as required by SoundCloud's API
        # See: https://developers.soundcloud.com/docs/api/guide#auth-code
        soundcloud = OAuth2Session(client_id, redirect_uri=REDIRECT_URI, pkce="S256")
        authorization_url, _ = soundcloud.authorization_url(AUTHORIZATION_URL)

        logger.info(f"Opening browser for authentication: {authorization_url}")
        webbrowser.open(authorization_url)

        code_received.wait()  # Wait for the handler to receive the code
        httpd.shutdown()

    token_data = soundcloud.fetch_token(
        TOKEN_URL,
        client_secret=client_secret,
        code=auth_code,
        # The SoundCloud API expects client_id and client_secret in the body,
        # not as a Basic Auth header. `include_client_id` forces this.
        include_client_id=True,
    )
    return Token.model_validate(token_data)


def get_authenticated_session(settings: Settings) -> OAuth2Session:
    """
    Creates and returns an authenticated OAuth2Session that handles token refreshes.

    Args:
        settings: The application settings containing client credentials and token.

    Returns:
        An authenticated OAuth2Session instance.

    Raises:
        ValueError: If client_id, client_secret, or token is missing from settings.
    """
    if not all([settings.client_id, settings.client_secret, settings.token]):
        raise ValueError(
            "Client ID, Client Secret, and Token must be configured for an authenticated session."
        )

    def token_updater(new_token_data: dict):
        """Callback function to save the refreshed token."""
        logger.debug("OAuth token has been refreshed, saving new token to config.")
        settings.token = Token.model_validate(new_token_data)
        save_settings(settings)

    # Extra parameters needed for the token refresh request
    extra = {
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
    }

    return OAuth2Session(
        client_id=settings.client_id,
        token=settings.token.model_dump(),
        auto_refresh_url=TOKEN_URL,
        auto_refresh_kwargs=extra,
        token_updater=token_updater,
    )
