# PaperBench High-Difficulty and Expanded Tasks delivery probe -- sourced by every task's tests/test.sh.
#
# Why this exists
# ---------------
# The verifier can only ever see /home/submission; it never sees the agent
# transcript. So these two situations arrive at the scorer looking identical,
# and both are recorded as an honest zero:
#
#   1. the model worked for hours and got the physics wrong;
#   2. the agent never ran -- `claude -p` aborted on an API 502 at turn 1,
#      exited 0, and left /home/submission untouched.
#
# Case 2 is not a model result and must not be averaged in as one. This probe
# records which case it was, in a machine-readable form aggregation can filter:
#
#   /logs/verifier/delivery_status.json   always written
#   /logs/verifier/infra_failure.json     only when nothing was delivered
#
# Neither file changes the reward. Scoring stays exactly as it was; the point is
# that a zero now carries the reason it is a zero.
#
# All functions are deliberately failure-tolerant: a probe that aborts the
# verifier under `set -euo pipefail` would be worse than no probe at all.

PBX_VERIFIER_LOGS_DIR="${PBX_VERIFIER_LOGS_DIR:-/logs/verifier}"

# Hash every solver-authored regular file below $1, as "<relpath> <sha256>"
# lines on stdout. The excluded names are the generated replay roots, i.e. the
# set instruction.md documents as deleted before replay -- so an agent that only
# ran the untouched starter still compares equal to the starter.
pbx_source_manifest() {
    local root="$1"
    [ -d "$root" ] || return 0
    (
        cd "$root" 2>/dev/null || exit 0
        find -P . -mindepth 1 \
            \( -path './config' -o -path './results' -o -path './views' \
               -o -path './geometry' -o -name '__pycache__' \
               -o -name '*.pyc' -o -name 'replay_receipt.json' \) -prune -o \
            -type f -print0 2>/dev/null \
          | sort -z \
          | xargs -0 -r sha256sum 2>/dev/null \
          | awk '{ print $2, $1 }'
    ) || true
}

pbx_count_files() {
    local root="$1"
    [ -d "$root" ] || { echo 0; return 0; }
    local n
    n="$(find -P "$root" -mindepth 1 -name '__pycache__' -prune -o \
            -type f -print 2>/dev/null | wc -l)" || n=0
    echo "${n:-0}"
}

# pbx_write_infra_failure <kind> <detail>
# Marks this trial as "the agent delivered nothing", which is an infrastructure
# outcome rather than a model score.
#
# First writer wins. Detection runs earliest-to-latest, so the first kind to fire
# is the closest to the root cause: an empty /home/submission explains a missing
# reproduce.sh, not the other way round. Later calls still log to stderr.
pbx_write_infra_failure() {
    local kind="$1"
    local detail="$2"
    mkdir -p "$PBX_VERIFIER_LOGS_DIR" 2>/dev/null || true
    if [ -f "$PBX_VERIFIER_LOGS_DIR/infra_failure.json" ]; then
        echo "PBX-INFRA-FAILURE: $kind: $detail (marker already set; keeping the earlier root cause)" >&2
        return 0
    fi
    cat > "$PBX_VERIFIER_LOGS_DIR/infra_failure.json" <<EOF || true
{
  "schema_version": 1,
  "kind": "$kind",
  "detail": "$detail",
  "valid_model_attempt": false,
  "note": "The reward for this trial is a floor, not a measurement. Exclude it from score aggregation."
}
EOF
    echo "PBX-INFRA-FAILURE: $kind: $detail" >&2
}

# pbx_write_delivery_status [submission_root] [starter_root]
# Classifies what the agent actually left behind, before any replay runs.
#   delivery = "absent"       nothing at all, or no regular files
#            | "starter_only" byte-identical to the provided starter scaffolding
#            | "delivered"    the agent wrote something of its own
pbx_write_delivery_status() {
    local submission="${1:-/home/submission}"
    local starter="${2:-/home/starter_submission}"

    mkdir -p "$PBX_VERIFIER_LOGS_DIR" 2>/dev/null || true

    # `|| true` throughout: test.sh runs under `set -euo pipefail`, and a probe
    # that aborts the verifier would destroy the very evidence it collects.
    local submission_exists=false
    [ -d "$submission" ] && submission_exists=true || true

    local reproduce_present=false
    if [ -f "$submission/reproduce.sh" ] && [ ! -L "$submission/reproduce.sh" ]; then
        reproduce_present=true
    fi

    local file_count
    file_count="$(pbx_count_files "$submission")"

    # differs_from_starter stays null when the container ships no starter to
    # compare against, rather than guessing.
    local starter_json="null"
    local differs="null"
    if [ -d "$starter" ]; then
        starter_json="\"$starter\""
        if [ "$(pbx_source_manifest "$submission")" = "$(pbx_source_manifest "$starter")" ]; then
            differs=false
        else
            differs=true
        fi
    fi

    local delivery="delivered"
    if [ "$submission_exists" != true ] || [ "$file_count" -eq 0 ]; then
        delivery="absent"
    elif [ "$differs" = false ]; then
        delivery="starter_only"
    fi

    cat > "$PBX_VERIFIER_LOGS_DIR/delivery_status.json" <<EOF || true
{
  "schema_version": 1,
  "submission_root": "$submission",
  "submission_exists": $submission_exists,
  "submission_file_count": $file_count,
  "reproduce_sh_present": $reproduce_present,
  "starter_reference": $starter_json,
  "differs_from_starter": $differs,
  "delivery": "$delivery"
}
EOF

    echo "PBX-DELIVERY: delivery=$delivery files=$file_count reproduce_sh=$reproduce_present differs_from_starter=$differs"

    if [ "$delivery" = "absent" ]; then
        pbx_write_infra_failure no_submission \
            "$submission holds no files at verifier start; the agent phase produced nothing to grade"
    fi
}

# pbx_record_replay_exit <exit_code>
# The clean-replay exit code, in a file the aggregator can read without having
# to parse the verifier's stdout.
pbx_record_replay_exit() {
    mkdir -p "$PBX_VERIFIER_LOGS_DIR" 2>/dev/null || true
    echo "${1:-}" > "$PBX_VERIFIER_LOGS_DIR/replay_exit_code.txt" 2>/dev/null || true
}
