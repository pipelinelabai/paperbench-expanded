#!/bin/bash
NAV_LLM_MODEL_PATH="${NAV_LLM_MODEL_PATH:-/home/models/Qwen2.5-VL-7B-Instruct}"
NAV_LLM_MODEL="${NAV_LLM_MODEL:-Qwen2.5-VL-7B-Instruct}"
NAV_VLLM_PORT="${NAV_VLLM_PORT:-8000}"
NAV_VLLM_HOST="${NAV_VLLM_HOST:-localhost}"
NAV_VLLM_GPU_UTIL="${NAV_VLLM_GPU_UTIL:-0.85}"
NAV_VLLM_MAX_LEN="${NAV_VLLM_MAX_LEN:-32768}"
NAV_VLLM_LOG="${NAV_VLLM_LOG:-/tmp/nav_vllm.log}"
NAV_VLLM_EXTRA="${NAV_VLLM_EXTRA:-}"
NAV_VLLM_MAX_IMAGES="${NAV_VLLM_MAX_IMAGES:-8}"
NAV_VLLM_MAX_PIXELS="${NAV_VLLM_MAX_PIXELS-262144}"
_NAV_VLLM_PID=""

nav_vllm_start() {
    if ! python3 -c 'import ipaddress, sys; host = sys.argv[1]; sys.exit(0 if host == "localhost" or ipaddress.ip_address(host).is_loopback else 1)' "$NAV_VLLM_HOST"; then
        printf 'Navigation service must bind to loopback.\n' >&2
        return 3
    fi
    if [ ! -r "$NAV_LLM_MODEL_PATH/config.json" ]; then
        printf 'Navigation model config missing or unreadable: %s\n' "$NAV_LLM_MODEL_PATH" >&2
        return 3
    fi
    local endpoint_host="$NAV_VLLM_HOST"
    if [[ "$endpoint_host" == *:* ]]; then
        endpoint_host="[$endpoint_host]"
    fi
    local endpoint="http://${endpoint_host}:${NAV_VLLM_PORT}"
    if curl --max-time 2 -fsS "$endpoint/health" >/dev/null 2>&1; then
        printf 'Navigation port already in use: %s\n' "$endpoint" >&2
        return 3
    fi
    local -a processor_args=() extra_args=()
    if [ -n "$NAV_VLLM_MAX_PIXELS" ]; then
        processor_args=(--mm-processor-kwargs "{\"max_pixels\":$NAV_VLLM_MAX_PIXELS}")
    fi
    read -r -a extra_args <<< "$NAV_VLLM_EXTRA"
    setsid vllm serve "$NAV_LLM_MODEL_PATH" \
        --served-model-name "$NAV_LLM_MODEL" \
        --host "$NAV_VLLM_HOST" \
        --port "$NAV_VLLM_PORT" \
        --gpu-memory-utilization "$NAV_VLLM_GPU_UTIL" \
        --max-model-len "$NAV_VLLM_MAX_LEN" \
        --limit-mm-per-prompt "image=$NAV_VLLM_MAX_IMAGES" \
        "${processor_args[@]}" \
        --trust-remote-code \
        --disable-log-requests \
        "${extra_args[@]}" > "$NAV_VLLM_LOG" 2>&1 &
    _NAV_VLLM_PID=$!
    trap nav_vllm_stop EXIT
    local startup_second
    for startup_second in $(seq 1 600); do
        if ! kill -0 "$_NAV_VLLM_PID" 2>/dev/null; then
            tail -30 "$NAV_VLLM_LOG" >&2 || true
            nav_vllm_stop
            return 4
        fi
        if curl --max-time 2 -fsS "$endpoint/health" >/dev/null 2>&1; then
            export NAV_LLM_BASE_URL="$endpoint/v1"
            export NAV_LLM_API_KEY="${NAV_LLM_API_KEY:-local}"
            export NAV_LLM_MODEL
            printf 'Navigation service ready: %s\n' "$NAV_LLM_BASE_URL"
            return 0
        fi
        sleep 1
    done
    tail -30 "$NAV_VLLM_LOG" >&2 || true
    nav_vllm_stop
    return 5
}

nav_vllm_stop() {
    trap - EXIT
    if [ -n "$_NAV_VLLM_PID" ]; then
        kill -TERM -- "-$_NAV_VLLM_PID" 2>/dev/null || true
        local stop_second
        for stop_second in $(seq 1 30); do
            if ! kill -0 -- "-$_NAV_VLLM_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        kill -KILL -- "-$_NAV_VLLM_PID" 2>/dev/null || true
        wait "$_NAV_VLLM_PID" 2>/dev/null || true
        _NAV_VLLM_PID=""
    fi
    return 0
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    trap 'exit 130' INT
    trap 'exit 143' TERM
    nav_vllm_start || exit $?
    wait "$_NAV_VLLM_PID"
fi
