# Public asset provenance and canonical hashes

## Literature sources

- Article: Cao, Kong, and Tantillo, *J. Am. Chem. Soc.* 2025,
  DOI `10.1021/jacs.5c16476` (`../paper.pdf`, searchable extraction in
  `../paper.md`).
- Official Supporting Information: `supporting_information.pdf`.
- The article's Supporting Information identifies its optimized-geometry
  collection at the ioChem-BD locator
  `https://iochem-bd.bsc.es/browse/reviewcollection/100/478645/0d00175ed2134579ed9be110`.
  The two XYZ files and two imaginary-mode arrays below are the study's
  frozen public extracts. No network fetch is needed during clean replay.

For each named upstream CML, the study preserves the CML atom order,
serializes its transition-structure coordinates into the 53-row XYZ at eight
decimal places, extracts the displacement associated with the named imaginary
frequency, and Euclidean-normalizes that Cartesian displacement before JSON
serialization. The upstream CML files are not bundled, so no upstream raw-CML
byte hash is claimed; the distributed extracts and their canonicalized content
are instead bound by the hashes below.

The supplied starting structures and modes are input evidence, not outcome
labels, energies, gradients, trajectories, or a reference solution.

## Raw-file integrity

These hashes cover the exact bytes of the distributed files:

| file | raw-file SHA-256 |
|---|---|
| `../paper.pdf` | `6712f4d8832a992dbd1034f4b602161c4344b19dd7d735c2228c4f6da17a27f5` |
| `TSre.xyz` | `4f0097a48aaae9e1dbb508d04a1b96cd30b42e27c2c21e2b42603ecf98d5dffa` |
| `TSsi.xyz` | `ddd15522179b165ef40fd12b03dd397aa0d6f845ce15e2dbcaaa955c9604e10a` |
| `mode_TSre.json` | `d1ee686dde0e29a77f610dd0200789e64bda6d1864a7aa00c59653dbe8612795` |
| `mode_TSsi.json` | `23309a52dade6d03fb3427c2bbd9cdbc2b97b550f1848f89875ec1c495eac6a4` |
| `supporting_information.pdf` | `cff45b75e7623c181703a408376a3496dce77f142c5cb5e735caa3d86fb1cad8` |

## Canonical geometry hashes

The public `coordinate_sha256` is deliberately independent of XYZ headers and
whitespace. Parse the atom rows in order, then serialize each as
`Element.capitalize() x:.8f y:.8f z:.8f`, join rows with a single LF (`\n`),
add no final newline, UTF-8 encode, and SHA-256 hash.

| structure | canonical coordinate SHA-256 |
|---|---|
| TSre | `5f07872c5b2ae0e7d634a4eb2c059ae7c35b7885192cea5407b35f8cf9c819dc` |
| TSsi | `45c3cb429b5644b755eb6aca85be70c042df80939aab48d99bb74ed54bb014cd` |

## Canonical mode hashes

Parse the `displacement` array from each mode JSON. Serialize that array with
Python `json.dumps(displacement, sort_keys=True, separators=(",", ":"))`,
preserving list order, float values, and signed zero. UTF-8 encode the resulting
string and SHA-256 hash it.

| mode | source locator recorded in JSON | canonical displacement SHA-256 |
|---|---|---|
| TSre | `syn_cpp_TSre_output.cml`, imaginary mode -1046.9530 cm^-1 | `28439af19ce6c40925ca5f096b5c7dc54e58e00f633206270c84cd70b1b2d26b` |
| TSsi | `syn_cpp_TSsi_output.cml`, imaginary mode -979.8382 cm^-1 | `055d746e108852fb39aeb92ad4e51dde78348cb2654ea3a5a8e10c0d90ba0dd2` |

Trajectory JSON fields `start_geometry_sha256` and `mode.sha256` use these
canonical hashes, not the raw-file hashes.
