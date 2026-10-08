import hashlib
import xml.etree.ElementTree as ET

import numpy as np

from evidence import Evidence, checksum, qe_xml
from numerics import finite


PSEUDOPOTENTIALS = {
    'Mo-sp_r.upf': 'b5a929dee3378934d30b33a8f510c8a715450d22b4f1a3469276569ac47ab29d',
    'S_r.upf': '47dc390784fa31acb520275f817fbe0bb42219399f641ecbcfb97ca9a1f947fa',
}
OBSERVABLES = ('direct_K_gap_ev', 'K_valence_splitting_ev', 'K_conduction_splitting_ev')
PAW_PSEUDOPOTENTIALS = {
    False: {'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF': '4396e0c640fcce5c25f020efccf1ab12',
        'S.pbe-n-kjpaw_psl.1.0.0.UPF': 'fb45dfebcf3e72a4e1bd4a866ec2e262'},
    True: {'Mo.rel-pbe-spn-kjpaw_psl.1.0.0.UPF': '6cda9dff73cdab358834687290e4775f',
        'S.rel-pbe-n-kjpaw_psl.1.0.0.UPF': '665a6610193808042cdd4f03574b9f7b'},
}


def xml_root(path):
    root = ET.parse(path).getroot()
    for element in root.iter():
        element.tag = element.tag.split('}')[-1]
    return root


def pinned_inputs(input_root):
    inputs = Evidence(input_root)
    records = {}
    for name, expected in PSEUDOPOTENTIALS.items():
        path = inputs.path('soc_control_pseudo/' + name)
        if checksum(path) != expected:
            raise ValueError('Changed fixed NC pseudopotential: ' + name)
        records[name] = hashlib.md5(path.read_bytes()).hexdigest()
    return records


def native_state(evidence, directory, soc, pseudopotentials, expected_species=None):
    root = xml_root(evidence.path(directory + '/data-file-schema.xml'))
    native_output = evidence.path(directory + '/pw.out').read_text()
    if 'JOB DONE.' not in native_output:
        raise ValueError('NC calculation did not finish natively')
    species = {element.attrib['name']: element.findtext('pseudo_file').strip()
        for element in root.findall('./input/atomic_species/species')}
    if species != (expected_species or {'Mo': 'Mo-sp_r.upf', 'S': 'S_r.upf'}):
        raise ValueError('NC comparison substituted a different pseudopotential model')
    for name, digest in pseudopotentials.items():
        if name not in native_output or digest not in native_output:
            raise ValueError('NC native pseudopotential hash is missing or inconsistent')
    for field in ('noncolin', 'spinorbit'):
        nodes = root.findall('.//' + field)
        if not nodes or any(node.text.strip().lower() != str(soc).lower() for node in nodes):
            raise ValueError('NC native SOC switch mismatch')
    if any(node.text.strip().lower() != 'false' for node in root.findall('.//lsda')):
        raise ValueError('Unexpected spin-polarized state in the nonmagnetic comparison')
    bands = root.find('./output/band_structure')
    expected_bands = 40 if soc else 20
    if (bands is None or int(bands.findtext('nbnd', '0')) != expected_bands
            or float(bands.findtext('nelec', 'nan')) != 26):
        raise ValueError('NC native electron or band count mismatch')
    structure = root.find('./input/atomic_structure')
    if structure is None:
        raise ValueError('Missing NC native geometry')
    cell = finite([np.fromstring(structure.findtext('cell/' + axis), sep=' ') for axis in ('a1', 'a2', 'a3')], (3, 3))
    atoms = structure.findall('./atomic_positions/atom')
    positions = finite([np.fromstring(atom.text, sep=' ') for atom in atoms], (3, 3))
    if [atom.attrib['name'] for atom in atoms] != ['Mo', 'S', 'S']:
        raise ValueError('NC native atom identity mismatch')
    smearing = root.find('./input/bands/smearing')
    if smearing is None:
        raise ValueError('Missing NC native smearing')
    settings = {
        'cell_bohr': cell.tolist(), 'positions_bohr': positions.tolist(),
        'functional': root.findtext('./input/dft/functional'),
        'smearing': smearing.text.strip(), 'degauss_hartree': float(smearing.attrib['degauss']),
        'occupations': root.findtext('./input/bands/occupations'),
        'charge': float(root.findtext('./input/bands/tot_charge', 'nan')),
        'ecutwfc_hartree': float(root.findtext('./input/basis/ecutwfc', 'nan')),
        'ecutrho_hartree': float(root.findtext('./input/basis/ecutrho', 'nan')),
        'conv_thr_hartree': float(root.findtext('./input/electron_control/conv_thr', 'nan')),
    }
    finite([settings[key] for key in ('degauss_hartree', 'charge', 'ecutwfc_hartree', 'ecutrho_hartree', 'conv_thr_hartree')])
    if (settings['functional'] != 'PBE' or settings['charge'] != 0
            or settings['smearing'] != 'fd' or settings['occupations'] != 'smearing'
            or abs(settings['degauss_hartree'] * 27.211386245988 - 0.05) > 1e-10):
        raise ValueError('NC functional or charge differs from the fixed model')
    mesh = root.find('./input/k_points_IBZ/monkhorst_pack')
    calculation = root.findtext('./input/control_variables/calculation')
    if calculation == 'scf':
        if mesh is None or root.findtext('./output/convergence_info/scf_conv/convergence_achieved') != 'true':
            raise ValueError('NC SCF lacks a converged native mesh calculation')
    elif calculation != 'bands':
        raise ValueError('NC state is not an SCF or native band calculation')
    return {'settings': settings, 'mesh': dict(mesh.attrib) if mesh is not None else None,
        'calculation': calculation, 'alat_bohr': float(finite(float(structure.attrib['alat']), ())),
        'cell_bohr': cell, 'xml_sha256': checksum(evidence.path(directory + '/data-file-schema.xml'))}


