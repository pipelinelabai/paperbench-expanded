ARG HFSS_BASE_IMAGE
FROM python:3.11-slim AS derive_runtime

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG PBX_DOWNLOAD_TIMEOUT=30
ARG PBX_DOWNLOAD_RETRIES=5
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_DEFAULT_TIMEOUT=${PBX_DOWNLOAD_TIMEOUT}
ARG PIP_RETRIES=${PBX_DOWNLOAD_RETRIES}
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
RUN test "$PBX_DOWNLOAD_TIMEOUT" -gt 0 && test "$PBX_DOWNLOAD_RETRIES" -gt 0
RUN python -m pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3

FROM ${HFSS_BASE_IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG PBX_DOWNLOAD_TIMEOUT=30
ARG PBX_DOWNLOAD_RETRIES=5
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_DEFAULT_TIMEOUT=${PBX_DOWNLOAD_TIMEOUT}
ARG PIP_RETRIES=${PBX_DOWNLOAD_RETRIES}
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG npm_config_registry=https://registry.npmjs.org
ARG npm_config_fetch_timeout=60000
ARG npm_config_fetch_retries=${PBX_DOWNLOAD_RETRIES}

RUN test "$PBX_DOWNLOAD_TIMEOUT" -gt 0 && \
    test "$PBX_DOWNLOAD_RETRIES" -gt 0 && \
    printf '\ntimeout=%s\nretries=%s\nminrate=1024\n' "$PBX_DOWNLOAD_TIMEOUT" "$PBX_DOWNLOAD_RETRIES" >> /etc/dnf/dnf.conf

WORKDIR /home

ENV ANSYS_PYTHON=/ansys_inc/v251/AnsysEM/commonfiles/CPython/3_10/linx64/Release/python/bin/python3.10 \
    PYAEDT_USE_PRE_GRPC_ARGS=True \
    PYAEDT_LOCAL_SETTINGS_PATH=/opt/hfss-verifier-runtime-v1/pyaedt_settings.yaml \
    PYTHONDONTWRITEBYTECODE=1
RUN dnf install -y curl ca-certificates python3-pip procps-ng shadow-utils util-linux libseccomp && \
    "$ANSYS_PYTHON" -m pip install --no-cache-dir pyaedt==1.4.0 'protobuf>=4.25.8,<5' && \
    mkdir -p /opt/hfss-verifier-runtime-v1 && \
    printf '%s\n' 'grpc:' '  grpc_secure_mode: false' '  grpc_listen_all: false' 'general:' '  desktop_launch_timeout: 180' > /opt/hfss-verifier-runtime-v1/pyaedt_settings.yaml && \
    printf '%s\n' 'import os, sys' 'os.environ["PYAEDT_USE_PRE_GRPC_ARGS"] = "True"' 'os.environ["PYAEDT_LOCAL_SETTINGS_PATH"] = "/opt/hfss-verifier-runtime-v1/pyaedt_settings.yaml"' 'os.environ["PYTHONDONTWRITEBYTECODE"] = "1"' 'sys.dont_write_bytecode = True' > "$($ANSYS_PYTHON -c 'import site; print(site.getsitepackages()[0])')/hfss_verifier_runtime_v1_bootstrap.py" && \
    printf '%s\n' 'import hfss_verifier_runtime_v1_bootstrap' > "$($ANSYS_PYTHON -c 'import site; print(site.getsitepackages()[0])')/hfss_verifier_runtime_v1.pth" && \
    "$ANSYS_PYTHON" -m pip install --no-cache-dir 'openai>=1.40,<2' 'httpx>=0.27' && \
    ln -sf "$ANSYS_PYTHON" /usr/local/bin/python3 && \
    ln -sf "$ANSYS_PYTHON" /usr/local/bin/python && \
    curl --connect-timeout "$PBX_DOWNLOAD_TIMEOUT" --max-time 180 --retry "$PBX_DOWNLOAD_RETRIES" --retry-delay 2 --retry-max-time 300 -fsSL https://rpm.nodesource.com/setup_20.x -o /tmp/pbx-node-setup.sh && bash /tmp/pbx-node-setup.sh && rm -f /tmp/pbx-node-setup.sh && \
    dnf install -y nodejs && \
    curl --connect-timeout "$PBX_DOWNLOAD_TIMEOUT" --max-time 180 --retry "$PBX_DOWNLOAD_RETRIES" --retry-delay 2 --retry-max-time 300 -fsSL https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz | tar -xz -C /tmp && \
    install -m0755 /tmp/ripgrep-14.1.1-x86_64-unknown-linux-musl/rg /usr/local/bin/rg && \
    rm -rf /tmp/ripgrep-14.1.1-x86_64-unknown-linux-musl && \
    npm install -g @anthropic-ai/claude-code@2.1.232 @openai/codex@0.148.0 && \
    dnf clean all

RUN "$ANSYS_PYTHON" -m pip install --no-cache-dir --force-reinstall --no-deps scipy==1.15.3 && \
    "$ANSYS_PYTHON" -c "from scipy.signal import find_peaks; from scipy.optimize import minimize; assert list(find_peaks([0, 1, 0])[0]) == [1]"

RUN useradd --create-home --shell /bin/bash pbsolver && \
    useradd --create-home --shell /bin/bash pbverifier && \
    mkdir -p /home/paper/paper_image /home/submission /home/starter_submission

# Copy only candidate-visible task materials. Evaluator policy and rubric files
# remain under /tests and are never exposed through /home/paper.
COPY paper/paper.md /home/paper/paper.md
COPY paper/paper.pdf /home/paper/paper.pdf
COPY paper/paper_image/ /home/paper/paper_image/
COPY paper/addendum.md /home/paper/addendum.md
COPY paper/tools/ /home/paper/tools/
COPY paper/blacklist.md /home/paper/blacklist.md
COPY --from=derive_runtime / /opt/pbx-derive-root/
COPY starter_submission/ /home/starter_submission/

RUN chmod 0755 /home/starter_submission/reproduce.sh && \
    chmod -R a+rX /home/paper /home/starter_submission && \
    chmod 0777 /home/submission

RUN chmod 0755 /home/paper/tools/check_submission.py && \
    ln -sf /home/paper/tools/check_submission.py /usr/local/bin/pbx-submission-check

RUN rm -f /home/paper/numerical_policy.json
RUN rm -f /home/paper/config.yaml \
    /home/paper/paper_alignment.md \
    /home/paper/reproduction.md \
    /home/paper/setup.md \
    /home/paper/artifact_io.py \
    /home/paper/check_submission.py \
    /home/paper/submission_contract.json

COPY init-workspace.sh /usr/local/bin/pbx-init-workspace
RUN chmod 0755 /usr/local/bin/pbx-init-workspace
