import argparse
import json
from pathlib import Path

import numpy as np

from evidence import EvidenceMissing, Evidence, EvidenceError, checksum, qe_stress, qe_xml, trusted_replay
from soc_control10 import OBSERVABLES, audit_pair, compare_report, primary_state, primary_values
from numerics import cubic_mass, finite, stiffness


ROOT = Path(__file__).resolve().parents[1]


def native_elastic_stress(evidence, record):
    relative = record.get('native_output')
    mapping_source = 'metadata.native_output'
    if relative is None:
        relative = f'results/elastic/{record["family"]}_{record["strain"]:+.4f}/pw.out'
        mapping_source = 'default_native_output_path'
    result = {'native_output': relative, 'mapping_source': mapping_source, 'native_bound': False}
    try:
        path = evidence.path(relative)
        stress = finite(qe_stress(path.read_text()), (3, 3))
        result.update(status='native_text_parsed', native_bound=True, stress_kbar=stress.tolist(),
            native_output_sha256=checksum(path))
    except (EvidenceError, OSError, ValueError, TypeError) as error:
        result.update(status='missing_or_invalid_native_text', error={'type': type(error).__name__, 'message': str(error)})
    return result


def materials(evidence):
    bands, masses, tensors = {}, {}, {}
    native_points = {}
    errors = []

    def fail(label, error):
        errors.append({'section': label,
            'kind': 'evidence_reader_failure' if isinstance(error, (EvidenceError, OSError)) else 'scientific_or_schema_issue',
            'error': {'type': type(error).__name__, 'message': str(error)}})

    for path in sorted((evidence.root / 'results/elastic').glob('*/metrics.json')):
        relative = str(path.relative_to(evidence.root))
        try:
            record = evidence.json(relative)
            native_points[relative] = native_elastic_stress(evidence, record)
        except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            fail(relative, error)
    for variant in ('bands_nosoc', 'bands_soc'):
        relative = f'results/{variant}/raw_arrays.npz'
        if not (evidence.root / relative).is_file():
            continue
        try:
            arrays = evidence.arrays(relative)
            native = qe_xml(evidence.path(f'results/{variant}/bands/data-file-schema.xml'))
            energies = finite(arrays['eigenvalues_ev'])
            if native['eigenvalues_ev'].shape != energies.shape:
                raise ValueError('QE eigenvalue shape mismatch')
            point_count = len(np.unique(np.round(arrays['kpoints_crystal'], 12), axis=0))
            occupied = 26 if variant == 'bands_soc' else 13
            bands[variant] = {'distinct_native_path_points': point_count, 'native_eigenvalue_max_error_ev': float(np.max(abs(energies - native['eigenvalues_ev']))),
                'path_gap_ev': float(np.min(energies[:, occupied]) - np.max(energies[:, occupied - 1])),
                'path_is_not_full_BZ_proof': True}
        except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            fail('bands/' + variant, error)
    relative = 'results/elastic/raw_arrays.npz'
    if (evidence.root / relative).is_file():
        try:
            arrays = evidence.arrays(relative)
            metadata = evidence.json('results/elastic/metrics.json')
            for family in ('exx', 'eyy'):
                records = [record for record in metadata['points'] if record['family'] == family]
                if len(records) >= 4:
                    sources = ((family + '_stress_printed_kbar', 'qe_printed', 1),
                        (family + '_stress_qe_kbar', 'qe_printed', 1),
                        (family + '_stress_tensile_kbar', 'tensile', -1))
                    selected = next((source for source in sources if source[0] in arrays), None)
                    if selected is None:
                        tensors[family] = {'status': 'reader_mapping_required', 'available_keys': list(arrays)}
                        continue
                    stress_key, convention, native_sign = selected
                    strains = finite(arrays.get(family + '_strain', [record['strain'] for record in records]))
                    by_strain = {float(finite(record['strain'], ())): record for record in records}
                    if len(by_strain) != len(records) or any(float(strain) not in by_strain for strain in strains):
                        raise ValueError('Elastic strain samples do not uniquely identify native records')
                    ordered = [by_strain[float(strain)] for strain in strains]
                    native_stress = native_sign * finite(arrays[stress_key], (len(strains), 3, 3))
                    retained = [{key: record[key] for key in ('strain', 'stress_printed_kbar', 'native_output') if key in record}
                        for record in ordered]
                    metadata_error = None
                    fit_source = 'raw_arrays.npz:' + stress_key + ' normalized to QE printed stress'
                    if all('stress_printed_kbar' in record for record in ordered):
                        printed = finite([record['stress_printed_kbar'] for record in ordered], (len(strains), 3, 3))
                        metadata_error = float(finite(np.max(abs(native_stress - printed)), ()))
                        native_stress = printed
                        fit_source = 'metrics.json:points[].stress_printed_kbar'
                    tensors[family] = stiffness(strains, native_stress, metadata['c_cell_angstrom'])
                    bindings = [native_elastic_stress(evidence, record) for record in ordered]
                    bound_count = sum(binding['native_bound'] for binding in bindings)
                    native_error = None
                    self_consistency_fit = dict(tensors[family])
                    if bound_count == len(ordered):
                        parsed_stress = np.asarray([binding['stress_kbar'] for binding in bindings])
                        native_error = float(finite(np.max(abs(native_sign * arrays[stress_key] - parsed_stress)), ()))
                        tensors[family] = stiffness(strains, parsed_stress, metadata['c_cell_angstrom'])
                        fit_source = 'QE pw.out:last (kbar) stress blocks'
                    tensors[family].update(stress_array_key=stress_key, stress_array_convention=convention,
                        strain_samples=strains.tolist(), fit_stress_source=fit_source,
                        stiffness_input_convention='qe_printed', native_stress_records=retained,
                        stress_array_native_max_error_kbar=native_error,
                        stress_array_metadata_max_error_kbar=metadata_error,
                        native_bound=bound_count == len(ordered), native_bound_points=bound_count,
                        native_binding_status='all_native_text_bound' if bound_count == len(ordered) else 'partial_native_text_bound' if bound_count else 'self_consistency_only',
                        native_stress_bindings=bindings, self_consistency_fit=self_consistency_fit)
        except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            fail('elastic', error)
    for path in sorted((evidence.root / 'results/effmass').glob('*/metrics.json')):
        try:
            record = evidence.json(str(path.relative_to(evidence.root)))
            arrays_path = 'results/effmass/raw_arrays.npz'
            if not (evidence.root / arrays_path).is_file():
                continue
            arrays = evidence.arrays(arrays_path)
            prefix = record['raw_key_prefix']
            offsets = arrays[prefix + '_dk_cart_inv_angstrom']
            energies = arrays[prefix + '_eigenvalues_ev']
            native = qe_xml(evidence.path(str(path.parent.relative_to(evidence.root)) + '/data-file-schema.xml'))
            if not np.allclose(energies, native['eigenvalues_ev'], atol=1e-8, rtol=0):
                raise ValueError('Mass samples do not match native eigenvalues')
            branches = {}
            for branch, fit in record['bands'].items():
                branches[branch] = cubic_mass(offsets, energies[:, fit['band_index_zero_based']])
            masses[prefix] = branches
        except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            fail(str(path.relative_to(evidence.root)), error)
    paired = None
    if (evidence.root / 'results/paired_soc_and_edges/metrics.json').is_file():
        try:
            paired = {}
            common_geometry = None
            for stage, suffix in (('paired_soc_and_edges', 'local'), ('accuracy_controls', 'edges')):
                metadata = evidence.json(f'results/{stage}/metrics.json')
                primary = {}
                for variant in ('S', 'F1'):
                    directory = f'results/{stage}/{variant}_{suffix}'
                    primary[variant] = primary_values(evidence, directory, variant == 'F1')
                    reported = metadata['variants'][variant]
                    compare_report({key: value for key, value in primary[variant].items()
                        if key in ('fundamental_gap_ev', 'direct_K_gap_ev') or key in reported}, reported)
                    bands_identity = primary_state(evidence, directory, variant == 'F1')
                    base_scf = 'results/bands_soc/scf' if variant == 'F1' else 'results/bands_nosoc/scf'
                    scf_directory = base_scf if stage == 'paired_soc_and_edges' else f'results/{stage}/{variant}_scf'
                    scf_identity = primary_state(evidence, scf_directory, variant == 'F1')
                    if (scf_identity['calculation'] != 'scf' or bands_identity['calculation'] != 'bands'
                            or scf_identity['settings'] != bands_identity['settings']):
                        raise ValueError('Primary PAW SCF and sampled bands have different model settings')
                    geometry = {field: bands_identity['settings'][field] for field in ('cell_bohr', 'positions_bohr')}
                    if common_geometry is None:
                        common_geometry = geometry
                    elif common_geometry != geometry:
                        raise ValueError('PAW SOC comparison or refinement changed the common geometry')
                primary['nc_soc_control'] = audit_pair(evidence, metadata['nc_soc_control'], primary,
                    stage, evidence.root.parent / 'inputs')
                if stage == 'paired_soc_and_edges':
                    paired.update(primary)
                else:
                    paired['accuracy_controls'] = primary
            baseline = paired['nc_soc_control']
            refinement = paired['accuracy_controls']['nc_soc_control']
            if baseline['matched_settings'] == refinement['matched_settings'] and baseline['mesh'] == refinement['mesh']:
                raise ValueError('NC refinement repeats the baseline numerical settings')
            paired['nc_numerical_sensitivity_ev'] = {variant: {quantity:
                refinement['variants'][variant][quantity] - baseline['variants'][variant][quantity]
                for quantity in OBSERVABLES} for variant in ('N0', 'N1')}
        except (EvidenceError, OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
            fail('paired_soc_and_edges', error)
    return {'task_id': '10', 'bands': bands, 'elastic': tensors, 'mass_fits': masses, 'paired_soc': paired,
        'elastic_native_points': native_points, 'section_errors': errors, 'native_calls_independently_attested': False,
        'diagnostic_limitations': ['Structural/SCF branch audit', 'Elastic and band-edge independent convergence envelopes', 'Mass branch tracking/degeneracy audit', 'Vacuum and numerical-control adjudication', 'Scientific interpretation is not established by arithmetic checks', 'Arithmetic diagnostics do not assign rubric scores']}


def json_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=('10',), required=True)
    parser.add_argument('--run-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-live-diagnostic', action='store_true')
    arguments = parser.parse_args()
    run_root = arguments.run_directory.resolve()
    output = arguments.output.resolve()
    if output.is_relative_to(run_root):
        raise ValueError('Audit output must not modify replay source or evidence')
    state = trusted_replay(run_root)
    if state['status'] == 'running' and not arguments.allow_live_diagnostic:
        raise RuntimeError('Refusing to score unfrozen running evidence; use diagnostic mode only')
    report = {'task_id': arguments.task, 'replay': state,
        'run_directory': str(run_root), 'trusted_replay_sha256': checksum(run_root / 'trusted_replay.json'),
        'status': 'scientific_diagnostic', 'scoring_dimensions': {'A': 10, 'B': 10, 'C': 80}}
    try:
        evidence = Evidence(run_root / 'outputs')
        report['scientific_checks'] = materials(evidence)
    except EvidenceMissing as error:
        report['status'] = 'candidate_evidence_incomplete'
        report['missing_evidence'] = str(error)
    except EvidenceError as error:
        report['status'] = 'evidence_reader_failure_not_scientific_zero'
        report['error'] = str(error)
    except (ValueError, KeyError, IndexError) as error:
        report['status'] = 'scientific_or_schema_issue_requires_triage'
        report['error'] = {'type': type(error).__name__, 'message': str(error)}
    serialized = json.dumps(report, indent=2, allow_nan=False, default=json_scalar) + '\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        stream.write(serialized)
    print(json.dumps({'output': str(output), 'status': report['status']}))


if __name__ == '__main__':
    main()
