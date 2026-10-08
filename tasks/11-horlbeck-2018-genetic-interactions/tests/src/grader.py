from __future__ import annotations

import json
import math
import os

from evidence_io import digest, load, save, tree_manifest
from judge_review import call_judge, judge_settings
from rubric_tree import load_rubric


def combine(rubric, numeric, review):
    if numeric.get('status') != 'numeric_scored' or review.get('status') != 'scored':
        raise ValueError('Both independent numerical and explanatory assessment must complete')
    leaves = rubric['leaves']
    if len({leaf['id'] for leaf in leaves}) != len(leaves) or sum(leaf['points'] for leaf in leaves) != 100:
        raise ValueError('Malformed frozen rubric')
    assessments = {'code': numeric, 'review': review}
    if {leaf['route'] for leaf in leaves} != set(assessments):
        raise ValueError('Unknown scoring route')
    for route, assessment in assessments.items():
        if set(assessment['leaves']) != {leaf['id'] for leaf in leaves if leaf['route'] == route}:
            raise ValueError('Scored leaves must exactly cover their frozen rubric route')
    result = []
    for leaf in leaves:
        assessment = assessments[leaf['route']]['leaves'][leaf['id']]
        fraction = assessment['fraction']
        if isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
            raise ValueError('Invalid scored fraction')
        result.append({**leaf, 'fraction': fraction, 'earned': leaf['points'] * fraction,
                       'rationale': assessment.get('rationale', 'See independent numeric_score.json')})
    return {'status': 'scored', 'reward': sum(leaf['earned'] for leaf in result) / 100,
            'possible_points': 100, 'leaves': result, 'judge_ok': True,
            'historical_score_inherited': False}


def packet(tests, submission, paper, logs, numeric):
    evidence = submission / 'results/horlbeck_gi_reproduction'
    rubric = load_rubric(tests)
    explanatory = [leaf for leaf in rubric['leaves'] if leaf['route'] == 'review']
    files = {'task/instruction.md': tests / 'config/public_contract.md'}
    for name in ('paper.md', 'addendum.md', 'conventions.json', 'blacklist.md', 'data_manifest.json'):
        files['paper/' + name] = paper / name
    for relative in load(logs / 'source_manifest_before.json'):
        path = submission / relative
        if path.suffix.lower() in {'.py', '.sh', '.md', '.txt', '.toml', '.yaml', '.yml', '.json', '.r', '.jl'}:
            files['submission/' + relative] = path
    for path in sorted(evidence.iterdir()):
        if path.is_file() and path.suffix.lower() in {'.md', '.json'}:
            files['results/' + path.name] = path
    null_summary = evidence / 'identity_null/summary.json'
    if null_summary.is_file():
        files['results/identity_null/summary.json'] = null_summary
    document = ['# Frozen explanatory rubric\n' + json.dumps(explanatory, indent=2),
                '# Trusted judge instructions\n' + (tests / 'config/judge_prompt.md').read_text().split('\n\n## Task-specific judging rules\n\n', 1)[1]]
    hashes = {name: digest(tests / name) for name in
              ('rubric.json', 'config/evaluation.json', 'config/judge_prompt.md')}
    total = 0
    for label, path in files.items():
        total += path.stat().st_size
        if total > 1800000:
            raise ValueError('Evidence packet exceeds automatic-review allowance; manual adaptation required')
        numbered = '\n'.join(f'{number}: {line}' for number, line in enumerate(path.read_text().splitlines(), 1))
        document.append(f'\n# Evidence: {label}\n{numbered}')
        hashes[label] = digest(path)
    receipt = load(logs / 'native_run.json')
    receipt.update(numerical_checks=sum(len(leaf['checks']) for leaf in numeric['leaves'].values()),
                   numerical_check_failures=sum(check['fraction'] < 1 for leaf in numeric['leaves'].values() for check in leaf['checks']),
                   limits='Numerical agreement does not establish correct interpretation; no previous review supplied.')
    document.append('\n# Trusted execution and numerical verification\n' + json.dumps(receipt, indent=2))
    images = [('results/' + path.relative_to(evidence).as_posix(), path)
              for path in sorted(evidence.rglob('*')) if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg'}]
    if len(images) > 16 or sum(path.stat().st_size for _, path in images) > 20 * 1024 * 1024:
        raise ValueError('Figure packet needs verifier adaptation rather than silent truncation')
    for label, path in images:
        hashes[label] = digest(path)
    save(logs / 'judge_packet_manifest.json', hashes)
    return '\n'.join(document), images, [leaf['id'] for leaf in explanatory]


def assess(tests, submission, paper, logs, numeric):
    evidence = submission / 'results/horlbeck_gi_reproduction'
    before = load(logs / 'evidence_manifest_before.json')
    if tree_manifest(evidence) != before:
        raise ValueError('Evidence changed before external judging')
    document, images, leaf_ids = packet(tests, submission, paper, logs, numeric)
    review = call_judge(judge_settings(os.environ), document, images, leaf_ids, logs)
    after = tree_manifest(evidence)
    save(logs / 'evidence_manifest_after.json', after)
    if after != before or tree_manifest(submission, exclude_results=True) != load(logs / 'source_manifest_before.json'):
        raise ValueError('Frozen source or evidence changed during judging')
    rubric = load_rubric(tests)
    result = combine(rubric, numeric, review)
    native = load(logs / 'native_run.json')
    result['replay_completed'] = native['native_exit_code'] == 0
    result['native_exit_code'] = native['native_exit_code']
    result['partial_scientific_evidence'] = (
        not result['replay_completed'] or numeric['completed_omissions'] != numeric['required_omissions'])
    result.update(rubric_revision=rubric['revision'], rubric_sha256=digest(tests / 'rubric.json'),
                  numeric_score_sha256=digest(logs / 'numeric/numeric_score.json'),
                  review_sha256=digest(logs / 'judge_review.json'))
    save(logs / 'result.json', result)
    save(logs / 'publication.json', {'status': 'scored', 'eligible_for_ranking': True,
                                    'ranking_score': result['reward']})
    with (logs / 'reward.txt').open('x') as stream:
        stream.write(format(result['reward'], '.12g') + '\n')


def evaluate():
    from pathlib import Path
    from evidence_io import withhold

    tests = Path(__file__).resolve().parents[1]
    submission, paper, logs = Path('/home/submission'), Path('/home/paper'), Path('/logs/verifier')
    if os.getuid() != 0:
        raise RuntimeError('Scoring must run in the trusted verifier after clean replay')
    try:
        receipt, integrity = load(logs / 'native_run.json'), load(logs / 'integrity.json')
        if (receipt['network'] != 'none'
                or not receipt['read_only_source'] or not integrity['frozen_source_matches']
                or not integrity['empty_initial_results'] or not integrity['input_bytes_unchanged']):
            raise ValueError('A trusted, unchanged clean replay is required before scoring')
        inputs = load(logs / 'input_manifest_before.json')
        if inputs != {'paper': tree_manifest(paper), 'data': tree_manifest(Path('/home/data/horlbeck'))}:
            raise ValueError('Trusted input bytes changed after replay')
        if (logs / 'result.json').exists() or (logs / 'score_withheld.json').exists():
            raise FileExistsError('Never overwrite an existing assessment; use a fresh trial')
        assess(tests, submission, paper, logs, load(logs / 'numeric/numeric_score.json'))
        return 0
    except Exception as error:
        withhold(logs, 'external_assessment', error)
        return 1
