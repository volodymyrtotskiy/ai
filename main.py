"""
Program entry point for the local desktop assistant.
"""

import argparse

from ui import AssistantApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Local AI assistant")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Serve the AI dashboard in the browser instead of the desktop UI",
    )
    parser.add_argument("--host", default="127.0.0.1", help="With --web: bind address")
    parser.add_argument("--port", type=int, default=8765, help="With --web: port")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="With --web: do not open a browser tab",
    )
    args = parser.parse_args()

    if args.web:
        from serve_dashboard import run as serve_dashboard

        serve_dashboard(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return

    app = AssistantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
