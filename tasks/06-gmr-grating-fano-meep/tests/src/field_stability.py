"""Native field-tail diagnostics; no solver, files, provenance verification, or scores."""

import math

import numpy as np

TAIL_SLOPE_MAX = 0.0
TAIL_RATIO_MAX = 1.1


def _array(value, name, real=False):
    result = np.asarray(value)
    if result.dtype.kind not in 'iufc' or not result.size or not np.isfinite(result).all():
        raise ValueError(f'{name} must contain finite numeric samples, not booleans/strings')
    if real and np.iscomplexobj(result):
        raise ValueError(f'{name} must be real')
    return result.astype(float if real else complex)

def _axis(value, name, minimum=2):
    result = _array(value, name, real=True)
    if result.ndim != 1 or len(result) < minimum or np.any(np.diff(result) <= 0):
        raise ValueError(f'{name} must be a sufficiently sampled, strictly increasing axis')
    return result

def _scalar(value, name, minimum=0):
    if isinstance(value, (bool, str)) or np.ndim(value) != 0:
        raise ValueError(f'{name} must be a finite real scalar')
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f'{name} must be finite and >= {minimum}')
    return result

def _field(quantities, prefix=''):
    names = [prefix + name for name in ('field', 'field_envelope') if prefix + name in quantities]
    if len(names) != 1:
        raise ValueError(f'Bind exactly one {prefix}field or {prefix}field_envelope')
    name = names[0]
    envelope = name.endswith('field_envelope')
    values = _array(quantities[name], name, real=envelope)
    if envelope and np.any(values < 0):
        raise ValueError('A declared envelope cannot contain negative samples')
    return np.abs(values)

def _blocks(time, envelope, start, end):
    edges = np.linspace(start, end, 7)
    maxima, maximum_times, counts = [], [], []
    for index in range(6):
        selected = (time >= edges[index]) & ((time < edges[index + 1]) if index < 5 else (time <= end))
        indices = np.flatnonzero(selected)
        counts.append(len(indices))
        if len(indices):
            maximum = indices[np.argmax(envelope[indices])]
            maxima.append(float(envelope[maximum]))
            maximum_times.append(float(time[maximum]))
        else:
            maxima.append(None)
            maximum_times.append(None)
    return edges.tolist(), maxima, maximum_times, counts

