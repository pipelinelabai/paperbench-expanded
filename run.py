"""List, validate and launch PaperBench High-Difficulty and Expanded Tasks tasks 01–12 with private API settings."""

import argparse
import asyncio
from datetime import datetime
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
from urllib.parse import urlparse

import yaml

from scripts.runner_compat import check_runner
from scripts.container_contract import audit_task
from scripts.summarize_scores import summarize
from scripts.build_images import build_images


ROOT = Path(__file__).resolve().parent
GPU_TASKS = {"09", "12"}
HFSS_TASKS = {"01", "02", "03"}
SECRET_REFERENCE = "${JUDGE_API_KEY}"


def catalog(root=ROOT):
    records = []
    for path in sorted((root / "tasks").glob("*/task.toml")):
        records.append({"number": path.parent.name.split("-", 1)[0],
                        "name": path.parent.name, "path": path.parent,
                        "config": tomllib.loads(path.read_text())})
    if [item["number"] for item in records] != [f"{number:02d}" for number in range(1, 13)]:
        raise ValueError("Expected exactly twelve task packages, numbered 01–12.")
    return records


def select_tasks(selectors, root=ROOT):
    records = catalog(root)
    if selectors == ["all"]:
        return records
    chosen = set()
    for selector in selectors:
        matches = [item for item in records if selector in {
            item["number"], str(int(item["number"])), item["name"], item["name"].split("-", 1)[1]}]
        if len(matches) != 1:
            raise ValueError(f"Unknown or ambiguous task: {selector}")
        chosen.add(matches[0]["name"])
    return [item for item in records if item["name"] in chosen]


def release_errors(records):
    return [f'{item["name"]}: scored evaluation is disabled by task configuration; '
        'see task.toml metadata.'
        for item in records if item['config'].get('metadata', {}).get('harbor_scoring_enabled') is False]


def load_environment(path):
    if path is not None:
        from dotenv import load_dotenv
        path = path.resolve()
        if not path.is_file():
            raise ValueError(f"Environment file not found: {path}")
        if path.stat().st_mode & 0o077:
            raise ValueError("Private environment file must have mode 0600; run chmod 600 on it.")
        load_dotenv(path, override=True, interpolate=False)


def agent_config(adapter, model, environ):
    if adapter == "oracle":
        return {"name": adapter, "n_concurrent": 1, "env": {}}
    endpoint = environ.get("AGENT_BASE_URL") or "https://agent.example.invalid/v1"
    parsed_endpoint = urlparse(endpoint)
    if parsed_endpoint.scheme not in {"http", "https"} or not parsed_endpoint.hostname or parsed_endpoint.username or parsed_endpoint.password or parsed_endpoint.query or parsed_endpoint.fragment or any(character.isspace() for character in endpoint):
        raise ValueError("AGENT_BASE_URL must be an HTTP(S) endpoint without embedded credentials or query parameters.")
    common = {"name": adapter, "model_name": model, "n_concurrent": 1}
    if adapter == "claude-code":
        common.update({"kwargs": {"version": "2.1.232", "reasoning_effort": "max", "max_thinking_tokens": 32000},
                       "env": {"ANTHROPIC_API_KEY": "${AGENT_API_KEY}", "ANTHROPIC_BASE_URL": "${AGENT_BASE_URL}",
                               "BASH_DEFAULT_TIMEOUT_MS": "39600000", "BASH_MAX_TIMEOUT_MS": "86400000",
                               "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000"}})
    elif adapter == "codex":
        common.update({"kwargs": {"version": "0.153.4", "reasoning_effort": "high",
                                  "config": {"model_provider": "configured_endpoint", "model_providers": {
                                      "configured_endpoint": {"name": "Configured endpoint", "base_url": endpoint,
                                                              "env_key": "OPENAI_API_KEY", "wire_api": "responses", "supports_websockets": False}}}},
                       "env": {"OPENAI_API_KEY": "${AGENT_API_KEY}", "OPENAI_BASE_URL": "${AGENT_BASE_URL}",
                               "CODEX_UNSAFE_ALLOW_NO_SANDBOX": "1"}})
    else:
        raise ValueError("Unsupported agent adapter: " + adapter)
    return common


