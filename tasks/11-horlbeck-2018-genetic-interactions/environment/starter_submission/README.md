# Submission workspace

Implement `reproduce.sh` as the single offline entrypoint. Read the paper and
public addendum for scientific scope and required evidence. Keep editable source
and authored static inputs outside `results/`. Clean replay deletes `results/`,
protects source against modification, and runs as the unprivileged solver user.
Write generated reports, figures and numeric evidence below
`results/horlbeck_gi_reproduction/`.

The runtime provides Python, NumPy, SciPy, pandas and matplotlib. Raw counts and
guide identities are already installed at `/home/data/horlbeck/`; no weights or
additional study-data downloads are needed. This starter contains no solution.
