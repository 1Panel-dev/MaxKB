FROM ghcr.io/1panel-dev/maxkb-vector-model:v1.0.0 as vector-model

FROM node:18-alpine3.18 as web-build
COPY ui ui
RUN cd ui && \
    npm install && \
    npm run build

FROM ghcr.io/1panel-dev/maxkb-python-pg:python3.11.8-pg15.3
# 创建工作目录
RUN mkdir -p /opt/maxkb/app && /opt/maxkb/app/ui && mkdir -p /opt/maxkb/model && mkdir -p /opt/maxkb/conf
# 拷贝项目
COPY . /opt/maxkb/app
COPY installer/config.yaml /opt/maxkb/conf
COPY --from=vector-model model /opt/maxkb/app/model
COPY --from=web-build ui/dist /opt/maxkb/app/ui
ENV POSTGRES_USER root
ENV POSTGRES_PASSWORD Password123@postgres
WORKDIR /opt/maxkb/app
RUN rm -rf /opt/maxkb/app/build && \
    mv /opt/maxkb/app/model/* /opt/maxkb/model && \
    cp -r /opt/maxkb/model/base/hub /opt/maxkb/model/tokenizer && \
    apt-get update && apt-get install -y curl && \
    pip3 install --upgrade pip && \
    pip3 install poetry && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 cache purge && \
    rm -rf /var/lib/apt/lists/*
# 启动命令
VOLUME /opt/maxkb/conf
EXPOSE 8000
COPY installer/run-maxkb.sh /usr/bin/
RUN chmod 755 /usr/bin/run-maxkb.sh
ENTRYPOINT ["bash", "-c"]
CMD [ "/usr/bin/run-maxkb.sh" ]