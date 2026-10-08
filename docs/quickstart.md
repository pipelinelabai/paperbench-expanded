# Run Your First Task

[Overview](../README.md) · [Task catalog](tasks.md) · [Evaluation](evaluation.md) · [HFSS setup](../README_HFSS.md)

## 1. Install the Launcher

Use Linux x86-64, Python **3.12+**, Docker Engine, and Docker Compose **2.27.0+**.
Your account must be able to use Docker. Initial image builds need access to
public dependency sources. GPU and commercial tasks have additional requirements.

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip --isolated install --index-url https://pypi.org/simple -r requirements.txt
python scripts/runner_compat.py --apply
cp .env.example .env
chmod 600 .env
```

The compatibility helper checks Harbor **0.21.0** and applies only the recognized
numeric-setting log-scrub fix. This prevents numeric environment settings from
being treated as secrets and corrupting recorded results. Use a dedicated virtual
environment; do not bypass the check by upgrading dependencies arbitrarily.

## 2. Inspect a Task Without Running It

```bash
python run.py list
python run.py check --task all
```

`check` validates Docker build inputs, workspace boundaries, task discovery, and
Harbor configuration. It does **not** build an image, call a model, check out a
license, run a scientific solver, or certify a score.

For an initial CPU workflow, task **06** has a self-contained Meep build recipe.
Read its [instruction](../tasks/06-gmr-grating-fano-meep/instruction.md),
[paper supplement](../tasks/06-gmr-grating-fano-meep/environment/paper/addendum.md),
and [rubric](../tasks/06-gmr-grating-fano-meep/tests/rubric.json) before running it.
This is an entry point for learning the workflow, not a promise of an easy or fast
scientific solution.

## 3. Configure the Solving Agent and Independent Judge

Edit your private `.env`. These settings serve different roles:

| Variable | Purpose |
|---|---|
| `AGENT_TYPE` | Launcher adapter: `claude-code` or `codex` |
| `AGENT_MODEL` | Actual model identifier accepted by the solving service |
| `AGENT_API_KEY` | Solving-service credential |
| `AGENT_BASE_URL` | Solving-service base URL, compatible with the adapter |
| `JUDGE_MODEL` | Actual model identifier used for independent grading |
| `JUDGE_API_KEY` | Judge-service credential, not passed to the solving agent |
| `JUDGE_BASE_URL` | Judge-service base URL |
| `JUDGE_TRANSPORT` | `openai` for 01–03 and 05/09/10; either protocol for 04/06/07/08/11; `anthropic` for 12 |

### Match the Protocol, Not Just the Model Name

- `AGENT_TYPE=claude-code` needs an Anthropic Messages-compatible service.
- `AGENT_TYPE=codex` uses a Responses-compatible service through the launcher's
  `wire_api="responses"` configuration; a Chat Completions-only endpoint is not
  sufficient for this adapter.
- `JUDGE_TRANSPORT=openai` uses Chat Completions with tool calling and any image
  inputs required by the task.
- `JUDGE_TRANSPORT=anthropic` needs Messages, tool calling, and any required image
  inputs. Tasks 01–03 require their OpenAI-compatible artifact reviewer; task 12
  requires its Anthropic-compatible evaluator. The native scientific judges for
  05/09/10 also require `openai`.

Use the provider's **base URL**, not the complete `/messages`, `/responses`, or
`/chat/completions` request URL. Adapter names are not model IDs. The adapters are
pinned to Claude Code **2.1.232** and Codex **0.153.4** in this release.

Tasks 05–08 use `JUDGE_API_KEY`, `JUDGE_BASE_URL`, `JUDGE_MODEL` and
`JUDGE_TRANSPORT` for grading. The task configs forward these variables even
when the launcher is not used; unrelated provider credentials are optional.
For 06–08, explicit scorer CLI options take precedence, followed by the
canonical judge variables and then legacy provider aliases. An explicit
`PBX_LLM_TRANSPORT` takes precedence over `JUDGE_TRANSPORT`.

Keep credentials out of shell history, task files, images, and public logs. The
launcher writes environment references rather than actual API keys into generated
configuration. Use HTTPS where available; embedded credentials and URL query
parameters are rejected. Environment files must have mode `0600` and are read as
data, not executed as shell scripts.

The root `.env` is loaded automatically if present. Select another private file
with `--env-file /absolute/path/to/private.env`. This is useful when switching
between task 12's judge protocol and the other tasks.

## 4. Check, Build, and Run

```bash
python run.py check --task 06 --host
python run.py build --task 06
python run.py config --task 06
python run.py run --task 06 --concurrency 1 --job-name first-task06
python run.py summary jobs/first-task06
```

| Command | What it does | Starts a scientific evaluation? |
|---|---|---|
| `list` | Shows tasks and configured budgets | No |
| `check` | Validates the package; `--host` also checks host prerequisites | No |
| `build` | Builds task images and saves private build logs | No |
| `config` | Writes a private Harbor configuration | No |
| `run` | Builds the environment, runs the agent, replays the submission, and grades it | **Yes: consumes model APIs and compute** |
| `summary` | Reads a completed or partial job and separates scores from failures | No |

`build` is optional: `run` builds the task image through Harbor. A prior build can
warm Docker's cache but does not count as a trial. Generated configurations and
build logs go under `runs/`; evaluation jobs go under `jobs/`.

Task selectors accept `6`, `06`, or the complete task-directory name. CPU tasks
may be selected together, for example `--task 04 06`. GPU tasks **09 and 12 must
each run alone with concurrency 1**; do not use `run --task all`. Increase CPU
concurrency only after confirming combined memory, CPU, and license availability.

Default settings are one concurrent trial, one attempt, and no automatic retries.

### Native Replay for Tasks 05, 09 and 10

Use the same `python run.py run` command. The launcher selects the trusted host
verifier automatically. It stops the solving container, exports immutable source
and static inputs, and runs `bash reproduce.sh` in a fresh container using the
same image ID. Replay has no network or judge credentials, read-only source and
root filesystem, and only newly generated outputs. Task09 retains its assigned
GPU; task10 writes replay outputs to a local Docker volume and archives them
before removing the volume.

The host then runs independent numerical checks and the judge. Install the
complete root `requirements.txt`; its scientific Python dependencies are separate
from the native solver environment. No Docker socket or private tests are exposed
to the solving agent. Evidence and results are under the trial's
`verifier/native_replay/`, `verifier/review/` and `verifier/result.json`.
Infrastructure failures withhold the reward rather than becoming a scientific
zero.
For task05, a failed reference computation, missing summary or invalid summary
also withholds the reward. A successful reference computation that reports
missing candidate cases remains eligible for the existing evidence-based
partial-credit rules; evaluator failures are not substituted for missing
scientific evidence.
`--attempts` and `--retries` increase consumption. For unattended execution, add
`--yes` only when you intend to accept Harbor's execution prompts.

## 5. Special Environment Requirements

### Tasks 01–03: Commercial HFSS

Provide an authorized HFSS runtime image and a reachable license server. Neither
is distributed here. See [the task-specific HFSS guide](../README_HFSS.md) for
required software paths, missing-image troubleshooting, and separate task commands.

### Task 09: GPU Quantum Chemistry

Provide an NVIDIA GPU, a driver compatible with CUDA **12.4**, and NVIDIA Container
Toolkit. The included Dockerfile builds the PySCF / GPU4PySCF environment.

```bash
nvidia-smi
```

Set `GPU_ID` explicitly to an available GPU index or UUID in `.env`, then:

```bash
python run.py check --task 09 --host
python run.py run --task 09 --concurrency 1
```

The launcher does not pick a GPU silently or fall back to CPU. Its busy-GPU check
is not a cross-user reservation or a replacement for your scheduler.

### Task 12: Local Navigation VLM

Task 12 needs no host-side asset directories. Its build defaults to
`suermars/paperbenchx-mapgpt-r2r-full` on DockerHub, which provides the runtime,
RGB observations and Qwen2.5-VL-7B-Instruct weights. The task configuration pins
the image digest so a later change to `latest` does not silently change a run.
Leave `MAPGPT_BASE_IMAGE` empty to use that default:

```dotenv
# Optional override: build on your own authorized runtime instead (see the
# runtime contract below). Leave unset to use the pinned DockerHub default.
MAPGPT_BASE_IMAGE=
GPU_ID=YOUR_AVAILABLE_GPU
JUDGE_TRANSPORT=anthropic
NAV_LLM_BASE_URL=
```

The template deliberately leaves `NAV_LLM_BASE_URL` empty. The packaged helper
exports it after starting the **container-local navigation service**. If using
another local deployment, set the URL to that service, for example
`http://localhost:8000/v1`, and start it in `reproduce.sh`.
The task uses local Qwen2.5-VL-7B for navigation, not the solving agent
or remote judge. Never substitute a remote navigation endpoint or reuse judge
credentials for navigation. `NAV_LLM_API_KEY=local` is a local-service placeholder,
not a real API credential.

