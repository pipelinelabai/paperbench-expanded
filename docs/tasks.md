# Public Task Catalog

[Overview](../README.md) · [Quickstart](quickstart.md) · [Evaluation](evaluation.md) · [HFSS setup](../README_HFSS.md)

PaperBench High-Difficulty and Expanded Tasks releases one representative task from each of its **12 research
areas**. The broader benchmark also maintains **81 restricted evaluation tasks**;
those tasks and their private resources are not included in this repository.

## Browse the Scientific Goals

| ID | Research area | What the agent must reproduce | Scientific stack | Environment access |
|---|---|---|---|---|
| [01](../tasks/01-cpw-quad-port-uwb-mimo/instruction.md) | Multi-port antennas | Matching, isolation, radiation, and geometric controls in a CPW UWB MIMO antenna | HFSS | Commercial; own image and license |
| [02](../tasks/02-anisotropic-coding-diffusion-metasurface/instruction.md) | Coding metasurfaces | Polarization-dependent reflection, finite-surface scattering, and the separate array-factor model | HFSS | Commercial; own image and license |
| [03](../tasks/03-dual-passband-angular-stable-fss/instruction.md) | Frequency-selective surfaces | Two passbands and angular/polarization stability, with native field and convergence evidence | HFSS | Commercial; own image and license |
| [04](../tasks/04-swg-anisotropic-phase-shifter-meep/instruction.md) | Integrated photonic phase shifters | Differential transmission phase of two fixed SWG waveguides and independent Bloch-mode checks | Meep | Included CPU build recipe |
| [05](../tasks/05-pt-bragg-unidirectional-invisibility-meep/instruction.md) | Non-Hermitian photonics | Unidirectional invisibility and a causal gain–loss Bragg realization | Meep | Included CPU build recipe |
| [06](../tasks/06-gmr-grating-fano-meep/instruction.md) | Guided-mode resonances | Two resonance branches in a slotted multilayer grating, with fits and decay comparisons | Meep | Included CPU build recipe |
| [07](../tasks/07-brewster-spatial-differentiator-meep/instruction.md) | Optical analog computing | Brewster-interface spatial differentiation, usable bandwidth, and beam demonstrations | Meep | Included CPU build recipe |
| [08](../tasks/08-clc-1d-resonator-meep/instruction.md) | Anisotropic liquid-crystal optics | Thickness-dependent linear/circular transmission of cholesteric slabs | Meep | Included CPU build recipe |
| [09](../tasks/09-pimarenyl-bifurcation-v2/instruction.md) | Reaction dynamics | Short-time steering of pimarenyl-cation trajectories under fixed initial conditions | PySCF / GPU4PySCF | Included build recipe; own GPU |
| [10](../tasks/10-haastrup-2018-mos2-bands/instruction.md) | Two-dimensional materials | Elastic response, SOC/no-SOC bands, band edges, and effective masses of monolayer MoS2 | Quantum ESPRESSO | Included CPU build recipe |
| [11](../tasks/11-horlbeck-2018-genetic-interactions/instruction.md) | Functional genomics | Reconstructing and testing a human CRISPRi genetic-interaction map | Python scientific stack | Included CPU build recipe and supplied inputs |
| [12](../tasks/12-mapgpt-r2r/instruction.md) | Vision-and-language navigation | MapGPT mapping, prompting, and adaptive planning on 216 R2R cases | Local Qwen2.5-VL / vLLM | Own GPU; runtime image with observations and weights |

Tasks 04–12 are the **nine non-HFSS tasks**. That does not mean every external
asset is redistributed: task 12 builds on a runtime image that carries its
observations and weights, and GPU tasks require compatible hardware. Scientific software,
models, datasets, papers, and container components retain their own terms.

## Read a Task in This Order

1. `instruction.md`: scientific target, required methods, and deliverables.
2. `environment/paper/addendum.md`: detailed conditions, scope, and artifact contract.
3. `environment/paper/paper.md`, `paper.pdf`, and figures: original scientific source.
4. `task.toml` and `environment/Dockerfile`: execution limits and environment requirements.
5. `tests/rubric.json` and verifier resources: how submitted evidence is assessed.

The last step is available for community inspection. During an actual trial,
trusted verifier resources are kept separate from the agent-visible environment;
they must not be copied into the solving image or injected as additional answers.

### Verifier Configuration

Every task uses the same configuration filenames and responsibilities:

- `tests/config/judge_prompt.md`: trusted judging instructions, including task-specific judging rules.
- `tests/config/public_contract.md`: the verifier's copy of the applicable public instructions or addendum; not a private answer key.
- `tests/config/evaluation.json`: machine-read policies only, where required. Tasks 01–03 use evidence and native-run policies; 05/09/10 use numerical checks and replay configuration; 11 uses numerical policies and scoring routes. Tasks without such settings do not carry an empty JSON file.

The layout is shared, not the scientific requirements: each task keeps its own
criteria, evidence, and numerical tolerances. Reference answers and audit keys
belong in `tests/refs/`, not in the public contract. `tests/rubric.json` defines
the scoring tree. Content hashes bind the relevant grader inputs to an assessment.

## Resource Limits

The following values reflect this package's task configuration. Native replay
runs **inside** the verifier budget; the two times are not additive.

| ID | CPUs | Memory | GPU | Agent limit | Verifier limit | Storage declaration |
|---|---|---|---|---|---|---|
| 01 | 32 | 128 GiB | — | 24 h | 25 h | 200 GiB |
| 02 | 32 | 128 GiB | — | 72 h | 73 h | 200 GiB |
| 03 | 32 | 128 GiB | — | 48 h | 49 h | 300 GiB |
| 04 | 8 | 32 GiB | — | 7 h | 6 h | 50 GiB |
| 05 | 8 | 32 GiB | — | 5 h | 5 h | 50 GiB |
| 06 | 8 | 32 GiB | — | 7 h | 6 h | 50 GiB |
| 07 | 8 | 32 GiB | — | 6 h | 5 h | 50 GiB |
| 08 | 8 | 32 GiB | — | 7 h | 7 h | 50 GiB |
| 09 | 8 | 32 GiB | 1 | 7 h | 7 h | 50 GiB |
| 10 | 8 | 32 GiB | — | 7 h | 7 h | 50 GiB |
| 11 | 8 | 32 GiB | — | 6 h | 6 h | 50 GiB |
| 12 | 8 | 32 GiB | 1 | 18 h | 7 h | 100 GiB |

Run `python run.py list` to inspect the active configuration. These are timeout
and resource declarations, not guarantees of completion, reservation, or full
scores. Docker image layers, build caches, temporary files, and archived evidence
consume additional disk space; the storage declaration is not a Docker disk quota.

The replay entrypoint can impose a smaller limit than the outer verifier. For
example, task 02 describes a 72-hour native-compute budget but its current replay
entrypoint is capped at 48 hours. Do not assume increasing the outer budget
automatically extends the replay limit. Consult each task's entrypoint when
planning a long run.

## Choosing a Workflow

- **Inspect the benchmark:** read a task's instructions and rubric, then run the
  no-execution packaging check.
- **Try a CPU-native reproduction:** use one of tasks 04–08, 10, or 11 after reading
  its scientific and resource requirements.
- **Use commercial electromagnetic tools:** configure tasks 01–03 through the
  [HFSS guide](../README_HFSS.md).
- **Study GPU workflows:** run 09 and 12 separately, with explicit GPU selection;
  task 12 also needs externally supplied observations, weights, and a base image.

A working package is not a demonstrated reproduction. Judge results must come
from the actual submitted workflow and regenerated evidence, not from an image
build or precomputed results.
