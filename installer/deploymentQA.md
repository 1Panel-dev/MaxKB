# MaxKB 部署问题排查指南

本文档记录 MaxKB 部署过程中常见问题及解决方案。

## Poetry.lock 文件说明

### poetry.lock 文件的作用

1. **依赖版本锁定**
   - 记录项目所有依赖包的确切版本
   - 包括直接依赖和间接依赖的精确版本
   - 包含包的哈希值用于安全验证

2. **确保环境一致性**
   - 开发环境：所有开发者使用相同版本的依赖
   - 生产环境：部署时使用与开发时完全相同的依赖版本
   - CI/CD：确保构建过程可重复

3. **安全性**
   - 防止依赖包被恶意替换
   - 确保构建的可重现性

---

## 问题1：Poetry 依赖冲突

### 问题描述
在使用 `build-images.sh` 构建后台镜像时，出现以下错误：

```
pyproject.toml changed significantly since poetry.lock was last generated. Run `poetry lock` to fix the lock file.
ERROR: failed to build: failed to solve: process "/bin/sh -c python3 -m venv /opt/py3 && ... poetry install --only=main ..." did not complete successfully: exit code: 1
```

### 根本原因
Docker 构建过程中的文件修改导致依赖冲突：

1. **文件复制到容器**：`COPY . /opt/maxkb-app`
2. **动态修改 pyproject.toml**：`sed -i 's/^torch.*/torch = {version = "2.7.1+cpu", source = "pytorch"}/g' pyproject.toml`
3. **poetry.lock 过时**：修改后的 `pyproject.toml` 与现有 `poetry.lock` 不匹配

### 一劳永逸解决方案

**已在 `installer/Dockerfile-backend` 中实施修复**：

```dockerfile
# 创建 Python 虚拟环境并安装依赖
RUN python3 -m venv /opt/py3 && \
    pip install poetry==2.0.0 --break-system-packages && \
    poetry config virtualenvs.create false && \
    . /opt/py3/bin/activate && \
    if [ "$(uname -m)" = "x86_64" ]; then sed -i 's/^torch.*/torch = {version = "2.7.1+cpu", source = "pytorch"}/g' pyproject.toml; fi && \
    rm -f poetry.lock && \
    poetry lock && \
    poetry install --only=main && \
    pip install requests pymysql psycopg2-binary
```

**关键修改**：
- 添加 `rm -f poetry.lock`：删除可能过时的锁定文件
- 添加 `poetry lock`：在修改 pyproject.toml 后重新生成锁定文件

### 优势
1. **无需本地操作**：无论本地 poetry.lock 状态如何，都能正常构建
2. **架构自适应**：自动处理不同 CPU 架构的 torch 依赖
3. **版本一致性**：确保容器内依赖版本与 pyproject.toml 匹配

---

## 问题2：构建脚本语法错误

### 问题描述
执行构建脚本时出现语法错误：

```bash
./installer/build-images.sh --registry docker.zhouke.tech/gs_kh --push backend
./installer/build-images.sh: 行 116: 未预期的记号 "fi" 附近有语法错误
```

### 原因分析
通过 `cat -A` 命令检查发现文件中存在：
- UTF-8 编码问题导致的乱码字符
- 中文注释变成乱码（如：`M-fM-^NM-(M-iM-^@M-^AM-iM-^UM-^\`）
- 语法关键字被污染（如：`then` 变成 `thenprop`）

### 诊断方法

#### 1. 检查文件语法
```bash
bash -n installer/build-images.sh
```

#### 2. 检查文件编码
```bash
file installer/build-images.sh
```

#### 3. 查看隐藏字符
```bash
sed -n '110,120p' installer/build-images.sh | cat -A
```

#### 4. 检查进程冲突
```bash
ps aux | grep build-images
ps aux | grep docker
```

### 解决方案

#### 方案1：重新获取干净文件（推荐）
```bash
# 如果使用 Git
git checkout -- installer/build-images.sh

# 验证修复
bash -n installer/build-images.sh
```

#### 方案2：修复编码问题
```bash
# 转换换行符
dos2unix installer/build-images.sh

