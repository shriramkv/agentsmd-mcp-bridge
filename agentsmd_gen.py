"""Reverse direction: emit an AGENTS.md section from an MCP tool manifest.

Given a manifest describing the tools an MCP server exposes (the shape returned
by an MCP ``tools/list`` call), this produces a Markdown section documenting
those tools so that coding agents reading the repository's AGENTS.md know what
is available.
"""

from __future__ import annotations

import json
from typing import Any

from .models import ToolManifest, ToolSpec


def load_manifest(data: str | dict[str, Any]) -> ToolManifest:
    """Load a tool manifest from JSON text or a mapping.

    Accepts either the object returned by an MCP ``tools/list`` call
    (``{"tools": [...]}``) or a bare list of tools.

    Args:
        data: JSON string or already-parsed mapping/list.

    Returns:
        A ToolManifest.
    """
    obj: Any = json.loads(data) if isinstance(data, str) else data
    server = "mcp-server"
    if isinstance(obj, dict):
        server = obj.get("server", server)
        raw_tools = obj.get("tools", [])
    else:
        raw_tools = obj

    tools: list[ToolSpec] = []
    for t in raw_tools:
        tools.append(
            ToolSpec(
                name=t.get("name", "tool"),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", t.get("input_schema", {})) or {},
            )
        )
    return ToolManifest(server=server, tools=tools)


def _format_params(schema: dict[str, Any]) -> str:
    props = schema.get("properties", {})
    if not props:
        return "none"
    required = set(schema.get("required", []))
    parts = []
    for pname, pspec in props.items():
        ptype = pspec.get("type", "any")
        flag = "" if pname in required else " (optional)"
        parts.append(f"`{pname}`: {ptype}{flag}")
    return ", ".join(parts)


def generate_agentsmd_section(manifest: ToolManifest, heading: str = "MCP Tools") -> str:
    """Render an AGENTS.md Markdown section from a tool manifest.

    Args:
        manifest: The tools to document.
        heading: The section heading text.

    Returns:
        A Markdown string beginning with a level-two heading.
    """
    lines = [f"## {heading}", ""]
    lines.append(
        f"This repository exposes the following tools through the "
        f"`{manifest.server}` MCP server."
    )
    lines.append("")
    if not manifest.tools:
        lines.append("_No tools are currently exposed._")
        lines.append("")
        return "\n".join(lines)

    for tool in manifest.tools:
        lines.append(f"### `{tool.name}`")
        lines.append("")
        if tool.description:
            lines.append(tool.description.strip())
            lines.append("")
        lines.append(f"Parameters: {_format_params(tool.input_schema)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
