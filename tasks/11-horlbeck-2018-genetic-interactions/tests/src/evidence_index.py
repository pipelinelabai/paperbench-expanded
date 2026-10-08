from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def canonical(name):
    return ''.join(character for character in str(name).lower() if character.isalnum())


def load_npz(path):
    with np.load(path, allow_pickle=False) as archive:
        return {name: archive[name] for name in archive.files}


def read_columns(path):
    return [str(column) for column in pd.read_csv(path, nrows=0, keep_default_na=False).columns]


class EvidenceIndex:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.files = [path for path in sorted(self.root.rglob('*')) if path.is_file()]
        self._keys = {}
        self._arrays = {}

    def relative(self, path):
        return path.relative_to(self.root).as_posix()

    def arrays(self, path):
        if path not in self._arrays:
            try:
                self._arrays[path] = load_npz(path)
            except Exception:
                self._arrays[path] = {}
        return self._arrays[path]

    def keys(self, path):
        if path not in self._keys:
            self._keys[path] = self._read_keys(path)
        return self._keys[path]

    def _read_keys(self, path):
        suffix = path.suffix.lower()
        try:
            if suffix == '.npz':
                return {canonical(name) for name in self.arrays(path)}
            if suffix in {'.csv', '.gz'}:
                return {canonical(name) for name in read_columns(path)}
            if suffix == '.json':
                record = json.loads(path.read_text())
                return {canonical(key) for key in record} if isinstance(record, dict) else set()
        except Exception:
            return set()
        return set()

    def search(self, suffixes, required=(), any_of=(), scope=None):
        required = {canonical(key) for key in required}
        any_of = {canonical(key) for key in any_of}
        found = []
        for path in self.files:
            if path.suffix.lower() not in suffixes:
                continue
            if scope is not None and not path.is_relative_to(scope):
                continue
            keys = self.keys(path)
            if not required <= keys:
                continue
            if any_of and not any_of & keys:
                continue
            found.append(path)
        return sorted(found, key=lambda path: (len(self.relative(path).split('/')), self.relative(path)))

    def matrix_npz(self, scope, matrix_hint, axis_hint=(), minimum_matrices=1):
        candidates = []
        for path in self.search({'.npz'}, scope=scope):
            arrays = self.arrays(path)
            names = {canonical(name): name for name in arrays}
            matrices = [name for name in names if arrays[name].ndim == 2 and arrays[name].dtype.kind in 'fiu']
            vectors = [name for name in names if arrays[name].ndim == 1 and arrays[name].dtype.kind in 'USO']
            if len(matrices) < minimum_matrices or not vectors:
                continue
            score = 0
            for hint in matrix_hint:
                if any(hint in name for name in matrices):
                    score += 2
            for hint in axis_hint:
                if any(hint in name for name in vectors):
                    score += 1
            candidates.append((-score, len(self.relative(path).split('/')), self.relative(path), path))
        if not candidates:
            return None
        return sorted(candidates)[0][3]

    def table(self, suffixes, scope, required=(), any_of=(), columns=()):
        wanted = {canonical(column) for column in columns}
        best = None
        for path in self.search(suffixes, required=required, any_of=any_of, scope=scope):
            present = self.keys(path)
            score = len(wanted & present)
            key = (-score, len(self.relative(path).split('/')), self.relative(path))
            if best is None or key < best[0]:
                best = (key, path)
        return None if best is None else best[1]

    def records(self, suffixes=('.json',), scope=None):
        for path in self.files:
            if path.suffix.lower() not in suffixes:
                continue
            if scope is not None and not path.is_relative_to(scope):
                continue
            try:
                record = json.loads(path.read_text())
            except Exception:
                continue
            if isinstance(record, dict):
                yield path, record
