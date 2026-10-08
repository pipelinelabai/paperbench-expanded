
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


def cubic_mass(offsets, energies):
    offsets, energies = finite(offsets), finite(energies)
    if offsets.ndim != 2 or offsets.shape[1] != 2 or energies.shape != (len(offsets),) or not len(offsets):
        raise ValueError('Invalid two-dimensional mass samples')
    powers = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (3, 0), (2, 1), (1, 2), (0, 3))
    scale = float(np.linalg.norm(offsets, axis=1).max()) or 1.0
    scaled = offsets / scale
    matrix = np.column_stack([scaled[:, 0] ** first * scaled[:, 1] ** second for first, second in powers])
    singular = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.linalg.matrix_rank(matrix))
    result = {'rank': rank, 'points': len(offsets), 'distinct_points': len(np.unique(offsets, axis=0)),
        'singular_values': singular.tolist(), 'distinct_energies': len(np.unique(energies)), 'identified': rank == 10}
    if rank != 10:
        return result
    coefficients = np.linalg.lstsq(matrix, energies - energies.mean(), rcond=None)[0]
    physical = coefficients / np.asarray([scale ** (first + second) for first, second in powers])
    hessian = np.asarray([[2 * physical[3], physical[4]], [physical[4], 2 * physical[5]]])
    eigenvalues = np.linalg.eigvalsh(hessian)
    result.update(coefficients=physical.tolist(), hessian_ev_angstrom2=hessian.tolist(),
        gradient_ev_angstrom=physical[1:3].tolist(), rms_ev=float(np.sqrt(np.mean((matrix @ coefficients - (energies - energies.mean())) ** 2))),
        principal_curvatures=eigenvalues.tolist(), principal_masses_m0=(2 * 3.8099821161548593 / eigenvalues).tolist() if np.all(eigenvalues != 0) else None)
    return result


def stiffness(strains, stresses_kbar, height_angstrom):
    strains, stresses = finite(strains), finite(stresses_kbar)
    if strains.ndim != 1 or len(strains) < 4 or stresses.shape != (len(strains), 3, 3):
        raise ValueError('Invalid strain-family data')
    if height_angstrom <= 0 or len(np.unique(strains)) != len(strains):
        raise ValueError('Invalid cell height or duplicated strains')
    if not all(np.any(np.isclose(strains, value, atol=1e-10, rtol=0)) for value in (-0.01, 0.01)):
        raise ValueError('Missing paper +/-1% strain observations')
    tensile = -stresses * height_angstrom * 0.01
    matrix = np.column_stack((strains, np.ones(len(strains))))
    fit = np.linalg.lstsq(matrix, tensile.reshape(len(strains), -1), rcond=None)[0]
    residual = tensile.reshape(len(strains), -1) - matrix @ fit
    smaller = np.abs(strains) < 0.01 - 1e-10
    if smaller.sum() < 2 or not np.allclose(np.sort(strains[smaller]), np.sort(-strains[smaller]), atol=1e-10, rtol=0):
        raise ValueError('Missing smaller symmetric strain pair')
    local = np.linalg.lstsq(matrix[smaller], tensile.reshape(len(strains), -1)[smaller], rcond=None)[0]
    return {'tensor_slope_N_per_m': fit[0].reshape(3, 3).tolist(),
        'smaller_strain_slope_N_per_m': local[0].reshape(3, 3).tolist(),
        'rms_N_per_m': np.sqrt(np.mean(residual ** 2, axis=0)).reshape(3, 3).tolist()}
