FROM python:3.11-slim-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG PBX_DOWNLOAD_TIMEOUT=30
ARG PBX_DOWNLOAD_RETRIES=5
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_DEFAULT_TIMEOUT=${PBX_DOWNLOAD_TIMEOUT}
ARG PIP_RETRIES=${PBX_DOWNLOAD_RETRIES}
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PBX_APT_MIRROR=
ARG npm_config_registry=https://registry.npmjs.org
ARG npm_config_fetch_timeout=60000
ARG npm_config_fetch_retries=${PBX_DOWNLOAD_RETRIES}

RUN test "$PBX_DOWNLOAD_TIMEOUT" -gt 0 && test "$PBX_DOWNLOAD_RETRIES" -gt 0 && \
    printf 'Acquire::http::Timeout "%s";\nAcquire::https::Timeout "%s";\nAcquire::Retries "%s";\nAPT::Update::Error-Mode "any";\n' "$PBX_DOWNLOAD_TIMEOUT" "$PBX_DOWNLOAD_TIMEOUT" "$PBX_DOWNLOAD_RETRIES" > /etc/apt/apt.conf.d/80pbx-network && \
    if [ -n "$PBX_APT_MIRROR" ]; then \
      case "$PBX_APT_MIRROR" in *[!a-zA-Z0-9.:-]*) exit 1 ;; esac; \
      sed -E -i "s#(https?://)(deb.debian.org|security.debian.org)/#\1${PBX_APT_MIRROR}/#g" /etc/apt/sources.list.d/debian.sources; \
    fi

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    bash ca-certificates curl git nodejs npm ripgrep iptables strace procps util-linux \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/pbx-requirements.txt
RUN pip install --no-cache-dir -r /tmp/pbx-requirements.txt && \
    rm /tmp/pbx-requirements.txt
RUN npm install -g @anthropic-ai/claude-code@2.1.232 @openai/codex@0.153.4
RUN useradd --create-home --shell /bin/bash pbsolver && \
    useradd --create-home --shell /usr/sbin/nologin pbverifier && \
    mkdir -p /home/submission

COPY paper/ /home/paper/
COPY starter_submission/inputs/ /home/data/
COPY starter_submission/ /home/starter_submission/
COPY init-workspace.sh /usr/local/bin/pbx-init-workspace
RUN chmod 0755 /usr/local/bin/pbx-init-workspace && \
    chmod -R a+rX,a-w /home/paper /home/data /home/starter_submission && \
    python -c 'import numpy, scipy, pandas, matplotlib, yaml' && \
    command -v strace && command -v iptables && command -v ip6tables

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /home/submission
