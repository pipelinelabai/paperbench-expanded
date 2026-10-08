from __future__ import annotations

import hashlib
import json
import math

from evidence_io import load


def flatten(tree, routes):
    if tree.get('id') != 'root' or tree.get('weight') != 100:
        raise ValueError('Expected the standard root scoring tree')
    checksum = hashlib.sha256(json.dumps(tree, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if checksum != routes.get('rubric_sha256'):
        raise ValueError('Scoring routes are not bound to the authoritative rubric')
    seen, leaves = set(), []

    def visit(node, factor):
        identifier = node['id']
        if identifier in seen:
            raise ValueError('Duplicate rubric node: ' + identifier)
        seen.add(identifier)
        weight = node['weight']
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or not 0 < weight <= 100:
            raise ValueError('Invalid rubric weight')
        current = factor * weight / 100
        children = node.get('sub_tasks', [])
        if children:
            if not math.isclose(sum(child['weight'] for child in children), 100, rel_tol=0, abs_tol=1e-9):
                raise ValueError('Sibling weights must sum to 100: ' + identifier)
            for child in children:
                visit(child, current)
        else:
            route = routes['leaves'][identifier]
            if route['route'] not in {'code', 'review'}:
                raise ValueError('Unknown criterion scoring route')
            leaves.append({'id': identifier, 'title': node['title'], 'group': route['group'],
                           'points': round(current * 100, 12), 'route': route['route'],
                           'requirement': node['description']})

    visit(tree, 1.0)
    if {leaf['id'] for leaf in leaves} != set(routes['leaves']):
        raise ValueError('Scoring routes must exactly cover the rubric leaves')
    return {'revision': routes['rubric_revision'], 'total_points': 100, 'leaves': leaves}


def load_rubric(tests):
    return flatten(load(tests / 'rubric.json'), load(tests / 'config/evaluation.json')['scoring_routes'])
