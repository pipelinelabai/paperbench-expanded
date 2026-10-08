
import numpy as np


def finite(values, shape=None):
    array = np.asarray(values)
    if array.dtype.kind not in 'fciu' or not np.isfinite(array).all():
        raise ValueError('Expected finite numerical data')
    if shape is not None and array.shape != shape:
        raise ValueError(f'Unexpected array shape {array.shape}; required {shape}')
    return array


def merge_samples(parts):
    samples = {}
    for axis, values in parts:
        axis, values = finite(axis), finite(values)
        if axis.ndim != 1 or len(axis) != len(values):
            raise ValueError('Sample axes and rows do not match')
        for coordinate, row in zip(axis, values):
            key = float(coordinate)
            if key in samples and not np.array_equal(samples[key], row):
                raise ValueError('Conflicting duplicate scientific sample')
            samples[key] = row
    if not samples:
        raise ValueError('No scientific samples')
    axis = np.asarray(sorted(samples))
    return axis, np.asarray([samples[coordinate] for coordinate in axis])


def center_component(axis, constraints, center):
    axis, constraints = finite(axis), finite(constraints)
    if axis.ndim != 1 or len(axis) < 2 or constraints.shape[0] != len(axis):
        raise ValueError('Invalid interval samples')
    if constraints.ndim == 1:
        constraints = constraints[:, None]
    if constraints.ndim != 2 or np.any(np.diff(axis) <= 0) or not axis[0] <= center <= axis[-1]:
        raise ValueError('Invalid interval axis or center')
    if any(np.interp(center, axis, constraints[:, column]) > 1 for column in range(constraints.shape[1])):
        return None
    intervals = []
    for index in range(len(axis) - 1):
        lower, upper = 0.0, 1.0
        for first, second in zip(constraints[index], constraints[index + 1]):
            if first > 1 and second > 1:
                lower, upper = 1.0, 0.0
                break
            difference = second - first
            if difference > 0:
                upper = min(upper, float((1 - first) / difference))
            elif difference < 0:
                lower = max(lower, float((1 - first) / difference))
        if lower <= upper:
            interval = [float(axis[index] + lower * (axis[index + 1] - axis[index])),
                float(axis[index] + upper * (axis[index + 1] - axis[index]))]
            if intervals and interval[0] <= intervals[-1][1]:
                intervals[-1][1] = max(intervals[-1][1], interval[1])
            else:
                intervals.append(interval)
    for lower, upper in intervals:
        if lower <= center <= upper:
            return {'lower': lower, 'upper': upper, 'width': upper - lower,
                'lower_censored': bool(lower == axis[0]), 'upper_censored': bool(upper == axis[-1])}
    raise ValueError('Center is feasible but no connected interval was recovered')


def lorentz_epsilon(position, frequency, gain_sign=1):
    position, frequency = finite(position), finite(frequency)
    real_index = 1 + 0.001 * np.cos(2 * np.pi * position / 0.775)
    imaginary_index = gain_sign * 0.001 * np.sin(2 * np.pi * position / 0.775)
    center = 1 / 1.550
    return real_index ** 2 - imaginary_index ** 2 + 2 * real_index * imaginary_index * center ** 2 / (
        center ** 2 - frequency[:, None] ** 2 - 1j * center * frequency[:, None])


def invariant_residuals(stokes, kappa, gain, rho=1, detuning=0):
    stokes = finite(stokes)
    if stokes.ndim != 3 or stokes.shape[1] != 4:
        raise ValueError('Stokes data must have shape (profile,4,position)')
    total, difference, real_cross, imaginary_cross = np.moveaxis(stokes, 1, 0)
    quantities = [difference ** 2 + real_cross ** 2 + imaginary_cross ** 2 - total ** 2,
        gain * total - kappa * difference,
        3 * rho * gain * total ** 2 - 4 * kappa * detuning * difference + 4 * kappa * gain * real_cross]
    scales = [np.max(total ** 2, axis=1),
        np.max(abs(gain * total) + abs(kappa * difference), axis=1),
        np.max(abs(3 * rho * gain * total ** 2) + abs(4 * kappa * detuning * difference) + abs(4 * kappa * gain * real_cross), axis=1)]
    results = []
    for index, (quantity, scale) in enumerate(zip(quantities, scales)):
        residual = quantity if index == 0 else quantity - quantity[:, :1]
        results.append(np.max(abs(residual), axis=1) / np.where(scale > 0, scale, 1))
    return np.stack(results, axis=1)
