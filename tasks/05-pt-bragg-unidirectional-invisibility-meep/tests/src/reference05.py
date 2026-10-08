import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

from acceptance import NONLINEAR_TOLERANCE, TURN_INPUT_TOLERANCE, bounded_interval_contains, root_set_comparison
from evidence import Evidence, EvidenceMissing


ROOT_XTOL = 1e-11
SECTION_ATOL = 1e-10
MAX_INPUT = 3.2
MAX_OUTPUT = 16.0
GRID_SIZES = (2049, 4097)


def stokes_flow(position, state, gain):
    total, difference, real_cross, imaginary_cross = state.reshape(4, -1)
    kappa = 0.25
    return np.asarray([2 * kappa * imaginary_cross, 2 * gain * imaginary_cross,
        -3 * total * imaginary_cross, 3 * total * real_cross + 2 * kappa * total - 2 * gain * difference]).ravel()


def variational_flow(position, state, gain):
    total, difference, real_cross, imaginary_cross, tangent_total, tangent_difference, tangent_real, tangent_imaginary = state.reshape(8, -1)
    kappa = 0.25
    return np.asarray([2*kappa*imaginary_cross, 2*gain*imaginary_cross,
        -3*total*imaginary_cross, 3*total*real_cross+2*kappa*total-2*gain*difference,
        2*kappa*tangent_imaginary, 2*gain*tangent_imaginary,
        -3*(tangent_total*imaginary_cross+total*tangent_imaginary),
        (3*real_cross+2*kappa)*tangent_total-2*gain*tangent_difference+3*total*tangent_real]).ravel()


def solve_variational(output_power, gain, side, tight):
    powers = np.atleast_1d(output_power).astype(float)
    if side not in ('left', 'right') or powers.ndim != 1 or not np.isfinite(powers).all() or np.any(powers < 0):
        raise ValueError('Expected a direction and finite nonnegative output powers')
    initial = np.zeros((8, len(powers)))
    initial[0] = powers
    initial[1] = powers if side == 'left' else -powers
    initial[4] = 1
    initial[5] = 1 if side == 'left' else -1
    start, end = (3.5, -3.5) if side == 'left' else (-3.5, 3.5)
    solution = solve_ivp(variational_flow, (start, end), initial.ravel(), args=(gain,),
        method='DOP853', rtol=2e-11 if tight else 2e-9, atol=2e-13 if tight else 2e-11,
        max_step=7 / (256 if tight else 128), t_eval=[end])
    if not solution.success:
        raise RuntimeError(solution.message)
    final = solution.y[:, -1].reshape(8, -1)
    if not np.isfinite(final).all():
        raise RuntimeError('Nonfinite independent Stokes/variational solution')
    incident = (final[0] + final[1]) / 2 if side == 'left' else (final[0] - final[1]) / 2
    reflected = (final[0] - final[1]) / 2 if side == 'left' else (final[0] + final[1]) / 2
    sign = 1 if side == 'left' else -1
    return {'input_power': incident, 'reflected_power': reflected,
        'input_derivative': (final[4]+sign*final[5])/2,
        'reflection_derivative': (final[4]-sign*final[5])/2,
        'stokes_final': final[:4].T, 'stokes_variation_final': final[4:].T}


def solve(output_power, gain, side, tight):
    result = solve_variational(output_power, gain, side, tight)
    return result['input_power'], result['reflected_power']


def evaluator(gain, side, tight, powers=(), values=None):
    cache = {}
    if values is not None:
        for index, power in enumerate(powers):
            cache[float(power)] = {key: float(values[key][index])
                for key in ('input_power', 'reflected_power', 'input_derivative', 'reflection_derivative')}

    def evaluate(power):
        power = float(power)
        if power not in cache:
            data = solve_variational(power, gain, side, tight)
            cache[power] = {key: float(data[key][0])
                for key in ('input_power', 'reflected_power', 'input_derivative', 'reflection_derivative')}
        return cache[power]
    return evaluate


