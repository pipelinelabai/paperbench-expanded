import csv
import json
import math
from pathlib import Path
import zipfile

import numpy as np


SUPPORTED_SUFFIXES = {'.npz', '.npy', '.json', '.csv', '.tsv', '.h5', '.hdf5'}
MAX_FILE_BYTES = 1024 * 1024 * 1024
MAX_ARRAY_BYTES = 512 * 1024 * 1024
MAX_TEXT_BYTES = 64 * 1024 * 1024
MAX_ARRAYS = 4096
FORMAT_POLICY = '''
Equivalent evidence must receive the same scientific judgment regardless of file
name, directory, JSON nesting, column order, prose language or numeric container.
Rubric evidence paths are discovery hints, not required filenames. A missing hint
is not missing evidence: list the actual submission files, read the report/code,
and inspect plausible alternate datasets before declaring the quantity absent.
Use numeric tools for NPZ, NPY, numeric JSON, headered CSV/TSV and numeric HDF5.
Nested JSON and HDF5 keys retain their full paths; never combine different
variants merely because the terminal key is the same. CSV columns retain names.
Compare physical quantities after explicitly justified unit conversion; never
guess units, infer phase from intensity, insert missing values or manufacture
data. A renamed field must be mapped from its documented meaning and source.
An annotated raw spatial field with coordinates can evidence a field-view leaf;
a pretty or nonempty PNG alone cannot. All required physics, controls, provenance,
and clean-replay requirements still apply. No credit for booleans or claimed
metrics alone when the leaf requires a calculation from raw data.
These reading tools are evaluator infrastructure. If genuine alternate evidence
cannot be read because the tool does not support its format or its resource
budget, mark evidence_access='tool_error' and explain the problem; do not turn
that tool failure into a model score. If evidence was searched for and is really
absent, contradictory or numerically incorrect, judge that scientific deficiency.
Do not demand a renamed copy, new report, new run or new information from a model
solely to match this evaluator's preferred layout. Preserve original artifacts.
'''.strip()


