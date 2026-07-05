"""Local scaffold for future Bedrock/MCP integration.

This module intentionally avoids any runtime dependency on an MCP server or
Bedrock credentials. It exists to document the future seam for enterprise
agent deployment while keeping local deterministic tests self-contained.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer



def get_mcp_server_scaffold() -> dict:
    return {
        "status": "scaffolded",
        "runtime": "local deterministic harness",
        "future_targets": ["AWS Bedrock", "MCP tool server"],
        "credential_requirement": "not required for local tests",
    }


class _MCPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path not in {"/", "/health"}:
            self.send_error(404, "Not Found")
            return

        payload = {
            **get_mcp_server_scaffold(),
            "mode": os.getenv("AREOS_MODE", "local_mock"),
            "api_base_url": os.getenv("API_BASE_URL", "http://api:8000"),
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def main() -> None:
    port = int(os.getenv("PORT", "8001"))
    server = ThreadingHTTPServer(("0.0.0.0", port), _MCPRequestHandler)
    print(f"[mcp-server] listening on 0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
