"""Parse an AGENTS.md file into structured sections and code blocks.

The parser is deliberately dependency-free and forgiving. It walks the document
line by line, tracking the current heading and collecting both the prose body
and any fenced code blocks that appear under each heading.
"""

from __future__ import annotations

import re

from .models import AgentsDoc

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE = re.compile(r"^```(.*)$")


def parse_agents_md(text: str) -> AgentsDoc:
    """Parse the text of an AGENTS.md file.

    Args:
        text: The full contents of an AGENTS.md file.

    Returns:
        An AgentsDoc with the title, per-heading prose and per-heading code
        blocks. Content that appears before the first heading is stored under
        the empty-string key.
    """
    doc = AgentsDoc()
    current = ""  # heading key for content before the first heading
    doc.sections.setdefault(current, "")
    doc.code_blocks.setdefault(current, [])

    in_fence = False
    fence_lines: list[str] = []

    for line in text.splitlines():
        fence = _FENCE.match(line)
        if fence:
            if in_fence:
                doc.code_blocks[current].append("\n".join(fence_lines))
                fence_lines = []
                in_fence = False
            else:
                in_fence = True
            continue

        if in_fence:
            fence_lines.append(line)
            continue

        heading = _HEADING.match(line)
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip()
            if level == 1 and not doc.title:
                doc.title = title
            current = title
            doc.sections.setdefault(current, "")
            doc.code_blocks.setdefault(current, [])
            continue

        doc.sections[current] = (doc.sections[current] + line + "\n") if doc.sections[current] else line + "\n"

    # close an unterminated fence gracefully
    if in_fence and fence_lines:
        doc.code_blocks[current].append("\n".join(fence_lines))

    return doc
