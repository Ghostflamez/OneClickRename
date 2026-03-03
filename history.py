"""
Undo/redo stack using Command Pattern.
Each action stores before/after file paths for reversal.
"""

from collections import deque
from pathlib import Path

MAX_STACK_DEPTH = 50


class History:
    """
    Manages undo/redo operations for file renames.

    Each action is a dict:
        {"before": list[Path], "after": list[Path]}
    """

    def __init__(self):
        self._undo_stack: deque[dict] = deque(maxlen=MAX_STACK_DEPTH)
        self._redo_stack: deque[dict] = deque(maxlen=MAX_STACK_DEPTH)

    def push(self, action: dict) -> None:
        """
        Record a new action. Clears redo stack.

        Args:
            action: Dict with "before" and "after" lists of Path objects
        """
        self._undo_stack.append(action)
        self._redo_stack.clear()

    def undo(self) -> dict | None:
        """
        Pop the last action for undoing.

        Returns:
            The action dict to undo, or None if stack is empty
        """
        if not self._undo_stack:
            return None
        action = self._undo_stack.pop()
        self._redo_stack.append(action)
        return action

    def redo(self) -> dict | None:
        """
        Pop the last undone action for redoing.

        Returns:
            The action dict to redo, or None if stack is empty
        """
        if not self._redo_stack:
            return None
        action = self._redo_stack.pop()
        self._undo_stack.append(action)
        return action

    def can_undo(self) -> bool:
        """Check if there are actions to undo."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if there are actions to redo."""
        return len(self._redo_stack) > 0

    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