def build_config(records, adapter=None, model=None, concurrency=1, attempts=1, retries=0,
                 job_name=None, environ=None, gpu_overlay=None, root=ROOT):
    environ = os.environ if environ is None else environ
    if min(concurrency, attempts) < 1 or retries < 0:
        raise ValueError("Concurrency and attempts must be positive; retries cannot be negative.")
    gpu_records = [item for item in records if item["number"] in GPU_TASKS]
    if gpu_records and (len(records) != 1 or concurrency != 1):
        raise ValueError("Run GPU tasks separately from CPU tasks, at concurrency 1 per selected GPU.")
    model = model or environ.get("AGENT_MODEL") or "REPLACE_WITH_AGENT_MODEL"
    adapter = adapter or environ.get("AGENT_TYPE") or "claude-code"
    if adapter == "oracle":
        missing = [item["name"] for item in records if not (item["path"] / "solution" / "solve.sh").is_file()]
        if missing:
            raise ValueError("No packaged Oracle solution for: " + ", ".join(missing))
    agent = agent_config(adapter, model, environ)
    agent["n_concurrent"] = concurrency
    transport = environ.get("JUDGE_TRANSPORT") or ("anthropic" if any(item["number"] == "12" for item in records) else "openai")
    if transport not in {"auto", "openai", "anthropic"}:
        raise ValueError("JUDGE_TRANSPORT must be auto, openai or anthropic.")
    native_verifier = any(item['config'].get('metadata', {}).get('verifier_backend') == 'host_native_replay'
                          for item in records)
    if native_verifier and transport != 'openai':
        raise ValueError('Tasks 05/09/10 require JUDGE_TRANSPORT=openai for their scientific judge.')
    if any(item["number"] in HFSS_TASKS for item in records) and transport != "openai":
        raise ValueError("HFSS tasks 01–03 require JUDGE_TRANSPORT=openai with tool calling.")
    if any(item["number"] == "12" for item in records) and transport != "anthropic":
        raise ValueError("Task 12's unchanged evaluator requires JUDGE_TRANSPORT=anthropic.")
    verifier = {"JUDGE_MODEL": environ.get("JUDGE_MODEL") or "REPLACE_WITH_JUDGE_MODEL",
                "PBX_LLM_TRANSPORT": transport, "PBX_ALLOW_MISSING_IPTABLES": "0",
                "PBX_ALLOW_NETWORK_ISOLATION_FAILURE": "0"}
    for key in ("JUDGE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        verifier[key] = SECRET_REFERENCE
    for key in ("JUDGE_API_BASE", "JUDGE_BASE_URL", "OPENAI_API_BASE", "OPENAI_BASE_URL"):
        verifier[key] = "${JUDGE_BASE_URL}"
    # Task 12's unchanged evaluator speaks the Anthropic API; some gateways expose it
    # under a different path prefix than the OpenAI-compatible one.
    verifier["ANTHROPIC_BASE_URL"] = "${" + (
        "JUDGE_ANTHROPIC_BASE_URL" if environ.get("JUDGE_ANTHROPIC_BASE_URL") else "JUDGE_BASE_URL") + "}"
    if any(item["number"] in HFSS_TASKS for item in records):
        verifier["ANSYSLMD_LICENSE_FILE"] = "${ANSYSLMD_LICENSE_FILE}"
    if any(item["number"] == "12" for item in records):
        navigation = {"NAV_LLM_MODEL": "Qwen2.5-VL-7B-Instruct",
                      "NAV_LLM_BASE_URL": environ.get("NAV_LLM_BASE_URL", ""), "NAV_LLM_API_KEY": "local"}
        agent["env"].update(navigation)
        verifier.update(navigation)
    environment = {"type": "docker", "force_build": True, "delete": True}
    if gpu_records:
        environment = {"import_path": "scripts.harbor_docker_gpu_env:GpuDockerEnvironment", "force_build": True, "delete": True}
        if gpu_overlay is not None:
            environment["extra_docker_compose"] = [str(gpu_overlay.resolve())]
    if job_name and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", job_name):
        raise ValueError("Job name must be a simple name, not a path.")
    verifier_config = {"env": verifier}
    if native_verifier:
        verifier_config['import_path'] = 'scripts.harbor_native_verifier:NativeReplayVerifier'
    return {"job_name": job_name or "paperbench-expanded_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "jobs_dir": str((root / "jobs").resolve()), "n_attempts": attempts, "n_concurrent_trials": concurrency,
            "debug": False, "retry": {"max_retries": retries}, "environment": environment,
            "agents": [agent], "verifier": verifier_config,
            "datasets": [{"path": str(item["path"].parent.resolve()), "task_names": [item["name"]]} for item in records]}


async def discover_tasks(parsed):
    groups = await asyncio.gather(*(dataset.get_task_configs() for dataset in parsed.datasets))
    return [task for group in groups for task in group]


def validate_config(config):
    from harbor.models.job.config import JobConfig
    parsed = JobConfig.model_validate(config)
    tasks = asyncio.run(discover_tasks(parsed))
    if len(tasks) != sum(len(dataset["task_names"]) for dataset in config["datasets"]):
        raise ValueError("Harbor did not discover exactly the requested tasks.")
    return parsed


def required_environment_errors(config, environ):
    errors = []
    if config['verifier'].get('import_path') == 'scripts.harbor_native_verifier:NativeReplayVerifier':
        import importlib.util
        for module in ('numpy', 'scipy', 'h5py'):
            if importlib.util.find_spec(module) is None:
                errors.append('Install requirements.txt before native verification; missing ' + module)
    oracle = config["agents"][0]["name"] == "oracle"
    required = (["JUDGE_API_KEY", "JUDGE_BASE_URL"] if oracle
                else ["AGENT_API_KEY", "AGENT_BASE_URL", "JUDGE_API_KEY", "JUDGE_BASE_URL"])
    for key in required:
        value = environ.get(key, "")
        if not value.strip() or "REPLACE_WITH" in value or "example.invalid" in value or value.startswith(('${', 'YOUR_')):
            errors.append("Set " + key + " in your private environment file.")
    for key in (["JUDGE_BASE_URL"] if oracle else ["AGENT_BASE_URL", "JUDGE_BASE_URL"]):
        value = environ.get(key, "")
        parsed = urlparse(value)
        if value and (parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or any(character.isspace() for character in value)):
            errors.append(key + " must be an HTTP(S) endpoint without embedded credentials or query parameters.")
    models = [("JUDGE_MODEL", config["verifier"]["env"]["JUDGE_MODEL"])] if oracle else [
        ("AGENT_MODEL (or --model)", config["agents"][0].get("model_name")),
        ("JUDGE_MODEL", config["verifier"]["env"]["JUDGE_MODEL"])]
    for label, value in models:
        if not value or "REPLACE_WITH" in value or value.startswith('YOUR_'):
            errors.append("Set " + label + ".")
    return errors


def runtime_environment_errors(records, environ):
    errors = []
    for key, selected in (
        ("HFSS_BASE_IMAGE", any(item["number"] in HFSS_TASKS for item in records)),
    ):
        if selected:
            image = environ.get(key, "")
            if not image or any(character.isspace() for character in image) or image.startswith(('${', 'YOUR_')):
                errors.append("Set " + key + " to your authorized, available Docker image reference.")
    if any(item["number"] in HFSS_TASKS for item in records) and not environ.get("ANSYSLMD_LICENSE_FILE", "").strip():
        errors.append("HFSS tasks 01–03 require ANSYSLMD_LICENSE_FILE for your own reachable license server; see README_HFSS.md.")
    if any(item["number"] == "12" for item in records):
        image = environ.get("MAPGPT_BASE_IMAGE", "")
        if image and (any(character.isspace() for character in image) or image.startswith(('${', 'YOUR_'))):
            errors.append("MAPGPT_BASE_IMAGE must be a Docker image reference, or left unset to use the default runtime.")
    return errors


def navigation_environment_errors(records, environ):
    if not any(item["number"] == "12" for item in records):
        return []
    endpoint = environ.get("NAV_LLM_BASE_URL", "")
    parsed = urlparse(endpoint)
    local = parsed.hostname == "localhost"
    if parsed.hostname and not local:
        try:
            local = ipaddress.ip_address(parsed.hostname).is_loopback
        except ValueError:
            pass
    if not endpoint:
        return []
    if parsed.scheme not in {"http", "https"} or not local or parsed.username or parsed.password or parsed.query or parsed.fragment or any(character.isspace() for character in endpoint):
        return ["NAV_LLM_BASE_URL must be a local-loopback HTTP(S) endpoint without embedded credentials or query parameters; remote navigation is forbidden."]
    return []


def host_errors(records, environ):
    errors = []
    if not shutil.which("docker"):
        return ["Docker CLI is not installed."]
    for command in (["docker", "info", "--format", "{{.ServerVersion}}"], ["docker", "compose", "version", "--short"]):
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode:
                errors.append("Host command failed: " + " ".join(command))
            elif command[1] == "compose":
                match = re.search(r"(\d+)\.(\d+)\.(\d+)", result.stdout)
                if not match or tuple(map(int, match.groups())) < (2, 27, 0):
                    errors.append("Use Docker Compose 2.27.0 or newer.")
        except (OSError, subprocess.TimeoutExpired):
            errors.append("Host command unavailable or timed out: " + " ".join(command))
    if any(item["number"] in GPU_TASKS for item in records):
        gpu = environ.get("GPU_ID", "")
        if not re.fullmatch(r"(?:\d+|GPU-[a-fA-F0-9-]+|MIG-[a-zA-Z0-9/-]+)", gpu):
            errors.append("Set GPU_ID explicitly to an available GPU index or UUID.")
        if not shutil.which("nvidia-smi"):
            errors.append("nvidia-smi is required for GPU tasks.")
        elif gpu:
            probe = subprocess.run(["nvidia-smi", "-i", gpu, "--query-gpu=uuid", "--format=csv,noheader"], capture_output=True, text=True, timeout=30)
            if probe.returncode:
                errors.append("The selected GPU is not accessible to nvidia-smi.")
            else:
                processes = subprocess.run(
                    ["nvidia-smi", "-i", gpu, "--query-compute-apps=pid", "--format=csv,noheader"],
                    capture_output=True, text=True, timeout=30)
                if processes.returncode or processes.stdout.strip():
                    errors.append("The selected GPU is busy or its compute-process status could not be checked.")
    errors.extend(runtime_environment_errors(records, environ))
    return errors


def gpu_overlay_text(gpu):
    return ("services:\n  main:\n    deploy:\n      resources:\n        reservations:\n          devices: !override\n"
            "            - driver: nvidia\n              device_ids: [" + json.dumps(gpu) + "]\n              capabilities: [gpu]\n")


def build_network_overlay(environ=None):
    environ = os.environ if environ is None else environ
    mode = environ.get("PBX_BUILD_PROXY_MODE") or "docker"
    if mode not in {"docker", "env", "direct"}:
        raise ValueError("PBX_BUILD_PROXY_MODE must be docker, env or direct.")
    build = {}
    network = environ.get("PBX_BUILD_NETWORK")
    if network:
        if network not in {"host", "default", "none"}:
            raise ValueError("PBX_BUILD_NETWORK must be host, default or none.")
        build["network"] = network
    if mode != "docker":
        selected = {}
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"):
            selected[name] = next((key for key in ("PBX_BUILD_" + name, name, name.lower()) if key in environ), None)
        if mode == "env":
            if selected["HTTP_PROXY"] is None:
                selected["HTTP_PROXY"] = selected["ALL_PROXY"]
            if selected["HTTPS_PROXY"] is None:
                selected["HTTPS_PROXY"] = selected["HTTP_PROXY"]
        arguments = {}
        for name, source in selected.items():
            value = ""
            if mode == "direct":
                value = "*" if name == "NO_PROXY" else ""
            elif source is not None:
                endpoint = environ[source]
                if name != "NO_PROXY" and endpoint:
                    try:
                        parsed = urlparse(endpoint)
                        valid = (parsed.scheme in {"http", "https"} and parsed.hostname
                                 and parsed.path in {"", "/"} and not parsed.query and not parsed.fragment)
                        if parsed.port is not None and parsed.port < 1:
                            valid = False
                    except ValueError:
                        valid = False
                    if not valid:
                        raise ValueError(source + " must be an HTTP(S) proxy URL. For a SOCKS-only service, use its HTTP/mixed port or an HTTP-to-SOCKS bridge; the build tools do not uniformly support raw SOCKS.")
                value = "${" + source + "}"
            arguments[name] = value
            arguments[name.lower()] = value
        build["args"] = arguments
    return {"services": {"main": {"build": build}}} if build else None


def write_config(config, path, gpu=None, environ=None):
    path = path.resolve()
    if path.exists():
        raise ValueError("Refusing to overwrite an existing run config: " + str(path))
    network = build_network_overlay(environ)
    path.parent.mkdir(parents=True, exist_ok=True)
    overlays = list(config["environment"].get("extra_docker_compose", []))
    if gpu is not None:
        overlay = path.with_suffix(".gpu.yaml")
        with overlay.open("x") as handle:
            handle.write(gpu_overlay_text(gpu))
        overlay.chmod(0o600)
        overlays.append(str(overlay))
    if network is not None:
        overlay = path.with_suffix(".network.yaml")
        with overlay.open("x") as handle:
            yaml.safe_dump(network, handle, sort_keys=False)
        overlay.chmod(0o600)
        overlays.append(str(overlay))
    if overlays:
        config["environment"]["extra_docker_compose"] = overlays
    with path.open("x") as handle:
        yaml.safe_dump(config, handle, sort_keys=False)
    path.chmod(0o600)
    return path


def launch(config_path, *, yes=False):
    environ = os.environ.copy()
    environ.pop("CLAUDE_CODE_MAX_TURNS", None)
    environ["PYTHONPATH"] = str(ROOT) + os.pathsep + environ.get("PYTHONPATH", "")
    environ["PYTHONDONTWRITEBYTECODE"] = "1"
    environ["NETWORK_MODE"] = "bridge"
    command = [sys.executable, "-B", "-m", "harbor.cli.main", "run", "-c", str(config_path)]
    if yes:
        command.append("--yes")
    return subprocess.run(command, cwd=ROOT, env=environ).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List tasks and their configured local budgets.")
    summary_parser = commands.add_parser("summary", help="Summarize a job without zero-filling missing scores.")
    summary_parser.add_argument("job", type=Path)
    for command in ("check", "config", "build", "run"):
        sub = commands.add_parser(command)
        sub.add_argument("--task", nargs="+", required=command != "check", default=["all"])
        sub.add_argument("--env-file", type=Path, default=ROOT / ".env" if (ROOT / ".env").is_file() else None)
        if command == "check":
            sub.add_argument("--host", action="store_true")
        elif command == "build":
            sub.add_argument("--output", type=Path, help="New private build-log directory.")
        else:
            sub.add_argument("--agent", choices=("claude-code", "codex", "oracle"))
            sub.add_argument("--model")
            sub.add_argument("--concurrency", type=int, default=1)
            sub.add_argument("--attempts", type=int, default=1)
            sub.add_argument("--retries", type=int, default=0)
            sub.add_argument("--job-name")
            sub.add_argument("--output", type=Path)
            if command == "run":
                sub.add_argument("-y", "--yes", action="store_true", help="Explicitly approve Harbor prompts for unattended execution.")
    args = parser.parse_args()
    try:
        if args.command == "summary":
            if not args.job.is_dir():
                raise ValueError("Job directory does not exist.")
            print(json.dumps(summarize(args.job), indent=2, ensure_ascii=False))
            return 0
        if args.command == "list":
            for item in catalog():
                config = item["config"]
                environment = config["environment"]
                status = ' [CANDIDATE; scored Harbor runs blocked]' if release_errors([item]) else ''
                print(f'{item["number"]}  {item["name"]}: {environment["cpus"]} CPU, {environment["memory_mb"] // 1024} GiB RAM, '
                      f'agent {config["agent"]["timeout_sec"] / 3600:g} h, verifier {config["verifier"]["timeout_sec"] / 3600:g} h{status}')
            return 0
        load_environment(args.env_file)
        build_network_overlay()
        records = select_tasks(args.task)
        if args.command in ('run', 'config') and release_errors(records):
            raise ValueError('\n'.join(release_errors(records)))
        errors = [error for item in records for error in audit_task(item['path'])]
        if errors:
            raise ValueError("\n".join(errors))
        print(check_runner())
        if args.command == "build":
            errors = host_errors([], os.environ) + runtime_environment_errors(records, os.environ)
            if errors:
                raise ValueError("\n".join(errors))
            output = args.output or ROOT / "runs" / ("build_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
            build_images(records, output, os.environ, build_network_overlay())
            return 0
        if args.command == "check":
            for item in records:
                check_environment = dict(os.environ, JUDGE_TRANSPORT="anthropic") if item["number"] == "12" else os.environ
                validate_config(build_config([item], environ=check_environment))
            errors = (host_errors(records, os.environ) + navigation_environment_errors(records, os.environ)
                      if args.host else [])
            if errors:
                raise ValueError("\n".join(errors))
            print(f"PASS: {len(records)} task structure and Harbor dataset/schema checks.")
            print("No image build, license checkout, model request, native solve or full-score claim.")
            for message in release_errors(records):
                print('RELEASE BLOCK: ' + message)
            return 0
        config = build_config(records, args.agent, args.model, args.concurrency, args.attempts, args.retries, args.job_name)
        validate_config(config)
        if args.command == "run":
            errors = required_environment_errors(config, os.environ) + host_errors(records, os.environ) + navigation_environment_errors(records, os.environ)
            if errors:
                raise ValueError("\n".join(errors))
        gpu = None
        if any(item["number"] in GPU_TASKS for item in records):
            gpu = os.environ.get("GPU_ID") or "${GPU_ID:?Set GPU_ID explicitly}"
        output = args.output or ROOT / "runs" / (config["job_name"] + ".yaml")
        path = write_config(config, output, gpu)
        print("Config: " + str(path))
        if args.command == "config":
            print("Configuration only; API keys remain environment references. No job started.")
            return 0
        print("Starting the requested task(s); this consumes model API calls and host compute.", flush=True)
        status = launch(path, yes=args.yes)
        summary = summarize(Path(config['jobs_dir']) / config['job_name'])
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return status
    except (ValueError, OSError, ImportError, subprocess.SubprocessError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
