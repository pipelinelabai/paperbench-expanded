from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from evidence import Evidence, EvidenceMissing
from acceptance import linear_comparison, power_comparison


def scattering(transfer, uniform_phase):
    basis = np.asarray([[1, 1], [1, -1]], dtype=complex)
    wave = np.linalg.solve(basis, transfer @ basis)
    denominator = wave[:, 1, 1]
    if np.any(abs(denominator) < 1e-12):
        raise ValueError('A scattering pole requires explicit singular-point treatment')
    return {'t': np.exp(-1j * uniform_phase) / denominator,
        'r_left': -wave[:, 1, 0] / denominator, 'r_right': wave[:, 0, 1] / denominator,
        'determinant_error': float(np.max(abs(np.linalg.det(wave) - 1)))}


def helmholtz(axis, imaginary=0.001, causal=False, tight=True):
    axis = np.atleast_1d(np.asarray(axis, dtype=float))
    period = 0.775 if causal else np.pi / 100
    wavenumber = 2 * np.pi / axis if causal else 100 - axis
    initial = np.broadcast_to(np.eye(2, dtype=complex), (len(axis), 2, 2)).copy()
    frequency = 1 / axis if causal else None

    def flow(position, flattened):
        real_index = 1 + 0.001 * np.cos(2 * np.pi * position)
        imaginary_index = imaginary * np.sin(2 * np.pi * position)
        if causal:
            resonance = 1 / 1.550
            strength = 2 * real_index * imaginary_index
            epsilon = real_index ** 2 - imaginary_index ** 2 + strength * resonance ** 2 / (
                resonance ** 2 - frequency ** 2 - 1j * resonance * frequency)
        else:
            epsilon = (real_index + 1j * imaginary_index) ** 2
        fields = flattened.reshape(len(axis), 2, 2)
        derivative = np.empty_like(fields)
        derivative[:, 0, :] = 1j * (period * wavenumber)[:, None] * fields[:, 1, :]
        derivative[:, 1, :] = 1j * (period * wavenumber * epsilon)[:, None] * fields[:, 0, :]
        return derivative.ravel()

    solution = solve_ivp(flow, (0, 1), initial.ravel(), method='DOP853', t_eval=[1],
        rtol=2e-13 if tight else 2e-10, atol=2e-15 if tight else 2e-12,
        max_step=1 / (128 if tight else 48))
    if not solution.success:
        raise ValueError(solution.message)
    cell = solution.y[:, -1].reshape(len(axis), 2, 2)
    transfer = np.linalg.matrix_power(cell, 1250)
    result = scattering(transfer, wavenumber * period * 1250)
    result['rhs_evaluations'] = solution.nfev
    return result


def coupled_modes(detuning, imaginary):
    detuning = np.atleast_1d(np.asarray(detuning, dtype=float))
    coupling = (100 - detuning) * 0.001 / 2
    gain = (100 - detuning) * imaginary / 2
    matrices = np.zeros((len(detuning), 2, 2), dtype=complex)
    matrices[:, 0, 0], matrices[:, 1, 1] = -1j * detuning, 1j * detuning
    matrices[:, 0, 1], matrices[:, 1, 0] = 1j * (coupling + gain), -1j * (coupling - gain)
    transfer = np.asarray([expm(matrix * 12.5 * np.pi) for matrix in matrices])
    denominator = transfer[:, 1, 1]
    return {'t': np.exp(1j * detuning * 12.5 * np.pi) / denominator,
        'r_left': -transfer[:, 1, 0] / denominator, 'r_right': transfer[:, 0, 1] / denominator}


def phase_delay(solver, detuning, step):
    transmission = solver(detuning)['t']
    phase = np.unwrap(np.angle(transmission))
    center = int(np.argmin(abs(detuning)))
    phase -= 2 * np.pi * np.rint((phase[center] - np.angle(transmission[center])) / (2 * np.pi))
    plus, minus = solver(detuning + step)['t'], solver(detuning - step)['t']
    delay = -np.angle(plus / minus) / (2 * step)
    return phase, delay


def derivative_refinement(solver, detuning):
    steps = (1e-4, 5e-5, 2.5e-5)
    evaluations = [phase_delay(solver, detuning, step) for step in steps]
    differences = [float(np.max(abs(second[1] - first[1])))
        for first, second in zip(evaluations[:-1], evaluations[1:])]
    metadata = {'steps_detuning': list(steps), 'successive_delay_max_changes': differences,
        'empirical_order_from_max_changes': float(np.log2(differences[0] / differences[1]))
        if min(differences) > 0 else None,
        'scope': 'Three-step differentiation sensitivity, not a rigorous error bound'}
    return evaluations[-1][0], evaluations[-1][1], metadata


def sampled(arrays, axis):
    source_axis = np.asarray(arrays['delta'])
    if source_axis.ndim != 1 or not np.isfinite(source_axis).all() or len(np.unique(source_axis)) != len(source_axis):
        raise ValueError('The paper reporting axis must have unique finite coordinates')
    indices = np.argmin(abs(source_axis[:, None] - axis[None, :]), axis=0)
    if not np.allclose(source_axis[indices], axis, atol=1e-12, rtol=0):
        raise ValueError('The required fixed paper reporting points are not retained')
    return {key: arrays[key][indices] for key in ('t', 'r_left', 'r_right', 'phase', 'delay')}


