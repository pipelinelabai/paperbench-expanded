"""Independent continuous-Maxwell calculations; never a substitute for FDTD evidence."""

import numpy as np
from scipy.optimize import brentq


def bilayer_trace(wavelength_um):
    wavelength = np.asarray(wavelength_um, dtype=float)
    high, low = 2.38, 1.46
    first = 2 * np.pi * high * 0.1628 / wavelength
    second = 2 * np.pi * low * 0.2672 / wavelength
    return np.cos(first) * np.cos(second) - 0.5 * (high / low + low / high) * np.sin(first) * np.sin(second)


def bilayer_edges():
    lower = brentq(lambda wavelength: float(bilayer_trace(wavelength) + 1), 1.2, 1.55)
    upper = brentq(lambda wavelength: float(bilayer_trace(wavelength) + 1), 1.55, 2.1)
    return lower, upper


def unpatterned_guided_roots():
    transverse_wavevector = 2 * np.pi / 0.9

    def residual(wavelength):
        vacuum_wavevector = 2 * np.pi / wavelength
        alpha = np.sqrt(transverse_wavevector**2 - vacuum_wavevector**2)
        matrix = np.eye(2, dtype=complex)
        for refractive_index, thickness in [(2.38, 0.1628), (1.46, 0.2672)] * 3:
            normal_wavevector = np.sqrt(complex((refractive_index * vacuum_wavevector)**2 - transverse_wavevector**2))
            phase = normal_wavevector * thickness
            layer = np.array([[np.cos(phase), np.sin(phase) / normal_wavevector],
                              [-normal_wavevector * np.sin(phase), np.cos(phase)]])
            matrix = layer @ matrix
        return float(np.real(matrix[1, 0] + alpha * matrix[1, 1]
                             + alpha * matrix[0, 0] + alpha**2 * matrix[0, 1]))

    samples = np.linspace(1.25, 1.75, 2001)
    values = [residual(value) for value in samples]
    return [brentq(residual, left, right) for left, right, first, second
            in zip(samples[:-1], samples[1:], values[:-1], values[1:]) if first * second < 0]
