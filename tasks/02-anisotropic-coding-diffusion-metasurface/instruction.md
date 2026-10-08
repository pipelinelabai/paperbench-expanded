# Polarization-dependent reflection and diffuse scattering from a coding metasurface

Use HFSS to characterize the specified anisotropic unit cell at normal and oblique TM incidence, then calculate the finite coding metasurface and same-size metallic reference. Measure complex reflection in the fixed polarization basis and derive RCS reduction from the two independently solved scattering spectra. Separately reproduce the paper's numerical array-factor model for the three supplied coding matrices. Compare the spectra, currents and scattering patterns with the paper's simulation results without treating the array-factor model as a full-wave measurement.

## Deliverables and starting materials

Deliver the polarization-resolved unit-cell spectra, three array-factor patterns, and independently calculated metasurface and metallic-reference scattering data.

Work in `/home/submission`. Read `/home/paper/addendum.md` for the scientific protocol, required data formats, computing limits and offline `bash reproduce.sh` procedure. Use the supplied article and figures for context.

## Comparison conditions

The addendum explains the paper's comparison conditions, phase and receive definitions, and characterization requirements. Its Licensed HFSS environment section describes the owner-specific runtime and prerequisites; this is not a turnkey solver distribution. Keep all detailed deliverables and the public computing budgets.

## External resources

Read `/home/paper/blacklist.md` before consulting external resources and follow its resource-use restrictions throughout this task.

The quantitative result comparisons in the addendum remain required. Describe a nonmatching or unresolved result honestly; reporting it does not establish the requested performance. Do not change the model or numerical thresholds to obtain agreement.