def k_values(evidence, directory, soc, identity):
    arrays = evidence.arrays(directory + '/raw_arrays.npz')
    native = qe_xml(evidence.path(directory + '/data-file-schema.xml'))
    energies = finite(native['eigenvalues_ev'], (1, 40 if soc else 20))
    points = finite(native['points'], (1, 3)) @ identity['cell_bohr'].T / identity['alat_bohr']
    if not np.allclose(points, [[1 / 3, 1 / 3, 0]], atol=1e-10, rtol=0):
        raise ValueError('NC eigenvalues were not measured at native K')
    if not np.allclose(finite(arrays['kpoints_crystal'], (1, 3)), points, atol=1e-10, rtol=0):
        raise ValueError('NC archive relabels the native k-point')
    if not np.allclose(finite(arrays['eigenvalues_ev'], energies.shape), energies, atol=1e-8, rtol=0):
        raise ValueError('NC archive differs from native eigenvalues')
    if np.any(np.diff(energies[0]) < 0):
        raise ValueError('NC bands are not energy ranked')
    occupied = 26 if soc else 13
    return {'direct_K_gap_ev': float(energies[0, occupied] - energies[0, occupied - 1]),
        'K_valence_splitting_ev': float(energies[0, occupied - 1] - energies[0, occupied - 2]) if soc else 0.,
        'K_conduction_splitting_ev': float(energies[0, occupied + 1] - energies[0, occupied]) if soc else 0.}


def compare_report(actual, reported):
    for quantity, value in actual.items():
        if abs(float(finite(reported[quantity], ())) - value) > 1e-8:
            raise ValueError('Reported NC quantity disagrees with native recomputation: ' + quantity)


def primary_state(evidence, directory, soc):
    pseudopotentials = PAW_PSEUDOPOTENTIALS[soc]
    species = {name.split('.')[0]: name for name in pseudopotentials}
    return native_state(evidence, directory, soc, pseudopotentials, species)


