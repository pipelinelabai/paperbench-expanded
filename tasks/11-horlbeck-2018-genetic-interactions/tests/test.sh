#!/bin/bash
set -euo pipefail
test_dir="${TEST_DIR:-/tests}"
exec env -i PATH=/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin HOME=/root LANG=C.UTF-8 \
    JUDGE_API_KEY="${JUDGE_API_KEY:-}" JUDGE_BASE_URL="${JUDGE_BASE_URL:-}" \
    JUDGE_MODEL="${JUDGE_MODEL:-}" JUDGE_TIMEOUT_SEC="${JUDGE_TIMEOUT_SEC:-300}" \
    PBX_LLM_TRANSPORT="${PBX_LLM_TRANSPORT:-openai}" \
    python3 -B "$test_dir/src/replay.py"
