"""Independent continuous-Maxwell calculations; never a substitute for FDTD evidence."""

import numpy as np
from scipy.linalg import expm


def cascade(first, second):
    reflection_left, reverse_transmission, transmission, reflection_right = first
    next_left, next_reverse, next_transmission, next_right = second
    first_inverse = np.linalg.inv(np.eye(2) - reflection_right @ next_left)
    second_inverse = np.linalg.inv(np.eye(2) - next_left @ reflection_right)
    return (reflection_left + reverse_transmission @ next_left @ first_inverse @ transmission,
            reverse_transmission @ second_inverse @ next_reverse,
            next_transmission @ first_inverse @ transmission,
            next_right + next_transmission @ first_inverse @ reflection_right @ next_reverse)


def clc_jones(wavelength_um, pitches, ordinary=1.5, extraordinary=1.8, handedness=1):
    wavelengths = np.asarray(wavelength_um, dtype=float)
    rotation_rate = handedness * 2 * np.pi
    generator = np.array([[0, -1], [1, 0]])
    identity = np.eye(2)
    boundary = np.block([[identity, np.zeros((2, 2))], [rotation_rate * generator, identity]])
    circular = np.array([[1, 1], [1j, -1j]]) / np.sqrt(2)
    transmissions, reflections = [], []
    for wavelength in wavelengths:
        vacuum_wavevector = 2 * np.pi / wavelength
        propagation = np.block([[np.zeros((2, 2)), identity],
                                [rotation_rate**2 * identity - vacuum_wavevector**2 * np.diag([extraordinary**2, ordinary**2]),
                                 -2 * rotation_rate * generator]])
        transfer = boundary @ expm(propagation) @ np.linalg.inv(boundary)
        forward = np.vstack([identity, 1j * vacuum_wavevector * 1.5 * identity])
        backward = np.vstack([identity, -1j * vacuum_wavevector * 1.5 * identity])
        scattering = np.linalg.solve(np.column_stack([transfer @ backward, -forward]),
                                     np.column_stack([-transfer @ forward, backward]))
        period = (scattering[:2, :2], scattering[:2, 2:], scattering[2:, :2], scattering[2:, 2:])
        accumulated = (np.zeros((2, 2), complex), identity.astype(complex),
                       identity.astype(complex), np.zeros((2, 2), complex))
        for unused in range(int(pitches)):
            accumulated = cascade(accumulated, period)
        transmissions.append(circular.conj().T @ accumulated[2] @ circular)
        reflections.append(circular.conj().T @ accumulated[0] @ circular)
    return np.asarray(transmissions), np.asarray(reflections)
