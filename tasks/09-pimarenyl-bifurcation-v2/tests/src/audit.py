import argparse
import json
from pathlib import Path

import numpy as np

from evidence import EvidenceMissing, Evidence, EvidenceError, checksum, native_rks_frames, native_text_comparison, trusted_replay
from numerics import condition_statistics, finite, trajectory_checks


ROOT = Path(__file__).resolve().parents[1]


def chemistry(evidence, run_root):
    inputs = json.loads((run_root / 'inputs/initial_states.json').read_text())
    runs, problems, reported_mismatches = {}, [], []
    missing = object()
    submitted_summary = None
    summary_error = None
    try:
        submitted_summary = evidence.json('scientific_summary.json')
        if not isinstance(submitted_summary, dict) or not submitted_summary:
            raise ValueError('Expected a nonempty scientific summary object')
    except (EvidenceError, OSError, ValueError, TypeError) as error:
        submitted_summary = None
        reported_mismatches.append('scientific_summary.json: missing_or_invalid')
        summary_error = {'type': type(error).__name__, 'message': str(error)}

    def reported(*keys):
        value = submitted_summary
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return missing
            value = value[key]
        return value

    def compare(value, expected, location, tolerance):
        try:
            if expected is None or isinstance(expected, str):
                matches = value == expected
            else:
                expected = np.asarray(expected)
                actual = finite(value, expected.shape)
                matches = np.allclose(actual, expected, atol=tolerance, rtol=0)
        except (ValueError, TypeError, OverflowError):
            matches = False
        if not matches:
            reported_mismatches.append(location)

    for specification in inputs['runs']:
        identifier = specification['run_id']
        relative = f'trajectories/{identifier}.json'
        if not (evidence.root / relative).exists():
            problems.append({'run_id': identifier, 'kind': 'not_yet_available'})
            continue
        computed = {'complete': False, 'frame_count': 0, 'observations': []}
        try:
            record = evidence.json(relative)
            if record['run'] != specification:
                raise ValueError(f'Changed experiment identity: {identifier}')
            finite([frame['time_fs'] for frame in record['frames']])
            initial = inputs['states'][specification['state_id']]
            checked = trajectory_checks(record, initial, inputs['structures'][initial['structure_id']], inputs['constants'])
            json.dumps(checked, allow_nan=False, default=json_scalar)
            computed = checked
            native = native_rks_frames(evidence.path(f'native/{identifier}.log').read_text())
            if len(native) < computed['frame_count']:
                raise ValueError(f'Missing native frame receipts: {identifier}')
            energy_errors, gradient_errors, precision_checks = [], [], []
            diagnostic_errors = {'gradient_rms_hartree_per_bohr': [], 'kinetic_energy_hartree': []}
            for index, frame in enumerate(record['frames']):
                receipt = native[index]
                if receipt['step'] != index or receipt['run_id'] != identifier:
                    raise ValueError('Native receipt identity does not match frame')
                energy_errors.append(float(finite(abs(float(finite(receipt['energy_hartree'], ())) - frame['energy_hartree']), ())))
                gradient_errors.append(float(finite(np.max(abs(finite(receipt['gradient_hartree_per_bohr'], (53, 3)) - frame['gradient_hartree_per_bohr'])), ())))
                precision = {'step': index}
                for field, precision_field in (
                        ('energy_hartree', 'energy_rounding_half_unit_hartree'),
                        ('gradient_hartree_per_bohr', 'gradient_rounding_half_unit_hartree_per_bohr')):
                    precision[field] = native_text_comparison(receipt[field], frame[field], receipt[precision_field]) if precision_field in receipt else None
                precision_checks.append(precision)
                observation = computed['observations'][index]
                for field, target in (('gradient_rms_hartree_per_bohr', 'gradient_rms'), ('kinetic_energy_hartree', 'kinetic_hartree')):
                    try:
                        difference = float(finite(abs(float(finite(frame[field], ())) - observation[target]), ()))
                    except (KeyError, ValueError, TypeError, OverflowError):
                        difference = None
                        reported_mismatches.append(f'{identifier}/frames/{index}/{field}')
                    diagnostic_errors[field].append(difference)
            computed['reported_frame_diagnostics'] = {field: {
                'absolute_errors': errors,
                'max_absolute_error': max((value for value in errors if value is not None), default=None),
                'acceptance_tolerance': None, 'status': 'diagnostic_only_no_public_tolerance'}
                for field, errors in diagnostic_errors.items()}
            computed['native_energy_error_hartree'] = max(energy_errors, default=0)
            computed['native_gradient_error_hartree_per_bohr'] = max(gradient_errors, default=0)
            computed['native_text_diagnostic'] = {
                'energy_scale_hartree': 1e-6, 'gradient_scale_hartree_per_bohr': 6e-7,
                'within_consistency_scales': computed['native_energy_error_hartree'] <= 1e-6
                    and computed['native_gradient_error_hartree_per_bohr'] <= 6e-7,
                'used_for_validity_or_statistics': False}
            comparisons = [entry[field]['compatible'] if entry[field] is not None else None
                for entry in precision_checks for field in ('energy_hartree', 'gradient_hartree_per_bohr')]
            precision_consistent = False if False in comparisons else None if not comparisons or None in comparisons else True
            computed['native_text_precision_consistent'] = precision_consistent
            computed['native_text_precision_status'] = 'matched_printed_precision' if precision_consistent is True else 'incompatible_with_printed_precision' if precision_consistent is False else 'pending_review_missing_precision_fields'
            computed['native_text_precision_checks'] = precision_checks
            if precision_consistent is False:
                problems.append({'run_id': identifier, 'kind': 'native_text_precision_mismatch'})
            computed['state_and_integrator_consistent'] = bool(computed['frame_count'] and (
                computed['initial_coordinate_error_angstrom'] <= 1e-6 and computed['initial_velocity_within_public_tolerance']
                and computed['max_vv_coordinate_error_bohr'] <= 5e-8 and computed['max_vv_velocity_error_au'] <= 5e-8))
            if computed['frame_count'] and not computed['state_and_integrator_consistent']:
                problems.append({'run_id': identifier, 'kind': 'state_integrator_or_native_text_inconsistent'})
        except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            computed['state_and_integrator_consistent'] = False
            computed['error'] = {'type': type(error).__name__, 'message': str(error)}
            problems.append({'run_id': identifier,
                'kind': 'evidence_reader_failure' if isinstance(error, (EvidenceError, OSError)) else 'scientific_or_schema_issue',
                'error': computed['error']})
        computed['valid_complete'] = computed['complete'] and computed['state_and_integrator_consistent'] and computed.get('native_text_precision_consistent') is not False
        runs[identifier] = computed
    valid_runs = {identifier: result for identifier, result in runs.items()
        if result['state_and_integrator_consistent'] and result.get('native_text_precision_consistent') is not False}
    for specification in inputs['runs']:
        if specification['family'] != 'primary':
            continue
        identifier = specification['run_id']
        if not runs.get(identifier, {}).get('valid_complete', False):
            if reported('classifications', identifier) is not missing:
                reported_mismatches.append(f'classifications/{identifier}/no_valid_complete_primary')
            continue
        if submitted_summary is None:
            continue
        observation = runs[identifier]['observations'][-1]
        compare(reported('classifications', identifier, 'label'), observation['label'], f'classifications/{identifier}/label', 0)
        for name, distance in observation['distances_angstrom'].items():
            compare(reported('classifications', identifier, 'distances_angstrom', name), distance,
                f'classifications/{identifier}/distances_angstrom/{name}', 1e-6)
        margin = reported('classifications', identifier, 'commitment_margin_angstrom')
        if margin is not missing:
            compare(margin, observation['commitment_margin_angstrom'], f'classifications/{identifier}/commitment_margin_angstrom', 1e-6)
        boundaries = observation['boundary_distances_angstrom']
        active = ['reactant']
        if observation['label'] != 'reactant':
            active.append('transfer')
            if observation['label'] != 'incomplete':
                active.append('commitment')
        margins = reported('classifications', identifier, 'boundary_margins_angstrom')
        if margins is missing:
            margins = reported('classifications', identifier, 'boundary_distances_angstrom')
        if isinstance(margins, dict):
            for name in boundaries:
                if name in active or name in margins:
                    compare(margins.get(name, missing), boundaries[name], f'classifications/{identifier}/boundary/{name}', 1e-6)
        else:
            names = list(boundaries) if isinstance(margins, list) and len(margins) == 3 else active
            compare(margins, [boundaries[name] for name in names], f'classifications/{identifier}/boundary_margins_angstrom', 1e-6)
    statistics = {}
    for condition in ('tsre', 'tssi'):
        labels = [runs[f'{condition}-{index:02d}']['observations'][-1]['label'] for index in range(1, 5)
            if runs.get(f'{condition}-{index:02d}', {}).get('valid_complete', False)]
        statistics[condition] = condition_statistics(labels)
        if submitted_summary is not None:
            for field in ('completed', 'required'):
                compare(reported('statistics', condition, field), statistics[condition][field], f'{condition}/{field}', 0)
            for label, result in statistics[condition]['labels'].items():
                for name in ('count', 'fraction', 'wilson_95', 'full_sample_bounds'):
                    tolerance = 0 if name == 'count' else 1e-4 if name == 'wilson_95' else 1e-6
                    compare(reported('statistics', condition, 'labels', label, name), result[name], f'{condition}/{label}/{name}', tolerance)
    decomposition = {}
    for instant in (0, 10, 20, 40):
        groups = {}
        for condition in ('tsre', 'tssi'):
            starts, actual = [], []
            for index in range(1, 5):
                observations = valid_runs.get(f'{condition}-{index:02d}', {}).get('observations', [])
                selected = next((entry for entry in observations if entry['time_fs'] == instant), None)
                if selected:
                    starts.append(observations[0]['q_angstrom'])
                    actual.append(selected['q_angstrom'])
            if len(actual) == 4:
                initial_mean = np.mean(starts, axis=0)
                current_mean = np.mean(actual, axis=0)
                groups[condition] = {'initial': initial_mean, 'motion': current_mean - initial_mean, 'absolute': current_mean}
        if len(groups) == 2:
            entry = {name: (groups['tsre'][name] - groups['tssi'][name]).tolist() for name in ('initial', 'motion', 'absolute')}
            decomposition[str(instant)] = entry
            if submitted_summary is not None:
                for target, field in (('initial', 'initial_mean'), ('motion', 'change_mean'), ('absolute', 'current_mean')):
                    compare(reported('geometry_motion_decomposition', str(instant), 'TSre_minus_TSsi_' + field),
                        entry[target], f'decomposition/{instant}/{target}', 1e-6)
    interventions = {}
    for condition in ('tsre', 'tssi'):
        ids = [condition + suffix for suffix in ('-01', '-01-reversed', '-01-halfstep', '-01-reversed-halfstep')]
        for instant in (10, 20):
            values = [next((np.asarray(entry['q_angstrom']) for entry in valid_runs.get(identifier, {}).get('observations', []) if entry['time_fs'] == instant), None) for identifier in ids]
            entry = {}
            for target, field, first, second in (
                    ('primary_pair_effect', 'reversal_effect_angstrom', 0, 1),
                    ('halfstep_pair_effect', 'halfstep_effect_angstrom', 2, 3)):
                if values[first] is not None and values[second] is not None:
                    entry[target] = (values[second] - values[first]).tolist()
                    if submitted_summary is not None:
                        compare(reported('paired_momentum', condition, str(instant), field), entry[target],
                            f'paired_momentum/{condition}/{instant}/{field}', 1e-6)
            changes = [None if values[index] is None or values[index + 2] is None else (values[index + 2] - values[index]).tolist()
                for index in range(2)]
            if any(change is not None for change in changes):
                entry['individual_timestep_changes'] = changes
                submitted = reported('paired_momentum', condition, str(instant), 'individual_timestep_changes_angstrom')
                for index, change in enumerate(changes):
                    if change is not None and submitted_summary is not None:
                        value = submitted[index] if isinstance(submitted, list) and len(submitted) == 2 else missing
                        compare(value, change, f'paired_momentum/{condition}/{instant}/individual_timestep_changes_angstrom/{index}', 1e-6)
            if all(value is not None for value in values):
                entry['two_sided_sensitivity'] = (abs(values[2] - values[0]) + abs(values[3] - values[1])).tolist()
                entry['pair_timestep_change'] = ((values[3] - values[2]) - (values[1] - values[0])).tolist()
                if submitted_summary is not None:
                    compare(reported('paired_momentum', condition, str(instant), 'two_sided_sensitivity_angstrom'),
                        entry['two_sided_sensitivity'], f'paired_momentum/{condition}/{instant}/two_sided_sensitivity_angstrom', 1e-6)
                    difference = reported('paired_momentum', condition, str(instant), 'pair_timestep_change_angstrom')
                    if difference is not missing:
                        compare(difference, entry['pair_timestep_change'], f'paired_momentum/{condition}/{instant}/pair_timestep_change_angstrom', 1e-6)
            if entry:
                interventions[f'{condition}/{instant}'] = entry
    complete = sum(entry['complete'] for entry in runs.values())
    precisions = [entry.get('native_text_precision_consistent') for entry in runs.values()]
    precision_pending = not precisions or None in precisions
    text_and_vv_consistent = complete == 14 and all(entry.get('state_and_integrator_consistent', False) for entry in runs.values()) and False not in precisions
    return {'task_id': '09', 'runs': runs, 'complete_runs': complete, 'required_runs': 14,
        'valid_complete_runs': sum(entry['valid_complete'] for entry in runs.values()),
        'statistics': statistics, 'decomposition': decomposition, 'interventions': interventions,
        'reported_mismatches': reported_mismatches, 'missing': problems, 'summary_error': summary_error,
        'all_retained_native_text_and_vv_arrays_consistent': None if text_and_vv_consistent and precision_pending else text_and_vv_consistent,
        'statistics_native_precision_status': 'incompatible_cases_excluded' if False in precisions else 'pending_review_missing_precision_fields' if precision_pending else 'matched_retained_text',
        'native_calls_independently_attested': False,
        'diagnostic_limitations': ['Independent trajectory/state numerical envelopes', 'Decision-boundary margin audit', 'Scientific interpretation is not established by arithmetic checks', 'Arithmetic diagnostics do not assign rubric scores', 'Reported gradient RMS/kinetic-energy residual adjudication: no public acceptance tolerance']
            + (['Native RKS text precision unavailable for some retained cases'] if precision_pending else [])}


