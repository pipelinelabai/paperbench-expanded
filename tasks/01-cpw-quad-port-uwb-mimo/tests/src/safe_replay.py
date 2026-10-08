#!/usr/bin/env python3
"""Run candidate replay code without verifier privileges or private context."""

from __future__ import annotations

import ctypes
import json
import os
import pwd
import re
import grp
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SUBMISSION = Path(os.environ.get("PBX_SUBMISSION_DIR", "/home/submission")).resolve()
TESTS = Path(os.environ.get("PBX_TESTS_DIR", "/tests")).resolve()
LOGS = Path(os.environ.get("PBX_VERIFIER_LOGS", "/logs/verifier")).resolve()
TIMEOUT_SEC = int(os.environ.get("PBX_SAFE_REPLAY_TIMEOUT_SEC", "172800"))
REPORT = LOGS / "safe_replay.json"

DENIED_ENV_MARKERS = (
    "API_KEY",
    "AUTH_TOKEN",
    "ACCESS_TOKEN",
    "SECRET",
    "PASSWORD",
    "JUDGE",
    "ANTHROPIC",
    "OPENAI",
)
ALLOWED_ENV_NAMES = {
    "CUDA_VISIBLE_DEVICES",
    "DISPLAY",
    "LANG",
    "LC_ALL",
    "LD_LIBRARY_PATH",
    "LM_LICENSE_FILE",
    "NVIDIA_DRIVER_CAPABILITIES",
    "NVIDIA_VISIBLE_DEVICES",
    "OMP_NUM_THREADS",
    "PATH",
    "PYTHONNOUSERSITE",
    "TZ",
}
ALLOWED_ENV_SUFFIXES = ("_LICENSE_FILE", "_LICENSE_SERVER")
ALLOWED_ENV_PREFIXES = ("ANSYSEM_ROOT", "AWP_ROOT")
FORBIDDEN_FILE_TYPES = {
    stat.S_IFLNK,
    stat.S_IFIFO,
    stat.S_IFSOCK,
    stat.S_IFBLK,
    stat.S_IFCHR,
}


class IsolationError(RuntimeError):
    pass


def _walk(root: Path):
    yield root
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(current)
        for name in directories:
            yield base / name
        for name in files:
            yield base / name


def _validate_submission() -> None:
    try:
        SUBMISSION.relative_to(Path("/"))
    except ValueError as exc:
        raise IsolationError("submission path must be absolute") from exc
    if not SUBMISSION.is_dir() or SUBMISSION.is_symlink():
        raise IsolationError("submission root must be a real directory")
    for path in _walk(SUBMISSION):
        info = path.lstat()
        kind = stat.S_IFMT(info.st_mode)
        if kind in FORBIDDEN_FILE_TYPES:
            raise IsolationError(f"forbidden submission file type: {path}")
        if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
            raise IsolationError(f"hard-linked submission file: {path}")
        if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
            raise IsolationError(f"unsupported submission file type: {path}")


def _private_tree(root: Path) -> dict[Path, int]:
    if not root.is_dir() or root.is_symlink():
        raise IsolationError(f"private verifier tree is unsafe: {root}")
    modes = {}
    for path in _walk(root):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise IsolationError(f"symlink in private verifier tree: {path}")
        modes[path] = stat.S_IMODE(info.st_mode)
        os.chown(path, 0, 0, follow_symlinks=False)
        os.chmod(path, 0o700 if stat.S_ISDIR(info.st_mode) else 0o600)
    for path in modes:
        if stat.S_IMODE(path.lstat().st_mode) & 0o077:
            raise IsolationError(f"could not protect verifier path: {path}")
    return modes


def _restore_modes(modes: dict[Path, int]) -> None:
    for path, mode in sorted(modes.items(), key=lambda item: len(item[0].parts), reverse=True):
        if path.exists() and not path.is_symlink():
            os.chmod(path, mode)


def _unused_identity() -> tuple[int, int, list[int]]:
    used_uids = {entry.pw_uid for entry in pwd.getpwall()}
    used_gids = {entry.gr_gid for entry in grp.getgrall()}
    for uid in range(59999, 59000, -1):
        if uid not in used_uids and uid not in used_gids:
            supplementary = [
                entry.gr_gid for entry in grp.getgrall()
                if entry.gr_name in {"render", "video"}
            ]
            return uid, uid, supplementary
    raise IsolationError("no unused replay UID available")


def _chown_submission(uid: int, gid: int, writable: bool) -> None:
    for path in _walk(SUBMISSION):
        info = path.lstat()
        os.chown(path, uid if writable else 0, gid if writable else 0, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            os.chmod(path, 0o700 if writable else 0o500)
        else:
            executable = bool(info.st_mode & 0o111)
            os.chmod(path, (0o700 if executable else 0o600) if writable else (0o500 if executable else 0o400))


def _sanitize_and_freeze_submission() -> None:
    """Remove unsafe replay outputs, then make all remaining evidence root-only."""
    paths = sorted(_walk(SUBMISSION), key=lambda path: len(path.parts), reverse=True)
    for path in paths:
        info = path.lstat()
        if path != SUBMISSION and (
            stat.S_IFMT(info.st_mode) in FORBIDDEN_FILE_TYPES
            or (stat.S_ISREG(info.st_mode) and info.st_nlink != 1)
            or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))
        ):
            path.unlink(missing_ok=True)
            continue
        os.chown(path, 0, 0, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            os.chmod(path, 0o500)
        else:
            os.chmod(path, 0o500 if info.st_mode & 0o111 else 0o400)


def _write_aedt_temp_config(home: Path) -> None:
    for name in os.environ:
        match = re.fullmatch(r"ANSYSEM_ROOT(\d{2})(\d)", name)
        if match is None:
            continue
        product = f"ElectronicsDesktop20{match.group(1)}.{match.group(2)}"
        config = home / "Ansoft" / product / "config" / "default.cfg"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("$begin 'Config'\n\ttempdirectory='" + str(home / "tmp") + "'\n$end 'Config'\n")


def _copy_runtime_config(home: Path, uid: int, gid: int) -> None:
    for relative in (".config/Lumerical", ".config/Ansys", ".ansys"):
        source = Path("/root") / relative
        target = home / relative
        if not source.exists() or source.is_symlink():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, symlinks=False)
    _write_aedt_temp_config(home)
    for path in _walk(home):
        os.chown(path, uid, gid, follow_symlinks=False)


