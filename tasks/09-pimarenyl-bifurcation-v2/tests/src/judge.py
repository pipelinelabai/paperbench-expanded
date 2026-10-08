import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import sys
import time
import urllib.error
import urllib.request

import numpy as np

from evidence import Evidence, EvidenceError, EvidenceMissing, checksum, trusted_replay


ROOT = Path(__file__).resolve().parents[1]
from rubric_scoring import aggregate_scores, validate_scoring


def credentials(profile):
    names = ('JUDGE_API_KEY', 'JUDGE_BASE_URL', 'JUDGE_MODEL', 'JUDGE_TRANSPORT')
    configuration = {name: os.environ.get(name, '') for name in names} if profile is None else {}
    for line in profile.read_text().splitlines() if profile is not None else ():
        line = line.removeprefix('export ').strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        name, value = line.split('=', 1)
        if name not in ('JUDGE_API_KEY', 'JUDGE_BASE_URL', 'JUDGE_MODEL', 'JUDGE_TRANSPORT'):
            continue
        tokens = shlex.split(value)
        if len(tokens) != 1:
            raise ValueError('Invalid judge profile value')
        configuration[name] = tokens[0]
    if configuration.get('JUDGE_TRANSPORT') != 'openai' or not all(configuration.get(name) for name in ('JUDGE_API_KEY', 'JUDGE_BASE_URL', 'JUDGE_MODEL')):
        raise ValueError('Explicit compatible judge endpoint, model and credential required')
    return configuration


def json_ready(value):
    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return {'bytes_hex': value.hex()}
    if isinstance(value, complex):
        return {'real': value.real, 'imag': value.imag}
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return {'nonfinite': str(value)}
    return value


def public_contract(root, task):
    text = (root / 'config/public_contract.md').read_text()
    acceptance = root / 'config/acceptance.json'
    if acceptance.is_file():
        text += '\nPublic numerical acceptance policy:\n' + acceptance.read_text()
    return text, checksum(acceptance) if acceptance.is_file() else None


def validate_reference(task, path, run_directory):
    reference = json.loads(path.read_text())
    if reference.get('task_id') != task:
        raise EvidenceError('Independent reference belongs to a different task')
    if reference.get('trusted_replay_sha256') != checksum(run_directory / 'trusted_replay.json'):
        raise EvidenceError('Independent reference belongs to a different frozen replay')
    artifacts = reference.get('candidate_artifacts')
    if not isinstance(artifacts, dict) or not artifacts:
        raise EvidenceError('Independent reference lacks its candidate-evidence binding')
    evidence = Evidence(run_directory / 'outputs')
    for relative, expected in artifacts.items():
        if checksum(evidence.path(relative)) != expected:
            raise EvidenceError('Independent reference belongs to different or changed numerical evidence')
    if task == '09':
        required = {f'{identifier}/{step}' for identifier, step in [('tsre-01', 0), ('tssi-01', 0)]
            + [(identifier, 20) for identifier in ('tsre-01', 'tssi-01', 'tsre-01-reversed', 'tssi-01-reversed')]}
        available = set(reference.get('observations', {})) & required
        for observation in available:
            dependency = 'trajectories/' + observation.split('/')[0] + '.json'
            if dependency not in artifacts:
                raise EvidenceError('Independent force probe lacks its actual trajectory dependency')
        reference['missing_cases'] = sorted(required - available)
        if checksum(run_directory / 'inputs/initial_states.json') != reference.get('inputs_sha256'):
            raise EvidenceError('Independent force reference uses different initial inputs')
    return reference


def unavailable_reference_units(task, identifier, reference):
    if task == '09' and identifier in ('09.1b', '09.2a', '09.5a'):
        available = set((reference or {}).get('observations', {}))
        if identifier == '09.1b':
            return {} if {'tsre-01/0', 'tssi-01/0'} <= available else {'whole_requirement': 'Independent electronic-state probes unavailable'}
        blocked = {}
        for unit in unit_ids(task, identifier):
            condition = unit[:4]
            required = {condition + '-01/0', condition + '-01/20'} if identifier == '09.2a' else {condition + '-01/20', condition + '-01-reversed/20'}
            if not required <= available:
                blocked[unit] = 'Independent force reference unavailable for this condition'
        return blocked
    return {}


