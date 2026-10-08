from __future__ import annotations

import base64
import hashlib
import json
import math
from pathlib import Path
import time
import urllib.request
import urllib.parse

from evidence_io import save


SYSTEM = (Path(__file__).resolve().parents[1] / 'config/judge_prompt.md').read_text().partition('\n\n## Task-specific judging rules\n\n')[0]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, stream, code, message, headers, new_url):
        return None


def parse_review(text, expected_ids):
    cleaned = text.strip()
    if cleaned.startswith("```json") and cleaned.endswith("```"):
        cleaned = cleaned[7:-3].strip()
    elif cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()
    review = json.loads(cleaned)
    if review.get("status") not in {"scored", "insufficient_evidence"}:
        raise ValueError("External judge did not provide a recognized assessment status")
    leaves = review.get("leaves")
    if not isinstance(leaves, dict) or set(leaves) != set(expected_ids):
        raise ValueError("External judge leaf coverage mismatch")
    for leaf in leaves.values():
        if not isinstance(leaf, dict) or not isinstance(leaf.get("rationale"), str) or not leaf["rationale"].strip():
            raise ValueError("External assessment lacks rationale")
        if not isinstance(leaf.get("evidence"), list) or not leaf["evidence"]:
            raise ValueError("External assessment lacks evidence references")
        fraction = leaf.get("fraction")
        if fraction is None and review["status"] == "insufficient_evidence":
            continue
        if isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
            raise ValueError("External judge returned an invalid fraction")
    return review


def judge_settings(environ):
    model = environ.get('JUDGE_MODEL', '').strip()
    key = environ.get('JUDGE_API_KEY', '').strip()
    base = environ.get('JUDGE_BASE_URL', '').strip().rstrip('/')
    if not all((model, key, base)) or any('${' in value for value in (model, key, base)):
        raise ValueError('Dedicated JUDGE_MODEL, JUDGE_API_KEY and JUDGE_BASE_URL are required')
    parsed = urllib.parse.urlsplit(base)
    if (parsed.scheme not in {'https', 'http'} or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('Judge base URL must not contain credentials, query or fragment')
    transport = environ.get('PBX_LLM_TRANSPORT', 'openai')
    if transport == 'auto':
        transport = 'anthropic' if parsed.hostname == 'api.anthropic.com' else 'openai'
    if transport not in {'openai', 'anthropic'}:
        raise ValueError('Unsupported judge transport')
    timeout = float(environ.get('JUDGE_TIMEOUT_SEC', '300'))
    if not math.isfinite(timeout) or not 1 <= timeout <= 360:
        raise ValueError('Judge timeout must be between 1 and 360 seconds')
    if transport == 'anthropic' and not parsed.path.rstrip('/'):
        base += '/v1'
    endpoint = base + ('/messages' if transport == 'anthropic' else '/chat/completions')
    return {'model': model, 'key': key, 'endpoint': endpoint,
            'transport': transport, 'timeout': timeout}


def call_judge(settings, document, images, leaf_ids, logs):
    content = [{'type': 'text', 'text': document}]
    for label, path in images:
        encoded = base64.b64encode(path.read_bytes()).decode('ascii')
        mime = 'image/png' if path.suffix.lower() == '.png' else 'image/jpeg'
        content.append({'type': 'text', 'text': 'Rendered evidence: ' + label})
        if settings['transport'] == 'anthropic':
            content.append({'type': 'image', 'source': {'type': 'base64', 'media_type': mime, 'data': encoded}})
        else:
            content.append({'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{encoded}'}})
    payload = {'model': settings['model'], 'max_tokens': 6000,
               'messages': [{'role': 'user', 'content': content}]}
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + settings['key']}
    if settings['transport'] == 'anthropic':
        payload['system'] = SYSTEM
        headers.update({'x-api-key': settings['key'], 'anthropic-version': '2023-06-01'})
    else:
        payload['messages'].insert(0, {'role': 'system', 'content': SYSTEM})
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    save(logs / 'judge_request.json', payload)
    save(logs / 'judge_request_binding.json', {
        'request_sha256': hashlib.sha256(body).hexdigest(),
        'endpoint_sha256': hashlib.sha256(settings['endpoint'].encode()).hexdigest(),
        'model_requested': settings['model'], 'transport': settings['transport'],
        'prior_scores_supplied': False, 'retry_policy': 'one request; no model substitution'})
    request = urllib.request.Request(settings['endpoint'], data=body, headers=headers, method='POST')
    started = time.monotonic()
    with urllib.request.build_opener(NoRedirect).open(request, timeout=settings['timeout']) as response:
        raw_bytes = response.read(4 * 1024 * 1024 + 1)
    (logs / 'judge_response.raw').write_bytes(raw_bytes)
    if len(raw_bytes) > 4 * 1024 * 1024:
        raise ValueError('External judge response exceeds verifier allowance')
    raw = json.loads(raw_bytes)
    save(logs / 'judge_response.json', raw)
    save(logs / 'judge_response_binding.json', {
        'response_sha256': hashlib.sha256(raw_bytes).hexdigest(),
        'model_requested': settings['model'], 'model_returned': raw.get('model'),
        'response_id': raw.get('id'), 'wall_seconds': time.monotonic() - started,
        'usage': raw.get('usage')})
    if settings['transport'] == 'anthropic':
        if raw.get('stop_reason') != 'end_turn':
            raise ValueError('External judge did not finish a complete turn')
        text = '\n'.join(part.get('text', '') for part in raw.get('content', []) if part.get('type') == 'text')
    else:
        choices = raw.get('choices', [])
        if len(choices) != 1 or choices[0].get('finish_reason') != 'stop':
            raise ValueError('External judge did not return one complete assessment')
        text = choices[0]['message']['content']
    review = parse_review(text, leaf_ids)
    save(logs / 'judge_review.json', review)
    if review['status'] != 'scored':
        raise ValueError('External judge requires additional evidence; do not fabricate leaf scores')
    return review
