FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps: git (worktrees, branches), curl (healthcheck), jq (agent bash),
# openssh-client (optional SSH git), gh CLI (draft PRs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl openssh-client jq && \
    # Install GitHub CLI
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y --no-install-recommends gh && \
    rm -rf /var/lib/apt/lists/*

# Git config (agents need this for commits)
RUN git config --global user.name "SWE Agent" && \
    git config --global user.email "swe-agent@agentfield.ai"

# Install uv for fast package installation
RUN pip install --no-cache-dir uv

# Install project dependencies
COPY requirements-docker.txt /app/requirements.txt
RUN uv pip install --system -r /app/requirements.txt

# Copy application code
COPY . /app/

EXPOSE 8003

ENV PORT=8003 \
    AGENTFIELD_SERVER=http://control-plane:8080 \
    NODE_ID=swe-planner

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["python", "-m", "swe_af"]
