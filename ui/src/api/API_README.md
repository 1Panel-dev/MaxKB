# API 目录说明

`src/api` 负责前端与服务端之间的通信，按照应用入口隔离 Admin 与 Chat 请求体系。当前只实现
Admin API；Chat 目录作为独立体系预留。

```text
src/api/
├── admin/
│   ├── core/             # Admin 请求基础能力
│   │   ├── request.ts    # Axios 实例、HTTP 方法与统一响应解包
│   │   └── types.ts      # Admin 请求协议和 loading 类型
│   ├── auth/             # Admin 登录认证接口
│   │   └── types.ts      # 认证 API 与认证 Store 共用类型
│   ├── workspace/        # 工作空间业务接口
│   └── system/           # 系统管理业务接口
├── chat/                 # Chat 独立请求体系，当前预留
├── types/                # API 与 View/Component 共用的业务类型
│   ├── index.ts          # API 公共类型的唯一导入入口
│   ├── common.ts         # 多个 API 业务域共用的基础类型
│   └── <domain>.ts       # 按明确业务域拆分的共享类型
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

- 业务 API 按一级业务域、二级资源文件归类，例如 `workspace/agent.ts` 和
  `system/workspace.ts`。
- 一类资源的增删改查放在同一个文件，不创建同名业务文件夹或汇总所有业务接口的 `api.ts`。
- 每个业务接口函数必须添加简短的 JSDoc，说明接口的业务作用；注释应描述“获取什么”“保存什么”
  或“对哪个资源执行什么操作”，不重复参数类型、请求方法等代码已经清楚表达的信息。
- 每个业务接口使用 `const` 声明的箭头函数，不单独具名导出；在文件末尾通过
  `export default { ... }` 直接默认导出接口对象，不为默认导出声明中间变量。调用方统一按
  “文件名 PascalCase + `Api`”命名默认导入并通过该对象调用，不创建只做二次转发的聚合入口。
  该规则适用于 `admin/auth`、`admin/workspace`、`admin/system` 等业务 API；
  `admin/core/request.ts` 等请求基础设施可按职责提供具名导出。
  例如从 `login.ts` 使用 `import LoginApi from '@/api/admin/auth/login'`，再调用
  `LoginApi.postLogin()`；System Workspace API 使用
  `import WorkspaceApi from '@/api/admin/system/workspace'`。

## 类型组织

API 类型统一在 `src/api` 范围内管理，相关规则由本文档统一维护。

新增或移动类型时按以下顺序判断：

1. 只在一个文件中使用：直接在该文件中声明，不导出。
2. 只在同一个 API 业务边界内跨文件使用：放在该边界的 `types.ts`；出现重复声明时，提取到
   最近共同目录的 `common.ts`。
3. 同一个业务类型同时被 API 和 View 或 Component 使用：放入 `src/api/types/<domain>.ts`，
   通过 `src/api/types/index.ts` 导出。
4. Router、Layout、View 或 Component 专属类型保留在所属目录或实现文件，不放入
   `src/api/types`。

具体规则：

- API 专用的请求参数、响应包装、请求配置和基础设施类型，放在对应 API 文件、资源目录的
  `types.ts`，或该 API 业务域的 `common.ts`。
- `src/api/types` 只存放 API 与 View 或 Component 跨层共用的业务类型，使用方统一通过
  `import type { ... } from '@/api/types'` 导入，不写 `/index.ts`。
- `src/api/types/index.ts` 只负责导出各业务域类型，不直接声明类型。
- 新增类型前先搜索是否已有等价声明，优先复用或扩展已有类型。
- 同一业务边界内的重复类型提取到最近共同目录的 `common.ts`；`common.ts` 不得成为无关类型
  的集合。
- API 与 View 或 Component 使用同一业务类型时只保留一份声明，不得在两层分别定义。
- 名称相同但业务含义或字段约束不同的类型不要强行合并，应使用明确的领域名称区分。
- 使用 `interface` 描述对象结构，使用 `type` 描述联合类型、交叉类型、工具类型结果或别名。
- 类型名称必须体现业务含义，避免使用 `Data`、`Item`、`Info` 等脱离领域后含义不清的名称。

## 接口命名

- 业务接口函数使用“HTTP 方法 + 业务名称”的 camelCase 名称，使调用处能直接识别请求方式，
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
- 文件下载接口使用 `postBlob` 获取原始 `Blob`，由调用页面负责命名并触发浏览器下载。
- 业务代码通过 `api.method().then(...)` 处理接口成功后的状态变化；通用接口错误由请求层统一
  提示，不在调用处重复使用 `try/catch` 或 `.catch()` 提示相同错误。只有业务降级、状态恢复等
  非提示类失败处理可以按需保留失败分支。
- token 和平台公开档案由 `stores/auth.ts` 管理，语言由 `stores/user.ts` 管理；Router、Axios 等业务代码通过
  `stores/index.ts` 导出的 `useStore()` 按需访问 Store；401 响应统一清除 token 并跳转 Admin
  登录页。
- loading 不作为 API 函数参数，由调用接口的页面或 Store 管理。
- 上传、下载和流式请求在真实需求出现时独立设计，不提前塞入普通 JSON 请求客户端。
