import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time
import uuid


class SubmissionError(ValueError):
    pass


def save_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def inventory(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise SubmissionError('Expected a regular source/evidence directory')
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise SubmissionError('Nonregular source/evidence member: ' + str(path.relative_to(directory)))
        if path.is_file():
            hasher = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    hasher.update(chunk)
            result[path.relative_to(directory).as_posix()] = hasher.hexdigest()
    return result


def docker_inspect(identifier):
    completed = subprocess.run(['docker', 'inspect', identifier], check=True, capture_output=True, text=True, timeout=45)
    records = json.loads(completed.stdout)
    if len(records) != 1:
        raise RuntimeError('Expected exactly one Docker object')
    return records[0]


def extract_regular_archive(stream, destination, expected_root):
    with tarfile.open(fileobj=stream, mode='r|*') as archive:
        for member in archive:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] != expected_root:
                raise SubmissionError('Container archive escapes its expected source root')
            if not (member.isdir() or member.isfile()):
                raise SubmissionError('Links and special files are not valid immutable source/inputs')
            target = destination / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open('xb') as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            target.chmod(0o755 if member.mode & 0o111 else 0o644)


def export_submission(container_id, destination):
    if not re.fullmatch(r'[0-9a-f]{64}', container_id):
        raise ValueError('An inspected immutable container ID is required')
    inspection = docker_inspect(container_id)
    if inspection['State']['Running']:
        raise RuntimeError('Stop the solving container before exporting immutable source')
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    for name in ('reproduce.sh', 'src', 'inputs'):
        archive_path = destination / ('.' + name + '.tar')
        with archive_path.open('xb') as output:
            completed = subprocess.run(['docker', 'cp', container_id + ':/home/submission/' + name, '-'],
                stdout=output, stderr=subprocess.PIPE, timeout=300)
        if completed.returncode:
            archive_path.unlink()
            if name == 'inputs' and b'Could not find the file' in completed.stderr:
                continue
            raise SubmissionError('Cannot export required immutable submission member: ' + name)
        with archive_path.open('rb') as stream:
            extract_regular_archive(stream, destination, name)
        archive_path.unlink()
    inventory(destination)


def prepare_submission(submission, destination, task):
    inventory(submission)
    script = submission / 'reproduce.sh'
    if script.is_symlink() or not script.is_file():
        raise SubmissionError('A regular no-argument reproduce.sh is required')
    inventory(submission / 'src')
    source = destination / 'source'
    source.mkdir()
    shutil.copy2(script, source / 'reproduce.sh')
    shutil.copytree(submission / 'src', source / 'src', ignore=shutil.ignore_patterns('__pycache__'))
    inputs = destination / 'inputs'
    canonical = task / 'environment/starter_submission/inputs'
    if canonical.is_dir():
        inventory(canonical)
        shutil.copytree(canonical, inputs)
        for path in [inputs, *inputs.rglob('*')]:
            if path.is_dir():
                path.chmod(path.stat().st_mode | 0o700)
    elif task.name.startswith(('09-', '10-')):
        raise RuntimeError('The task package lacks its canonical scientific inputs')
    else:
        inputs.mkdir()
    supplied = submission / 'inputs'
    if supplied.exists() or supplied.is_symlink():
        for relative, digest in inventory(supplied).items():
            target = inputs / relative
            if target.exists():
                if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                    raise SubmissionError('Submission changes reserved public input: ' + relative)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(supplied / relative, target)
    return source, inputs


def mount(source, destination, readonly=True):
    source = str(source.resolve())
    if any(character in source for character in ',\r\n'):
        raise ValueError('Docker bind-mount paths cannot contain commas or line breaks')
    return f'type=bind,src={source},dst={destination}' + (',readonly' if readonly else '')


def isolated_command(name, image_id, uid, gid, gpu=None):
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', image_id) or uid == 0:
        raise ValueError('Native replay requires an immutable image and a non-root user')
    command = ['docker', 'run', '--name', name, '--network', 'none', '--read-only', '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges', '--user', f'{uid}:{gid}', '--cpus', '8',
        '--memory', '32g', '--memory-swap', '32g', '--pids-limit', '512',
        '--tmpfs', '/tmp:rw,nosuid,nodev,size=2g', '--shm-size', '1g',
        '--env', 'HOME=/tmp', '--env', 'PYTHONDONTWRITEBYTECODE=1']
    if gpu is not None:
        if not re.fullmatch(r'(?:\d+|GPU-[0-9a-fA-F-]+)', str(gpu)):
            raise ValueError('A single inspected GPU device is required')
        command += ['--gpus', 'device=' + str(gpu)]
    return command


