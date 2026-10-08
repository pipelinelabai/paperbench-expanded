import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib
import uuid

from scripts.native_replay import execute_container, inventory, isolated_command, mount, replay, save_json


def stage(command, log, seconds, deadline):
    timeout = min(seconds, deadline - time.monotonic())
    if timeout <= 0:
        raise TimeoutError('The public verifier time budget is exhausted')
    environment = {**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    with log.open('xb') as output:
        process = subprocess.Popen(command, env=environment, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()


def independent_force_probe(task, native, output, image_id, gpu, deadline):
    root = output / 'independent_forces'
    root.mkdir()
    uid, gid = (os.getuid(), os.getgid()) if os.getuid() else (65534, 65534)
    if os.getuid() == 0:
        os.chown(root, uid, gid)
    name = 'pbx-force-probe-' + uuid.uuid4().hex[:16]
    command = isolated_command(name, image_id, uid, gid, gpu)
    for source, target, readonly in ((task / 'tests/src/force_probe09.py', '/probe.py', True),
            (native / 'outputs', '/evidence', True), (native / 'inputs', '/inputs', True),
            (native / 'trusted_replay.json', '/trusted_replay.json', True), (root, '/probe-output', False)):
        command += ['--mount', mount(source, target, readonly)]
    seconds = min(1800, int(deadline - time.monotonic() - 300))
    if seconds <= 0:
        raise TimeoutError('No time remains for independent force verification')
    command += ['--env', 'OMP_NUM_THREADS=8', '--env', 'OPENBLAS_NUM_THREADS=1',
        '--entrypoint', '/bin/bash', image_id, '-c',
        f'exec timeout --signal=TERM --kill-after=30 {seconds} python3 /probe.py --evidence /evidence '
        '--inputs /inputs/initial_states.json --replay-record /trusted_replay.json --output /probe-output/results']
    try:
        execute_container(command, name, output / 'independent_reference.log', seconds)
    finally:
        subprocess.run(['docker', 'rm', '--force', name], capture_output=True, timeout=60)
    return root / 'results/summary.json'


def evaluate(task, arguments):
    started = time.monotonic()
    config = tomllib.loads((task / 'task.toml').read_text())
    settings = json.loads((task / 'tests/config/evaluation.json').read_text())['runtime']
    if not config['metadata']['harbor_scoring_enabled'] or not settings['harbor_scoring_enabled']:
        raise RuntimeError('This frozen package does not enable native Harbor scoring')
    if arguments.output.is_symlink():
        raise ValueError('Verifier output must not be a symlink')
    output = arguments.output.resolve()
    submission = arguments.submission.resolve()
    if (output.is_relative_to(submission) or submission.is_relative_to(task)
            or output.is_relative_to(task) or task.is_relative_to(output)):
        raise ValueError('Verifier output and candidate source must be outside the task package')
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in ('reward.txt', 'result.json', 'native_replay', 'review')):
        raise FileExistsError('A fresh verifier output directory is required')
    deadline = started + config['verifier']['timeout_sec'] - 120
    source = task / 'tests/src'
    state = {'task_id': settings['task_id'], 'status': 'preflight', 'reward': None}
    try:
        if os.environ.get('JUDGE_TRANSPORT') != 'openai':
            raise ValueError('The native scientific judge currently requires JUDGE_TRANSPORT=openai')
        if not all(os.environ.get(key) for key in ('JUDGE_API_KEY', 'JUDGE_BASE_URL', 'JUDGE_MODEL')):
            raise ValueError('Independent judge configuration is incomplete')
        import numpy
        import scipy
        import h5py
        state['verifier_versions'] = {'numpy': numpy.__version__, 'scipy': scipy.__version__, 'h5py': h5py.__version__}
        state['task_files_sha256'] = inventory(task)
        state['status'] = 'native_replay'
        save_json(output / 'state.json', state)
        native = output / 'native_replay'
        receipt = replay(task, submission, native, arguments.image_id, settings['native_timeout_sec'], arguments.gpu)
        state.update(native_exit_code=receipt['exit_code'], native_wall_seconds=receipt['wall_seconds'])
        sys.path.insert(0, str(source))
        from evidence import trusted_replay
        verified = trusted_replay(native)
        if verified['status'] not in ('integrity_verified', 'failed_prefix_integrity_verified'):
            raise RuntimeError('Native replay evidence failed its independent integrity checks')
        review = output / 'review'
        review.mkdir()
        state['status'] = 'independent_reference'
        save_json(output / 'state.json', state)
        reference = None
        if settings['task_id'] == '05':
            code = stage([sys.executable, '-B', str(source / 'reference05.py'), '--candidate-output', str(native / 'outputs'),
                '--output', str(review / 'independent_stokes')], review / 'independent_reference.log', 1920, deadline)
            state['independent_reference_exit_code'] = code
            if code:
                raise RuntimeError('Independent reference failed; inspect review/independent_reference.log')
            reference = review / 'independent_stokes/summary.json'
            if not reference.is_file():
                raise RuntimeError('Independent reference did not produce its summary; inspect review/independent_reference.log')
            summary = json.loads(reference.read_text())
            if (not isinstance(summary, dict) or summary.get('task_id') != '05'
                    or not isinstance(summary.get('cases'), dict)
                    or not isinstance(summary.get('candidate_artifacts'), dict)
                    or not isinstance(summary.get('linear'), dict)):
                raise RuntimeError('Independent reference returned an invalid summary')
        elif settings['task_id'] == '09':
            reference = independent_force_probe(task, native, review, arguments.image_id, arguments.gpu, deadline)
        state['status'] = 'scientific_audit'
        save_json(output / 'state.json', state)
        diagnostic = review / 'scientific_audit.json'
        code = stage([sys.executable, '-B', str(source / 'audit.py'), '--task', settings['task_id'],
            '--run-directory', str(native), '--output', str(diagnostic)], review / 'scientific_audit.log', 1200, deadline)
        if code:
            raise RuntimeError('Scientific diagnostic failed; inspect review/scientific_audit.log')
        state['status'] = 'judging'
        save_json(output / 'state.json', state)
        command = [sys.executable, '-B', str(source / 'judge.py'), '--task', settings['task_id'],
            '--run-directory', str(native), '--diagnostic', str(diagnostic), '--output', str(review / 'judgment')]
        if reference is not None and reference.is_file() and json.loads(reference.read_text()).get('candidate_artifacts'):
            command += ['--independent-reference', str(reference)]
        code = stage(command, review / 'judge.log', 3600, deadline)
        grade_path = review / 'judgment/grading_result.json'
        if code or not grade_path.is_file():
            raise RuntimeError('Judge could not publish a complete scientific score; inspect review/judge.log and grading_result.json')
        grade = json.loads(grade_path.read_text())
        if grade['status'] != 'scored':
            raise RuntimeError('Incomplete judgments must not become a scientific zero')
        trusted_replay(native)
        if inventory(task) != state['task_files_sha256']:
            raise RuntimeError('Task or evaluator inputs changed during verification')
        state.update(status='scored', reward=grade['rubric_score']['reward'],
            dimension_points=grade['rubric_score']['dimension_points'],
            native_replay_complete=grade['native_replay_complete'],
            wall_seconds=time.monotonic() - started)
        save_json(output / 'result.json', state)
        save_json(output / 'state.json', state)
        (output / 'reward.txt').write_text(str(state['reward']) + '\n')
        return 0
    except BaseException as error:
        state.update(status='verifier_error', failed_stage=state['status'], reward=None,
            error_type=type(error).__name__, reason=str(error), wall_seconds=time.monotonic() - started)
        (output / 'reward.txt').unlink(missing_ok=True)
        save_json(output / 'result.json', state)
        save_json(output / 'state.json', state)
        return 1


def main(task):
    parser = argparse.ArgumentParser(description='Trusted host entrypoint for isolated Docker clean replay and scientific judging')
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--image-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--gpu')
    arguments = parser.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Verifier interrupted; native containers must be stopped')
    signal.signal(signal.SIGTERM, interrupted)
    return evaluate(task.resolve(), arguments)
