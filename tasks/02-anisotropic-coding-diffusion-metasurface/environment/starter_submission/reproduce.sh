#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p hfss results views
for variant in unit_normal unit_tm15 unit_tm30 unit_tm45 array_ms array_pec af_patterns; do
  python3 src/run_all.py --variant "$variant"
done
python3 src/derive.py --results results --check