def execute_container(command, name, log_path, budget):
    with log_path.open('xb') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            return process.wait(timeout=budget + 120)
        finally:
            subprocess.run(['docker', 'stop', '--time', '30', name], capture_output=True, timeout=60)
            if process.poll() is None:
                process.wait(timeout=60)


def export_outputs(container, destination):
    archive_path = destination.parent / '.native-outputs.tar'
    with archive_path.open('xb') as output:
        subprocess.run(['docker', 'cp', container + ':/home/submission/outputs', '-'],
            stdout=output, stderr=subprocess.PIPE, check=True, timeout=600)
    with archive_path.open('rb') as stream:
        extract_regular_archive(stream, destination.parent, 'outputs')
    archive_path.unlink()


def replay(task, submission, destination, image_id, budget, gpu=None):
    task_id = task.name[:2]
    if task_id not in {'05', '09', '10'} or (task_id == '09') != (gpu is not None):
        raise ValueError('GPU selection does not match the scientific task')
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    source, inputs = prepare_submission(submission, destination, task)
    outputs = destination / 'outputs'
    outputs.mkdir()
    uid, gid = (os.getuid(), os.getgid()) if os.getuid() else (65534, 65534)
    if os.getuid() == 0:
        os.chown(outputs, uid, gid)
    before = {'source': inventory(source), 'inputs': inventory(inputs)}
    name = 'pbx-native-' + task_id + '-' + uuid.uuid4().hex[:16]
    volume = name + '-outputs' if task_id == '10' else None
    if volume:
        subprocess.run(['docker', 'volume', 'create', '--label', 'paperbench-expanded.native-replay=' + name, volume],
            capture_output=True, check=True, timeout=45)
        subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
            '--cap-add', 'CHOWN', '--security-opt', 'no-new-privileges', '--user', '0:0',
            '--mount', f'type=volume,src={volume},dst=/outputs', '--entrypoint', '/bin/sh', image_id,
            '-ec', f'case "$(stat -f -c %T /outputs)" in nfs*|cifs|smb*) exit 70;; esac; chown {uid}:{gid} /outputs'],
            capture_output=True, check=True, timeout=90)
    command = isolated_command(name, image_id, uid, gid, gpu)
    for host, target, readonly in ((source / 'src', '/home/submission/src', True),
            (source / 'reproduce.sh', '/home/submission/reproduce.sh', True),
            (inputs, '/home/submission/inputs', True)):
        command += ['--mount', mount(host, target, readonly)]
    command += ['--mount', f'type=volume,src={volume},dst=/home/submission/outputs' if volume
                else mount(outputs, '/home/submission/outputs', False)]
    command += ['--workdir', '/home/submission', '--entrypoint', '/bin/bash', image_id,
        '-c', f'exec timeout --signal=TERM --kill-after=60 {int(budget)} bash reproduce.sh']
    record = {'task_id': task_id, 'status': 'running', 'container_name': name, 'image_id': image_id,
        'source_inputs_before': before, 'command': command, 'submission_kind': 'supplied_source',
        'runtime_origin': 'harbor_host_native', 'started_epoch': time.time(),
        'outputs_volume': volume,
        'budget_seconds': budget, 'evidence_scope': 'native_replay'}
    metadata = destination / 'trusted_replay.json'
    save_json(metadata, record)
    started = time.monotonic()
    try:
        record['exit_code'] = execute_container(command, name, destination / 'console.log', budget)
        inspection = docker_inspect(name)
        save_json(destination / 'docker_inspect.json', [inspection])
        record['container_state'] = inspection['State']
        if volume:
            export_outputs(name, outputs)
        record['source_inputs_after'] = {'source': inventory(source), 'inputs': inventory(inputs)}
        record['source_inputs_unchanged'] = before == record['source_inputs_after']
        record['outputs_sha256'] = inventory(outputs)
        record['status'] = ('native_completed' if record['exit_code'] == 0
            and record['source_inputs_unchanged'] else 'native_failed')
    except BaseException as error:
        record.update(status='runner_failed', error={'type': type(error).__name__, 'message': str(error)})
        raise
    finally:
        record['wall_seconds'] = time.monotonic() - started
        save_json(metadata, record)
        subprocess.run(['docker', 'rm', '--force', name], capture_output=True, timeout=60)
        if volume and 'outputs_sha256' in record:
            subprocess.run(['docker', 'volume', 'rm', volume], capture_output=True, timeout=60)
    return record
