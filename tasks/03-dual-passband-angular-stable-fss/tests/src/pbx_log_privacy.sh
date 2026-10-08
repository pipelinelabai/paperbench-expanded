pbx_seal_verifier_logs() {
    local log_root="${PBX_VERIFIER_LOGS_DIR:-/logs/verifier}"
    [ ! -L "$log_root" ] || return 1
    [ -d "$log_root" ] || return 0
    chown -hR root:pbverifier "$log_root" || return 1
    find -P "$log_root" -type d -exec chmod 0750 {} + || return 1
    find -P "$log_root" -type f -exec chmod 0640 {} + || return 1
    chmod 0751 "$log_root" || return 1
    if [ -f "$log_root/reward.txt" ] && [ ! -L "$log_root/reward.txt" ]; then
        chmod 0644 "$log_root/reward.txt" || return 1
    fi
}
