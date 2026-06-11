"""
Copyright (c) 2023-2026. Vili and contributors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Iterable


@dataclass(frozen=True)
class ToolArgument:
    """
    Metadata for a value a tool accepts from the CLI.

    The first argument of a tool can be supplied directly through the tool's
    shortcut flags, for example ``--ip example.com``. If the flag is provided
    without a value, ``None`` is passed to the tool so it can prompt
    interactively.
    """

    name: str
    metavar: str
    help_text: str
    flags: tuple[str, ...] = ()
    parser_type: Callable[[str], Any] | None = None
    default: Any = None


class BaseTool:
    """
    Base class for every H4X-Tools plugin.

    To add a tool, create a new ``tools/my_tool.py`` file, subclass
    ``BaseTool``, fill in the class metadata, and implement ``run``. The app
    discovers subclasses automatically at startup and uses the metadata for the
    menu, help text, and direct CLI flags.
    """

    id: ClassVar[str]
    name: ClassVar[str]
    description: ClassVar[str]
    order: ClassVar[int] = 999
    aliases: ClassVar[tuple[str, ...]] = ()
    arguments: ClassVar[tuple[ToolArgument, ...]] = ()

    @property
    def cli_dest(self) -> str:
        return f"tool_{self.id}"

    def validate(self) -> None:
        if not getattr(self, "id", None):
            raise ValueError(f"{self.__class__.__name__} is missing an id")
        if not getattr(self, "name", None):
            raise ValueError(f"{self.__class__.__name__} is missing a name")
        if not getattr(self, "description", None):
            raise ValueError(f"{self.__class__.__name__} is missing a description")
        if not self.aliases:
            raise ValueError(f"{self.__class__.__name__} is missing CLI aliases")

    def add_cli_arguments(self, group: argparse._ArgumentGroup) -> None:
        """Add this tool's direct-run flags to an argparse group."""
        if self.arguments:
            primary = self.arguments[0]
            primary_kwargs: dict[str, Any] = {
                "dest": self.cli_dest,
                "nargs": "?",
                "const": True,
                "default": None,
                "metavar": primary.metavar,
                "help": primary.help_text,
            }
            if primary.parser_type is not None:
                primary_kwargs["type"] = primary.parser_type
            group.add_argument(*self.aliases, **primary_kwargs)

            for argument in self.arguments[1:]:
                if not argument.flags:
                    continue

                argument_kwargs: dict[str, Any] = {
                    "dest": argument.name,
                    "default": argument.default,
                    "metavar": argument.metavar,
                    "help": argument.help_text,
                }
                if argument.parser_type is not None:
                    argument_kwargs["type"] = argument.parser_type
                group.add_argument(*argument.flags, **argument_kwargs)
            return

        group.add_argument(
            *self.aliases,
            dest=self.cli_dest,
            action="store_true",
            help=self.description,
        )

    def selected(self, args: argparse.Namespace) -> bool:
        value = getattr(args, self.cli_dest, None)
        return value is not None if self.arguments else bool(value)

    def cli_values(self, args: argparse.Namespace) -> list[Any]:
        """Build positional values for ``run`` from parsed CLI args."""
        if not self.arguments:
            return []

        values: list[Any] = []
        primary_value = getattr(args, self.cli_dest)
        values.append(
            None if primary_value is True or primary_value is None else primary_value
        )

        for argument in self.arguments[1:]:
            values.append(getattr(args, argument.name, argument.default))

        return values

    def run_from_cli(self, args: argparse.Namespace) -> None:
        self.run(*self.cli_values(args))

    def run(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError


def ensure_unique_tools(tools: Iterable[BaseTool]) -> list[BaseTool]:
    """Validate tool metadata and reject duplicate IDs or menu orders."""
    validated = list(tools)
    seen_ids: set[str] = set()
    seen_aliases: set[str] = set()

    for tool in validated:
        tool.validate()
        if tool.id in seen_ids:
            raise ValueError(f"Duplicate tool id: {tool.id}")
        seen_ids.add(tool.id)

        for alias in tool.aliases:
            if alias in seen_aliases:
                raise ValueError(f"Duplicate tool alias: {alias}")
            seen_aliases.add(alias)

        for argument in tool.arguments:
            for flag in argument.flags:
                if flag in seen_aliases:
                    raise ValueError(f"Duplicate tool argument flag: {flag}")
                seen_aliases.add(flag)

    return sorted(validated, key=lambda tool: (tool.order, tool.name.lower()))
