from __future__ import annotations

import os
from pathlib import Path
import pwd
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from evidence_io import digest, load, save, tree_manifest, withhold


SUBMISSION = Path('/home/submission')
PAPER = Path('/home/paper')
DATA = Path('/home/data/horlbeck')
LOGS = Path('/logs/verifier')
TESTS = Path(__file__).resolve().parents[1]
TIMEOUT = 18900
MEMORY_BYTES = 32768 * 1024 * 1024
SAFE_ENV = {'PATH': '/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C.UTF-8',
            'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUNBUFFERED': '1',
            'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}


class IncompleteReplay(RuntimeError):
    pass


class EvidenceContractError(RuntimeError):
    pass


def stop_solver(account):
    completed = subprocess.run(['pkill', '-KILL', '-u', str(account.pw_uid)],
                               env=SAFE_ENV, capture_output=True)
    if completed.returncode not in (0, 1):
        raise RuntimeError('Cannot stop solver-owned processes')


def restore_log_access(owner, mode, solver, verifier):
    protected_groups = {0, verifier.pw_gid}
    public_receipts = {'reward.txt', 'result.json', 'publication.json', 'failure.json',
                       'score_withheld.json', 'native_run.json', 'integrity.json'}
    for path in LOGS.rglob('*'):
        metadata = path.lstat()
        if path.is_symlink() or metadata.st_uid not in (0, verifier.pw_uid):
            raise RuntimeError('Unexpected owner or link in the trusted verifier archive')
        if metadata.st_gid not in protected_groups:
            os.chown(path, metadata.st_uid, verifier.pw_gid)
        path.chmod(metadata.st_mode & 0o770)
        if owner[0] != solver.pw_uid:
            os.chown(path, owner[0], verifier.pw_gid)
        elif path.parent == LOGS and path.is_file() and path.name in public_receipts:
            os.chown(path, owner[0], verifier.pw_gid)
    os.chown(LOGS, *owner)
    LOGS.chmod(mode & (0o700 if owner[1] == solver.pw_gid else 0o750))


def protect_tree(root):
    tree_manifest(root)
    for path in [root, *root.rglob('*')]:
        executable = bool(path.stat().st_mode & 0o111)
        os.chown(path, 0, 0)
        path.chmod(0o555 if path.is_dir() or executable else 0o444)


def archive_tree(source, destination, expected, exclude_results=False):
    if tree_manifest(source, exclude_results=exclude_results) != expected:
        raise RuntimeError('Evidence changed before archival')
    ignored = (lambda directory, names: ['results'] if Path(directory) == source else []) if exclude_results else None
    shutil.copytree(source, destination, ignore=ignored)
    if tree_manifest(destination) != expected:
        raise RuntimeError('Archived evidence does not match its frozen manifest')
    protect_tree(destination)


def block_network(account):
    for binary in ('iptables', 'ip6tables'):
        rule = ['OUTPUT', '-m', 'owner', '--uid-owner', str(account.pw_uid), '-j', 'REJECT']
        subprocess.run([binary, '-w', '10', '-I', *rule], check=True, env=SAFE_ENV,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        subprocess.run([binary, '-w', '10', '-C', *rule], check=True, env=SAFE_ENV,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def validate_inputs():
    reference = load(TESTS / 'refs/targets/key_targets.json')
    if (digest(PAPER / 'paper.md') != reference['paper']['sha256']
            or digest(PAPER / 'conventions.json') != reference['conventions_sha256']):
        raise RuntimeError('Trusted paper or conventions do not match the reference record')
    manifest = load(TESTS / 'refs/inputs/data_manifest.json')
    if manifest != load(PAPER / 'data_manifest.json'):
        raise RuntimeError('Public input manifest differs from the trusted reference')
    for item in manifest['inputs']:
        path = DATA / item['name']
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise RuntimeError('Trusted raw-input provisioning mismatch')


def prepare_workspace(account):
    if not (SUBMISSION / 'reproduce.sh').is_file():
        raise IncompleteReplay('Missing public reproduce.sh entrypoint')
    tree_manifest(SUBMISSION)
    results = SUBMISSION / 'results'
    if results.exists():
        if not results.is_dir():
            raise IncompleteReplay('results must be a directory')
        shutil.rmtree(results)
    before = tree_manifest(SUBMISSION, exclude_results=True)
    protect_tree(SUBMISSION)
    results.mkdir(mode=0o700)
    os.chown(results, account.pw_uid, account.pw_gid)
    if any(results.iterdir()):
        raise RuntimeError('Clean results directory is not empty')
    home = Path(tempfile.mkdtemp(prefix='pbx11-replay-'))
    os.chown(home, account.pw_uid, account.pw_gid)
    return before, home


def native_replay(account, home):
    runtime = {**SAFE_ENV, 'HOME': str(home), 'TMPDIR': str(home),
               'XDG_CACHE_HOME': str(home / '.cache'), 'MPLCONFIGDIR': str(home / '.mpl')}
    command = ['strace', '-f', '-e', 'trace=process', '-o', str(LOGS / 'native.trace'),
               'runuser', '-u', account.pw_name, '--', 'env', '-i',
               *(f'{key}={value}' for key, value in runtime.items()),
               '/bin/bash', '/home/submission/reproduce.sh']
    started = time.monotonic()
    timed_out = False
    with (LOGS / 'native.stdout').open('xb') as stdout, (LOGS / 'native.stderr').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=SUBMISSION, env=SAFE_ENV,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = 124
        finally:
            stop_solver(account)
    receipt = {'native_exit_code': code, 'native_wall_seconds': time.monotonic() - started,
               'timeout_seconds': TIMEOUT, 'memory_bytes': MEMORY_BYTES,
               'network': 'none', 'network_isolation': 'IPv4 and IPv6 solver-UID OUTPUT rejection',
               'read_only_source': True, 'read_only_inputs': True,
               'execution': 'container non-root public entrypoint', 'timed_out': timed_out}
    save(LOGS / 'native_run.json', receipt)
    return receipt


def run_numeric(verifier):
    output = LOGS / 'numeric'
    output.mkdir(mode=0o700)
    os.chown(output, verifier.pw_uid, verifier.pw_gid)
    command = ['runuser', '-u', verifier.pw_name, '--', 'env', '-i',
               *(f'{key}={value}' for key, value in {**SAFE_ENV, 'HOME': '/tmp'}.items()),
               'python3', '-B', str(TESTS / 'src/grade_numeric.py'),
               '--data', str(DATA), '--paper', str(PAPER),
               '--evidence', str(SUBMISSION / 'results/horlbeck_gi_reproduction'),
               '--receipts', str(LOGS), '--policy', str(TESTS / 'config/evaluation.json'),
               '--report', str(output / 'numeric_score.json')]
    with (LOGS / 'numeric.stdout').open('xb') as stdout, (LOGS / 'numeric.stderr').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=TESTS / 'src', env=SAFE_ENV,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=2100)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise RuntimeError('Numeric verifier exceeded its execution allowance')
    protect_tree(output)
    if code or not (output / 'numeric_score.json').is_file():
        report_path = output / 'numeric_score.json'
        try:
            reported = load(report_path) if report_path.is_file() else {}
        except (OSError, ValueError):
            reported = {}
        if reported.get('error_type') == 'AdapterRequired':
            raise EvidenceContractError(
                'Numeric verifier could not resolve the declared evidence-manifest layout: '
                + str(reported.get('error', '')))
        raise RuntimeError('Numeric verifier could not complete; inspect numeric.stderr and its adapter report')
    return load(output / 'numeric_score.json')


def main():
    stage = 'preflight'
    if os.getuid() != 0:
        raise RuntimeError('Verifier requires the container administrator')
    solver, verifier = pwd.getpwnam('pbsolver'), pwd.getpwnam('pbverifier')
    stop_solver(solver)
    for root in (LOGS, TESTS):
        if root.is_symlink():
            raise RuntimeError('Trusted directory must not be a symlink')
    LOGS.mkdir(parents=True, exist_ok=True)
    if any((LOGS / name).exists() for name in ('native_run.json', 'failure.json', 'reward.txt', 'result.json')):
        raise RuntimeError('Use a fresh trial; completed evidence is never overwritten')
    log_owner = (LOGS.stat().st_uid, LOGS.stat().st_gid)
    log_mode = LOGS.stat().st_mode
    try:
        os.chown(LOGS, 0, verifier.pw_gid)
        LOGS.chmod(0o750)
        from judge_review import judge_settings
        judge_settings(os.environ)
        tree_manifest(TESTS)
        for path in [TESTS, *TESTS.rglob('*')]:
            os.chown(path, 0, verifier.pw_gid)
            path.chmod(0o550 if path.is_dir() else 0o440)
        validate_inputs()
        inputs_before = {'paper': tree_manifest(PAPER), 'data': tree_manifest(DATA)}
        protect_tree(PAPER)
        protect_tree(DATA)
        block_network(solver)
        stage = 'clean_replay'
        source_before, home = prepare_workspace(solver)
        save(LOGS / 'source_manifest_before.json', source_before)
        save(LOGS / 'input_manifest_before.json', inputs_before)
        archive_tree(SUBMISSION, LOGS / 'source_submission', source_before, exclude_results=True)
        receipt = native_replay(solver, home)
        source_after = tree_manifest(SUBMISSION, exclude_results=True)
        save(LOGS / 'source_manifest_after.json', source_after)
        unchanged = source_before == source_after
        inputs_after = {'paper': tree_manifest(PAPER), 'data': tree_manifest(DATA)}
        save(LOGS / 'integrity.json', {'frozen_source_matches': unchanged,
                                      'empty_initial_results': True,
                                      'submission_source_sha256': source_before,
                                      'input_bytes_unchanged': inputs_before == inputs_after})
        if not unchanged or inputs_before != inputs_after:
            raise IncompleteReplay('Source or trusted inputs changed during replay')
        protect_tree(SUBMISSION / 'results')
        evidence = SUBMISSION / 'results/horlbeck_gi_reproduction'
        if not evidence.is_dir():
            raise IncompleteReplay('Replay generated no declared scientific evidence')
        outputs_before = tree_manifest(evidence)
        save(LOGS / 'evidence_manifest_before.json', outputs_before)
        archive_tree(evidence, LOGS / 'candidate_outputs/results/horlbeck_gi_reproduction', outputs_before)
        stage = 'numeric_assessment'
        numeric = run_numeric(verifier)
        if numeric.get('status') != 'numeric_scored' or tree_manifest(evidence) != outputs_before:
            raise RuntimeError('Incomplete numeric assessment or changed evidence')
        stage = 'external_assessment'
        from grader import evaluate
        if evaluate():
            raise RuntimeError('External assessment was withheld; inspect verifier receipts')
        return 0
    except Exception as error:
        kind = ('submission' if isinstance(error, IncompleteReplay)
                else 'candidate_contract' if isinstance(error, EvidenceContractError) else 'infra')
        withhold(LOGS, stage, error, kind)
        print(f'{stage}: score withheld ({type(error).__name__}); see verifier receipts', file=sys.stderr)
        return 1
    finally:
        stop_solver(solver)
        restore_log_access(log_owner, log_mode, solver, verifier)


if __name__ == '__main__':
    sys.exit(main())
