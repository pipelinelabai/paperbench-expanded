#!/usr/bin/env python3
"""Prepare, run, and freeze an untrusted PaperBench High-Difficulty and Expanded Tasks submission replay."""

import argparse
import hashlib
import json
import math
import os
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid
from pathlib import Path


SUBMISSION = Path("/home/submission")
STARTER = Path("/home/starter_submission")
LOG_DIR = Path("/logs/verifier")
SOURCE_SNAPSHOT = LOG_DIR / "source_submission"
EVIDENCE_ROOT = LOG_DIR / "candidate_outputs"
STATE_PATH = LOG_DIR / ".candidate_replay_state.json"
BEFORE_MANIFEST = LOG_DIR / "candidate_inputs_before.sha256"
AFTER_MANIFEST = LOG_DIR / "candidate_inputs_after.sha256"
REPLAY_LOG = LOG_DIR / "candidate_replay.log"
SOLVER_UID = 65532
SOLVER_GID = 65532
RUNTIME_WRITABLE_ROOT = Path("/tmp")
FIREWALL_CHAIN = "PBX_REPLAY_OUT"
IPV6_INTERFACES = Path("/proc/net/if_inet6")
# util-linux/libcap-ng versions in the oldest task images reject the newer
# ``-all`` shorthand. Drop the explicit complete set instead and keep the
# preflight assertion aligned with the command used for the real replay.
CAPABILITY_DROP = "-" + ",-".join((
    "chown", "dac_override", "dac_read_search", "fowner", "fsetid", "kill",
    "setgid", "setuid", "setpcap", "linux_immutable", "net_bind_service",
    "net_broadcast", "net_admin", "net_raw", "ipc_lock", "ipc_owner",
    "sys_module", "sys_rawio", "sys_chroot", "sys_ptrace", "sys_pacct",
    "sys_admin", "sys_boot", "sys_nice", "sys_resource", "sys_time",
    "sys_tty_config", "mknod", "lease", "audit_write", "audit_control",
    "setfcap", "mac_override", "mac_admin", "syslog", "wake_alarm",
    "block_suspend", "audit_read",
))
RUNNER_GENERATED = {"candidate_replay.json", "replay_receipt.json"}


class CandidateError(RuntimeError):
    pass


class InfrastructureError(RuntimeError):
    pass


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_roots(raw_roots):
    roots = []
    for raw in raw_roots:
        for value in raw.split(","):
            name = value.strip().strip("/")
            if not name:
                continue
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
                raise CandidateError(f"generated root must be one top-level name: {value!r}")
            roots.append(name)
    return sorted(set(roots))


def scan_tree(root, excluded=None):
    """Return regular files and reject links/devices/sockets anywhere in the tree."""
    excluded = excluded or set()
    if not root.is_dir():
        return []
    files = []
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root)
        if relative_dir == Path("."):
            dirs[:] = [name for name in dirs if name not in excluded]
            names = [name for name in names if name not in excluded]
        for name in list(dirs):
            path = current_path / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise CandidateError(f"unsafe submission entry: {path.relative_to(root)}")
        for name in names:
            path = current_path / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise CandidateError(f"unsafe submission entry: {path.relative_to(root)}")
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def manifest(root, excluded):
    lines = []
    for path in scan_tree(root, excluded):
        relative = path.relative_to(root).as_posix()
        lines.append(f"{file_sha256(path)}  {relative}")
    return "\n".join(lines) + ("\n" if lines else "")


def copy_source_snapshot(excluded):
    if SOURCE_SNAPSHOT.exists():
        shutil.rmtree(SOURCE_SNAPSHOT)
    SOURCE_SNAPSHOT.mkdir(parents=True)
    for item in sorted(SUBMISSION.iterdir(), key=lambda path: path.name):
        if item.name in excluded:
            continue
        if item.is_dir():
            shutil.copytree(item, SOURCE_SNAPSHOT / item.name, symlinks=False)
        else:
            shutil.copy2(item, SOURCE_SNAPSHOT / item.name)
    make_readable_frozen(SOURCE_SNAPSHOT)


