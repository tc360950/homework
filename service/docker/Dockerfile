ARG SERVICE

FROM python:3.10-slim as dependencies
ARG SERVICE=service

WORKDIR /data
RUN pip install --no-cache-dir poetry==2.1.3
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY ${SERVICE}/pyproject.toml ${SERVICE}/poetry.lock ./
RUN touch README.md && poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.10-slim as prod
ARG USERNAME=service
ARG USER_UID=1000
ARG USER_GID=1000
ARG SERVICE=service
ARG WORKSPACE=/app

RUN groupadd --gid $USER_GID $USERNAME &&  \
  useradd -s /bin/bash --uid $USER_UID --gid $USERNAME -m $USERNAME  -d /home/${USERNAME} && \
  chown -R ${USERNAME} /home/${USERNAME}

RUN mkdir ${WORKSPACE} && chown -R ${USERNAME} ${WORKSPACE}

COPY --chown=${USERNAME} --from=dependencies /data/.venv /home/${USERNAME}/.local

USER ${USERNAME}
WORKDIR ${WORKSPACE}
COPY --chown=${USERNAME} ${SERVICE} ${WORKSPACE}
RUN chmod +x scripts/entrypoint.sh
RUN pip install  --no-cache-dir .

CMD ["./scripts/entrypoint.sh"]