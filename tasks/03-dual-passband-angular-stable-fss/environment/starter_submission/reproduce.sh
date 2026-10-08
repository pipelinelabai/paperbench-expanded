#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p hfss results views
for variant in te_00 te_30 te_60 te_86 tm_00 tm_30 tm_60 tm_83; do
  python3 src/run_all.py --variant "$variant"
done
