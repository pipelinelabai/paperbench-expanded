import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys

import numpy as np

from meep_evidence_formats import NumericEvidence, canonical_unit, convert_units


MAX_BINDINGS = 32
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_RESULT_BYTES = 128 * 1024
BINDING_REVISION = 'swg-array-bindings-v2'

from source_citations import CITATION_SCHEMA, source_citation

BINDING_SCHEMA = {
    'type': 'object',
    'properties': {
        'path': {'type': 'string'}, 'array': {'type': 'string'},
        'source_unit': {'type': 'string'}, 'target_unit': {'type': 'string'},
        'unit_evidence': CITATION_SCHEMA, 'imaginary_array': {'type': 'string'},
        'complex_evidence': CITATION_SCHEMA,
        'selection': {
            'type': 'array', 'minItems': 1, 'maxItems': 16,
            'items': {'anyOf': [{'type': 'null'}, {'type': 'integer', 'minimum': 0}]},
            'description': 'One entry per stored axis. Exactly one null retains that entire sample axis; nonnegative integers select documented port/direction/component axes. No sample slicing, reordering, averaging or flattening.',
        },
        'selection_evidence': CITATION_SCHEMA,
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
              'binding_revision': BINDING_REVISION,
              'binding_schema': BINDING_SCHEMA,
              'binding_structure': 'bindings directly maps each required quantity name to one binding object. Do not add a quantities wrapper. unit_evidence is an object containing path and quote, or metadata_key, never a prose string.',
              'array_selection': 'Keep array equal to the exact stored dataset key. For multidimensional coefficients use selection plus selection_evidence citing the documented axis order, port identity and direction. Retain the entire native sample axis using exactly one null. Apply the same selection to split real/imaginary arrays. Never put Python indexing expressions in array.',
              'solver_units': 'Meep flux/power and explicitly declared Meep arbitrary source units are consistent flux, not watts or dimensionless ratios. Cite the actual metadata or source declaration; the original units and normalization remain in the binding record. Undeclared a.u. is ambiguous. Ratios still require the same per-arm incident/transmitted source convention.',
              'policy': 'Bind actual candidate arrays and cite their declared units. No guessed phase, variant, normalization or units.'}
    encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
    if len(encoded.encode()) > MAX_RESULT_BYTES:
        raise ValueError('Scientific metric description exceeds the tool budget')
    return result


def verify_citation(tools, evidence, citation):
    if not isinstance(citation, dict):
        raise ValueError('Evidence citation must contain path/quote, path/line_start/line_end, or an exact metadata_key')
    if citation.get('metadata_key'):
        key = citation['metadata_key']
        if key not in evidence.metadata or not str(evidence.metadata[key]).strip():
            raise ValueError('Citation must identify existing nonempty numeric metadata')
        return {'metadata_key': key, 'quote': str(evidence.metadata[key])}
    if not citation.get('path'):
        raise ValueError('Source citation must identify a candidate path')
    path = candidate_path(tools, citation['path'])
    if not path.is_file():
        raise ValueError(f'Unit source is not a regular candidate file: {citation["path"]}')
    if path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError('Unit citation file exceeds the inspection budget; select a smaller explicit source')
    text = path.read_text(encoding='utf-8-sig', errors='strict')
    locator = source_citation(citation, text)
    return {'path': str(path), 'sha256': file_digest(path), **locator}


def verify_unit_evidence(tools, evidence, binding):
    locator = verify_citation(tools, evidence, binding.get('unit_evidence'))
    if 'metadata_key' in locator:
        if canonical_unit(locator['quote']) != canonical_unit(binding['source_unit']):
            raise ValueError('Declared source unit does not match the cited numeric metadata')
        locator['unit'] = binding['source_unit']
    return locator


def select_vector(tools, evidence, binding, values):
    selection = binding.get('selection')
    if selection is None:
        if 'selection' in binding or 'selection_evidence' in binding:
            raise ValueError('selection_evidence requires an explicit axis selection')
        return values, None
    if not isinstance(selection, list) or len(selection) != values.ndim or len(selection) > 16:
        raise ValueError('selection must contain one entry per stored array axis')
    if sum(index is None for index in selection) != 1:
        raise ValueError('selection must retain exactly one complete native sample axis with null')
    for axis, index in enumerate(selection):
        if index is not None and (type(index) is not int or index < 0 or index >= values.shape[axis]):
            raise ValueError('Only in-range nonnegative component indices are allowed; no sample slicing')
    locator = verify_citation(tools, evidence, binding.get('selection_evidence'))
    indices = tuple(slice(None) if index is None else index for index in selection)
    record = {'selection': selection, 'selection_evidence': locator,
              'stored_shape': list(values.shape), 'sample_axis': selection.index(None)}
    return values[indices], record


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
        selection_record = None
        with NumericEvidence(path) as evidence:
            values = np.asarray(evidence.get(binding['array']))
            if binding.get('imaginary_array'):
                imaginary = np.asarray(evidence.get(binding['imaginary_array']))
                if values.shape != imaginary.shape or np.iscomplexobj(values) or np.iscomplexobj(imaginary):
                    raise ValueError('Split real/imaginary components need identical shapes and real-valued arrays')
                complex_evidence = verify_unit_evidence(tools, evidence, {
                    'source_unit': 'real_plus_i_imag', 'unit_evidence': binding.get('complex_evidence')})
                values = values + 1j * imaginary
            values, selection_record = select_vector(tools, evidence, binding, values)
            try:
                unit_evidence = verify_unit_evidence(tools, evidence, binding)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise ValueError(f'Unit evidence for quantity {quantity!r}, array {binding["array"]!r}, source {binding.get("unit_evidence", {}).get("path")!r}: {exc}') from exc
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
        if selection_record is not None:
            records[quantity].update(selection_record)
    metrics = json_metric_value(module.derive_metrics(quantities, context))
    if not isinstance(metrics, dict):
        raise ValueError('Private metric module must return a mapping of scientific results')
    result = {'operation': operation, 'module_sha256': digest, 'metrics': metrics,
              'binding_revision': BINDING_REVISION,
              'bindings': records, 'context': context,
              'status': 'recomputed_from_candidate_arrays' if bindings else 'analytic_context_only'}
    encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
    if len(encoded.encode()) > MAX_RESULT_BYTES:
        raise ValueError('Scientific metric result exceeds the evaluator tool budget')
    return result
