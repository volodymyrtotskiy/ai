"""
Tkinter user interface for the local assistant.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from calculator import CalculatorEngine
from command_parser import CommandParser
from tasks import TaskManager


class ThemeManager:
    """Manage light/dark palettes for the UI."""

    def __init__(self) -> None:
        self._themes = {
            "light": {
                "bg": "#f3f4f6",
                "panel_bg": "#ffffff",
                "text": "#111827",
                "muted": "#4b5563",
                "entry_bg": "#ffffff",
                "button_bg": "#e5e7eb",
                "button_fg": "#111827",
                "button_active_bg": "#d1d5db",
                "accent": "#2563eb",
            },
            "dark": {
                "bg": "#111827",
                "panel_bg": "#1f2937",
                "text": "#f9fafb",
                "muted": "#cbd5f5",
                "entry_bg": "#0f172a",
                "button_bg": "#374151",
                "button_fg": "#f9fafb",
                "button_active_bg": "#4b5563",
                "accent": "#60a5fa",
            },
        }
        self.current = "light"

    def toggle(self) -> None:
        self.current = "dark" if self.current == "light" else "light"

    def palette(self) -> dict[str, str]:
        return self._themes[self.current]


class HistoryPanel(tk.Frame):
    """Display and store calculation history."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.items: list[tuple[str, str]] = []

        self.title_label = tk.Label(self, text="History", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(anchor="w", padx=8, pady=(8, 4))

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.listbox = tk.Listbox(list_frame, height=12, exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=scrollbar.set)

    def add_item(self, expression: str, result: str) -> None:
        # Store items in a list so we can reuse the result on click.
        self.items.append((expression, result))
        self.listbox.insert("end", f"{expression} = {result}")
        self.listbox.see("end")

    def get_selected_result(self) -> str | None:
        selection = self.listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        return self.items[index][1]

    def apply_theme(self, palette: dict[str, str]) -> None:
        self.configure(bg=palette["panel_bg"])
        self.title_label.configure(bg=palette["panel_bg"], fg=palette["text"])
        self.listbox.configure(
            bg=palette["entry_bg"],
            fg=palette["text"],
            selectbackground=palette["accent"],
            selectforeground=palette["text"],
            highlightbackground=palette["panel_bg"],
        )


class TaskPanel(tk.Frame):
    """Display and manage a simple task list."""

    def __init__(self, parent: tk.Widget, manager: TaskManager) -> None:
        super().__init__(parent)
        self.manager = manager

        self.title_label = tk.Label(self, text="Tasks", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(anchor="w", padx=8, pady=(8, 4))

        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.listbox = tk.Listbox(list_frame, height=8, exportselection=False)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=scrollbar.set)

    def add_task(self, text: str) -> None:
        self.manager.add_task(text)
        self._refresh()

    def toggle_task(self, index: int) -> None:
        self.manager.toggle_task(index)
        self._refresh()

    def _refresh(self) -> None:
        self.listbox.delete(0, "end")
        for item in self.manager.get_tasks():
            marker = "[x]" if item["done"] else "[ ]"
            self.listbox.insert("end", f"{marker} {item['text']}")

    def apply_theme(self, palette: dict[str, str]) -> None:
        self.configure(bg=palette["panel_bg"])
        self.title_label.configure(bg=palette["panel_bg"], fg=palette["text"])
        self.listbox.configure(
            bg=palette["entry_bg"],
            fg=palette["text"],
            selectbackground=palette["accent"],
            selectforeground=palette["text"],
            highlightbackground=palette["panel_bg"],
        )


class CalculatorPad(tk.Frame):
    """Buttons for calculator input."""

    def __init__(
        self,
        parent: tk.Widget,
        on_insert: Callable[[str], None],
        on_clear: Callable[[], None],
        on_equals: Callable[[], None],
    ) -> None:
        super().__init__(parent)

        self.buttons: list[tk.Button] = []
        layout = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "(", ")"],
            ["%", "**", "+", "C"],
        ]

        for row_index, row in enumerate(layout):
            for col_index, label in enumerate(row):
                if label == "C":
                    command = on_clear
                else:
                    command = lambda token=label: on_insert(token)

                button = tk.Button(self, text=label, command=command, width=4, height=2)
                button.grid(row=row_index, column=col_index, sticky="nsew", padx=3, pady=3)
                self.buttons.append(button)

        # Equals button is wider and sits below the grid.
        equals_button = tk.Button(self, text="=", command=on_equals, height=2)
        equals_button.grid(
            row=len(layout),
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=3,
            pady=(6, 0),
        )
        self.buttons.append(equals_button)

        for col in range(4):
            self.grid_columnconfigure(col, weight=1)

    def apply_theme(self, palette: dict[str, str]) -> None:
        self.configure(bg=palette["panel_bg"])
        for button in self.buttons:
            button.configure(
                bg=palette["button_bg"],
                fg=palette["button_fg"],
                activebackground=palette["button_active_bg"],
                activeforeground=palette["button_fg"],
                highlightbackground=palette["panel_bg"],
            )


