"""Test suite for agentsmd-mcp-bridge."""

from __future__ import annotations

import ast
import json

import pytest

from agentsmd_mcp_bridge import (
    extract_commands,
    generate_agentsmd_section,
    generate_mcp_server,
    load_manifest,
    parse_agents_md,
)
from agentsmd_mcp_bridge.models import Command

SAMPLE = """# My Project

Some intro text about the project.

## Build

Build the project:

```bash
npm run build
```

## Test

```sh
pytest -q
ruff check .
```

## Notes

Just prose, `not a command` here but `pytest tests/` is one.

## Deploy

Deploy with `docker compose up -d`.
"""


# ---------- parser ----------

def test_parse_title_and_sections():
    doc = parse_agents_md(SAMPLE)
    assert doc.title == "My Project"
    assert "Build" in doc.sections
    assert "Test" in doc.sections
    assert "Deploy" in doc.sections


def test_parse_code_blocks_captured():
    doc = parse_agents_md(SAMPLE)
    assert any("npm run build" in b for b in doc.code_blocks["Build"])
    assert any("pytest -q" in b for b in doc.code_blocks["Test"])


def test_parse_unterminated_fence_is_graceful():
    doc = parse_agents_md("## Build\n```bash\nnpm run build\n")
    assert any("npm run build" in b for b in doc.code_blocks["Build"])


def test_parse_content_before_first_heading():
    doc = parse_agents_md("intro line\n# Title\nbody\n")
    assert "intro line" in doc.sections[""]
    assert doc.title == "Title"


# ---------- extractor ----------

def test_extract_finds_code_block_commands():
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    commands = {c.command for c in cmds}
    assert "npm run build" in commands
    assert "pytest -q" in commands
    assert "ruff check ." in commands


def test_extract_names_are_unique_and_safe():
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    names = [c.name for c in cmds]
    assert len(names) == len(set(names)), "tool names must be unique"
    for n in names:
        assert n.replace("_", "").isalnum()


def test_extract_inline_commands_under_command_heading():
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    commands = {c.command for c in cmds}
    # 'docker compose up -d' appears inline under the Deploy heading
    assert "docker compose up -d" in commands


def test_extract_ignores_prose_backticks():
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    commands = {c.command for c in cmds}
    assert "not a command" not in commands


def test_extract_strict_mode_filters_non_command_headings():
    text = "## Random\n```bash\nnpm run build\n```\n"
    doc = parse_agents_md(text)
    assert extract_commands(doc, strict=True) == []
    assert len(extract_commands(doc, strict=False)) == 1


# ---------- mcp generator ----------

def test_generate_mcp_server_is_valid_python():
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    source = generate_mcp_server(cmds, server_name="test-server")
    ast.parse(source)  # raises SyntaxError if invalid


def test_generate_mcp_server_contains_tools_and_server_name():
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    source = generate_mcp_server(cmds, server_name="my-srv")
    assert 'FastMCP("my-srv")' in source
    for c in cmds:
        assert f"def {c.name}(" in source
        assert repr(c.command) in source


def test_generate_mcp_server_empty_raises():
    with pytest.raises(ValueError):
        generate_mcp_server([])


def test_generate_mcp_server_deduplicates_tool_names():
    cmds = [
        Command(name="build", description="d", command="a"),
        Command(name="build", description="d", command="b"),
    ]
    source = generate_mcp_server(cmds)
    assert source.count("def build(") == 1


# ---------- reverse generator ----------

MANIFEST = {
    "server": "demo",
    "tools": [
        {
            "name": "search",
            "description": "Search the index.",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {"name": "ping", "description": "", "inputSchema": {}},
    ],
}


def test_load_manifest_from_json_string():
    m = load_manifest(json.dumps(MANIFEST))
    assert m.server == "demo"
    assert [t.name for t in m.tools] == ["search", "ping"]


def test_load_manifest_from_bare_list():
    m = load_manifest([{"name": "x"}])
    assert m.tools[0].name == "x"


def test_generate_agentsmd_section_renders_tools_and_params():
    m = load_manifest(MANIFEST)
    md = generate_agentsmd_section(m)
    assert md.startswith("## MCP Tools")
    assert "### `search`" in md
    assert "`query`: string" in md
    assert "Parameters: none" in md  # for ping


def test_generate_agentsmd_section_empty_manifest():
    m = load_manifest({"tools": []})
    md = generate_agentsmd_section(m)
    assert "No tools" in md


def test_custom_heading():
    m = load_manifest(MANIFEST)
    md = generate_agentsmd_section(m, heading="Available Tools")
    assert md.startswith("## Available Tools")


# ---------- round trip ----------

def test_round_trip_names_survive():
    """Commands -> MCP server source should mention every tool name once."""
    doc = parse_agents_md(SAMPLE)
    cmds = extract_commands(doc)
    source = generate_mcp_server(cmds)
    for c in cmds:
        assert source.count(f"def {c.name}(") == 1