def stationary_points(powers, derivatives, evaluate):
    found, unresolved = {}, []
    for index in range(len(powers)-1):
        lower, upper = map(float, powers[index:index+2])
        first, second = derivatives[index:index+2]
        if first == 0:
            found[lower] = [lower, lower]
        if first*second < 0:
            root = brentq(lambda power: evaluate(power)['input_derivative'], lower, upper, xtol=ROOT_XTOL)
            found[float(root)] = [lower, upper]
        elif first == second == 0:
            unresolved.append({'output_bracket': [lower, upper], 'reason': 'zero derivative at both sample endpoints'})
    if derivatives[-1] == 0:
        found[float(powers[-1])] = [float(powers[-1]), float(powers[-1])]
    for index in range(1, len(powers)-1):
        neighborhood = derivatives[index-1:index+2]
        magnitude = abs(neighborhood)
        if (np.all(neighborhood > 0) or np.all(neighborhood < 0)) and magnitude[1] < min(magnitude[0], magnitude[2]):
            if magnitude[1] > np.max(abs(np.diff(neighborhood))):
                continue
            lower, upper = map(float, powers[index-1:index+2:2])
            sign = 1 if neighborhood[1] > 0 else -1
            minimum = minimize_scalar(lambda power: sign*evaluate(power)['input_derivative'],
                bounds=(lower, upper), method='bounded', options={'xatol': ROOT_XTOL})
            probe = float(minimum.x)
            if evaluate(probe)['input_derivative'] == 0:
                found[probe] = [lower, upper]
            elif sign*evaluate(probe)['input_derivative'] < 0:
                for first_bound, second_bound in ((lower, probe), (probe, upper)):
                    root = brentq(lambda power: evaluate(power)['input_derivative'], first_bound, second_bound, xtol=ROOT_XTOL)
                    found[float(root)] = [first_bound, second_bound]
            else:
                unresolved.append({'output_bracket': [lower, upper], 'output_power': probe,
                    'derivative_residual': evaluate(probe)['input_derivative'],
                    'reason': 'same-sign derivative minimum; stationary contact not established'})
    turns = []
    for power, bracket in sorted(found.items()):
        if not powers[0] < power < powers[-1]:
            continue
        initial = bracket.copy()
        if bracket[0] != bracket[1]:
            for multiplier in (1, 2, 4, 8, 16, 32, 64):
                trial = [max(initial[0], power-multiplier*ROOT_XTOL), min(initial[1], power+multiplier*ROOT_XTOL)]
                if evaluate(trial[0])['input_derivative']*evaluate(trial[1])['input_derivative'] <= 0:
                    bracket = trial
                    break
        left, right = evaluate(bracket[0]), evaluate(bracket[1])
        measured = evaluate(power)
        earlier = left['input_derivative'] or evaluate(float(powers[max(0, np.searchsorted(powers, power)-1)]))['input_derivative']
        later = right['input_derivative'] or evaluate(float(powers[min(len(powers)-1, np.searchsorted(powers, power)+1)]))['input_derivative']
        kind = 'maximum' if earlier > 0 and later < 0 else 'minimum' if earlier < 0 and later > 0 else 'stationary_contact'
        turns.append({'output_power': power, 'input_power': measured['input_power'], 'kind': kind,
            'initial_output_bracket': initial, 'output_bracket': bracket,
            'input_bracket': [min(left['input_power'], right['input_power'], measured['input_power']),
                              max(left['input_power'], right['input_power'], measured['input_power'])],
            'derivative_bracket': [left['input_derivative'], right['input_derivative']],
            'derivative_residual': measured['input_derivative']})
    return turns, unresolved


