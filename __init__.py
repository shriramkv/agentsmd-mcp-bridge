"""agentsmd-mcp-bridge: turn an AGENTS.md into an MCP server, and back.

The bridge reads the commands a repository documents for coding agents in its
AGENTS.md file and generates a Model Context Protocol (MCP) server that exposes
those commands as callable tools. It also runs in reverse: given an MCP tool
manifest, it emits an AGENTS.md section documenting the available tools.
"""

__version__ = "0.1.0"

from .agentsmd_gen import generate_agentsmd_section, load_manifest
from .extractor import extract_commands
from .mcp_gen import generate_mcp_server
from .models import AgentsDoc, Command, ToolManifest, ToolSpec
from .parser import parse_agents_md

__all__ = [
    "Command",
    "AgentsDoc",
    "ToolSpec",
    "ToolManifest",
    "parse_agents_md",
    "extract_commands",
    "generate_mcp_server",
    "generate_agentsmd_section",
    "load_manifest",
    "__version__",
]
