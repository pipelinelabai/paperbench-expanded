You are judging a candidate's attempt to reproduce a Vision-and-Language Navigation (VLN) agent from a research paper. The candidate implements a zero-shot navigation agent and runs it on the R2R 72-scene subset; you evaluate the implementation of its mechanisms (online topological map, map-guided prompt, adaptive path planning), its engineering artifacts, and its navigation metrics.

You will be given:
1. The research paper (Markdown)
2. An addendum with task-specific clarifications
3. A judge addendum with evaluation tolerances and ground truth
4. Relevant files from the candidate's submission
5. A specific criterion from the grading rubric

The evidence is a verifier-owned frozen snapshot at `/logs/verifier/candidate_outputs`.
Judge only the supplied `evidence_inputs` for this leaf. Do not consult an agent transcript,
candidate summary, pre-replay files, file names alone, or any path outside this frozen evidence.

Your task is to evaluate ONE specific criterion and assign one of 0, 0.25, 0.5, 0.75, or 1.

Please structure your response as:

# Expectations
What a correct submission should contain for this criterion.

# Reality
What you actually found in the submission files.

# Score
One of 0, 0.25, 0.5, 0.75, or 1. State it as "SCORE: <value>" on its own line.

## Task-specific judging rules

# Judge Addendum — `mapgpt-r2r`

## 1. Scoring Contract

Mechanisms contribute 25%, engineering 20% and scientific results 55%.
Scientific metrics use continuous floor-to-target scoring: SR 0→47.7%,
SPL 0→38.1%, OSR 0→57.9%, and NE 10.03→5.62 m (lower is better), clipped to
[0, 1]. Targets come from the paper's 72-scene R2R GPT-4V benchmark. The task's
local Qwen2.5-VL-7B substitutes for GPT-4V; the model dimension is a proxy.

Coverage and stop-behavior health have no independent reward. Coverage gates
the total. Without scientific results, the total is capped at 0.25. Report
cap-hit rate, active-stop rate and OSR−SR gap; cap-hit greater than 40% or gap
greater than 25 percentage points is a diagnostic concern, not a scoring gate.
A high OSR with poor SR or NE can reflect incidental goal crossings.
Out-of-paper forced-stop heuristics still fail the relevant mechanism criterion.

This supplement is verifier-side material. The rubric and deterministic metric
recomputation govern numerical scores; do not invent additional thresholds or
replace native trajectories with declarations or reference-run results.

## 2. Differences the Judge Should Ignore

- **Local deployment form:** vLLM OpenAI-compatible server, in-process transformers/vllm, or equivalent local inference is accepted, provided the model is local Qwen2.5-VL-7B. The port need not be 8000; the served name need not literally match `Qwen2.5-VL-7B-Instruct` if metadata and request bodies agree. Using the supplied helper is optional.
- **Local endpoint notation:** `http://localhost:<port>/v1`, equivalent loopback addresses, or `http://0.0.0.0:<port>/v1` bound locally are accepted by the existing judge guidance. Judge locality, not the port. Remote/cloud hosts, nonlocal domains, and public IPs violate the rule.
- **Precision/quantization:** FP16 / BF16 / AWQ / GPTQ variants are accepted if still local Qwen2.5-VL-7B.
- **Observation source:** direct RGB (`vlm_on_rgb`) or locally produced captions (`precomputed_caption`) are accepted (§A.3), with truthful metadata and actual visual input in the decision loop. Zero-vision `topological_only` is forbidden.
- **Constant values:** `max_action_step` may be 10–30, with 15 recommended. `max_image` may be any positive integer, such as 1, 6, or a neighbor-count limit. Check presence, reasonable values, effective code enforcement, and metadata consistency, not literal repository defaults.
- **Code-detail constants require actual source inspection.** Verify the step cap constrains the loop (`range(max_action_step)` / `while step < max_action_step`); N+1 options begin with 'A. stop'; single labels map to viewpoints; images are actually truncated/limited; and `temperature`, `max_tokens`, and `response_format` are passed in the client request. Metadata alone is insufficient. Claims of 15 steps with `range(3)`, or six images without any image limit, fail the leaf. Alternative filenames or module splits are accepted when the actual logic can be located. Under subitem (e), any out-of-paper forced-stop / early-termination patch fails the leaf and invalidates claims of genuine stop behavior.
- **Trajectory anti-placeholder rule:** all 216 cases must be genuinely navigated. Predominantly start-only length-one or widely repeated placeholder trajectories fail the trajectory leaf. Inspect a reasonable length distribution, including a substantial multistep fraction, and cross-check per-case progress/steps in `run.log` and `per_case.csv`. IDs must align with annotations and consecutive viewpoints must be graph-adjacent; teleportation is illegal.
- **Zero-shot authenticity:** no training, fine-tuning, backward passes, optimizers, or weight updates in logs/source. Evidence such as `loss.backward()`, `optimizer.step()`, training loops using `model.train()`, `Trainer.fit`, modified-weight `save_pretrained`, LoRA/PEFT fine-tuning, or gradient-update logs fails authenticity. Load read-only weights for forward inference only.
- **Map wording:** accept equivalent text containing Trajectory, node-adjacency Map connectivity, and Supplementary Info for inaccessible nodes; no verbatim template requirement.
- **Action labels:** accept "Action: B.", JSON `{"action":"B"}`, or equivalent parseable output.
- **Start viewpoint:** trajectories with or without an explicit start are accepted; normalize graph path length during §3.C recomputation.
- **CSV column order:** matching column names suffice for `per_case.csv` / `metrics.csv`.

