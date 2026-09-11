# API 目录说明

`src/api` 负责前端与服务端之间的通信，按照应用入口隔离 Admin 与 Chat 请求体系。当前只实现
Admin API；Chat 目录作为独立体系预留。

```text
src/api/
├── constants.ts                     # Admin 与 Chat 的 API base 路径常量
├── admin/
│   ├── auth/                         # Admin 登录认证与当前用户接口
│   │   └── types.ts                  # 认证 API 与认证 Store 共用类型
│   ├── core/                         # Admin 请求基础能力
│   │   ├── request.ts                # Axios 实例、HTTP 方法与统一响应解包
│   │   └── types.ts                  # Admin 请求协议和 loading 类型
│   ├── system/                       # 系统管理业务接口
│   │   ├── chat-user/                # 对话用户、用户组及认证接口
│   │   ├── settings/                 # 登录认证、邮件与外观设置接口
│   │   ├── shared-resources/         # System 共享资源接口
│   │   └── <resource>.ts             # 其他 System 单资源接口
│   ├── workspace/                    # 工作空间业务接口
│   │   ├── application/              # 智能体接口
│   │   ├── knowledge/                # 知识库接口
│   │   ├── model/                    # 模型接口
│   │   ├── trigger/                   # 触发器查询及维护接口
│   │   ├── tool/                     # 工具、工具工作流及工具商店接口
│   │   └── <resource>.ts             # 工作空间公共资源接口
│   └── provider.ts                   # Workspace 与 System 共用的模型供应商接口
├── chat/                             # Chat 独立请求体系，当前预留
│   └── README.md                     # Chat API 边界与后续实现说明
├── enums/                            # 后端固定枚举值
│   ├── index.ts                      # API 枚举值的唯一导入入口
│   └── <domain>.ts                   # 按明确业务域拆分的枚举值
├── types/                            # API 与 View/Component 共用的业务类型
│   ├── index.ts                      # API 公共类型的唯一导入入口
│   ├── common.ts                     # 多个 API 业务域共用的基础类型
│   └── <domain>.ts                   # 按明确业务域拆分的共享类型
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

- 业务 API 先按 Admin 入口下的 `auth`、`workspace`、`system` 等一级业务域归类。Workspace 和
  System 内部可继续按明确的功能域建立子目录，例如 `workspace/application/`、
  `workspace/tool/`、`system/chat-user/` 和 `system/settings/`；不需要分组的单资源接口直接放在
  所属一级业务域下。
- 一类资源的增删改查放在同一个最终资源文件中。调用方直接导入该文件，不为业务目录创建聚合
  入口，也不创建汇总所有业务接口的 `api.ts`。
- 工具基础信息和工具工作流使用后端不同资源接口：`workspace/tool/tool.ts` 维护工具增删改查，
  `workspace/tool/workflow.ts` 维护工具工作流的加载、保存和发布。
  工具工作流保存请求的 `default_model_setting` 与详情响应统一复用 `DefaultModelSettingPayload`。
- 每个业务接口函数必须添加简短的 JSDoc，说明接口的业务作用；注释应描述“获取什么”“保存什么”
  或“对哪个资源执行什么操作”，不重复参数类型、请求方法等代码已经清楚表达的信息。
- 每个业务接口使用 `const` 声明的箭头函数，不单独具名导出；在文件末尾通过
  `export default { ... }` 直接默认导出接口对象，不为默认导出声明中间变量。调用方统一按
  “文件名 PascalCase + `Api`”命名默认导入并通过该对象调用，不创建只做二次转发的聚合入口。
  该规则适用于 `admin/auth`、`admin/workspace`、`admin/system` 等业务 API；
  `admin/core/request.ts` 等请求基础设施可按职责提供具名导出。
  例如从 `login.ts` 使用 `import LoginApi from '@/api/admin/auth/login'`，再调用
  `LoginApi.postLogin()`；System Workspace API 使用
  `import WorkspaceApi from '@/api/admin/system/workspace'`；System 登录设置使用
  `import AuthSettingApi from '@/api/admin/system/settings/auth-setting'`。

### 四类特殊资源 API

`application`、`knowledge`、`model`、`tool` 是需要同时考虑 Workspace、System 资源管理和
System 共享资源的四类特殊资源。其接口按真实后端边界分别维护在 `admin/workspace/` 与
`admin/system/` 下，不把不同范围的 URL 合并为页面侧 API Map，也不让卡片或 Action 根据路由拼接
System 接口地址。

页面根据路由 `resourceScope` 选择当前范围的完整业务 API 对象，并将其传给需要请求的 Card
Action、Drawer 或 Dialog。复用方直接使用 `typeof XxxApi` 约束完整 API 对象；不要为每组 Action
额外维护逐方法接口，例如 `ModelActionApi`，也不要使用不断扩展的 `Pick<typeof XxxApi, ...>`。
仅展示数据的组件不接收 API。

### 工具列表查询

`workspace/tool/tool.ts` 的 `getAllTool(query)` 查询支持 `folder_id` 筛选的工作空间工具
非分页列表，用于文件夹菜单和工具选择弹窗。`getToolListWithShared(query)` 请求 `tool/tool_list`，
将响应的 `tools` 与 `shared_tools` 合并为 `ToolItem[]`，用于包含已授权共享工具的选项查询；
按工具类型筛选时使用 `tool_type`。`workspace/shared.ts` 的 `getAllTool(query)` 仅查询共享工具。

### 知识库维护

`workspace/knowledge/knowledge.ts` 与 `workspace/shared.ts` 的 `getAllKnowledge(query)`
分别查询工作空间及共享知识库的非分页列表，返回 `KnowledgeItem[]`，用于关联知识库选择等
需要全量选项的场景。原有 `getKnowledgePage` 继续用于分页列表。

`workspace/knowledge/knowledge.ts` 的 `putKnowledge` 更新普通知识库，`putLarkKnowledge`
更新飞书知识库；单项转移提交 `folder_id`。`putBatchMoveKnowledge` 将知识库 ID 数组和目标目录
组装为 `{ id_list, folder_id }`，`putBatchDeleteKnowledge` 将 ID 数组组装为 `{ id_list }`，
分别使用 PUT 请求 `batch_move` 和 `batch_delete`。页面和 Action 负责类型判断及 loading。

## 枚举与类型组织

API 枚举与类型统一在 `src/api` 范围内管理，相关规则由本文档统一维护。

后端字段的固定枚举值放在 `src/api/enums/<domain>.ts`，使用 `as const` 对象声明，并通过
`src/api/enums/index.ts` 统一导出。业务代码统一从 `@/api/enums` 导入运行时枚举值，不直接
引用领域文件；不得重复使用裸字符串或另建同值常量。

`src/api/enums` 按明确业务域拆分文件，不创建收集无关枚举的通用文件。枚举的联合类型在对应的
`src/api/types/<domain>.ts` 中由枚举对象派生，并继续通过 `@/api/types` 对外提供。例如
`TOOL_TYPE` 从 `@/api/enums` 导入，`ToolType` 从 `@/api/types` 导入。

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
- 字符串键字典统一使用 `@/api/types` 导出的 `Dict<T>`；未收窄值类型的请求查询参数使用
  `Dict<unknown>`，不再为相同结构声明额外别名。
- `src/api/types` 只存放 API 与 View 或 Component 跨层共用的业务类型，使用方统一通过
  `import type { ... } from '@/api/types'` 导入，不写 `/index.ts`。
- `src/api/types/index.ts` 只负责导出各业务域类型，不直接声明类型。
- 新增类型前先搜索是否已有等价声明，优先复用或扩展已有类型。
- `src/api/types/index.ts` 只使用 `export type *` 导出类型，运行时值不得从 `@/api/types` 暴露。
- 同一业务边界内的重复类型提取到最近共同目录的 `common.ts`；`common.ts` 不得成为无关类型
  的集合。
- API 与 View 或 Component 使用同一业务类型时只保留一份声明，不得在两层分别定义。
- 智能体详情及保存参数中的 `default_model_setting` 使用 `DefaultModelSettingPayload`；该类型由
  `DefaultModelType` 和单项配置 `ModelConfig` 组合而成（`types/model.ts`），工作流页面及设置抽屉
  从 `@/api/types` 引用。
- 名称相同但业务含义或字段约束不同的类型不要强行合并，应使用明确的领域名称区分。
- 使用 `interface` 描述对象结构，使用 `type` 描述联合类型、交叉类型、工具类型结果或别名。
- 类型名称必须体现业务含义，避免使用 `Data`、`Item`、`Info` 等脱离领域后含义不清的名称。

## 接口命名

- 业务接口函数使用“HTTP 方法 + 业务名称”的 camelCase 名称，使调用处能直接识别请求方式，
  例如 `getCaptcha`、`postLogin`、`postLogout`、`getWorkspaceDetail`、`postTool`、
  `putRole` 和 `deleteKnowledge`。
- 前缀与实际请求方法保持一致：查询使用 `get`，创建和业务动作使用 `post`，完整更新使用
  `put`，删除使用 `delete`。局部更新接口真实采用 PATCH 时使用 `patch`。
- 文件导出是直接触发浏览器下载的业务动作，使用 `exportXxx` 命名，例如 `exportTool`。
- HTTP 方法前缀后必须带有明确的业务名称，不导出 `get`、`post`、`list`、`detail`、`login`
  或 `logout` 等缺少请求方式或业务含义的名称。
- 函数名不追加 `Api` 后缀，所属业务域由目录和文件名表达。

## 请求约定

- `constants.ts` 统一导出 `ADMIN_API_BASE_PATH` 和 `CHAT_API_BASE_PATH`，分别优先读取
  `window.MaxKB.prefix` 和 `window.MaxKB.chatPrefix`，再回退到 `VITE_BASE_PATH` 和各自默认路径；
  去掉末尾斜杠后追加 `/api`。Admin、Chat 请求客户端和会话流式请求复用这些常量。
- Admin 普通业务接口只声明相对资源路径，由 `core/request.ts` 的 Axios baseURL 处理部署前缀；
  流式接口显式传入对应的 API base 常量。
- Admin Router 直接读取 `window.MaxKB` 运行时路径配置，请求客户端通过上述常量读取；`Window` 和
  `MaxKBRuntimeConfig` 的全局类型统一声明在根目录 `env.d.ts`。
- Admin 普通 JSON 请求使用 Axios；`request.ts` 导出 Axios 实例以及 `promise`、`get`、
  `post`、`put`、`del`、流式响应 `postStream` 和 Blob 文件 `downloadRequest` 请求封装。
- 正常 JSON 接口返回 `Promise<T>`，请求层负责解包后端 `{ code, message, data }` 响应。
- GET 文件导出使用 `getExportFile`；需要通过 POST 同时传递查询参数和可选请求体的 Excel 导出
  使用 `postExportExcel`；Skill 压缩包等指定请求方法的文件下载使用 `downloadRequest`。请求层统一
  获取 Blob、解析 `Content-Disposition` 文件名并触发浏览器下载；业务 API 只需传入接口地址及业务参数。
- 业务代码通过 `api.method().then(...)` 处理接口成功后的状态变化；通用接口错误由请求层统一
  提示，不在调用处重复使用 `try/catch` 或 `.catch()` 提示相同错误。只有业务降级、状态恢复等
  非提示类失败处理可以按需保留失败分支。
- token 和平台公开档案由 `stores/auth.ts` 管理，语言由 `stores/user.ts` 管理；Router、Axios 等业务代码通过
  `stores/index.ts` 导出的 `useStore()` 按需访问 Store；401 响应统一清除 token 并跳转 Admin
  登录页。
- loading 不作为 API 函数参数，由调用接口的页面或 Store 管理。
- 流式 POST 请求使用 `postStream` 返回原始 `Response`，由业务组件按具体协议解析数据块；
  参数顺序为 `postStream(base, path, data?, config?)`，`config.signal` 用于取消请求。
  鉴权、语言请求头和错误状态仍由请求基础设施统一处理。
- 上传、下载和其他特殊请求在真实需求出现时独立设计，不提前塞入普通 JSON 请求客户端。

### 资源用户授权

`admin/workspace/resource-authorization.ts` 按指定资源查询和更新用户权限，使用
`resource_user_permission/resource/<target>/resource/<resource>`；与 System 用户视角的
`user_resource_permission` 区分。分页使用 `ParamsPage`，直接返回
`ResponsePage<ResourceUserPermission>`；提交 `ResourceUserPermissionPayload[]`。
用户及用户组的查询和更新接口均以必填的 `workspaceId` 为首个参数，由调用方从资源或文件夹
接口数据的 `workspace_id` 传入，不读取或回退到路由工作空间。
`ResourceAuthorizationTargetType` 包含资源类型和三个 `_FOLDER` 类型，文件夹类型用于后端
鉴权。包含子资源时传 `include_children: true` 及经过管理权限筛选的 `folder_ids`，
普通资源或仅当前文件夹不传子文件夹 ID。loading、刷新及成功提示由抽屉负责。

用户组视角使用同文件的 `getResourceUserGroupAuthorization` 和
`putResourceUserGroupAuthorization`，请求路径为
`resource_user_group_permission/resource/<target>/resource/<resource>`。分页返回
`ResponsePage<ResourceUserGroupPermission>`（`id`、`name`、`count`、`permission`），
名称查询参数为 `name`，提交 `ResourceUserGroupPermissionPayload[]`，对象 ID 字段为
`user_group_id`；文件夹生效范围参数与用户授权一致。

System 资源管理的用户授权维护在 `admin/system/resource-management/resource-authorization.ts`，
使用 `/system/workspace/<workspaceId>/resource_management/resource/<target>/resource/<resource>`。
查询与保存方法以必填的 `workspaceId` 为首个参数，由调用方从资源数据的 `workspace_id` 传入，
不得读取或回退到路由工作空间。其余参数、分页类型、响应类型及提交类型与 Workspace 用户授权一致。
loading 由组件管理。`ResourceAuthorizationDrawer` 内部通过 `isSystemResource()` 选择完整的用户授权
API 对象和工作空间上下文，作为该抽屉的范围选择例外；用户组仍使用
现有 Workspace 接口，不推测 System 用户组路径。

### 关联资源

`admin/workspace/related-resources.ts` 维护关联资源查询：
`getResourceDependencies` 查询当前资源依赖的资源，对应后端 `mapping_resource`；
`getResourceDependents` 查询引用当前资源的资源，对应后端 `resource_mapping`。
前端按关联资源语义命名，后端接口路径保持不变。方法接收工作空间 ID、资源类型、资源 ID、`ParamsPage`
和查询参数；工作空间 ID 由目标资源数据的 `workspace_id` 显式传入，不读取路由。返回 `ResponsePage<RelatedResource>`，
不传 loading，不重复解包响应。`RelatedResource` 通过 `@/api/types` 导出，保留
`source_*`、`target_*` 字段。依赖查询按 `target_type` 筛选，被依赖查询按 `source_type`
筛选，类型数组沿用请求层的数组序列化。页面负责按资源范围传入完整 API，未推测 System 接口。

### 触发器维护

`workspace/trigger/trigger.ts` 维护分页、详情、新建、编辑、删除及批量接口。
`putBatchActivateTrigger(ids, isActive)` 提交 `{ id_list, is_active }` 到 `batch_activate`；
`putBatchDeleteTrigger(ids)` 提交 `{ id_list }` 到 `batch_delete`。单项启停通过 `putTrigger`
仅提交 `is_active`。`Trigger` 为分页摘要，`TriggerDetail` 为含任务参数的完整详情；
`TriggerPayload` 用于新建和编辑，ID 在新建前生成以展示事件回调 URL。

### 知识库工作流

`workspace/knowledge/knowledge.ts` 的 `getKnowledgeDetail` 返回 `KnowledgeDetail`，包含知识库
名称、所属目录，以及工作流类型的 `work_flow` 和发布状态；进入画布只调用此详情接口加载。
`workspace/knowledge/workflow.ts` 维护保存和发布，保存提交 `work_flow`，响应使用
`KnowledgeWorkflowDetail`。前端详情与保存协议的 `default_model_setting` 复用
`DefaultModelSettingPayload`；服务端需支持该字段的持久化与回传（当前仓库知识库后端尚未实现）。
