# MaxKB 离线部署指南

本文档介绍如何将 MaxKB 项目打包成 Docker 镜像并在本地环境中离线部署。

## 准备工作

1. 确保目标机器上已安装 Docker
2. 准备好 MaxKB 项目的完整代码包

## 构建离线镜像

### 方法一：直接从源码构建

1. 克隆或下载 MaxKB 项目源码到本地：
```bash
git clone https://github.com/your-repo/maxkb.git
```

2. 进入项目目录并构建镜像：
```bash
cd maxkb
docker build -f installer/Dockerfile-offline -t maxkb-offline:v2.0 .
```

### 方法二：预构建镜像导出/导入

如果您已经有构建好的镜像，可以导出为 tar 文件进行传输：

1. 在联网环境中导出镜像：
```bash
docker save -o maxkb-offline-v2.0.tar maxkb-offline:v2.0
```

2. 将 tar 文件传输到目标机器后导入：
```bash
docker load -i maxkb-offline-v2.0.tar
```

## 运行容器

使用以下命令运行 MaxKB 容器：

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /opt/maxkb/data:/opt/maxkb/data \
  -v /opt/maxkb/logs:/opt/maxkb/logs \
  maxkb-offline:v2.0
```

### 自定义配置

如果需要自定义数据库或其他配置，可以通过挂载配置文件实现：

```bash
# 创建配置文件
mkdir -p /opt/maxkb/conf
cp config.yaml /opt/maxkb/conf/config.yml

# 修改配置文件中的数据库和其他设置

# 运行容器并挂载配置
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /opt/maxkb/data:/opt/maxkb/data \
  -v /opt/maxkb/logs:/opt/maxkb/logs \
  -v /opt/maxkb/conf:/opt/maxkb/conf \
  maxkb-offline:v2.0
```

## 访问应用

容器启动后，可以通过以下地址访问 MaxKB：

- 用户界面: http://localhost:8080/admin
- 对话界面: http://localhost:8080/chat
- API 文档: http://localhost:8080/api/doc

## 数据持久化

默认情况下，应用数据保存在以下目录中：

- 数据库数据: `/opt/maxkb/data`
- 日志文件: `/opt/maxkb/logs`
- 配置文件: `/opt/maxkb/conf`

请确保这些目录在宿主机上有适当的读写权限。

## 故障排除

### 查看容器日志

```bash
docker logs -f maxkb
```

### 进入容器调试

```bash
docker exec -it maxkb bash
```

### 停止和删除容器

```bash
# 停止容器
docker stop maxkb

# 删除容器
docker rm maxkb

# 删除镜像
docker rmi maxkb-offline:v2.0
```

## 系统要求

- Docker 18.09 或更高版本
- 至少 4GB 内存
- 至少 2 核 CPU
- 至少 10GB 可用磁盘空间

## 注意事项

1. 首次启动可能需要几分钟来初始化数据库和服务
2. 默认管理员账户信息请参考官方文档
3. 生产环境部署建议使用外部数据库以提高稳定性