def section_roots(target, nodes, evaluate):
    found, contacts, nonisolated = {}, [], []
    values = [evaluate(power)['input_power']-target for power in nodes]
    for index, power in enumerate(nodes):
        if values[index] == 0:
            found[('node', index)] = (power, [power, power], 'endpoint' if index in (0, len(nodes)-1) else 'stationary_contact')
        elif abs(values[index]) <= SECTION_ATOL and index not in (0, len(nodes)-1):
            if values[index]*values[index-1] >= 0 and values[index]*values[index+1] >= 0:
                contacts.append({'output_power': power, 'input_residual': values[index],
                                 'status': 'near-contact unresolved; not rounded into a root'})
    for index, (lower, upper) in enumerate(zip(nodes[:-1], nodes[1:])):
        first, second = values[index:index+2]
        if first*second < 0:
            root = brentq(lambda power: evaluate(power)['input_power']-target, lower, upper, xtol=ROOT_XTOL)
            found[('segment', index)] = (float(root), [lower, upper], 'crossing')
        elif first == second == 0 and evaluate((lower+upper)/2)['input_power'] == target:
            nonisolated.append([lower, upper])
    roots = []
    for power, bracket, kind in sorted(found.values()):
        measured = evaluate(power)
        branches = [index for index, (lower, upper) in enumerate(zip(nodes[:-1], nodes[1:])) if lower <= power <= upper]
        roots.append({'output_power': float(power), 'input_residual': measured['input_power']-target,
            'reflected_power': measured['reflected_power'], 'output_bracket': bracket,
            'T': power/target if target else None, 'R': measured['reflected_power']/target if target else None,
            'kind': kind, 'incident_branch_indices': branches, 'branch_multiplicity': len(branches)})
    return {'roots': roots, 'unresolved_contacts': contacts, 'nonisolated_intervals': nonisolated}


def branch_atlas(powers, derivatives, evaluate):
    turns, unresolved = stationary_points(powers, derivatives, evaluate)
    nodes = [float(powers[0])]+[turn['output_power'] for turn in turns]+[float(powers[-1])]
    boundaries = {}
    for target in (0., MAX_INPUT):
        section = section_roots(target, nodes, evaluate)
        boundaries[str(target)] = section
    cuts = sorted(set(nodes+[root['output_power'] for section in boundaries.values() for root in section['roots']]))
    branches = []
    for lower, upper in zip(cuts[:-1], cuts[1:]):
        midpoint = evaluate((lower+upper)/2)
        if 0 <= midpoint['input_power'] <= MAX_INPUT:
            branches.append({'output_interval': [lower, upper],
                'input_endpoints': [evaluate(lower)['input_power'], evaluate(upper)['input_power']],
                'input_derivative_at_midpoint': midpoint['input_derivative'], 'singleton': False})
    for power in cuts:
        if 0 <= evaluate(power)['input_power'] <= MAX_INPUT and not any(branch['output_interval'][0] <= power <= branch['output_interval'][1] for branch in branches):
            branches.append({'output_interval': [power, power], 'input_endpoints': [evaluate(power)['input_power']]*2,
                'input_derivative_at_midpoint': evaluate(power)['input_derivative'], 'singleton': True})
    branches.sort(key=lambda branch: branch['output_interval'])
    component = -1
    previous = None
    for branch in branches:
        if previous != branch['output_interval'][0]:
            component += 1
        branch['component_index'] = component
        previous = branch['output_interval'][1]
    for section in boundaries.values():
        for root in section['roots']:
            power = root['output_power']
            left_inside = any(lower < power <= upper for lower, upper in (branch['output_interval'] for branch in branches))
            right_inside = any(lower <= power < upper for lower, upper in (branch['output_interval'] for branch in branches))
            root['rectangle_event'] = 'entry' if right_inside and not left_inside else 'exit' if left_inside and not right_inside else 'contact'
    return {'turns': turns, 'nodes': nodes, 'branches': branches, 'component_count': component+1,
        'input_boundaries': boundaries,
        'output_boundaries': [{'output_power': power, **evaluate(power),
            'inside_rectangle': 0 <= evaluate(power)['input_power'] <= MAX_INPUT} for power in (float(powers[0]), float(powers[-1]))],
        'unresolved_stationary_candidates': unresolved}