class AssistantApp(tk.Tk):
    """Main window for the desktop assistant."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Local AI Assistant")
        self.geometry("860x520")
        self.minsize(780, 480)

        self.engine = CalculatorEngine()
        self.parser = CommandParser()
        self.tasks = TaskManager()
        self.theme = ThemeManager()

        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        # Top area with title and theme switch.
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.title_label = tk.Label(
            self.top_frame, text="Local AI Assistant", font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side="left")

        self.theme_button = tk.Button(self.top_frame, text="Switch to Dark", command=self._toggle_theme)
        self.theme_button.pack(side="right")

        # Middle area with calculator and history.
        self.middle_frame = tk.Frame(self)
        self.middle_frame.pack(fill="both", expand=True, padx=16)

        self.calc_frame = tk.Frame(self.middle_frame, padx=12, pady=12)
        self.calc_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        self.right_frame = tk.Frame(self.middle_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.history_panel = HistoryPanel(self.right_frame)
        self.history_panel.pack(fill="both", expand=True, pady=(0, 12))
        self.history_panel.listbox.bind("<<ListboxSelect>>", self._on_history_select)

        self.task_panel = TaskPanel(self.right_frame, self.tasks)
        self.task_panel.pack(fill="both", expand=True)
        self.task_panel.listbox.bind("<Double-Button-1>", self._on_task_toggle)

        self.middle_frame.columnconfigure(0, weight=3)
        self.middle_frame.columnconfigure(1, weight=1)
        self.middle_frame.rowconfigure(0, weight=1)

        # Calculator input.
        self.expression_var = tk.StringVar()
        self.expression_entry = tk.Entry(
            self.calc_frame, textvariable=self.expression_var, font=("Consolas", 14)
        )
        self.expression_entry.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        self.expression_entry.bind("<Return>", self._on_equals)

        # Result display.
        self.result_var = tk.StringVar(value="Result: ")
        self.result_label = tk.Label(
            self.calc_frame, textvariable=self.result_var, font=("Segoe UI", 11), anchor="w"
        )
        self.result_label.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 12))

        # Calculator buttons.
        self.calc_pad = CalculatorPad(
            self.calc_frame, self._insert_token, self._clear_expression, self._evaluate_expression
        )
        self.calc_pad.grid(row=2, column=0, columnspan=4, sticky="nsew")

        for col in range(4):
            self.calc_frame.columnconfigure(col, weight=1)
        self.calc_frame.rowconfigure(2, weight=1)

        # Bottom command input.
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill="x", padx=16, pady=(8, 16))

        self.command_label = tk.Label(self.bottom_frame, text="Command:", font=("Segoe UI", 10))
        self.command_label.pack(side="left")

        self.command_entry = tk.Entry(self.bottom_frame, font=("Consolas", 11))
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.command_entry.bind("<Return>", self._on_command_submit)

        self.command_button = tk.Button(self.bottom_frame, text="Run", command=self._handle_command)
        self.command_button.pack(side="left")

        self.expression_entry.focus_set()

    def _insert_token(self, token: str) -> None:
        # Insert button text into the expression field at the cursor.
        self.expression_entry.insert(tk.INSERT, token)
        self.expression_entry.focus_set()

    def _clear_expression(self) -> None:
        self.expression_var.set("")
        self._set_result("")

    def _set_result(self, message: str) -> None:
        display = f"Result: {message}" if message else "Result: "
        self.result_var.set(display)

    def _evaluate_expression(self) -> None:
        raw_input = self.expression_var.get().strip()
        # Allow natural language math in the calculator input field.
        command_type, payload = self.parser.parse_command(raw_input)
        expression = payload if command_type == "math" else raw_input
        success, result = self.engine.evaluate(expression)
        self._set_result(result)

        if success:
            self.history_panel.add_item(expression, result)

    def _on_equals(self, event: tk.Event | None = None) -> None:
        self._evaluate_expression()

    def _on_command_submit(self, event: tk.Event | None = None) -> None:
        self._handle_command()

    def _handle_command(self) -> None:
        command_text = self.command_entry.get().strip()
        self.command_entry.delete(0, "end")

        if not command_text:
            return

        command_type, payload = self.parser.parse_command(command_text)
        if command_type == "task":
            self.task_panel.add_task(payload)
            self._set_result("Task added.")
            return

        if command_type == "math":
            self.expression_var.set(payload)
            self._evaluate_expression()
            return

        self._set_result("I currently only understand math and task commands.")

    def _on_history_select(self, event: tk.Event | None = None) -> None:
        result = self.history_panel.get_selected_result()
        if result:
            # Reuse the result by placing it into the expression field.
            self.expression_var.set(result)
            self.expression_entry.focus_set()

    def _on_task_toggle(self, event: tk.Event | None = None) -> None:
        selection = self.task_panel.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self.task_panel.toggle_task(index)

    def _toggle_theme(self) -> None:
        self.theme.toggle()
        self._apply_theme()

    def _apply_theme(self) -> None:
        palette = self.theme.palette()
        self.configure(bg=palette["bg"])

        # Frames
        self.top_frame.configure(bg=palette["bg"])
        self.middle_frame.configure(bg=palette["bg"])
        self.calc_frame.configure(bg=palette["panel_bg"])
        self.right_frame.configure(bg=palette["bg"])
        self.bottom_frame.configure(bg=palette["bg"])

        # Labels and entries
        self.title_label.configure(bg=palette["bg"], fg=palette["text"])
        self.result_label.configure(bg=palette["panel_bg"], fg=palette["muted"])
        self.command_label.configure(bg=palette["bg"], fg=palette["text"])

        self.expression_entry.configure(
            bg=palette["entry_bg"],
            fg=palette["text"],
            insertbackground=palette["text"],
            highlightbackground=palette["panel_bg"],
        )
        self.command_entry.configure(
            bg=palette["entry_bg"],
            fg=palette["text"],
            insertbackground=palette["text"],
            highlightbackground=palette["bg"],
        )

        # Buttons
        self.theme_button.configure(
            bg=palette["button_bg"],
            fg=palette["button_fg"],
            activebackground=palette["button_active_bg"],
            activeforeground=palette["button_fg"],
            highlightbackground=palette["bg"],
            text="Switch to Light" if self.theme.current == "dark" else "Switch to Dark",
        )
        self.command_button.configure(
            bg=palette["button_bg"],
            fg=palette["button_fg"],
            activebackground=palette["button_active_bg"],
            activeforeground=palette["button_fg"],
            highlightbackground=palette["bg"],
        )

        self.calc_pad.apply_theme(palette)
        self.history_panel.apply_theme(palette)
        self.task_panel.apply_theme(palette)