def calibrate(candidate_output, output):
    candidate_output, output = Path(candidate_output), Path(output)
    evidence = Evidence(candidate_output)
    output.mkdir(parents=True, exist_ok=False)
    report = {'method': 'Independent adaptive dimensionless-cell Helmholtz IVP plus 1250-cell transfer; coupled modes by constant-generator matrix exponential',
        'phase_derivative': 'Independent centered local phase-ratio differences at 1e-4, 5e-5 and 2.5e-5 detuning, not a candidate spline',
        'candidate_artifacts': {}, 'paper': {}, 'causal': {},
        'scope': 'Measured discretization and model discrepancies, not guaranteed error bounds'}
    detuning = np.linspace(-1, 1, 201)
    for label, imaginary in (('passive', 0.0), ('exceptional', 0.001)):
        report['paper'][label] = {}
        for model in ('helmholtz', 'coupled_mode'):
            solver = (lambda values: helmholtz(values, imaginary)) if model == 'helmholtz' else (lambda values: coupled_modes(values, imaginary))
            fields = solver(detuning)
            phase, delay, derivative = derivative_refinement(solver, detuning)
            fields.update(phase=phase, delay=delay)
            relative = f'results/paper/linear/{label}/{model}.npz'
            identifier = f'linear/{label}/{model}'
            try:
                candidate = sampled(evidence.observation(identifier, relative, axis='delta'), detuning)
            except EvidenceMissing as error:
                report.setdefault('missing_observations', {})[identifier] = str(error)
                continue
            comparison = {key + '_max_difference': float(np.max(abs(fields[key] - candidate[key])))
                for key in ('t', 'r_left', 'r_right', 'phase', 'delay')}
            comparison['independent_delay_refinement_change'] = derivative['successive_delay_max_changes'][-1]
            comparison['independent_differentiation_refinement'] = derivative
            comparison['scaled_complex_amplitude_differences'] = {key:
                float(np.max(abs(fields[key] - candidate[key]) / np.maximum(1, abs(fields[key]))))
                for key in ('t', 'r_left', 'r_right')}
            comparison['acceptance'] = linear_comparison(fields, candidate)
            comparison['candidate_artifacts'] = evidence.observation_artifacts[identifier]
            if model == 'helmholtz':
                coarse = helmholtz(detuning, imaginary, tight=False)
                comparison['independent_integration_t_change'] = float(np.max(abs(fields['t'] - coarse['t'])))
                comparison['independent_complex_field_refinement'] = {key:
                    float(np.max(abs(fields[key] - coarse[key]) / np.maximum(1, abs(fields[key]))))
                    for key in ('t', 'r_left', 'r_right')}
                comparison['independent_phase_refinement_rad'] = float(np.max(abs(np.angle(fields['t'] / coarse['t']))))
                comparison['independent_determinant_error'] = fields['determinant_error']
            report['paper'][label][model] = comparison
            np.savez_compressed(output / f'{label}_{model}.npz', delta=detuning, **fields)
    wavelength = np.linspace(1.520, 1.580, 301)
    for group, imaginary in (('baseline', 0.001), ('control', -0.001)):
        fine = helmholtz(wavelength, imaginary, causal=True)
        coarse = helmholtz(wavelength, imaginary, causal=True, tight=False)
        report['causal'][group] = {'independent_integration_t_change': float(np.max(abs(fine['t'] - coarse['t']))),
            'independent_reflection_power_refinement': {side:
                float(np.max(abs(abs(fine['r_' + side]) ** 2 - abs(coarse['r_' + side]) ** 2)))
                for side in ('left', 'right')},
            'independent_determinant_error': fine['determinant_error']}
        for side in ('left', 'right'):
            identifier = f'native/{group}_{side}'
            try:
                raw = evidence.observation(identifier, f'results/{identifier}/raw.npz', axis='wavelength_um')
            except EvidenceMissing:
                report['causal'][group][side] = {'status': 'native_case_missing'}
                continue
            if not np.allclose(raw['wavelength_um'], wavelength, atol=1e-12, rtol=0):
                raise ValueError('Changed native causal reporting axis')
            transmission = raw['device_outgoing'][:, 0] / raw['reference_outgoing'][:, 0]
            report['causal'][group][side] = {'native_t_max_difference': float(np.max(abs(transmission - fine['t']))),
                'native_R_center_difference': float(raw['R'][150] - abs(fine['r_' + side][150]) ** 2),
                'native_R_center_pass': power_comparison(float(raw['R'][150]), float(abs(fine['r_' + side][150]) ** 2)),
                'candidate_artifacts': evidence.observation_artifacts[identifier]}
        np.savez_compressed(output / f'causal_{group}.npz', wavelength_um=wavelength, **fine)
    report['candidate_artifacts'].update(evidence.artifacts)
    return report
