#!/bin/bash
set -euo pipefail
. /tests/src/pbx_log_privacy.sh
install -d -m 0755 -o root -g root /usr/local/libexec
umask 027

REPLAY_TIMEOUT_SEC="${PBX_REPLAY_TIMEOUT_SEC:-18000}"
if ! [[ "$REPLAY_TIMEOUT_SEC" =~ ^[1-9][0-9]{0,5}$ ]] || (( REPLAY_TIMEOUT_SEC > 18000 )); then
    echo "ERROR: replay timeout must be an integer from 1 to 18000 seconds within the 6h verifier budget." >&2
    exit 2
fi

echo "============================================================"
echo " Meep v2 clean replay + tool-augmented LLM verifier"
echo "============================================================"

if [ -d /logs/verifier ]; then
    find /logs/verifier -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
fi
install -d -m 0750 -o root -g pbverifier /logs/verifier
chmod 0750 /logs/verifier

# Record what the agent actually delivered before any replay touches it, so a
# zero caused by a dead agent phase is distinguishable from a zero earned by a
# real attempt.  Writes /logs/verifier/delivery_status.json, plus
# infra_failure.json when /home/submission is empty.  Never changes the reward.
# shellcheck source=/dev/null
. /tests/src/pbx_delivery_probe.sh
pbx_write_delivery_status /home/submission /home/starter_submission

# The candidate replay account cannot inspect verifier code or private refs.
chown -R root:pbverifier /tests
find /tests -type d -exec chmod 0750 {} +
find /tests -type f -exec chmod 0640 {} +

NETWORK_BLOCKED=0
block_candidate_network() {
    if python3 - <<'PYISOLATION'
import socket
raise SystemExit(0 if {name for _, name in socket.if_nameindex()} <= {'lo'} else 1)
PYISOLATION
    then
        echo "Verified outer network namespace: loopback only; no external interface."
        return 0
    fi
    if ! command -v iptables >/dev/null 2>&1 || ! command -v ip6tables >/dev/null 2>&1; then
        echo "ERROR: no verified outer isolation and no IPv4/IPv6 owner firewall."
        return 1
    fi
    if ! iptables -w -I OUTPUT 1 -m owner --uid-owner pbsolver -j REJECT; then
        return 1
    fi
    if ! ip6tables -w -I OUTPUT 1 -m owner --uid-owner pbsolver -j REJECT; then
        iptables -w -D OUTPUT -m owner --uid-owner pbsolver -j REJECT 2>/dev/null || true
        return 1
    fi
    NETWORK_BLOCKED=1
}
unblock_candidate_network() {
    [ "$NETWORK_BLOCKED" -eq 1 ] || return 0
    iptables -w -D OUTPUT -m owner --uid-owner pbsolver -j REJECT 2>/dev/null || true
    ip6tables -w -D OUTPUT -m owner --uid-owner pbsolver -j REJECT 2>/dev/null || true
    NETWORK_BLOCKED=0
}
cleanup() {
    unblock_candidate_network || true
    pbx_seal_verifier_logs
}
trap cleanup EXIT

snapshot_submission() {
    local outfile="$1"
    local root="${2:-/home/submission}"
    if [ -n "${PBX_REPLAY_SOURCE_INVENTORY:-}" ]; then
        if python3 /tests/src/meep_replay_inventory.py fingerprint --source "$root" \
          --inventory "$PBX_REPLAY_SOURCE_INVENTORY" > "$outfile"; then
            return 0
        fi
        REPLAY_SETUP_ERROR="source_inventory_fingerprint_failed"
        echo "snapshot unavailable" > "$outfile"
        return 0
    fi
    local inventory="/logs/verifier/frozen_source_inputs.json"
    if [ ! -f "$inventory" ]; then
        if ! python3 /tests/src/replay_source_inputs.py freeze --source "$root" --inventory "$inventory" >/dev/null; then
            REPLAY_SETUP_ERROR="source_input_freeze_failed"
            REPRO_EXIT=126
            echo "snapshot unavailable" > "$outfile"
            return 0
        fi
    fi
    if ! python3 /tests/src/replay_source_inputs.py fingerprint --source "$root" --inventory "$inventory" > "$outfile"; then
        REPLAY_SETUP_ERROR="source_input_fingerprint_failed"
        REPRO_EXIT=126
        echo "snapshot unavailable" > "$outfile"
    fi
}

