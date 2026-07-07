"""Typed data models shared across the bridge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Command:
    """A single command extracted from an AGENTS.md file.

    Attributes:
        name: A safe identifier used as the MCP tool name (snake_case).
        description: Human-readable description, taken from the source heading.
        command: The shell command string to execute.
        section: The AGENTS.md heading the command was found under.
    """

    name: str
    description: str
    command: str
    section: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Command.name must not be empty")
        if not self.command.strip():
            raise ValueError("Command.command must not be empty")


@dataclass
class AgentsDoc:
    """A parsed AGENTS.md document.

    Attributes:
        title: The first level-one heading, if present.
        sections: Mapping of heading text to the raw body under it.
        code_blocks: Mapping of heading text to the fenced code blocks under it.
    """

    title: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    code_blocks: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class ToolSpec:
    """A single tool in an MCP manifest."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolManifest:
    """A manifest of MCP tools, typically obtained from a running server."""

    server: str = "mcp-server"
    tools: list[ToolSpec] = field(default_factory=list)
