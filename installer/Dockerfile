FROM ghcr.io/1panel-dev/maxkb-vector-model:v1.0.0 as vector-model

FROM node:18-alpine3.18 as web-build
COPY ui ui
RUN cd ui && \
    npm install && \
    npm run build && \
    rm -rf ./node_modules

FROM ghcr.io/1panel-dev/maxkb-python-pg:python3.11.8-pg15.3
# 创建工作目录
RUN mkdir -p /opt/maxkb/app && mkdir -p /opt/maxkb/model && mkdir -p /opt/maxkb/conf
# 拷贝项目
COPY . /opt/maxkb/app
RUN rm -rf /opt/maxkb/app/ui
COPY installer/config.yaml /opt/maxkb/conf
COPY --from=vector-model model /opt/maxkb/app/model
COPY --from=web-build ui /opt/maxkb/app/ui
ENV POSTGRES_USER root
ENV POSTGRES_PASSWORD Password123@postgres
WORKDIR /opt/maxkb/app
RUN mv /opt/maxkb/app/model/* /opt/maxkb/model && \
    cp -r /opt/maxkb/model/base/hub /opt/maxkb/model/tokenizer && \
    apt-get update && apt-get install -y curl && \
    pip3 install --upgrade pip && \
    cat pyproject.toml && \
    if [ "$(uname -m)" = "aarch64" ]; then sed -i '/^torch/d' pyproject.toml; fi && \
    cat pyproject.toml && \
    pip3 install poetry && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    cat requirements.txt && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 cache purge && \
    rm -rf /var/lib/apt/lists/*
# 启动命令
EXPOSE 8080
COPY installer/run-maxkb.sh /usr/bin/
RUN chmod 755 /usr/bin/run-maxkb.sh
ENTRYPOINT ["bash", "-c"]
CMD [ "/usr/bin/run-maxkb.sh" ]