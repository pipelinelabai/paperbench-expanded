from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

import yaml


def write_private(path, text):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as handle:
        handle.write(text)


def write_receipt(path, records):
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as handle:
        json.dump({'updated_at': datetime.now(timezone.utc).isoformat(), 'images': records}, handle, indent=2)
        handle.write('\n')
        temporary = handle.name
    os.replace(temporary, path)


def build_images(records, output, environ, network_overlay=None):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    build_env = dict(environ)
    for name in list(build_env):
        if any(marker in name for marker in ('API_KEY', 'AUTH_TOKEN', 'ACCESS_TOKEN')):
            build_env.pop(name)
    info = subprocess.run(['docker', 'info', '--format', '{{.DockerRootDir}}'],
                          env=build_env, capture_output=True, text=True, check=True, timeout=30)
    docker_root = Path(info.stdout.strip())
    if not docker_root.is_absolute() or not docker_root.is_dir():
        raise ValueError('Build requires a local Docker daemon with an accessible Docker data directory.')
    minimum_free = float(environ.get('PBX_BUILD_MIN_FREE_GIB') or '30')
    if not 0 < minimum_free < 100000:
        raise ValueError('PBX_BUILD_MIN_FREE_GIB must be a positive finite disk reserve.')
    receipt = output / 'images.json'
    results = []
    for record in records:
        if shutil.disk_usage(docker_root).free < minimum_free * 1024**3:
            raise ValueError('Docker storage is below the configured free-space reserve; no cleanup was attempted.')
        task = record['path']
        build_id = uuid.uuid4().hex
        image = f'paperbench-expanded-task{record["number"]}:{build_id[:16]}'
        directory = output / record['number']
        directory.mkdir(mode=0o700)
        overlay = directory / 'image.yaml'
        write_private(overlay, yaml.safe_dump({'services': {'main': {'image': image}}}))
        settings = dict(build_env)
        settings.update({
            'CONTEXT_DIR': str(task / 'environment'),
            'HOST_VERIFIER_LOGS_PATH': str(directory / 'verifier'),
            'ENV_VERIFIER_LOGS_PATH': '/logs/verifier',
            'HOST_AGENT_LOGS_PATH': str(directory / 'agent'),
            'ENV_AGENT_LOGS_PATH': '/logs/agent',
            'TEST_DIR': '/tests', 'NETWORK_MODE': 'bridge',
            'MEMORY': str(record['config']['environment']['memory_mb'] * 1024**2),
            'CPUS': str(record['config']['environment']['cpus']),
        })
        command = ['docker', 'compose', '--env-file', '/dev/null', '--progress', 'plain',
                   '-p', f'pbx-build-{record["number"]}-{build_id[:12]}',
                   '-f', str(overlay), '-f', str(task / 'environment/docker-compose.yaml')]
        if network_overlay is not None:
            network = directory / 'network.yaml'
            write_private(network, yaml.safe_dump(network_overlay, sort_keys=False))
            command.extend(['-f', str(network)])
        command.extend(['build', 'main'])
        result = {'task': record['name'], 'image': image, 'build_id': build_id,
                  'state': 'building', 'started_at': datetime.now(timezone.utc).isoformat(),
                  'log': str(directory / 'build.log')}
        results.append(result)
        write_receipt(receipt, results)
        print(f'Building {record["number"]}: {image}; log: {result["log"]}', flush=True)
        try:
            descriptor = os.open(result['log'], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, 'w') as log:
                completed = subprocess.run(command, env=settings, stdout=log, stderr=subprocess.STDOUT,
                                           timeout=record['config']['environment']['build_timeout_sec'])
            result['exit_code'] = completed.returncode
            if completed.returncode:
                raise ValueError(f'Task {record["number"]} image build failed; inspect its private build log.')
            inspect = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', image],
                                     env=settings, capture_output=True, text=True, check=True, timeout=30)
            result['image_id'] = inspect.stdout.strip()
            result['state'] = 'built'
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            result['state'] = 'failed'
            result['error_type'] = type(error).__name__
            raise
        finally:
            result['finished_at'] = datetime.now(timezone.utc).isoformat()
            write_receipt(receipt, results)
    print(f'Built {len(results)} image(s). No agent, API request or verifier was started. Receipt: {receipt}')
    return results