class EvidenceFormatError(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceFormatError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def pointer_token(value):
    return str(value).replace('~', '~0').replace('/', '~1')


def numeric_array(value):
    array = np.asarray(value)
    if array.dtype.kind not in 'biufc':
        raise EvidenceFormatError('Numeric evidence cannot use object, string or structured dtype')
    if array.nbytes > MAX_ARRAY_BYTES:
        raise EvidenceFormatError('Array exceeds the evaluator read budget; this is not a model failure')
    return array


def validate_numpy_header(stream):
    version = np.lib.format.read_magic(stream)
    if version == (1, 0):
        shape, _, dtype = np.lib.format.read_array_header_1_0(stream)
    elif version == (2, 0):
        shape, _, dtype = np.lib.format.read_array_header_2_0(stream)
    else:
        raise EvidenceFormatError('Unsupported NPY header version; evaluator adaptation required')
    if any(size < 0 for size in shape) or math.prod(shape) * dtype.itemsize > MAX_ARRAY_BYTES:
        raise EvidenceFormatError('Declared array shape exceeds evaluator memory budget')


class NumericEvidence:
    def __init__(self, path):
        self.path = Path(path)
        self.handle = None
        self.arrays = {}
        self.metadata = {}
        self.rejected = {}
        self.hdf_datasets = {}
        if self.path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise EvidenceFormatError('Unsupported numeric format; request evaluator-side adaptation')
        if not self.path.is_file() or self.path.is_symlink():
            raise EvidenceFormatError('Evidence must be a regular non-symlink file')
        if self.path.stat().st_size > MAX_FILE_BYTES:
            raise EvidenceFormatError('File exceeds evaluator read budget; do not assign model failure')
        try:
            self._open()
            if len(self.keys()) > MAX_ARRAYS:
                raise EvidenceFormatError('Too many datasets for the evaluator read budget')
        except Exception:
            self.close()
            raise

    def _open(self):
        suffix = self.path.suffix.lower()
        if suffix == '.npz':
            with zipfile.ZipFile(self.path) as archive:
                members = archive.infolist()
                names = [item.filename for item in members]
                if len(names) != len(set(names)):
                    raise EvidenceFormatError('Duplicate NPZ members')
                if len(names) > MAX_ARRAYS or any(item.file_size > MAX_ARRAY_BYTES for item in members):
                    raise EvidenceFormatError('NPZ exceeds evaluator read budget')
                for item in members:
                    if not item.filename.endswith('.npy'):
                        raise EvidenceFormatError('NPZ contains a non-array member')
                    with archive.open(item) as stream:
                        validate_numpy_header(stream)
            self.handle = np.load(self.path, allow_pickle=False)
            if len(self.handle.files) != len(set(self.handle.files)):
                raise EvidenceFormatError('Ambiguous NPZ array names')
        elif suffix == '.npy':
            with self.path.open('rb') as stream:
                validate_numpy_header(stream)
            self.arrays['array'] = numeric_array(np.load(self.path, allow_pickle=False, mmap_mode='r'))
        elif suffix in {'.h5', '.hdf5'}:
            self._open_hdf()
        else:
            if self.path.stat().st_size > MAX_TEXT_BYTES:
                raise EvidenceFormatError('Text evidence exceeds evaluator parsing budget')
            if suffix == '.json':
                value = json.loads(self.path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)
                self._walk_json(value)
            else:
                self._open_table('\t' if suffix == '.tsv' else ',')

    def _walk_json(self, value, prefix=''):
        name = prefix or 'array'
        if isinstance(value, dict):
            if set(value) == {'real', 'imag'}:
                real = numeric_array(value['real'])
                imag = numeric_array(value['imag'])
                if real.shape != imag.shape or np.iscomplexobj(real) or np.iscomplexobj(imag):
                    raise EvidenceFormatError(f'{name}: mismatched real/imag components')
                self.arrays[name] = numeric_array(real + 1j * imag)
                return
            for key, item in value.items():
                self._walk_json(item, prefix + '/' + pointer_token(key))
            return
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            fields = list(value[0])
            if any(set(item) != set(fields) for item in value):
                for index, record in enumerate(value):
                    self._walk_json(record, prefix + '/' + str(index))
                return
            for field in fields:
                self._walk_json([item[field] for item in value], prefix + '/' + pointer_token(field))
            return
        if isinstance(value, (list, int, float, bool)):
            try:
                self.arrays[name] = numeric_array(value)
            except (ValueError, TypeError) as error:
                self.rejected[name] = str(error)
        elif value is not None:
            self.metadata[name] = value

    def _open_table(self, delimiter):
        with self.path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.reader(stream, delimiter=delimiter)
            header = next(reader, None)
            if not header:
                raise EvidenceFormatError('Numeric table requires named columns')
            header = [column.strip() for column in header]
            if any(not column for column in header) or len(header) != len(set(header)):
                raise EvidenceFormatError('Blank or duplicate table column names')
            if len(header) > MAX_ARRAYS:
                raise EvidenceFormatError('Too many table columns')
            columns = {name: [] for name in header}
            for row in reader:
                if not row:
                    continue
                if len(row) != len(header):
                    raise EvidenceFormatError('Inconsistent table row width; no imputation allowed')
                for name, value in zip(header, row):
                    columns[name].append(value)
            for name, values in columns.items():
                try:
                    self.arrays[name] = numeric_array(np.asarray(values, dtype=float))
                except ValueError as error:
                    self.rejected[name] = str(error)

    def _open_hdf(self):
        try:
            import h5py
        except ImportError as error:
            raise EvidenceFormatError('HDF5 reader unavailable in evaluator environment') from error
        self.handle = h5py.File(self.path, 'r')

        def attributes(item):
            for name, value in item.attrs.items():
                array = np.asarray(value)
                if array.size != 1 or array.dtype.kind not in 'biufSU':
                    continue
                value = array.item()
                if isinstance(value, bytes):
                    value = value.decode('utf-8', errors='replace')
                self.metadata[item.name + '@' + name] = value

        def visit(group, ancestors):
            identifier = h5py.h5o.get_info(group.id).addr
            if identifier in ancestors:
                raise EvidenceFormatError('HDF5 contains a cyclic group')
            attributes(group)
            for name in group:
                link = group.get(name, getlink=True)
                if not isinstance(link, h5py.HardLink):
                    raise EvidenceFormatError('HDF5 external/soft links are not allowed')
                item = group[name]
                if isinstance(item, h5py.Group):
                    visit(item, ancestors | {identifier})
                elif isinstance(item, h5py.Dataset):
                    if item.is_virtual or item.external:
                        raise EvidenceFormatError('HDF5 virtual/external datasets are not allowed')
                    settings = item.id.get_create_plist()
                    if any(settings.get_filter(index)[0] > 6 for index in range(settings.get_nfilters())):
                        raise EvidenceFormatError('Custom HDF5 filters are not allowed')
                    attributes(item)
                    self.hdf_datasets[item.name] = item
                    if len(self.hdf_datasets) > MAX_ARRAYS:
                        raise EvidenceFormatError('Too many HDF5 datasets')
        visit(self.handle, set())

    def keys(self):
        if self.path.suffix.lower() == '.npz':
            return list(self.handle.files)
        if self.hdf_datasets:
            return list(self.hdf_datasets)
        return list(self.arrays)

    def get(self, key):
        if key not in self.keys():
            raise EvidenceFormatError(f'No exact dataset {key!r}; inspect keys instead of guessing aliases')
        if self.path.suffix.lower() == '.npz':
            return numeric_array(self.handle[key])
        if key in self.hdf_datasets:
            dataset = self.hdf_datasets[key]
            if dataset.dtype.kind not in 'biufc' or dataset.size * dataset.dtype.itemsize > MAX_ARRAY_BYTES:
                raise EvidenceFormatError('HDF5 dataset is non-numeric or exceeds the read budget')
            return numeric_array(dataset[()])
        return numeric_array(self.arrays[key])

    def close(self):
        if self.handle is not None:
            self.handle.close()
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()


def canonical_unit(unit):
    if not isinstance(unit, str) or not unit.strip():
        raise EvidenceFormatError('Units must be explicitly declared nonempty strings')
    normalized = ' '.join(unit.strip().casefold().replace('-', ' ').split())
    aliases = {
        'mode amplitude': 'mode amplitude',
        'modal amplitude': 'mode amplitude',
        'consistent flux': 'consistent flux',
        'meep flux': 'consistent flux',
        'meep power': 'consistent flux',
        'meep arbitrary source units': 'consistent flux',
    }
    declaration, separator, convention = normalized.partition(';')
    if separator and convention.strip() == 'mode basis normalized to unit forward power':
        normalized = declaration.strip()
        if aliases.get(normalized) != 'consistent flux':
            return unit
    return aliases.get(normalized, unit)


def convert_units(array, source_unit, target_unit):
    source_unit = canonical_unit(source_unit)
    target_unit = canonical_unit(target_unit)
    units = {
        'm': ('length', 1.0), 'mm': ('length', 1e-3),
        'um': ('length', 1e-6), 'µm': ('length', 1e-6), 'μm': ('length', 1e-6),
        'nm': ('length', 1e-9), 'Hz': ('frequency', 1.0),
        'GHz': ('frequency', 1e9), 'THz': ('frequency', 1e12),
        's': ('time', 1.0), 'ps': ('time', 1e-12), 'fs': ('time', 1e-15),
        'rad': ('angle', 1.0), 'deg': ('angle', math.pi / 180),
        '1': ('ratio', 1.0), '%': ('ratio', 0.01),
        'W': ('power', 1.0), 'mW': ('power', 1e-3),
        'consistent flux': ('solver_flux', 1.0),
        'mode amplitude': ('modal_amplitude', 1.0),
    }
    if source_unit not in units or target_unit not in units:
        raise EvidenceFormatError('Unsupported or undeclared unit; do not infer it')
    source_dimension, source_scale = units[source_unit]
    target_dimension, target_scale = units[target_unit]
    if source_dimension != target_dimension:
        raise EvidenceFormatError('Incompatible unit dimensions')
    return numeric_array(array) * (source_scale / target_scale)