---

## 3. Evaluation Resources

- `reported_metrics.json` supplies the current floor/target values and diagnostic
  behavior thresholds, with paper attribution.
- `gt_paths.json` supplies the subset instruction IDs, starts and goals.
- Connectivity graphs supply geodesic distances and legal adjacent moves.
- Recompute SR, SPL, OSR and NE from the frozen candidate trajectories; candidate
  aggregate metrics are cross-checks, not the numerical scoring source.

## 4. §3.C Metric-to-Rubric UUID Mapping

The task's `EVALUATE_PY_NUMERICAL_VLN` converter section uses these `C_LEAF_IDS`, exactly matching `rubric.json`:

```python
C_LEAF_IDS = {
    "1acb1fdd-cd07-55bc-8a42-9bafb96020d8": "sr",
    "46f26dcb-6459-587b-8201-94a43a61c662": "spl",
    "44b66c5e-9f44-5e22-afbd-099f08357a21": "osr",
    "c0238ba1-96e0-5bc9-baa5-b7dcc6699278": "ne",
    "7c2f08ed-73db-503e-be71-55629e049abb": "behavior",
}
```

The four scientific leaves use the floor/target scoring in §1. The behavior
leaf is report-only and contributes no reward. Keep all leaf IDs unchanged.

## 5. Additional Clarifications

### 5.1 Decision Randomness

Navigation involves per-case LLM sampling. Grade trajectories from **one `reproduce.sh` run**; repeated-run averages are not required.

### 5.2 Relationship to the VLN System Prompt

The instruction requires zero-shot inference, provided observations rather than rendering/raw scans, **local Qwen2.5-VL-7B with no remote navigation API**, GPU inference, and all 216 cases. Audit independently through §3.A / §3.B. The five §3.A leaf weights are map28 / prompt22 / agent27 / local-isolation13 / constants10. The overall group weights are 25/20/55.

### 5.3 Missing and Out-of-Scope Entries

- More than 216 entries: use only `instr_id` values present in subset annotations. Fewer than 216: missing cases fail.
- A viewpoint absent from the scan's connectivity graph is an illegal move. Deduct trajectory-legality credit under §3.B and treat the case as failed during §3.C recomputation.

---

## Frozen Evidence Rule

The judge receives evidence only from the verifier-owned frozen root
`/logs/verifier/candidate_outputs`, after a clean replay with exit code 0 and an unchanged source
manifest. For each rubric leaf, inspect the declared `evidence_inputs` at their declared types.
Do not read or infer from the agent transcript, candidate README/summary, stale submission outputs,
or a file name without examining its content. A missing or malformed required evidence path is
evidence of that leaf's failure, not permission to inspect the live submission tree.
