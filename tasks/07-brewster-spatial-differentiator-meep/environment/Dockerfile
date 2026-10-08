FROM ubuntu:22.04

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

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-meep \
    python3-h5py \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    libhdf5-serial-dev \
    libmeep23 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir "numpy<1.25" pandas autograd

WORKDIR /home

RUN apt-get update -qq && \
    apt-get install -y -qq curl ca-certificates python3-numpy python3-h5py python3-matplotlib && \
    curl --connect-timeout "$PBX_DOWNLOAD_TIMEOUT" --max-time 180 --retry "$PBX_DOWNLOAD_RETRIES" --retry-delay 2 --retry-max-time 300 -fsSL https://deb.nodesource.com/setup_20.x -o /tmp/pbx-node-setup.sh && bash /tmp/pbx-node-setup.sh && rm -f /tmp/pbx-node-setup.sh && \
    apt-get install -y -qq nodejs ripgrep && \
    npm install -g @anthropic-ai/claude-code@2.1.232 @openai/codex@0.148.0 && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash pbsolver && \
    useradd --create-home --shell /bin/bash pbverifier

RUN mkdir -p /home/paper/paper_image /home/submission

COPY paper/paper.md /home/paper/paper.md
COPY paper/paper.pdf /home/paper/paper.pdf
COPY paper/paper_image/ /home/paper/paper_image/
COPY paper/addendum.md /home/paper/addendum.md
COPY paper/blacklist.md /home/paper/blacklist.md
COPY starter_submission/ /home/starter_submission/

RUN apt-get update && apt-get install -y --no-install-recommends iptables strace util-linux procps && rm -rf /var/lib/apt/lists/*


RUN chown -R pbsolver:pbsolver /home/submission && chmod 0755 /home/paper
RUN rm -f /home/paper/config.yaml \
    /home/paper/paper_scope.json \
    /home/paper/reproduction.md

COPY init-workspace.sh /usr/local/bin/pbx-init-workspace
RUN chmod 0755 /usr/local/bin/pbx-init-workspace
