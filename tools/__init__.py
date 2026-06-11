"""
Auto-discovered tool plugins for H4X-Tools.

Add new tools by dropping a Python module into this package and subclassing
``tools.base.BaseTool``.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from functools import lru_cache

from helper import printer
from tools.base import BaseTool, ToolArgument, ensure_unique_tools


@lru_cache(maxsize=1)
def discover_tools() -> tuple[BaseTool, ...]:
    """Import every module in ``tools/`` and instantiate discovered tools."""
    package = importlib.import_module(__name__)
    discovered: list[BaseTool] = []

    for module_info in pkgutil.iter_modules(package.__path__, f"{__name__}."):
        module_name = module_info.name.rsplit(".", 1)[-1]
        if module_name.startswith("_") or module_name == "base":
            continue

        try:
            module = importlib.import_module(module_info.name)
        except Exception as exc:
            printer.warning(f"Skipping tool module {module_info.name}: {exc}")
            continue

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is BaseTool or not issubclass(obj, BaseTool):
                continue
            if obj.__module__ != module.__name__:
                continue
            discovered.append(obj())

    return tuple(ensure_unique_tools(discovered))


def get_tool(tool_id: str) -> BaseTool:
    """Return a discovered tool by ID."""
    for tool in discover_tools():
        if tool.id == tool_id:
            return tool
    raise KeyError(f"Unknown tool id: {tool_id}")


__all__ = ["BaseTool", "ToolArgument", "discover_tools", "get_tool"]
