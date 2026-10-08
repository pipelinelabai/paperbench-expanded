from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from evidence_index import EvidenceIndex, canonical


class AdapterRequired(RuntimeError):
    pass


def safe_path(root, relative):
    relative = Path(relative)
    path = root / relative
    if relative.is_absolute() or '..' in relative.parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Evidence path escapes its root')
    if any(part.is_symlink() for part in [path, *path.parents] if part.is_relative_to(root)):
        raise ValueError('Symlinked evidence is not allowed')
    return path


def renamed(record, aliases):
    if isinstance(record, pd.DataFrame):
        return record.rename(columns=aliases)
    return {aliases.get(key, key): value for key, value in record.items()}


PATH_KEYS = ('path', 'directory', 'dir', 'root', 'location', 'value', 'filename', 'file')


def path_value(value, label):
    """Unwrap a declared file/directory location to a relative path string.

    Candidates legitimately declare locations as a string, a one-element list, or
    a richer mapping that also carries the per-phase array schema. Only the
    location is taken here; no scientific content is inferred or substituted.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        for key in PATH_KEYS:
            if key in value:
                return path_value(value[key], label)
        raise TypeError(f'No declared location for {label}')
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return path_value(value[0], label)
    raise TypeError(f'Unsupported declared location for {label}')


FIELD_ALIASES = {
    'profile_matrix': ('profile_matrix', 'gi_score', 'genetic_interaction', 'interaction_score', 'gi', 'profile'),
    'observed_double': ('observed_double', 'observed', 'double', 'observed_gi'),
    'expected_double': ('expected_double', 'expected', 'expected_gi'),
    'uncertainty': ('uncertainty', 'uncertainty_sd', 'sd', 'sigma')}
GUIDE_FIELD_ALIASES = {
    'observed_double': ('observed_double', 'observed', 'double', 'guide_observed', 'measured'),
    'gi_score': ('gi_score', 'profile_matrix', 'gi', 'genetic_interaction')}
FIT_ALIASES = {
    'query_guide_id': ('query_guide_id', 'query_guide', 'guide_id', 'guide', 'guides'),
    'quadratic': ('quadratic', 'quadratic_a', 'quadratic_coefficient', 'a'),
    'linear': ('linear', 'linear_b', 'linear_coefficient', 'b'),
    'intercept': ('intercept', 'fixed_intercept', 'c'),
    'negative_residual_sample_sd': ('negative_residual_sample_sd', 'control_residual_sd', 'residual_sd', 'scale', 'sd')}
NORMALIZATION_ALIASES = {
    'input_guide_count': ('input_guide_count', 'raw_active_guides', 'guide_count', 'n_guides', 'input_guides'),
    'input_construct_count': ('input_construct_count', 'raw_active_constructs', 'construct_count', 'n_constructs',
                              'n_raw_constructs_remaining'),
    'retained_guide_count': ('retained_guide_count', 'retained_guides', 'n_retained_guides'),
    'retained_construct_count': ('retained_construct_count', 'retained_constructs', 'n_constructs_after_filter'),
    'initial_pseudocount_total': ('initial_pseudocount_total', 'pseudocounted_t0_total', 't0_total_with_pseudocount'),
    'endpoint_pseudocount_total': ('endpoint_pseudocount_total', 'pseudocounted_endpoint_total',
                                   'endpoint_total_with_pseudocount'),
    'negative_center': ('negative_center', 'control_log2_center', 'log2_center', 'control_center',
                        'control_median_log2_enrichment'),
    'population_doublings': ('population_doublings', 'doublings')}
FILTER_ALIASES = {
    'guide_id': ('guide_id', 'guide', 'guides'),
    'retained': ('retained', 'retained_flag', 'keep'),
    'median_endpoint_a': ('median_endpoint_A', 'median_endpoint_a', 'median_a'),
    'median_endpoint_b': ('median_endpoint_B', 'median_endpoint_b', 'median_b')}
LOCAL_VALUE_ALIASES = {
    'phase': ('phase', 'study', 'replicate'),
    'partner_id': ('partner_id', 'partner_gene', 'partner'),
    'baseline_gi': ('baseline_gi', 'baseline', 'before'),
    'perturbed_gi': ('perturbed_gi', 'perturbed', 'after')}
LOCAL_STATISTIC_ALIASES = {
    'run_id': ('run_id', 'intervention', 'omission'),
    'phase': ('phase', 'study', 'replicate'),
    'gene_id': ('gene_id', 'focal_gene', 'gene')}


def canonical_record(record, aliases):
    lookup = alias_lookup(aliases)
    return {lookup.get(canonical(key), key): value for key, value in record.items()}


def alias_lookup(aliases):
    return {canonical(option): target for target, options in aliases.items() for option in options}


def canonical_columns(record, aliases, keep=True):
    lookup = alias_lookup(aliases)
    mapping = {column: lookup[canonical(column)] for column in record.columns if canonical(column) in lookup}
    renamed_record = record.rename(columns=mapping)
    if keep:
        return renamed_record
    return renamed_record[[column for column in renamed_record.columns if column in set(lookup.values())]]


STATISTICS_ALIASES = {
    'comparison_count': ('comparison_count', 'n', 'n_common', 'n_pairs', 'comparisons'),
    'pearson': ('pearson', 'pearson_r', 'pearson_correlation'),
    'rmse': ('rmse',),
    'relative_l2': ('relative_l2', 'relative_l2_change', 'relative_rmse'),
    'sign_change_count': ('sign_change_count', 'sign_changes', 'n_sign_flips'),
    'baseline_partner_count': ('baseline_partner_count', 'n_baseline', 'baseline_partners'),
    'coverage_fraction': ('coverage_fraction', 'retained_coverage'),
    'undefined_reason': ('undefined_reason', 'reason'),
    'finite_gene_count': ('finite_gene_count', 'finite_comparisons')}


COMPARISON_ALIASES = {
    'figure2D_gene_pair_GI': ('figure2D_gene_pair_GI', 'figure2D_gene_pair_values',
                              'figure_2D_GI_score_agreement', 'figure_2D_gene_pair_values',
                              'gene_pair_GI_agreement'),
    'figure2E_gene_profile_correlations': ('figure2E_gene_profile_correlations',
                                           'figure2E_profile_correlation_values',
                                           'figure_2E_profile_correlation_agreement',
                                           'figure_2E_gene_pair_correlation_values',
                                           'profile_correlation_agreement'),
    'same_gene_cross_replicate_partner_profile': ('same_gene_cross_replicate_partner_profile',
                                                  'same_gene_cross_replicate_profile',
                                                  'same_gene_partner_profile')}


FIGURE_COMPARISONS = ('figure2D_gene_pair_GI', 'figure2E_gene_profile_correlations')


class Evidence:
    def __init__(self, root):
        self.root = Path(root)
        self.index = EvidenceIndex(self.root)
        self.manifest = self._manifest()
        self._shared = None
        try:
            self.replicates = self._replicates()
            self.combined = self._combined()
            self.gene_spec = self._gene_spec()
            self.guide_spec = self._guide_spec()
            self.fit_file = self._fit_file()
            self.axes_file = self._axes_file()
            self.shared_file = self._shared_file()
            self.interventions = self._interventions()
            self.compact = self._raw_derived()
            if self.gene_spec['row_axis'] == self.gene_spec['column_axis']:
                raise KeyError('Distinct axis identifiers required')
            if set(self.replicates) != {'rep1', 'rep2'}:
                raise KeyError('Replicate identity adapter needed')
        except (KeyError, TypeError, AttributeError, ValueError) as error:
            declared = sorted(self.manifest) if isinstance(self.manifest, dict) else type(self.manifest).__name__
            raise AdapterRequired(
                'Unresolved evidence-manifest schema: this verifier requires the published '
                'analysis_manifest.json declarations (study/replicate/intervention identities, array axes, '
                'file locations and mappings to count-derived, guide-level and fit evidence). '
                f'Failing declaration: {error!r}. Manifest top-level keys: {declared}. '
                'Treat this as a candidate contract/layout issue, not an automatic scientific zero.') from error

    def _manifest(self):
        default = self.root / 'analysis_manifest.json'
        if default.is_file():
            return json.loads(default.read_text())
        found = self.index.search({'.json'}, any_of=('axes', 'interventions', 'replicates', 'array_schemas'))
        if not found:
            raise AdapterRequired('The evidence tree carries no analysis_manifest.json')
        return json.loads(found[0].read_text())

    def declared(self, *synonyms):
        wanted = {canonical(name) for name in synonyms}
        queue = [self.manifest]
        while queue:
            node = queue.pop(0)
            if isinstance(node, dict):
                for key, value in node.items():
                    if canonical(key) in wanted:
                        return value
                    if isinstance(value, (dict, list)):
                        queue.append(value)
            elif isinstance(node, list):
                queue.extend(item for item in node if isinstance(item, (dict, list)))
        return None

    def resolve(self, value, directory=None):
        if value is None:
            return None
        try:
            name = str(path_value(value, 'declared'))
        except TypeError:
            return None
        for token in ('<phase>', '<replicate_phase>', '<replicate>', '<intervention>', '<omission>'):
            name = name.replace(token + '/', '').replace(token, '')
        name = name.strip().lstrip('./')
        if not name:
            return None
        bases = ([directory] if directory is not None else []) + [self.root]
        for base in bases:
            candidate = base / name
            if candidate.is_file():
                return candidate
        if directory is not None:
            candidate = directory / Path(name).name
            if candidate.is_file():
                return candidate
        return None

    def locate(self, suffixes, directory=None, declared=None, required=(), any_of=(), label='evidence'):
        path = self.resolve(declared, directory)
        if path is not None:
            return path
        found = self.index.search(suffixes, required=required, any_of=any_of, scope=directory)
        if not found:
            raise FileNotFoundError('No declared or discoverable ' + label)
        wanted = canonical(label)
        return sorted(found, key=lambda path: (0 if wanted in canonical(path.stem) else 1,
                                               len(self.index.relative(path).split('/')),
                                               self.index.relative(path)))[0]

    @staticmethod
    def _replicate_key(name):
        digits = [character for character in str(name) if character.isdigit()]
        return 'rep' + (digits[-1] if digits else str(name))

    def _replicates(self):
        record = self.declared('replicate_directories', 'replicates', 'replicate_paths')
        result = {}
        if isinstance(record, dict):
            for key, value in record.items():
                result[self._replicate_key(key)] = path_value(value, 'replicates[' + str(key) + ']')
        elif isinstance(record, list):
            for item in record:
                if isinstance(item, dict):
                    identity = item.get('id', item.get('name', item.get('replicate_id')))
                    result[self._replicate_key(identity)] = path_value(item.get('path', item), 'replicates')
                elif isinstance(item, str):
                    result[self._replicate_key(item)] = item
        if not result:
            raise KeyError('replicates')
        return result

    def _combined(self):
        value = self.declared('combined_directory', 'combined_path', 'combined')
        path = self.resolve(value)
        if path is not None and path.is_dir():
            relative = self.index.relative(path)
            return relative if relative else '.'
        return '.'

    def _gene_spec(self):
        value = self.declared('gene_arrays', 'gene_profiles', 'gi_profiles', 'gene_profile_arrays')
        spec = value if isinstance(value, dict) else ({'filename': value} if isinstance(value, str) else {})
        row_axis = spec.get('row_axis') or self.declared('row_axis', 'row_ids', 'rows') or 'gene_ids'
        column_axis = spec.get('column_axis') or self.declared('column_axis', 'column_ids', 'columns') or 'partner_ids'
        fields = spec.get('fields') or self.declared('gene_array_fields', 'array_fields')
        if isinstance(fields, dict):
            fields = list(fields.values())
        if not fields:
            fields = ['profile_matrix', 'observed_double', 'expected_double', 'uncertainty']
        lookup = alias_lookup(FIELD_ALIASES)
        fields = [lookup.get(canonical(field), field) for field in fields]
        filename = spec.get('filename') or self.declared('gene_array_filename', 'profile_filename')
        return {'filename': filename, 'row_axis': row_axis, 'column_axis': column_axis, 'fields': list(fields)}

    def _guide_spec(self):
        value = self.declared('guide_state', 'guide_observed', 'guide_arrays', 'guide_observed_doubles')
        spec = value if isinstance(value, dict) else ({'filename': value} if isinstance(value, str) else {})
        spec = dict(spec)
        spec.setdefault('filename', self.declared('guide_state_filename', 'guide_axes', 'guide_axes_filename'))
        spec.setdefault('row_axis', spec.get('row_axis') or 'guide_ids')
        spec.setdefault('column_axis', spec.get('column_axis') or 'guide_ids')
        spec.setdefault('observed_double', spec.get('observed_double') or 'observed_double')
        if spec.get('filename') is None:
            path = self.index.matrix_npz(self.root, GUIDE_FIELD_ALIASES['observed_double'], ('guide',),
                                         minimum_matrices=1)
            if path is None:
                raise KeyError('guide state evidence')
            spec['filename'] = self.index.relative(path)
        return spec

    def _fit_file(self):
        value = self.declared('fit_evidence', 'query_fits', 'fits')
        if isinstance(value, dict):
            value = value.get('filename') or value.get('path')
        if isinstance(value, str):
            return value.split(':', 1)[0].strip()
        path = self.index.search({'.csv', '.gz'}, any_of=('quadratic_coefficient', 'quadratic', 'linear_coefficient'))
        if not path:
            raise KeyError('query fit evidence')
        return self.index.relative(path[0])

    def _axes_file(self):
        value = self.declared('guide_axes', 'guide_identities', 'guide_index')
        if isinstance(value, dict):
            value = value.get('filename') or value.get('path')
        if isinstance(value, str):
            return value
        return self.guide_spec['filename']

    def _shared_file(self):
        return self.declared('shared', 'raw_shared', 'shared_raw', 'raw_measurements')

    def _raw_derived(self):
        axes = self.declared('raw_guide_indices', 'raw_indices')
        return bool(axes) or bool(self._shared_file())

    def _interventions(self):
        items = self.declared('interventions', 'intervention_manifest', 'omissions')
        if isinstance(items, dict):
            items = [dict(value, run_id=key) for key, value in items.items() if isinstance(value, dict)]
        if not isinstance(items, list):
            raise KeyError('interventions')
        result = {}
        for item in items:
            if not isinstance(item, dict):
                raise KeyError('interventions')
            run_id = item.get('run_id', item.get('id', item.get('omission_id')))
            location = item.get('phase_outputs', item.get('evidence_location',
                                                         item.get('path', item.get('directory'))))
            if isinstance(location, dict) and any(phase in location for phase in ('rep1', 'rep2', 'combined')):
                phase_roots = {phase: path_value(value, str(run_id) + '.' + phase)
                               for phase, value in location.items()}
                flat = None
            else:
                phase_roots = None
                flat = path_value(location, str(run_id))
            if run_id in result:
                raise ValueError('Duplicate intervention identities')
            result[run_id] = {**item, 'run_id': run_id, 'phase_outputs': flat, 'phase_roots': phase_roots}
        if not result:
            raise KeyError('interventions')
        return result

    def find(self, label, suffixes, directory=None, any_of=(), required=()):
        return self.locate(suffixes, directory=directory, declared=self.declared(label),
                           required=required, any_of=any_of, label=label)

    def gene_matrix_path(self, directory=None):
        return self._gene_matrix_path(directory)

    def guide_matrix_path(self, directory=None):
        return self._guide_matrix_path(directory)

    def artifact(self, label, suffixes, directory=None, required=(), any_of=()):
        return self.locate(suffixes, directory=directory, declared=self.declared(label),
                           required=required, any_of=any_of, label=label)

    def _gene_matrix_path(self, directory=None):
        path = self.resolve(self.gene_spec.get('filename'), directory)
        if path is not None:
            return path
        scope = directory if directory is not None else self.root
        path = self.index.matrix_npz(scope, FIELD_ALIASES['profile_matrix'], ('gene', 'partner'),
                                     minimum_matrices=2)
        if path is None:
            raise FileNotFoundError('No discoverable gene-array evidence in ' + str(scope))
        return path

    def _guide_matrix_path(self, directory=None):
        path = self.resolve(self.guide_spec.get('filename'), directory)
        if path is not None:
            return path
        scope = directory if directory is not None else self.root
        path = self.index.matrix_npz(scope, GUIDE_FIELD_ALIASES['observed_double'], ('guide',), minimum_matrices=1)
        if path is None:
            raise FileNotFoundError('No discoverable guide-state evidence in ' + str(scope))
        return path

    def json(self, relative, directory=None):
        return json.loads(safe_path(directory or self.root, relative).read_text())

    def csv(self, relative, directory=None):
        return pd.read_csv(safe_path(directory or self.root, relative),
                           keep_default_na=False, float_precision='round_trip')

    def npz(self, relative, directory=None):
        with np.load(safe_path(directory or self.root, relative), allow_pickle=False) as archive:
            return {name: archive[name] for name in archive.files}

    def run_root(self, run_id):
        entry = self.interventions[run_id]
        if entry['phase_roots'] and 'combined' in entry['phase_roots']:
            return safe_path(self.root, entry['phase_roots']['combined'])
        return safe_path(self.root, entry['phase_outputs'])

    def phase_root(self, phase, run_id=None):
        if run_id is not None:
            entry = self.interventions[run_id]
            if entry['phase_roots']:
                if phase not in entry['phase_roots']:
                    raise KeyError('Undeclared phase output: ' + phase)
                return safe_path(self.root, entry['phase_roots'][phase])
            base = safe_path(self.root, entry['phase_outputs'])
        else:
            base = self.root
        nested = safe_path(base, self.combined if phase == 'combined' else self.replicates[phase])
        if run_id is not None and not nested.exists():
            flat = safe_path(base, 'combined' if phase == 'combined' else phase)
            if flat.exists():
                return flat
        return nested

    def _field_names(self, archive, aliases):
        lookup = alias_lookup(aliases)
        resolved = {}
        for name in archive:
            target = lookup.get(canonical(name))
            if target is not None and target not in resolved:
                resolved[target] = name
        return resolved

    @staticmethod
    def _axes(archive, primary, secondary, label):
        rows = archive.get(primary)
        columns = archive.get(secondary)
        identifiers = [name for name in archive if archive[name].ndim == 1 and archive[name].dtype.kind in 'USO']
        if rows is None and identifiers:
            rows = archive[identifiers[0]]
        if columns is None:
            columns = archive[identifiers[1]] if len(identifiers) > 1 else rows
        if rows is None or columns is None:
            raise ValueError(label + ' axes are undeclared and undiscoverable')
        return rows.astype(str), columns.astype(str)

    def arrays(self, directory, reference):
        archive = dict(self.index.arrays(self._gene_matrix_path(directory)))
        rows, columns = self._axes(archive, self.gene_spec['row_axis'], self.gene_spec['column_axis'], 'Gene')
        expected = reference['gene_ids']
        if rows.ndim != 1 or columns.ndim != 1:
            raise ValueError('Gene axes must be one-dimensional')
        if len(set(rows)) != len(rows) or len(set(columns)) != len(columns):
            raise ValueError('Duplicated gene axes')
        resolved = self._field_names(archive, FIELD_ALIASES)
        pair_first = next((name for name in archive
                           if canonical(name) in {'pairgeneaindex', 'pairaindex', 'geneaindex', 'pairfirstindex'}), None)
        if pair_first is not None:
            pair_second = next((name for name in archive
                                if canonical(name) in {'pairgenebindex', 'pairbindex', 'genebindex', 'pairsecondindex'}), None)
            if pair_second is None:
                raise ValueError('Compact pair indices are incomplete')
            first, second = archive[pair_first], archive[pair_second]
            if (first.dtype.kind not in 'iu' or second.dtype.kind not in 'iu'
                    or first.ndim != 1 or first.shape != second.shape
                    or np.any(first < 0) or np.any(second < 0)
                    or np.any(first >= len(rows)) or np.any(second >= len(rows))):
                raise ValueError('Invalid compact pair indices')
            identities = [tuple(sorted(pair)) for pair in zip(rows[first], rows[second])]
            if (any(left == right for left, right in identities) or len(set(identities)) != len(identities)
                    or len(identities) != len(rows) * (len(rows) - 1) // 2):
                raise ValueError('Incomplete or duplicated compact pair coverage')
            for field in ('observed_double', 'expected_double', 'uncertainty'):
                name = next((name for name in archive if canonical(name) == canonical('pair_' + field)), None)
                if name is None:
                    raise ValueError('Compact pair evidence lacks ' + field)
                values = archive[name]
                if values.shape != first.shape:
                    raise ValueError('Compact pair value shape mismatch')
                matrix = np.full((len(rows), len(columns)), np.nan)
                second_columns = pd.Index(columns).get_indexer(rows[second])
                first_columns = pd.Index(columns).get_indexer(rows[first])
                matrix[first, second_columns] = values
                matrix[second, first_columns] = values
                archive[field] = matrix
            axes = dict(self.index.arrays(self._guide_matrix_path(directory)))
            guide_ids = self._axes(axes, 'guide_ids', 'guide_ids', 'Guide')[0]
            if len(set(guide_ids)) != len(guide_ids):
                raise ValueError('Duplicate guide identities')
            gene_axis = next((axes[name] for name in axes
                              if canonical(name) in {'geneids', 'geneid', 'genes'}), None)
            if gene_axis is None:
                raise ValueError('Guide evidence lacks its gene axis')
            archive['guide_count'] = np.array([np.count_nonzero(gene_axis.astype(str) == gene) for gene in rows])
            fields = ['profile_matrix', 'observed_double', 'expected_double', 'uncertainty', 'guide_count']
        else:
            fields = ['profile_matrix', 'observed_double', 'expected_double', 'uncertainty', 'guide_count']
        row_order, column_order = pd.Index(rows).get_indexer(expected), pd.Index(columns).get_indexer(expected)
        output = {'gene_ids': expected, 'candidate_gene_ids': sorted(set(rows.astype(str)) | set(columns.astype(str)))}
        for field in fields:
            name = resolved.get(field)
            if name is None or name not in archive:
                shape = (len(expected),) if field == 'guide_count' else (len(expected), len(expected))
                output[field] = np.full(shape, np.nan)
                continue
            values = archive[name]
            if values.ndim == 1:
                aligned = np.full(len(expected), np.nan)
                present = row_order >= 0
                aligned[present] = values[row_order[present]]
            else:
                if values.shape != (len(rows), len(columns)):
                    raise ValueError('Gene evidence shape disagrees with declared axes: ' + field)
                aligned = np.full((len(expected), len(expected)), np.nan)
                first_present, second_present = row_order >= 0, column_order >= 0
                aligned[np.ix_(first_present, second_present)] = values[
                    np.ix_(row_order[first_present], column_order[second_present])]
            output[field] = aligned
        return output

    def guide_observations(self, directory):
        archive = dict(self.index.arrays(self._guide_matrix_path(directory)))
        resolved = self._field_names(archive, GUIDE_FIELD_ALIASES)
        identifiers = archive.get(self.guide_spec.get('row_axis', 'guide_ids'))
        if identifiers is None:
            identifiers = next((archive[name] for name in archive
                                if archive[name].ndim == 1 and archive[name].dtype.kind in 'USO'), None)
        if identifiers is None:
            raise ValueError('Guide identities are undeclared and undiscoverable')
        identifiers = identifiers.astype(str)
        indices = next((archive[name] for name in archive
                        if canonical(name) in {'rawguideindices', 'rawindices', 'guideindices'}), None)
        measured_name = resolved.get('observed_double')
        if measured_name is not None and indices is None:
            measured = archive[measured_name]
            if identifiers.ndim != 1 or measured.shape != (len(identifiers), len(identifiers)):
                raise ValueError('Guide evidence shape disagrees with declared axes')
            return identifiers, measured
        if indices is None:
            raise ValueError('Guide evidence carries neither observable doubles nor raw indices')
        if self._shared is None:
            shared = self.resolve(self.shared_file)
            if shared is None:
                raise FileNotFoundError('Raw shared measurements are unavailable')
            self._shared = self.index.arrays(shared)
        if (indices.dtype.kind not in 'iu' or indices.ndim != 1 or len(set(indices)) != len(indices)
                or np.any(indices < 0) or np.any(indices >= len(self._shared['guide_ids']))
                or not np.array_equal(self._shared['guide_ids'][indices], identifiers)):
            raise ValueError('Raw guide index/identity mismatch')
        records = [self._normalization_record(directory)]
        if 'replicate_id' not in records[0]:
            records = [self._normalization_record(safe_path(self.root, self.replicates[phase]))
                       for phase in ('rep1', 'rep2')]
        measurements = []
        for record in records:
            values = self._shared[record['replicate_id'] + '_log2_count_ratio'][np.ix_(indices, indices)]
            measurements.append((values + record['log2_library_shift'] - record['control_log2_center'])
                                / record['doublings'])
        measured = np.mean(measurements, axis=0)
        return identifiers, (measured + measured.T) / 2

    def fits(self, directory):
        record = pd.read_csv(self._fit_path(directory), keep_default_na=False)
        record = canonical_columns(record, FIT_ALIASES)
        if 'guide_id' not in record.columns and 'query_guide_id' in record.columns:
            record['guide_id'] = record['query_guide_id']
        return pd.concat([record.assign(orientation=orientation) for orientation in
                          ('variable_A_query_B', 'variable_B_query_A')], ignore_index=True)

    def _normalization_record(self, directory):
        path = self.locate({'.json'}, directory=directory,
                           any_of=('doublings', 'log2libraryshift', 'controllog2center'), label='normalization')
        return json.loads(path.read_text())

    def _fit_path(self, directory):
        path = self.resolve(self.fit_file, directory)
        if path is not None:
            return path
        return self.locate({'.csv', '.gz'}, directory=directory,
                           any_of=('quadraticcoefficient', 'quadratic'), label='query fit evidence')

    def _checksum_record(self):
        path = self.resolve(self.declared('input_checksums', 'input_hashes', 'checksums', 'input_byte_binding'))
        if path is None:
            path = self._checksum_file()
        return json.loads(path.read_text())

    @staticmethod
    def _hash_value(value):
        if isinstance(value, str) and len(value) == 64 and all(character in '0123456789abcdef' for character in value.lower()):
            return value
        if isinstance(value, dict):
            for key, item in value.items():
                if canonical(key) in {'sha256', 'sha', 'digest', 'hash'} and isinstance(item, str):
                    return item
        return None

    def _checksum_file(self):
        candidates = []
        for path, record in self.index.records():
            if any(self._hash_value(value) is not None for value in record.values()):
                candidates.append(path)
        if not candidates:
            raise FileNotFoundError('No discoverable input checksums')
        return sorted(candidates, key=lambda path: (len(self.index.relative(path).split('/')),
                                                    self.index.relative(path)))[0]

    def _json_role(self, label, any_of, suffixes=('.json',)):
        path = self.locate(suffixes, declared=self.declared(label, label.replace('_', '')), any_of=any_of,
                           label=label)
        return json.loads(path.read_text())

    def input_hashes(self):
        record = self._checksum_record()
        if isinstance(record.get('inputs'), list):
            values = {item['name']: item['sha256'] for item in record['inputs']}
            if len(values) != len(record['inputs']):
                raise ValueError('Duplicate input bindings')
            return values
        source = record.get('source')
        if isinstance(source, list):
            return {Path(item['path']).name: item['sha256'] for item in source}
        values = {}
        for key, value in record.items():
            text = str(key)
            if text.startswith(('/home/submission/', '/home/paper/')):
                continue
            digest_value = self._hash_value(value)
            if digest_value is not None:
                values[Path(text).name] = digest_value
        return values

    def provenance(self):
        path = self.resolve(self.declared('provenance'))
        if path is not None:
            return json.loads(path.read_text())
        default = self.root / 'provenance.json'
        if default.is_file():
            return json.loads(default.read_text())
        record = self._checksum_record()
        source = {}
        if isinstance(record.get('source'), list):
            for item in record['source']:
                relative = Path(item['path'])
                relative = relative.relative_to('/home/submission') if relative.is_absolute() else relative
                safe_path(self.root, relative)
                if str(relative) in source:
                    raise ValueError('Duplicate source bindings')
                source[str(relative)] = item['sha256']
        else:
            for key, value in record.items():
                candidate = Path(key)
                digest_value = self._hash_value(value)
                if digest_value is None:
                    continue
                if str(candidate).startswith('/home/submission/'):
                    source[str(candidate.relative_to('/home/submission'))] = digest_value
        paper = {}
        if isinstance(record.get('method_and_metadata'), list):
            paper = {item['path']: item['sha256'] for item in record['method_and_metadata']}
        else:
            paper = {key: self._hash_value(value) for key, value in record.items()
                     if str(key).startswith('/home/paper/') and self._hash_value(value) is not None}
        return {'source_sha256': source, 'paper_sha256': paper.get('/home/paper/paper.md'),
                'conventions_sha256': paper.get('/home/paper/conventions.json')}

    def execution(self):
        record = canonical_record(self._json_role('execution_status',
                                                 ('status', 'omissions', 'failures')), {})
        completed = record.get('completed_omissions', record.get('completed'))
        expected = record.get('expected_omissions', record.get('expected'))
        failures = record.get('failures', record.get('unhandled_exceptions'))
        declared = record.get('process_completed')
        return {**record,
                'process_completed': declared if isinstance(declared, bool)
                else str(record.get('status', '')).lower() in {'complete', 'completed'},
                'protocol_complete': completed is not None and expected is not None and completed == expected,
                'unhandled_exceptions': [] if failures is None else failures}

    def resources(self):
        record = canonical_record(self._json_role('resource_usage',
                                                  ('wall_seconds', 'peak', 'rss', 'memory')), {})
        rss = record.get('peak_rss_bytes')
        if not isinstance(rss, (int, float)):
            kib = record.get('peak_RSS_KiB', record.get('maximum_worker_peak_rss_kib',
                                                      record.get('parent_peak_rss_kib')))
            rss = float(kib) * 1024 if isinstance(kib, (int, float)) else 0
        return {**record, 'wall_clock_seconds': record.get('wall_clock_seconds',
                                                           record.get('wall_seconds', 0)),
                'peak_rss_bytes': rss}

    def normalization(self, directory, phase):
        record = self._normalization_record(directory)
        nested = record.get('replicate_normalizations') if isinstance(record, dict) else None
        if nested:
            if isinstance(nested, dict):
                record = nested.get(phase, nested.get(self._replicate_key(phase), record))
            else:
                for item in nested:
                    if isinstance(item, dict) and str(item.get('replicate_id', item.get('phase', ''))).endswith(
                            str(phase)[-1]):
                        record = item
                        break
        return canonical_record(record, NORMALIZATION_ALIASES) if isinstance(record, dict) else record

    def filtering(self, directory, omitted):
        path = self.locate({'.csv', '.gz'}, directory=directory,
                           any_of=('retained', 'medianendpointa', 'reason'), label='filter ledger')
        record = canonical_columns(pd.read_csv(path, keep_default_na=False), FILTER_ALIASES)
        if omitted is not None and 'guide_id' in record.columns:
            record = record[record['guide_id'] != omitted]
        return record

    def _comparison_targets(self, frame, targets):
        if 'comparison' not in frame.columns:
            return frame
        lookup = alias_lookup(COMPARISON_ALIASES)
        frame = frame.copy()
        frame['comparison'] = [lookup.get(canonical(name), name) for name in frame['comparison']]
        frame = frame[frame['comparison'].isin(targets)]
        if 'gene_a' in frame.columns and 'gene_b' in frame.columns:
            marked = (frame['gene_a'].astype(str) == 'ALL') & (frame['gene_b'].astype(str) == 'ALL')
            if marked.any():
                frame = frame[marked]
        return frame

    def replication(self):
        frames = []
        declared_summary = self.declared('replicate_comparisons', 'replicate_summary')
        path = self.resolve(declared_summary)
        if path is None:
            for candidate in self.index.search({'.csv', '.gz'}, required=('comparison',)):
                table = pd.read_csv(candidate, keep_default_na=False)
                if 'entity_id' not in table.columns and 'run_id' not in table.columns:
                    path = candidate
                    break
        if path is not None:
            frames.append(self._comparison_targets(pd.read_csv(path, keep_default_na=False), FIGURE_COMPARISONS))
        declared_genes = self.declared('same_gene_replication', 'same_gene_values')
        path = self.resolve(declared_genes)
        if path is None:
            for keys in (('comparison', 'entity_id'), ('comparison', 'gene_a'), ('comparison', 'gene_id')):
                found = self.index.search({'.csv', '.gz'}, required=keys)
                found = [candidate for candidate in found if 'values' not in candidate.name]
                if found:
                    path = found[0]
                    break
        if path is not None:
            genes = canonical_columns(pd.read_csv(path, keep_default_na=False),
                                      {'entity_id': ('entity_id', 'gene_a', 'gene_id', 'gene')})
            if 'comparison' in genes.columns:
                genes = genes.copy()
                genes['comparison'] = 'same_gene_cross_replicate_partner_profile'
            frames.append(genes)
        if not frames:
            raise FileNotFoundError('No discoverable replicate comparison evidence')
        return canonical_columns(pd.concat(frames, ignore_index=True), STATISTICS_ALIASES)

    def omission_inventory(self):
        path = self.locate({'.csv', '.gz'}, declared=self.declared('omission_eligibility'),
                           any_of=('eligible', 'commonguideids', 'commonguides'), label='omission eligibility')
        inventory = pd.read_csv(path, keep_default_na=False)
        if 'guide_id' in inventory.columns and 'gene_id' in inventory.columns:
            return inventory[['gene_id', 'guide_id']]
        selected = inventory[inventory['eligible'].astype(str).str.lower().isin(('true', '1'))]
        records = []
        for row in selected.to_dict('records'):
            fields = {canonical(key): value for key, value in row.items()}
            guides = None
            for key in ('commonguideids', 'commonguides'):
                if key in fields:
                    guides = self._guide_list(fields[key])
                    break
            if guides is None:
                first = self._guide_list(fields.get('guidesrep1', fields.get('guides1')))
                second = self._guide_list(fields.get('guidesrep2', fields.get('guides2')))
                if first and second:
                    guides = [guide for guide in first if guide in set(second)]
            if guides is None:
                guides = self._guide_list(fields.get('testedguides', fields.get('eligibleguides')))
            for guide in guides:
                if not guide:
                    raise ValueError('Empty eligible guide identity')
                records.append({'gene_id': row['gene_id'], 'guide_id': guide})
        return pd.DataFrame(records, columns=['gene_id', 'guide_id'])

    @staticmethod
    def _guide_list(value):
        if value is None:
            return None
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value]
        text = str(value).strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return [item for item in text.split(';') if item]

    def attempts(self):
        path = self.locate({'.csv', '.gz'}, declared=self.declared('omission_manifest', 'intervention_manifest'),
                           required=('runid', 'geneid', 'guideid'), any_of=('status',), label='intervention manifest')
        record = pd.read_csv(path, keep_default_na=False)
        if 'status' in record.columns:
            record['status'] = record['status'].replace({'complete': 'completed'})
        return record

    def local_statistics(self):
        path = self.locate({'.csv', '.gz'}, declared=self.declared('local_omission_metrics'),
                           required=('runid', 'phase', 'geneid'),
                           any_of=('coveragefraction',), label='local omission metrics')
        return canonical_columns(pd.read_csv(path, keep_default_na=False), STATISTICS_ALIASES)

    def local_values(self, directory):
        path = self.locate({'.csv', '.gz'}, directory=directory,
                           any_of=('partner', 'baselinegi', 'perturbedgi'), label='local pair values')
        return canonical_columns(pd.read_csv(path, keep_default_na=False), LOCAL_VALUE_ALIASES)

    def null_evidence(self):
        mappings_path = next((candidate for candidate in self.index.search({'.csv', '.gz'},
                                                                          required=('permutationid',))
                              if 'pearsonr' not in self.index.keys(candidate)), None)
        if mappings_path is None:
            mappings_path = self.locate({'.csv', '.gz'}, required=('permutationid',),
                                        any_of=('replicate1gene', 'gene1'), label='null mappings')
        mappings = pd.read_csv(mappings_path, keep_default_na=False)
        statistics = pd.read_csv(self.locate({'.csv', '.gz'}, required=('kind', 'statistic'),
                                             label='null statistics'), keep_default_na=False)
        summary = json.loads(self.locate({'.json'}, any_of=('observed', 'observedmedian', 'permutations',
                                                            'npermutations', 'nulldistribution', 'null',
                                                            'nullinterval95', 'exceedances'),
                                        label='null summary').read_text())
        if 'profile_pearson' not in mappings.columns:
            focal = pd.read_csv(self.locate({'.csv', '.gz'}, required=('permutationid',),
                                            any_of=('pearson', 'pearsonr', 'pearsoncorrelation'),
                                            label='null focal values'),
                                keep_default_na=False)
            keys = [column for column in ('permutation_id', 'replicate1_gene', 'replicate2_gene')
                    if column in focal.columns and column in mappings.columns]
            merged = mappings.merge(focal, on=keys, how='left', validate='one_to_one')
            mappings = renamed(merged, {'pearson': 'profile_pearson', 'pearson_r': 'profile_pearson',
                                        'n_partners': 'partner_count'})
        mappings = renamed(mappings, {'replicate1gene': 'replicate1_gene',
                                      'replicate2gene': 'replicate2_gene'})
        statistics = renamed(statistics, {'finite_comparisons': 'finite_gene_count',
                                          'n_finite': 'finite_gene_count'})
        summary = renamed(summary, {'observed': 'observed_median_profile_pearson',
                                    'observed_median': 'observed_median_profile_pearson',
                                    'permutations': 'randomized_matchings',
                                    'n_permutations': 'randomized_matchings',
                                    'defined_permutations': 'defined_randomized_matchings',
                                    'null_interval_95': 'null_quantiles_025_975',
                                    'null_interval': 'null_quantiles_025_975',
                                    'exceedance_probability_exact_95_interval':
                                        'monte_carlo_exceedance_probability_95_interval',
                                    'monte_carlo_p_upper': 'upper_tail_plus_one_probability',
                                    'finite_permutations': 'defined_randomized_matchings',
                                    'exceedances': 'upper_tail_exceedances',
                                    'upper_tail_probability_plus_one': 'upper_tail_plus_one_probability',
                                    'binomial_95pct_interval_for_unadjusted_tail_probability':
                                        'monte_carlo_exceedance_probability_95_interval'})
        distribution = next((value for key, value in summary.items()
                             if canonical(key) in {'nulldistribution', 'null'} and isinstance(value, dict)), None)
        if distribution is not None:
            summary.setdefault('null_median', distribution.get('median'))
            if 'null_quantiles_025_975' not in summary:
                quantiles = [distribution.get(key) for key in ('q025', 'q975')]
                if all(value is not None for value in quantiles):
                    summary['null_quantiles_025_975'] = quantiles
        summary.setdefault('biological_replicates', self.declared('n_biological_replicates') or 2)
        if 'defined_randomized_matchings' not in summary and 'randomized_matchings' in summary:
            summary['defined_randomized_matchings'] = summary['randomized_matchings']
        return mappings, statistics, summary
