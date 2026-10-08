import argparse
import json
from pathlib import Path

import numpy as np

from evidence import EvidenceMissing, Evidence, EvidenceError, checksum, trusted_replay
from numerics import center_component, finite, invariant_residuals, lorentz_epsilon


ROOT = Path(__file__).resolve().parents[1]


def photonics(evidence):
    runs, unresolved = {}, []
    for group in ('baseline', 'grid', 'time', 'control'):
        for side in ('left', 'right'):
            identifier = group + '_' + side
            relative = f'results/native/{identifier}/raw.npz'
            try:
                raw = evidence.observation(f'native/{identifier}', relative, axis='wavelength_um')
            except EvidenceMissing:
                continue
            try:
                wavelength = finite(raw['wavelength_um'], (301,))
                if not np.allclose(wavelength, np.linspace(1.520, 1.580, 301), rtol=0, atol=1e-12):
                    raise ValueError('Changed native workband axis')
                transmission = finite(raw['device_outgoing'])[:, 0] / finite(raw['reference_outgoing'])[:, 0]
                reflection = (finite(raw['device_incoming'])[:, 0] - finite(raw['reference_incoming'])[:, 0]) / raw['reference_incoming'][:, 0]
                exterior_distance = abs(float(finite(raw['input_z_um'], ()))) - float(finite(raw['slab_length_um'], ())) / 2
                reflection = finite(reflection * np.exp(-4j * np.pi * (1 / wavelength) * exterior_distance), (301,))
                flux_reflection = finite(-finite(raw['device_flux_in'], (301,)) / finite(raw['reference_flux_in'], (301,)), (301,))
                flux_transmission = finite(finite(raw['device_flux_out'], (301,)) / finite(raw['reference_flux_out'], (301,)), (301,))
                target = lorentz_epsilon(raw['profile_position_um'], raw['profile_frequency'], int(raw['gain_sign']))
                index_error = np.sqrt(finite(raw['actual_epsilon'])) - np.sqrt(target)
                center = 150
                runs[identifier] = {'raw': raw, 't': transmission, 'r': reflection, 'R': flux_reflection, 'T': flux_transmission,
                    'material_real_error': float(np.max(abs(index_error.real)) / 0.001),
                    'material_imaginary_error': float(np.max(abs(index_error.imag)) / 0.001),
                    'reported_t_error': float(np.max(abs(transmission - raw['t']))),
                    'reported_r_error': float(np.max(abs(reflection - finite(raw['r'], (301,))))),
                    'reported_R_error': float(np.max(abs(flux_reflection - finite(raw['R'], (301,))))),
                    'reported_T_error': float(np.max(abs(flux_transmission - finite(raw['T'], (301,))))),
                    'reflection_deembedding_distance_um': exterior_distance,
                    'native_power_R_error': float(np.max(abs(abs(reflection) ** 2 - raw['R']))),
                    'native_power_T_error': float(np.max(abs(abs(transmission) ** 2 - raw['T']))),
                    'center_R': float(abs(reflection[center]) ** 2), 'center_T': float(abs(transmission[center]) ** 2),
                    'band': center_component(wavelength, np.column_stack((abs(reflection) ** 2 / 0.01, abs(transmission - 1) / 0.05)), 1.550)}
            except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
                unresolved.append({'run_id': identifier,
                    'kind': 'evidence_reader_failure' if isinstance(error, (EvidenceError, OSError)) else 'scientific_or_schema_issue',
                    'error': {'type': type(error).__name__, 'message': str(error)}})
    comparisons = {}
    for group in ('baseline', 'grid', 'time', 'control'):
        if all(group + '_' + side in runs for side in ('left', 'right')):
            comparisons[group + '_reciprocity'] = float(np.max(abs(runs[group + '_left']['t'] - runs[group + '_right']['t'])))
    for group in ('grid', 'time'):
        if all(prefix + '_' + side in runs for prefix in ('baseline', group) for side in ('left', 'right')):
            comparisons[group + '_t_change'] = float(max(np.max(abs(runs[group + '_' + side]['t'] - runs['baseline_' + side]['t'])) for side in ('left', 'right')))
    reversal = {'cases': {}, 'missing_pairs': [], 'status': 'diagnostic_only', 'phase_rotation_fitted': False,
        'amplitude_gauge': 'r uses exp(-4j*pi*(1/wavelength)*(abs(input_z_um)-slab_length_um/2)); t uses matched outgoing fields',
        'power_definition': 'R=-device_flux_in/reference_flux_in; T=device_flux_out/reference_flux_out',
        'interpretation': 'Nonzero complex reversal differences are retained, not fitted away or required to vanish; nominal reference planes and finite-grid phase differences remain distinct from power reversal.'}
    for side, opposite in (('left', 'right'), ('right', 'left')):
        identifiers = {'control': 'control_' + side, 'baseline': 'baseline_' + opposite}
        if any(identifier not in runs for identifier in identifiers.values()):
            reversal['missing_pairs'].append(side)
            continue
        control, baseline = (runs[identifiers[name]] for name in ('control', 'baseline'))
        if not np.array_equal(control['raw']['wavelength_um'], baseline['raw']['wavelength_um']):
            reversal['cases'][side] = {'status': 'wavelength_axis_mismatch'}
            continue
        grid = runs.get('grid_' + opposite)
        if grid is not None:
            if np.array_equal(grid['raw']['wavelength_um'], baseline['raw']['wavelength_um']):
                identifiers['baseline_grid'] = 'grid_' + opposite
            else:
                grid = None
        entry = {'native_observations': {name: f'native/{identifier}' for name, identifier in identifiers.items()},
            'reference_planes_requested_um': {name: {
                'incoming': float(finite(runs[identifier]['raw']['input_z_um'], ())),
                'deembedding_exterior_distance': runs[identifier]['reflection_deembedding_distance_um']}
                for name, identifier in identifiers.items()},
            'opposite_material_and_direction': int(control['raw']['gain_sign']) == -int(baseline['raw']['gain_sign'])
                and int(control['raw']['direction']) == -int(baseline['raw']['direction'])}
        for name, identifier in identifiers.items():
            if 'output_z_um' in runs[identifier]['raw']:
                entry['reference_planes_requested_um'][name]['outgoing'] = float(finite(runs[identifier]['raw']['output_z_um'], ()))
        for quantity in ('r', 't', 'R', 'T'):
            difference = control[quantity] - baseline[quantity]
            entry[quantity + '_max_absolute_difference'] = float(np.max(abs(difference)))
            entry[quantity + '_design_point_difference'] = {'real': float(difference[150].real), 'imag': float(difference[150].imag)}
            if grid is not None:
                entry[quantity + '_opposite_baseline_grid_change_max'] = float(np.max(abs(grid[quantity] - baseline[quantity])))
        usable = (abs(control['r']) > 0) & (abs(baseline['r']) > 0)
        phase_difference = np.angle(control['r'][usable] * np.conj(baseline['r'][usable]))
        entry['reflection_phase_difference_max_rad'] = float(np.max(abs(phase_difference))) if np.any(usable) else None
        entry['undefined_phase_samples'] = int(np.sum(~usable))
        reversal['cases'][side] = entry
    report_path = 'results/native_reversal_comparison.json'
    reversal['reported_comparison_status'] = 'not_available'
    reversal['reported_errors'], reversal['reported_issues'] = {}, []
    try:
        submitted = evidence.record('native/reversal_comparison', report_path)
    except EvidenceMissing:
        submitted = None
    if submitted is not None:
        try:
            if not isinstance(submitted, dict) or not isinstance(submitted.get('cases'), dict):
                raise ValueError('Expected reversal report cases')
            reversal['reported_comparison_status'] = 'compared_diagnostic_only'
            for side, entry in reversal['cases'].items():
                candidate = submitted['cases'].get(side)
                errors = {}
                if not isinstance(candidate, dict):
                    reversal['reported_issues'].append(side + ': missing_or_invalid_case')
                    continue
                for field, expected in entry.items():
                    if not (field.endswith(('_max_absolute_difference', '_design_point_difference', '_opposite_baseline_grid_change_max'))
                            or field in ('reflection_phase_difference_max_rad', 'undefined_phase_samples')):
                        continue
                    try:
                        actual = candidate[field]
                        if isinstance(expected, dict):
                            errors[field] = {component: float(abs(float(finite(actual[component], ())) - value)) for component, value in expected.items()}
                        elif expected is None:
                            if actual is not None:
                                raise ValueError('Reported phase is defined at an undefined phase sample')
                            errors[field] = None
                        else:
                            errors[field] = float(abs(float(finite(actual, ())) - expected))
                    except (KeyError, ValueError, TypeError, OverflowError):
                        reversal['reported_issues'].append(f'{side}/{field}: missing_or_invalid')
                reversal['reported_errors'][side] = errors
        except (EvidenceError, OSError, ValueError, TypeError) as error:
            reversal['reported_comparison_status'] = 'reader_or_schema_issue'
            reversal['reported_issues'].append(str(error))
    nonlinear = {}
    for imaginary, side in ((imaginary, side) for imaginary in (0.3, 0.5, 0.8) for side in ('left', 'right')):
        label = f'n2_{str(imaginary).replace(".", "p")}_{side}'
        relative = f'results/paper/nonlinear/{label}'
        try:
            raw = evidence.observation(f'nonlinear/{label}/continuation', relative + '/continuation.npz', axis='output_intensity')
            roots = evidence.observation(f'nonlinear/{label}/roots', relative + '/matched_input_roots.csv', table=True)
        except EvidenceMissing:
            continue
        gain = imaginary / 2
        residuals = invariant_residuals(raw['stokes'], 0.25, gain)
        selected = {str(level): roots[np.isclose(roots[:, 0], level, atol=1e-10, rtol=0)].tolist() for level in (0.2, 0.8, 1.6, 3.2)}
        nonlinear[label] = {'max_invariant_residual': float(np.max(residuals)),
            'fixed_section_roots': selected, 'output_domain_violations': int(np.sum(roots[:, 2] ** 2 > 16 + 1e-8)),
            'max_input_residual': float(np.max(abs(roots[:, 5])))}
    for entry in runs.values():
        del entry['raw'], entry['t'], entry['r'], entry['R'], entry['T']
    return {'task_id': '05', 'native_runs': runs, 'comparisons': comparisons, 'nonlinear': nonlinear,
        'native_reversal_comparison': reversal,
        'complete_native_cases': len(runs), 'required_native_cases': 8,
        'unresolved_native_cases': unresolved,
        'diagnostic_limitations': ['Independent P/C phase and delay envelopes', 'Nonlinear branch coverage and boundary audit', 'Native time-tail/stationarity adjudication', 'Scientific interpretation is not established by arithmetic checks', 'Arithmetic diagnostics do not assign rubric scores']}


def json_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=('05',), required=True)
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
        report['scientific_checks'] = photonics(evidence)
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
