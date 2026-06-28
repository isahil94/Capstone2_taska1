"""Hooks system - Event-driven automation."""

from __future__ import annotations

from typing import Callable, Any


class HookRegistry:
    """Manages event hooks for the agent system."""

    def __init__(self):
        self._hooks: dict[str, list[Callable]] = {
            "on_analysis_complete": [],
            "on_file_modified": [],
            "on_graph_built": [],
        }

    def register(self, event: str, callback: Callable) -> None:
        """Register a callback for an event."""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    def trigger(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Trigger all callbacks for an event."""
        if event not in self._hooks:
            return

        for callback in self._hooks[event]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Hook error ({event}): {str(e)}")

    def clear(self, event: str | None = None) -> None:
        """Clear hooks for an event or all events."""
        if event:
            self._hooks[event] = []
        else:
            for key in self._hooks:
                self._hooks[key] = []


# Global hook registry
_registry = HookRegistry()


def register(event: str, callback: Callable) -> None:
    """Register a hook callback."""
    _registry.register(event, callback)


def trigger(event: str, *args: Any, **kwargs: Any) -> None:
    """Trigger a hook event."""
    _registry.trigger(event, *args, **kwargs)


def get_registry() -> HookRegistry:
    """Get the global hook registry."""
    return _registry
