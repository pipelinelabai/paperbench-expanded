FROM ubuntu:22.04@sha256:3b06811b2afd352be909dd088a004166d665dc76d38b13eada33522a9d915c6f

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

RUN set -eux; apt-get update -qq; \
    apt-get install -y -qq --no-install-recommends \
      quantum-espresso openmpi-bin libopenmpi3 \
      python3 python3-pip \
      curl ca-certificates iptables strace procps util-linux coreutils \
      bash gawk sed grep findutils tar gzip xz-utils file; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/pbx-requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/pbx-requirements.txt && \
    rm /tmp/pbx-requirements.txt

RUN set -eux; \
    curl --connect-timeout "$PBX_DOWNLOAD_TIMEOUT" --max-time 180 --retry "$PBX_DOWNLOAD_RETRIES" --retry-delay 2 --retry-max-time 300 -fsSL https://deb.nodesource.com/setup_20.x -o /tmp/pbx-node-setup.sh && bash /tmp/pbx-node-setup.sh && rm -f /tmp/pbx-node-setup.sh; \
    apt-get install -y -qq nodejs ripgrep; \
    npm install -g @anthropic-ai/claude-code@2.1.232 @openai/codex@0.153.4; \
    rm -rf /var/lib/apt/lists/*

# --- v2 clean-replay shims -------------------------------------------------
# The verifier replays reproduce.sh as pbsolver under `env -i`, so OMP_NUM_THREADS
# is unset. Left unset, each MPI rank opens one OpenMP thread per host core and
# thrashes the 8-CPU container quota. /usr/local/bin precedes /usr/bin on the
# sanitized replay PATH, so these shims pin threads for every native invocation.
RUN set -eux; mkdir -p /opt/pbx; \
    { \
      echo 'OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"'; \
      echo 'MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"'; \
      echo 'OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"'; \
      echo 'export OMP_NUM_THREADS MKL_NUM_THREADS OPENBLAS_NUM_THREADS'; \
    } > /opt/pbx/qe_env.sh; \
    chmod 0644 /opt/pbx/qe_env.sh; \
    for b in pw.x bands.x dos.x projwfc.x pp.x average.x ph.x ev.x; do \
      printf '#!/bin/sh\n. /opt/pbx/qe_env.sh\nexec /usr/bin/%s "$@"\n' "$b" > "/usr/local/bin/$b"; \
      chmod 0755 "/usr/local/bin/$b"; \
    done; \
    printf '#!/bin/sh\n. /opt/pbx/qe_env.sh\nexec /usr/bin/mpirun "$@"\n' > /usr/local/bin/mpirun; \
    printf '#!/bin/sh\n. /opt/pbx/qe_env.sh\nexec /usr/bin/mpiexec "$@"\n' > /usr/local/bin/mpiexec; \
    chmod 0755 /usr/local/bin/mpirun /usr/local/bin/mpiexec

# Fail the build rather than ship an image whose shims do not work.
RUN set -eux; \
    env -i PATH=/usr/local/bin:/usr/bin:/bin sh -c '\
      for b in pw.x bands.x dos.x projwfc.x pp.x average.x mpirun mpiexec python3; do \
        command -v "$b" >/dev/null || { echo "shim missing: $b" >&2; exit 1; }; \
      done; \
      python3 -c "import numpy, scipy, matplotlib" || exit 1; \
      echo "shim self-check OK"'

# --- pseudopotential provisioning --------------------------------------------
# Baked into the image: the scored replay runs with no network, so the solver
# cannot download UPFs at run time. Path is stable and documented in the addendum.
COPY starter_submission/inputs/pseudo/ /opt/pseudo/
RUN set -eux; chmod -R a+rX /opt/pseudo; \
    for f in /opt/pseudo/*.UPF; do \
      head -c 400 "$f" | grep -q '<UPF version=' || { echo "not a UPF: $f" >&2; exit 1; }; \
    done; \
    ls -1 /opt/pseudo
ENV ESPRESSO_PSEUDO=/opt/pseudo

WORKDIR /home

RUN useradd --create-home --shell /bin/bash pbsolver && \
    useradd --create-home --shell /bin/bash pbverifier && \
    mkdir -p /home/paper/paper_image /home/submission /home/pbsolver/.local/bin /home/pbsolver/.local/lib/node_modules && \
    chown -R pbsolver:pbsolver /home/pbsolver && \
    chown -R pbverifier:pbverifier /home/pbverifier

# Copy paper materials. paper_scope.json is deliberately NOT copied: it carries
# the rubric leaf mapping and must stay out of the solver's image.
COPY paper/paper.md /home/paper/paper.md
COPY paper/paper.pdf /home/paper/paper.pdf
COPY paper/paper_image/ /home/paper/paper_image/
COPY paper/addendum.md /home/paper/addendum.md
COPY starter_submission/ /home/starter_submission/

COPY pbx_engineering.py /usr/local/bin/pbx-submission-check
RUN chmod 0755 /usr/local/bin/pbx-submission-check

RUN rm -f /home/paper/acceptance.json
RUN rm -f /home/paper/acceptance.md \
    /home/paper/config.yaml \
    /home/paper/reproduction.md

COPY init-workspace.sh /usr/local/bin/pbx-init-workspace
RUN chmod 0755 /usr/local/bin/pbx-init-workspace

COPY starter_submission/inputs/ /home/paper/inputs/
RUN chmod -R a-w /home/paper/inputs
