ARG MAPGPT_BASE_IMAGE
FROM ${MAPGPT_BASE_IMAGE}

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

WORKDIR /home
ENV PYTHONDONTWRITEBYTECODE=1

RUN test "$PBX_DOWNLOAD_TIMEOUT" -gt 0 && test "$PBX_DOWNLOAD_RETRIES" -gt 0 && \
    apt-get -o Acquire::Retries="$PBX_DOWNLOAD_RETRIES" -o Acquire::http::Timeout="$PBX_DOWNLOAD_TIMEOUT" update && \
    apt-get install -y --no-install-recommends curl ca-certificates ripgrep procps acl iptables util-linux python3-pip gcc g++ && \
    curl --connect-timeout "$PBX_DOWNLOAD_TIMEOUT" --max-time 180 --retry "$PBX_DOWNLOAD_RETRIES" -fsSL https://deb.nodesource.com/setup_20.x -o /tmp/pbx-node-setup.sh && \
    bash /tmp/pbx-node-setup.sh && rm /tmp/pbx-node-setup.sh && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g @anthropic-ai/claude-code@2.1.232 @openai/codex@0.153.4 && \
    rm -rf /var/lib/apt/lists/*

RUN test -r /home/data/R2R/annotations/MapGPT_72_scenes_processed.json && \
    test -d /home/data/connectivity && \
    test -n "$(find /home/data/RGB_Observations -type f -name '*.jpg' -print -quit)" && \
    test -r /home/models/Qwen2.5-VL-7B-Instruct/config.json && \
    python3 -c "import vllm"

COPY requirements-evaluator.txt /tmp/pbx-requirements-evaluator.txt
RUN python3 -m pip install --no-cache-dir --target /opt/pbx-verifier-site -r /tmp/pbx-requirements-evaluator.txt && \
    rm /tmp/pbx-requirements-evaluator.txt

RUN id pbsolver >/dev/null 2>&1 || useradd --create-home --shell /bin/bash pbsolver
RUN mkdir -p /home/paper/paper_image /home/submission /home/starter_submission

COPY paper/paper.md /home/paper/paper.md
COPY paper/paper.pdf /home/paper/paper.pdf
COPY paper/paper_image/ /home/paper/paper_image/
COPY paper/addendum.md /home/paper/addendum.md
COPY paper/blacklist.txt /home/paper/blacklist.txt
COPY starter_submission/ /home/starter_submission/
COPY init-workspace.sh /usr/local/bin/pbx-init-workspace

COPY serve_nav_vllm.sh /usr/local/bin/serve_nav_vllm.sh
RUN chmod 0755 /usr/local/bin/serve_nav_vllm.sh && test -r /usr/local/bin/serve_nav_vllm.sh

RUN chmod -R a+rX /home/paper /home/starter_submission /home/data /home/models/Qwen2.5-VL-7B-Instruct && \
    chmod -R a-w /home/data /home/models/Qwen2.5-VL-7B-Instruct && \
    chmod 0755 /home/starter_submission/reproduce.sh /usr/local/bin/pbx-init-workspace
