"""Evidence access recovery without changing scientific judgments or thresholds."""

import hashlib
import json
from pathlib import Path


def paper_directories(task_root, tests_root):
    directories = [task_root / "environment/paper", task_root / "solver"]
    if task_root.resolve() == Path("/tests") and tests_root.resolve() == Path("/tests"):
        directories.append(Path("/home/paper"))
    return directories


def reference_catalog(roots, max_chars, read_text):
    text_suffixes = {".txt", ".md", ".json", ".csv", ".toml", ".yaml", ".yml", ".py", ".sh"}
    image_suffixes = {".png", ".jpg", ".jpeg", ".webp"}
    seen = set()
    blocks = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            resolved = path.resolve()
            if not path.is_file() or path.is_symlink() or resolved in seen or path.suffix.lower() in image_suffixes:
                continue
            if not resolved.is_relative_to(root.resolve()):
                continue
            seen.add(resolved)
            heading = "### refs/" + path.relative_to(root).as_posix()
            if path.suffix.lower() in text_suffixes:
                contents = read_text(path, max_chars)
            else:
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                contents = json.dumps(dict(path="refs/" + path.relative_to(root).as_posix(),
                                           format=path.suffix.lower(), size_bytes=path.stat().st_size,
                                           sha256=digest.hexdigest(), binary_content_not_decoded=True))
                contents += "\nUse inspect_numeric and the numeric evidence tools to inspect these reference arrays."
            blocks.append(heading + "\n" + contents)
    text = "\n\n".join(blocks)
    if len(text) <= max_chars:
        return text
    return text[:max_chars // 2] + "\n<<REFS_TRUNCATED: inspect the referenced files with tools>>\n" + text[-max_chars // 2:]


class EvidenceValidationError(ValueError):
    def __init__(self, message, diagnostics):
        super().__init__(message)
        self.diagnostics = diagnostics


class EvidenceRecovery:
    def __init__(self, max_reasks=2):
        self.max_reasks = max_reasks
        self.rejected = []

    def validate_or_reask(self, final, validate, rounds_used, max_tool_rounds):
        try:
            validate(final)
        except ValueError as error:
            trace = final.get("_tool_trace") or []
            self.rejected.append(dict(
                validation_error=str(error), tool_rounds_used=rounds_used, tool_calls=len(trace),
                completion={key: final.get(key) for key in ("score", "evidence_access", "reason", "missing_evidence")},
                tool_outcomes=[dict(tool=entry.get("tool"), arguments=entry.get("arguments"),
                                    result_excerpt=json.dumps(entry.get("result"), ensure_ascii=False, default=str)[:6000])
                               for entry in trace[-8:]],
            ))
            if len(self.rejected) > self.max_reasks or rounds_used >= max_tool_rounds:
                raise EvidenceValidationError(str(error), self.rejected) from error
            return (
                "The previous completion is not a valid assessment because evidence validation failed: "
                + str(error)
                + "\nThis is evaluator feedback, not evidence that the candidate should pass or fail. "
                "Keep the scientific requirements and numerical thresholds unchanged. "
                "Use the available evidence tools before issuing another verdict. Start with "
                "list_evidence_files(root_kind='submission'), then inspect relevant contents; "
                "use describe_scientific_metrics to obtain the required bindings before numerical derivation. "
                "Read the supplied unit/phase conventions instead of guessing. A failed tool call is "
                "not proof that evidence is missing. If the candidate genuinely fails, return score=0 "
                "with the inspected scientific reason. If access still fails, report tool_error honestly. "
                "Do not invent tool results or change a valid scientific failure into a pass."
            )
        return None
