# agentsmd-mcp-bridge

[![CI](https://github.com/shriramkv/agentsmd-mcp-bridge/actions/workflows/ci.yml/badge.svg)](https://github.com/shriramkv/agentsmd-mcp-bridge/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20to%203.13-1F3864.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-2A9D8F.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-98%25-2A9D8F.svg)](#tests)

**Turn a repository's `AGENTS.md` into a working MCP server, and back again.**

`AGENTS.md` tells a coding agent, in prose, how to build, test and run a
project. The Model Context Protocol (MCP) lets an agent actually *call* tools.
This bridge closes the gap between the two: it reads the commands a repository
documents for agents and generates an MCP server that exposes those commands as
callable tools, so an agent can run a project's real build and test commands
instead of merely reading about them. It also runs in reverse, turning an MCP
server's tool manifest into an `AGENTS.md` section.

Both `AGENTS.md` and MCP are founding projects of the Linux Foundation's
Agentic AI Foundation (AAIF); this tool sits at the seam between them.

![architecture](docs/architecture.png)

## Why

- **`AGENTS.md` is human-readable, MCP is machine-callable.** Teams already
  document their build and test commands for agents. This makes that
  documentation executable, with no duplicate configuration to maintain.
- **Regenerate, do not hand-write.** The MCP server is generated from the single
  source of truth, so it never drifts from the documented commands.
- **Safe by construction.** Generated tools run only the fixed documented
  command, with no caller-supplied arguments, through a shell-free argument list
  (`shlex.split`), under a timeout, capturing output rather than streaming it.

## Install

```bash
pip install agentsmd-mcp-bridge          # core (dependency-free)
pip install "agentsmd-mcp-bridge[mcp]"   # plus the MCP SDK to run generated servers
```

## Usage

### Generate an MCP server from AGENTS.md

```bash
agentsmd-mcp-bridge generate-mcp AGENTS.md -o mcp_server.py -s my-project
python mcp_server.py            # run the server (requires the mcp extra)
```

Each command-like section of `AGENTS.md` (Build, Test, Lint, Run, ...) becomes
one MCP tool named after its heading.

### Inspect what would be exposed

```bash
agentsmd-mcp-bridge list-commands AGENTS.md
# build    npm run build
# test     pytest -q
# lint     ruff check .
```

Use `--strict` to only consider headings that look command-like.

### Generate an AGENTS.md section from an MCP manifest

```bash
agentsmd-mcp-bridge generate-agentsmd manifest.json -o section.md
```

where `manifest.json` is the object returned by an MCP `tools/list` call.

## How extraction works

The parser is dependency-free and forgiving. Under each heading it collects both
prose and fenced code blocks, then keeps only lines that begin with a recognised
command launcher (`npm`, `pip`, `python`, `pytest`, `ruff`, `make`, `cargo`,
`go`, `docker`, and others). Prose back-ticks that are not commands are ignored.
This curated allow-list is a deliberate safety choice: the bridge will not turn
an arbitrary sentence into an executable tool.

## Library API

```python
from agentsmd_mcp_bridge import parse_agents_md, extract_commands, generate_mcp_server

doc = parse_agents_md(open("AGENTS.md").read())
commands = extract_commands(doc)
source = generate_mcp_server(commands, server_name="my-project")
```

## Tests

```bash
pip install -e ".[dev]"
pytest --cov=agentsmd_mcp_bridge
```

31 tests, 98% line coverage, ruff-clean, CI across Python 3.10 to 3.13. The CI
also dogfoods: it generates an MCP server from this repository's own `AGENTS.md`
and asserts the result is valid Python.

## Examples

See - a sample `AGENTS.md`, the MCP server generated from
it, a sample MCP manifest, and the `AGENTS.md` section generated from that.

## License

MIT. See [LICENSE](LICENSE).
