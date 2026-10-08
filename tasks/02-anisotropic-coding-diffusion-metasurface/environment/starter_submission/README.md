# HFSS reproduction starter

This is an intentionally incomplete pipeline, not a reference solution.
Read `/home/paper/addendum.md`, the complete paper
and its figures, and `blacklist.md`. Implement `src/run_all.py --variant NAME`
and `src/derive.py --results results [--check]`, then run `bash reproduce.sh`.

Replace this README with your extracted parameters, modeling choices, variants,
commands, convergence disclosures, artifact index and limitations. Preserve
native HFSS exports byte-for-byte under each solved variant's `raw/`, write
`raw/MANIFEST.json`, and document actual paper issues in `PAPER_AUDIT.md`.

Only regenerated evidence establishes the reported results. Do not store cached simulation results
among source inputs. Failed or unconverged variants must be reported honestly.
