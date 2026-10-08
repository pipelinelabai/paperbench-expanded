#!/bin/bash
set -euo pipefail

EVIDENCE_ROOT=/logs/verifier/candidate_outputs
if [ ! -d "$EVIDENCE_ROOT" ]; then
    echo "frozen evidence root is missing: $EVIDENCE_ROOT" >&2
    exit 70
fi
if [ ! -d /opt/pbx-verifier-site ]; then
    echo "offline evaluator environment is missing: /opt/pbx-verifier-site" >&2
    exit 70
fi

export EVIDENCE_ROOT
export PYTHONPATH="/opt/pbx-verifier-site${PYTHONPATH:+:$PYTHONPATH}"
export PIP_NO_INDEX=1
export UV_OFFLINE=1
exec python3 /tests/evaluate.py
