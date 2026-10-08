import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import time

import numpy as np
from pyscf import gto, lib
from gpu4pyscf.dft import rks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay-record', type=Path, required=True)
    arguments = parser.parse_args()
    lib.num_threads(8)
    arguments.output.mkdir(exist_ok=False)
    inputs = json.loads(arguments.inputs.read_text())
    selections = [('tsre-01', 0), ('tssi-01', 0)] + [(identifier, 20) for identifier in (
        'tsre-01', 'tssi-01', 'tsre-01-reversed', 'tssi-01-reversed')]
    report = {'status': 'independent_fresh_RKS_probe_not_full_trajectory_uniqueness', 'task_id': '09',
        'model': 'Same pinned direct GPU4PySCF RKS Hamiltonian; every selected state starts from fresh minao, no candidate density or source used',
        'observations': {}, 'candidate_artifacts': {}, 'complete': False,
        'required_observations': [f'{identifier}/{step}' for identifier, step in selections],
        'trusted_replay_sha256': hashlib.sha256(arguments.replay_record.read_bytes()).hexdigest(),
        'inputs_sha256': hashlib.sha256(arguments.inputs.read_bytes()).hexdigest(),
        'package_versions': {package: version(package) for package in ('pyscf', 'gpu4pyscf-cuda12x', 'pyscf-dispersion')}}
    for identifier, step in selections:
        source = arguments.evidence / 'trajectories' / (identifier + '.json')
        if not source.is_file():
            report.setdefault('missing_observations', []).append(f'{identifier}/{step}')
            continue
        report['candidate_artifacts'][str(source.relative_to(arguments.evidence))] = hashlib.sha256(source.read_bytes()).hexdigest()
        trajectory = json.loads(source.read_text())
        if len(trajectory['frames']) <= step:
            report.setdefault('missing_observations', []).append(f'{identifier}/{step}')
            continue
        frame = trajectory['frames'][step]
        if frame['step'] != step:
            raise ValueError('Unexpected selected frame identity')
        structure = inputs['structures'][trajectory['structure_id']]
        started = time.monotonic()
        with (arguments.output / f'{identifier}-{step}.log').open('w') as log:
            molecule = gto.M(atom=list(zip(structure['symbols'], frame['coordinates_angstrom'])),
                unit='Angstrom', charge=1, spin=0, basis='6-31G(d)', verbose=0, output=None)
            molecule.stdout = log
            molecule.verbose = 4
            molecule.max_memory = 28000
            mean_field = rks.RKS(molecule)
            mean_field.xc = 'B3LYP'
            mean_field.disp = 'd3bj'
            mean_field.grids.level = 1
            mean_field.conv_tol = 1e-8
            mean_field.max_cycle = 150
            mean_field.init_guess = 'minao'
            mean_field.chkfile = None
            energy = float(mean_field.kernel())
            if not mean_field.converged:
                raise RuntimeError('Independent fresh electronic state failed to converge')
            gradient = mean_field.nuc_grad_method().kernel()
            gradient = np.asarray(gradient.get() if hasattr(gradient, 'get') else gradient)
        error = gradient - np.asarray(frame['gradient_hartree_per_bohr'])
        report['observations'][f'{identifier}/{step}'] = {
            'input_trajectory_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'energy_hartree': energy, 'gradient_hartree_per_bohr': gradient.tolist(),
            'energy_difference_hartree': energy - frame['energy_hartree'],
            'max_gradient_difference_hartree_per_bohr': float(np.max(abs(error))),
            'rms_gradient_difference_hartree_per_bohr': float(np.sqrt(np.mean(error ** 2))),
            'wall_seconds': time.monotonic() - started}
        (arguments.output / 'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        print(identifier, step, energy, report['observations'][f'{identifier}/{step}']['max_gradient_difference_hartree_per_bohr'], flush=True)
    report['complete'] = set(report['observations']) == set(report['required_observations'])
    (arguments.output / 'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