class ReadOnlyTools:
    def __init__(self, roots):
        self.roots = {name: Evidence(path) for name, path in roots.items()}
        self.inspected = set()
        self.reader_errors = []
        self.unresolved_reader_paths = set()
        self.discovered = {}
        self.discovery_totals = {}
        self.numerical_reads = set()
        self.numerical_contexts = {}

    def numerical_case_read(self, path, unit):
        if path not in self.numerical_reads:
            return False
        if unit == 'whole_requirement':
            return True
        aliases = (unit,)
        separators = ('.', '_') if unit.startswith(('tsre-', 'tssi-')) else ('.', '-', '_')
        for context in self.numerical_contexts.get(path, []):
            tokens = context['identities'] + list(Path(path).parts) + context['key'].split('/')
            for token in tokens:
                for alias in aliases:
                    if token == alias or any(token.startswith(alias + separator) for separator in separators):
                        return True
        return False

    def execute(self, arguments):
        root = arguments.get('root')
        if root not in self.roots:
            raise EvidenceError('Unknown evidence root')
        evidence = self.roots[root]
        operation = arguments['operation']
        relative = arguments.get('path', '')
        if operation == 'array':
            parts = Path(relative).parts
            for index, part in enumerate(parts[:-1]):
                if Path(part).suffix.lower() in ('.npz', '.npy', '.json', '.h5', '.hdf5', '.csv', '.tsv'):
                    embedded_key = '/'.join(parts[index + 1:])
                    if arguments.get('key') not in (None, embedded_key):
                        return {'argument_error': 'Specify the dataset once: use archive path plus key, or archive/dataset', 'canonical_archive': str(Path(*parts[:index + 1]))}
                    relative = str(Path(*parts[:index + 1]))
                    arguments.update(path=relative, key=embedded_key)
                    break
        offset = int(arguments.get('offset', 0))
        limit = min(int(arguments.get('limit', 10000)), 20000)
        if offset < 0 or limit < 1:
            raise EvidenceError('Invalid pagination')
        if operation == 'list':
            files = sorted(str(path.relative_to(evidence.root)) for path in evidence.root.rglob('*') if path.is_file())
            selected = files[offset:offset + min(limit, 300)]
            self.discovered.setdefault(root, set()).update(selected)
            self.discovery_totals[root] = len(files)
            return {'files': selected, 'total': len(files), 'next_offset': offset + len(selected) if offset + len(selected) < len(files) else None}
        path = evidence.path(relative)
        if operation == 'text':
            if path.suffix.lower() in ('.pdf', '.png', '.jpg', '.jpeg', '.npz', '.npy', '.h5', '.hdf5'):
                raise EvidenceError('Binary evidence requires an appropriate reader; use bundled paper.md for text')
            text = path.read_text()
            if offset >= len(text):
                raise EvidenceError('Text request returned no evidence; offset is beyond the available content')
            self.inspected.add(root + '/' + relative)
            return {'sha256': checksum(path), 'offset': offset, 'text': text[offset:offset + limit], 'total_chars': len(text),
                'next_offset': offset + limit if offset + limit < len(text) else None}
        if operation == 'array':
            arrays = evidence.arrays(relative)
            key = arguments.get('key')
            if key is None:
                return {'keys': list(arrays)}
            if key in arrays:
                selected = arrays[key]
            else:
                selected = arrays
                try:
                    for component in key.split('/'):
                        component = component.replace('~1', '/').replace('~0', '~')
                        selected = selected[int(component)] if isinstance(selected, list) else selected[component]
                except (KeyError, IndexError, TypeError, ValueError):
                    return {'argument_error': 'Requested array key does not exist; inspect available keys and use the corresponding evidence rather than infer scientific absence',
                        'available_keys': list(arrays), 'canonical_archive': relative, 'requested_key': key}
            array = np.asarray(selected)
            if offset >= array.size:
                raise EvidenceError('Array request returned no evidence; inspect valid indices or report an empty array explicitly')
            result = {'shape': list(array.shape), 'dtype': str(array.dtype), 'size': array.size, 'key': key,
                'samples': json_ready(array.reshape(-1)[offset:offset + min(limit, 1000)]), 'canonical_path': root + '/' + relative}
            if array.dtype.kind in 'fciu':
                self.numerical_reads.add(root + '/' + relative)
                identities = []
                metadata = arrays.get('run', arrays)
                if isinstance(metadata, dict):
                    for name in ('case_id', 'run_id', 'variant', 'condition', 'family'):
                        value = metadata.get(name)
                        if isinstance(value, np.ndarray) and value.ndim == 0:
                            value = value.item()
                        if isinstance(value, str):
                            identities.append(value)
                    case_ids = metadata.get('case_ids', metadata.get('case_id'))
                    if case_ids is not None and not isinstance(case_ids, str):
                        labels = np.asarray(case_ids)
                        if labels.ndim == 1 and array.ndim and len(labels) == array.shape[0]:
                            width = max(1, array.size // len(labels))
                            first, last = offset // width, min(len(labels), (offset + min(limit, 1000) + width - 1) // width)
                            identities.extend(str(label) for label in labels[first:last])
                self.numerical_contexts.setdefault(root + '/' + relative, []).append({'key': key, 'identities': identities})
                result['all_finite'] = bool(np.isfinite(array).all())
                if array.size:
                    result['absolute_min'] = float(np.min(abs(array)))
                    result['absolute_max'] = float(np.max(abs(array)))
            self.inspected.add(root + '/' + relative)
            return result
        raise EvidenceError('Only read-only list/text/array operations are available')


TOOLS = [{'type': 'function', 'function': {
    'name': 'inspect_evidence',
    'description': 'Read only frozen candidate source/inputs/results, original paper, or independently computed diagnostic report. Paginate listings/text fully before declaring evidence absent. No command or code execution.',
    'parameters': {'type': 'object', 'properties': {
        'root': {'type': 'string', 'enum': ['source', 'inputs', 'outputs', 'paper', 'diagnostic']},
        'operation': {'type': 'string', 'enum': ['list', 'text', 'array']},
        'path': {'type': 'string', 'description': 'Relative file path. For arrays prefer path="data.npz" with key="values"; data.npz/values is also accepted. Cite the canonical_path returned by the reader.'},
        'key': {'type': 'string', 'description': 'Array/dataset key. Omit to list keys. Nested JSON supports frames/0/coordinates_angstrom; escape a literal slash in a key as ~1.'},
        'offset': {'type': 'integer', 'minimum': 0}, 'limit': {'type': 'integer', 'minimum': 1, 'maximum': 20000}},
        'required': ['root', 'operation'], 'additionalProperties': False}}}]


def post(configuration, payload):
    endpoint = configuration['JUDGE_BASE_URL'].rstrip('/')
    if not endpoint.endswith('/chat/completions'):
        endpoint += '/chat/completions'
    body = json.dumps(payload).encode()
    request = urllib.request.Request(endpoint, body,
        {'Authorization': 'Bearer ' + configuration['JUDGE_API_KEY'], 'Content-Type': 'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (408, 429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f'Judge HTTP status {error.code}; credentials/response body suppressed') from None
        except (TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise RuntimeError('Judge transport unavailable; endpoint and credentials suppressed') from None
        time.sleep(4 * (attempt + 1))


def unit_ids(task, identifier):
    if task == '09':
        primary = [condition + f'-{index:02d}' for condition in ('tsre', 'tssi') for index in range(1, 5)]
        if identifier in ('09.2a', '09.2b', '09.2c', '09.3a', '09.3b', '09.7a'):
            return primary
        if identifier in ('09.5a', '09.5b', '09.5c', '09.6b', '09.8a', '09.8b', '09.9a'):
            return ['tsre', 'tssi']
        if identifier in ('09.6a', '09.6c'):
            return [condition + suffix for condition in ('tsre', 'tssi') for suffix in ('-01-halfstep', '-01-reversed-halfstep')]
    return ['whole_requirement']


def score_check(task, check, public_text, configuration, roots, output, blocked_units=None):
    toolset = ReadOnlyTools(roots)
    required_units = unit_ids(task, check['id'])
    blocked_units = blocked_units or {}
    units = required_units
    system = (ROOT / 'config/judge_prompt.md').read_text().rstrip('\n')
    prompt = public_text + '\n\nCURRENT CHECK\n' + json.dumps(check) + '\nUNITS\n' + json.dumps(units)
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]
    trace = []
    try:
        if not units:
            raise EvidenceError('Independent evidence dependency unavailable for all units of this check')
        for round_index in range(16):
            response = post(configuration, {'model': configuration['JUDGE_MODEL'], 'messages': messages, 'tools': TOOLS, 'max_tokens': 4096})
            message = response['choices'][0]['message']
            messages.append({key: message[key] for key in ('role', 'content', 'tool_calls') if key in message})
            trace.append({'round': round_index, 'message': message, 'usage': response.get('usage')})
            if message.get('tool_calls'):
                for call in message['tool_calls']:
                    arguments = {}
                    try:
                        if call['function']['name'] != 'inspect_evidence':
                            raise EvidenceError('Unrecognized tool')
                        arguments = json.loads(call['function']['arguments'])
                        result = toolset.execute(arguments)
                        if 'argument_error' in result:
                            toolset.reader_errors.append('argument_error: ' + result['argument_error'])
                            toolset.unresolved_reader_paths.add((arguments.get('root'), arguments.get('path')))
                        elif arguments.get('operation') in ('text', 'array') and 'keys' not in result:
                            toolset.unresolved_reader_paths.discard((arguments.get('root'), arguments.get('path')))
                    except EvidenceMissing as error:
                        result = {'missing_evidence': str(error)}
                    except (EvidenceError, OSError, ValueError, KeyError) as error:
                        result = {'reader_error': str(error)}
                        toolset.reader_errors.append(str(error))
                        toolset.unresolved_reader_paths.add((arguments.get('root'), arguments.get('path')))
                    messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': json.dumps(result, allow_nan=False)})
                    trace.append({'tool_call_id': call['id'], 'result': result})
                continue
            content = message.get('content') or ''
            if content.strip().startswith('```'):
                content = content.strip().split('\n', 1)[1].rsplit('```', 1)[0]
            judgment = json.loads(content)
            scores = judgment.get('unit_scores', {})
            if set(scores) != set(units) or any(type(score) is not int or score not in (0, 1) for score in scores.values()):
                raise ValueError('Judge returned invalid unit scores')
            if judgment.get('evidence_access') not in ('ok', 'missing', 'tool_error'):
                raise ValueError('Invalid evidence access status')
            if judgment['evidence_access'] == 'tool_error':
                raise EvidenceError('Judge could not inspect required evidence')
            if toolset.unresolved_reader_paths:
                raise EvidenceError('An actual reader failure remains unresolved; no scientific score is assigned')
            if judgment['evidence_access'] == 'missing' and ('outputs' not in toolset.discovery_totals
                    or len(toolset.discovered['outputs']) != toolset.discovery_totals['outputs']):
                raise EvidenceError('Evidence absence was asserted without complete output discovery')
            paths = judgment.get('evidence_paths', [])
            if not paths or not set(paths) <= toolset.inspected:
                messages.append({'role': 'user', 'content': 'Judgment validation failed: cited evidence was not actually inspected. Use the read-only tools, then cite their canonical_path values and return a supported judgment.'})
                trace.append({'validation_error': 'uninspected_citation'})
                continue
            if (any(scores.values()) or judgment['evidence_access'] != 'missing') and not any(path.startswith('outputs/') for path in paths):
                messages.append({'role': 'user', 'content': 'Judgment validation failed: only source or background material was cited. Inspect the retained candidate results that substantiate this criterion and cite those outputs; do not infer execution or results from source alone.'})
                trace.append({'validation_error': 'no_candidate_output_inspected'})
                continue
            unit_paths = judgment.get('unit_evidence_paths', {})
            unsupported_units = []
            for unit, score in scores.items():
                if score:
                    cited = unit_paths.get(unit, [])
                    if not cited or not set(cited) <= toolset.inspected or not any(toolset.numerical_case_read(path, unit) for path in cited):
                        unsupported_units.append(unit)
            if unsupported_units:
                messages.append({'role': 'user', 'content': 'Judgment validation failed: these positive units lack their own inspected numerical evidence: ' + json.dumps(unsupported_units)
                    + '. Inspect an actual array for each corresponding case (including a case-scoped dataset in a combined file), then return unit_evidence_paths for each. A listing, prose, metadata or another case is insufficient.'})
                trace.append({'validation_error': 'positive_case_numeric_evidence_missing', 'units': unsupported_units})
                continue
            blocked_units = {unit: reason for unit, reason in blocked_units.items() if scores[unit] > 0}
            inspected_score = sum(score for unit, score in scores.items() if unit not in blocked_units)
            result = {'check_id': check['id'], 'status': 'partially_judged' if blocked_units else 'judged',
                'score': None if blocked_units else sum(scores.values()) / len(units),
                'unit_scores': {unit: None if unit in blocked_units else scores[unit] for unit in required_units}, 'blocked_units': blocked_units,
                'score_bounds': [inspected_score / len(required_units), (inspected_score + len(blocked_units)) / len(required_units)],
                'judgment': judgment, 'inspected_paths': sorted(toolset.inspected), 'reader_errors': toolset.reader_errors,
                'unresolved_reader_paths': sorted(toolset.unresolved_reader_paths, key=repr)}
            break
        else:
            raise EvidenceError('Tool budget exhausted without a supported judgment')
    except Exception as error:
        result = {'check_id': check['id'], 'status': 'judge_error', 'score': None,
            'error': {'type': type(error).__name__, 'message': str(error)}, 'inspected_paths': sorted(toolset.inspected),
            'blocked_units': blocked_units, 'score_bounds': [0.0, 1.0],
            'reader_errors': toolset.reader_errors,
            'unresolved_reader_paths': sorted(toolset.unresolved_reader_paths, key=repr)}
    (output / (check['id'] + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    (output / (check['id'] + '.trace.json')).write_text(json.dumps(trace, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=('09',), required=True)
    parser.add_argument('--run-directory', required=True, type=Path)
    parser.add_argument('--diagnostic', required=True, type=Path)
    parser.add_argument('--profile', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--independent-reference', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    arguments = parser.parse_args()
    if not 1 <= arguments.workers <= 8:
        raise ValueError('Judge concurrency must be between 1 and 8')
    task = json.loads((ROOT / 'config/evaluation.json').read_text())['runtime']['task_id']
    if arguments.task != task:
        raise ValueError('Judge task does not match the packaged rubric')
    rubric_path = ROOT / 'config/evaluation.json'
    rubric = json.loads(rubric_path.read_text())['scoring_contract']
    validate_scoring(rubric)
    state = trusted_replay(arguments.run_directory)
    if state['status'] not in ('integrity_verified', 'failed_prefix_integrity_verified') and not arguments.dry_run:
        raise RuntimeError('Cannot grade an incomplete or integrity-invalid native replay')
    reference = None
    if arguments.independent_reference:
        reference = validate_reference(arguments.task, arguments.independent_reference, arguments.run_directory)
    configuration = credentials(arguments.profile)
    diagnostic = json.loads(arguments.diagnostic.read_text())
    if not arguments.dry_run:
        if diagnostic.get('task_id') != arguments.task or diagnostic.get('run_directory') != str(arguments.run_directory.resolve()):
            raise EvidenceError('Diagnostic report belongs to a different replay')
        if diagnostic.get('trusted_replay_sha256') != checksum(arguments.run_directory / 'trusted_replay.json'):
            raise EvidenceError('Diagnostic report is stale')
        if diagnostic.get('status') not in ('scientific_diagnostic', 'candidate_evidence_incomplete'):
            raise EvidenceError('Resolve scientific/schema/reader audit issues before judging')
    paper_root = ROOT.parent / 'environment/paper'
    if not paper_root.is_dir():
        paper_root = Path('/home/paper')
    if not paper_root.is_dir():
        raise FileNotFoundError('The task paper directory is unavailable')
    roots = {'source': arguments.run_directory / 'source', 'inputs': arguments.run_directory / 'inputs',
        'outputs': arguments.run_directory / 'outputs', 'paper': paper_root,
        'diagnostic': arguments.diagnostic.parent}
    output = arguments.output.resolve()
    if output.is_relative_to(arguments.run_directory.resolve()):
        raise ValueError('Judge output cannot be placed inside frozen replay evidence')
    output.mkdir(parents=True, exist_ok=False)
    diagnostic_root = output / 'diagnostic'
    diagnostic_root.mkdir()
    (diagnostic_root / 'independent_science.json').write_text(arguments.diagnostic.read_text())
    if arguments.independent_reference:
        shutil.copytree(arguments.independent_reference.parent, diagnostic_root / 'reference')
    roots['diagnostic'] = diagnostic_root
    public_text, acceptance_sha256 = public_contract(ROOT, task)
    checks = [check for block in rubric['blocks'] for check in block['checks']]
    fingerprint = {'evaluation_sha256': checksum(rubric_path),
        'rubric_sha256': checksum(ROOT / 'rubric.json'),
        'judge_prompt_sha256': checksum(ROOT / 'config/judge_prompt.md'), 'public_sha256': hashlib.sha256(public_text.encode()).hexdigest(),
        'acceptance_sha256': acceptance_sha256,
        'native_replay_sha256': checksum(arguments.run_directory / 'trusted_replay.json'), 'diagnostic_sha256': checksum(arguments.diagnostic),
        'judge_model': configuration['JUDGE_MODEL'], 'scientific_program_sha256': {path.name: checksum(path) for path in Path(__file__).parent.glob('*.py')},
        'scope': '10/10/80 scientific scoring from frozen replay evidence'}
    if arguments.independent_reference:
        fingerprint['independent_reference_sha256'] = checksum(arguments.independent_reference)
    (output / 'fingerprint.json').write_text(json.dumps(fingerprint, indent=2) + '\n')
    if arguments.dry_run:
        print(json.dumps({'status': 'prepared_not_judged', 'checks': len(checks), 'units': sum(len(unit_ids(arguments.task, check['id'])) for check in checks), 'model': configuration['JUDGE_MODEL']}))
        return 0
    results = {}
    with ThreadPoolExecutor(max_workers=arguments.workers) as executor:
        futures = [executor.submit(score_check, arguments.task, check, public_text, configuration, roots, output,
            unavailable_reference_units(arguments.task, check['id'], reference)) for check in checks]
        for future in as_completed(futures):
            result = future.result()
            results[result['check_id']] = result
            print(result['check_id'], result['status'], result['score'], flush=True)
    report = {'status': 'judge_errors' if any(result['status'] != 'judged' for result in results.values()) else 'scored',
        'check_results': results, 'scoring_dimensions': {'A': 10, 'B': 10, 'C': 80},
        'native_replay_complete': state['completed']}
    if report['status'] == 'scored':
        report['rubric_score'] = aggregate_scores(rubric, {identifier: result['score'] for identifier, result in results.items()})
    else:
        report['rubric_score_bounds_not_final_score'] = [aggregate_scores(rubric,
            {identifier: result['score_bounds'][bound] for identifier, result in results.items()}) for bound in (0, 1)]
    report['independent_reference_complete'] = bool(reference and reference.get('complete') and not reference.get('missing_cases'))
    (output / 'grading_result.json').write_text(json.dumps(report, indent=2) + '\n')
    return 1 if report['status'] == 'judge_errors' else 0


if __name__ == '__main__':
    raise SystemExit(main())
