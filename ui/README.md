# MaxKB v3 前端

MaxKB 企业级 AI 智能体平台的前端工程，使用 Vue 3.5、TypeScript 6、Vite 8、Element Plus、
Tailwind CSS 4、Pinia 3 和 Vue Router 5，工作流画布基于 LogicFlow。

项目采用 Admin 和 Chat 双入口。Admin 包含登录、工作空间资源、系统管理和工作流编辑等功能；
Chat 包含单应用与门户认证、智能体列表及正式对话，使用独立的 Router、Pinia 和请求客户端。

## 本地开发

Node.js 版本要求为 `^22.18.0 || >=24.12.0`，以 `package.json` 的 `engines` 为准。
以下命令均在 `ui/` 目录执行：

```bash
npm install
npm run dev
```

Admin 默认访问地址为 `http://localhost:3000/admin/`。在另一个终端运行 `npm run chat`，
可通过 `http://localhost:3001/chat/` 访问 Chat 入口。开发服务器启用 `strictPort`，端口被占用时不会自动换端口。

### 后端代理与环境变量

公共及 Admin 默认配置在 `env/.env`，Chat 模式通过 `env/.env.chat` 覆盖入口、路径和端口。
本地覆盖可放在 `env/.env.local`，Chat 专属覆盖可放在 `env/.env.chat.local`。

| 变量              | Admin 默认值 | Chat 默认值 | 用途                       |
| ----------------- | ------------ | ----------- | -------------------------- |
| `VITE_APP_NAME`   | `admin`      | `chat`      | 应用名称                   |
| `VITE_BASE_PATH`  | `/admin/`    | `/chat/`    | 路由基础路径与构建输出目录 |
| `VITE_APP_PORT`   | `3000`       | `3001`      | 开发服务端口               |
| `VITE_APP_TITLE`  | `MaxKB`      | `MaxKB`     | HTML 标题                  |
| `VITE_ENTRY`      | `admin.html` | `chat.html` | HTML 入口                  |
| `VITE_API_TARGET` | 未设置       | 未设置      | 覆盖开发代理的后端地址     |

当前未设置 `VITE_API_TARGET` 时，使用 `vite.config.ts` 中的 `defaultBackendTarget`，
值为 `http://47.120.55.164:38080`。连接本地后端时，在 `env/.env.local` 中配置：

```dotenv
VITE_API_TARGET=http://127.0.0.1:8080
```

开发代理覆盖 `/admin/api`、`/chat/api`、`/doc`、`/schema`、`/static` 和当前应用基础路径下的
OSS 文件接口。前端业务接口需要可用的后端服务。

## 构建与检查

| 命令                             | 作用                            |
| -------------------------------- | ------------------------------- |
| `npm run dev`                    | 启动 Admin 开发服务             |
| `npm run chat`                   | 启动 Chat 开发服务              |
| `npm run build`                  | 类型检查并构建 Admin            |
| `npm run build-chat`             | 类型检查并构建 Chat             |
| `npm run build-only`             | 仅构建 Admin                    |
| `npm run build-only-chat`        | 仅构建 Chat                     |
| `npm run type-check`             | 使用 `vue-tsc --build` 检查类型 |
| `npm run preview`                | 预览 Admin 构建产物             |
| `npm run preview -- --mode chat` | 预览 Chat 构建产物              |
| `npm run format`                 | 使用 Prettier 格式化 `src/`     |

`npm run lint` 当前仅配置了 `run-s "lint:*"`，但尚未定义任何 `lint:*` 子脚本，不能作为已执行
ESLint 检查的依据。需要检查代码时，可运行 `npx eslint <待检查的文件或目录>`。

路由菜单回归测试使用 Node 内置测试运行器：`node --test tests/router-menu.test.mjs`。

默认构建分别输出 `dist/admin/index.html` 和 `dist/chat/index.html`，HTML 由构建插件统一重命名。
静态资源使用相对路径（`base: './'`）；部署时仍需为 History 路由配置对应入口回退，
并由部署服务转发 API 和文件请求。Vite 的开发代理不会随静态构建产物部署。

## 开发规则

目录职责、开发约束和专题文档索引统一见 [AGENTS.md](AGENTS.md)。
修改代码前读取对应专题，文档只维护当前实现和使用规则。
