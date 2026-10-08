import asyncio
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

from harbor.environments.docker.docker import (
    DockerEnvironment,
    _sanitize_docker_compose_project_name,
)
from harbor.models.verifier.result import VerifierResult
from harbor.utils.env import resolve_env_vars
from harbor.verifier.verifier import Verifier

from scripts.native_replay import docker_inspect, export_submission, save_json


class NativeReplayVerifier(Verifier):
    def _compose_project_name(self):
        return _sanitize_docker_compose_project_name(self.environment.session_id)

    @staticmethod
    def _docker_ids(arguments):
        completed = subprocess.run(
            ['docker', *arguments], check=False, capture_output=True, text=True, timeout=60)
        lines = [line.strip() for line in (completed.stdout or '').splitlines() if line.strip()]
        return [line for line in lines if re.fullmatch(r'[0-9a-f]{64}', line)], completed

    async def _resolve_main_container(self, logs):
        """Locate the single `main` service container, tolerating noisy compose output.

        The authoritative lookup is compose's own project-scoped `ps`; some
        compose versions prepend warnings to stdout or report nothing even when
        the container exists, so labelled Docker lookups are used as fallbacks.
        Every attempt is recorded so a genuine mismatch stays diagnosable.
        """
        attempts = []
        container_id = None
        try:
            response = await self.environment._run_docker_compose_command(['ps', '--all', '--quiet', 'main'])
            stdout = response.stdout or ''
            attempts.append({'method': 'compose_ps_main', 'return_code': response.return_code,
                             'stdout': stdout[:8192]})
            if re.fullmatch(r'[0-9a-f]{64}', stdout.strip()):
                container_id = stdout.strip()
        except Exception as error:  # noqa: BLE001 - recorded for diagnosis, then fallbacks run
            attempts.append({'method': 'compose_ps_main', 'error': repr(error)[:2048]})
        project = self._compose_project_name()
        if container_id is None:
            for method, arguments in (
                ('label_project_service', ['ps', '-a', '--no-trunc',
                    '--filter', 'label=com.docker.compose.project=' + project,
                    '--filter', 'label=com.docker.compose.service=main',
                    '--format', '{{.ID}}']),
                ('name_prefix', ['ps', '-a', '--no-trunc',
                    '--filter', 'name=' + project + '-main-',
                    '--format', '{{.ID}}']),
            ):
                identifiers, completed = self._docker_ids(arguments)
                attempts.append({'method': method, 'return_code': completed.returncode,
                                 'stdout': (completed.stdout or '')[:8192],
                                 'stderr': (completed.stderr or '')[:2048]})
                if len(identifiers) == 1:
                    container_id = identifiers[0]
                    break
        save_json(logs / 'container_lookup.json',
                  {'compose_project': project, 'resolved': container_id, 'attempts': attempts})
        if container_id is None:
            raise RuntimeError('Cannot identify the solving container unambiguously')
        return container_id

    async def verify(self):
        task = self.task.paths.tests_dir.parent
        if self.task.config.metadata.get('verifier_backend') != 'host_native_replay':
            return await super().verify()
        if not isinstance(self.environment, DockerEnvironment):
            raise RuntimeError('Native replay requires a local Docker environment')
        logs = self.trial_paths.verifier_dir.resolve()
        logs.mkdir(parents=True, exist_ok=True)
        if any((logs / name).exists() for name in ('native_replay', 'source_submission', 'result.json', 'reward.txt')):
            raise FileExistsError('Use a new trial rather than overwriting frozen replay evidence')
        process = None
        try:
            container_id = await self._resolve_main_container(logs)
            inspection = await asyncio.to_thread(docker_inspect, container_id)
            image_id = inspection['Image']
            devices = [device for request in (inspection['HostConfig'].get('DeviceRequests') or [])
                for device in (request.get('DeviceIDs') or [])]
            if task.name.startswith('09-') and len(devices) != 1:
                raise RuntimeError('Task09 requires one explicitly assigned GPU for native replay')
            await self.environment.stop_service('main')
            source = logs / 'source_submission'
            await asyncio.to_thread(export_submission, container_id, source)
            save_json(logs / 'solving_container.json', {'Id': inspection['Id'], 'Image': image_id,
                'gpu_devices': devices, 'container_stopped_before_export': True})
            configured = {**self.task.config.verifier.env,
                **(self.verifier_env or {}), **self.override_env}
            merged = resolve_env_vars({key: value for key, value in configured.items()
                if key in ('JUDGE_API_KEY', 'JUDGE_BASE_URL', 'JUDGE_MODEL', 'JUDGE_TRANSPORT', 'PBX_LLM_TRANSPORT')})
            environment = {key: value for key, value in os.environ.items()
                if not any(marker in key.upper() for marker in ('API_KEY', 'AUTH_TOKEN', 'ACCESS_TOKEN'))}
            environment.update({key: value for key, value in merged.items() if key.startswith('JUDGE_')})
            environment.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                JUDGE_TRANSPORT=merged.get('PBX_LLM_TRANSPORT', merged.get('JUDGE_TRANSPORT', 'openai')))
            command = [sys.executable, '-B', str(task / 'tests/evaluate.py'),
                '--submission', str(source), '--image-id', image_id, '--output', str(logs)]
            if task.name.startswith('09-'):
                command += ['--gpu', devices[0]]
            with self.trial_paths.test_stdout_path.open('xb') as output:
                process = await asyncio.create_subprocess_exec(*command, env=environment,
                    stdout=output, stderr=asyncio.subprocess.STDOUT, start_new_session=True)
                code = await process.wait()
            if code:
                raise RuntimeError('Native verifier did not publish a score; inspect verifier/result.json and stage logs')
            result = json.loads((logs / 'result.json').read_text())
            reward = result.get('reward')
            if result.get('status') != 'scored' or type(reward) not in (int, float) or not math.isfinite(reward) or not 0 <= reward <= 1:
                raise RuntimeError('The native verifier did not return a complete valid score')
            if float((logs / 'reward.txt').read_text()) != reward:
                raise RuntimeError('Published reward differs from the complete scientific score')
            return VerifierResult(rewards={'reward': reward})
        except BaseException as error:
            if process is not None and process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 90)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
            (logs / 'reward.txt').unlink(missing_ok=True)
            if not (logs / 'result.json').exists():
                save_json(logs / 'result.json', {'status': 'verifier_error', 'reward': None,
                    'error_type': type(error).__name__, 'reason': str(error)})
            raise
