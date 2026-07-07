"""Command-line interface for agentsmd-mcp-bridge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .agentsmd_gen import generate_agentsmd_section, load_manifest
from .extractor import extract_commands
from .mcp_gen import generate_mcp_server
from .parser import parse_agents_md


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _cmd_generate_mcp(args: argparse.Namespace) -> int:
    doc = parse_agents_md(_read(args.agents_md))
    commands = extract_commands(doc, strict=args.strict)
    if not commands:
        print("no commands found in AGENTS.md", file=sys.stderr)
        return 2
    source = generate_mcp_server(commands, server_name=args.server, out_path=args.output or "mcp_server.py")
    if args.output:
        Path(args.output).write_text(source, encoding="utf-8")
        print(f"wrote {args.output} with {len(commands)} tool(s)")
    else:
        sys.stdout.write(source)
    return 0


def _cmd_list_commands(args: argparse.Namespace) -> int:
    doc = parse_agents_md(_read(args.agents_md))
    commands = extract_commands(doc, strict=args.strict)
    if not commands:
        print("no commands found", file=sys.stderr)
        return 2
    for c in commands:
        print(f"{c.name}\t{c.command}")
    return 0


def _cmd_generate_agentsmd(args: argparse.Namespace) -> int:
    manifest = load_manifest(_read(args.manifest))
    section = generate_agentsmd_section(manifest, heading=args.heading)
    if args.output:
        Path(args.output).write_text(section, encoding="utf-8")
        print(f"wrote {args.output} with {len(manifest.tools)} tool(s)")
    else:
        sys.stdout.write(section)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agentsmd-mcp-bridge",
        description=(
            "Bridge AGENTS.md and MCP: generate an MCP server from "
            "AGENTS.md, or an AGENTS.md section from an MCP manifest."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate-mcp", help="generate an MCP server from AGENTS.md")
    g.add_argument("agents_md", help="path to AGENTS.md")
    g.add_argument("-o", "--output", help="output path (default: stdout)")
    g.add_argument("-s", "--server", default="agentsmd-bridge", help="MCP server name")
    g.add_argument("--strict", action="store_true", help="only use command-like headings")
    g.set_defaults(func=_cmd_generate_mcp)

    lc = sub.add_parser("list-commands", help="list commands extracted from AGENTS.md")
    lc.add_argument("agents_md", help="path to AGENTS.md")
    lc.add_argument("--strict", action="store_true", help="only use command-like headings")
    lc.set_defaults(func=_cmd_list_commands)

    r = sub.add_parser("generate-agentsmd", help="generate an AGENTS.md section from an MCP manifest")
    r.add_argument("manifest", help="path to a JSON tool manifest")
    r.add_argument("-o", "--output", help="output path (default: stdout)")
    r.add_argument("--heading", default="MCP Tools", help="section heading")
    r.set_defaults(func=_cmd_generate_agentsmd)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
