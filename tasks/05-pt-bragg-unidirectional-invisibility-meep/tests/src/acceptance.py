import json
from pathlib import Path

import numpy as np


POLICY = json.loads((Path(__file__).resolve().parents[1] / 'config/acceptance.json').read_text())['same_model']
AMPLITUDE_TOLERANCE = POLICY['complex_amplitude_normalized']
PHASE_TOLERANCE_RAD = POLICY['phase_absolute_rad']
DELAY_TOLERANCE = POLICY['delay_normalized']
NONLINEAR_TOLERANCE = POLICY['nonlinear_observable_normalized']
TURN_INPUT_TOLERANCE = POLICY['turn_input_absolute']
NEAR_ZERO_POWER_TOLERANCE = POLICY['near_zero_power_absolute']


def power_comparison(actual, reference):
    return bool(abs(actual - reference) <= max(0.05 * abs(reference), NEAR_ZERO_POWER_TOLERANCE))


def linear_comparison(reference, candidate):
    amplitudes = {}
    for name in ('t', 'r_left', 'r_right'):
        actual, expected = np.asarray(candidate[name]), np.asarray(reference[name])
        if actual.shape != expected.shape or not np.isfinite(actual).all():
            raise ValueError('Linear amplitudes must be finite with the required reporting shape')
        amplitudes[name] = float(np.max(abs(actual - expected) / np.maximum(1, abs(expected))))
    transmission = np.asarray(reference['t'])
    phase, delay = np.asarray(candidate['phase']), np.asarray(candidate['delay'])
    if phase.shape != transmission.shape or delay.shape != transmission.shape:
        raise ValueError('Phase and delay shapes differ from their reporting axis')
    defined = abs(transmission) > 0
    undefined_valid = bool(np.isnan(phase[~defined]).all() and np.isnan(delay[~defined]).all())
    defined_valid = bool(np.isfinite(phase[defined]).all() and np.isfinite(delay[defined]).all())
    phase_error = float(np.max(abs(phase[defined] - np.asarray(reference['phase'])[defined]))) if defined.any() and defined_valid else None
    delay_error = float(np.max(abs(delay[defined] - np.asarray(reference['delay'])[defined]) / (1 + abs(np.asarray(reference['delay'])[defined])))) if defined.any() and defined_valid else None
    phase_consistency = float(np.max(abs(np.exp(1j * phase[defined]) - candidate['t'][defined] / abs(candidate['t'][defined])))) if defined.any() and defined_valid and np.all(abs(candidate['t'][defined]) > 0) else None
    return {'scaled_amplitude_errors': amplitudes, 'amplitudes_pass': all(value <= AMPLITUDE_TOLERANCE for value in amplitudes.values()),
        'phase_max_error_rad': phase_error, 'delay_max_normalized_error': delay_error,
        'phase_complex_t_consistency': phase_consistency, 'undefined_phase_samples': int((~defined).sum()),
        'phase_pass': undefined_valid and defined_valid and phase_error is not None and phase_error <= PHASE_TOLERANCE_RAD and phase_consistency is not None and phase_consistency <= PHASE_TOLERANCE_RAD,
        'delay_pass': undefined_valid and defined_valid and delay_error is not None and delay_error <= DELAY_TOLERANCE}


def bounded_interval_contains(interval, reference, maximum_width, uncertainty=0.):
    if interval is None:
        return False
    values = np.asarray(interval, dtype=float)
    if values.shape != (2,) or not np.isfinite(values).all() or values[0] > values[1]:
        return False
    if values[1] - values[0] > maximum_width or not 0 <= uncertainty <= maximum_width:
        return False
    return bool(values[0] - uncertainty <= reference <= values[1] + uncertainty)


def root_set_comparison(reference_roots, candidate_rows, target, evaluate):
    rows = np.asarray(candidate_rows, dtype=float)
    if rows.ndim != 2 or rows.shape[1] < 6 or not np.isfinite(rows).all():
        raise ValueError('Root records require six finite numeric columns')
    references = sorted(reference_roots, key=lambda root: root['output_power'])
    ordered = rows[np.argsort(rows[:, 2] ** 2, kind='stable')]
    result = {'count_matches': len(references) == len(ordered), 'matched_roots': [], 'passes': False}
    if not result['count_matches']:
        return result
    for reference, row in zip(references, ordered):
        power = float(row[2] ** 2)
        measured = evaluate(power)
        transmission = power / target
        reflection = measured['reflected_power'] / target
        residual = abs(measured['input_power'] - target) / (1 + abs(target))
        transmission_error = abs(transmission - reference['T']) / (1 + abs(reference['T']))
        reflection_error = abs(reflection - reference['R']) / (1 + abs(reference['R']))
        lower, upper = reference['output_bracket']
        in_segment = lower <= power <= upper
        if not in_segment:
            nearest = min((lower, upper), key=lambda endpoint: abs(endpoint - power))
            in_segment = abs(power - nearest) / (target + abs(reference['output_power'])) <= NONLINEAR_TOLERANCE and abs(evaluate(nearest)['input_power'] - target) / (1 + abs(target)) <= NONLINEAR_TOLERANCE
        reported_transmission_error = abs(float(row[3]) - transmission) / (1 + abs(transmission))
        reported_reflection_error = abs(float(row[4]) - reflection) / (1 + abs(reflection))
        reported_residual_error = abs(float(row[5]) - (measured['input_power'] - target)) / (1 + abs(target))
        physical = 0 <= power <= 16 and row[2] >= 0 and measured['reflected_power'] >= -NONLINEAR_TOLERANCE
        nearest_reference = min(references, key=lambda root: abs(root['output_power'] - power))
        distinct_root_identity = nearest_reference is reference
        passed = physical and in_segment and distinct_root_identity and max(residual, transmission_error, reflection_error, reported_transmission_error, reported_reflection_error, reported_residual_error) <= NONLINEAR_TOLERANCE
        result['matched_roots'].append({'output_power': power, 'normalized_boundary_residual': residual,
            'normalized_T_error': transmission_error, 'normalized_R_error': reflection_error,
            'reported_T_error': reported_transmission_error, 'reported_R_error': reported_reflection_error,
            'reported_residual_error': reported_residual_error, 'same_reference_segment': bool(in_segment),
            'distinct_root_identity': distinct_root_identity,
            'reference_branch_multiplicity': reference['branch_multiplicity'], 'passes': bool(passed)})
    distinct = len(np.unique(ordered[:, 2] ** 2)) == len(ordered)
    result['duplicate_output_roots'] = not distinct
    result['passes'] = distinct and all(item['passes'] for item in result['matched_roots'])
    return result
