FROM nvidia/cuda:12.4.1-devel-ubuntu22.04@sha256:da6791294b0b04d7e65d87b7451d6f2390b4d36225ab0701ee7dfec5769829f5

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

RUN test "$PBX_DOWNLOAD_TIMEOUT" -gt 0 && \
    test "$PBX_DOWNLOAD_RETRIES" -gt 0 && \
    printf 'Acquire::http::Timeout "%s";\nAcquire::https::Timeout "%s";\nAcquire::Retries "%s";\nAPT::Update::Error-Mode "any";\n' "$PBX_DOWNLOAD_TIMEOUT" "$PBX_DOWNLOAD_TIMEOUT" "$PBX_DOWNLOAD_RETRIES" > /etc/apt/apt.conf.d/80pbx-network && \
    if [ -n "$PBX_APT_MIRROR" ]; then \
      case "$PBX_APT_MIRROR" in *[!a-zA-Z0-9.:-]*) printf '%s\n' 'PBX_APT_MIRROR must be a hostname, optionally with a port' >&2; exit 1 ;; esac; \
      for source_file in /etc/apt/sources.list /etc/apt/sources.list.d/*.list /etc/apt/sources.list.d/*.sources; do \
        if [ -f "$source_file" ]; then \
          sed -E -i "s#(https?://)(deb\.debian\.org|security\.debian\.org|([a-z]{2}\.)?archive\.ubuntu\.com|security\.ubuntu\.com|ports\.ubuntu\.com)/#\1${PBX_APT_MIRROR}/#g" "$source_file"; \
        fi; \
      done; \
    fi

WORKDIR /home
ENV DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /tmp/pbx-requirements.txt

RUN apt-get update -qq && \
    apt-get install -y -qq python3 python3-pip git curl ca-certificates ripgrep && \
    pip3 install --no-cache-dir -r /tmp/pbx-requirements.txt && \
    pip3 check && \
    rm -rf /var/lib/apt/lists/* /tmp/pbx-requirements.txt

RUN printf '#!/bin/sh\nexit 0\n' > /usr/local/bin/apk && chmod +x /usr/local/bin/apk

RUN apt-get update -qq && \
    apt-get install -y -qq curl ca-certificates procps util-linux coreutils strace iptables && \
    curl --connect-timeout "$PBX_DOWNLOAD_TIMEOUT" --max-time 180 --retry "$PBX_DOWNLOAD_RETRIES" --retry-delay 2 --retry-max-time 300 -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/pbx-node-setup.sh && bash /tmp/pbx-node-setup.sh && rm -f /tmp/pbx-node-setup.sh && \
    apt-get install -y -qq nodejs && \
    npm install -g @anthropic-ai/claude-code@2.1.232 @openai/codex@0.148.0 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/paper/data /home/submission /home/starter_submission /logs/verifier

RUN id pbsolver >/dev/null 2>&1 || useradd --create-home --shell /bin/bash pbsolver; \
    id pbverifier >/dev/null 2>&1 || useradd --create-home --shell /bin/bash pbverifier; \
    chown -R pbsolver:pbsolver /home/pbsolver /home/submission && \
    chown -R pbverifier:pbverifier /home/pbverifier /logs/verifier

RUN npm config set prefix /home/pbsolver/.local --global && \
    mkdir -p /home/pbsolver/.local/bin /home/pbsolver/.local/lib/node_modules && \
    chown -R pbsolver:pbsolver /home/pbsolver/.local


COPY paper/paper.md /home/paper/paper.md
COPY paper/paper.pdf /home/paper/paper.pdf
COPY paper/addendum.md /home/paper/addendum.md
COPY paper/blacklist.md /home/paper/blacklist.md
COPY paper/data/ /home/paper/data/
COPY paper/paper_image/ /home/paper/paper_image/

COPY starter_submission/ /home/starter_submission/

WORKDIR /home/submission

COPY pbx_engineering.py /usr/local/bin/pbx-submission-check
RUN chmod 0755 /usr/local/bin/pbx-submission-check
RUN rm -f /home/paper/config.yaml \
    /home/paper/reproduction.md

COPY init-workspace.sh /usr/local/bin/pbx-init-workspace
RUN chmod 0755 /usr/local/bin/pbx-init-workspace

COPY starter_submission/inputs/ /home/paper/inputs/
RUN chmod -R a-w /home/paper/inputs
COPY paper/model_manifest.json /home/paper/model_manifest.json
