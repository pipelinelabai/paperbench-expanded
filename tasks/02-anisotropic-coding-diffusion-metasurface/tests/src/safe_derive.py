#!/usr/bin/env python3
"""Run derive.py --check in a solver-free, credential-free, network-denied chroot.

This is a fail-only prerequisite, not proof that a candidate's check is honest.
The scientific judge must also inspect its implementation and coverage.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import errno
import hashlib
import json
import os
import pwd
import resource
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from pathlib import Path

RUNTIME = Path('/opt/pbx-derive-root')
SUBMISSION = Path(os.environ.get('SUBMISSION_DIR', '/home/submission'))
LOGS = Path(os.environ.get('VERIFIER_LOG_DIR', '/logs/verifier'))
TIMEOUT = 600


def snapshot(root: Path) -> dict[str, str]:
    out = {}
    if root.is_symlink() or not root.is_dir():
        raise ValueError('submission must be a real directory')
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if rel.parts[0] == 'hfss':
            continue
        if rel.parts[0] == 'views' and path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
            continue
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError(f'unsafe derive input: {rel}')
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(block)
        out[rel.as_posix()] = digest.hexdigest()
    return out


def deny_network() -> None:
    """Kernel-enforced denial, inherited by every descendant of derive.py."""
    libname = ctypes.util.find_library('seccomp')
    if not libname:
        raise RuntimeError('libseccomp is required; no permissive fallback')
    lib = ctypes.CDLL(libname, use_errno=True)
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_rule_add.restype = ctypes.c_int
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_load.restype = ctypes.c_int
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW
    if not ctx:
        raise RuntimeError('seccomp_init failed')
    try:
        for name in (b'socket', b'socketpair', b'connect', b'bind', b'listen',
                     b'accept', b'accept4', b'sendto', b'sendmsg', b'sendmmsg',
                     b'io_uring_setup'):
            number = lib.seccomp_syscall_resolve_name(name)
            if number >= 0 and lib.seccomp_rule_add(ctx, 0x00050000 | errno.EPERM, number, 0):
                raise RuntimeError(f'seccomp rule failed: {name!r}')
        if lib.seccomp_load(ctx):
            raise RuntimeError('seccomp_load failed')
    finally:
        lib.seccomp_release(ctx)


def isolate(jail: Path, uid: int) -> None:
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT, TIMEOUT + 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024**2, 64 * 1024**2))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(38, 1, 0, 0, 0):  # PR_SET_NO_NEW_PRIVS
        raise OSError(ctypes.get_errno(), 'PR_SET_NO_NEW_PRIVS')
    deny_network()
    os.chroot(jail)
    os.chdir('/home/submission')
    os.setgroups([])
    os.setgid(uid)
    os.setuid(uid)
    os.umask(0o077)


def kill_uid(uid: int) -> None:
    for path in Path('/proc').glob('[0-9]*/status'):
        try:
            row = next(line for line in path.read_text().splitlines() if line.startswith('Uid:'))
            if int(row.split()[1]) == uid:
                os.kill(int(path.parent.name), signal.SIGKILL)
        except (OSError, ValueError, StopIteration):
            pass


def main() -> int:
    private = LOGS / 'private'
    private.mkdir(parents=True, exist_ok=True)
    report = {'owner': 'paperbench-expanded_verifier', 'schema_version': 1,
              'status': 'infrastructure_error', 'exit_code': None,
              'runtime': 'python3.11+numpy+scipy; no HFSS/AEDT',
              'network_denied': False, 'input_sha256': {}}
    process = None
    jail = None
    uid = None
    started = time.time()
    try:
        if os.geteuid() != 0:
            raise RuntimeError('derive isolation requires verifier root')
        if not (RUNTIME / 'usr/local/bin/python3').exists():
            raise RuntimeError('offline derive runtime missing; rebuild the task image')
        before = snapshot(SUBMISSION)
        report['input_sha256'] = before
        if 'src/derive.py' not in before:
            report.update(status='candidate_missing_derive', exit_code=127)
            return 0
        used = {item.pw_uid for item in pwd.getpwall()}
        uid = next(value for value in range(58999, 58000, -1) if value not in used)
        jail = Path(tempfile.mkdtemp(prefix='pbx-derive-', dir='/tmp'))
        shutil.copytree(RUNTIME, jail, symlinks=True, dirs_exist_ok=True)
        evidence = jail / 'home/submission'
        evidence.mkdir(parents=True, exist_ok=True)
        for name in before:
            target = evidence / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SUBMISSION / name, target)
            target.chmod(0o444)
        for path in [evidence, *evidence.rglob('*')]:
            if path.is_dir():
                path.chmod(0o555)
        (jail / 'tmp').mkdir(exist_ok=True)
        (jail / 'tmp').chmod(0o1777)
        jail.chmod(0o755)
        with (private / 'derive_check.log').open('wb') as output:
            process = subprocess.Popen(
                ['/usr/local/bin/python3', '/home/submission/src/derive.py',
                 '--results', '/home/submission/results', '--check'],
                env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/tmp',
                     'TMPDIR': '/tmp', 'PYTHONDONTWRITEBYTECODE': '1',
                     'PYTHONNOUSERSITE': '1', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'},
                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                close_fds=True, start_new_session=True,
                preexec_fn=lambda: isolate(jail, uid),
            )
            report['network_denied'] = True
            try:
                rc = process.wait(timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                rc = 124
        if snapshot(SUBMISSION) != before:
            raise RuntimeError('original evidence changed during isolated derive check')
        report.update(status='completed' if rc == 0 else 'candidate_check_failed', exit_code=rc)
        return 0
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        return 125
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        if uid is not None:
            kill_uid(uid)
        if jail is not None:
            shutil.rmtree(jail)
        report['elapsed_seconds'] = round(time.time() - started, 3)
        (private / 'derive_receipt.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report.get(key) for key in ('status', 'exit_code', 'error')}))


if __name__ == '__main__':
    raise SystemExit(main())
