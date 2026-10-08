import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import shlex
import stat


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_path(root, relative):
    if not isinstance(relative, str) or not relative or '\x00' in relative or '\n' in relative:
        raise ValueError('Invalid source-input path')
    parsed = PurePosixPath(relative)
    if parsed.is_absolute() or '..' in parsed.parts or str(parsed) != relative:
        raise ValueError('Source-input paths must be normalized and relative')
    current = root
    for part in parsed.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('Source inputs cannot traverse symbolic links')
    if not current.is_file() or not stat.S_ISREG(current.stat().st_mode):
        raise ValueError('A reviewed source input is missing or nonregular')
    return current


def reviewed_inventory(source, inventory):
    source = Path(source).resolve()
    inventory = Path(inventory)
    if inventory.is_symlink() or not inventory.is_file() or inventory.resolve().is_relative_to(source):
        raise ValueError('Input inventory must be verifier-owned and outside the candidate submission')
    metadata = inventory.stat()
    if metadata.st_uid != os.geteuid() or metadata.st_mode & 0o022 or metadata.st_size > 2 * 1024 * 1024:
        raise ValueError('Input inventory is writable by an untrusted account or exceeds the size budget')
    document = json.loads(inventory.read_text())
    if document.get('schema_version') != 1 or document.get('review_status') != 'approved_source_inputs':
        raise ValueError('Source inventory has not been approved by the evaluator')
    inputs = document.get('inputs')
    if not isinstance(inputs, list) or not 1 <= len(inputs) <= 10000:
        raise ValueError('A bounded, complete source input list is required')
    paths = [entry.get('path') for entry in inputs if isinstance(entry, dict)]
    if len(paths) != len(inputs) or not all(isinstance(path, str) for path in paths) or len(set(paths)) != len(paths):
        raise ValueError('Invalid or duplicate source inputs')
    command = document.get('replay_command')
    if command is None:
        if 'reproduce.sh' not in paths:
            raise ValueError('The default replay entry point is missing from the source inventory')
    elif not isinstance(command, list) or not 1 <= len(command) <= 32 or not all(
        isinstance(argument, str) and argument and '\x00' not in argument and '\n' not in argument and len(argument) <= 8192
        for argument in command
    ):
        raise ValueError('A reviewed alternate replay command must be a bounded argument vector')
    for entry in inputs:
        checksum = entry.get('sha256')
        if not isinstance(checksum, str) or len(checksum) != 64 or any(character not in '0123456789abcdef' for character in checksum):
            raise ValueError('Every reviewed input needs its frozen SHA256')
        source_path(source, entry['path'])
    return document


def snapshot(source, destination, inventory):
    source = Path(source).resolve()
    destination = Path(destination).absolute()
    if destination.is_symlink() or destination.resolve().is_relative_to(source) or source.is_relative_to(destination.resolve()):
        raise ValueError('Snapshot destination must be separate from the candidate tree')
    document = reviewed_inventory(source, inventory)
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError('Refusing to overwrite a nonempty source snapshot')
    checked = []
    for entry in document['inputs']:
        path = source_path(source, entry['path'])
        if digest(path) != entry['sha256']:
            raise ValueError('Frozen source differs from the evaluator-reviewed inventory')
        checked.append((path, entry['path']))
    destination.mkdir(parents=True, exist_ok=True)
    for path, relative in checked:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return {'status': 'source_only_snapshot_created', 'inventory_sha256': digest(Path(inventory)),
            'input_count': len(checked), 'policy': 'Only evaluator-reviewed inputs copied; all other paths, regardless of name/format, excluded.'}


def fingerprint(source, inventory):
    source = Path(source).resolve()
    document = reviewed_inventory(source, inventory)
    return {entry['path']: digest(source_path(source, entry['path']))
            for entry in sorted(document['inputs'], key=lambda entry: entry['path'])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['snapshot', 'fingerprint', 'shell-command'])
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    if args.operation == 'snapshot':
        if args.destination is None:
            parser.error('snapshot requires --destination')
        result = snapshot(args.source, args.destination, args.inventory)
    elif args.operation == 'fingerprint':
        result = fingerprint(args.source, args.inventory)
    else:
        document = reviewed_inventory(args.source, args.inventory)
        print('exec ' + shlex.join(document.get('replay_command', ['bash', '/home/submission/reproduce.sh'])))
        return
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
