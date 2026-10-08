from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from collections import Counter

import numpy as np
import pandas as pd
from scipy.stats import beta

from evidence_adapter import AdapterRequired, Evidence, safe_path
from independent_numeric import eligible_omissions, independent_study, load_counts, pearson_rows


def read_json(path):
    return json.loads(path.read_text())


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def optional_evidence(evidence, label, suffixes, directory=None, any_of=(), required=()):
    try:
        return evidence.find(label, suffixes, directory, any_of=any_of, required=required)
    except FileNotFoundError:
        return None


def number_value(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def numeric_credit(actual, expected, policy):
    actual, expected = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    if actual.shape != expected.shape or not expected.size:
        return 0.0
    valid = np.isfinite(actual) & np.isfinite(expected)
    coverage = float(valid.sum() / expected.size)
    if not valid.any():
        return 0.0
    actual, expected = actual[valid], expected[valid]
    if np.allclose(actual, expected, rtol=1e-8, atol=1e-10):
        return coverage
    scale = float(np.std(expected))
    if actual.size < 2 or scale == 0:
        return 0.0
    correlation = float(np.corrcoef(actual, expected)[0, 1]) if np.std(actual) > 0 else -1.0
    error = float(np.sqrt(np.mean((actual - expected) ** 2)) / scale)
    correlation_knots = np.asarray(policy['curves']['correlation'])
    error_knots = np.asarray(policy['curves']['nrmse'])
    agreement = policy['agreement']
    return coverage * float(
        agreement['correlation_weight'] * np.interp(correlation, *correlation_knots.T)
        + agreement['nrmse_weight'] * np.interp(error, *error_knots.T))


class Scores:
    def __init__(self, policy):
        self.policy = policy
        self.checks = {}

    def add(self, leaf, label, score, details=None):
        if not np.isfinite(score) or not 0 <= score <= 1:
            raise ValueError('Invalid component credit')
        self.checks.setdefault(leaf, []).append(
            {'check': label, 'fraction': float(score), 'details': details})

    def exact(self, leaf, label, condition, details=None):
        self.add(leaf, label, float(bool(condition)), details)

    def numeric(self, leaf, label, actual, expected, scale=1.0):
        self.add(leaf, label, numeric_credit(actual, expected, self.policy) * scale)

    def result(self):
        return {leaf: {'fraction': float(np.mean([item['fraction'] for item in checks])),
                       'checks': checks} for leaf, checks in self.checks.items()}

    def section(self, slots, label, operation):
        checked = Scores(self.policy)
        try:
            operation(checked)
        except AdapterRequired:
            raise
        except (FileNotFoundError, ValueError, KeyError, IndexError) as error:
            if str(error) == 'Invalid component credit':
                raise
            for leaf, count in slots.items():
                for position in range(count):
                    self.add(leaf, label + ':missing_evidence:' + str(position), 0,
                             {'reason': str(error), 'status': 'candidate_missing'})
            return False
        if {leaf: len(checks) for leaf, checks in checked.checks.items()} != slots:
            raise RuntimeError('Scientific check slots differ from the fixed assessment plan: ' + label)
        for leaf, checks in checked.checks.items():
            self.checks.setdefault(leaf, []).extend(checks)
        return True


def phase_slots(guide_leaf, fit_leaf, gene_leaf, phase, full_tables=False):
    slots = Counter({gene_leaf: 5})
    slots[guide_leaf] += 1
    slots[fit_leaf] += 8
    if full_tables:
        slots[gene_leaf] += 4
        slots['C1d' if phase == 'combined' else gene_leaf] += 1
    return dict(slots)


def check_phase(scores, evidence, reference, phase, guide_leaf, fit_leaf, gene_leaf, run_id=None, full_tables=False):
    directory = evidence.phase_root(phase, run_id)
    label = f'{run_id or "baseline"}:{phase}'
    arrays = evidence.arrays(directory, reference)
    size = len(reference['gene_ids'])
    upper = np.triu_indices(size, 1)
    off_diagonal = ~np.eye(size, dtype=bool)
    expected_ids = set(reference['gene_ids'].astype(str))
    candidate_ids = set(arrays.get('candidate_gene_ids', expected_ids))
    axis_scale = (len(expected_ids & candidate_ids) / len(expected_ids | candidate_ids)
                  if candidate_ids else 0.0)
    for field in ['profile_matrix', 'observed_double', 'expected_double', 'uncertainty']:
        scores.numeric(gene_leaf, label + ':' + field,
                       arrays[field][off_diagonal], reference[field][off_diagonal], axis_scale)
    scores.exact(gene_leaf, label + ':guide_count', np.array_equal(arrays['guide_count'], reference['guide_count']))
    actual_ids, observations = evidence.guide_observations(directory)
    if len(actual_ids) != len(set(actual_ids)):
        raise ValueError(label + ': duplicated guide identities')
    guide_expected = set(reference['guide_ids'].astype(str))
    guide_measured = set(actual_ids.astype(str))
    guide_scale = (len(guide_expected & guide_measured) / len(guide_expected | guide_measured)
                   if guide_measured else 0.0)
    order = pd.Index(actual_ids).get_indexer(reference['guide_ids'])
    present = order >= 0
    measured = np.full((len(reference['guide_ids']), len(reference['guide_ids'])), np.nan)
    measured[np.ix_(present, present)] = observations[np.ix_(order[present], order[present])]
    scores.numeric(guide_leaf, label + ':count_derived_measurements', measured,
                   reference['guide_observed'], guide_scale)
    fits = evidence.fits(directory)
    for orientation, expected in zip(['variable_A_query_B', 'variable_B_query_A'], reference['directions']):
        subset = fits[fits['orientation'] == orientation].set_index('query_guide_id')
        if not subset.index.is_unique:
            raise ValueError(label + ': fitted query identities are not unique')
        subset = subset.reindex(reference['guide_ids'])
        for column, expected_values in [('quadratic', expected['coefficients'][0]),
                                        ('linear', expected['coefficients'][1]),
                                        ('intercept', expected['intercepts']),
                                        ('negative_residual_sample_sd', expected['scale'])]:
            actual = subset[column] if column in subset.columns else pd.Series(
                np.nan, index=subset.index, dtype=float)
            scores.numeric(fit_leaf, label + ':' + orientation + ':' + column, actual, expected_values, guide_scale)
    if full_tables:
        pairs = pd.read_csv(evidence.find('gene_pairs', ('.csv', '.gz'), directory, ('gene_a', 'gene_b')))
        identities = [tuple(sorted(str(value) for value in pair))
                      for pair in pairs[['gene_a', 'gene_b']].itertuples(index=False, name=None)]
        if len(set(identities)) != len(identities):
            raise ValueError(label + ': duplicated pair identities')
        expected_pairs = [(str(first), str(second))
                          for first, second in zip(reference['gene_ids'][upper[0]], reference['gene_ids'][upper[1]])]
        positions = {identity: position for position, identity in enumerate(identities)}
        pair_scale = (len(set(identities) & set(expected_pairs)) / len(set(identities) | set(expected_pairs))
                      if identities else 0.0)
        for column, field in [('observed_double', 'observed_double'), ('expected_double', 'expected_double'),
                              ('gi_score', 'profile_matrix'), ('uncertainty', 'uncertainty')]:
            actual = np.full(len(expected_pairs), np.nan)
            if column in pairs.columns:
                values = pd.to_numeric(pairs[column], errors='coerce').to_numpy()
                for index, identity in enumerate(expected_pairs):
                    position = positions.get(identity)
                    if position is not None:
                        actual[index] = values[position]
            scores.numeric(gene_leaf, label + ':pair_table:' + column, actual, reference[field][upper], pair_scale)
        scores.numeric('C1d' if phase == 'combined' else gene_leaf, label + ':profiles',
                       arrays['profile_matrix'][off_diagonal], reference['profile_matrix'][off_diagonal], axis_scale)
    return arrays


def scalar_statistics(first, second):
    difference = second - first
    scale = float(np.linalg.norm(first))
    return {'comparison_count': len(first), 'pearson': float(np.corrcoef(first, second)[0, 1]),
            'rmse': float(np.sqrt(np.mean(difference ** 2))),
            'relative_l2': float(np.linalg.norm(difference) / scale) if scale else None,
            'sign_change_count': int(np.count_nonzero(np.sign(first) != np.sign(second)))}


def check_statistics(scores, leaf, label, row, expected):
    for field, value in expected.items():
        actual = row.get(field)
        number = number_value(actual)
        if value is None:
            valid = number is not None and np.isnan(number) and bool(row.get('undefined_reason', ''))
        elif field.endswith('count'):
            valid = number is not None and number == value
        else:
            valid = number is not None and np.isfinite(number) and np.isclose(number, value, rtol=1e-8, atol=1e-10)
        scores.exact(leaf, label + ':' + field, valid,
                     {'expected': value, 'actual': number})


def aligned_reference(baseline):
    genes = np.array(sorted(set(baseline['rep1']['gene_ids']) & set(baseline['rep2']['gene_ids'])))
    matrices = []
    for phase in ['rep1', 'rep2']:
        order = pd.Index(baseline[phase]['gene_ids']).get_indexer(genes)
        matrices.append(baseline[phase]['profile_matrix'][order][:, order])
    return genes, *matrices


def check_replication(scores, evidence, baseline):
    genes, first, second = aligned_reference(baseline)
    upper = np.triu_indices(len(genes), 1)
    comparisons = evidence.replication()
    profiles_first, profiles_second = pearson_rows(first, first), pearson_rows(second, second)
    for leaf, name, first_values, second_values in [
        ('C2b', 'figure2D_gene_pair_GI', first[upper], second[upper]),
        ('C2c', 'figure2E_gene_profile_correlations', profiles_first[upper], profiles_second[upper])]:
        subset = comparisons[comparisons['comparison'] == name]
        if len(subset) != 1:
            raise ValueError('Missing or duplicate named replicate comparison: ' + name)
        check_statistics(scores, leaf, name, subset.iloc[0], scalar_statistics(first_values, second_values))
    per_gene = comparisons[comparisons['comparison'] == 'same_gene_cross_replicate_partner_profile'].set_index('entity_id')
    scores.exact('C2d', 'all_common_genes', per_gene.index.is_unique and set(per_gene.index) == set(genes))
    for position, gene in enumerate(genes):
        if gene not in per_gene.index:
            for field in scalar_statistics(first[position], second[position]):
                scores.add('C2d', str(gene) + ':' + field, 0, {'status': 'candidate_missing'})
            continue
        partners = np.arange(len(genes)) != position
        check_statistics(scores, 'C2d', str(gene), per_gene.loc[gene],
                         scalar_statistics(first[position, partners], second[position, partners]))
    return genes, first, second


def check_local(scores, evidence, baseline, perturbed, row, all_statistics):
    run_id, gene = row['run_id'], row['gene_id']
    directory = evidence.run_root(run_id)
    values = evidence.local_values(directory)
    for phase in ['rep1', 'rep2', 'combined']:
        before, after = baseline[phase], perturbed[phase]
        partners = sorted((set(before['gene_ids']) & set(after['gene_ids'])) - {gene})
        subset = values[values['phase'] == phase].set_index('partner_id')
        if not subset.index.is_unique:
            raise ValueError(run_id + ': repeated focal partner evidence')
        declared_partners = set(subset.index.astype(str))
        wanted_partners = set(str(partner) for partner in partners)
        partner_scale = (len(declared_partners & wanted_partners) / len(declared_partners | wanted_partners)
                         if declared_partners else 0.0)
        subset = subset.reindex(partners)
        before_row = pd.Index(before['gene_ids']).get_loc(gene)
        after_row = pd.Index(after['gene_ids']).get_loc(gene)
        first = before['profile_matrix'][before_row, pd.Index(before['gene_ids']).get_indexer(partners)]
        second = after['profile_matrix'][after_row, pd.Index(after['gene_ids']).get_indexer(partners)]
        scores.numeric('C3c', run_id + ':' + phase + ':baseline_values', subset['baseline_gi'], first,
                       partner_scale)
        scores.numeric('C3c', run_id + ':' + phase + ':perturbed_values', subset['perturbed_gi'], second,
                       partner_scale)
        statistics = all_statistics[(all_statistics['run_id'] == run_id) & (all_statistics['phase'] == phase)]
        if len(statistics) != 1:
            raise ValueError(run_id + ': missing or repeated local summary')
        expected = scalar_statistics(first, second)
        expected['baseline_partner_count'] = len(before['gene_ids']) - 1
        expected['coverage_fraction'] = len(partners) / expected['baseline_partner_count']
        check_statistics(scores, 'C3c', run_id + ':' + phase, statistics.iloc[0], expected)


def check_normalization(scores, evidence, guide_ids, raw, phase, omitted=None, run_id=None):
    directory = evidence.phase_root(phase, run_id)
    keep = guide_ids != omitted if omitted is not None else np.ones(len(guide_ids), dtype=bool)
    guide_axis = guide_ids[keep]
    start, end = (values[keep][:, keep] for values in raw[phase])
    median_a, median_b = np.median(end, axis=1), np.median(end, axis=0)
    retained = (median_a >= 35) & (median_b >= 35)
    qc = evidence.filtering(directory, omitted).set_index('guide_id')
    if not qc.index.is_unique or set(qc.index) != set(guide_axis):
        raise ValueError('Filtering ledger lacks input guide identities')
    qc = qc.loc[guide_axis]
    label = f'{run_id or "baseline"}:{phase}:filtering'
    scores.exact('B3', label + ':decisions', np.array_equal(qc['retained'], retained))
    scores.numeric('B3', label + ':median_a', qc['median_endpoint_a'], median_a)
    scores.numeric('B3', label + ':median_b', qc['median_endpoint_b'], median_b)
    normalization = evidence.normalization(directory, phase)
    selected_start, selected_end = start[retained][:, retained] + 10, end[retained][:, retained] + 10
    control = np.array([guide.startswith('negative_') for guide in guide_axis[retained]])
    ratio = np.log2((selected_end / selected_end.sum()) / (selected_start / selected_start.sum()))
    expected = {'input_guide_count': len(guide_axis), 'input_construct_count': start.size,
                'retained_guide_count': int(retained.sum()), 'retained_construct_count': selected_start.size,
                'initial_pseudocount_total': float(selected_start.sum()),
                'endpoint_pseudocount_total': float(selected_end.sum()),
                'negative_center': float(np.median(ratio[control][:, control])),
                'population_doublings': 6.91 if phase == 'rep1' else 7.61}
    check_statistics(scores, 'B3', label + ':normalization', normalization, expected)


def check_lineage(scores, evidence, phase, expected_hashes, omitted=None, run_id=None):
    directory = evidence.phase_root(phase, run_id)
    label = f'{run_id or "baseline"}:{phase}:lineage'
    if evidence.compact:
        scores.exact('B3', label + ':inputs', evidence.input_hashes() == expected_hashes)
        records = [evidence.normalization(evidence.phase_root(replicate, run_id), replicate)
                   for replicate in (['rep1', 'rep2'] if phase == 'combined' else [phase])]
        declared = [record.get('omitted_guide') if isinstance(record, dict) else None for record in records]
        if run_id is not None:
            lineage_path = evidence.find('lineage', ('.json',), evidence.run_root(run_id),
                                         ('omitted_guide', 'run_id'))
            lineage = read_json(lineage_path)
            intervention = lineage.get('intervention') if isinstance(lineage, dict) else None
            bound = intervention.get('guide_id') if isinstance(intervention, dict) else None
            bound = bound or (lineage.get('omitted_guide') if isinstance(lineage, dict) else None)
            declared.append(bound if lineage.get('run_id') == run_id else None)
        if omitted is None:
            omission_bound = all(value is None for value in declared)
        else:
            omission_bound = (any(value == omitted for value in declared)
                              and all(value in (None, omitted) for value in declared))
        scores.exact('B3', label + ':omitted_guide', omission_bound)
        axes = evidence.index.arrays(evidence.guide_matrix_path(directory))
        actual_ids, measured = evidence.guide_observations(directory)
        diagnostics_path = optional_evidence(evidence, 'fit_diagnostics', ('.json',), directory,
                                            ('symmetric_gamma_sha256', 'fit_parameters_sha256'))
        diagnostics = read_json(diagnostics_path) if diagnostics_path is not None else {}
        measured_hash = hashlib.sha256(np.ascontiguousarray(measured).tobytes()).hexdigest()
        scores.exact('B3', label + ':normalized_measurement_binding',
                     diagnostics.get('symmetric_gamma_sha256') == measured_hash)
        fits = evidence.fits(directory)
        parameters = fits[['quadratic', 'linear', 'negative_residual_sample_sd']].to_numpy()
        scores.exact('B3', label + ':query_fit_binding', diagnostics.get('fit_parameters_sha256') ==
                     hashlib.sha256(np.ascontiguousarray(parameters).tobytes()).hexdigest())
        scores.exact('B3', label + ':identity_binding', np.array_equal(actual_ids, fits['guide_id'])
                     and np.array_equal(axes['guide_ids'], actual_ids) and omitted not in actual_ids)
        return
    record = read_json(evidence.find('lineage', ('.json',), directory, ('omitted_guide', 'run_id')))
    scores.exact('B3', label + ':inputs', record.get('input_sha256') == expected_hashes)
    scores.exact('B3', label + ':omitted_guide', record.get('omitted_guide') == omitted)
    for key, path in [('gene_arrays_sha256', evidence.gene_matrix_path(directory)),
                      ('guide_state_sha256', evidence.guide_matrix_path(directory)),
                      ('query_fit_sha256', evidence.find('query_fits', ('.csv', '.gz'), directory,
                                                         ('quadratic', 'linear')))]:
        scores.exact('B3', label + ':' + key, record.get(key) == digest(path))


def check_null(scores, evidence, baseline, conventions):
    genes, first, second = aligned_reference(baseline)
    correlation = pearson_rows(first, second)
    mappings, statistics, summary = evidence.null_evidence()
    seed = conventions['benchmark_controls']['identity_matching_seed']
    minimum = conventions['benchmark_controls']['minimum_matching_permutations']
    observed_values = np.diag(correlation)
    observed = float(np.nanmedian(observed_values))
    observed_rows = statistics[statistics['kind'] == 'observed']
    if len(observed_rows) != 1:
        raise ValueError('Expected one observed null statistic')
    check_statistics(scores, 'C4b', 'observed', observed_rows.iloc[0],
                     {'statistic': observed, 'finite_gene_count': int(np.isfinite(observed_values).sum())})
    permutations = list(mappings.groupby('permutation_id', sort=True))
    scores.exact('C4a', 'required_matching_count', len(permutations) >= minimum)
    scores.exact('C4a', 'declared_seed', set(statistics['seed']) == {seed} and summary.get('seed') == seed)
    values = []
    for permutation, mapping in permutations:
        label = f'permutation:{permutation}'
        bijective = (len(mapping) == len(genes) and set(mapping['replicate1_gene']) == set(genes)
                     and set(mapping['replicate2_gene']) == set(genes))
        scores.exact('C4a', label + ':bijection', bijective)
        if not bijective:
            raise ValueError('Identity permutation is not a bijection')
        first_order = pd.Index(genes).get_indexer(mapping['replicate1_gene'])
        second_order = pd.Index(genes).get_indexer(mapping['replicate2_gene'])
        expected = correlation[first_order, second_order]
        scores.numeric('C4a', label + ':partner_identity_values', mapping['profile_pearson'], expected)
        scores.exact('C4a', label + ':self_exclusions',
                     np.array_equal(mapping['partner_count'], len(genes) - 2 + (first_order == second_order)))
        matched = statistics[(statistics['kind'] == 'randomized') & (statistics['permutation_id'] == permutation)]
        if len(matched) != 1:
            raise ValueError('Missing or duplicated randomized statistic')
        value = float(np.nanmedian(expected))
        check_statistics(scores, 'C4b', label, matched.iloc[0],
                         {'statistic': value, 'finite_gene_count': int(np.isfinite(expected).sum())})
        values.append(value)
    scores.exact('C4b', 'no_omitted_or_extra_statistics', len(statistics) == len(values) + 1)
    values = np.asarray(values)
    exceedances = int(np.count_nonzero(values >= observed))
    lower = 0.0 if exceedances == 0 else float(beta.ppf(0.025, exceedances, len(values) - exceedances + 1))
    upper = 1.0 if exceedances == len(values) else float(beta.ppf(0.975, exceedances + 1, len(values) - exceedances))
    expected = {'observed_median_profile_pearson': observed, 'randomized_matchings': len(values),
                'defined_randomized_matchings': len(values), 'null_median': float(np.median(values)),
                'upper_tail_exceedances': exceedances,
                'upper_tail_plus_one_probability': (exceedances + 1) / (len(values) + 1),
                'biological_replicates': 2}
    check_statistics(scores, 'C4b', 'distribution_summary', summary, expected)
    scores.numeric('C4b', 'empirical_quantiles', summary['null_quantiles_025_975'], np.quantile(values, [0.025, 0.975]))
    scores.numeric('C4b', 'monte_carlo_interval', summary['monte_carlo_exceedance_probability_95_interval'], [lower, upper])


def grade(arguments):
    evidence = Evidence(arguments.evidence)
    scores = Scores(read_json(arguments.policy)['numerical_policy'])
    receipt = read_json(arguments.receipts / 'integrity.json')
    native = read_json(arguments.receipts / 'native_run.json')
    scores.exact('B1', 'trusted_clean_offline_replay',
                 receipt['frozen_source_matches'] and receipt['empty_initial_results']
                 and native['native_exit_code'] == 0 and native['network'] == 'none'
                 and native['read_only_source'] and native['native_wall_seconds'] <= native['timeout_seconds'])
    conventions = read_json(arguments.paper / 'conventions.json')
    input_manifest = read_json(arguments.paper / 'data_manifest.json')
    expected_hashes = {item['name']: digest(arguments.data / item['name']) for item in input_manifest['inputs']}
    if any(expected_hashes[item['name']] != item['sha256'] for item in input_manifest['inputs']):
        raise RuntimeError('Trusted input provisioning mismatch')
    provenance = evidence.provenance()
    scores.exact('B2', 'input_byte_binding', evidence.input_hashes() == expected_hashes)
    submitted = receipt['submission_source_sha256']
    declared_source = provenance['source_sha256']
    authored = {path: value for path, value in submitted.items() if Path(path).suffix.lower() in {'.py', '.sh'}}
    scores.exact('B2', 'source_byte_binding',
                 all(submitted.get(path) == value for path, value in declared_source.items())
                 and all(declared_source.get(path) == value for path, value in authored.items()))
    scores.exact('B2', 'paper_byte_binding', provenance['paper_sha256'] == digest(arguments.paper / 'paper.md'))
    scores.exact('B2', 'conventions_byte_binding', provenance['conventions_sha256'] == digest(arguments.paper / 'conventions.json'))
    execution = evidence.execution()
    scores.exact('B2', 'real_completion', execution['process_completed'] and execution['protocol_complete']
                 and not execution['unhandled_exceptions'])
    resources = evidence.resources()
    scores.exact('B2', 'measured_resources', 0 < resources['wall_clock_seconds'] <= native['native_wall_seconds']
                 and 0 < resources['peak_rss_bytes'] < native['memory_bytes'])
    guide_ids, raw = load_counts(arguments.data)
    baseline = independent_study(guide_ids, raw)
    for phase in ['rep1', 'rep2', 'combined']:
        leaves = ('C1a', 'C1b', 'C1c') if phase == 'combined' else ('C2a', 'C2a', 'C2a')
        scores.section(phase_slots(*leaves, phase, full_tables=True),
                       phase, lambda checked: check_phase(
                           checked, evidence, baseline[phase], phase, *leaves, full_tables=True))
        scores.section({'B3': 5}, phase + ':lineage', lambda checked: check_lineage(
            checked, evidence, phase, expected_hashes))
        if phase != 'combined':
            scores.section({'B3': 11}, phase + ':normalization', lambda checked: check_normalization(
                checked, evidence, guide_ids, raw, phase))
    common_genes = len(aligned_reference(baseline)[0])
    scores.section({'C2b': 5, 'C2c': 5, 'C2d': 1 + 5 * common_genes}, 'replication',
                   lambda checked: check_replication(checked, evidence, baseline))
    required = eligible_omissions(baseline)
    inventory = evidence.omission_inventory()
    attempts = evidence.attempts()
    actual_inventory = sorted(inventory[['gene_id', 'guide_id']].itertuples(index=False, name=None))
    actual_attempts = sorted(attempts[['gene_id', 'guide_id']].itertuples(index=False, name=None))
    scores.exact('C3a', 'eligible_inventory', actual_inventory == sorted(required))
    required_set = set(required)
    counts = Counter(actual_attempts)
    valid_rows = [row for row in attempts.to_dict('records')
                  if (row['gene_id'], row['guide_id']) in required_set
                  and counts[(row['gene_id'], row['guide_id'])] == 1]
    if not attempts['run_id'].is_unique:
        raise ValueError('Duplicate intervention run identities')
    attempted = {(row['gene_id'], row['guide_id']) for row in valid_rows}
    scores.add('C3a', 'tested_inventory', len(attempted) / len(required) if required else 1,
               {'attempted': len(attempted), 'required': len(required)})
    scores.exact('C3a', 'unique_runs', attempts['run_id'].is_unique
                 and set(attempts['run_id']) == set(evidence.interventions)
                 and len(valid_rows) == len(attempts))
    rows_by_identity = {(row['gene_id'], row['guide_id']): row for row in valid_rows}
    completed = 0
    declared_completed = 0
    recomputed = 0
    for index, identity in enumerate(required):
        row = rows_by_identity.get(identity)
        if row is None:
            continue
        if row['run_id'] not in evidence.interventions:
            raise ValueError('Attempt has no declared intervention evidence')
        checked = Scores(scores.policy)
        checked.exact('C3b', row['run_id'] + ':completion', row['status'] == 'completed')
        if row['status'] != 'completed':
            continue
        declared_completed += 1
        reference = independent_study(guide_ids, raw, row['guide_id'])
        recomputed += 1
        evidence_complete = True
        for phase in ['rep1', 'rep2', 'combined']:
            phase_complete = checked.section(phase_slots('C3b', 'C3b', 'C3b', phase),
                row['run_id'] + ':' + phase, lambda section: check_phase(
                section, evidence, reference[phase], phase, 'C3b', 'C3b', 'C3b', run_id=row['run_id']))
            lineage_complete = checked.section({'B3': 5}, row['run_id'] + ':' + phase + ':lineage', lambda section: check_lineage(
                section, evidence, phase, expected_hashes, row['guide_id'], row['run_id']))
            evidence_complete = evidence_complete and phase_complete and lineage_complete
            if phase != 'combined':
                normalization_complete = checked.section({'B3': 11}, row['run_id'] + ':' + phase + ':normalization',
                                lambda section: check_normalization(
                                    section, evidence, guide_ids, raw, phase, row['guide_id'], row['run_id']))
                evidence_complete = evidence_complete and normalization_complete
        local_complete = checked.section({'C3c': 27}, row['run_id'] + ':local', lambda section: check_local(
            section, evidence, baseline, reference, row, evidence.local_statistics()))
        for leaf, checks in checked.checks.items():
            scores.checks.setdefault(leaf, []).extend(checks)
        completed += int(evidence_complete and local_complete)
        if (index + 1) % 25 == 0 or index + 1 == len(required):
            print(json.dumps({'scored_raw_omissions': index + 1, 'required': len(required)}), flush=True)
    try:
        permutations = len(evidence.null_evidence()[0].groupby('permutation_id'))
    except FileNotFoundError:
        permutations = conventions['benchmark_controls']['minimum_matching_permutations']
    scores.section({'C4a': 2 + 3 * permutations, 'C4b': 12 + 2 * permutations}, 'identity_null',
                   lambda checked: check_null(checked, evidence, baseline, conventions))
    results = scores.result()
    coverage = declared_completed / len(required) if required else 1.0
    for leaf in ('C3b', 'C3c'):
        if leaf not in results:
            results[leaf] = {'fraction': 0.0, 'checks': []}
        results[leaf]['fraction'] *= coverage
        results[leaf]['coverage'] = coverage
    return {'status': 'numeric_scored', 'leaves': results,
            'required_omissions': len(required), 'attempted_omissions': len(attempted),
            'declared_completed_omissions': declared_completed,
            'completed_omissions': completed, 'independently_recomputed_omissions': recomputed,
            'independently_recomputed_phases': 3 * (recomputed + 1),
            'evidence_adapter': 'declared-compact-v1' if evidence.compact else 'explicit-dense-v1'}


def main():
    parser = argparse.ArgumentParser()
    for argument in ['data', 'paper', 'evidence', 'receipts', 'policy', 'report']:
        parser.add_argument('--' + argument, required=True, type=Path)
    arguments = parser.parse_args()
    if arguments.report.exists():
        raise FileExistsError('Never overwrite an existing score attempt')
    started = time.monotonic()
    report = {'status': 'verifier_error', 'reward': None}
    try:
        report = grade(arguments)
    except Exception as error:
        report.update(error_type=type(error).__name__, error=str(error))
        raise
    finally:
        report['elapsed_seconds'] = time.monotonic() - started
        arguments.report.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
