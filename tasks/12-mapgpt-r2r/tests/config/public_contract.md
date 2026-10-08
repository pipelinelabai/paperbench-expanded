# Reproduction Goals and Scope

## Reproduction Goal

Reproduce the **zero-shot, training-free VLN navigation agent** from *MapGPT: Map-Guided Prompting with Adaptive Path Planning for Vision-and-Language Navigation* (Chen et al., 2024, arXiv:2401.07314). The agent uses a general-purpose LLM/VLM to make step-by-step decisions on the discrete Room-to-Room (R2R) navigation graph. Its core contributions are:

- An **online topological map**: explored, accessible, and inaccessible nodes and their connections are verbalized in the prompt, providing global context rather than greedy selection among nearby candidates.
- **Adaptive path planning**: explicit multi-step planning at every step, including backtracking to nonadjacent historical nodes for re-exploration.

Run the agent on the official MapGPT **R2R sampled subset, 72 scenes / 216 cases**, generate a trajectory for every case, and report SR / SPL / OSR / NE. The local navigation model is Qwen2.5-VL-7B, which substitutes for the paper's GPT-4V; do not treat a local-model result as a same-model reproduction of the paper's published table.

> **Reading discipline:** Prefer `paper.md` and `paper_image/`. Read the full Markdown paper and visually inspect every supplied figure, including Fig.1 (framework), Fig.2 (prompt structure and map verbalization), and Fig.3 (adaptive planning and backtracking). Use `paper.pdf` as a fallback for missing extraction content or ambiguous captions.

## In Scope

- The paper's online topological map: explored / accessible / unexplored-inaccessible node classes, numbering by observation order, connectivity `E_t`, and natural-language Trajectory / Map connectivity / Supplementary Info injected into prompts.
- All seven map-guided prompt components, organized by a prompt manager: Task description (D), Instruction (I), History (H_t), Observation (O_t), Action space (A_t, N+1 including stop), Map (M_t), and Previous Planning (P_{t-1}).
- Adaptive path planning: Thought (T_t), New Planning (P_t), and a single action label such as "Action: B." at each step; P_t becomes the next step's input, with nonadjacent historical backtracking supported.
- Navigation for every case in the **R2R val-unseen 72-scene / 216-case subset**, `MapGPT_72_scenes_processed`.
- Standard R2R NE / OSR / SR / SPL, using geodesic shortest paths on the connectivity graph.

## Out of Scope

- **Any training or fine-tuning:** do not train models or update LLM weights.
- Real-time rendering: use the provided RGB observations. Matterport3DSimulator rendering and the 1.3 TB raw scans are unnecessary. Local navigation VLM inference **does require a GPU**; one is reserved.
- The complete R2R val-unseen split; only the 72-scene subset is required.
- REVERIE; see §A.5.
- Reproducing GPT-4V versus GPT-4o comparisons; one navigation configuration is required.
- Appendix component ablations for Trajectory / Supplementary Info / Updating Mechanism. They need not be rerun.
- Reimplementing BLIP-2 caption generation or Faster R-CNN detection. Provided observations/descriptions are accepted; see §A.3.

## Core Variant

There is **one variant**, `r2r_val_unseen_subset`, comprising 72 scenes / 216 cases from R2R val-unseen.

---

## A. Clarifications

### A.1 Local Navigation VLM and Judge Isolation — Mandatory

Navigation decisions must use **`Qwen2.5-VL-7B-Instruct` locally inside the container**, zero-shot and inference-only:

- Weights are provided read-only at `/home/models/Qwen2.5-VL-7B-Instruct/`; `vllm` is preinstalled and one GPU is reserved. The paper used GPT-4V, while the official repository defaults to GPT-4o. This task substitutes a local 7B VLM for the paper's GPT-4V. A local-model result is not a same-model reproduction of the paper's published table.
- **Every navigation step must use the local Qwen2.5-VL-7B for visual decisions.** The helper `/usr/local/bin/serve_nav_vllm.sh` can start a vLLM OpenAI-compatible server: source it, call `nav_vllm_start`, and configure `NAV_LLM_BASE_URL` to match the local service (the task template leaves it empty). Call `nav_vllm_stop` when finished; an EXIT trap handles cleanup. Equivalent in-process transformers/vllm deployment is accepted.
- **All remote/external navigation APIs are forbidden.** `NAV_LLM_BASE_URL` must be local loopback (for example `localhost`), never a cloud endpoint. Do not use OpenAI, Anthropic, or any remote model for navigation. Record the actual local endpoint in source and in `meta.json.nav_llm.base_url`.
- Navigation configuration is separate from the verifier's Anthropic judge credential: `NAV_LLM_MODEL` (`Qwen2.5-VL-7B-Instruct`), `NAV_LLM_BASE_URL` (local vLLM), and `NAV_LLM_API_KEY` (local placeholder `local`; vLLM does not validate keys by default).
- Explicitly record in `meta.json.nav_llm`: model name, local endpoint, `temperature`, `max_tokens`, `response_format`, `max_image`, and `max_action_step` / `max_steps` (15 recommended).
- Sampling settings must be documented. Map, planning and visual-input mechanisms are separate from the reported navigation metrics.

