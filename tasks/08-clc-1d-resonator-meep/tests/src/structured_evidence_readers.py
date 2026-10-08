import hashlib
import json
from pathlib import Path


MAX_TEXT_BYTES = 64 * 1024 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def file_details(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"path": str(path), "sha256": digest.hexdigest(), "size_bytes": path.stat().st_size}


def read_text_evidence(path, max_chars, offset=0):
    path = Path(path)
    if not isinstance(offset, int) or isinstance(offset, bool) or not 0 <= offset <= MAX_TEXT_BYTES:
        raise ValueError("Text offset must be a bounded nonnegative character index")
    if max_chars < 1:
        raise ValueError("Text inspection length must be positive")
    with path.open(encoding="utf-8", errors="strict") as stream:
        stream.read(offset)
        text = stream.read(max_chars + 1)
    truncated = len(text) > max_chars
    return dict(file_details(path), text=text[:max_chars], offset=offset, truncated=truncated,
                next_offset=offset + max_chars if truncated else None)


def read_json_evidence(path, max_chars, pointer="", offset=0):
    path = Path(path)
    if path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError("JSON evidence exceeds the bounded parsing budget")
    if max_chars < 1 or not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise ValueError("Use a positive output budget and an exact JSON pointer")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("JSON child offset must be a nonnegative integer")
    with path.open(encoding="utf-8-sig") as stream:
        value = json.load(stream, object_pairs_hook=unique_object)
    for token in pointer.split("/")[1:] if pointer else []:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict):
            value = value[token]
        elif isinstance(value, list) and token.isdigit() and str(int(token)) == token:
            value = value[int(token)]
        else:
            raise ValueError("JSON pointer does not select an existing value")
    report = dict(file_details(path), pointer=pointer)
    if offset == 0 and len(json.dumps(value, ensure_ascii=False)) <= max_chars:
        return dict(report, json=value, truncated=False)
    if isinstance(value, dict):
        children = list(value.items())
    elif isinstance(value, list):
        children = list(enumerate(value))
    else:
        return dict(report, truncated=True, selected_type=type(value).__name__,
                    instruction="Selected scalar exceeds the display budget; inspect its source through paginated read_text_file.")
    entries = []
    for key, child in children[offset:offset + 60]:
        token = str(key).replace("~", "~0").replace("/", "~1")
        entry = {"pointer": pointer + "/" + token, "type": type(child).__name__}
        if isinstance(child, (dict, list, str)):
            entry["length"] = len(child)
        elif child is None or isinstance(child, (int, float, bool)):
            entry["value"] = child
        if len(json.dumps(entries + [entry], ensure_ascii=False)) > max_chars:
            break
        entries.append(entry)
    next_offset = offset + len(entries)
    return dict(report, truncated=True, children=entries, child_count=len(children), offset=offset,
                next_offset=next_offset if entries and next_offset < len(children) else None,
                instruction="JSON was parsed completely, not truncated before parsing. Read an exact child pointer; use next_offset to list remaining children or inspect_numeric for arrays.")