prepare_source_only_replay_workspace() {
    local original="/home/submission"
    local source_snapshot="/logs/verifier/source_submission"

    rm -rf "$source_snapshot"
    install -d -m 0755 -o root -g root "$source_snapshot"

    if [ -n "${PBX_REPLAY_SOURCE_INVENTORY:-}" ]; then
        python3 /tests/src/meep_replay_inventory.py snapshot --source "$original" \
          --destination "$source_snapshot" --inventory "$PBX_REPLAY_SOURCE_INVENTORY" \
          > /logs/verifier/replay_source_inventory_receipt.json || return 126
    else
        # Copy every solver-authored input except the generated replay roots.  An
        # exclusion list is used rather than a name whitelist so that task-specific
        # source files at the submission root (e.g. model_config.json) survive; a
        # whitelist dropped them silently and replay then failed with FileNotFound,
        # which scored as a candidate failure.  The exclusion list mirrors the prune
        # list in snapshot_submission so the two functions agree on what counts as
        # source, and matches the set instruction.md documents as deleted.
        local name
        while IFS= read -r -d "" entry; do
            name="${entry#./}"
            case "$name" in
                config|results|views|geometry|report.md|replay_receipt.json|__pycache__)
                    continue ;;
            esac
            if [ -L "$original/$name" ]; then
                echo "NOTE: dropping top-level symlink from replay workspace: $name" \
                  | tee -a /logs/verifier/candidate_replay.log
                continue
            fi
            cp -a "$original/$name" "$source_snapshot/$name"
        done < <(cd "$original" && find -P . -mindepth 1 -maxdepth 1 -print0)
    
        # Strip generated outputs from the snapshot too, so the copy on /logs stays
        # source-only and does not carry multi-GB stale result arrays.
        chmod -R u+rwX "$source_snapshot" 2>/dev/null || true
        rm -rf "$source_snapshot/config" \
               "$source_snapshot/results" \
               "$source_snapshot/views" \
               "$source_snapshot/geometry" \
               "$source_snapshot/replay_receipt.json" "$source_snapshot/report.md"
        find -P "$source_snapshot" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
        find -P "$source_snapshot" -type f -name "*.pyc" -delete 2>/dev/null || true
    
    fi

    if find -P "$source_snapshot" -type l -print -quit | grep -q .; then
        echo "ERROR: source-only replay snapshot contains a symlink" | tee -a /logs/verifier/candidate_replay.log
        return 126
    fi
    if find -P "$source_snapshot" -mindepth 1 ! -type f ! -type d -print -quit | grep -q .; then
        echo "ERROR: source-only replay snapshot contains a nonregular filesystem object" | tee -a /logs/verifier/candidate_replay.log
        return 126
    fi

    # Replace the *contents* of /home/submission with a clean source-only
    # workspace, keeping the canonical path visible to candidates that hard-code
    # /home/submission.
    #
    # /home/submission is a bind mount in the sandbox, so it can never be
    # unlinked: "rm -rf $original" always fails with EBUSY there.  That failure
    # used to be unchecked, and because this function is invoked as
    # "if ! prepare_source_only_replay_workspace", bash suppresses errexit for
    # everything inside it -- so a half-prepared workspace still reported
    # success and the replay ran on it anyway.  Clear the directory contents
    # instead, and check each step explicitly since errexit cannot help here.
    chmod -R u+rwX "$original" 2>/dev/null || true
    find "$original" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
    if find "$original" -mindepth 1 -print -quit | grep -q .; then
        echo "ERROR: could not clear $original before clean replay; leftovers:" \
          | tee -a /logs/verifier/candidate_replay.log
        find "$original" -mindepth 1 -maxdepth 2 -printf "%M %u:%g %p\\n" \
          2>/dev/null | tee -a /logs/verifier/candidate_replay.log
        return 126
    fi
    if ! install -d -m 0755 -o pbsolver -g pbsolver "$original"; then
        echo "ERROR: could not reset ownership/mode on $original" \
          | tee -a /logs/verifier/candidate_replay.log
        return 126
    fi
    if ! cp -a "$source_snapshot"/. "$original"/; then
        echo "ERROR: could not populate the clean replay workspace" \
          | tee -a /logs/verifier/candidate_replay.log
        return 126
    fi
    chown -hR pbsolver:pbsolver "$original" || return 126

    # Defense in depth: the replay workspace must contain source inputs only.
    # Even if a candidate packaged generated outputs under source directories
    # or ownership/permissions were preserved by the copy, remove all generated
    # replay roots and recreate them as fresh pbsolver-owned directories.
    if [ -z "${PBX_REPLAY_SOURCE_INVENTORY:-}" ]; then
        chmod -R u+rwX "$original" 2>/dev/null || true
        rm -rf "$original/config" \
               "$original/results" \
               "$original/views" \
               "$original/geometry" \
               "$original/replay_receipt.json" "$original/report.md"
        install -d -m 0755 -o pbsolver -g pbsolver \
            "$original/config" \
            "$original/results" \
            "$original/views" \
            "$original/geometry"
    fi

    chown -hR pbsolver:pbsolver "$original" || return 126
    find -P /home/submission -type d -exec chmod u+rwx,go+rx {} + || return 126
    find -P /home/submission -type f -exec chmod u+rw,go+r {} + || return 126
    if [ -f /home/submission/reproduce.sh ]; then chmod 0700 /home/submission/reproduce.sh; fi
    runuser -u pbsolver -- env -i PATH=/usr/bin:/bin /bin/sh -se <<'PYWRITE'