def _candidate_environment(home: Path) -> dict[str, str]:
    result = {
        "HOME": str(home),
        "USER": "pbsolver",
        "LOGNAME": "pbsolver",
        "TMPDIR": str(home / "tmp"),
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "PYTHONNOUSERSITE": "1",
    }
    for name, value in os.environ.items():
        upper = name.upper()
        if any(marker in upper for marker in DENIED_ENV_MARKERS):
            continue
        if (name in ALLOWED_ENV_NAMES or name.endswith(ALLOWED_ENV_SUFFIXES)
                or upper.startswith(ALLOWED_ENV_PREFIXES)):
            result[name] = value
    python_path = os.environ.get("PYTHONPATH", "")
    safe_python_path = [part for part in python_path.split(os.pathsep) if part and not part.startswith(str(TESTS))]
    if safe_python_path:
        result["PYTHONPATH"] = os.pathsep.join(safe_python_path)
    return result


def _drop_privileges(uid: int, gid: int, supplementary: list[int]) -> None:
    os.setgroups(supplementary)
    os.setgid(gid)
    os.setuid(uid)
    os.umask(0o077)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_NO_NEW_PRIVS) failed")


def _kill_uid(uid: int) -> None:
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            status = (entry / "status").read_text(errors="replace")
            uid_line = next(line for line in status.splitlines() if line.startswith("Uid:"))
            real_uid = int(uid_line.split()[1])
            if real_uid == uid:
                os.kill(int(entry.name), signal.SIGKILL)
        except (FileNotFoundError, PermissionError, ProcessLookupError, StopIteration, ValueError):
            continue


def _write_report(**values) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(values, indent=2, sort_keys=True) + "\n")
    os.chown(REPORT, 0, 0)
    os.chmod(REPORT, 0o600)


def main() -> int:
    if os.geteuid() != 0:
        print("safe replay requires verifier root to establish isolation", file=sys.stderr)
        return 125
    if len(sys.argv) < 2:
        print("usage: safe_replay.py /home/submission/reproduce.sh [args...]", file=sys.stderr)
        return 125

    LOGS.mkdir(parents=True, exist_ok=True)
    os.chown(LOGS, 0, 0)
    os.chmod(LOGS, 0o700)
    (LOGS / "reward.txt").unlink(missing_ok=True)

    started = time.time()
    tests_modes: dict[Path, int] = {}
    replay_home: Path | None = None
    uid = gid = -1
    process: subprocess.Popen | None = None
    exit_code = 125
    status = "isolation_error"
    error = None

    def interrupt(signum, _frame):
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        raise InterruptedError(f"safe replay interrupted by signal {signum}")

    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    try:
        _validate_submission()
        script = Path(sys.argv[1]).resolve(strict=True)
        script.relative_to(SUBMISSION)
        if script.is_symlink() or not script.is_file():
            raise IsolationError("replay entrypoint must be a regular submission file")

        uid, gid, supplementary = _unused_identity()
        tests_modes = _private_tree(TESTS)
        _chown_submission(uid, gid, writable=True)
        replay_home = Path(tempfile.mkdtemp(prefix="pbx-replay-", dir="/tmp"))
        (replay_home / "tmp").mkdir()
        _copy_runtime_config(replay_home, uid, gid)
        command = ["/bin/bash", str(script), *sys.argv[2:]]
        process = subprocess.Popen(
            command,
            cwd=SUBMISSION,
            env=_candidate_environment(replay_home),
            start_new_session=True,
            preexec_fn=lambda: _drop_privileges(uid, gid, supplementary),
        )
        try:
            exit_code = process.wait(timeout=TIMEOUT_SEC)
            status = "completed" if exit_code == 0 else "replay_nonzero"
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            exit_code = 124
            status = "replay_timeout"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        print(f"safe replay failed closed: {error}", file=sys.stderr)
    finally:
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if uid >= 0:
            _kill_uid(uid)
        try:
            _sanitize_and_freeze_submission()
        except Exception as exc:
            status = "post_replay_isolation_error"
            exit_code = 125
            error = error or f"{type(exc).__name__}: {exc}"
        if tests_modes:
            _restore_modes(tests_modes)
        if replay_home is not None:
            shutil.rmtree(replay_home, ignore_errors=True)
        _write_report(
            status=status,
            exit_code=exit_code,
            elapsed_seconds=round(time.time() - started, 3),
            replay_uid=uid,
            judge_environment_exposed=False,
            tests_exposed=False,
            error=error,
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