def ordered_comparison(reference, candidate):
    reference, candidate = sorted(reference), sorted(candidate)
    return {'independent_count': len(reference), 'candidate_count': len(candidate),
        'count_matches': len(reference) == len(candidate),
        'max_power_difference': float(np.max(abs(np.asarray(reference)-candidate))) if reference and len(reference) == len(candidate) else None,
        'independent_output_powers': reference, 'candidate_output_powers': candidate}


def polyline_roots(powers, inputs, target):
    roots = [float(power) for power, value in zip(powers, inputs) if value == target]
    for lower, upper, first, second in zip(powers[:-1], powers[1:], inputs[:-1]-target, inputs[1:]-target):
        if first*second < 0:
            roots.append(float(lower-first*(upper-lower)/(second-first)))
    return sorted(roots)


def compare_candidate_atlas(atlas, evaluate, powers, inputs, rows, candidate_turns, coarse_evaluate=None):
    reference_turns = [turn for turn in atlas['turns'] if 0 <= turn['input_power'] <= MAX_INPUT]
    turns = [turn for turn in candidate_turns if 0 <= turn['input_intensity'] <= MAX_INPUT and 0 <= turn['output_intensity'] <= MAX_OUTPUT]
    reference_turns.sort(key=lambda turn: turn['output_power'])
    turns.sort(key=lambda turn: turn['output_intensity'])
    comparison = ordered_comparison([turn['output_power'] for turn in reference_turns], [turn['output_intensity'] for turn in turns])
    comparison['matched_turns'] = []
    if len(reference_turns) == len(turns):
        for independent, candidate in zip(reference_turns, turns):
            amplitude_bracket = candidate.get('amplitude_bracket')
            output_bracket = [value**2 for value in amplitude_bracket] if amplitude_bracket is not None else candidate.get('output_bracket')
            input_bracket = candidate.get('input_bracket')
            input_uncertainty = abs(coarse_evaluate(independent['output_power'])['input_power'] - independent['input_power']) if coarse_evaluate is not None else 0.
            output_uncertainty = max(ROOT_XTOL, independent['output_bracket'][1] - independent['output_bracket'][0])
            output_cap = NONLINEAR_TOLERANCE * (1 + abs(independent['output_power']))
            input_difference = candidate['input_intensity'] - independent['input_power']
            output_difference = candidate['output_intensity'] - independent['output_power']
            comparison['matched_turns'].append({'input_difference': candidate['input_intensity']-independent['input_power'],
                'candidate_output_bracket': output_bracket, 'candidate_input_bracket': input_bracket,
                'reference_input_uncertainty': input_uncertainty, 'reference_output_uncertainty': output_uncertainty,
                'output_bracket_contains_reference': bounded_interval_contains(output_bracket, independent['output_power'], output_cap, output_cap),
                'input_bracket_contains_reference': bounded_interval_contains(input_bracket, independent['input_power'], TURN_INPUT_TOLERANCE, TURN_INPUT_TOLERANCE),
                'candidate_stationary_residual': abs(evaluate(candidate['output_intensity'])['input_derivative']),
                'coordinates_pass': abs(input_difference) <= TURN_INPUT_TOLERANCE and abs(output_difference) <= output_cap,
                'bracket_comparison': 'Public bounded coordinate tolerance, not an assertion of rigorous uncertainty bounds'})
    comparison['passes'] = comparison['count_matches'] and all(
        turn['coordinates_pass'] and turn['output_bracket_contains_reference'] and turn['input_bracket_contains_reference']
        for turn in comparison['matched_turns'])
    critical = sorted(set([0., MAX_INPUT]+[turn['input_power'] for turn in reference_turns if 0 < turn['input_power'] < MAX_INPUT]))
    sections = {}
    for lower, upper in zip(critical[:-1], critical[1:]):
        target = (lower+upper)/2
        independent = section_roots(target, atlas['nodes'], evaluate)
        sections[str(target)] = ordered_comparison([root['output_power'] for root in independent['roots']], polyline_roots(powers, inputs, target))
        sections[str(target)]['candidate_representation'] = 'piecewise-linear retained continuation, not a fresh native root solve'
    boundaries = {level: ordered_comparison([root['output_power'] for root in section['roots']], polyline_roots(powers, inputs, float(level)))
                  for level, section in atlas['input_boundaries'].items()}
    connectivity = {}
    for branch_id in np.unique(rows[:, 1]):
        selected = rows[rows[:, 1] == branch_id]
        compatible = set(range(len(atlas['nodes'])-1))
        for row in selected:
            power = float(row[2]**2)
            compatible &= {index for index, (lower, upper) in enumerate(zip(atlas['nodes'][:-1], atlas['nodes'][1:]))
                           if lower <= power <= upper or any(abs(power - boundary) <= NONLINEAR_TOLERANCE * (1 + abs(boundary))
                               and abs(evaluate(power)['input_power'] - evaluate(boundary)['input_power']) <= TURN_INPUT_TOLERANCE
                               for boundary in (lower, upper))}
        connectivity[str(branch_id)] = {'row_count': len(selected), 'compatible_independent_segments': sorted(compatible),
            'limitation': 'Only bounded endpoint shifts are accepted; branch counts and connectivity remain separate requirements'}
    uncovered = [branch['output_interval'] for branch in atlas['branches']
                 if branch['output_interval'][0] < powers[0] or branch['output_interval'][1] > powers[-1]]
    return {'turn_comparison': comparison, 'interior_section_comparisons': sections, 'boundary_comparisons': boundaries,
        'candidate_branch_connectivity': connectivity, 'independent_intervals_outside_candidate_extent': uncovered,
        'candidate_atlas_basis': 'declared turns, retained continuation and root-table branch IDs; branch names are not matched'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-output', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output.resolve().is_relative_to(arguments.candidate_output.resolve()):
        raise ValueError('Independent reference output cannot alter candidate evidence')
    arguments.output.mkdir(parents=True, exist_ok=False)
    summary = {'status': 'independent_stokes_comparison_not_global_uniqueness_proof', 'task_id': '05',
        'method': 'Independent real Stokes IVP and dS/dIout variational equations; no candidate source imported',
        'cases': {}, 'candidate_artifacts': {}, 'complete': False,
        'grid_sizes': list(GRID_SIZES), 'root_xtol': ROOT_XTOL, 'section_identity_atol': SECTION_ATOL,
        'coverage_kind': 'numerical grid/integration refinement, not a rigorous global proof'}
    summary['trusted_replay_sha256'] = hashlib.sha256((arguments.candidate_output.parent / 'trusted_replay.json').read_bytes()).hexdigest()
    evidence = Evidence(arguments.candidate_output)
    candidate_summary = {}
    try:
        candidate_summary = evidence.record('nonlinear/summary', 'results/paper/nonlinear/summary.json')
    except EvidenceMissing:
        pass
    for imaginary in (0.3, 0.5, 0.8):
        gain = imaginary / 2
        for side in ('left', 'right'):
            label = f'n2_{str(imaginary).replace(".", "p")}_{side}'
            relative = f'results/paper/nonlinear/{label}'
            try:
                archive = evidence.observation(f'nonlinear/{label}/continuation', relative + '/continuation.npz', axis='output_intensity')
                candidate_roots = evidence.observation(f'nonlinear/{label}/roots', relative + '/matched_input_roots.csv', table=True)
            except EvidenceMissing:
                summary.setdefault('missing_cases', []).append(label)
                continue
            all_powers = archive['output_intensity'].copy()
            all_input = archive['input_intensity'].copy()
            if (all_powers.ndim != 1 or all_input.shape != all_powers.shape or len(all_powers) < 2
                    or not np.isfinite(all_powers).all() or not np.isfinite(all_input).all()
                    or np.any(np.diff(all_powers) <= 0)):
                raise ValueError('Candidate continuation must have finite, strictly increasing output powers')
            sample_count = len(all_powers)
            indices = np.unique(np.rint(np.linspace(0, sample_count - 1, min(257, sample_count))).astype(int))
            powers = all_powers[indices]
            candidate_incident = all_input[indices]
            candidate_reflected = archive['reflected_intensity'][indices]
            candidate_derivative = archive['input_derivative_amplitude'][indices] if 'input_derivative_amplitude' in archive else None
            coarse = solve_variational(powers, gain, side, False)
            refined = solve_variational(powers, gain, side, True)
            scans = []
            for count in GRID_SIZES:
                power_grid = np.linspace(0, MAX_OUTPUT, count)
                grid = solve_variational(power_grid, gain, side, True)
                evaluate = evaluator(gain, side, True, power_grid, grid)
                scans.append((power_grid, grid, evaluate, branch_atlas(power_grid, grid['input_derivative'], evaluate)))
            coarse_grid, coarse_values, coarse_evaluate, coarse_atlas = scans[0]
            power_grid, grid, evaluate, atlas = scans[1]
            loose_evaluate = evaluator(gain, side, False)
            roots = {}
            sections, root_refinement = {}, {}
            for target in (0.2, 0.8, 1.6, 3.2):
                section = section_roots(target, atlas['nodes'], evaluate)
                sections[str(target)] = section
                roots[str(target)] = section['roots']
                lower_resolution = section_roots(target, coarse_atlas['nodes'], coarse_evaluate)
                lower_accuracy = section_roots(target, atlas['nodes'], loose_evaluate)
                fine_powers = [root['output_power'] for root in section['roots']]
                root_refinement[str(target)] = {
                    'grid': ordered_comparison(fine_powers, [root['output_power'] for root in lower_resolution['roots']]),
                    'integration': ordered_comparison(fine_powers, [root['output_power'] for root in lower_accuracy['roots']])}
                if len(section['roots']) == len(lower_accuracy['roots']) and section['roots']:
                    root_refinement[str(target)]['normalized_T_R_integration_changes'] = {
                        key: max(abs(first[key]-second[key])/(1+abs(first[key]))
                            for first, second in zip(section['roots'], lower_accuracy['roots'])) for key in ('T', 'R')}
            if candidate_roots.shape[1] < 6 or not np.isfinite(candidate_roots).all():
                raise ValueError('Malformed candidate root table')
            root_comparisons = {}
            for target, reference in roots.items():
                selected = candidate_roots[np.isclose(candidate_roots[:, 0], float(target), atol=SECTION_ATOL, rtol=0)]
                independent_power = sorted(item['output_power'] for item in reference)
                candidate_power = sorted(selected[:, 2] ** 2)
                root_comparisons[target] = ordered_comparison(independent_power, candidate_power)
                root_comparisons[target]['acceptance'] = root_set_comparison(reference, selected, float(target), evaluate)
            turn_refinement = []
            for turn in atlas['turns']:
                lower, upper = turn['initial_output_bracket']
                first, second = loose_evaluate(lower)['input_derivative'], loose_evaluate(upper)['input_derivative']
                if first*second <= 0:
                    root = brentq(lambda power: loose_evaluate(power)['input_derivative'], lower, upper, xtol=ROOT_XTOL) if lower != upper else lower
                    turn_refinement.append({'tight_output_power': turn['output_power'], 'coarse_output_power': float(root),
                        'input_change': abs(loose_evaluate(root)['input_power']-turn['input_power']),
                        'coarse_derivative_residual': loose_evaluate(root)['input_derivative']})
                else:
                    turn_refinement.append({'tight_output_power': turn['output_power'], 'status': 'coarse integration does not bracket this stationary point'})
            grid_turn_comparison = ordered_comparison([turn['output_power'] for turn in atlas['turns']],
                                                     [turn['output_power'] for turn in coarse_atlas['turns']])
            if len(atlas['turns']) == len(coarse_atlas['turns']):
                grid_turn_comparison['max_input_difference'] = max((abs(first['input_power']-second['input_power'])
                    for first, second in zip(atlas['turns'], coarse_atlas['turns'])), default=0.)
            candidate_case = candidate_summary.get('cases', {}).get(label, {})
            atlas_comparison = compare_candidate_atlas(atlas, evaluate, all_powers, all_input, candidate_roots, candidate_case.get('turns', []), loose_evaluate)
            atlas_comparison['candidate_turn_records_available'] = 'turns' in candidate_case
            derivative_difference = None
            if candidate_derivative is not None:
                positive = powers > 0
                derivative_difference = float(np.max(abs(candidate_derivative[positive]/(2*np.sqrt(powers[positive]))-refined['input_derivative'][positive])))
            summary['cases'][label] = {
                'candidate_artifacts': {**evidence.observation_artifacts[f'nonlinear/{label}/continuation'],
                    **evidence.observation_artifacts[f'nonlinear/{label}/roots']},
                'sample_count': len(powers), 'independent_integration_input_change': float(np.max(abs(refined['input_power']-coarse['input_power']))),
                'independent_integration_reflection_change': float(np.max(abs(refined['reflected_power']-coarse['reflected_power']))),
                'candidate_input_max_difference': float(np.max(abs(refined['input_power']-candidate_incident))),
                'candidate_reflection_max_difference': float(np.max(abs(refined['reflected_power']-candidate_reflected))),
                'candidate_input_derivative_max_difference': derivative_difference,
                'root_comparisons': root_comparisons, 'fixed_section_roots': roots,
                'fixed_section_topology': sections, 'root_refinement': root_refinement,
                'independent_atlas': atlas, 'candidate_atlas_comparison': atlas_comparison,
                'grid_turn_comparison': grid_turn_comparison, 'turn_integration_refinement': turn_refinement,
                'coarse_grid_atlas': coarse_atlas,
                'boundary_grid_comparisons': {level: ordered_comparison([root['output_power'] for root in section['roots']],
                    [root['output_power'] for root in coarse_atlas['input_boundaries'][level]['roots']])
                    for level, section in atlas['input_boundaries'].items()},
                'minimum_scanned_input_power': float(np.min(grid['input_power'])),
                'minimum_scanned_reflected_power': float(np.min(grid['reflected_power'])),
                'zero_input_limit': {'T': 1/grid['input_derivative'][0] if grid['input_derivative'][0] else None,
                    'R': grid['reflection_derivative'][0]/grid['input_derivative'][0] if grid['input_derivative'][0] else None},
                'coverage_limit': '2049/4097-node variational stationary-point search, monotone-segment roots, rectangle boundaries and atlas comparison. Tangency uncertainty is retained; sub-grid stationary pairs and global completeness are not rigorously excluded.'}
            np.savez_compressed(arguments.output / (label + '.npz'), output_power=power_grid, **grid,
                coarse_output_power=coarse_grid, **{'coarse_'+key: value for key, value in coarse_values.items()})
            (arguments.output / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
            print(label, summary['cases'][label]['candidate_input_max_difference'], flush=True)
    summary['candidate_artifacts'].update(evidence.artifacts)
    from linear_reference05 import calibrate
    try:
        linear = calibrate(arguments.candidate_output, arguments.output / 'linear')
    except FileNotFoundError as error:
        linear = {'paper': {}, 'candidate_artifacts': {}, 'missing_evidence': str(error)}
    summary['linear'] = linear
    summary['candidate_artifacts'].update(linear['candidate_artifacts'])
    summary['complete'] = len(summary['cases']) == 6
    (arguments.output / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
