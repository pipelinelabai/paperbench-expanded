# HFSS Runtime Setup — Tasks 01, 02, and 03

## What Is Not Included

This repository does not distribute ANSYS AEDT/HFSS, a commercial solver license,
license-server access, or a prebuilt commercial runtime image. You must provide
an image and license you are authorized to use. There is no default image,
license server, fixed hostname, MAC address, or machine identity.

The task Dockerfiles extend your base image with public task materials and
dependencies. They do not install the commercial solver for you.

## Task-Specific Requirements

| Task | Task directory | Scientific workload | Required runtime |
|---|---|---|---|
| 01 | `tasks/01-cpw-quad-port-uwb-mimo/` | Four-port CPW UWB MIMO antenna | AEDT/HFSS 2025 R1 with an authorized solver license |
| 02 | `tasks/02-anisotropic-coding-diffusion-metasurface/` | Anisotropic coding diffusion metasurface | AEDT/HFSS 2025 R1 with an authorized solver license |
| 03 | `tasks/03-dual-passband-angular-stable-fss/` | Dual-passband angular-stable FSS | AEDT/HFSS 2025 R1 with an authorized solver license |

All three currently use the same base-image interface, but each has its own
Dockerfile, paper, scientific submission contract, budget, and verifier. You may
use one compatible authorized base image for all three. If different images are
needed, use a separate private environment file for each task. Do not copy solver
results between tasks or treat a successful image build as scientific evidence.

The base image must provide:

- Linux x86-64 and the `dnf` package manager used by the task Dockerfiles.
- ANSYS AEDT/HFSS 2025 R1 installed under `/ansys_inc/v251/AnsysEM/`.
- The embedded Python executable at
  `/ansys_inc/v251/AnsysEM/commonfiles/CPython/3_10/linx64/Release/python/bin/python3.10`.
- The libraries and runtime environment needed for native HFSS execution.
- License-server connectivity permitted by your ANSYS license terms.

Do not use an image containing reference solutions, private verifier inputs, or
precomputed submission results. Public redistribution requires separate clearance.

## Configure Your Runtime

Create a private configuration file from the public template:

```bash
cp .env.example .env
chmod 600 .env
```

Fill these values in `.env` with your own available image and license server:

```dotenv
HFSS_BASE_IMAGE=YOUR_AUTHORIZED_REGISTRY/YOUR_HFSS_RUNTIME:YOUR_FIXED_TAG
ANSYSLMD_LICENSE_FILE=YOUR_LICENSE_PORT@YOUR_LICENSE_SERVER
JUDGE_TRANSPORT=openai
```

These are placeholders, not usable credentials. Use a fixed image tag that you
control. A registry image reference or an existing local image reference is
accepted; no image-checksum inventory is supplied. Configure the agent and judge
API variables separately before a full run. Task 12's `NAV_LLM_BASE_URL` is not
used by these HFSS tasks.

For separate task configurations, copy the template to `.env.01`, `.env.02`, and
`.env.03`, give each mode `0600`, and set its own `HFSS_BASE_IMAGE` and license
configuration. Select the corresponding file using `--env-file`.

## If the Image Is Missing

First verify that the image exists locally:

```bash
docker image inspect YOUR_AUTHORIZED_IMAGE_REFERENCE
```

If it is a remote image you are entitled to access, authenticate to that registry
and pull it:

```bash
docker login YOUR_AUTHORIZED_REGISTRY
docker pull YOUR_AUTHORIZED_IMAGE_REFERENCE
```

Keep credentials in Docker's credential mechanism, not task files. If the image
does not exist or you lack access, obtain a compatible runtime from your
organization's authorized ANSYS administrator, or build one from licensed
installation media under the vendor's terms. Do not substitute an unrelated
Python/Linux image: it will not contain HFSS or the embedded ANSYS Python.

Useful failure distinctions:

- Empty `HFSS_BASE_IMAGE`: configure your image reference first.
- Registry authentication failure: confirm registry access and Docker login.
- Image/tag not found: confirm the repository/tag or load your authorized local image.
- Missing `dnf` or embedded Python: the base image is incompatible with the Dockerfile.
- License checkout failure: confirm the server, port, entitlement, and permitted
  container-to-server connectivity; an image alone does not grant a license.
- Native solve failure: inspect the task's actual solver logs. Passing a setup
  check is not proof of a working solve or full score.

## Build and Run Each Task Separately

Packaging checks do not need a commercial image or model API calls:

```bash
python run.py check --task 01 02 03
```

After supplying your image and license, check the host configuration:

```bash
python run.py check --task 01 02 03 --host --env-file .env
```

Build one task without starting the solving agent or scientific verifier:

```bash
python run.py build --task 01 --env-file .env
python run.py build --task 02 --env-file .env
python run.py build --task 03 --env-file .env
```

After completing the agent/judge API configuration, run the selected task:

```bash
python run.py run --task 01 --concurrency 1 --env-file .env
python run.py run --task 02 --concurrency 1 --env-file .env
python run.py run --task 03 --concurrency 1 --env-file .env
```

Use `.env.01`, `.env.02`, or `.env.03` instead if you maintain separate runtimes.
Each full run consumes solver resources and model API calls. Respect each task's
declared budgets and your license's concurrency limits. Scientific scoring still
requires native execution and the task's clean-replay evidence contract.