cd /home/submission
probe=$(mktemp .pbx-write-check.XXXXXX)
trap 'rm -f "$probe"' EXIT HUP INT TERM
printf '%s\n' ready > "$probe"
test "$(cat "$probe")" = ready
PYWRITE
}

write_replay_wrapper() {
    cat > /usr/local/libexec/pbx_run_candidate_replay.sh <<'EOF'
#!/bin/bash
set -euo pipefail
cd /home/submission
umask 022
export MPLBACKEND=Agg
export PYTHONUNBUFFERED=1
EOF
    if [ -n "${PBX_REPLAY_SOURCE_INVENTORY:-}" ]; then
        python3 /tests/src/meep_replay_inventory.py shell-command --source /home/submission \
          --inventory "$PBX_REPLAY_SOURCE_INVENTORY" >> /usr/local/libexec/pbx_run_candidate_replay.sh || return 126
    else
        cat >> /usr/local/libexec/pbx_run_candidate_replay.sh <<'EOF'
rm -rf config results views geometry report.md replay_receipt.json
install -d -m 0755 config results views geometry
exec bash /home/submission/reproduce.sh
EOF
    fi
    chown root:root /usr/local/libexec/pbx_run_candidate_replay.sh
    chmod 0755 /usr/local/libexec/pbx_run_candidate_replay.sh
}

REPRO_EXIT=0
REPLAY_SETUP_ERROR=""
REPLAY_NONCE="$(od -An -N24 -tx1 /dev/urandom | tr -d ' \n')"
REPLAY_STARTED="$(date --iso-8601=seconds)"
echo "runner: candidate clean replay started" > /logs/verifier/candidate_replay.log
: > /logs/verifier/candidate_exec.trace
SECONDS=0
snapshot_submission /logs/verifier/candidate_inputs_before.sha256

if [ -z "${PBX_REPLAY_SOURCE_INVENTORY:-}" ] && { [ ! -f /home/submission/reproduce.sh ] || [ -L /home/submission/reproduce.sh ]; }; then
    echo "ERROR: reproduce.sh is missing" | tee -a /logs/verifier/candidate_replay.log
    echo "Top-level submission files:" >> /logs/verifier/candidate_replay.log
    find -P /home/submission -maxdepth 2 -mindepth 1 -printf '%M %u:%g %p\n' \
      >> /logs/verifier/candidate_replay.log 2>/dev/null || true
    pbx_write_infra_failure missing_reproduce_sh \
      "reproduce.sh is absent from /home/submission, so there is no candidate pipeline to replay"
    REPRO_EXIT=127
    REPLAY_SETUP_ERROR="entrypoint_requires_evaluator_source_review"
