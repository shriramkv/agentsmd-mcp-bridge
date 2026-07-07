"""Tests for the command-line interface and remaining edge cases."""

from __future__ import annotations

import ast
import json

import pytest

from agentsmd_mcp_bridge.cli import main
from agentsmd_mcp_bridge.models import Command

AGENTS = """# Demo

## Build
```bash
npm run build
```

## Test
```bash
pytest -q
```
"""

MANIFEST = {"server": "demo", "tools": [{"name": "ping", "description": "Ping.", "inputSchema": {}}]}


@pytest.fixture()
def agents_file(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text(AGENTS, encoding="utf-8")
    return p


@pytest.fixture()
def manifest_file(tmp_path):
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(MANIFEST), encoding="utf-8")
    return p


def test_cli_generate_mcp_to_file(agents_file, tmp_path, capsys):
    out = tmp_path / "mcp_server.py"
    rc = main(["generate-mcp", str(agents_file), "-o", str(out), "-s", "srv"])
    assert rc == 0
    src = out.read_text(encoding="utf-8")
    ast.parse(src)
    assert 'FastMCP("srv")' in src
    assert "wrote" in capsys.readouterr().out


def test_cli_generate_mcp_to_stdout(agents_file, capsys):
    rc = main(["generate-mcp", str(agents_file)])
    assert rc == 0
    assert "FastMCP" in capsys.readouterr().out


def test_cli_list_commands(agents_file, capsys):
    rc = main(["list-commands", str(agents_file)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "npm run build" in out
    assert "pytest -q" in out


def test_cli_generate_mcp_no_commands(tmp_path, capsys):
    empty = tmp_path / "AGENTS.md"
    empty.write_text("# Nothing here\n\nJust prose.\n", encoding="utf-8")
    rc = main(["generate-mcp", str(empty)])
    assert rc == 2
    assert "no commands" in capsys.readouterr().err


def test_cli_list_commands_no_commands(tmp_path, capsys):
    empty = tmp_path / "AGENTS.md"
    empty.write_text("# Nothing\n", encoding="utf-8")
    rc = main(["list-commands", str(empty)])
    assert rc == 2


def test_cli_generate_agentsmd_to_file(manifest_file, tmp_path, capsys):
    out = tmp_path / "section.md"
    rc = main(["generate-agentsmd", str(manifest_file), "-o", str(out)])
    assert rc == 0
    assert "### `ping`" in out.read_text(encoding="utf-8")
    assert "wrote" in capsys.readouterr().out


def test_cli_generate_agentsmd_to_stdout(manifest_file, capsys):
    rc = main(["generate-agentsmd", str(manifest_file), "--heading", "Tools"])
    assert rc == 0
    assert "## Tools" in capsys.readouterr().out


def test_cli_strict_flag(agents_file, capsys):
    rc = main(["list-commands", str(agents_file), "--strict"])
    assert rc == 0
    assert "npm run build" in capsys.readouterr().out


def test_cli_requires_subcommand():
    with pytest.raises(SystemExit):
        main([])


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


# ---- model validation edge cases ----

def test_command_empty_name_raises():
    with pytest.raises(ValueError):
        Command(name="", description="d", command="x")


def test_command_empty_command_raises():
    with pytest.raises(ValueError):
        Command(name="n", description="d", command="   ")
