import csv
import hashlib
import json
from pathlib import Path
import stat

import numpy as np


class EvidenceError(RuntimeError):
    pass


class EvidenceMissing(EvidenceError):
    pass


def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


class Evidence:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.artifacts = {}
        self.observation_artifacts = {}

    def observation(self, identifier, legacy=None, axis=None, table=False):
        manifest_path = self.root / 'evidence_manifest.json'
        if manifest_path.is_file():
            manifest = self.json('evidence_manifest.json')
            if not isinstance(manifest, dict):
                raise EvidenceError('Manifest must be a JSON object')
            self.artifacts['evidence_manifest.json'] = checksum(self.path('evidence_manifest.json'))
            observations = manifest.get('observations')
            if not isinstance(observations, dict):
                raise EvidenceError('Manifest observations must be a logical-ID mapping')
            if identifier not in observations:
                raise EvidenceMissing(f'Observation unavailable: {identifier}')
            entries = observations[identifier]
            entries = entries if isinstance(entries, list) else [entries]
        elif legacy is not None:
            entries = [{'path': legacy}]
        else:
            raise EvidenceMissing(f'Observation unavailable: {identifier}')
        parts = []
        static_columns = set()
        dependencies = {}
        if manifest_path.is_file():
            dependencies['evidence_manifest.json'] = self.artifacts['evidence_manifest.json']
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
                raise EvidenceError(f'Invalid observation entry: {identifier}')
            relative = entry['path']
            actual = checksum(self.path(relative))
            if manifest_path.is_file() and entry.get('sha256') != actual:
                raise EvidenceError(f'Observation checksum mismatch: {identifier}: {relative}')
            self.artifacts[relative] = actual
            dependencies[relative] = actual
            columns = entry.get('columns', {})
            if not isinstance(columns, dict):
                raise EvidenceError('Observation columns must be a mapping')
            static = entry.get('static_columns', [])
            if not isinstance(static, list) or any(not isinstance(name, str) for name in static):
                raise EvidenceError('Static columns must be a list of array names')
            static_columns.update(static)
            if identifier.startswith('native/'):
                static_columns.update(('profile_position_um', 'profile_frequency', 'actual_epsilon'))
            raw = self.arrays(relative)
            if not isinstance(raw, dict):
                raise EvidenceError(f'Observation must contain named arrays: {identifier}')
            mapped = dict(raw) if not columns else {}
            for target, source in columns.items():
                try:
                    if isinstance(source, str):
                        mapped[target] = np.asarray(raw[source])
                    elif isinstance(source, dict) and set(source) == {'real', 'imag'}:
                        mapped[target] = np.asarray(raw[source['real']]) + 1j * np.asarray(raw[source['imag']])
                    else:
                        raise EvidenceError(f'Invalid column mapping: {identifier}/{target}')
                except (KeyError, TypeError, ValueError) as error:
                    raise EvidenceError(f'Cannot resolve column: {identifier}/{target}: {error}') from error
            parts.append({key: np.asarray(value) for key, value in mapped.items()})
        self.observation_artifacts[identifier] = dependencies
        if not parts:
            raise EvidenceError(f'Empty observation: {identifier}')
        if table:
            names = ('input_intensity', 'branch_id', 'output_amplitude', 'transmission', 'reflection', 'input_residual')
            tables = []
            branch_labels = {}
            for part in parts:
                if 'values' in part:
                    tables.append(part['values'])
                    continue
                if 'output_amplitude' not in part and 'output_intensity' in part:
                    if np.any(part['output_intensity'] < 0):
                        raise EvidenceError('Negative transmitted power in a root record')
                    part['output_amplitude'] = np.sqrt(part['output_intensity'])
                if not set(names) <= set(part):
                    if len(part) != 6 or manifest_path.is_file() and any(entry.get('columns') for entry in entries):
                        raise EvidenceError('Root records require six logical columns')
                    part = dict(zip(names, list(part.values())[:6]))
                labels = np.asarray(part['branch_id'])
                if labels.dtype.kind not in 'fiu':
                    labels = np.asarray([branch_labels.setdefault(str(label), len(branch_labels)) for label in labels])
                tables.append(np.column_stack([labels if name == 'branch_id' else part[name] for name in names]))
            return np.concatenate(tables).astype(float)
        if identifier.startswith('native/'):
            for part in parts:
                for name in ('device_outgoing', 'reference_outgoing', 'device_incoming', 'reference_incoming'):
                    if name in part and part[name].ndim == 1:
                        part[name] = part[name][:, None]
        if len(parts) == 1:
            result = parts[0]
            if axis is not None and axis in result:
                return self._merge_observation(parts, axis, static_columns)
            return result
        if axis is None:
            raise EvidenceError(f'Split observation requires a sample axis: {identifier}')
        return self._merge_observation(parts, axis, static_columns)

    def _merge_observation(self, parts, axis, static_columns):
        samples, constants = {}, {}
        keys = set(parts[0])
        if any(set(part) != keys for part in parts) or axis not in keys:
            raise EvidenceError('Split observations must retain identical named columns and an axis')
        for part in parts:
            coordinates = part[axis]
            if coordinates.ndim != 1 or not np.isfinite(coordinates).all():
                raise EvidenceError('Observation axis must be finite and one-dimensional')
            for name, values in part.items():
                if name == axis:
                    continue
                if name in static_columns or values.ndim == 0 or values.shape[0] != len(coordinates):
                    if name in constants and not np.array_equal(constants[name], values):
                        raise EvidenceError(f'Conflicting observation metadata: {name}')
                    constants[name] = values
            for index, coordinate in enumerate(coordinates):
                row = {name: values[index] for name, values in part.items() if name not in constants}
                coordinate = float(coordinate)
                if coordinate in samples and any(not np.array_equal(samples[coordinate][name], value, equal_nan=np.asarray(value).dtype.kind in 'fc') for name, value in row.items()):
                    raise EvidenceError('Conflicting duplicate scientific sample')
                samples[coordinate] = row
        if not samples:
            raise EvidenceError('Empty scientific sample axis')
        ordered = sorted(samples)
        return {**constants, **{name: np.asarray([samples[coordinate][name] for coordinate in ordered]) for name in samples[ordered[0]]}}

    def record(self, identifier, legacy=None):
        if (self.root / 'evidence_manifest.json').is_file():
            manifest = self.json('evidence_manifest.json')
            if not isinstance(manifest, dict):
                raise EvidenceError('Manifest must be a JSON object')
            self.artifacts['evidence_manifest.json'] = checksum(self.path('evidence_manifest.json'))
            observations = manifest.get('observations')
            if not isinstance(observations, dict):
                raise EvidenceError('Manifest observations must be a logical-ID mapping')
            entry = observations.get(identifier)
            if entry is None:
                raise EvidenceMissing(f'Observation unavailable: {identifier}')
            if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
                raise EvidenceError('JSON records require a single manifest entry')
            relative = entry['path']
            if entry.get('sha256') != checksum(self.path(relative)):
                raise EvidenceError(f'Observation checksum mismatch: {identifier}')
        elif legacy is not None:
            relative = legacy
        else:
            raise EvidenceMissing(f'Observation unavailable: {identifier}')
        self.artifacts[relative] = checksum(self.path(relative))
        self.observation_artifacts[identifier] = {relative: self.artifacts[relative]}
        if (self.root / 'evidence_manifest.json').is_file():
            self.observation_artifacts[identifier]['evidence_manifest.json'] = self.artifacts['evidence_manifest.json']
        return self.json(relative)

    def path(self, relative):
        relative = Path(relative)
        if relative.is_absolute() or '..' in relative.parts:
            raise EvidenceError('Evidence path escapes its root')
        location = self.root / relative
        if not location.resolve().is_relative_to(self.root):
            raise EvidenceError('Evidence symlink escapes its root')
        for ancestor in (location, *location.parents):
            if ancestor == self.root:
                break
            if ancestor.is_symlink():
                raise EvidenceError('Nonregular evidence path')
        try:
            regular = stat.S_ISREG(location.stat().st_mode)
        except FileNotFoundError as error:
            raise EvidenceMissing(f'Evidence unavailable: {relative}') from error
        except OSError as error:
            raise EvidenceError(f'Evidence inaccessible: {relative}: {type(error).__name__}') from error
        if not regular:
            raise EvidenceError(f'Nonregular evidence: {relative}')
        return location

    def json(self, relative):
        try:
            return json.loads(self.path(relative).read_text())
        except (OSError, ValueError) as error:
            raise EvidenceError(f'Cannot inspect JSON evidence: {relative}: {error}') from error

    def arrays(self, relative):
        location = self.path(relative)
        try:
            if location.suffix == '.npz':
                with np.load(location, allow_pickle=False) as archive:
                    return {key: archive[key] for key in archive.files}
            if location.suffix == '.npy':
                return {'values': np.load(location, allow_pickle=False)}
            if location.suffix == '.json':
                return self.json(relative)
            if location.suffix in ('.csv', '.tsv'):
                with location.open() as stream:
                    rows = list(csv.DictReader(stream, delimiter='\t' if location.suffix == '.tsv' else ','))
                if not rows:
                    raise ValueError('Empty table')
                columns = {}
                for key in rows[0]:
                    values = [row[key] for row in rows]
                    try:
                        columns[key] = np.asarray(values, dtype=float)
                    except (TypeError, ValueError):
                        columns[key] = np.asarray(values, dtype=str)
                return columns
            if location.suffix in ('.h5', '.hdf5'):
                import h5py
                arrays = {}
                with h5py.File(location, 'r') as archive:
                    def collect(name, item):
                        if isinstance(item, h5py.Dataset):
                            arrays[name] = item[()]
                    archive.visititems(collect)
                return arrays
            raise EvidenceError('Unsupported evidence representation; reader adaptation required')
        except (OSError, ValueError, ImportError) as error:
            raise EvidenceError(f'Cannot inspect numerical evidence: {relative}: {error}') from error


