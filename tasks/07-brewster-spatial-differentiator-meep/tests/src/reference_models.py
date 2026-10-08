"""Independent continuous-Maxwell calculations; never a substitute for FDTD evidence."""

import numpy as np


def brewster_reflection(normalized_wavevector, index=2.1):
    angle = np.arctan(index) + np.arcsin(np.asarray(normalized_wavevector))
    transmitted_cosine = np.sqrt(1 - (np.sin(angle) / index)**2)
    return (index * np.cos(angle) - transmitted_cosine) / (index * np.cos(angle) + transmitted_cosine)


def brewster_reference():
    from review_numerics import quadrature_weights
    wavevector = np.linspace(-0.1, 0.1, 4001)
    reflection = brewster_reflection(wavevector)
    coefficient = 2.1 / 2 - 1 / (2 * 2.1**3)
    approximation = -coefficient * wavevector
    result = {"operator_coefficient": coefficient,
              "maximum_reflectance_within_support": float(np.max(np.abs(reflection)**2))}
    for name, spectrum in (("gaussian", np.exp(-0.5 * (wavevector / 0.025)**2)),
                           ("sinc", (np.abs(wavevector) <= 0.09 + 1e-12).astype(float))):
        boundary = .09 if name == "sinc" else .1
        weights = quadrature_weights(wavevector, -boundary, boundary)
        output, target = reflection * spectrum, approximation * spectrum
        error = np.sqrt(np.dot(weights, np.abs(output - target)**2)
                        / np.dot(weights, np.abs(target)**2))
        efficiency = np.dot(weights, np.abs(output)**2) / np.dot(weights, np.abs(spectrum)**2)
        result[name] = {"fixed_operator_relative_l2_error": float(error), "reflected_power_fraction": float(efficiency)}
    return result
