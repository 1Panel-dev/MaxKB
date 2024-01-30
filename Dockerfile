FROM python:3.11-slim

ENV LANG=C.UTF-8

USER root
# 创建工作目录
RUN mkdir -p /opt/maxkb/app && mkdir -p /opt/maxkb/model
# 拷贝项目
COPY . /opt/maxkb/app
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
RUN pip3 install --no-cache-dir -r requirements.txt --trusted-host pypi.tuna.tsinghua.edu.cn
# 删除前端依赖
RUN rm -rf ui/node_modules
# 启动命令
CMD ["bash","-c","python /opt/maxkb/app/main.py start"]