def trusted_replay(run_directory):
    root = Path(run_directory).resolve()
    record = json.loads((root / 'trusted_replay.json').read_text())
    if record['status'] == 'running':
        return {'status': 'running', 'completed': False, 'reason': 'Native replay is still in progress'}
    completed = record['status'] == 'native_completed' and record.get('exit_code') == 0
    if not record.get('source_inputs_after') or not (root / 'docker_inspect.json').is_file():
        return {'status': 'runner_record_incomplete', 'completed': False, 'reason': 'No complete host-side frozen replay inventory'}
    if not record.get('source_inputs_unchanged') or record['source_inputs_before'] != record['source_inputs_after']:
        raise EvidenceError('Source/input integrity failed')
    inspection = json.loads((root / 'docker_inspect.json').read_text())[0]
    host = inspection['HostConfig']
    container_state = inspection.get('State', {})
    if inspection.get('Image') != record.get('image_id') or not record.get('image_id'):
        raise EvidenceError('Native container image differs from the trusted replay identity')
    if container_state.get('Running') is not False or container_state.get('ExitCode') != record.get('exit_code'):
        raise EvidenceError('Native container completion differs from the trusted replay status')
    if record.get('container_state') != container_state:
        raise EvidenceError('Frozen container state differs from the trusted replay record')
    user = inspection['Config'].get('User', '').split(':', 1)[0]
    if host['NetworkMode'] != 'none' or not host['ReadonlyRootfs'] or user in ('', '0', 'root'):
        raise EvidenceError('Replay isolation is insufficient')
    for kind in ('source', 'inputs'):
        directory = root / kind
        if directory.is_symlink() or not directory.is_dir():
            raise EvidenceError(f'Nonregular frozen {kind} root')
        paths = list(directory.rglob('*'))
        if any(path.is_symlink() or not (path.is_dir() or path.is_file()) for path in paths):
            raise EvidenceError(f'Nonregular frozen {kind} path')
        files = {str(path.relative_to(directory)): checksum(path) for path in paths if path.is_file()}
        if files != record['source_inputs_before'][kind]:
            raise EvidenceError(f'Frozen {kind} changed after replay')
    if (root / 'outputs').is_symlink() or not (root / 'outputs').is_dir():
        raise EvidenceError('Nonregular frozen output root')
    evidence = Evidence(root / 'outputs')
    actual_outputs = set()
    for path in evidence.root.rglob('*'):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise EvidenceError('Nonregular frozen output')
        if path.is_file():
            actual_outputs.add(str(path.relative_to(evidence.root)))
    if actual_outputs != set(record['outputs_sha256']):
        raise EvidenceError('Frozen output inventory has missing or additional files')
    for relative, expected in record['outputs_sha256'].items():
        if checksum(evidence.path(relative)) != expected:
            raise EvidenceError('Frozen numerical evidence changed after replay')
    return {'status': 'integrity_verified' if completed else 'failed_prefix_integrity_verified', 'completed': completed, 'image_id': record['image_id'],
        'wall_seconds': record['wall_seconds'], 'native_output_files': len(record['outputs_sha256'])}
