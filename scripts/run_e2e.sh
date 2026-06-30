#!/usr/bin/env bash
set -euo pipefail

pytest -q tests/test_e2e_kernel_flow.py tests/test_phase6_live_connectors_and_backbone.py tests/test_bedrock_runtime_client.py
