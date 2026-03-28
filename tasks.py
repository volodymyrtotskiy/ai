"""
Task manager for storing simple text-based tasks.
"""

from __future__ import annotations


class TaskManager:
    """Store tasks in memory and manage completion state."""

    def __init__(self) -> None:
        self._tasks: list[dict[str, object]] = []

    def add_task(self, text: str) -> None:
        # Store each task with a completion flag.
        self._tasks.append({"text": text, "done": False})

    def toggle_task(self, index: int) -> None:
        if 0 <= index < len(self._tasks):
            self._tasks[index]["done"] = not self._tasks[index]["done"]

    def get_tasks(self) -> list[dict[str, object]]:
        return list(self._tasks)
