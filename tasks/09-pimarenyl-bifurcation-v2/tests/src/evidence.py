import csv
import hashlib
import json
from pathlib import Path
import re
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


def native_rounding_half_unit(token):
    from decimal import Decimal

    value = Decimal(token)
    if not value.is_finite() or not np.isfinite(float(value)):
        raise ValueError('Nonfinite native numerical token')
    half_unit = float(Decimal('0.5').scaleb(value.as_tuple().exponent))
    return float(np.nextafter(half_unit, np.inf))


def native_text_comparison(printed, saved, half_unit):
    import math

    printed, saved, half_unit = (np.asarray(value, dtype=float) for value in (printed, saved, half_unit))
    if printed.shape != saved.shape or printed.shape != half_unit.shape:
        raise ValueError('Native precision arrays must have matching shapes')
    if not all(np.isfinite(value).all() for value in (printed, saved, half_unit)) or np.any(half_unit < 0):
        raise ValueError('Invalid native precision comparison')
    ulp = np.vectorize(math.ulp, otypes=[float])
    roundoff = 2 * (ulp(printed) + ulp(saved))
    allowed = np.nextafter(half_unit + roundoff, np.inf)
    errors = abs(printed - saved)
    if not np.isfinite(errors).all() or not np.isfinite(allowed).all():
        raise ValueError('Nonfinite native precision arithmetic')
    return {'compatible': bool(np.all(errors <= allowed)),
        'max_absolute_error': float(np.max(errors)), 'max_allowed_error': float(np.max(allowed)),
        'mismatched_indices': np.argwhere(errors > allowed).tolist(),
        'roundoff_rule': '2*(ulp(parsed_native)+ulp(saved)); half-unit and tolerance addition rounded upward'}


def native_rks_frames(text):
    records = []
    for match in re.finditer(r'PBX_FRAME_BEGIN run_id=(\S+) step=(\d+)\n(.*?)PBX_FRAME_END run_id=\1 step=\2\n', text, re.S):
        body = match.group(3)
        energy = re.findall(r'converged SCF energy\s*=\s*([-+\d.eE]+)', body)
        gradient_rows = re.findall(r'^\s*\d+\s+[A-Z][a-z]?\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s*$', body, re.M)
        if not energy or len(gradient_rows) < 53 or 'gpu4pyscf.dft.rks' not in body:
            raise ValueError('Frame lacks native RKS energy, class identity or gradient rows')
        records.append({'run_id': match.group(1), 'step': int(match.group(2)), 'energy_hartree': float(energy[-1]),
            'gradient_hartree_per_bohr': np.asarray(gradient_rows[-53:], dtype=float),
            'energy_rounding_half_unit_hartree': native_rounding_half_unit(energy[-1]),
            'gradient_rounding_half_unit_hartree_per_bohr': np.asarray([
                [native_rounding_half_unit(token) for token in row] for row in gradient_rows[-53:]])})
    return records


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
