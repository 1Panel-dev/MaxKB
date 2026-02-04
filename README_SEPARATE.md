#  前后端分离启动说明

本文档介绍如何将项目的前端和后端分别独立启动。

## 前后端分离启动

### 启动后端服务

```bash
./start_backend.sh
```

或者直接运行：
```bash
python main.py start all
```

后端服务默认运行在 `http://localhost:8080`

### 启动前端服务

```bash
./start_frontend.sh
```

或者进入 ui 目录分别启动：
```bash
cd ui
npm run dev     # 启动管理界面，运行在 http://localhost:3000
npm run chat    # 启动聊天界面，运行在 http://localhost:3001
```

### 访问应用

- 管理界面: http://localhost:3000
- 聊天界面: http://localhost:3001
- 后端 API: http://localhost:8080

## 注意事项

1. 首次运行前请确保已经安装了所有依赖：
   ```bash
   pip install -r pyproject.toml
   cd ui && npm install
   ```

2. 前后端分离模式下，前端通过代理配置连接后端服务，请确保后端服务在前端访问时处于运行状态。

3. 如果需要更改默认端口，请相应地更新以下配置：
   - 后端端口：修改 main.py 中的 runserver 参数
   - 前端管理界面端口：修改 ui/env/.env 文件中的 VITE_APP_PORT
   - 前端聊天界面端口：修改 ui/env/.env.chat 文件中的 VITE_APP_PORT

4. 已经修复了跨域问题，现在可以正常登录。