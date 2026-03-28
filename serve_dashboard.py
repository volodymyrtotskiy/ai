"""
Serve the AI dashboard HTML over HTTP (stdlib only).

Usage:
  python serve_dashboard.py
  python serve_dashboard.py --port 8080 --bind 127.0.0.1
"""

from __future__ import annotations

import argparse
import http.server
import socketserver
import webbrowser
from pathlib import Path

DASHBOARD_FILE = "ai-dashboard.html"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def make_handler(root: Path):
    class DashboardHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def do_GET(self) -> None:
            clean = self.path.split("?", 1)[0]
            if clean in ("/", "/index.html"):
                self.path = f"/{DASHBOARD_FILE}"
            return super().do_GET()

    return DashboardHandler


def run(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    open_browser: bool = True,
) -> None:
    root = _repo_root()
    dashboard = root / DASHBOARD_FILE
    if not dashboard.is_file():
        raise SystemExit(f"Missing {dashboard}")

    handler = make_handler(root)
    with socketserver.TCPServer((host, port), handler) as httpd:
        url = f"http://{host}:{port}/"
        print(f"Serving {root} at {url}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the AI dashboard over HTTP.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser tab")
    args = parser.parse_args()
    run(host=args.host, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
