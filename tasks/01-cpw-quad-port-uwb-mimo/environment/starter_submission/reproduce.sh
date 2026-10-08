#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p hfss results views
for variant in mimo_final single_initial single_stub h2_10p7 h2_11p7 mimo_nostub; do
  python3 src/run_all.py --variant "$variant"
done
python3 src/derive.py --results results --check
