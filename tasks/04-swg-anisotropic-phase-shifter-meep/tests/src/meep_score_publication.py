import json
import math
import os
import shutil
import stat
from pathlib import Path


class InvalidGrade(ValueError):
    pass


def block_disabled_scoring(tests, logs):
    marker = Path(tests) / 'SCORING_DISABLED'
    if not marker.is_file():
        return False
    logs = Path(logs)
    logs.mkdir(parents=True, exist_ok=True)
    for name in ('reward.txt', 'reward.json', 'reward_partial.txt'):
        (logs / name).unlink(missing_ok=True)
    record = {
        'status': 'scoring_disabled', 'score': None,
        'reason': 'Scoring is explicitly disabled for this task.',
        'action': 'Do not publish a reward while scoring is disabled.',
    }
    (logs / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    (logs / 'score_withheld.json').write_text(json.dumps(record, indent=2) + '\n')
    return True


def prepare_source_review(logs):
    logs = Path(logs)
    source = logs / 'source_submission'
    evidence = logs / 'candidate_outputs'
    if not source.is_dir() or source.is_symlink():
        raise OSError('No trusted source snapshot is available for review')
    if evidence.exists():
        for current, directories, files in os.walk(evidence):
            Path(current).chmod(0o755)
        shutil.rmtree(evidence)
    evidence.mkdir(mode=0o755)
    for current, directories, files in os.walk(source, followlinks=False):
        directories[:] = [name for name in directories if not (Path(current) / name).is_symlink()]
        target = evidence / Path(current).relative_to(source)
        target.mkdir(parents=True, exist_ok=True)
        for name in files:
            path = Path(current) / name
            if stat.S_ISREG(path.lstat().st_mode):
                shutil.copyfile(path, target / name)
    record = json.loads((logs / 'candidate_replay.json').read_text())
    record['evidence_scope'] = 'source_only'
    record['review_note'] = 'Replay setup failed. Assess source evidence independently; generated outputs are unavailable.'
    (evidence / 'candidate_replay.json').write_text(json.dumps(record, indent=2) + '\n')


def withhold_replay_setup_error(logs, reason):
    logs = Path(logs)
    logs.mkdir(parents=True, exist_ok=True)
    for name in ('reward.txt', 'reward.json', 'reward_partial.txt'):
        (logs / name).unlink(missing_ok=True)
    try:
        previous = json.loads((logs / 'result.json').read_text())
    except (OSError, ValueError):
        previous = {}
    record = {'status': 'replay_infrastructure_error', 'score': None, 'reason': reason,
              'diagnostic_score': previous.get('score', previous.get('diagnostic_score')),
              'action': 'Repair the evaluator replay setup or review the source/output inventory, then replay the same frozen submission. Do not resample the model.'}
    for name in ('result.json', 'score_withheld.json'):
        (logs / name).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')


def rubric_weights(node, inherited=1.0):
    children = node.get('sub_tasks') or []
    if not children:
        return {node['id']: inherited}
    weights = [float(child['weight']) for child in children]
    if not all(math.isfinite(weight) and weight > 0 for weight in weights):
        raise InvalidGrade('Rubric contains invalid weights')
    denominator = sum(weights)
    result = {}
    for child, weight in zip(children, weights):
        leaves = rubric_weights(child, inherited * weight / denominator)
        if result.keys() & leaves.keys():
            raise InvalidGrade('Rubric contains duplicate leaf IDs')
        result.update(leaves)
    return result


def validated_score(result, grades, rubric):
    if result.get('status') != 'scored':
        raise InvalidGrade('Only a complete, error-free score may be published')
    if result.get('n_judge_errors') != 0:
        raise InvalidGrade('Missing judge status or judge-side errors')
    errors = result.get('judge_errors') or {}
    if errors.get('n_errors', 0) != 0:
        raise InvalidGrade('Judge error details contradict the summary')
    expected = rubric_weights(rubric)
    if not isinstance(grades, list) or len(grades) != len(expected):
        raise InvalidGrade('Incomplete rubric coverage')
    observed = set()
    total = 0.0
    for grade in grades:
        leaf_id = grade.get('leaf_id')
        if leaf_id not in expected or leaf_id in observed:
            raise InvalidGrade('Unknown or duplicate leaf ID')
        observed.add(leaf_id)
        value = grade.get('score')
        weight = grade.get('effective_weight')
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidGrade('Non-numeric leaf score')
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise InvalidGrade('Leaf score is outside [0, 1]')
        if not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise InvalidGrade('Invalid effective weight')
        if not math.isclose(weight, expected[leaf_id], rel_tol=1e-8, abs_tol=1e-10):
            raise InvalidGrade('Effective weight differs from the frozen rubric')
        judgement = grade.get('judge_json') or {}
        if grade.get('error') or grade.get('judge_error') or judgement.get('error'):
            raise InvalidGrade('A leaf contains an unresolved judge error')
        total += value * weight
    reported = result.get('score')
    if isinstance(reported, bool) or not isinstance(reported, (int, float)):
        raise InvalidGrade('Missing numeric total')
    if not math.isfinite(reported) or not math.isclose(total, reported, abs_tol=1e-6):
        raise InvalidGrade('Published total differs from the rubric-weighted score')
    return total


def withhold_invalid_score(result_path, rubric_path, grades_path, logs):
    logs = Path(logs)
    try:
        result = json.loads(Path(result_path).read_text())
        grades = json.loads(Path(grades_path).read_text())
        rubric = json.loads(Path(rubric_path).read_text())
        return validated_score(result, grades, rubric)
    except (InvalidGrade, ValueError, KeyError, TypeError, OSError) as error:
        logs.mkdir(parents=True, exist_ok=True)
        for name in ['reward.txt', 'reward.json']:
            (logs / name).unlink(missing_ok=True)
        record = {'status': 'judge_infrastructure_error', 'score': None,
                  'reason': str(error), 'source_result': str(result_path),
                  'action': 'Retry the judge on the identical frozen submission; do not resample the solver.'}
        (logs / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
        (logs / 'score_withheld.json').write_text(json.dumps(record, indent=2) + '\n')
        raise InvalidGrade(str(error)) from error