else
    pkill -KILL -u pbsolver 2>/dev/null || true
    if ! prepare_source_only_replay_workspace; then
        REPRO_EXIT=126
        REPLAY_SETUP_ERROR="source_only_workspace_preparation_failed"
    fi
    if ! write_replay_wrapper; then
        REPRO_EXIT=126
        REPLAY_SETUP_ERROR="replay_wrapper_preparation_failed"
    fi
    if [ "${REPRO_EXIT}" -ne 0 ]; then
        :
    elif ! block_candidate_network; then
        echo "ERROR: could not establish candidate network isolation"
        REPRO_EXIT=126
        REPLAY_SETUP_ERROR="candidate_network_isolation_failed"
    else
        echo "Clean replay as pbsolver (candidate Python and Meep/MPB, up to ${REPLAY_TIMEOUT_SEC}s inside the 6h verifier budget)..."
        set +e
        if command -v strace >/dev/null 2>&1; then
          setsid timeout --signal=TERM --kill-after=60s "${REPLAY_TIMEOUT_SEC}s" \
            strace -f -qq -s 4096 -e trace=execve -o /logs/verifier/candidate_exec.trace \
            runuser -u pbsolver -- \
            env -i HOME=/home/pbsolver USER=pbsolver LOGNAME=pbsolver \
            PYTHONNOUSERSITE=1 PATH=/usr/local/bin:/usr/bin:/bin \
            PBX_REPLAY_NONCE="$REPLAY_NONCE" CONTAINER_CPUS="${CONTAINER_CPUS:-8}" \
            bash /usr/local/libexec/pbx_run_candidate_replay.sh \
            >> /logs/verifier/candidate_replay.log 2>&1
          REPRO_EXIT=$?
        else
          echo "WARNING: strace not available; running clean replay without exec trace." | tee -a /logs/verifier/candidate_replay.log
          echo "strace unavailable in verifier environment" > /logs/verifier/candidate_exec.trace
          setsid timeout --signal=TERM --kill-after=60s "${REPLAY_TIMEOUT_SEC}s" \
            runuser -u pbsolver -- \
            env -i HOME=/home/pbsolver USER=pbsolver LOGNAME=pbsolver \
            PYTHONNOUSERSITE=1 PATH=/usr/local/bin:/usr/bin:/bin \
            PBX_REPLAY_NONCE="$REPLAY_NONCE" CONTAINER_CPUS="${CONTAINER_CPUS:-8}" \
            bash /usr/local/libexec/pbx_run_candidate_replay.sh \
            >> /logs/verifier/candidate_replay.log 2>&1
          REPRO_EXIT=$?
        fi
        set -e
    fi
fi
pkill -KILL -u pbsolver 2>/dev/null || true
unblock_candidate_network

if [ "${REPRO_EXIT}" -eq 0 ]; then
    snapshot_submission /logs/verifier/candidate_inputs_after.sha256
    if ! cmp -s /logs/verifier/candidate_inputs_before.sha256 /logs/verifier/candidate_inputs_after.sha256; then
        echo "ERROR: replay modified the source/input snapshot or wrote an unclassified output path"
        REPRO_EXIT=125
        if [ -z "${PBX_REPLAY_SOURCE_INVENTORY:-}" ]; then
            REPLAY_SETUP_ERROR="source_output_classification_requires_evaluator_review"
        fi
    fi
else
    snapshot_submission /logs/verifier/candidate_inputs_after.sha256
fi
if find /home/submission -type l -print -quit | grep -q .; then
    echo "ERROR: submission contains a symlink"
    REPRO_EXIT=126
fi
if find /home/submission -mindepth 1 ! -type f ! -type d -print -quit | grep -q .; then
    echo "ERROR: submission contains a nonregular filesystem object"
    REPRO_EXIT=126