**Credential-isolation rule:** the navigation client may read **only `NAV_LLM_API_KEY`**, never judge-only `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN`.

Forbidden, even if described as a fallback:

```python
api_key = os.environ.get("NAV_LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
```

Correct: fail explicitly if navigation configuration is missing.

```python
api_key = os.environ.get("NAV_LLM_API_KEY")
if not api_key:
    raise RuntimeError("NAV_LLM_API_KEY is required for navigation; refusing to use the judge key")
```

During replay, `NAV_LLM_*` and `ANTHROPIC_*` coexist. The forbidden fallback can actually use the judge credential if the navigation key is absent. Any source-level read or fallback to `ANTHROPIC_*` for navigation is forbidden, whether or not it executes. The same applies to a visual caption client: read only `CAP_LLM_API_KEY`, with no fallback to `ANTHROPIC_*`.

### A.2 Subset and Provided Assets

The configured runtime provides these lightweight assets; no downloads or raw Matterport3D scans are needed:

| Asset | Container path | Purpose |
|---|---|---|
| R2R connectivity graphs, JSON | `/home/data/connectivity/` | Node positions, adjacency, geodesic distances |
| `MapGPT_72_scenes_processed.json`, 216 cases | `/home/data/R2R/annotations/` | Instructions and starting points; ground-truth paths are removed |
| Precomputed RGB observations | `/home/data/RGB_Observations/` | Visual observations |
| **Qwen2.5-VL-7B-Instruct weights** | `/home/models/Qwen2.5-VL-7B-Instruct/` | **Read-only local navigation VLM** |
| vLLM, one GPU, `serve_nav_vllm.sh` | Preinstalled / reserved / `/usr/local/bin/` | Start local inference |

Run every case in this 216-case subset. Do not submit only the first N cases.

### A.3 Captions, Detection, and Visual Input

The paper uses BLIP-2 captions and Faster R-CNN detections in Observation (O_t). Reproducing those models is not required because the local Qwen2.5-VL-7B can read RGB directly, matching the paper's one-stage GPT-4V visual-decision configuration:

- **Recommended, one-stage:** feed RGB observations for navigable viewpoints directly to the local VLM for visual interpretation and decisions.
- Optional, two-stage: generate captions locally from the RGB observations, then insert the text into the prompt.

**Vision must genuinely enter the decision loop**, in either configuration. Record `meta.json.observation_source`, for example `vlm_on_rgb` or `precomputed_caption`. **Zero-vision/topological-only navigation is forbidden**; it is not a paper configuration. Retain VLM-call evidence in `run.log`, image or observation blocks in `prompt_sample.txt`, and the matching metadata.

### A.4 Standard R2R Evaluation

Use geodesic shortest paths on the connectivity graph:

- **NE:** distance in meters from the final viewpoint to the goal.
- **SR:** fraction of cases with NE ≤ 3.0 m.
- **OSR:** fraction with any visited viewpoint within 3.0 m of the goal.
- **SPL:** success weighted by `shortest_path_length / max(actual_path_length, shortest_path_length)`.

The verifier independently recomputes metrics from ground truth and the connectivity graph. Self-reported `metrics.csv` is only a cross-check.

### A.5 REVERIE Is Out of Scope

The paper also evaluates a REVERIE val-unseen subset of 500 instructions, reporting OSR 42.6 / SR 28.4 / SPL 14.5, zero-shot without GPS. This task evaluates only the specified R2R subset; REVERIE observations and evaluation are not required.

---

## B. Scope Checklist

| Status | Requirement |
|---|---|
| In scope | Online topological map: three node classes, numbering, connectivity, prompt verbalization |
| In scope | Seven prompt components D / I / H_t / O_t / A_t / M_t / P_{t-1} |
| In scope | Adaptive planning: Thought / New Planning / Action, linked plans, nonadjacent backtracking |
| In scope | All 72 scenes / 216 cases, with trajectories |
| In scope | **Local Qwen2.5-VL-7B visual navigation**, vLLM/transformers, local endpoint, no remote API |
| In scope | NE / OSR / SR / SPL computed from the trajectories |
| Out of scope | Training / fine-tuning |
| Out of scope | Real-time rendering and raw scans; GPU inference remains in scope |
| Out of scope | Full R2R val-unseen and REVERIE unless a second variant is enabled |
| Out of scope | Reproducing BLIP-2 / Faster R-CNN |
| Out of scope | Component ablations |