def clean_generated(roots):
    for name in roots:
        target = SUBMISSION / name
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                raise CandidateError(f"generated root is a symlink: {name}")
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.mkdir(parents=True, mode=0o755)
        os.chown(target, SOLVER_UID, SOLVER_GID)


def clean_generated_files(names):
    for name in names:
        target = SUBMISSION / name
        if not target.exists() and not target.is_symlink():
            continue
        if target.is_symlink() or not target.is_file():
            raise CandidateError(f"generated file has an unsafe type: {name}")
        target.unlink()


def validate_runtime_writable_paths(raw_paths):
    """Accept only explicitly declared direct children of the replay temp root."""
    paths = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute() or path.parent != RUNTIME_WRITABLE_ROOT:
            raise InfrastructureError(
                f"runtime writable path must be a direct child of {RUNTIME_WRITABLE_ROOT}: {raw!r}"
            )
        paths.append(path)
    return sorted(set(paths), key=str)


def provision_runtime_writable_paths(paths):
    """Recreate fixed log files as private files owned by the replay uid."""
    try:
        root_info = RUNTIME_WRITABLE_ROOT.lstat()
    except OSError as error:
        raise InfrastructureError(f"runtime writable root is unavailable: {RUNTIME_WRITABLE_ROOT}") from error
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise InfrastructureError(f"runtime writable root is unsafe: {RUNTIME_WRITABLE_ROOT}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    for path in paths:
        try:
            info = path.lstat()
        except FileNotFoundError:
            info = None
        if info is not None:
            if not (stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode)):
                raise CandidateError(f"runtime writable path has an unsafe type: {path}")
            path.unlink()
        try:
            descriptor = os.open(path, flags, 0o600)
            try:
                os.fchmod(descriptor, 0o600)
                os.fchown(descriptor, SOLVER_UID, SOLVER_GID)
            finally:
                os.close(descriptor)
        except OSError as error:
            raise InfrastructureError(f"cannot provision runtime writable path: {path}") from error


def owner_snapshot(root):
    owners = {}
    if not root.exists():
        return owners
    paths = [root]
    paths.extend(sorted(root.rglob("*"), key=lambda path: len(path.parts)))
    for path in paths:
        info = path.lstat()
        owners[str(path.relative_to(root))] = [info.st_uid, info.st_gid]
    return owners


def restore_owners(state):
    for relative, owner in sorted(
        state.get("owners", {}).items(), key=lambda item: len(Path(item[0]).parts), reverse=True
    ):
        path = SUBMISSION if relative == "." else SUBMISSION / relative
        if path.exists() and not path.is_symlink():
            try:
                os.chown(path, int(owner[0]), int(owner[1]))
            except OSError:
                pass


