# Task: MapGPT: Map-Guided Prompting with Adaptive Path Planning for Vision-and-Language Navigation

## Workspace and Materials

Your workspace is `/home`. The following materials are provided:

- `/home/paper/paper.md` — full paper in Markdown with figure references.
- `/home/paper/paper.pdf` — PDF fallback.
- `/home/paper/paper_image/` — paper figures in PNG format.
- `/home/paper/addendum.md` — **required reading: detailed reproduction requirements**.
- `/home/paper/blacklist.txt` — external resources that must not be accessed.

The dataset and model are provided **read-only; no downloads are needed**:

- `/home/data/connectivity/` — Matterport3D / R2R navigation graphs in JSON, with viewpoint positions and adjacency for each scene.
- `/home/data/R2R/annotations/MapGPT_72_scenes_processed.json` — instructions and starting points for the R2R val-unseen 72-scene / 216-case subset.
- `/home/data/RGB_Observations/` — precomputed panoramic RGB observations for each viewpoint.
- `/home/models/Qwen2.5-VL-7B-Instruct/` — **read-only navigation VLM weights for local inference**.
- Preinstalled `vllm`, one GPU reserved through Compose, and `/usr/local/bin/serve_nav_vllm.sh`, a helper for starting the local vLLM server.

Write all submission artifacts to `/home/submission/`.

---

## System Requirements

### §1 Task and Environment

- Reproduce a **zero-shot, training-free VLN navigation agent** using a general-purpose LLM/VLM to make step-by-step decisions on the discrete R2R navigation graph.
- **Do not train or fine-tune any model.** This is inference only.
- Use the provided RGB observations. Real-time rendering and raw Matterport3D scans are not required.
- **Local navigation VLM deployment is mandatory**:
  - The navigation model is **`Qwen2.5-VL-7B-Instruct`**, provided read-only at `/home/models/Qwen2.5-VL-7B-Instruct/`. The container has `vllm` installed and one GPU reserved.
  - **Run the model inside the container. Every navigation step must use the local Qwen2.5-VL-7B for visual decision-making.** An OpenAI-compatible vLLM server is recommended. Source `/usr/local/bin/serve_nav_vllm.sh`, then call `nav_vllm_start` to start the local service and `nav_vllm_stop` when finished. Set `NAV_LLM_BASE_URL` to the matching local endpoint; the task template leaves it empty. Equivalent local deployment, including in-process transformers/vllm inference, is accepted.
  - **Remote or external navigation APIs are forbidden.** Do not point `NAV_LLM_BASE_URL` outside local loopback, or use OpenAI, Anthropic, or any cloud model for navigation. The navigation client's base URL must be local loopback.
  - Configure navigation separately from the judge through `NAV_LLM_MODEL` (`Qwen2.5-VL-7B-Instruct`), `NAV_LLM_BASE_URL` (empty in the template; configure the local endpoint before running), and `NAV_LLM_API_KEY` (a local placeholder such as `local`).
  - **Never use the judge-only `ANTHROPIC_API_KEY` for navigation.** Code such as `NAV_LLM_API_KEY or ANTHROPIC_API_KEY` is prohibited, even as a fallback. If navigation configuration is missing, fail explicitly rather than reading `ANTHROPIC_*`. Navigation and judge configuration coexist during verification; such a fallback can actually use the judge credential.
  - Record the actual model, local endpoint, and sampling settings (`temperature`, `max_tokens`, `response_format`, per-step image limit, and maximum action steps) in `meta.json.nav_llm`.
- Additional Python dependencies, such as numpy or networkx, may be installed during development with `python3` / `pip`, but must already be available before offline clean replay. Do not install packages during replay.

### §2 Submission Artifacts

See `/home/paper/addendum.md` §D for the complete artifact structure. Keep everything under `/home/submission/`. The online topological map, map-guided prompt, and adaptive planning must be implemented in source code, not merely described in a README.

### §3 Evaluation

- Run **all 216 cases** in the 72-scene subset, not just an initial subset.
- Compute NE / OSR / SR / SPL using standard R2R geodesic shortest paths on the connectivity graph, with a success threshold of **3.0 m**.
- The verifier **recomputes** metrics from the connectivity graph; it does not trust self-reported `metrics.csv` values.
- **Stop-behavior diagnostics:** the verifier also recomputes cap-hit rate and OSR−SR gap using trajectory `stopped` flags and `max_action_step`. The cap-hit rate should be low and the gap small. The navigation LLM must genuinely choose **'A. stop'** near the goal, rather than exhaust the step budget and be forcibly truncated. **Out-of-paper forced-stop patches are forbidden**, including repeated-viewpoint loop guards or heuristic early breaks. Stop decisions must come from the local navigation LLM.

---

## Task Details

Read `/home/paper/addendum.md` for the reproduction scope, artifact schemas, and scientific protocol.
Read `/home/paper/paper.md` and `/home/paper/paper_image/` for the paper and figures.
Consult `/home/paper/blacklist.txt` for prohibited resources.

---

## Required `reproduce.sh`

Create an independently executable `/home/submission/reproduce.sh`. This is the **only replay entrypoint**: the verifier executes it in a fresh environment and uses the regenerated outputs.

> The verifier clears `/home/submission/results/` before running `reproduce.sh`. The script must independently navigate all 216 cases from scratch and regenerate every required artifact. During development, first validate your implementation on a small number of cases, then submit a script that runs the complete subset.

Requirements:

1. Location: `/home/submission/reproduce.sh`.
2. Start from an empty results directory, finish all 216 cases, and generate every artifact in addendum §D.
3. Be self-contained: start the local Qwen2.5-VL-7B inference service, configure dataset paths, and do not depend on temporary development-session state. Stop the service when finished.
4. Exit with code 0 on success and nonzero on failure.

Minimal example structure, which you may extend:

```bash
#!/bin/bash
set -euo pipefail

source /usr/local/bin/serve_nav_vllm.sh
nav_vllm_start
trap nav_vllm_stop EXIT

cd /home/submission/src
python3 run_navigation.py \
    --split /home/data/R2R/annotations/MapGPT_72_scenes_processed.json \
    --connectivity /home/data/connectivity \
    --img_root /home/data/RGB_Observations \
    --output /home/submission/results/r2r_val_unseen_subset
```

**The verifier deletes existing results and reruns `reproduce.sh`; the script must reproduce all trajectories and metrics from scratch.**

---

## Completion

The task is complete when `/home/submission/reproduce.sh` exists and `/home/submission/src/` contains the complete navigation implementation: topological map, prompt manager, and adaptive planning.

## Clean Replay Contract

The verifier treats authored inputs and generated evidence separately. Authored inputs include
`reproduce.sh`, `README.md`, `src/`, and other configuration or code outside `/home/submission/results/`.
The generated roots are `/home/submission/results/`; they are deleted before verification and must be fully
regenerated by this single public entrypoint:

```bash
bash /home/submission/reproduce.sh
```

The clean replay runs as uid/gid 65532 with no Linux capabilities and no external network. Local
loopback remains available for policy servers. All dependencies, weights, datasets, and code needed
by replay must therefore already be present in the image, mounted read-only, or authored in the
submission. Do not install or download packages, repositories, models, or data during replay.

The verifier sets a task-specific `PBX_MAX_WORKERS` cap no higher than the container CPU quota.
Every process pool, rollout pool, and dataloader must use no more than that many workers. Source files are hashed before and after
replay. Only artifacts copied into the verifier-owned frozen evidence root after an unchanged,
clean replay are the regenerated evidence; pre-existing or subsequently modified outputs are not.