# 修复权限
chmod +x installer/build-images.sh

# 手动修复关键语法错误
sed -i 's/then.*$/then/' installer/build-images.sh
```

#### 方案3：创建简化构建脚本
如果原脚本无法修复，可使用简化版本：

```bash
cat > build-backend-simple.sh << 'EOF'
#!/bin/bash
set -e

REGISTRY=""
TAG="v2.0"
PLATFORM="linux/amd64"
PUSH="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --registry) REGISTRY="$2"; shift 2 ;;
        --tag) TAG="$2"; shift 2 ;;
        --platform) PLATFORM="$2"; shift 2 ;;
        --push) PUSH="true"; shift ;;
        backend) shift ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

if [ -z "$REGISTRY" ]; then
    echo "错误: 请指定 --registry 参数"
    exit 1
fi

IMAGE_NAME="$REGISTRY/maxkb/backend:$TAG"
echo "构建后台应用镜像: $IMAGE_NAME"

docker build --platform $PLATFORM \
    -f installer/Dockerfile-backend \
    -t "$IMAGE_NAME" \
    .

if [ "$PUSH" = "true" ]; then
    echo "推送镜像: $IMAGE_NAME"
    docker push "$IMAGE_NAME"
fi

echo "构建完成"
EOF

chmod +x build-backend-simple.sh
./build-backend-simple.sh --registry your-registry --push backend
```

### 预防措施

1. **版本控制**
```bash
# 提交工作版本
git add installer/build-images.sh
git commit -m "Working version of build script"
```

2. **备份关键文件**
```bash
cp installer/build-images.sh installer/build-images.sh.backup
```

3. **设置文件保护**
```bash
# 构建时设为只读
chmod 444 installer/build-images.sh
# 完成后恢复
chmod 755 installer/build-images.sh
```

4. **环境检查**
```bash
# 检查系统编码
locale

# 检查编辑器设置
# 确保 IDE 使用 UTF-8 编码和 Unix 换行符
```

---

## 常见问题排查流程

### 1. 环境检查
```bash
# 检查 Docker 环境
docker --version
docker info

# 检查文件权限
ls -la installer/build-images.sh

# 检查当前目录
pwd
# 确保在项目根目录执行脚本
```

### 2. 依赖检查
```bash
# 检查 Poetry 状态（可选，Dockerfile 已自动处理）
poetry check
poetry show --tree

# 检查必要文件
ls -la installer/Dockerfile-backend
ls -la ui/package.json
ls -la pyproject.toml
```

### 3. 脚本检查
```bash
# 语法检查
bash -n installer/build-images.sh

# 文件完整性
file installer/build-images.sh
wc -l installer/build-images.sh
```

### 4. 网络和仓库检查
```bash
# 测试镜像仓库连接
docker login your-registry

# 测试网络连接
ping your-registry-domain
```

---

## 快速构建指南

### 标准构建流程

```bash
# 1. 进入项目根目录
cd ~/PycharmProjects/MokeKB

# 2. 直接构建（无需预处理 poetry.lock）
./installer/build-images.sh --registry your-registry.com --push backend

# 3. 构建其他组件（可选）
./installer/build-images.sh --registry your-registry.com --push frontend
./installer/build-images.sh --registry your-registry.com --push models

# 4. 构建所有组件
./installer/build-images.sh --registry your-registry.com --push all
```

### 构建参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--registry` | 私有镜像仓库地址 | `docker.zhouke.tech/gs_kh` |
| `--tag` | 镜像标签 | `v2.0`（默认） |
| `--platform` | 目标平台 | `linux/amd64`（默认） |
| `--push` | 构建后推送到仓库 | 无参数值 |
| `--no-cache` | 不使用缓存构建 | 无参数值 |

---

## 联系支持

如果遇到本文档未涵盖的问题，请：

1. 收集错误信息和日志
2. 记录操作步骤
3. 注明系统环境（OS、Docker版本、Python版本等）
4. 提交 Issue 或联系技术支持

---

*文档更新时间：2024年*
*适用版本：MaxKB v2.0*
*最后修改：Dockerfile 已优化，自动处理 poetry 依赖冲突*