---

## C. Variants

| Variant | Dataset | Size | Navigation VLM | Purpose |
|---|---|---|---|---|
| `r2r_val_unseen_subset` | R2R val-unseen | 72 scenes / 216 cases | **Local Qwen2.5-VL-7B-Instruct, vLLM** | Reproduce MapGPT main results |

---

## D. Required Artifacts

Organize all artifacts under `submission/`. **Paths and filenames are hard requirements.**

```text
submission/
├── README.md
├── reproduce.sh
├── src/
│   ├── map.py
│   ├── prompt_manager.py
│   ├── agent.py
│   ├── llm_client.py
│   └── evaluate_metrics.py
└── results/
    └── r2r_val_unseen_subset/
        ├── trajectories.json
        ├── metrics.csv
        ├── per_case.csv
        ├── prompt_sample.txt
        ├── meta.json
        └── run.log
```

`README.md` must list the variant, artifact index, entrypoint, navigation model, and known deviations. `reproduce.sh` is the independent verifier entrypoint. Source modules implement the topological map, prompt manager, navigation loop, endpoint client configured through the environment, and geodesic self-evaluation. `run.log` records episode progress and model-call evidence.

### D.2 `trajectories.json` — Main Scoring Input

A JSON object keyed by annotation `instr_id`, with each value containing its predicted trajectory:

```json
{
  "<instr_id>": {
    "instr_id": "<instr_id>",
    "scan": "<scene_hash_id>",
    "trajectory": ["<viewpoint_id_0>", "<viewpoint_id_1>", "..."],
    "stopped": true
  }
}
```

- `trajectory` is the sequence of actually visited viewpoint IDs, including the start and ending at the node where the agent chooses stop.
- Cover all 216 cases; missing cases count as failures.
- Keep compatibility with R2R/DUET prediction formats: `instr_id` → `trajectory`.

### D.3 `metrics.csv` — Self-Reported Aggregate, Cross-Check Only

UTF-8 CSV with one row:

| Column | Type | Meaning |
|---|---|---|
| `n_cases` | int | Number evaluated, expected 216 |
| `NE` | float | Mean navigation error, meters |
| `OSR` | float | Oracle success rate, percent |
| `SR` | float | Success rate, percent |
| `SPL` | float | SPL, percent |

### D.4 `per_case.csv`

One row per case: `instr_id, scan, NE, success(0/1), oracle_success(0/1), path_len, shortest_len`.

### D.5 `prompt_sample.txt` — Authenticity Evidence

Include at least one complete case: the full prompt sent at each step, including Map / Action space / Planning, and the raw response containing Thought / New Planning / Action. The judge uses it to verify that mechanisms actually execute.

### D.6 Task-Specific `meta.json` Fields

- `variant`: `"r2r_val_unseen_subset"`.
- `n_cases`: integer, expected 216.
- `nav_llm`: object with `model` (`"Qwen2.5-VL-7B-Instruct"`), `base_url` (**local loopback**, matching the operator-configured service), `deployment` (`"local_vllm"` / `"local_transformers"`), `temperature`, `max_tokens`, `response_format`, and `max_image` (positive integer per-step image limit).
- `observation_source`: string, for example `"vlm_on_rgb"` / `"precomputed_caption"`; zero-vision topological-only is forbidden (§A.3).
- `max_action_step`, or `max_action_len` / `max_steps`: integer; 15 recommended, matching the repository default.
- `success_threshold_m`: float, expected 3.0.
- `map_components`: list of implemented components, for example `["D","I","H","O","A","M","P_prev"]`.

> Enforce the step budget, `"A. stop"`, image limit, and sampling parameters in source, and record the same values in metadata.

---

## E. Scientific metrics

Report NE, OSR, SR and SPL for every case in the 72-scene / 216-case subset.
The task uses local Qwen2.5-VL-7B rather than the paper's GPT-4V, so a local-model
result is not a same-model reproduction of the paper's published table.

Retain cap-hit rate, active-stop rate and the OSR−SR gap. Cap-hit greater than
40% or an OSR−SR gap greater than 25 percentage points is a diagnostic concern.
Extra wandering can inflate OSR without improving final-goal SR or NE.
Out-of-paper forced-stop heuristics are not part of the paper method. The
recommended step limit is 15; document the actual effective limit and inference
parameters.

---

## F. Implementation Details

### F.1 Map Verbalization — Paper Method

