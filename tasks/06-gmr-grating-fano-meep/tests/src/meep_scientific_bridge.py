import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys

import numpy as np

from meep_evidence_formats import NumericEvidence, convert_units


MAX_BINDINGS = 32
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_RESULT_BYTES = 128 * 1024

CITATION_SCHEMA = {
    'type': 'object',
    'properties': {'path': {'type': 'string'}, 'quote': {'type': 'string'}, 'metadata_key': {'type': 'string'}},
    'anyOf': [{'required': ['path', 'quote']}, {'required': ['metadata_key']}],
    'additionalProperties': False,
    'description': 'An object, never a string: either path plus an exact quote from inspected candidate text, or metadata_key naming an exact attribute in this numeric file.',
}
BINDING_SCHEMA = {
    'type': 'object',
    'properties': {
        'path': {'type': 'string'}, 'array': {'type': 'string'},
        'source_unit': {'type': 'string'}, 'target_unit': {'type': 'string'},
        'unit_evidence': CITATION_SCHEMA, 'imaginary_array': {'type': 'string'},
        'complex_evidence': CITATION_SCHEMA,
    },
    'required': ['path', 'array', 'source_unit', 'target_unit', 'unit_evidence'],
    'additionalProperties': False,
}


def file_digest(path):
    hasher = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def tree_digest(root):
    root = Path(root)
    if not root.exists():
        return None
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Fingerprint root must be a non-symlink directory')
    hasher = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            raise ValueError('Frozen evidence contains a link or nonregular filesystem object')
        if stat.S_ISREG(mode):
            row = [str(path.relative_to(root)), file_digest(path)]
            hasher.update(json.dumps(row, ensure_ascii=False, separators=(',', ':')).encode())
            hasher.update(b'\n')
    return hasher.hexdigest()


def candidate_path(tools, logical_path):
    path = tools.resolve(logical_path)
    root = tools.evidence_root.resolve()
    if not path.resolve().is_relative_to(root):
        raise ValueError('Scientific measurement bindings must come from candidate evidence, never private targets')
    relative = path.absolute().relative_to(root)
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Scientific bindings cannot traverse a symlink')
    return path


