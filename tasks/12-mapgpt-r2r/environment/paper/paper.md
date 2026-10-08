# MapGPT: Map-Guided Prompting with Adaptive Path Planning for Vision-and-Language Navigation

Jiaqi Chen, Bingqian Lin, Ran Xu, Zhenhua Chai, Xiaodan Liang, Kwan-Yee K. Wong
(The University of Hong Kong; Shenzhen Campus of Sun Yat-sen University; Meituan)

> **Source note:** This `paper.md` is a Markdown text extraction of `paper.pdf` (arXiv:2401.07314, ACL 2024). The text and table values follow the original paper; figures are in `paper_image/` (fig1–fig6). Consult `paper.pdf` if the extraction is ambiguous.
>
> - arXiv: https://arxiv.org/abs/2401.07314
> - Official code: https://github.com/chen-judge/MapGPT (access prohibited during reproduction; see the blacklist)

---

## Abstract

Embodied agents equipped with GPT as their brains have exhibited extraordinary decision-making and generalization abilities across various tasks. However, existing zero-shot agents for vision-and-language navigation (VLN) only prompt GPT-4 to select potential locations within localized environments, without constructing an effective "global" map for the LLM to understand the global environment. In this work, we present a novel **map-guided GPT-based agent**, dubbed **MapGPT**, which introduces an online linguistic-formed map to encourage global exploration. Specifically, we build an online map and incorporate it into the prompts that include node information and topological relationships, to help the agent understand the spatial environment. Benefiting from this design, we further propose an **adaptive path planning** mechanism to assist the agent in performing multi-step path planning based on a map, systematically exploring multiple candidate nodes or sub-goals step by step. Extensive experiments demonstrate that MapGPT is applicable to both GPT-4 and GPT-4V, achieving state-of-the-art zero-shot performance on the R2R and REVERIE benchmarks (~10% and ~12% improvements in SR) simultaneously.

---

## 1. Introduction

(See `paper_image/fig1.png` — Figure 1: A comparison of the thinking process between previous agents that only choose from a *local action space* and MapGPT which reasons over a *global map / action space*.)

Existing zero-shot VLN agents (e.g. NavGPT, DiscussNav) only let GPT choose among nearby navigable viewpoints, lacking a global map. MapGPT builds an online topological map, linguistically encodes it into the prompt, and adds adaptive multi-step path planning so the agent can explore globally and backtrack to non-adjacent prior nodes.

---

## 2. Related Work

Prior VLN agents use precomputed maps for global navigation (DUET, etc.), but how to construct a map and convert it into a form usable by an LLM prompt was previously uninvestigated. NavGPT/DiscussNav are two-stage, multi-expert text-only systems with high token cost.

---

## 3. Method

We introduce (3.1) the single-expert prompt system, (3.2) the map-guided prompting method, and (3.3) the adaptive multi-step path planning mechanism.

### 3.1 Single Expert Prompt System

Unlike two-stage multi-expert systems (NavGPT, DiscussNav), MapGPT uses a **single navigation expert**:

