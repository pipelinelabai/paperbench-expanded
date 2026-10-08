#!/bin/bash
set -euo pipefail

TASK_NAME="mapgpt-r2r"
GENERATED_ROOTS="results"
DEFAULT_TRIES=1
DEFAULT_STALL_SECONDS=0
PRESERVE_RETRY_OUTPUTS=0
RUNTIME_WRITABLE_PATHS=""
REPLAY=/tests/evaluable_replay.py

mkdir -p /logs/verifier
rm -f /logs/verifier/reward.txt /logs/verifier/infra_failure.json \
      /logs/verifier/candidate_failure.json
cleanup() {
    python3 "$REPLAY" cleanup >/dev/null 2>&1 || true
    chmod -R a+rX /logs/verifier 2>/dev/null || true
}
trap cleanup EXIT

echo "=== ${TASK_NAME}: clean low-privilege replay ==="
PREPARE_ARGS=()
IFS=',' read -ra ROOTS <<< "$GENERATED_ROOTS"
for root in "${ROOTS[@]}"; do
    PREPARE_ARGS+=(--generated-root "$root")
done
if [ -n "$RUNTIME_WRITABLE_PATHS" ]; then
    IFS=',' read -ra WRITABLE_PATHS <<< "$RUNTIME_WRITABLE_PATHS"
    for runtime_path in "${WRITABLE_PATHS[@]}"; do
        [ -n "$runtime_path" ] && PREPARE_ARGS+=(--runtime-writable-path "$runtime_path")
    done
fi
set +e
python3 "$REPLAY" prepare "${PREPARE_ARGS[@]}"
PREPARE_EXIT=$?
set -e
if [ "$PREPARE_EXIT" -ne 0 ]; then
    if [ -f /logs/verifier/candidate_failure.json ]; then
        printf '0.000000\n' > /logs/verifier/reward.txt
        exit 0
    fi
    exit 1
fi

MAX_REPRO_TRIES="${MAX_REPRO_TRIES:-$DEFAULT_TRIES}"
STALL_SEC="${STALL_SEC:-$DEFAULT_STALL_SECONDS}"
REPRO_EXIT=1
for try in $(seq 1 "$MAX_REPRO_TRIES"); do
    if [ "$try" -gt 1 ] && [ "$PRESERVE_RETRY_OUTPUTS" -eq 0 ]; then
        python3 "$REPLAY" clean || exit 1
    fi
    nvidia-smi --query-gpu=index,utilization.gpu,memory.used \
        --format=csv,noheader,nounits 2>/dev/null | sed 's/^/[replay] gpu /' || true
    set +e
    python3 "$REPLAY" run --attempt "$try" --stall-seconds "$STALL_SEC"
    REPRO_EXIT=$?
    set -e
    echo "[replay] attempt ${try}/${MAX_REPRO_TRIES} exit=${REPRO_EXIT}"
    if [ -f /logs/verifier/infra_failure.json ]; then
        python3 "$REPLAY" freeze --exit-code "$REPRO_EXIT" || true
        rm -f /logs/verifier/reward.txt
        exit 1
    fi
    [ "$REPRO_EXIT" -eq 0 ] && break
    if [ "$REPRO_EXIT" -ge 128 ] || [ "$REPRO_EXIT" -eq 1 ] || [ "$REPRO_EXIT" -eq 124 ]; then
        continue
    fi
    break
done

if ! python3 "$REPLAY" freeze --exit-code "$REPRO_EXIT"; then
    printf '0.000000\n' > /logs/verifier/reward.txt
    exit 0
fi

if [ "$REPRO_EXIT" -ne 0 ]; then
    python3 "$REPLAY" failure --kind candidate --stage candidate_replay \
        --exit-code "$REPRO_EXIT" --message "reproduce.sh returned a deterministic failure"
    printf '0.000000\n' > /logs/verifier/reward.txt
    exit 0
fi

echo "Scoring frozen evidence at /logs/verifier/candidate_outputs"
set +e
/tests/run_evaluator.sh
EVAL_EXIT=$?
set -e
if [ "$EVAL_EXIT" -ne 0 ]; then
    if [ ! -f /logs/verifier/infra_failure.json ]; then
        python3 "$REPLAY" failure --kind infra --stage evaluator --exit-code "$EVAL_EXIT" \
            --message "evaluator failed; no normal reward is published"
    fi
    rm -f /logs/verifier/reward.txt
    exit 1
fi
cat /logs/verifier/reward.txt
