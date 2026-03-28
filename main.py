"""
Program entry point for the local desktop assistant.
"""

from ui import AssistantApp


def main() -> None:
    # Start the Tkinter application.
    app = AssistantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
