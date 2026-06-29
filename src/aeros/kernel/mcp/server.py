"""Local scaffold for future Bedrock/MCP integration.

This module intentionally avoids any runtime dependency on an MCP server or
Bedrock credentials. It exists to document the future seam for enterprise
agent deployment while keeping local deterministic tests self-contained.
"""


def get_mcp_server_scaffold() -> dict:
    return {
        "status": "scaffolded",
        "runtime": "local deterministic harness",
        "future_targets": ["AWS Bedrock", "MCP tool server"],
        "credential_requirement": "not required for local tests",
    }
