import argparse
import json
import math
from collections import Counter
from pathlib import Path


def read_json(path):
    try:
        result = path.read_text()
        value = json.loads(result)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def trial_score(trial):
    logs = trial / 'verifier'
    result = read_json(logs / 'result.json')
    publication = read_json(logs / 'publication.json')
    failure = read_json(logs / 'failure.json')
    if (failure.get('kind') == 'infra'
            or any((logs / name).is_file() for name in (
                'infra_failure.json', 'private/infrastructure_error.json', 'private/harness_failure.json'))):
        return None, 'infrastructure_error'
    if (result.get('judge_ok') is False or result.get('n_judge_errors')
            or (logs / 'score_withheld.json').exists()
            or (publication and not publication.get('eligible_for_ranking', False))):
        return None, publication.get('status') or result.get('status') or 'score_withheld'
    if result.get('status') in {'dry_run', 'scored_with_judge_errors', 'judge_unavailable',
                              'judge_error', 'judge_unavailable_partial', 'infrastructure_error'}:
        return None, result['status']
    try:
        score = float((logs / 'reward.txt').read_text())
    except (OSError, ValueError):
        return None, 'no_score'
    if not math.isfinite(score) or not 0 <= score <= 1:
        return None, 'invalid_score'
    if publication and publication.get('ranking_score') != score:
        expected = publication.get('ranking_score')
        if not isinstance(expected, (int, float)) or not math.isclose(expected, score, abs_tol=1e-6):
            return None, 'inconsistent_publication'
    return score, 'scored'


def summarize(job):
    rows = []
    trials = {path.parent for name in ('result.json', 'config.json', 'verifier', 'agent')
              for path in Path(job).glob('*/' + name)}
    for trial in sorted(trials):
        result = read_json(trial / 'result.json')
        score, status = trial_score(trial)
        rows.append({'trial': trial.name, 'task': result.get('task_name'),
                     'model': (result.get('agent_info') or {}).get('model_info', {}),
                     'score': score, 'status': status})
    scores = [row['score'] for row in rows if row['score'] is not None]
    return {'scientific_mean': sum(scores) / len(scores) if scores else None,
            'scored_trials': len(scores), 'total_trials': len(rows),
            'unscored_trials': len(rows) - len(scores),
            'status_counts': dict(Counter(row['status'] for row in rows)),
            'note': 'Missing or infrastructure-blocked scores are not zeros. Report coverage and failure counts with the mean; do not compare incomplete coverage as a complete benchmark.',
            'trials': rows}


def main():
    parser = argparse.ArgumentParser(description='Summarize scientific scores without zero-filling infrastructure failures.')
    parser.add_argument('job', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.job), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
