# Two-passband transmission and angular response of a frequency-selective surface

Use HFSS to reproduce the specified dual-passband frequency-selective surface under normal and oblique TE and TM incidence. Measure reflection, transmission, passband edges, resonant peaks and the inter-band transmission zero on the prescribed frequency grids. Compare the polarization and angular trends with the paper's full-wave curves, including the specified high-angle cases. Use the requested field plots and native convergence records to explain the response, keeping equivalent-circuit predictions and experimental measurements separate from the simulated results.

## Deliverables and starting materials

Deliver the TE/TM transmission and reflection spectra, angular trends, passband measurements, and field plots supporting the two-passband interpretation.

Work in `/home/submission`. Start with the materials already installed in the environment:

- `/home/paper/addendum.md`: scientific protocol, required data formats, computing limits and offline `bash reproduce.sh` procedure.
- `/home/paper/paper.md`: searchable full paper text.
- `/home/paper/paper.pdf`: original paper layout for equations, tables and figure details.
- `/home/paper/paper_image/`: extracted paper figures.

Read the local paper and figures before seeking additional material. The complete article is supplied; downloading another copy is unnecessary.

## Comparison conditions

The addendum includes the paper-comparison conditions and measurement definitions. Its Licensed HFSS environment section describes the owner-specific runtime and prerequisites; this is not a turnkey solver distribution. Keep all detailed deliverables and the public computing budgets.

## External resources

Read `/home/paper/blacklist.md` before consulting external resources and follow its resource-use restrictions throughout this task.

The quantitative result comparisons in the addendum remain required. Describe a nonmatching or unresolved result honestly; reporting it does not establish the requested performance. Do not change the model or numerical thresholds to obtain agreement.

No separate agent-written self-check script is required. The verifier independently checks the source-only replay outputs and their native-data consistency under the addendum's unchanged numerical tolerances.
