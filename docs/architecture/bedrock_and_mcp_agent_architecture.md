# Bedrock and MCP Agent Architecture

Phase 7 ships a deterministic local agent harness first.

## Local mode

- Rule-based orchestrator in `src/aeros/kernel/agents/orchestrator.py`
- Persona agents for QA, engineering, plant head, and validation
- Tool registry backed by existing assurance, dossier, workflow, and connector services
- No Bedrock credentials required

## Future AWS-native target

- AWS Bedrock for governed LLM inference
- MCP tool server boundary for enterprise tool registration and auditability
- Human approval gates remain mandatory for quality decisions and deviation closure

## Current status

- Local deterministic harness: implemented
- MCP server runtime: scaffolded only (`src/aeros/kernel/mcp/server.py`)
- Bedrock runtime wiring: future
