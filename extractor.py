"""Extract runnable commands from a parsed AGENTS.md document.

Heuristics, in order of preference:
  1. Fenced code blocks under command-like headings (Build, Test, Lint, ...).
  2. Inline back-ticked commands in the prose under those headings.

Each extracted command is given a safe snake_case tool name derived from its
heading, de-duplicated with a numeric suffix where necessary.
"""

from __future__ import annotations

import re

from .models import AgentsDoc, Command

# headings whose content is likely to contain runnable commands
_COMMAND_KEYWORDS = (
    "build", "test", "tests", "lint", "linting", "run", "start", "setup",
    "install", "dev", "develop", "format", "typecheck", "type check", "check",
    "compile", "deploy", "clean", "coverage", "bench", "benchmark", "commands",
    "usage", "scripts", "task", "tasks",
)

_INLINE_CODE = re.compile(r"`([^`]+)`")
# a line looks like a shell command if it starts with a known launcher
_LAUNCHER = re.compile(
    r"^(npm|pnpm|yarn|npx|pip|pip3|python|python3|pytest|ruff|black|mypy|"
    r"make|cargo|go|node|bash|sh|docker|uv|poetry|tox|nox|coverage|flake8|"
    r"eslint|prettier|tsc|gradle|mvn|dotnet)\b"
)


def _safe_name(text: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    if not name:
        name = "command"
    if name[0].isdigit():
        name = "cmd_" + name
    return name


def _looks_like_command(line: str) -> bool:
    line = line.strip()
    if not line or line.startswith("#"):
        return False
    return bool(_LAUNCHER.match(line))


def _heading_is_command_like(heading: str) -> bool:
    low = heading.lower()
    return any(kw in low for kw in _COMMAND_KEYWORDS)


def extract_commands(doc: AgentsDoc, *, strict: bool = False) -> list[Command]:
    """Extract commands from a parsed AGENTS.md document.

    Args:
        doc: The parsed document.
        strict: If True, only consider headings that look command-like. If
            False (default), also scan code blocks under any heading, but still
            only keep lines that look like shell commands.

    Returns:
        A list of Command objects with unique, safe tool names.
    """
    commands: list[Command] = []
    used: dict[str, int] = {}

    def add(section: str, cmd_line: str) -> None:
        base = _safe_name(section) or "command"
        if base in used:
            used[base] += 1
            name = f"{base}_{used[base]}"
        else:
            used[base] = 0
            name = base
        desc = section.strip() or "Run a documented command"
        commands.append(Command(name=name, description=desc, command=cmd_line.strip(), section=section))

    for heading, blocks in doc.code_blocks.items():
        if strict and heading and not _heading_is_command_like(heading):
            continue
        for block in blocks:
            for line in block.splitlines():
                if _looks_like_command(line):
                    add(heading or "command", line)

    # fall back to inline back-ticked commands under command-like headings
    for heading, body in doc.sections.items():
        if not _heading_is_command_like(heading):
            continue
        for match in _INLINE_CODE.findall(body):
            if _looks_like_command(match):
                # avoid duplicates already captured from code blocks
                if not any(c.command == match.strip() for c in commands):
                    add(heading, match)

    return commands
