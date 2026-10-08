import math
from decimal import Decimal


SCORING_DIMENSIONS = (
    {"id": "A", "title": "Structural Modeling", "points": 10},
    {"id": "B", "title": "Solver Config & Run Evidence Audit", "points": 10},
    {"id": "C", "title": "Result Analysis", "points": 80},
)
SCORING_SCHEME = "abc-10-10-80"


def validate_scoring(rubric):
    if rubric.get("scheme") != SCORING_SCHEME:
        raise ValueError("Unexpected scoring scheme")
    if rubric.get("scoring_dimensions") != list(SCORING_DIMENSIONS):
        raise ValueError("Scoring dimensions must be A=10, B=10, C=80")
    if rubric.get("total_points") != 100:
        raise ValueError("The total must be 100 points")
    totals = {dimension["id"]: 0 for dimension in SCORING_DIMENSIONS}
    identifiers = set()
    for block in rubric["blocks"]:
        if not block["checks"]:
            raise ValueError("Empty score block")
        for item in [block, *block["checks"]]:
            identifier = item["id"]
            if identifier in identifiers:
                raise ValueError(f"Duplicate score identifier: {identifier}")
            identifiers.add(identifier)
            if type(item["points"]) is not int or item["points"] <= 0:
                raise ValueError(f"Invalid point allocation: {identifier}")
        if sum(check["points"] for check in block["checks"]) != block["points"]:
            raise ValueError(f"Block point mismatch: {block['id']}")
        for check in block["checks"]:
            dimension = check.get("dimension")
            if dimension not in totals:
                raise ValueError(f"Unknown scoring dimension: {dimension}")
            totals[dimension] += check["points"]
    expected = {dimension["id"]: dimension["points"] for dimension in SCORING_DIMENSIONS}
    if totals != expected:
        raise ValueError(f"Dimension point mismatch: {totals}")
    return totals


def export_hierarchy(rubric):
    validate_scoring(rubric)
    sections = []
    for dimension in SCORING_DIMENSIONS:
        leaves = []
        for block in rubric["blocks"]:
            for check in block["checks"]:
                if check["dimension"] != dimension["id"]:
                    continue
                leaves.append({
                    "id": check["id"],
                    "title": f"{block['title']} / {check['id']}",
                    "weight": float(Decimal(check["points"]) * 100 / dimension["points"]),
                    "effective_points": check["points"],
                    "requirements": check["criterion"],
                    "evidence_gates": check["requires"],
                    "research_block_id": block["id"],
                    "sub_tasks": [],
                })
        sections.append({
            "id": dimension["id"],
            "title": dimension["title"],
            "weight": dimension["points"],
            "sub_tasks": leaves,
        })
    return {
        "id": f"{rubric['task_id']}-{SCORING_SCHEME}",
        "task_id": rubric["task_id"],
        "requirements": rubric["dependency_semantics"],
        "weight_semantics": "Root dimension weights sum to 100; child weights sum to 100 within each dimension. Multiply each level once. Research blocks are a crosswalk, not additional weighted parents.",
        "sub_tasks": sections,
    }


def aggregate_scores(rubric, scores):
    validate_scoring(rubric)
    checks = {check["id"]: check for block in rubric["blocks"] for check in block["checks"]}
    if set(scores) != set(checks):
        raise ValueError("Exactly one inspected score per check is required; missing scores are not zero")
    earned = {dimension["id"]: Decimal(0) for dimension in SCORING_DIMENSIONS}
    for identifier, check in checks.items():
        score = scores[identifier]
        if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError(f"Invalid score for {identifier}")
        earned[check["dimension"]] += Decimal(str(score)) * check["points"]
    total = sum(earned.values())
    return {
        "status": "arithmetic_only",
        "dimension_points": {dimension: float(points) for dimension, points in earned.items()},
        "score_points": float(total),
        "reward": float(total / 100),
    }


def scoring_tables(rubric):
    validate_scoring(rubric)
    lines = [
        "| Dimension | Points |",
        "|---|---:|",
        *[f"| {dimension['id']} — {dimension['title']} | {dimension['points']} |" for dimension in SCORING_DIMENSIONS],
        "",
        "These are scientific scoring dimensions, not a deterministic/LLM judging ratio. Each check belongs to exactly one dimension. The research-block crosswalk below describes the same 100 points; it is not a second scoring layer.",
        "",
        "| Research block | A | B | C | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    for block in rubric["blocks"]:
        allocation = {
            dimension["id"]: sum(check["points"] for check in block["checks"] if check["dimension"] == dimension["id"])
            for dimension in SCORING_DIMENSIONS
        }
        lines.append(f"| {block['title']} | {allocation['A']} | {allocation['B']} | {allocation['C']} | {block['points']} |")
    lines.extend([
        "| **Total** | **10** | **10** | **80** | **100** |",
        "",
        "A evaluates the fixed physical model and its implementation. B evaluates solver configuration and authentic execution of the required cases/controls. C evaluates recomputed scientific quantities, numerical validation and interpretation. A complete run can earn B credit without establishing a correct C result; a report without native evidence cannot earn dependent C credit. Evidence prerequisites do not create extra points or a global all-or-nothing gate.",
    ])
    return "\n".join(lines)
