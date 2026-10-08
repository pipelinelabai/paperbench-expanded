"""Shared scientific scoring rules for embodied PaperBench High-Difficulty and Expanded Tasks tasks."""

import re


HEALTH_KEYS = {"coverage", "behavior", "stop_behavior"}
JUDGE_LEVELS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _clip(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, float(value)))


def metric_score(reported, metric, value, default_floor, default_target, direction="higher"):
    """Map a measured metric continuously from a failure floor to a frozen target."""
    spec = ((reported or {}).get("scoring") or {}).get(metric, {})
    floor = float(spec.get("floor", default_floor))
    target = float(spec.get("target", default_target))
    direction = spec.get("direction", direction)

    if direction == "higher":
        denominator = target - floor
        score = _clip((float(value) - floor) / denominator) if denominator > 0 else 0.0
    elif direction == "lower":
        denominator = floor - target
        score = _clip((floor - float(value)) / denominator) if denominator > 0 else 0.0
    else:
        raise ValueError("unsupported metric direction: %s" % direction)

    source = spec.get("target_source", "unspecified")
    alignment = spec.get("paper_alignment", "unspecified")
    return score, (
        "%s=%0.4g, floor=%0.4g, target=%0.4g, direction=%s, "
        "target_source=%s, paper_alignment=%s"
        % (metric, float(value), floor, target, direction, source, alignment)
    )


def parse_judge_score(content):
    """Parse a judge score and quantize it to the supported five-level scale."""
    match = re.search(r"(?im)^\s*SCORE\s*:\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*$", content or "")
    if not match:
        match = re.search(r"(?i)\bscore\s*[:=]\s*(0(?:\.\d+)?|1(?:\.0+)?)\b", content or "")
    if not match:
        return 0.0
    value = _clip(float(match.group(1)))
    return min(JUDGE_LEVELS, key=lambda level: abs(level - value))


def coverage_gate(coverage, tasks_seen, n_tasks, zero_at=0.80, full_at=0.95):
    """Continuous completeness gate; task coverage remains independently binding."""
    if full_at <= zero_at:
        raise ValueError("full_at must be greater than zero_at")
    coverage_component = _clip((float(coverage) - zero_at) / (full_at - zero_at))
    if int(n_tasks or 0) <= 0:
        task_component = 0.0
    else:
        task_component = _clip(float(tasks_seen or 0) / float(n_tasks))
    return min(coverage_component, task_component)


def finalize_reward(raw_total, leaf_results, c_leaf_ids):
    """Apply coverage and a science-dependent cap to the rubric-weighted raw score."""
    science = []
    coverage = 1.0
    for leaf_id, key in c_leaf_ids.items():
        result = leaf_results.get(leaf_id)
        if result is None:
            continue
        if key == "coverage":
            coverage = float(result.get("score", 0.0))
        elif key not in HEALTH_KEYS:
            science.append((float(result.get("weight", 0.0)), float(result.get("score", 0.0))))

    science_weight = sum(weight for weight, _ in science)
    science_score = (
        sum(weight * score for weight, score in science) / science_weight
        if science_weight > 0
        else 0.0
    )
    science_cap = 0.25 + 0.75 * science_score
    final = coverage * min(float(raw_total), science_cap)
    return final, {
        "raw_total": float(raw_total),
        "science_score": science_score,
        "science_cap": science_cap,
        "coverage_gate": coverage,
    }
