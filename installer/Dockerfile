FROM node:24-alpine AS web-build
COPY ui ui
RUN cd ui && ls -la && if [ -d "dist" ]; then exit 0; fi && \
    npm install --prefer-offline --no-audit && \
    npm install -D concurrently && \
    NODE_OPTIONS="--max-old-space-size=4096" npx concurrently "npm run build" "npm run build-chat" && \
    find . -maxdepth 1 ! -name '.' ! -name 'dist' ! -name 'public' -exec rm -rf {} +

FROM ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.6 AS deps-build
COPY --chmod=700 . /opt/maxkb-app
WORKDIR /opt/maxkb-app
RUN pip install uv --break-system-packages && \
    python -m uv pip install -r pyproject.toml && \
    python -m uv pip install --target=/opt/maxkb-app/sandbox/python-packages requests pymysql psycopg2-binary

FROM ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.6 AS apps-build
COPY --chmod=700 . /opt/maxkb-app
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext libexpat1-dev libffi-dev && \
    apt-get clean all  && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/maxkb-app
RUN rm -rf /opt/maxkb-app/ui && \
    grep -oE '"django==[^"]+"' pyproject.toml | sed 's/"//g' | xargs -n 1 pip install && python /opt/maxkb-app/apps/manage.py compilemessages && \
    find /opt/maxkb-app  -depth \( -name ".git*" -o -name ".docker*" -o -name ".idea*" -o -name ".editorconfig*" -o -name ".prettierrc*" -o -name "README.md" -o -name "poetry.lock" -o -name "pyproject.toml"  \) -exec rm -rf {} + && \
    rm -rf /opt/maxkb-app/installer
COPY --from=web-build --chmod=700 ui /opt/maxkb-app/ui
COPY --from=deps-build /opt/maxkb-app/sandbox/python-packages /opt/maxkb-app/sandbox/python-packages

FROM ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.6
ARG DOCKER_IMAGE_TAG=dev \
    BUILD_AT \
    GITHUB_COMMIT

ENV MAXKB_VERSION="${DOCKER_IMAGE_TAG} (build at ${BUILD_AT}, commit: ${GITHUB_COMMIT})" \
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
    PIP_TARGET=/opt/maxkb/python-packages


WORKDIR /opt/maxkb-app
COPY --from=apps-build /opt/maxkb-app /opt/maxkb-app
COPY --from=deps-build /opt/py3/lib/python3.11/site-packages /opt/py3/lib/python3.11/site-packages

RUN chmod 755 /tmp

EXPOSE 8080
VOLUME /opt/maxkb
ENTRYPOINT ["bash", "-c"]
CMD [ "/usr/bin/start-all.sh" ]