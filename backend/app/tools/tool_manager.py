
from collections.abc import Callable
from typing import Any


class ToolManager:
    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        function: Callable[..., Any],
        description: str,
        arguments: dict[str, str],
    ) -> None:
        if not name or not name.strip():
            raise ValueError("Tool name cannot be empty.")

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        if not callable(function):
            raise TypeError("Tool must be callable.")

        if not isinstance(arguments, dict):
            raise TypeError("Tool arguments must be a dictionary.")

        self._tools[name] = {
            "function": function,
            "description": description,
            "arguments": arguments,
        }

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "description": tool["description"],
                "arguments": tool["arguments"],
            }
            for name, tool in self._tools.items()
        ]

    def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            raise TypeError("Tool arguments must be a dictionary.")

        tool = self._tools[name]
        expected = tool["arguments"]

        missing = set(expected) - set(arguments)
        unexpected = set(arguments) - set(expected)

        if missing:
            raise ValueError(
                f"Missing arguments for {name}: {sorted(missing)}"
            )

        if unexpected:
            raise ValueError(
                f"Unexpected arguments for {name}: {sorted(unexpected)}"
            )

        return tool["function"](**arguments)
