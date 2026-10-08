import shlex
from pathlib import Path, PurePosixPath

import yaml


def audit_task(task):
    task = Path(task)
    environment = task / 'environment'
    errors = []
    copied = []
    text = (environment / 'Dockerfile').read_text().replace('\\\n', ' ')
    for line in text.splitlines():
        if not line.startswith(('COPY ', 'ADD ')):
            continue
        tokens = shlex.split(line)
        if any(token.startswith('--from=') for token in tokens):
            continue
        arguments = [token for token in tokens[1:] if not token.startswith('--')]
        destination = arguments[-1]
        for source in arguments[:-1]:
            if source.startswith(('https://', 'http://')):
                continue
            paths = list(environment.glob(source))
            if not paths or not all(path.exists() for path in paths):
                errors.append(f'{task.name}: missing Docker COPY source {source}')
            copied.append((source, destination))
    compose = yaml.safe_load((environment / 'docker-compose.yaml').read_text())
    main = compose['services']['main']
    if main['build']['context'] != '${CONTEXT_DIR}':
        errors.append(f'{task.name}: build context must use Harbor CONTEXT_DIR')
    mounts = main.get('volumes', [])
    expected = (
        '${HOST_VERIFIER_LOGS_PATH}:${ENV_VERIFIER_LOGS_PATH}',
        '${HOST_AGENT_LOGS_PATH}:${ENV_AGENT_LOGS_PATH}',
    )
    for mount in expected:
        if mount not in mounts:
            errors.append(f'{task.name}: missing mount {mount}')
    if task.name == '10-haastrup-2018-mos2-bands':
        workspace_mount = 'submission_workspace:/home/submission'
        if mounts.count(workspace_mount) != 1:
            errors.append(f'{task.name}: workspace must use one project-local Docker volume')
        if compose.get('volumes', {}).get('submission_workspace') != {'driver': 'local'}:
            errors.append(f'{task.name}: workspace volume must be local, isolated and non-external')
        for mount in mounts:
            if mount == workspace_mount:
                continue
            if isinstance(mount, dict):
                target = mount.get('target', '')
            else:
                parts = mount.split(':')
                target = parts[1] if len(parts) > 1 else parts[0]
            target = PurePosixPath(target)
            workspace = PurePosixPath('/home/submission')
            if target == workspace or target in workspace.parents or workspace in target.parents:
                errors.append(f'{task.name}: extra mount overlaps the local workspace')
    elif '${HOST_AGENT_LOGS_PATH}/submission:/home/submission' not in mounts:
        errors.append(f'{task.name}: missing mount ${{HOST_AGENT_LOGS_PATH}}/submission:/home/submission')
    if any('/tests' in str(mount) or '/refs' in str(mount) for mount in mounts):
        errors.append(f'{task.name}: private verifier inputs must not be mounted during the agent phase')
    if 'pbx-init-workspace' not in ' '.join(main.get('command', [])):
        errors.append(f'{task.name}: writable workspace initialization is missing')
    for name in ('paper.md', 'paper.pdf', 'paper_image', 'addendum.md'):
        if not any(source == 'paper/' or destination.rstrip('/') == '/home/paper/' + name
                   for source, destination in copied):
            errors.append(f'{task.name}: public paper input is not copied: {name}')
    return errors
