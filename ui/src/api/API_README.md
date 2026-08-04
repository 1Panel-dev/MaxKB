# API 目录说明

`src/api` 负责前端与服务端之间的通信，按照应用入口隔离 Admin 与 Chat 请求体系。当前只实现
Admin API；Chat 目录作为独立体系预留。

```text
src/api/
├── admin/
│   ├── core/             # Admin 请求基础能力
│   │   ├── request.ts    # Axios 实例、HTTP 方法与统一响应解包
│   │   ├── types.ts      # 通用响应、分页与请求配置类型
│   ├── auth/             # Admin 登录认证接口
│   ├── workspace/        # 工作空间业务接口
│   └── system/           # 系统管理业务接口
├── chat/                 # Chat 独立请求体系，当前预留
└── API_README.md
```

## 分层职责

- `admin/core` 处理请求发送、协议解析和全局传输错误，通过 Admin Pinia Store 获取 token 与
  语言，并统一处理超时、404、401、403 的提示或跳转。
- `admin/auth`、`admin/workspace` 和 `admin/system` 描述具体业务接口，不管理页面 loading、
  消息提示或路由跳转。
- 页面或 Store 负责 loading、成功提示、特殊业务错误以及请求成功后的状态变更。
- Chat 的 base URL、鉴权和错误处理独立实现，不复用 Admin 请求客户端。

## 业务接口组织

- 业务 API 按一级业务域、二级资源模块归类，例如 `workspace/agent.ts` 和
  `system/authentication.ts`。
- 一类资源的增删改查放在同一个文件，不创建汇总所有业务接口的 `api.ts`。
- 模块私有类型优先与接口放在同一文件；同一业务域多个模块共享的类型放该业务域的
  `types.ts`；协议通用类型放 `admin/core/types.ts`。
- 每个业务接口使用 `export function` 单独导出，同时在文件末尾通过 `export default { ... }`
  直接默认导出接口对象，不为默认导出声明中间变量；调用方统一按“文件名 camelCase + `Api`”
  命名默认导入并通过该对象调用，不创建只做二次转发的 `index.ts`。
  例如从 `login.ts` 使用 `import loginApi from '@/api/admin/auth/login'`，再调用
  `loginApi.postLogin()`。
- 文件形成多个清晰子能力后再升级为同名目录，避免提前增加层级。

## 接口命名

- 导出函数使用“HTTP 方法 + 业务名称”的 camelCase 名称，使调用处能直接识别请求方式，
  例如 `getCaptcha`、`postLogin`、`postLogout`、`getWorkspaceDetail`、`postTool`、
  `putRole` 和 `deleteKnowledge`。
- 前缀与实际请求方法保持一致：查询使用 `get`，创建和业务动作使用 `post`，完整更新使用
  `put`，删除使用 `delete`。局部更新接口真实采用 PATCH 时使用 `patch`。
- HTTP 方法前缀后必须带有明确的业务名称，不导出 `get`、`post`、`list`、`detail`、`login`
  或 `logout` 等缺少请求方式或业务含义的名称。
- 函数名不追加 `Api` 后缀，所属业务域由目录和文件名表达。

## 请求约定

- Admin 业务接口只声明相对资源路径，`/admin/api` 等部署前缀由 `core/request.ts` 统一处理。
- Admin Router 与请求客户端直接读取 `window.MaxKB` 运行时路径配置；`Window` 和
  `MaxKBRuntimeConfig` 的全局类型统一声明在根目录 `env.d.ts`。
- Admin 普通 JSON 请求使用 Axios；`request.ts` 导出 Axios 实例以及 `promise`、`get`、
  `post`、`put`、`del` 请求封装。
- 正常 JSON 接口返回 `Promise<T>`，请求层负责解包后端 `{ code, message, data }` 响应。
- token 和语言分别由 `stores/login.ts`、`stores/user.ts` 管理；Router、Axios 等业务代码通过
  `stores/index.ts` 导出的 `useStore()` 按需访问 Store；401 响应统一清除 token 并跳转 Admin
  登录页。
- loading 不作为 API 函数参数，由调用接口的页面或 Store 管理。
- 上传、下载和流式请求在真实需求出现时独立设计，不提前塞入普通 JSON 请求客户端。