def stability_metrics(quantities, context):
    """Diagnose only the fixed observed tail; missing evidence stays indeterminate."""
    time = _axis(quantities['time'], 'time', 12)
    envelope = _field(quantities)
    if envelope.shape != time.shape:
        raise ValueError('Field samples must match the native time axis')
    source_off = _scalar(context['source_off_time'], 'source_off_time')
    result = dict(log_envelope_slope=None, late_early_ratio=None, last_three_growth=None,
                  block_maxima=[], block_maximum_times=[], tail_status='indeterminate',
                  tail_reason=None, source_off_time=source_off, observation_end_time=float(time[-1]),
                  slope_limit=TAIL_SLOPE_MAX, ratio_limit=TAIL_RATIO_MAX,
                  global_stability_established=False, provenance_status='external_review_required',
                  noise_floor=None, noise_status='not_supplied', tail_numeric_criteria_met=None)
    post_source = time >= source_off
    if time[0] > source_off or np.count_nonzero(post_source) < 12:
        result['tail_reason'] = 'need_full_source_on_trace_and_at_least_12_post_source_samples'
        return result
    result['post_source_block_maxima'] = _blocks(time, envelope, source_off, time[-1])[1]
    if 'arrival_time' not in context:
        result['tail_reason'] = 'missing_independently_justified_last_direct_pulse_arrival_time'
        return result
    arrival = _scalar(context['arrival_time'], 'arrival_time', source_off)
    if arrival >= time[-1]:
        result['tail_reason'] = 'observation_does_not_extend_beyond_direct_pulse_arrival'
        return result
    start = arrival + (time[-1] - arrival) / 2
    result.update(arrival_time=arrival, tail_window=[float(start), float(time[-1])],
                  tail_rule='final_half_after_last_direct_pulse_arrival',
                  arrival_basis=context.get('arrival_basis'))
    edges, maxima, maximum_times, counts = _blocks(time, envelope, start, time[-1])
    result.update(block_edges=edges, block_maxima=maxima, block_maximum_times=maximum_times,
                  block_sample_counts=counts)
    if min(counts) < 2:
        result['tail_reason'] = 'need_at_least_two_native_samples_in_each_equal_duration_tail_block'
        return result
    tail_times = time[time >= start]
    if np.max(np.diff(tail_times)) > (time[-1] - start) / 6:
        result['tail_reason'] = 'tail_sampling_gap_exceeds_one_block_duration'
        return result
    maxima = np.asarray(maxima)
    maximum_times = np.asarray(maximum_times)
    result['last_three_growth'] = bool(np.all(np.diff(maxima[-3:]) > 0))
    if np.all(maxima > 0):
        centered_time = maximum_times - np.mean(maximum_times)
        coefficients = centered_time / np.dot(centered_time, centered_time)
        log_origin = np.log(maxima[0])
        result['log_envelope_slope'] = float(np.dot(coefficients, np.log(maxima) - log_origin))
        result['late_early_ratio'] = float(maxima[-1] / maxima[0])
    else:
        result['tail_reason'] = 'zero_block_magnitude_does_not_define_a_log_slope'
        return result
    noise = 0.0
    noise_names = [name for name in quantities if name.startswith('noise_')]
    if noise_names or any(name in context for name in ('noise_floor', 'noise_run_id')):
        run_id, noise_id = context.get('run_id'), context.get('noise_run_id')
        if not isinstance(run_id, str) or not run_id or not isinstance(noise_id, str) or not noise_id or run_id == noise_id:
            result.update(noise_status='indeterminate', tail_reason='noise_requires_distinct_native_run_identities')
            return result
        if 'noise_time' not in quantities or 'noise_arrival_time' not in context:
            result.update(noise_status='indeterminate', tail_reason='noise_requires_raw_trace_and_independent_arrival')
            return result
        noise_time = _axis(quantities['noise_time'], 'noise_time', 12)
        noise_envelope = _field(quantities, 'noise_')
        if noise_envelope.shape != noise_time.shape:
            raise ValueError('Noise field samples must match their own time axis')
        noise_arrival = _scalar(context['noise_arrival_time'], 'noise_arrival_time')
        if noise_arrival > start or noise_time[0] > start or noise_time[-1] < time[-1]:
            result.update(noise_status='indeterminate', tail_reason='independent_noise_does_not_cover_the_same_source_free_tail')
            return result
        noise_blocks = _blocks(noise_time, noise_envelope, start, time[-1])
        if min(noise_blocks[3]) < 2:
            result.update(noise_status='indeterminate', tail_reason='independent_noise_tail_is_undersampled')
            return result
        noise = float(max(noise_blocks[1]))
        result.update(noise_status='raw_bound_requires_external_provenance_and_normalization_review',
                      noise_floor=noise, noise_run_id=noise_id, run_id=run_id)
    lower = maxima - noise
    upper = maxima + noise
    result['resolved_last_three_growth'] = bool(np.all(np.diff(maxima[-3:]) > 2 * noise))
    if np.any(lower <= 0):
        result['tail_reason'] = 'noise_floor_prevents_resolving_all_six_log_envelope_blocks'
        return result
    slope_lower = float(np.dot(coefficients, np.where(coefficients >= 0, np.log(lower), np.log(upper)) - log_origin))
    slope_upper = float(np.dot(coefficients, np.where(coefficients >= 0, np.log(upper), np.log(lower)) - log_origin))
    ratio_lower, ratio_upper = float(lower[-1] / upper[0]), float(upper[-1] / lower[0])
    result.update(log_slope_bounds=[slope_lower, slope_upper], late_early_ratio_bounds=[ratio_lower, ratio_upper])
    if slope_lower > TAIL_SLOPE_MAX or ratio_lower > TAIL_RATIO_MAX or result['resolved_last_three_growth']:
        result.update(tail_status='resolved_growth_or_ratio_exceedance', tail_numeric_criteria_met=False,
                      tail_reason='fixed_tail_criteria_exceeded_without_relaxing_thresholds')
    elif slope_upper <= TAIL_SLOPE_MAX and ratio_upper <= TAIL_RATIO_MAX and not result['last_three_growth']:
        result.update(tail_status='finite_observed_tail_criteria_met', tail_numeric_criteria_met=True,
                      tail_reason='not_a_proof_of_global_stability_or_duration_convergence')
    else:
        result['tail_reason'] = 'uncertainty_does_not_resolve_the_fixed_tail_criteria'
    return result
