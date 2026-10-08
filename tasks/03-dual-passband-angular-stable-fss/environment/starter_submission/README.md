# HFSS reproduction starter

This is an intentionally incomplete pipeline, not a reference solution.
Read `/home/paper/addendum.md`, `/home/paper/paper.md`, the original PDF at
`/home/paper/paper.pdf`, the figures in `/home/paper/paper_image/`, and
`/home/paper/blacklist.md`. These materials are already available locally.
Implement `src/run_all.py --variant NAME`, including output generation,
then run `bash reproduce.sh`. No separate self-check script is required;
the verifier independently checks the replayed data.

Replace this README with your extracted parameters, modeling choices, variants,
commands, convergence disclosures, artifact index and limitations. Preserve
native HFSS exports byte-for-byte under each solved variant's `raw/`, write
`raw/MANIFEST.json`, and document actual paper issues in `PAPER_AUDIT.md`.

Only regenerated evidence establishes the reported results. Do not store cached simulation results
among source inputs. Failed or unconverged variants must be reported honestly.
