#!/bin/sh
set -eu
owner="${1:-pbsolver}"
submission="${2:-/home/submission}"
starter="${3:-/home/starter_submission}"
if [ "$(id -u)" -ne 0 ]; then
    echo "Workspace initialization requires the container administrator." >&2
    exit 70
fi
if [ -L "$submission" ] || [ -L "$starter" ]; then
    echo "Workspace and starter roots must not be symbolic links." >&2
    exit 70
fi
group="$(id -gn "$owner")"
install -d -m 0755 -o "$owner" -g "$group" "$submission"
if [ -d "$starter" ] && [ -z "$(find "$submission" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
    cp -a "$starter"/. "$submission"/
fi
chown -hR "$owner:$group" "$submission"
find -P "$submission" -type d -exec chmod u+rwx {} +
find -P "$submission" -type f -exec chmod u+rw {} +
runuser -u "$owner" -- env -i PATH=/usr/bin:/bin /bin/sh -se -- "$submission" <<'PROBE'
cd "$1"
probe=$(mktemp .pbx-write-check.XXXXXX)
trap 'rm -f "$probe"' EXIT HUP INT TERM
printf '%s\n' ready > "$probe"
test "$(cat "$probe")" = ready
if [ -f reproduce.sh ]; then test -r reproduce.sh; fi
PROBE
printf 'Workspace ready for %s: %s\n' "$owner" "$submission"
