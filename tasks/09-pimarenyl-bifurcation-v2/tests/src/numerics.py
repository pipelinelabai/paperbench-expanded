import math

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


def molecular_observations(coordinates):
    coordinates = finite(coordinates, (53, 3))
    pairs = {'reactant': (24, 25), 'transfer': (25, 50), 'B': (44, 48), 'C': (38, 48), 'D': (41, 48)}
    distances = {name: float(np.linalg.norm(coordinates[first] - coordinates[second])) for name, (first, second) in pairs.items()}
    ranked = sorted((distances[name], name) for name in ('B', 'C', 'D'))
    margin = ranked[1][0] - ranked[0][0]
    if distances['reactant'] < 1.2:
        label = 'reactant'
    elif distances['transfer'] >= 1.2:
        label = 'incomplete'
    elif margin < 0.01:
        label = 'ambiguous'
    else:
        label = 'toward_' + ranked[0][1]
    return {'distances_angstrom': distances, 'label': label, 'commitment_margin_angstrom': margin,
        'boundary_distances_angstrom': {'reactant': abs(distances['reactant'] - 1.2), 'transfer': abs(distances['transfer'] - 1.2), 'commitment': abs(margin - 0.01)},
        'q_angstrom': [distances['C'] - distances['B'], distances['D'] - distances['B']]}


def wilson(successes, count):
    if type(count) is not int or type(successes) is not int or not 0 <= successes <= count:
        raise ValueError('Invalid binomial counts')
    if count == 0:
        return None
    confidence = 1.95996398454
    proportion = successes / count
    denominator = 1 + confidence ** 2 / count
    center = (proportion + confidence ** 2 / (2 * count)) / denominator
    radius = confidence * math.sqrt(proportion * (1 - proportion) / count + confidence ** 2 / (4 * count ** 2)) / denominator
    return [max(0.0, center - radius), min(1.0, center + radius)]


def condition_statistics(labels, required=4):
    names = ('reactant', 'incomplete', 'ambiguous', 'toward_B', 'toward_C', 'toward_D')
    if len(labels) > required or any(label not in names for label in labels):
        raise ValueError('Invalid primary labels or denominator')
    count = len(labels)
    return {'completed': count, 'required': required, 'labels': {
        name: {'count': labels.count(name), 'fraction': labels.count(name) / count if count else None,
            'wilson_95': wilson(labels.count(name), count),
            'full_sample_bounds': [labels.count(name) / required, (labels.count(name) + required - count) / required]}
        for name in names}}


def trajectory_checks(record, initial, structure, constants):
    frames = record['frames']
    specification = record['run']
    masses = finite(structure['masses_u'], (53,)) * constants['u_to_electron_mass']
    timestep = specification['dt_fs'] * constants['atomic_time_per_fs']
    position_residual, velocity_residual, energy_series, observations = [], [], [], []
    for index, frame in enumerate(frames):
        if frame['step'] != index or abs(frame['time_fs'] - index * specification['dt_fs']) > 1e-9:
            raise ValueError('Trajectory is not a continuous correctly timed prefix')
        position = finite(frame['coordinates_angstrom'], (53, 3)) / constants['angstrom_per_bohr']
        velocity = finite(frame['velocities_bohr_per_atomic_time'], (53, 3))
        gradient = finite(frame['gradient_hartree_per_bohr'], (53, 3))
        energy = float(finite(frame['energy_hartree']))
        acceleration = -gradient / masses[:, None]
        if index:
            predicted_position = previous_position + timestep * previous_velocity + 0.5 * timestep ** 2 * previous_acceleration
            predicted_velocity = previous_velocity + 0.5 * timestep * (previous_acceleration + acceleration)
            position_residual.append(float(np.max(abs(position - predicted_position))))
            velocity_residual.append(float(np.max(abs(velocity - predicted_velocity))))
        else:
            initial_position_error = float(np.max(abs(frame['coordinates_angstrom'] - np.asarray(structure['coordinates_angstrom']))))
            initial_velocity_error = float(np.max(abs(velocity - np.asarray(initial['velocities_bohr_per_atomic_time']))))
        kinetic = float(0.5 * np.sum(masses[:, None] * velocity ** 2))
        energy_series.append(energy + kinetic)
        observation = molecular_observations(frame['coordinates_angstrom'])
        observation.update(time_fs=frame['time_fs'], gradient_rms=float(np.sqrt(np.mean(gradient ** 2))), kinetic_hartree=kinetic)
        observations.append(observation)
        previous_position, previous_velocity, previous_acceleration = position, velocity, acceleration
    if not frames:
        return {'complete': False, 'frame_count': 0, 'observations': []}
    return {'complete': len(frames) == specification['steps'] + 1, 'frame_count': len(frames),
        'initial_coordinate_error_angstrom': initial_position_error,
        'initial_velocity_error_au': initial_velocity_error,
        'initial_velocity_within_public_tolerance': bool(np.allclose(frames[0]['velocities_bohr_per_atomic_time'], initial['velocities_bohr_per_atomic_time'], atol=1e-12, rtol=1e-8)),
        'max_vv_coordinate_error_bohr': max(position_residual, default=0),
        'max_vv_velocity_error_au': max(velocity_residual, default=0),
        'total_energy_hartree': energy_series,
        'total_energy_drift_hartree': float(np.max(abs(np.asarray(energy_series) - energy_series[0]))),
        'observations': observations}
