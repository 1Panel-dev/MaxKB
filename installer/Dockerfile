FROM ghcr.io/maxkb-dev/vector-model:v1.0.0 as vector-model

FROM node:18-alpine3.18 as web-build
COPY ui ui
RUN cd ui && \
    npm install && \
    npm run build && \
    rm -rf ./node_modules

FROM ghcr.io/maxkb-dev/python-pg:python3.11.8-pg15.6
# 创建工作目录
RUN mkdir -p /opt/maxkb/app && mkdir -p /opt/maxkb/model && mkdir -p /opt/maxkb/conf
VOLUME /opt/maxkb
# 拷贝项目
COPY . /opt/maxkb/app
COPY installer/config.yaml /opt/maxkb/conf
RUN rm -rf /opt/maxkb/app/ui /opt/maxkb/app/build
COPY --from=vector-model model /opt/maxkb/app/model
COPY --from=web-build ui /opt/maxkb/app/ui
RUN ls -la /opt/maxkb/app
# 复制模型
RUN mv /opt/maxkb/app/model/* /opt/maxkb/model
RUN ls /opt/maxkb/model
RUN cp -r /opt/maxkb/model/base/hub /opt/maxkb/model/tokenizer
# 设置工作目录
WORKDIR /opt/maxkb/app
# 更新apt-get包管理器
RUN apt-get update&&apt-get install -y  curl
# 更新pip
RUN pip3 install --upgrade pip
# 安装 poetry包管理器
RUN pip3 install poetry
# 导出依赖
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
# 下载python依赖
RUN pip3 install --no-cache-dir -r requirements.txt
# 启动命令
EXPOSE 8000
COPY installer/run-maxkb.sh /usr/bin/
RUN chmod 755 /usr/bin/run-maxkb.sh
ENTRYPOINT ["bash", "-c"]
CMD [ "/usr/bin/run-maxkb.sh" ]