# syntax=docker/dockerfile:experimental

FROM python:3.9-slim AS base

# Install development tools: compilers, curl, git, ssh, starship, vim, and zsh.
RUN apt-get update && \
    apt-get install --no-install-recommends --yes build-essential curl git ssh vim zsh zsh-antigen && \
    chsh --shell /usr/bin/zsh && \
    sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- "--yes" && \
    echo 'source /usr/share/zsh-antigen/antigen.zsh' >> ~/.zshrc && \
    echo 'antigen bundle zsh-users/zsh-autosuggestions' >> ~/.zshrc && \
    echo 'antigen apply' >> ~/.zshrc && \
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc && \
    rm -rf /var/lib/apt/lists/*

# Configure Python to print tracebacks on crash [1], and to not buffer stdout and stderr [2].
# [1] https://docs.python.org/3/using/cmdline.html#envvar-PYTHONFAULTHANDLER
# [2] https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

# Install Poetry.
ENV POETRY_VERSION 1.1.13
ENV PATH /root/.local/bin/:$PATH
RUN --mount=type=cache,target=/root/.cache/ \
    curl -sSL https://install.python-poetry.org | python - --version $POETRY_VERSION && \
    poetry config virtualenvs.create false

# Enable Poetry to publish to PyPI [1].
# [1] https://pythonspeed.com/articles/build-secrets-docker-compose/
ARG PYPI_TOKEN
ENV PYPI_TOKEN $PYPI_TOKEN

# Let Poe the Poet know it doesn't need to activate the Python environment.
ENV POETRY_ACTIVE 1

# Set the working directory.
WORKDIR /app/

FROM base as dev

# Install the development Python environment.
COPY .pre-commit-config.yaml poetry.lock* pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/ \
    mkdir -p src/pulumi_gcp_pufferpanel/ && touch src/pulumi_gcp_pufferpanel/__init__.py && touch README.md && \
    poetry install --no-interaction && \
    mkdir -p /var/lib/poetry/ && cp poetry.lock /var/lib/poetry/ && \
    git init && pre-commit install --install-hooks && \
    mkdir -p /var/lib/git/ && cp .git/hooks/commit-msg .git/hooks/pre-commit /var/lib/git/

FROM base as ci

# Install the run time Python environment.
# TODO: Replace `--no-dev` with `--without test` when Poetry 1.2.0 is released.
COPY poetry.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/ \
    mkdir -p src/pulumi_gcp_pufferpanel/ && touch src/pulumi_gcp_pufferpanel/__init__.py && touch README.md && \
    poetry install --no-dev --no-interaction