def primary_values(evidence, directory, soc):
    arrays = evidence.arrays(directory + '/raw_arrays.npz')
    path = evidence.path(directory + '/data-file-schema.xml')
    native = qe_xml(path)
    values = finite(native['eigenvalues_ev'])
    if values.ndim != 2 or values.shape[1] != (40 if soc else 20):
        raise ValueError('Primary PAW band shape mismatch')
    if not np.allclose(finite(arrays['eigenvalues_ev'], values.shape), values, atol=1e-8, rtol=0):
        raise ValueError('Primary PAW samples differ from native eigenvalues')
    structure = xml_root(path).find('./input/atomic_structure')
    cell = finite([np.fromstring(structure.findtext('cell/' + axis), sep=' ') for axis in ('a1', 'a2', 'a3')], (3, 3))
    points = finite(native['points'], (len(values), 3)) @ cell.T / float(structure.attrib['alat'])
    if not np.allclose(finite(arrays['kpoints_crystal'], points.shape), points, atol=1e-9, rtol=0):
        raise ValueError('Primary PAW archive relabels native k-points')
    corner = np.flatnonzero(np.max(abs(points - [1 / 3, 1 / 3, 0]), axis=1) < 1e-9)
    if len(corner) != 1:
        raise ValueError('Primary PAW comparison lacks an unambiguous native K point')
    corner = int(corner[0])
    occupied = 26 if soc else 13
    return {'fundamental_gap_ev': float(np.min(values[:, occupied]) - np.max(values[:, occupied - 1])),
        'direct_K_gap_ev': float(values[corner, occupied] - values[corner, occupied - 1]),
        'K_valence_splitting_ev': float(values[corner, occupied - 1] - values[corner, occupied - 2]) if soc else 0.,
        'K_conduction_splitting_ev': float(values[corner, occupied + 1] - values[corner, occupied]) if soc else 0.}


def audit_pair(evidence, metadata, primary, stage, input_root):
    pseudopotentials = pinned_inputs(input_root)
    variants, identities = {}, {}
    for variant, soc in (('N0', False), ('N1', True)):
        base = f'results/{stage}/{variant}'
        scf = native_state(evidence, base + '_scf', soc, pseudopotentials)
        bands = native_state(evidence, base + '_K', soc, pseudopotentials)
        if scf['calculation'] != 'scf' or bands['calculation'] != 'bands' or scf['settings'] != bands['settings']:
            raise ValueError('NC SCF and K bands do not share the electronic model')
        variants[variant] = k_values(evidence, base + '_K', soc, bands)
        compare_report(variants[variant], metadata['variants'][variant])
        identities[variant] = scf
    if (identities['N0']['settings'] != identities['N1']['settings']
            or identities['N0']['mesh'] != identities['N1']['mesh']):
        raise ValueError('NC SOC pair has unmatched geometry or numerical settings')
    geometry = xml_root(evidence.path('results/bands_nosoc/scf/data-file-schema.xml'))
    paw_structure = geometry.find('./input/atomic_structure')
    if paw_structure is None:
        raise ValueError('Missing primary PAW common geometry')
    for actual, expected in (
            (identities['N0']['settings']['cell_bohr'], [np.fromstring(paw_structure.findtext('cell/' + axis), sep=' ') for axis in ('a1', 'a2', 'a3')]),
            (identities['N0']['settings']['positions_bohr'], [np.fromstring(atom.text, sep=' ') for atom in paw_structure.findall('./atomic_positions/atom')])):
        if not np.allclose(actual, finite(expected, (3, 3)), atol=1e-9, rtol=0):
            raise ValueError('NC control is not at the common PAW geometry')
    contrasts = {}
    for quantity in OBSERVABLES:
        if quantity != 'direct_K_gap_ev' and quantity not in metadata['contrasts']:
            continue
        values = {'SOC_N1_minus_N0': variants['N1'][quantity] - variants['N0'][quantity],
            'off_model_N0_minus_S': variants['N0'][quantity] - primary['S'][quantity],
            'on_model_F1_minus_N1': primary['F1'][quantity] - variants['N1'][quantity],
            'total_F1_minus_S': primary['F1'][quantity] - primary['S'][quantity]}
        values['sum_residual_ev'] = sum(values[key] for key in ('SOC_N1_minus_N0', 'off_model_N0_minus_S', 'on_model_F1_minus_N1')) - values['total_F1_minus_S']
        compare_report(values, metadata['contrasts'][quantity])
        contrasts[quantity] = values
    return {'variants': variants, 'contrasts': contrasts, 'matched_settings': identities['N0']['settings'],
        'mesh': identities['N0']['mesh'], 'scope': 'Auxiliary NC K-only contrast; not an isolated PAW SOC effect',
        'native_xml_sha256': {variant: identity['xml_sha256'] for variant, identity in identities.items()}}