- **Trajectory:** list explored place IDs in observation order.
- **Map connectivity:** "Place {id} is connected with Places {...}"; connectivity need not be rebuilt during backtracking.
- **Supplementary Info:** keep scene descriptions only for inaccessible nodes; use "Nothing yet" if absent, matching DUET coarse-scale representation.
- Insert explored/accessible IDs directly into the action space without repeating descriptions.

### F.2 Per-Step Output and Parsing

Require **Thought + New Planning + Action**, with a single option label such as "Action: B.". Parse the label back to its candidate viewpoint. `response_format=json`, the repository default, is recommended for reliable parsing.

### F.3 Adaptive Backtracking

If a selected target is not directly reachable from the current node, use the map and Supplementary Info to backtrack to an appropriate historical node. The paper example has Place 10 inaccessible from Place 9, requiring a return to Place 1.

### F.4 `max_action_step`, `max_image`, and Stop

- `max_action_step`, also `max_action_len` / `max_steps`: **15 recommended**, the repository default. End a case on active stop or step-budget exhaustion.
- The first action-space option is fixed as **"A. stop"**, with N+1 options and a single output label such as "Action: B.".
- `max_image`: positive integer limiting images sent to the local VLM per step, for example neighbor count or a fixed cap; it controls memory use and latency.
- Enforce these constants in code and record them truthfully in `meta.json`.

### F.5 Authentic `run.log`

Include genuine per-case progress (`case i/216`), steps per case, and local VLM-call evidence, such as request/response summaries or token counts. Empty logs or fabricated fixed metrics are unacceptable.

### F.6 Local vLLM Deployment

- `vllm` is preinstalled, one GPU is reserved, and weights are provided read-only at `/home/models/Qwen2.5-VL-7B-Instruct/`.
- In `reproduce.sh`, source `/usr/local/bin/serve_nav_vllm.sh` and call `nav_vllm_start`. It uses `vllm serve` with `--served-model-name Qwen2.5-VL-7B-Instruct`, makes the local endpoint available after a health check; configure `NAV_LLM_BASE_URL` to match the service, and automatically stops the service on exit.
- `llm_client.py` reads `NAV_LLM_MODEL/BASE_URL/API_KEY` and sends `chat/completions` with image content blocks to the local endpoint. The client need not otherwise distinguish deployment type; the URL must remain local loopback.
- If GPU memory is insufficient, reduce `--gpu-memory-utilization` / `--max-model-len` through `NAV_VLLM_GPU_UTIL` / `NAV_VLLM_MAX_LEN`, or reduce `max_image`.

---

## G. Out-of-Scope Reminders

State these exemptions in the README's known deviations/exemptions section. You do **not** need to:

- Train or fine-tune any model; local VLM inference is zero-shot.
- Render observations or build a Matterport3DSimulator rendering backend; the GPU is for inference, not rendering.
- Download the provided model weights or use any remote navigation API.
- Download the 1.3 TB raw Matterport3D scans.
- Reproduce the full R2R val-unseen split or REVERIE.
- Reproduce BLIP-2 captioning / Faster R-CNN detection.
- Rerun component ablations.
- Copy a published metric table in place of NE, OSR, SR and SPL computed from the trajectories.

---

## H. Clean replay evidence contract

The only public execution entrypoint is:

```bash
bash /home/submission/reproduce.sh
```

It receives no arguments, runs offline, and must return nonzero when its own work fails.
`reproduce.sh`, `README.md`, `src/`, and authored configuration are source inputs. Everything
under `results/`, including logs, images, receipts, and metrics, is generated evidence. The
verifier deletes `results/` before replay, so no required configuration may live there.

Replay runs as uid/gid 65532 with external egress blocked. It writes the runner-owned audit files
under `/logs/verifier`, compares source manifests before and after execution, and freezes only a
successful unchanged replay at `/logs/verifier/candidate_outputs`. Only that frozen
root is assessed; pre-existing outputs, agent transcripts, and candidate summaries are not evidence.

## Clean Replay And Frozen Evidence

The sole public submission entry point is `bash /home/submission/reproduce.sh`. Authored inputs
such as `reproduce.sh`, `README.md`, `src/`, and configuration stay outside `/home/submission/results/`.
The verifier deletes those generated roots before replay, runs the entrypoint offline as uid/gid
65532, compares authored-file manifests before and after replay, and freezes the resulting
candidate evidence. Assessment reads only that frozen evidence root.

All replay dependencies, datasets, and model weights must already exist in the image or declared
read-only runtime paths. Runtime package installation, downloads, and external network access are
forbidden. Respect the verifier-provided `PBX_MAX_WORKERS` cap for every process or data worker.
A missing entrypoint or unchanged starter is `delivery_status != delivered` and is not a valid
measurement.