def load_metric_module(module_path):
    module_path = Path(module_path)
    if not module_path.is_file() or module_path.is_symlink():
        raise ValueError('This task has no reviewed scientific metric module yet')
    digest = file_digest(module_path)
    spec = importlib.util.spec_from_file_location('pbx_private_metrics_' + digest, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not callable(getattr(module, 'derive_metrics', None)) or not isinstance(getattr(module, 'METRIC_SPECS', None), dict):
        raise ValueError('Private metric module does not implement the reviewed interface')
    return module, digest


def describe_metrics(module_path):
    module, digest = load_metric_module(module_path)
    result = {'module_sha256': digest, 'operations': module.METRIC_SPECS,
              'binding_schema': BINDING_SCHEMA,
              'binding_structure': 'bindings directly maps each required quantity name to one binding object. Do not add a quantities wrapper. unit_evidence is an object containing path and quote, or metadata_key, never a prose string.',
              'policy': 'Bind actual candidate arrays and cite their declared units. No guessed phase, variant, normalization or units.'}
    encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
    if len(encoded.encode()) > MAX_RESULT_BYTES:
        raise ValueError('Scientific metric description exceeds the tool budget')
    return result


def verify_unit_evidence(tools, evidence, binding):
    citation = binding.get('unit_evidence')
    if not isinstance(citation, dict):
        raise ValueError('unit_evidence must be an object: {"path": "candidate text path", "quote": "exact inspected unit statement"}, or {"metadata_key": "exact numeric attribute key"}. A string is invalid; do not invent a quote.')
    if citation.get('metadata_key'):
        key = citation['metadata_key']
        if str(evidence.metadata.get(key, '')) != binding['source_unit']:
            raise ValueError('Declared source unit does not match the cited numeric metadata')
        return {'metadata_key': key, 'unit': binding['source_unit']}
    if not citation.get('path') or not citation.get('quote'):
        raise ValueError('Cite a report/source/header quote or numeric metadata for the unit mapping')
    path = candidate_path(tools, citation['path'])
    if path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError('Unit citation file exceeds the inspection budget; select a smaller explicit source')
    quote = str(citation['quote'])
    if len(quote) > 2048:
        raise ValueError('Unit citation is too long')
    text = path.read_text(encoding='utf-8', errors='strict')
    if ' '.join(quote.split()) not in ' '.join(text.split()):
        raise ValueError('Unit citation does not occur in the frozen candidate evidence')
    return {'path': str(path), 'sha256': file_digest(path), 'quote': quote}


def json_metric_value(value):
    if isinstance(value, np.ndarray):
        if value.size > 4096:
            raise ValueError('Metric module returned an array instead of bounded scientific summaries')
        return json_metric_value(value.tolist())
    if isinstance(value, np.generic):
        return json_metric_value(value.item())
    if isinstance(value, complex):
        return {'real': value.real, 'imag': value.imag}
    if isinstance(value, dict):
        return {str(key): json_metric_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_metric_value(item) for item in value]
    return value


def derive_metrics(tools, module_path, operation, bindings, context=None):
    module, digest = load_metric_module(module_path)
    if operation not in module.METRIC_SPECS:
        raise ValueError('Unknown metric operation; inspect the private metric specification first')
    if not isinstance(bindings, dict) or len(bindings) > MAX_BINDINGS:
        raise ValueError('A bounded, explicit quantity-to-dataset mapping is required')
    if not bindings and not module.METRIC_SPECS[operation].get('analytic_only', False):
        raise ValueError('Only explicitly analytic operations may run without candidate arrays')
    context = dict(context or {})
    if context.get('operation', operation) != operation:
        raise ValueError('Metric operation disagrees with the context')
    context['operation'] = operation
    if len(json.dumps(context, allow_nan=False).encode()) > 32768:
        raise ValueError('Metric context must not contain large fabricated result arrays')
    quantities = {}
    records = {}
    total_bytes = 0
    for quantity, binding in bindings.items():
        if not isinstance(binding, dict) or not all(binding.get(key) for key in ('path', 'array', 'source_unit', 'target_unit')):
            raise ValueError('Every binding needs exact path/dataset and declared source/target units')
        path = candidate_path(tools, binding['path'])
        complex_evidence = None
        with NumericEvidence(path) as evidence:
            values = np.asarray(evidence.get(binding['array']))
            if binding.get('imaginary_array'):
                imaginary = np.asarray(evidence.get(binding['imaginary_array']))
                if values.shape != imaginary.shape or np.iscomplexobj(values) or np.iscomplexobj(imaginary):
                    raise ValueError('Split real/imaginary components need identical shapes and real-valued arrays')
                complex_evidence = verify_unit_evidence(tools, evidence, {
                    'source_unit': 'real_plus_i_imag', 'unit_evidence': binding.get('complex_evidence')})
                values = values + 1j * imaginary
            unit_evidence = verify_unit_evidence(tools, evidence, binding)
        if binding['source_unit'] != binding['target_unit']:
            values = convert_units(values, binding['source_unit'], binding['target_unit'])
        total_bytes += values.nbytes
        if total_bytes > MAX_TOTAL_BYTES:
            raise ValueError('Combined scientific inputs exceed the evaluator budget')
        values.setflags(write=False)
        quantities[quantity] = values
        records[quantity] = {'path': str(path), 'sha256': file_digest(path), 'array': binding['array'],
                             'source_unit': binding['source_unit'], 'target_unit': binding['target_unit'],
                             'unit_evidence': unit_evidence, 'shape': list(values.shape), 'dtype': str(values.dtype)}
        if complex_evidence is not None:
            records[quantity].update(imaginary_array=binding['imaginary_array'], complex_evidence=complex_evidence,
                                     complex_convention='real_plus_i_imag')
    metrics = json_metric_value(module.derive_metrics(quantities, context))
    if not isinstance(metrics, dict):
        raise ValueError('Private metric module must return a mapping of scientific results')
    result = {'operation': operation, 'module_sha256': digest, 'metrics': metrics,
              'bindings': records, 'context': context,
              'status': 'recomputed_from_candidate_arrays' if bindings else 'analytic_context_only'}
    encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
    if len(encoded.encode()) > MAX_RESULT_BYTES:
        raise ValueError('Scientific metric result exceeds the evaluator tool budget')
    return result