def json_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=('09',), required=True)
    parser.add_argument('--run-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-live-diagnostic', action='store_true')
    arguments = parser.parse_args()
    run_root = arguments.run_directory.resolve()
    output = arguments.output.resolve()
    if output.is_relative_to(run_root):
        raise ValueError('Audit output must not modify replay source or evidence')
    state = trusted_replay(run_root)
    if state['status'] == 'running' and not arguments.allow_live_diagnostic:
        raise RuntimeError('Refusing to score unfrozen running evidence; use diagnostic mode only')
    report = {'task_id': arguments.task, 'replay': state,
        'run_directory': str(run_root), 'trusted_replay_sha256': checksum(run_root / 'trusted_replay.json'),
        'status': 'scientific_diagnostic', 'scoring_dimensions': {'A': 10, 'B': 10, 'C': 80}}
    try:
        evidence = Evidence(run_root / 'outputs')
        report['scientific_checks'] = chemistry(evidence, run_root)
    except EvidenceMissing as error:
        report['status'] = 'candidate_evidence_incomplete'
        report['missing_evidence'] = str(error)
    except EvidenceError as error:
        report['status'] = 'evidence_reader_failure_not_scientific_zero'
        report['error'] = str(error)
    except (ValueError, KeyError, IndexError) as error:
        report['status'] = 'scientific_or_schema_issue_requires_triage'
        report['error'] = {'type': type(error).__name__, 'message': str(error)}
    serialized = json.dumps(report, indent=2, allow_nan=False, default=json_scalar) + '\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        stream.write(serialized)
    print(json.dumps({'output': str(output), 'status': report['status']}))


if __name__ == '__main__':
    main()
