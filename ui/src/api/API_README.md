# API 目录说明

`src/api` 负责前端与服务端之间的通信，按照应用入口隔离 Admin 与 Chat 请求体系。
Admin 与 Chat 分别维护请求客户端和业务接口。

```text
src/api/
├── constants.ts                     # Admin 与 Chat 的 API base 路径常量
├── admin/
│   ├── file.ts                       # 通用文件上传、进度与取消
│   ├── auth/                         # Admin 登录认证与当前用户接口
│   │   └── types.ts                  # 认证 API 与认证 Store 共用类型
│   ├── core/                         # Admin 请求基础能力
│   │   ├── request.ts                # Axios 实例、HTTP 方法与统一响应解包
│   │   └── types.ts                  # Admin 请求协议类型
│   ├── system/                       # 系统管理业务接口
│   │   ├── chat-user/                # 对话用户、用户组及认证接口
│   │   ├── settings/                 # 登录认证、邮件与外观设置接口
│   │   ├── shared-resources/         # System 共享资源接口
│   │   └── <resource>.ts             # 其他 System 单资源接口
│   ├── workspace/                    # 工作空间业务接口
│   │   ├── conversation.ts           # 调试对话、历史会话与语音接口
│   │   ├── application/              # 智能体接口
│   │   ├── knowledge/                # 知识库接口
│   │   ├── model/                    # 模型接口
│   │   ├── trigger/                   # 触发器查询及维护接口
│   │   ├── tool/                     # 工具、工具工作流及工具商店接口
│   │   └── <resource>.ts             # 工作空间公共资源接口
│   └── provider.ts                   # Workspace 与 System 共用的模型供应商接口
├── chat/                             # Chat 独立请求体系
│   ├── core/request.ts               # JSON 与流式请求
│   ├── core/types.ts                 # Chat 请求协议类型
│   ├── file.ts                       # Chat 文件上传、进度与取消
│   ├── conversation.ts               # 正式对话、历史会话与语音接口
│   └── README.md                     # Chat API 边界说明
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

## 请求版本控制

除 `components/global/mk-infinite-scroll/index.vue` 的滚动加载外，未经用户明确要求，
不添加 `requestVersion`、请求序号、递增 ID、代次标记等用于忽略旧响应的请求版本控制，
也不通过改名或封装工具引入同类逻辑。普通请求直接维护数据、loading 和错误处理。

## 业务接口组织

`admin/system/chat-management/portal-setting.ts` 通过 Admin `/portal` 读取和局部保存门户配置，
公共类型维护在 `types/portal.ts`。JSON 用于访问开关和认证、跨域配置，门户名称与 Logo 使用
FormData；保存返回完整配置，页面以该返回值作为唯一数据来源。
认证配置保留未编辑字段，仅提交后端读取的 `login_value`、`max_attempts`、`failed_attempts`、
`lock_time`；跨域配置写入 `cross_domain_list`（对齐后端 `ApplicationApiKey.cross_domain_list`），
并保留 `cors_config` 中的其他字段。

- 业务 API 先按 Admin 入口下的 `auth`、`workspace`、`system` 等一级业务域归类。Workspace 和
  System 内部可继续按明确的功能域建立子目录，例如 `workspace/application/`、
  `workspace/tool/`、`system/chat-user/` 和 `system/settings/`；不需要分组的单资源接口直接放在
  所属一级业务域下。
- 一类资源的增删改查放在同一个最终资源文件中。调用方直接导入该文件，不为业务目录创建聚合
  入口，也不创建汇总所有业务接口的 `api.ts`。
- 工具基础信息和工具工作流使用后端不同资源接口：`workspace/tool/tool.ts` 维护工具增删改查，
  `workspace/tool/workflow.ts` 维护工具工作流的加载、保存、发布与调试。
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

### 当前账号密码

`admin/auth/current-user.ts` 的 `postCurrentUserPassword` 向 `/user/current/reset_password`
提交 RSA 加密的 `{ encryptedData }`。头像菜单的 `layout/avatar-dropdown/ChangePasswordDialog.vue`
负责新密码与确认密码校验、加密和提交，成功后清除本地登录凭据并跳转登录页。

### 四类特殊资源 API

`application`、`knowledge`、`model`、`tool` 是需要同时考虑 Workspace、System 资源管理和
System 共享资源的四类特殊资源。其接口按真实后端边界分别维护在 `admin/workspace/` 与
`admin/system/` 下，不把不同范围的 URL 合并为页面侧 API Map，也不让卡片或 Action 根据路由拼接
System 接口地址。

页面根据路由 `resourceScope` 选择当前范围的完整业务 API 对象，并将其传给需要请求的 Card
Action、Drawer 或 Dialog。复用方直接使用 `typeof XxxApi` 约束完整 API 对象；不要为每组 Action
额外维护逐方法接口，例如 `ModelActionApi`，也不要使用不断扩展的 `Pick<typeof XxxApi, ...>`。
完整 API 对象的方法集合不同时，共用组件使用完整对象类型的联合，例如
`typeof ModelApi | typeof SystemSharedModelApi`，不为凑齐类型添加其他范围不存在的接口。
仅展示数据的组件不接收 API。

### 工作流发布历史

`workspace/application/workflow.ts` 维护智能体 `application_version` 资源：
`getWorkflowVersions(applicationId)` 返回按创建时间倒序的完整 `WorkflowVersion[]`；
`putWorkflowVersion(applicationId, versionId, payload)` 编辑标题与更新说明，返回更新后的版本。
共用类型 `WorkflowVersion` 和 `WorkflowVersionPayload` 位于 `types/workflow-version.ts`，
通过 `@/api/types` 导出。`ButtonApplicationPublishHistory` 内部调用智能体版本 API，公共发布历史
UI 组件只接收数据和事件，不接收 API 或推测其他工作流的接口地址。
`workspace/tool/workflow.ts` 同时维护工具 `tool_version` 资源，提供
`getWorkflowVersions(toolId)` 和 `putWorkflowVersion(toolId, versionId, payload)`，
复用上述版本类型，由 `views/workflow/tool/ButtonPublishHistory.vue` 调用。
工具版本接口同样尚未支持 `description`，且未返回版本的默认模型配置。
`workspace/knowledge/workflow.ts` 维护知识库 `knowledge_version` 资源，提供同名查询与编辑方法，
由知识库 `ButtonPublishHistory.vue` 调用；知识库版本也尚未支持更新说明和默认模型配置。

v3 编辑表单提交 `{ name, description }`，标题上限 64、更新说明上限 1000。
当前仓库后端的版本编辑序列化器只处理 `name`，列表和详情也未返回 `description`；
更新说明的持久化与回显需要后端补齐，前端不将智能体自身的 `desc` 当作版本更新说明。

### 智能体模板中心

`admin/store.ts` 的 `getStoreApplicationList(query)` 查询智能体模板，直接返回
`ApplicationStoreResponse`，不再返回 `unknown`。公共模板元数据为 `api/types/workflow-template.ts` 的 `WorkflowStoreTemplate`，
智能体 `ApplicationStoreTemplate` 为其类型别名，响应结构仍由 `api/types/application.ts` 维护。
类型统一经 `@/api/types` 导入；各资源业务入口整理响应字段，公共 UI 不调用接口。
创建或覆盖工作流时通过已有智能体 API 提交 `work_flow_template`，成功后的刷新与导航由 View 负责。

### 模型选项查询

`workspace/model/model.ts` 的 `getModelListWithShared(query)` 请求
`/workspace/<workspaceId>/model_list`，支持 `name`、`model_type`、`model_name` 筛选。
将 `shared_model` 与 `model` 按共享在前的顺序合并为 `ModelItem[]`，分别标记
`source: 'shared'` 与 `source: 'workspace'`。`SelectModel` 的接口选项统一通过此方法查询，
工作流通过 Store 同名方法使用缓存或强制刷新。模型管理列表继续使用 `getModelList`。

### 工具列表查询

`workspace/tool/tool.ts` 的 `getAllTool(query)` 查询支持 `folder_id` 筛选的工作空间工具
非分页列表，用于文件夹菜单和工具选择弹窗。`getToolListWithShared(query)` 请求 `tool/tool_list`，
将响应的 `tools` 与 `shared_tools` 合并为 `ToolItem[]`，用于包含已授权共享工具的选项查询；
按工具类型筛选时使用 `tool_type`。`workspace/shared.ts` 的 `getAllTool(query)` 仅查询共享工具。

### 知识库维护

`getKnowledgeMcpConfig(knowledgeId)` 与 `postKnowledgeKeywordIndex(knowledgeId)` 为预留接口方法，
目前不发送 HTTP 请求：前者返回空配置文本，后者模拟成功。后续确认后端协议后替换方法内部实现。
MCP 入口加载配置后打开只读及复制弹窗；分词索引入口仅调用方法并在成功后提示“操作成功”。

`exportKnowledgeExcel`、`exportKnowledgeZip`、`exportKnowledge` 分别通过 GET 请求知识库
`/<knowledgeId>/export`、`export_zip`、`export_knowledge`，复用 `getExportFile` 下载。
三种结果分别为文档 Excel、包含图片的文档 ZIP 和可导入创建的知识库 ZIP；优先使用服务端文件名。

`postKnowledgeImport(file, folderId)` 将文件与 `folder_id` 组装为 FormData，POST 到
`/workspace/<workspaceId>/knowledge/import_knowledge`，响应为 `{ knowledge_id, type }`。
后端校验知识库导出包并创建资源；导入成功后的用户权限和列表刷新由调用页面负责。

`workspace/knowledge/knowledge.ts` 与 `workspace/shared.ts` 的 `getAllKnowledge(query)`
分别查询工作空间及共享知识库的非分页列表，返回 `KnowledgeItem[]`，用于关联知识库选择等
需要全量选项的场景。原有 `getKnowledgePage` 继续用于分页列表。

`workspace/knowledge/knowledge.ts` 的 `putKnowledge` 更新普通知识库，`putLarkKnowledge`
更新飞书知识库；单项转移提交 `folder_id`。`putBatchMoveKnowledge` 将知识库 ID 数组和目标目录
组装为 `{ id_list, folder_id }`，`putBatchDeleteKnowledge` 将 ID 数组组装为 `{ id_list }`，
分别使用 PUT 请求 `batch_move` 和 `batch_delete`。页面和 Action 负责类型判断及 loading。

`putReEmbeddingKnowledge` 使用 PUT 请求 `/<knowledgeId>/embedding` 重新向量化。
设置页更换向量模型时先确认、保存，再调用该接口；Web、飞书配置通过 `meta` 提交，保留未编辑的
已有配置，文件数量与大小限制仍作为知识库顶层字段提交。

知识库创建通过 `postKnowledge`、`postWebKnowledge` 分别提交到 `/base`、`/web`；
`postLarkKnowledge` 沿用飞书扩展接口 `/lark/save`，当前开源后端未包含该实现。
基础创建字段由 `KnowledgeCreatePayload` 统一维护，Web、飞书请求扩展对应类型；工作流创建
复用基础字段并附加 `work_flow` 及可选的 `KnowledgeWorkflowTemplate` 商店模板。
成功后的用户资料刷新、列表刷新和路由跳转由创建弹窗负责。

## 枚举与类型组织

`enums/state.ts` 的 `STATE_TYPES` 维护跨业务复用的任务状态，联合类型 `State` 定义在
`types/state.ts`。触发器及后续文件等业务直接引用公共状态，新增状态时保持已有接口值不变。

API 枚举与类型统一在 `src/api` 范围内管理，相关规则由本文档统一维护。

后端字段的固定枚举值放在 `src/api/enums/<domain>.ts`，使用 `as const` 对象声明，并通过
`src/api/enums/index.ts` 统一导出。业务代码统一从 `@/api/enums` 导入运行时枚举值，不直接
引用领域文件；不得重复使用裸字符串或另建同值常量。

`src/api/enums` 按明确业务域拆分文件，不创建收集无关枚举的通用文件。枚举的联合类型在对应的
`src/api/types/<domain>.ts` 中由枚举对象派生，并继续通过 `@/api/types` 对外提供。例如
`TOOL_TYPE` 从 `@/api/enums` 导入，`ToolType` 从 `@/api/types` 导入。

触发器参数来源、间隔单位和请求字段类型直接在对应接口字段中声明字符串联合类型，
不单独导出运行时枚举；表单选项使用对应字符串值。触发周期继续复用 `TRIGGER_SCHEDULE_TYPE`。

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
- loading 不作为业务 API 或 Admin、Chat 底层请求封装的参数；JSON 请求、文件上传和下载均遵循此规则。
  由调用接口的页面、组件或 Store 在请求前开启 loading，并在 Promise 的 `finally` 中释放，确保成功和失败都恢复状态。
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
`getTriggerTaskRecordPage` 按触发器查询执行记录，支持名称、状态、资源类型和执行时间排序；
`getTriggerTaskRecordDetails` 通过触发器、任务、记录 ID 查询执行详情，类型定义在 `api/types/trigger.ts`。
`putBatchActivateTrigger(ids, isActive)` 提交 `{ id_list, is_active }` 到 `batch_activate`；
`putBatchDeleteTrigger(ids)` 提交 `{ id_list }` 到 `batch_delete`。单项启停通过 `putTrigger`
仅提交 `is_active`。`Trigger` 为分页摘要，`TriggerDetail` 为含任务参数的完整详情；
`TriggerPayload` 用于新建和编辑，ID 在新建前生成以展示事件回调 URL。

### 资源触发器

`workspace/trigger/resource-trigger.ts` 独立维护工具、智能体资源端的触发器列表、详情、新建、编辑和移除。
接口前缀为 `/workspace/<workspaceId>/<sourceType>/<sourceId>/trigger`，资源类型使用
`RESOURCE_TYPE.TOOL` / `RESOURCE_TYPE.APPLICATION` 的后端值；工作空间从资源上下文显式传入。
`ResourceTriggerResource`、`ResourceTrigger`、`ResourceTriggerDetail` 定义在 `types/trigger.ts`。
详情的 `trigger_task` 是单对象，普通触发器详情是数组，调用表单负责统一结构。
新建提交含一个固定任务的 `TriggerPayload`；资源编辑只更新当前资源任务的参数和 meta，保留其他任务，
名称和周期等配置仍属于整个触发器。移除删除当前资源任务，最后一个任务移除后删除触发器。
列表沿用后端仅返回已启用触发器的行为，loading 由调用组件维护。

### 知识库工作流

`workspace/knowledge/knowledge.ts` 的 `getKnowledgeDetail` 返回 `KnowledgeDetail`，包含知识库
名称、所属目录，以及工作流类型的 `work_flow` 和发布状态；进入画布只调用此详情接口加载。
`workspace/knowledge/workflow.ts` 维护保存和发布，保存提交 `work_flow`，响应使用
`KnowledgeWorkflowDetail`。前端详情与保存协议的 `default_model_setting` 复用
`DefaultModelSettingPayload`；服务端需支持该字段的持久化与回传（当前仓库知识库后端尚未实现）。

### 智能体复制

`ApplicationDetail` 复用 `ApplicationFormPayload` 中的配置字段，并保留详情接口的 `model`
和可空描述。复制通过 `getApplicationDetail` 获取完整配置，将 `model` 映射为 `model_id`，
再调用 `postApplication` 创建副本；不使用卡片列表摘要作为复制数据。

### 工具执行记录

`workspace/tool/workflow.ts` 的 `getToolExecutionRecordPage` 查询 `/<toolId>/tool_record/<currentPage>/<pageSize>`，
支持 `source_name`、`source_type`、`state` 筛选，后端固定按创建时间倒序返回。
`getToolExecutionRecordDetail` 查询 `/<toolId>/tool_record/<recordId>`，返回状态、耗时和 `meta` 中的输入、输出、
错误及节点详情。共用类型 `ToolExecutionRecord`、`ToolExecutionRecordDetail` 维护在 `types/tool.ts`；
调用来源使用 `TOOL_RECORD_SOURCE`。抽屉负责 loading 和分页状态，不重复解包响应。

### 知识库执行记录

`workspace/knowledge/workflow.ts` 集中维护工作流、发布版本和执行记录接口。
`getKnowledgeExecutionRecordPage` 请求 `/<knowledgeId>/action/<currentPage>/<pageSize>`，
支持 `user_name`、`state` 筛选；详情和取消复用 `getKnowledgeWorkflowAction`、
`postCancelKnowledgeWorkflowAction`，对应 GET `action/<actionId>` 和 POST `action/<actionId>/cancel`。
`KnowledgeExecutionRecord` 为分页摘要，`KnowledgeWorkflowAction` 扩展节点详情；均从 `@/api/types` 导入。

### 工具工作流调试

`workspace/tool/workflow.ts` 的 `postToolWorkflowDebug(toolId, parameters)` 使用 Admin `postStream`
请求 `/<toolId>/debug`，返回原始 SSE Response；输入参数来自工具基础节点，`chat_record_id` 用于识别
执行记录，表单续跑沿用该 ID 并传入 `position`。`getToolWorkflowRecord(toolId, recordId)` 查询
`/<toolId>/tool_record/<recordId>`，返回 `ToolWorkflowRecord` 的运行状态、输出及节点详情。
工具调试读取服务端已保存工作流，画布页面在调试前保存未提交改动。

### 工具工作流模板中心

`admin/store.ts` 的 `getStoreToolWorkflowList(query)` 查询 `/workspace/store/tool_workflow_template`，
返回 `ToolWorkflowStoreResponse`，其中 `apps` 复用 `WorkflowStoreTemplate[]`。
`workspace/tool/workflow.ts` 的 `putToolWorkflow` 支持两种互斥载荷：保存 `work_flow` 与默认模型设置，
或提交 `work_flow_template` 由服务端下载并覆盖当前工具工作流。模板覆盖后由 View 重新查询详情，
同步默认模型设置、保存时间和图快照；确认取消或请求失败不关闭模板中心。

### 知识库工作流模板与导出

`admin/store.ts` 的 `getStoreKnowledgeList(query)` 查询 `/workspace/store/knowledge_template`，
返回 `KnowledgeWorkflowStoreResponse`，其中 `apps` 使用公共 `WorkflowStoreTemplate[]`。
`putKnowledgeWorkflow` 接受互斥的 `work_flow` 保存载荷或 `work_flow_template` 覆盖载荷，覆盖成功后由 View 重载详情。
`exportKnowledgeWorkflow(knowledgeId, name)` 通过 GET `/<knowledgeId>/workflow/export` 下载 `.kbwf` 文件，
只导出工作流，不调用包含文档的知识库包导出接口。

### 工作空间首页

`admin/workspace/homepage.ts` 维护 `/workspace/<workspaceId>/homepage` 的四类资源汇总、
每日趋势、三类排行分页、Tokens／对话总量及三类导出。每个接口均以必填的 `workspaceId` 为首个参数，
由调用方显式传入，API 文件不再自行读取当前路由。
资源汇总、日期范围、趋势及排行记录类型在 `types/homepage.ts`，统一从 `@/api/types` 导入。
`getRanking` 与 `exportRanking` 通过 `HomeRankingKind` 选择后端排行路径，名称及起止日期
筛选保持一致；分页使用 `ParamsPage` 与 `ResponsePage`。导出沿用 `getExportFile`。
工作空间总量接口返回数值，不与 System 首页的对象响应混用。

### 对话面板接口

`admin/workspace/conversation.ts` 集中维护调试对话的打开、发送、取消、续传、历史会话、
记录分页、删除、修改和语音识别接口，保留可选 `applicationId` 对历史资源范围的选择。
其中 `postSpeechToText(applicationId, data)` 请求指定智能体的
`/workspace/<workspaceId>/application/<applicationId>/speech_to_text`，loading 由调用方管理。
`chat/conversation.ts` 维护正式对话对应的接口。两者使用各自 `core/request.ts` 的请求方法；
`postStream` 返回原始 `Response`，由 `conversation-panel/stream.ts` 解析。

面板内部的 `conversation-panel/common/get-api.ts` 通过 `ChatType` 选择完整 API 对象，
仅负责模式判断，不声明 URL 或发送请求；固定模式的 Store 直接导入对应业务 API。
面板模式值统一维护在 `conversation-panel/common/enums.ts` 的 `CHAT_TYPE`，
`common/types.ts` 中的 `ChatType` 从该对象派生。

### 通用文件上传

`admin/file.ts` 与 `chat/file.ts` 分别提供 `postUploadFile(file, sourceId, sourceType, onProgress?)`，
通过各自请求客户端向 `/oss/file` 提交 FormData 的 `file`、`source_id` 和 `source_type`。
返回值统一为 `{ request, abort }`，`request` 解包得到文件地址，`abort()` 中断客户端请求。
普通上传直接等待 `request`，需要进度时传入 `(percent, event)`；只有能获取上传总量时才回调
0–100 的百分比，100 表示请求体已上传，不代表服务端处理成功，完成状态以 `request` 为准。
取消时 Promise 仍拒绝，由调用方处理状态，请求层不弹出通用错误提示；loading 由调用方在
`finally` 中恢复。

资源类型使用 `@/api/enums` 的 `FILE_SOURCE_TYPE` 与 `@/api/types` 的 `FileSourceType`，
包括知识库、智能体、工具、文档、对话及三种临时文件有效期。对话 Store 使用
`FILE_SOURCE_TYPE.CHAT` 调用对应 File API，对话 API 不再维护上传接口。