def run_checked(command, input_text=None):
    environment = os.environ.copy()
    environment["XTABLES_LOCKFILE"] = "/tmp/pbx-xtables.lock"
    result = subprocess.run(
        command, input=input_text, universal_newlines=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=environment,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise InfrastructureError(f"command failed ({result.returncode}): {' '.join(command)}: {detail}")


def has_non_loopback_ipv6():
    """Require an IPv6 owner rule only when IPv6 is actually enabled."""
    try:
        rows = IPV6_INTERFACES.read_text(encoding="ascii").splitlines()
    except OSError:
        return False
    for row in rows:
        fields = row.split()
        if len(fields) >= 6 and fields[-1] != "lo":
            return True
    return False


def firewall_cleanup():
    environment = os.environ.copy()
    environment["XTABLES_LOCKFILE"] = "/tmp/pbx-xtables.lock"
    for binary in ("iptables", "ip6tables"):
        if not shutil.which(binary):
            continue
        subprocess.run(
            [binary, "-w", "-D", "OUTPUT", "-m", "owner", "--uid-owner", str(SOLVER_UID),
             "-j", FIREWALL_CHAIN],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, env=environment,
        )
        subprocess.run(
            [binary, "-w", "-F", FIREWALL_CHAIN],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, env=environment,
        )
        subprocess.run(
            [binary, "-w", "-X", FIREWALL_CHAIN],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, env=environment,
        )


def firewall_setup():
    firewall_cleanup()
    rules = ["iptables"]
    if has_non_loopback_ipv6():
        rules.append("ip6tables")
    for binary in rules:
        if not shutil.which(binary):
            raise InfrastructureError(f"{binary} is not installed")
        run_checked([binary, "-w", "-N", FIREWALL_CHAIN])
        run_checked([binary, "-w", "-A", FIREWALL_CHAIN, "-o", "lo", "-j", "ACCEPT"])
        run_checked([binary, "-w", "-A", FIREWALL_CHAIN, "-j", "REJECT"])
        run_checked([
            binary, "-w", "-I", "OUTPUT", "1", "-m", "owner", "--uid-owner",
            str(SOLVER_UID), "-j", FIREWALL_CHAIN,
        ])


def protect_verifier_paths(enable):
    if not shutil.which("setfacl"):
        raise InfrastructureError("setfacl is not installed")
    for path in (Path("/tests"), LOG_DIR):
        if not path.exists():
            raise InfrastructureError(f"{path} is missing")
        args = ["setfacl", "-m", f"u:{SOLVER_UID}:---", str(path)] if enable else [
            "setfacl", "-x", f"u:{SOLVER_UID}", str(path)
        ]
        result = subprocess.run(
            args, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False,
        )
        if enable and result.returncode:
            raise InfrastructureError(
                f"could not protect {path} from replay uid: {result.stderr.strip()}")


def cpu_limit():
    limits = []
    try:
        limits.append(len(os.sched_getaffinity(0)))
    except (AttributeError, OSError):
        pass
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text(encoding="utf-8").split()
        if quota != "max":
            limits.append(max(1, math.ceil(int(quota) / int(period))))
    except (OSError, ValueError):
        pass
    for path in (Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"),):
        try:
            quota = int(path.read_text(encoding="utf-8"))
            period = int(path.with_name("cpu.cfs_period_us").read_text(encoding="utf-8"))
            if quota > 0:
                limits.append(max(1, math.ceil(quota / period)))
        except (OSError, ValueError):
            pass
    return max(1, min(limits or [os.cpu_count() or 1]))


def replay_environment():
    blocked_prefixes = ("ANTHROPIC_", "OPENAI_", "JUDGE_")
    blocked_names = {
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
        "UV_INDEX", "UV_INDEX_URL", "UV_DEFAULT_INDEX", "PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL",
    }
    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith(blocked_prefixes) and key not in blocked_names
    }
    home = Path("/tmp/pbx-solver-home")
    temporary = Path("/tmp/pbx-solver-tmp")
    for path in (home, temporary):
        path.mkdir(parents=True, exist_ok=True)
        os.chown(path, SOLVER_UID, SOLVER_GID)
        path.chmod(0o700)
    workers = cpu_limit()
    configured_workers = os.environ.get("PBX_MAX_WORKERS")
    if configured_workers:
        try:
            configured_workers_int = int(configured_workers)
        except ValueError as error:
            raise InfrastructureError("PBX_MAX_WORKERS must be a positive integer") from error
        if configured_workers_int < 1:
            raise InfrastructureError("PBX_MAX_WORKERS must be a positive integer")
        workers = min(workers, configured_workers_int)
    env.update({
        "HOME": str(home),
        "TMPDIR": str(temporary),
        "USER": "solver",
        "LOGNAME": "solver",
        "PBX_MAX_WORKERS": str(workers),
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "TOKENIZERS_PARALLELISM": "false",
        "PYTHONDONTWRITEBYTECODE": "1",
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "PIP_NO_INDEX": "1",
        "UV_OFFLINE": "1",
        "NO_PROXY": "*",
        "HTTP_PROXY": "",
        "HTTPS_PROXY": "",
        "ALL_PROXY": "",
    })
    return env


def gpu_infrastructure_problem():
    """Return a verifier-observed GPU fault without trusting candidate log text."""
    binary = shutil.which("nvidia-smi")
    if binary is None:
        return None
    result = subprocess.run(
        [binary, "--query-gpu=index,name", "--format=csv,noheader"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    detail = (result.stderr or result.stdout).strip()
    if result.returncode:
        return f"nvidia-smi failed after replay: {detail or f'exit {result.returncode}'}"
    lowered = detail.lower()
    fatal_markers = (
        "requires reset",
        "couldn't communicate with the nvidia driver",
        "driver/library version mismatch",
        "no devices were found",
    )
    if any(marker in lowered for marker in fatal_markers):
        return f"nvidia-smi reported an unusable GPU after replay: {detail}"
    return None


def load_state():
    if not STATE_PATH.is_file():
        raise InfrastructureError("prepare state is missing")
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state):
    atomic_json(STATE_PATH, state)


def record_failure(kind, stage, message, **extra):
    payload = {
        "schema_version": 1,
        "kind": kind,
        "stage": stage,
        "message": message,
        "time_unix": time.time(),
    }
    payload.update(extra)
    atomic_json(LOG_DIR / f"{kind}_failure.json", payload)


def remove_replay_artifact(path):
    """Remove only verifier-owned state left by a prior invocation."""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        raise InfrastructureError(f"stale verifier artifact is a symlink: {path}")
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def reset_prepare_artifacts():
    # A verifier can be invoked more than once in the same container. Never let a failed
    # preparation leave an older evidence tree or receipt available to a later invocation.
    for path in (
        SOURCE_SNAPSHOT,
        EVIDENCE_ROOT,
        STATE_PATH,
        BEFORE_MANIFEST,
        AFTER_MANIFEST,
        REPLAY_LOG,
        LOG_DIR / "delivery_status.json",
        LOG_DIR / "replay_exit_code.txt",
        LOG_DIR / "candidate_replay.json",
        LOG_DIR / "candidate_failure.json",
        LOG_DIR / "infra_failure.json",
    ):
        remove_replay_artifact(path)


def record_rejected_replay(command, error):
    """Emit the mandatory audit files even when prepare cannot create a replay state."""
    exit_code = 73
    (LOG_DIR / "replay_exit_code.txt").write_text(f"{exit_code}\n", encoding="utf-8")
    atomic_json(LOG_DIR / "candidate_replay.json", {
        "schema_version": 1,
        "status": "rejected",
        "stage": command,
        "exit_code": exit_code,
        "source_unchanged": None,
        "message": str(error),
    })


def prepare(args):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    reset_prepare_artifacts()
    roots = validate_roots(args.generated_root)
    runtime_writable_paths = validate_runtime_writable_paths(
        getattr(args, "runtime_writable_path", [])
    )
    excluded = set(roots) | RUNNER_GENERATED
    if not SUBMISSION.is_dir():
        atomic_json(LOG_DIR / "delivery_status.json", {
            "schema_version": 1, "status": "missing_submission", "entrypoint": False,
        })
        raise CandidateError("/home/submission is missing")
    scan_tree(SUBMISSION)
    before = manifest(SUBMISSION, excluded)
    starter = manifest(STARTER, excluded) if STARTER.is_dir() else None
    entrypoint = (SUBMISSION / "reproduce.sh").is_file()
    status = "delivered"
    if starter is not None and before == starter:
        status = "unchanged_starter"
    if not entrypoint:
        status = "missing_entrypoint"
    atomic_json(LOG_DIR / "delivery_status.json", {
        "schema_version": 1,
        "status": status,
        "entrypoint": entrypoint,
        "source_file_count": len(before.splitlines()),
        "source_manifest_sha256": hashlib.sha256(before.encode()).hexdigest(),
    })
    copy_source_snapshot(excluded)
    BEFORE_MANIFEST.write_text(before, encoding="utf-8")
    owners = owner_snapshot(SUBMISSION)
    state = {
        "schema_version": 1,
        "nonce": uuid.uuid4().hex,
        "prepared_at_unix": time.time(),
        "generated_roots": roots,
        "runtime_writable_paths": [str(path) for path in runtime_writable_paths],
        "owners": owners,
        "attempts": [],
    }
    save_state(state)
    clean_generated(roots)
    clean_generated_files(RUNNER_GENERATED)
    for path in [SUBMISSION] + list(SUBMISSION.rglob("*")):
        if not path.is_symlink():
            os.chown(path, SOLVER_UID, SOLVER_GID)
    provision_runtime_writable_paths(runtime_writable_paths)
    protect_verifier_paths(True)
    firewall_setup()
    REPLAY_LOG.write_text("", encoding="utf-8")
    return 0


def generated_signature(roots):
    digest = hashlib.sha256()
    for name in roots:
        root = SUBMISSION / name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            try:
                info = path.stat()
            except OSError:
                continue
            digest.update(str(path.relative_to(SUBMISSION)).encode())
            digest.update(f"\0{info.st_size}\0{info.st_mtime_ns}\n".encode())
    return digest.hexdigest()


def run_replay(args):
    state = load_state()
    entrypoint = SUBMISSION / "reproduce.sh"
    if not entrypoint.is_file():
        return 64
    env = replay_environment()
    command = [
        "setpriv", f"--reuid={SOLVER_UID}", f"--regid={SOLVER_GID}", "--clear-groups",
        "--no-new-privs", f"--bounding-set={CAPABILITY_DROP}",
        f"--inh-caps={CAPABILITY_DROP}", f"--ambient-caps={CAPABILITY_DROP}",
        "env", "-i",
    ]
    command.extend(f"{key}={value}" for key, value in sorted(env.items()))
    command.extend(["bash", str(entrypoint)])
    started = time.time()
    timed_out = False
    with REPLAY_LOG.open("a", encoding="utf-8", errors="replace") as log:
        header = f"\n=== replay attempt {args.attempt} at {started:.6f} ===\n"
        log.write(header)
        log.flush()
        sys.stdout.write(header)
        sys.stdout.flush()
        process = subprocess.Popen(
            command, cwd=SUBMISSION, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        def forward(signum, _frame):
            if process.poll() is None:
                os.killpg(process.pid, signum)

        previous = {sig: signal.signal(sig, forward) for sig in (signal.SIGTERM, signal.SIGINT)}
        selector = selectors.DefaultSelector()
        assert process.stdout is not None
        selector.register(process.stdout, selectors.EVENT_READ)
        signature = generated_signature(state["generated_roots"])
        last_change = time.monotonic()
        scan_interval = min(60.0, max(1.0, args.stall_seconds / 10.0)) \
            if args.stall_seconds > 0 else 60.0
        next_scan = time.monotonic() + scan_interval
        try:
            while process.poll() is None:
                for key, _ in selector.select(timeout=1.0):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if chunk:
                        text_chunk = chunk.decode("utf-8", errors="replace")
                        log.write(text_chunk)
                        log.flush()
                        sys.stdout.write(text_chunk)
                        sys.stdout.flush()
                    else:
                        selector.unregister(key.fileobj)
                if args.stall_seconds > 0 and time.monotonic() >= next_scan:
                    current = generated_signature(state["generated_roots"])
                    if current != signature:
                        signature = current
                        last_change = time.monotonic()
                    elif time.monotonic() - last_change >= args.stall_seconds:
                        timed_out = True
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                        break
                    next_scan = time.monotonic() + scan_interval
            # A successful entrypoint must not leave policy servers or workers mutating evidence.
            # Every child belongs to this dedicated session/process group.
            try:
                os.killpg(process.pid, signal.SIGTERM)
                time.sleep(0.2)
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            remainder = process.stdout.read()
            if remainder:
                text_chunk = remainder.decode("utf-8", errors="replace")
                log.write(text_chunk)
                sys.stdout.write(text_chunk)
        finally:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        return_code = 124 if timed_out else process.wait()
        if return_code < 0:
            return_code = 128 - return_code
    state["attempts"].append({
        "attempt": args.attempt,
        "started_at_unix": started,
        "elapsed_seconds": round(time.time() - started, 3),
        "exit_code": return_code,
        "stall_timeout": timed_out,
        "pbx_max_workers": int(env["PBX_MAX_WORKERS"]),
    })
    save_state(state)
    gpu_problem = gpu_infrastructure_problem() if return_code != 0 else None
    if gpu_problem is not None:
        record_failure("infra", "gpu_health", gpu_problem, exit_code=return_code)
        return 70
    return return_code


def make_readable_frozen(root):
    if not root.exists():
        return
    for path in [root] + list(root.rglob("*")):
        if path.is_symlink():
            continue
        os.chown(path, 0, 0)
        path.chmod(0o755 if path.is_dir() else 0o644)


def freeze(args):
    state = load_state()
    roots = state["generated_roots"]
    excluded = set(roots) | RUNNER_GENERATED
    scan_tree(SUBMISSION)
    after = manifest(SUBMISSION, excluded)
    AFTER_MANIFEST.write_text(after, encoding="utf-8")
    before = BEFORE_MANIFEST.read_text(encoding="utf-8")
    source_unchanged = before == after
    (LOG_DIR / "replay_exit_code.txt").write_text(f"{args.exit_code}\n", encoding="utf-8")
    receipt = SUBMISSION / "replay_receipt.json"
    replay_record = {
        "schema_version": 1,
        "status": "ok" if args.exit_code == 0 and source_unchanged else "failed",
        "nonce": state["nonce"],
        "exit_code": args.exit_code,
        "prepared_at_unix": state["prepared_at_unix"],
        "elapsed_seconds": round(sum(item["elapsed_seconds"] for item in state["attempts"]), 3),
        "attempts": state["attempts"],
        "source_manifest_before_sha256": hashlib.sha256(before.encode()).hexdigest(),
        "source_manifest_after_sha256": hashlib.sha256(after.encode()).hexdigest(),
        "source_unchanged": source_unchanged,
        "runtime_writable_paths": state.get("runtime_writable_paths", []),
        "replay_log_sha256": file_sha256(REPLAY_LOG),
        "candidate_receipt_sha256": file_sha256(receipt) if receipt.is_file() else None,
    }
    atomic_json(LOG_DIR / "candidate_replay.json", replay_record)
    if not source_unchanged:
        record_failure("candidate", "source_manifest", "candidate source changed during replay")
        restore_owners(state)
        return 73
    atomic_json(SUBMISSION / "candidate_replay.json", replay_record)
    temporary = LOG_DIR / ".candidate_outputs.tmp"
    if temporary.exists():
        shutil.rmtree(temporary)
    if EVIDENCE_ROOT.exists():
        shutil.rmtree(EVIDENCE_ROOT)
    shutil.copytree(SUBMISSION, temporary, symlinks=False)
    os.replace(temporary, EVIDENCE_ROOT)
    make_readable_frozen(EVIDENCE_ROOT)
    restore_owners(state)
    return 0


def cleanup(_args):
    firewall_cleanup()
    try:
        protect_verifier_paths(False)
    except InfrastructureError:
        pass
    if STATE_PATH.is_file():
        try:
            restore_owners(load_state())
        except (OSError, ValueError, InfrastructureError):
            pass
    make_readable_frozen(LOG_DIR)
    return 0


def write_failure(args):
    record_failure(args.kind, args.stage, args.message, exit_code=args.exit_code)
    return 0


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--generated-root", action="append", default=["results"])
    prepare_parser.add_argument("--runtime-writable-path", action="append", default=[])
    prepare_parser.set_defaults(func=prepare)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--attempt", type=int, required=True)
    run_parser.add_argument("--stall-seconds", type=int, default=0)
    run_parser.set_defaults(func=run_replay)
    clean_parser = subparsers.add_parser("clean")
    clean_parser.set_defaults(func=lambda _args: (clean_generated(load_state()["generated_roots"]), 0)[1])
    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("--exit-code", type=int, required=True)
    freeze_parser.set_defaults(func=freeze)
    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.set_defaults(func=cleanup)
    failure_parser = subparsers.add_parser("failure")
    failure_parser.add_argument("--kind", choices=("infra", "candidate"), required=True)
    failure_parser.add_argument("--stage", required=True)
    failure_parser.add_argument("--message", required=True)
    failure_parser.add_argument("--exit-code", type=int, default=None)
    failure_parser.set_defaults(func=write_failure)
    args = parser.parse_args()
    if not args.command:
        parser.error("a command is required")
    try:
        return args.func(args)
    except CandidateError as error:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        record_failure("candidate", args.command, str(error))
        if args.command == "prepare":
            record_rejected_replay(args.command, error)
        print(f"candidate replay rejected: {error}", file=sys.stderr)
        return 73
    except Exception as error:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        record_failure("infra", args.command, str(error))
        print(f"replay infrastructure failure: {error}", file=sys.stderr)
        return 70


if __name__ == "__main__":
    raise SystemExit(main())
