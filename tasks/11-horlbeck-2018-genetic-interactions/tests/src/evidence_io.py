from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat


def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def load(path):
    return json.loads(Path(path).read_text())


def tree_manifest(root, exclude_results=False):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Expected a regular directory: ' + str(root))
    manifest = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if exclude_results and relative.parts[0] == 'results':
            continue
        metadata = path.lstat()
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError('Linked or special evidence is not supported: ' + str(relative))
        manifest[relative.as_posix()] = digest(path)
    return manifest


def withhold(logs, stage, error, kind='infra'):
    record = {'status': 'score_withheld', 'stage': stage, 'kind': kind,
              'error_type': type(error).__name__, 'reason': str(error), 'reward': None}
    for name in ('failure.json', 'score_withheld.json'):
        if not (logs / name).exists():
            save(logs / name, record)
    if not (logs / 'publication.json').exists():
        save(logs / 'publication.json', {'eligible_for_ranking': False, 'ranking_score': None,
                                        'reason': 'No complete, trusted assessment'})