fi

python3 /tests/src/write_replay_record.py \
  --submission /home/submission \
  --log /logs/verifier/candidate_replay.log \
  --exec-trace /logs/verifier/candidate_exec.trace \
  --inputs-before /logs/verifier/candidate_inputs_before.sha256 \
  --inputs-after /logs/verifier/candidate_inputs_after.sha256 \
  --output /logs/verifier/candidate_replay.json \
  --nonce "$REPLAY_NONCE" \
  --exit-code "$REPRO_EXIT" \
  --started-at "$REPLAY_STARTED" \
  --elapsed-seconds "$SECONDS"
echo "Candidate replay exit: ${REPRO_EXIT}"
pbx_record_replay_exit "${REPRO_EXIT}"

# Freeze the executed submission, then copy clean-replay products into a
# verifier-owned physical evidence root. Rubric paths remain logical
# submission/... paths; the scorer maps them to this directory.
chown -hR root:root /home/submission
find -P /home/submission -type d -exec chmod 0555 {} +
find -P /home/submission -type f -exec chmod 0444 {} +
rm -rf /logs/verifier/candidate_outputs
install -d -m 0750 -o root -g pbverifier /logs/verifier/candidate_outputs
# Preserve every solver-authored source/input at the top level, not just a
# fixed whitelist.  Root files such as model_config.json must remain visible to
# the judge when a rubric leaf cites them.  Generated replay roots are copied in
# the second pass below so stale pre-replay outputs cannot leak into evidence.
while IFS= read -r -d "" entry; do
    name="${entry#./}"
    case "$name" in
        config|results|views|geometry|replay_receipt.json|__pycache__)
            continue ;;
    esac
    cp -a "/home/submission/$name" "/logs/verifier/candidate_outputs/$name"
done < <(cd /home/submission && find -P . -mindepth 1 -maxdepth 1 -print0)

for path in config geometry results views replay_receipt.json; do
    if [ -e "/home/submission/$path" ]; then
        cp -a "/home/submission/$path" "/logs/verifier/candidate_outputs/$path"
    fi
done
cp -a /logs/verifier/candidate_replay.json /logs/verifier/candidate_outputs/candidate_replay.json
chown -hR root:root /logs/verifier/candidate_outputs
find -P /logs/verifier/candidate_outputs -type d -exec chmod 0555 {} +
find -P /logs/verifier/candidate_outputs -type f -exec chmod 0444 {} +

if [ -n "$REPLAY_SETUP_ERROR" ]; then
    PBX_REPLAY_SETUP_ERROR="$REPLAY_SETUP_ERROR" python3 - <<'PYERROR'
import os
import sys
sys.path.insert(0, '/tests/src')
from meep_score_publication import prepare_source_review, withhold_replay_setup_error
prepare_source_review('/logs/verifier')
withhold_replay_setup_error('/logs/verifier', os.environ['PBX_REPLAY_SETUP_ERROR'])
PYERROR
fi

echo "Running tool-augmented LLM rubric evaluator..."
set +e
PBX_CANDIDATE_EVIDENCE_ROOT=/logs/verifier/candidate_outputs \
PBX_EVIDENCE_ROOT=/logs/verifier/candidate_outputs \
JUDGE_MODEL="${JUDGE_MODEL:-gpt-5.5}" \
python3 /tests/evaluate.py
EVAL_EXIT=$?
set -e
if [ -n "$REPLAY_SETUP_ERROR" ]; then
    PBX_REPLAY_SETUP_ERROR="$REPLAY_SETUP_ERROR" python3 - <<'PYREVIEW'
import os
import sys
sys.path.insert(0, '/tests/src')
from meep_score_publication import withhold_replay_setup_error
withhold_replay_setup_error('/logs/verifier', os.environ['PBX_REPLAY_SETUP_ERROR'])
PYREVIEW
    exit 75
fi
if [ "$EVAL_EXIT" -ne 0 ]; then exit "$EVAL_EXIT"; fi
pbx_seal_verifier_logs
echo "Final reward: $(cat /logs/verifier/reward.txt)"