1. No separate history-summary expert or instruction-decomposing expert — convenient to inject visual/textual inputs and maps.
2. The navigation expert can use GPT-4V to decide directly from visual observations in one stage, or take text descriptions in a two-stage GPT-4 system.
3. Simple and efficient: two-stage system averages 672 input / 115 output tokens per step (vs NavGPT's 3 experts at 2,465 input / 317 output tokens per step).

(See `paper_image/fig2.png` — Figure 2: the prompt system. A **prompt manager (PM)** organizes fundamental inputs — instruction `I`, history `H_t`, observation `O_t`, action space `A_t` — together with the task description `D`, and feeds them to the LLM to produce the current thought `T_t` and selected action `a_{t,i} ∈ A_t`.)

Base pipeline:

```
T_t, a_{t,i} = LLM(PM(D, I, H_t, O_t, A_t))            (Eq. 1)
```

**Task Description (D)**: task background, input definitions, output requirements (see `paper_image/fig4.png`, Figure 4: task description prompts for R2R and REVERIE).

**Action Space (A_t)**: `a_{t,0}` is fixed as "A. stop", giving N+1 options. Each remaining option uses the template `"{label} {direction} {o_{t,i}}"`. The agent outputs a single option label, e.g. `"Action: B"`.

**History (H_t)**: all previous actions, template `"step 0: {a*_0}, ..., step t-1: {a*_{t-1}}"` (`a*` = selected action with label removed). Initial `H_0 = "The navigation has just begun, with no history"`.

### 3.2 Map-Guided Prompting

We convert the topological relationships of an online map into textual prompts (see `paper_image/fig2.png`(b)). GPT-4V struggles to understand environments from precise coordinates, so we use topology, not GPS coordinates.

**Topological Mapping**: store the map as a dynamically updated graph `G_t = {V_t, E_t}`, following DUET. `V_t = {v_{t,i}}` are K observed nodes indexed `i` in observation order; `E_t` records edges. At each step the simulator provides currently navigable neighbors, which update `G_{t-1} → G_t`.

#### 3.2.1 Constructing Maps with Prompts

Each step, observed nodes are categorized into three types:
1. **Explored nodes** `{en_j}` (including start node `en_0` and current node `en_t`);
2. **Accessible nodes** `{an_t}`;
3. **Unexplored inaccessible nodes** `{un}`.

**Trajectory** prompt: `"Trajectory: Place {en_0} ... {en_t}"`, where each `en_j` is a node index/ID in observation order (avoids repeated exploration).

**Map Connectivity**: only topological relationships are kept (no GPS). Template:
```
Map:
Place {en_0} is connected with Places {an_0}, ...
Place {en_1} is connected with Places {an_1}, ...
...
Place {en_t} is connected with Places {an_t}, ...
```
Note: this connectivity does **not** need updating if the agent backtracks/revisits explored nodes.

**Map Annotations**: rather than repeating descriptions, node IDs are embedded directly into the action space — each option is reformulated as `"{label} {direction} Place {an_t}: {o_{t,i}}"`. The agent finds explored nodes in `H_t` and accessible nodes in `A_t`. Unexplored inaccessible nodes are kept as **"Supplementary Info"** to help the agent choose the most suitable node to **backtrack** to (one-stage: raw images; two-stage: scene descriptions; "Nothing yet" if none).

### 3.3 Adaptive Path Planning

Instead of documenting every thought (NavGPT/DiscussNav), MapGPT requires the agent to dynamically generate and update **multi-step path planning** at each step. The agent combines thought, map, and previous planning to produce new planning. The process is iterative: the planning output of one step is the input to the next (`P_0 = "Navigation has just started, with no planning yet"`).

Full MapGPT pipeline:

```
T_t, P_t, a_t = LLM(PM(D, I, H_t, O_t, A_t, M_t, P_{t-1}))    (Eq. 2)
```

Beyond the usual thought + action, MapGPT outputs multi-step planning, letting the agent focus on multiple potential nodes/sub-goals (vs DUET's single probabilistic choice) and **adaptively update its plan — continuing to explore sub-goals or backtracking to a previous node for re-exploration**.

(See `paper_image/fig3.png` — Figure 3: a successful REVERIE case showing global exploration, map understanding, and adaptive multi-step path planning; the agent focuses on four candidate places and systematically explores until it finds the bathroom at Place 8.)

---

## 4. Experiments

### 4.1 Experimental Settings

Evaluated on **R2R** and **REVERIE**. For cost-effective comparison, a subset of **72 scenes / 216 cases** of R2R is used (Table 1, Table 4), and **500 instructions** sampled from REVERIE val-unseen (Table 3). "Exp" = number of GPT experts.

### 4.2 Experimental Results

**Table 1: Results on 72 various scenes of the R2R dataset.** (lower NE better; higher OSR/SR/SPL better)

| Methods | LLM | Exp | NE↓ | OSR↑ | SR↑ | SPL↑ |
|---|---|---|---|---|---|---|
| NavGPT (Zhou et al.) | GPT-3.5 | 3 | 8.02 | 26.4 | 16.7 | 13.0 |
| MapGPT (Ours) | GPT-3.5 | 1 | 8.48 | 29.6 | 19.4 | 11.6 |
| DiscussNav (Long et al.) | GPT-4 | 5 | 6.30 | 51.0 | 37.5 | 33.3 |
| MapGPT (Ours) | GPT-4 | 1 | 5.80 | 61.6 | 41.2 | 25.4 |
| **MapGPT (Ours)** | **GPT-4V** | **1** | **5.62** | **57.9** | **47.7** | **38.1** |

**Table 2: R2R validation unseen set** (11 scenes / 783 trajectories). MapGPT outperforms two non-pretrained methods and zero-shot NavGPT. (Full numbers in `paper.pdf`; key point: GPT-4V MapGPT reaches SPL ≈ 34.8%; due to distribution difference the absolute SR is slightly lower than the 72-scene subset.)

**Table 3: REVERIE — randomly sampled subset (500 instructions) of validation unseen.** (HAMT/DUET retested on the same subset.)

| Settings | Methods | OSR↑ | SR↑ | SPL↑ |
|---|---|---|---|---|
| Train | Seq2Seq | 8.07 | 4.20 | 2.84 |
| Train | RCM | 14.2 | 9.29 | 6.97 |
| Train | SMNA | 11.3 | 8.15 | 6.44 |
| Train | FAST-MATTN | 28.2 | 14.4 | 7.19 |
| Pretrain | HAMT | 35.4 | 31.6 | 29.6 |
| Pretrain | DUET | 50.0 | 45.8 | 35.3 |
| Pretrain | LAD | 64.0 | 57.0 | 37.9 |
| ZS | NavGPT | 28.3 | 19.2 | 14.6 |
| ZS | MapGPT (GPT-4) | 42.6 | 28.4 | 14.5 |
| ZS | MapGPT (GPT-4V) | 36.8 | 31.6 | 20.3 |

**Backtracking ratio**: MapGPT backtracks in 49% of REVERIE cases, correcting its path ≥once with 80% probability among those. NavGPT backtracks in only 18% of cases, correcting 53% of those.

### 4.3 Ablation Study

**Table 4: Ablation of map / planning designs on 72 R2R scenes.**

| LLM | Map | Planning | NE↓ | OSR↑ | SR↑ | SPL↑ |
|---|---|---|---|---|---|---|
| GPT-4 | × | × | 6.49 | 49.5 | 32.9 | 19.4 |
| GPT-4 | Topological | × | 6.40 | 59.7 | 37.5 | 24.8 |
| GPT-4 | Topological | Adaptive | 5.80 | 61.6 | 41.2 | 25.4 |
| GPT-4V | × | × | 5.96 | 58.8 | 42.6 | 34.7 |
| GPT-4V | Coordinate | × | 6.12 | 55.1 | 41.2 | 32.8 |
| GPT-4V | Topological | × | 5.89 | 56.5 | 44.9 | 36.5 |
| GPT-4V | Topological | Action | 5.82 | 58.3 | 45.4 | 35.6 |
| **GPT-4V** | **Topological** | **Adaptive** | **5.62** | **57.9** | **47.7** | **38.1** |

Key findings:
- **Topological map** clearly beats no-map and **beats coordinate (GPT) maps** — GPT understands topology better than precise coordinates.
- **Adaptive planning** further improves SR (e.g. GPT-4V: 44.9 → 47.7) over no planning, and over a simpler "Action"-only planning variant.

---

## 5. Conclusion

MapGPT introduces an online linguistic-formed topological map and adaptive multi-step path planning into a single-expert GPT-based VLN agent, achieving SOTA zero-shot performance on R2R and REVERIE for both GPT-4 and GPT-4V.

---

## Appendix (selected)

- **Figure 4** (`paper_image/fig4.png`): Task description prompts for R2R and REVERIE.
- **Figure 5** (`paper_image/fig5.png`): A successful R2R example showing crucial map-guided steps. The worked example includes a step-4 prompt with `Task Description / Instruction / History / Surroundings / Action options (incl. "A. stop") / Supplementary Info / Trajectory / Map / Previous Planning`, and the LLM response with `Thought / New Planning / Action`.
- **Figure 6** (`paper_image/fig6.png`): Two typical failure reasons — (a) stopping erroneously in similar locations; (b) failing to backtrack in time.

### Worked step example (from Figure 5, R2R)

```
Task Description: [Task background] [Input Definitions] [Output Requirements]
Instruction: Go to third level bathroom and clean the washbasin
History: step 0: go up to Place 2 ..., step 1: turn around to Place 3 ..., ..., step 3: turn around to Place 4 ...
Surroundings: plant, cabinet.
Action options (step 4): ['A. stop', 'B. turn right to Place 9 ...', 'C. turn around to Place 2 ...', 'D. turn around to Place 5 ...']
Supplementary Info:
  Place 1 ...; Place 6 ...; Place 7 ...; Place 8 ...
Trajectory: Place 0 2 3 2 4
Map:
  Place 0 is connected with Places 1, 2, 3
  Place 2 is connected with Places 0, 4, 3, 5, 6, 7, 8
  Place 3 is connected with Places 0, 2, 6, 7, 8, 5
  Place 4 is connected with Places 9, 2, 5
Previous Planning: If Place 4 turns out to be the bathroom, I will stop ...; otherwise return to Place 2 and explore Place 5, 6, 7, or 8 ...

# LLM output:
Thought: ... I am currently at Place 4, which does not appear to be a bathroom ... I should return to Place 2 and explore 5/6/7/8 ...
New Planning: I will explore Place 5, 6, 7, or 8 ... starting with Place 5 ... if not, return to Place 2 then Place 6, 7, 8 ...
Action: D.
```
