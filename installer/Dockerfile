FROM ghcr.io/1panel-dev/maxkb-vector-model:v1.0.1 as vector-model
FROM node:18-alpine3.18 as web-build
COPY ui ui
RUN cd ui && \
    npm install && \
    npm run build && \
    rm -rf ./node_modules
FROM ghcr.io/1panel-dev/maxkb-python-pg:python3.11-pg15.6 as stage-build

ARG DEPENDENCIES="                    \
        python3-pip"

RUN apt-get update && \
    apt-get install -y --no-install-recommends $DEPENDENCIES && \
    apt-get clean all  && \
    rm -rf /var/lib/apt/lists/*

COPY . /opt/maxkb/app
RUN mkdir -p /opt/maxkb/app /opt/maxkb/model /opt/maxkb/conf && \
    rm -rf /opt/maxkb/app/ui
COPY --from=web-build ui /opt/maxkb/app/ui
WORKDIR /opt/maxkb/app
RUN python3 -m venv /opt/py3 && \
    pip install poetry --break-system-packages && \
    poetry config virtualenvs.create false && \
    . /opt/py3/bin/activate && \
    if [ "$(uname -m)" = "x86_64" ]; then sed -i 's/^torch.*/torch = {version = "^2.2.1+cpu", source = "pytorch"}/g' pyproject.toml; fi && \
    poetry install

FROM ghcr.io/1panel-dev/maxkb-python-pg:python3.11-pg15.6
ARG DOCKER_IMAGE_TAG=dev \
    BUILD_AT \
    GITHUB_COMMIT

ENV MAXKB_VERSION="${DOCKER_IMAGE_TAG} (build at ${BUILD_AT}, commit: ${GITHUB_COMMIT})" \
    MAXKB_CONFIG_TYPE=ENV \
    MAXKB_DB_NAME=maxkb \
    MAXKB_DB_HOST=127.0.0.1 \
    MAXKB_DB_PORT=5432  \
    MAXKB_DB_USER=root \
    MAXKB_DB_PASSWORD=Password123@postgres \
    MAXKB_EMBEDDING_MODEL_NAME=/opt/maxkb/model/embedding/shibing624_text2vec-base-chinese \
    MAXKB_EMBEDDING_MODEL_PATH=/opt/maxkb/model/embedding

WORKDIR /opt/maxkb/app
COPY --from=stage-build /opt/maxkb /opt/maxkb
COPY --from=stage-build /opt/py3 /opt/py3
COPY --from=vector-model /opt/maxkb/app/model /opt/maxkb/model

ENV LANG=en_US.UTF-8 \
    PATH=/opt/py3/bin:$PATH

ENV POSTGRES_USER root
ENV POSTGRES_PASSWORD Password123@postgres

RUN chmod 755 /opt/maxkb/app/installer/run-maxkb.sh && \
    cp -r /opt/maxkb/model/base/hub /opt/maxkb/model/tokenizer && \
    cp -f /opt/maxkb/app/installer/run-maxkb.sh /usr/bin/run-maxkb.sh && \
    cp -f /opt/maxkb/app/installer/init.sql /docker-entrypoint-initdb.d

EXPOSE 8080

ENTRYPOINT ["bash", "-c"]
CMD [ "/usr/bin/run-maxkb.sh" ]