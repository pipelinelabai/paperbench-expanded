#!/bin/bash
set -euo pipefail
submission_root="$(cd "$(dirname "$0")" && pwd)"
cd "$submission_root"
exec python3 src/run.py
