FROM node:18-alpine3.18 AS web-build
COPY ui ui
RUN cd ui && \
    npm install && \
    NODE_OPTIONS="--max-old-space-size=4096" npm run build && \
    NODE_OPTIONS="--max-old-space-size=4096" npm run build-chat && \
    find . -maxdepth 1 ! -name '.' ! -name 'dist' ! -name 'public' -exec rm -rf {} +

FROM ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.5 AS stage-build

ARG DEPENDENCIES="                    \
        python3-pip"

RUN apt-get update && \
    apt-get install -y --no-install-recommends $DEPENDENCIES && \
    apt-get clean all  && \
    rm -rf /var/lib/apt/lists/*

COPY --chmod=700 . /opt/maxkb-app

WORKDIR /opt/maxkb-app
RUN rm -rf /opt/maxkb-app/ui && \
    python3 -m venv /opt/py3 && \
    pip install poetry==2.0.0 --break-system-packages && \
    poetry config virtualenvs.create false && \
    . /opt/py3/bin/activate && \
    if [ "$(uname -m)" = "x86_64" ]; then sed -i 's/^torch.*/torch = {version = "2.7.1+cpu", source = "pytorch"}/g' pyproject.toml; fi && \
    poetry install && \
    find /opt/maxkb-app  -depth \( -name ".git*" -o -name ".docker*" -o -name ".idea*" -o -name ".editorconfig*" -o -name ".prettierrc*" -o -name "README.md" -o -name "poetry.lock" -o -name "pyproject.toml"  \) -exec rm -rf {} + && \
    export MAXKB_CONFIG_TYPE=ENV && python3 /opt/maxkb-app/apps/manage.py compilemessages && \
    export PIP_TARGET=/opt/maxkb-app/sandbox/python-packages && \
    pip install requests pymysql psycopg2-binary && \
    rm -rf /opt/maxkb-app/installer
COPY --from=web-build --chmod=700 ui /opt/maxkb-app/ui

FROM ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.5
ARG DOCKER_IMAGE_TAG=dev \
    BUILD_AT \
    GITHUB_COMMIT

ENV MAXKB_VERSION="${DOCKER_IMAGE_TAG} (build at ${BUILD_AT}, commit: ${GITHUB_COMMIT})" \
    MAXKB_CONFIG_TYPE=ENV \
    MAXKB_DB_NAME=maxkb \
    MAXKB_DB_HOST=127.0.0.1 \
    MAXKB_DB_PORT=5432  \
    MAXKB_DB_USER=${POSTGRES_USER} \
    MAXKB_DB_PASSWORD=${POSTGRES_PASSWORD} \
    MAXKB_DB_MAX_OVERFLOW=80 \
    MAXKB_REDIS_HOST=127.0.0.1 \
    MAXKB_REDIS_PORT=6379 \
    MAXKB_REDIS_DB=0 \
    MAXKB_REDIS_PASSWORD=${REDIS_PASSWORD} \
    MAXKB_EMBEDDING_MODEL_PATH=/opt/maxkb-app/model/embedding \
    MAXKB_EMBEDDING_MODEL_NAME=/opt/maxkb-app/model/embedding/shibing624_text2vec-base-chinese \
    MAXKB_LOCAL_MODEL_HOST=127.0.0.1 \
    MAXKB_LOCAL_MODEL_PORT=11636 \
    MAXKB_LOCAL_MODEL_PROTOCOL=http \
    MAXKB_SANDBOX=1 \
    PATH=/opt/py3/bin:$PATH \
    PIP_TARGET=/opt/maxkb/python-packages \
    PYTHONUNBUFFERED=1

WORKDIR /opt/maxkb-app
COPY --from=stage-build /opt/maxkb-app /opt/maxkb-app
COPY --from=stage-build /opt/py3 /opt/py3

RUN chmod 755 /tmp

EXPOSE 8080
VOLUME /opt/maxkb
ENTRYPOINT ["bash", "-c"]
CMD [ "/usr/bin/start-all.sh" ]