A runtime image must support Ubuntu/Debian build steps and provide CUDA, Python,
`vllm`, the subset annotations at
`/home/data/R2R/annotations/MapGPT_72_scenes_processed.json`, connectivity graphs
at `/home/data/connectivity/`, the RGB observations at `/home/data/RGB_Observations/`,
and the Qwen2.5-VL-7B-Instruct weights at `/home/models/Qwen2.5-VL-7B-Instruct/`.
The task build installs everything else, including the current
`/usr/local/bin/serve_nav_vllm.sh` (older runtime images carry a version that cannot
serve the task's multi-image prompts). It must not contain reference solutions,
private evaluator files, or previous answers. The RGB observations and the model
weights retain their own license/access conditions; the default image is published
only where those terms allow, and building on your own runtime keeps that choice
with you. The default registry is DockerHub; GitHub Packages is not required.
If registry access or pull limits prevent provisioning, configure DockerHub
authentication or set `MAPGPT_BASE_IMAGE` to a compatible runtime you can access.

```bash
python run.py check --task 12 --host
python run.py run --task 12 --concurrency 1
```

### Task 10: Local Docker Workspace Storage

Task 10 uses a per-trial Docker volume for `/home/submission`. Docker's data
directory must be on a local filesystem such as ext4/XFS, not NFS/CIFS. Logs can
be archived separately. The verifier preserves source and evidence under
`verifier/source_submission/` and `verifier/candidate_outputs/`; do not rely on
`agent/submission/` for this task. If stopping a container manually before
archival, save the workspace with `docker cp` before removing its volume.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Packaging passes but execution fails | Packaging is not a native-solver, GPU-memory, or license checkout test |
| Missing HFSS image/license | Follow [HFSS setup](../README_HFSS.md); an unrelated Linux/Python image is not sufficient |
| Task 12 refuses to start | Configure its base image, read-only assets, available GPU, local navigation URL, and Anthropic judge |
| API requests fail | Check actual model IDs, adapter/protocol compatibility, provider base URLs, and tool/image support |
| Replay cannot install a dependency | Install it during image building or otherwise provision it before offline replay |
| No score or withheld score | Inspect verifier failure/status files; do not interpret infrastructure or judge errors as scientific zeroes |
| Image build stops for storage | The default Docker free-space reserve is 30 GiB; provision more space or explicitly configure `PBX_BUILD_MIN_FREE_GIB` |

Public dependency sources are configured through `PBX_PIP_INDEX_URL`,
`PBX_APT_MIRROR`, and `PBX_NPM_REGISTRY`. `PBX_APT_MIRROR` takes a hostname, not a
full URL. Keep TLS verification enabled. Dependencies and data must be available
**before** offline scientific replay; build-time network access does not permit
replay-time downloads.

Budget values are limits, not completion-time estimates. See the
[task catalog](tasks.md) before scheduling a run.
