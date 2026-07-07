# Contributing

Thanks for your interest in improving agentsmd-mcp-bridge.

## Development setup

```bash
pip install -e ".[dev,mcp]"
```

## Before opening a pull request

Run the linter and the full test suite:

```bash
ruff check agentsmd_mcp_bridge tests
pytest --cov=agentsmd_mcp_bridge
```

Please keep the core modules (`parser`, `extractor`, `models`) dependency-free,
add tests for any new behaviour, and follow the existing style: British spelling
in prose and no em-dashes.

## Adding a command launcher

Extraction uses a curated allow-list of command launchers in
`agentsmd_mcp_bridge/extractor.py`. If a common tool is missing, add it to
`_LAUNCHER` with a test that shows it being extracted.
