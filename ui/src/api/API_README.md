# API 目录说明

`src/api` 负责前端与服务端之间的通信，按照应用入口隔离 Admin 与 Chat 请求体系。
Admin 与 Chat 分别维护请求客户端和业务接口。

## 目录职责

| 位置                            | 职责                                                             |
| ------------------------------- | ---------------------------------------------------------------- |
| `constants.ts`                  | Admin／Chat API base 路径                                        |
| `admin/core/`、`chat/core/`     | 各入口请求客户端与传输协议                                       |
| `admin/auth/`                   | Admin 认证及当前账号                                             |
| `admin/workspace/`              | Workspace 资源及业务接口                                         |
| `admin/workspace/shared/`       | 工作空间可用的共享资源查询                                       |
| `admin/system/`                 | 系统管理、资源管理、共享资源及设置                               |
| `admin/model-provider.ts`       | 公共模型供应商查询                                               |
| `admin/file.ts`、`chat/file.ts` | 各入口文件请求                                                   |
| `chat/`                         | 正式对话、门户、认证和对话用户；见 [Chat README](chat/README.md) |
| `enums/`、`types/`              | 后端枚举／跨 API 与 UI 共用业务类型，各自由 index.ts 对外导出    |

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

- 业务 API 先按 Admin 入口下的 `auth`、`workspace`、`system` 等一级业务域归类。Workspace 和
  System 内部可继续按明确的功能域建立子目录，例如 `workspace/application/`、
  `workspace/tool/`、`system/chat-management/` 和 `system/settings/`；不需要分组的单资源接口直接放在
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

系统登录设置的 `system_options` 仅用于登录方式选项，默认登录方式从已选 `login_methods` 中选择。
保存仅提交 `login_methods`、`default_value`、`max_attempts`、`failed_attempts`、`lock_time`、
`role_id`、`workspace_id` 和 `permission`，不透传查询响应中的选项或 `group_id`。

## 枚举与类型组织

`enums/state.ts` 的 `STATE_TYPES` 维护跨业务复用的任务状态，联合类型 `State` 定义在
`types/state.ts`。触发器及工具／知识库执行记录引用公共状态；文档任务使用 DOCUMENT_TASK_STATE，新增状态时保持已有接口值不变。

API 枚举与类型统一在 `src/api` 范围内管理，相关规则由本文档统一维护。

后端字段的固定枚举值放在 `src/api/enums/<domain>.ts`，使用 `as const` 对象声明，并通过
`src/api/enums/index.ts` 统一导出。业务代码统一从 `@/api/enums` 导入运行时枚举值，不直接
引用领域文件；不得重复使用裸字符串或另建同值常量。

`src/api/enums` 按明确业务域拆分文件，不创建收集无关枚举的通用文件。枚举的联合类型在对应的
`src/api/types/<domain>.ts` 中由枚举对象派生，并继续通过 `@/api/types` 对外提供。例如
`TOOL_TYPE` 从 `@/api/enums` 导入，`ToolType` 从 `@/api/types` 导入。

触发器参数来源、间隔单位和请求字段类型直接在对应接口字段中声明字符串联合类型，
不单独导出运行时枚举；表单选项使用对应字符串值。触发周期继续复用 `SCHEDULE_TYPE`。

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
  `Dict<unknown>`，不为相同结构声明额外别名。
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
  `downloadRequest` 的第五个参数可指定回退文件名，缺省为 `download`；服务端文件名始终优先。
- 业务代码通过 `api.method().then(...)` 处理接口成功后的状态变化；通用接口错误由请求层统一
  提示，不在调用处重复使用 `try/catch` 或 `.catch()` 提示相同错误。只有业务降级、状态恢复等
  非提示类失败处理可以按需保留失败分支。
- Admin token、公开档案和语言由 `stores/admin/` 管理；请求层使用该入口的 `useStore()`，401 清理凭据并跳转登录。
  Chat 使用 `stores/chat/`，认证和重新认证见 [Chat README](chat/README.md)。
- loading 不作为业务 API 或 Admin、Chat 底层请求封装的参数；JSON 请求、文件上传和下载均遵循此规则。
  由调用接口的页面、组件或 Store 在请求前开启 loading，并在 Promise 的 `finally` 中释放，确保成功和失败都恢复状态。
- 流式 POST 请求使用 `postStream` 返回原始 `Response`，由业务组件按具体协议解析数据块；
  参数顺序为 `postStream(base, path, data?, config?)`，`config.signal` 用于取消请求。
  鉴权、语言请求头和错误状态仍由请求基础设施统一处理。
- 上传、下载和其他特殊请求在真实需求出现时独立设计，不提前塞入普通 JSON 请求客户端。

## 业务协议与范围差异

以下只登记跨层协议、容易混淆的参数和真实能力差异；逐项函数签名以对应 API 源码及 JSDoc 为准。
页面流程见 [VIEW_README.md](../views/VIEW_README.md)，共享组件用法见组件文档。

### 门户配置

`admin/system/chat-management/portal-setting.ts` 通过 Admin `/portal` 读取和局部保存门户配置，
公共类型维护在 `types/portal.ts`。JSON 用于访问开关和认证、跨域配置，门户名称与 Logo 使用
FormData；保存返回完整配置，页面以该返回值作为唯一数据来源。
认证设置的登录方式选项来自 `auth_config.system_options`，默认登录方式从草稿已选的 `login_value`
中选择。认证配置仅提交 `login_value`、`type`、`max_attempts`、`failed_attempts`、`lock_time`，
不透传查询响应中的选项；跨域地址提交 `cross_domain_list` 数组，不另建 `cors_config`。

### 当前账号密码

`admin/auth/current-user.ts` 的 postCurrentUserPassword 向 `/user/current/reset_password`
提交 RSA 加密的 `{ encryptedData }`；调用方校验与加密，成功清除凭据后进入登录。

### 系统用户列表排序

系统用户分页排序以 `order_by` 传入 `create_time`；对话用户分页传入 `create_time` 或 `used_tokens`，
后者从列字段 `token_quota.used_tokens` 映射。升序使用字段原名，降序添加 `-`，取消排序不传值。
排序由服务端处理，不做前端当前页排序。

### 操作日志排序

操作日志列表与导出共用查询条件，操作时间排序通过 `order_by` 传入 `create_time` 或 `-create_time`，
取消排序不传值。

### 平台许可证

`admin/system/license.ts` 通过 GET、PUT `/license/profile` 查询和更新授权信息，
更新使用 FormData 的 `license_file` 字段。`LicenseProfile` 与 `LicenseInfo` 从 `@/api/types`
导入，查询结果直接读取 `license`。关于弹窗仅商业版本查询授权，更新入口沿用系统许可证权限；
更新成功后重新查询展示，关闭弹窗时刷新页面以应用授权与权限。

### 四类特殊资源 API

根据资源范围或业务上下文选择出的 API 对象统一命名为 `requestApi`，包括 `computed` 结果和
局部变量，不使用 `toolApi`、`authorizationApi` 或 `request` 等名称。同一作用域确需同时使用
多套 API 时，以 `request` 为前缀加业务名区分，例如 `requestModelApi`、`requestToolApi`。
知识库详情上下文的多模块接口入口使用 `resourceApi.knowledge / scheduledSync`，通过响应式 getter
读取当前范围，无需 `.value`；方法内选定单个接口对象时仍命名为 `requestApi`。
文档分段详情通过 `views/document-detail/context.ts` 装配四种范围的
`resourceApi.document / paragraph`，保留完整 API 对象及真实方法差异，不补造共享写入方法。
直接导入的 API 保持 PascalCase 命名；请求返回的 Promise 不属于此命名规则。

`application`、`knowledge`、`model`、`tool` 是需要同时考虑 Workspace 普通资源、Workspace 共享资源、System 资源管理和
System 共享资源的四类特殊资源。其接口按真实后端边界分别维护在 `admin/workspace/` 与
`admin/system/` 下，不把不同范围的 URL 合并为页面侧 API Map，也不让卡片或 Action 根据路由拼接
System 接口地址。

页面根据路由 `resourceScope` 选择当前范围的完整业务 API 对象；知识库详情由功能本地
`views/knowledge-detail/context.ts` 集中装配，由详情入口及 setting、library、对话用户子页复用该选择。缺失设置 API 模块保持未提供，
不回退其他资源范围。页面将选定对象传给需要请求的 Card
Action、Drawer 或 Dialog。复用方直接使用 `typeof XxxApi` 约束完整 API 对象；不要为每组 Action
额外维护逐方法接口，例如 `ModelActionApi`，也不要使用不断扩展的 `Pick<typeof XxxApi, ...>`。
完整 API 对象的方法集合不同时，共用组件使用完整对象类型的联合，例如
`typeof ModelApi | typeof SystemSharedModelApi`，不为凑齐类型添加其他范围不存在的接口。
仅展示数据的组件不接收 API。

### 版本与模板

智能体、工具、知识库 Workflow API 分别维护 application_version、tool_version、knowledge_version，
使用同名 getWorkflowVersions／putWorkflowVersion，类型为 WorkflowVersion／WorkflowVersionPayload。
前端版本标题上限 64、更新说明上限 1000，提交字段为 name、publish_desc，
不将资源 desc 当作版本说明。智能体和工具后端已支持 publish_desc；知识库版本当前只处理 name。
智能体与工具的 putXxxPublish 提交 publish_name、publish_desc，由发布弹框填写。
三个版本列表均未返回历史默认模型配置，预览与恢复保留当前配置。

`admin/store.ts` 的 getStoreApplicationList、getStoreToolWorkflowList、getStoreKnowledgeList 查询三类模板，
共用 WorkflowStoreTemplate 元数据，各响应类型保留本领域结构。工作流保存 work_flow 与覆盖 work_flow_template
是互斥载荷；覆盖成功后重新查询详情，不把模板响应直接当图数据。知识库创建使用 Knowledge API，画布使用 Workflow API。

### 模型选项查询

`model-provider.ts` 的 `getProviderList(query?)` 统一查询 `GET /provider`；不传参数获取全部供应商，
传入 `{ model_type }` 筛选支持指定模型类型的供应商，不单独封装按类型查询方法。

`workspace/model.ts` 的 `getModelListWithShared(query)` 请求
`/workspace/<workspaceId>/model_list`，支持 `name`、`model_type`、`model_name` 筛选。
将 `shared_model` 与 `model` 按共享在前的顺序合并为 `ModelItem[]`，分别标记
`source: 'shared'` 与 `source: 'workspace'`。`SelectModel` 的接口选项统一通过此方法查询，
工作流通过 Store 同名方法使用缓存或强制刷新。模型管理列表继续使用 `getModelList`。

`system/shared-resources/model.ts` 同样提供 `getModelListWithShared(query)`，沿用
`/system/shared/model` 查询共享模型，为每项标记 `source: 'shared'`；不查询工作空间模型。
共享工作流、代码生成和默认模型设置统一调用此方法，模型管理继续使用 `getModelList`。

### 资源选择查询

知识库／智能体／工具选择使用各范围的 getAllKnowledge、getAllApplication、getAllTool 全量查询。
System 不传 Workspace 文件夹条件；System 共享不提供智能体选择。
弹窗的范围和交互见 [组件文档](../components/COMPONENT_README.md#selectapplicationdialogselecttooldialog)。

### 工具列表查询

`workspace/tool/tool.ts` 的 `getAllTool(query)` 查询支持 `folder_id` 筛选的工作空间工具
非分页列表，用于文件夹菜单和工具选择弹窗。`getToolListWithShared(query)` 请求 `tool/tool_list`，
将响应的 `tools` 与 `shared_tools` 合并为 `ToolItem[]`，用于包含已授权共享工具的选项查询；
按工具类型筛选时使用 `tool_type`。`workspace/shared/tool.ts` 的 `getAllTool(query)` 仅查询共享工具。

### System 共享资源工作空间授权

`system/shared-resources/authorization.ts` 通过 GET、POST
`/system/shared/<knowledge|model|tool>/<resourceId>/authorization` 查询和保存工作空间授权，
沿用 v2 System 共享授权协议，依赖部署端提供对应接口。配置类型为 `SharedWorkspaceAuthorization`，
包含 `authentication_type`（`WHITE_LIST`／`BLACK_LIST`）和 `workspace_id_list`；请求层直接解包配置。
弹窗通过 System Workspace API 查询工作空间，不读取路由中的工作空间 ID。

### System 共享工具

`system/shared-resources/tool/tool.ts` 使用 `/system/shared/tool`，维护分页、详情、创建、更新、删除、
导入导出、连接测试、代码检查与调试、Skill 上传下载。路径沿用 v2 System 共享工具协议。
共享工具 API 不提供工作空间文件夹移动或批量接口；复用卡片、Action 和表单接收完整 Workspace
与 System 共享 API 的联合类型，不补造接口以匹配 Workspace 方法集合。

### 知识库召回测试

Workspace、System 资源管理和 System 共享资源均在各自 `knowledge/knowledge.ts` 中提供
`postKnowledgeHitTest(knowledgeId, payload)`，向知识库的 `/hit_test` 提交 POST，直接返回命中分段数组。
请求使用 `KnowledgeHitTestPayload`，包含 `query_text`、`image_list`、`top_number`、`similarity` 和
`search_mode`；检索模式复用 `KNOWLEDGE_SEARCH_MODE`。文本和图片至少提供一项，图片仅支持向量或混合检索。
结果使用 `KnowledgeHitTestResult`，保留分段、得分及图片命中信息。Workspace 共享暂无对应接口，不回退其他范围。
向量标签依据 `hit_unit_type`（`KNOWLEDGE_HIT_UNIT_TYPE`）：`image` 显示“图片向量”，`text` 显示“文本向量”，图片描述命中也属于文本向量。
`document_resource_type` 表示来源文档类型，`document_image_id` 用于展示图片文档原图，不用于判断命中向量类型。
`query_unit_type` 表示产生该命中的查询输入类型，与 `hit_unit_type` 分别描述查询端和命中端。

### System 共享知识库

`system/shared-resources/knowledge/knowledge.ts` 使用 `/system/shared/knowledge`，维护分页、详情、
通用 / Web / 飞书 / 工作流创建、导入、删除、重新向量化、Web 同步、关联问题、分词索引、MCP
配置与三种导出。工作流创建在 Workspace 与 System 共享范围均由同一个 Knowledge API 的
`postKnowledgeWorkflow` 提交；工作流转换由各范围的 `knowledge.ts` 维护，
`workspace/knowledge/workflow.ts` 仅维护已创建知识库的画布接口。System 共享范围没有工作空间文件夹、批量接口或独立的知识库工作流 API 文件。复用创建入口
和卡片 Action 时使用完整 Workspace / System 资源管理 / System 共享知识库 API 的联合类型，由页面显式传入当前范围的 API。

### 工具代码生成

三套 `tool/tool.ts` 的 postToolGenerateCode 向各范围 `/tool/generate_code` 提交
ToolGenerateCodePayload，无需已创建资源 ID。类型在 types/tool.ts，返回原始 SSE Response。
流式消费与生成 UI 见 GenerateContent 组件，业务表单负责模型、参数和载荷。

### 系统提示词生成

Workspace、System 资源管理和 System 共享资源均把 `postPromptGenerate(modelId, payload)` 放在对应范围的
`model.ts`，请求结构共用 `PromptGeneratePayload`（含 `model_params_setting`）。
路径为 `/workspace/<workspaceId>/model/<modelId>/prompt_generate` 与 `/system/model/<modelId>/prompt_generate`，
System 接口不依赖工作空间 ID。
均返回原始 SSE Response，由公共生成组件读取。画布的 `PromptGenerate` 通过
`useWorkflowStore(resourceScope).postPromptGenerate` 调用；三个范围的 Store 适配器分别引用对应的
Model API，直接转发生成请求，不使用查询缓存或请求去重。

### 流式补全

Workspace、System 资源管理和 System 共享资源均在对应范围的 `model.ts` 提供
`postChatCompletion(modelId, payload, signal)`，请求结构为 `ChatCompletionPayload`（OpenAI 格式的 messages 与 tools）。
路径为 `/workspace/<workspaceId>/model/<modelId>/chat_completion`、`/system/resource/model/<modelId>/chat_completion` 与
`/system/shared/model/<modelId>/chat_completion`；当前后端仅实现 Workspace 接口，System 接口需部署提供对应扩展。
均返回原始 SSE Response，事件为 `delta`、`reasoning`、`tool_call`、`completion` 与 `error`；`signal` 用于中止在途请求，
`postStream` 的第四个可选参数透传给 `fetch`。工作流 AI 生成通过 `useWorkflowStore(resourceScope).postChatCompletion` 调用，
Store 直接转发，不缓存或去重。

### 知识库维护

Workspace、System 资源管理、System 共享各自的 knowledge.ts 保留真实能力，Workspace 共享只查询。
知识库生成问题 PUT `/<id>/generate_related`，配置为 RelatedQuestionsConfig + state_list；文档生成
PUT `/<id>/document/batch_generate_related`，单项也传 document_id_list，不改成分段协议。

getKnowledgeMcpConfig 查询 external_service 并格式化 mcp_config；putKnowledgeKeywordIndex PUT tokenize 提交索引。
exportKnowledgeExcel、exportKnowledgeZip、exportKnowledge 下载文档 Excel、带图片文档 ZIP、可导入知识库 ZIP；
exportKnowledge 第三个参数为 withSourceFile，通过查询参数 with_source_file 传入是否包含源文件。
postKnowledgeImport 以 FormData file、folder_id 上传，响应 knowledge_id、type。

putKnowledge 更新通用字段，Workspace 飞书使用 putLarkKnowledge；移动传 folder_id，批量移动／删除传 id_list。
更换向量模型保存后通过 putReEmbeddingKnowledge 提交 embedding。Web 同步的 sync_type 为 incremental／replace／complete，
不自行改写协议值。Web doc_strategy 使用 DocumentStrategy，顶层详情可为 null，保存不立即同步。

postTransformWorkflow POST `/<id>/transform_workflow`，提交 `{ work_flow }`，保留已有文档；不能用工作流保存接口代替。
知识库 Workflow API 通过 getKnowledgeDetail 的 work_flow 加载，putKnowledgeWorkflow 保存，发布接口单独调用。
默认模型协议使用 DefaultModelSettingPayload，知识库后端已保存 default_model_setting 并在详情回传。

导入／导出工作流专用 `.kbwf`，接口为 workflow/import（FormData file）与 workflow/export，
不能使用包含文档的知识库包接口。正式文档执行用 upload_document，调试用 debug，复用 KnowledgeWorkflowDebugPayload。
知识库工作流 View 当前仍直接使用 Workspace Knowledge／Workflow API，其他来源仅有导航入口。

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
`ResourceAuthorizationDrawer` 内部通过 `isSystemResource()` 选择完整的用户授权
API 对象和工作空间上下文，作为该抽屉的范围选择例外。System 用户组查询／保存已提供，路径在同前缀下为
`user_group_resource/<target>/resource/<resource>`，两种授权均使用当前范围 API。

### 关联资源

`admin/workspace/related-resources.ts` 维护关联资源查询：
`getUsingResources` 查询当前资源依赖的资源，对应后端 `mapping_resource`；
`getUsedByResources` 查询引用当前资源的资源，对应后端 `resource_mapping`。
前端按关联资源语义命名，后端接口路径保持不变。方法接收资源类型、资源 ID、`ParamsPage`
和查询参数；Workspace 接口内部通过 `getWorkspaceId()` 读取当前路由工作空间，调用方不传工作空间 ID。返回 `ResponsePage<RelatedResource>`，
不传 loading，不重复解包响应。`RelatedResource` 通过 `@/api/types` 导出，保留
`source_*`、`target_*` 字段。依赖查询按 `target_type` 筛选，被依赖查询按 `source_type`
筛选，类型数组沿用请求层的数组序列化。页面负责按资源范围传入完整 API。

`system/shared-resources/related-resources.ts` 沿用 v2 `/system/shared/resource_mapping` 和
`/system/shared/mapping_resource`，方法只接收资源类型、资源 ID、分页和查询条件，不接收
`workspaceId`。工作空间筛选继续通过 `query.workspace_ids` 传入；两类 API 使用相同参数签名，抽屉直接调用页面传入的完整 API。

### 触发器与执行记录

- `workspace/trigger/trigger.ts` 提供普通触发器维护、记录分页与详情，Trigger 为摘要，TriggerDetail 含完整任务，
  TriggerPayload 新建前生成 ID。批量启停传 `{ id_list, is_active }`，批量删除传 `{ id_list }`，单项启停仅提交 is_active。
- `workspace/trigger/resource-trigger.ts` 前缀为 `/workspace/<workspaceId>/<sourceType>/<sourceId>/trigger`，
  workspaceId 从资源显式传入，sourceType 使用 RESOURCE_TYPE。资源详情 trigger_task 是对象，普通详情为数组。
  资源编辑保留其他任务，移除仅删除当前关联，最后任务移除后删除触发器；列表只返回启用触发器。
- 工具 Workflow API 记录为 `/<toolId>/tool_record/<page>/<size>` 及 `/<recordId>`，
  查询 source_name、source_type、state，返回 ToolExecutionRecord／ToolExecutionRecordDetail，按创建时间倒序。
  调试 POST debug 返回 SSE，chat_record_id 与 position 用于续跑，详情复用记录接口，不重复封装调试查询。
- 知识库 Workflow API 记录为 `/<id>/action/<page>/<size>`，筛选 user_name、state；
  详情和取消为 GET action/<actionId>、POST action/<actionId>/cancel。
- 智能体复制查询完整 ApplicationDetail，model 映射 model_id 后创建，不使用卡片摘要。
- Workspace 与 System 资源管理的 Application API 通过 `putApplicationPortalUp(applicationId)` 与
  `putApplicationPortalDown(applicationId)` 分别向各自范围的 `application/<applicationId>/portal_up`、
  `application/<applicationId>/portal_down` 发送 PUT 请求（上下架接口与通用编辑接口分离），返回 `ApplicationDetail`。
  上架仅允许已发布（`is_publish`）的智能体；上下架分别受门户上架/下架权限控制。
  `exportApplicationSkills(applicationId, applicationName)` 仍为本地 mock，返回 `{ application_id, name }`，
  不发送请求或生成 Skills 文件，真实下载接口待接入。

### 智能体概览

Workspace 与 System 资源管理的 `application/application.ts` 提供 `getAccessToken(applicationId)`，
沿用 V2 的 `/<applicationId>/access_token` GET 接口，返回公开访问凭证 `ApplicationAccessToken`。
概览使用 `access_token` 拼接 Web 链接，不使用智能体 ID 或 API Key 替代；API 文档地址使用 Chat 部署前缀。
两范围的 `putAccessToken` 向同一路径提交 `{ access_token_reset: true }` 重置链接，或 `{ is_active: boolean }` 修改 Web 访问状态；
载荷复用 `ApplicationAccessTokenPayload`，使用返回的访问凭证与启用状态回显，不二次查询。
后端 API 访问状态读取同次 GET 返回的 `enable_api_key`，两范围通过 `putEnableApiKey` 向各自
`/<applicationId>/enable_api_key` 发送 PUT，仅提交 `{ enable_api_key: boolean }`，ID 由 URL 传递。
返回 `workspace_id`、`application_id` 与 `enable_api_key`，用于保存后回显；该开关独立于 Web 访问和单个密钥启停。
Workspace 后台已提供此接口；System 路径按资源管理前缀接入，当前仓库无对应后台路由，需部署环境联调确认。
访问限制复用上述 GET／PUT，读取与保存 `access_num`、`white_active`、`white_list`、`authentication` 和
`authentication_value`。提问次数为 0～10000000 的整数；社区版仅编辑认证开关，保留已有 `authentication_value`，
不生成登录配置字段，身份认证读写待后台联调。Xpack 版认证配置使用 `type: 'login'`、`login_value`、
`max_attempts`，保留原配置中的其他字段；已有认证 `type` 不自动转换，缺省为 `login`。
保存访问限制携带原 `language`，避免后台省略字段时清空语言配置。
默认登录方式与账号锁定暂按 `authentication_value.default_value / failed_attempts / lock_time` 提交，
字段及认证配置生效能力待后台联调；前端不因认证字段缺失禁用编辑。System 资源管理的访问限制仍需部署环境联调。
Xpack 版可用登录方式统一调用 `system/chat-management/chat-user-auth.ts` 的 `getChatUserAuthType`，
GET `/chat_user/auth/types` 返回 `{ label, value }[]`，两种智能体入口共用。

社区版展示设置通过 `putAccessToken` 提交 `language`、`show_source` 与 `show_exec`，不调用 `/setting`。
Xpack 展示设置共用 `ApplicationDisplaySetting`；`ApplicationAccessToken` 兼容可选展示字段，缺失字段由弹窗补齐默认值。
两范围的 `putDisplaySetting` 沿用 V2 的 `/<applicationId>/setting` PUT 接口，提交 FormData：
`custom_theme`、`float_location` 序列化为 JSON，图片字段提交本次文件，`<field>_url` 保留已有地址；
恢复默认时图片文件与地址均提交空字符串。当前社区版后端未提供该路由，完整保存依赖支持此接口的部署。

API Key 按三个入口分别维护：

- `admin/workspace/application/api-key.ts`：`/workspace/<workspaceId>/application/<applicationId>/application_key`。
- `admin/system/resource-management/application/api-key.ts`：`/system/resource/application/<applicationId>/application_key`。
- `admin/system/api-key.ts`：`/system/api_key`，仅用于头像菜单。

三套均提供 `getApiKeyPage`、`postApiKey`、`putApiKey`、`deleteApiKey`；
两套智能体方法以 `applicationId` 为首参，仅 Workspace 接口在内部读取工作空间 ID；头像菜单接口不接收资源 ID。
分页使用 `ParamsPage` 和 `ResponsePage<ApiKeyRecord>`；创建 POST 空对象，由后端生成密钥；
修改只提交需要更新的配置，启停仅提交 `is_active`。Workspace 智能体删除返回空数据，其他两套沿用 V2 布尔类型；调用方不依赖返回值判断成功。
共用业务类型在 `types/api-key.ts`，`remark` 字段待后端补充返回与持久化；
两套系统接口沿用 V2 路径，仍需对应部署联调；头像菜单密钥与系统资源管理智能体密钥不能互相替代。

Workspace 与 System 资源管理的 `application/overview.ts` 独立维护概览接口，资源前缀分别为
`/workspace/<workspaceId>/application/<applicationId>` 与 `/system/resource/application/<applicationId>`。
`getMonitoring(workspaceId, range, applicationId)` 继续请求 `/application_stats`，返回 `HomeMonitoringDay[]`。

用户排行按首页协议预接入，以下分页、汇总及导出约定待后台实现，两套 API 均保留 TODO：

| 方法 | GET 路径（相对资源前缀） | 返回 |
| ---- | ----------------------- | ---- |
| `getRanking` | `/application_token_usage/<currentPage>/<pageSize>` 或 `/top_questions/<currentPage>/<pageSize>` | `ResponsePage<HomeRankingRecord>` |
| `getTokensAggregation` | `/tokens/aggregation` | 数值 |
| `getChatRecordAggregation` | `/chat_record/aggregation` | 数值 |
| `exportRanking` | `/application_token_usage/export` 或 `/top_questions/export` | Excel 文件 |

排行类型 `ApplicationRankingKind` 为 `userTokens`／`questions`，两者均按用户统计，分别按 Tokens／对话次数降序。
分页返回 `records`、`total`、`current`、`size`；记录沿用首页字段，需提供唯一 `chat_user_id`、
`asker.username`、`total_tokens`、`chat_record_count`。均 Tokens/次由前端计算，不按用户名拼接两个接口。
所有查询传入 `start_time`、`end_time`，分页和导出额外支持 `name`；汇总返回当前智能体同期总量，不受用户名搜索影响。
导出不传分页参数，返回全部匹配记录。TOP5 请求第一页 5 条，详情默认每页 20 条；不使用旧全量数组做前端分页。

### 工作空间首页

`admin/workspace/homepage.ts` 维护 `/workspace/<workspaceId>/homepage` 的四类资源汇总、
每日趋势、三类排行分页、Tokens／对话总量及三类导出。每个接口均以必填的 `workspaceId` 为首个参数，
由调用方显式传入，API 文件不再自行读取当前路由。
资源汇总、日期范围、趋势及排行记录类型在 `types/homepage.ts`，统一从 `@/api/types` 导入。
`getRanking` 与 `exportRanking` 通过 `HomeRankingKind` 选择后端排行路径，名称及起止日期
筛选保持一致；分页使用 `ParamsPage` 与 `ResponsePage`。导出沿用 `getExportFile`。
工作空间总量接口返回数值，不与 System 首页的对象响应混用。

System 首页的智能体选项使用 `system/resource-management/application/application.ts` 的
`getApplicationPage(page, query)`，请求 `/system/resource/application/<currentPage>/<pageSize>`。
工作空间筛选通过 `query.workspace_ids` 传入所选工作空间 ID 的 JSON 数组字符串；名称筛选使用 `name`。
Workspace 智能体分页方法只接收分页与查询条件，从当前资源上下文读取工作空间。

### 对话接口

Admin 调试接口在 `admin/workspace/conversation.ts`，正式 Chat 接口在 `chat/conversation.ts`，
使用各自请求客户端。面板 `common/get-api.ts` 仅按 ChatType 选择完整 API，不拼 URL。
Chat 协议及认证接口见 [chat/README.md](chat/README.md)。

历史消息和流式聚合复用 `@/api/types` 的 `ChatContent`，定义在 `types/chat-log.ts`；
`ChatLogRecord.question` 与 `messages` 使用该内容项类型，扩展字段保留为 `unknown`。
Chat、Workspace 调试和 System 调试的记录分页及详情均声明 `ChatLogRecord` 返回类型，
消息列表依赖从 `ConversationApiAdapter` 选取对应接口约定。
`conversation-panel/core/stream.ts` 的 `ConversationStream<Chunk>` 通过回调推断分片类型，
兼容对话内容项、工具调试和纯文本生成；流读取器使用原生 `Response` 与字节流类型。

### 通用文件上传

`admin/file.ts` 与 `chat/file.ts` 分别提供 `postUploadFile(file, sourceId, sourceType, onProgress?)`，
通过各自请求客户端向 `/oss/file` 提交 FormData 的 `file`、`source_id` 和 `source_type`。
Admin 上传尚未创建的资源文件时，`sourceId` 可传 `undefined`，省略 `source_id` 并使用后端默认值。
返回值统一为 `{ request, abort }`，`request` 解包得到文件地址，`abort()` 中断客户端请求。
普通上传直接等待 `request`，需要进度时传入 `(percent, event)`；只有能获取上传总量时才回调
0–100 的百分比，100 表示请求体已上传，不代表服务端处理成功，完成状态以 `request` 为准。
取消时 Promise 仍拒绝，由调用方处理状态，请求层不弹出通用错误提示；loading 由调用方在
`finally` 中恢复。Admin `FileApi.deleteFile(fileId)` 通过 DELETE `/oss/file/<fileId>` 删除已上传文件，
返回值沿用请求层统一解包，不使用 v2 的 `Result` 包装。

资源类型使用 `@/api/enums` 的 `FILE_SOURCE_TYPE` 与 `@/api/types` 的 `FileSourceType`，
包括知识库、智能体、工具、文档、对话及三种临时文件有效期。对话 Store 使用
`FILE_SOURCE_TYPE.CHAT` 调用对应 File API，对话 API 不再维护上传接口。
知识库工作流调试上传复用 Admin `FileApi.postUploadFile`，传知识库 ID 与 `FILE_SOURCE_TYPE.KNOWLEDGE`，
通过返回的 `request` 获取文件地址，再适配动态表单的 `{ data: url }` 返回协议；工作流 API 不重复封装上传。

### System 资源管理模型与工具

`views/system/resource-management/` 页面导入的 API 对象统一使用 `System` 前缀，
例如 `SystemModelApi`、`SystemToolApi`、`SystemToolWorkflowApi`、`SystemRelatedResourcesApi`、
`SystemResourceTriggerApi`、`SystemCommonApi`、`SystemWorkspaceApi` 和 `SystemModelProviderApi`。
此处前缀用于区分页面中的 API 引用；共用供应商接口仍使用原有模块和请求地址。

`admin/system/resource-management/model.ts`、`tool/tool.ts` 沿用 v2 已有的
`/system/resource/model` 与 `/system/resource/tool`，适配 v3 请求解包与命名。
分页使用 `ParamsPage` / `ResponsePage`；模型、工具的 `workspace_name`、`resource_count` 和
更新时间维护在各自公共业务类型中。页面维护 loading，不传入请求方法。
模型选项使用 `/model/model_list` 并合并 `shared_model`、`model`；参数表单与配置更新使用
资源自身 ID。工具仅提供既有的查询、编辑、删除、导出、调试、连接测试、代码检查及 Skill 文件接口，
不声明资源管理范围不存在的创建、导入接口。

`tool/tool-workflow.ts` 独立维护 System 工具工作流详情、保存、发布、调试、版本历史和执行记录，
协议与 Workspace 工作流接口一致。`related-resources.ts` 使用
`/system/resource/resource_mapping` 与 `/system/resource/mapping_resource`，参数签名与
当前 Workspace 关联资源 API 一致。`resource-trigger.ts` 使用
`/system/resource/<sourceType>/<sourceId>/trigger`，资源上下文与触发器载荷复用公共类型。
System 接口由资源管理服务提供；本地开源后端没有对应扩展时，需要连接提供这些接口的部署。

### System 共享工具工作流

`system/shared-resources/tool/tool-workflow.ts` 提供详情、保存、发布、调试、版本和执行记录，
前缀 `/system/shared/tool`，只接收资源 ID。两种 System 工具的 getToolListWithShared 查询各自
`/tool_list`，合并 tools／shared_tools；需相应部署支持扩展协议。

### 知识库工作流转换

Workspace、System 资源管理及 System 共享资源的 `knowledge.ts` 提供
`postTransformWorkflow(knowledgeId, { work_flow })`，沿用 v2 的 POST
`/<knowledgeId>/transform_workflow`，各自使用对应知识库前缀，返回布尔值；
转换页通过可管理范围上下文的 `resourceApi.knowledge` 调用，不固定 Workspace API。
服务端转换知识库类型并创建工作流，
保留已有文档，已是工作流类型时拒绝重复转换。页面负责确认、loading、成功提示及进入画布。
默认图复用知识库创建模板，不用保存工作流接口代替转换。

### 文档与分段

四范围 document.ts、paragraph.ts 的对象由详情上下文装配。Workspace 与 System 两种范围提供完整维护，
Workspace 共享只提供已有查询，不添加写方法或回退其他来源。

| 范围            | 知识库资源前缀                                     |
| --------------- | -------------------------------------------------- |
| Workspace       | `/workspace/<workspaceId>/knowledge`               |
| Workspace 共享  | `/system/shared/workspace/<workspaceId>/knowledge` |
| System 资源管理 | `/system/resource/knowledge`                       |
| System 共享     | `/system/shared/knowledge`                         |

文档接口在前缀后追加 `/<knowledgeId>/document`，分段再追加 `/<documentId>/paragraph`。
System 不读取 workspaceId；飞书在知识库前缀追加 lark/<knowledgeId>，模板下载不带知识库 ID。
System／飞书扩展及文件 ID 导入、策略协议需对应部署支持，不能因前端接口存在认定已联调。

文档分页使用 ParamsPage／ResponsePage<DocumentItem>，名称／创建者／任务／启用／命中／标签筛选支持组合。
图片与文档共用 Document API 的 `getDocumentPage` 列表接口及响应结构，图片列表额外传入查询参数
`resource_type: 'image'`，不单独封装图片列表接口。
不分页选项复用 `getAllDocuments(knowledgeId, { resource_type })`，类型为 `document` 或 `image`，返回 `DocumentItem[]`；
工作空间、System 资源管理及 System 共享使用相同参数，关联分段弹窗据此切换左侧资源列表。
批量删除提交 `{ id_list, resource_type }`，图片传 `image`，普通文档默认传 `document`；
服务端按知识库和资源类型校验整批 ID。
批量向量化提交 `{ id_list, state_list, resource_type }`；图片同样传 `image`，普通文档默认传 `document`。
Workspace 与 System 资源管理的 `knowledge/image.ts` 提供图片专属接口，通过上下文 `resourceApi.image` 读取。
`postUploadImagePreview` 通过 POST `image/preview` 按策略生成图片预览，
JSON 提交 `{ file_id_list, doc_strategy }`，复用上传成功的文件 ID，不重复上传，返回 ImageDocumentPreview[]；
图片预览结果仅包含 name、source_file_id、resource_type（image）、content 和 doc_strategy，
沿用 DocumentSplitResult 的分段结构；页面直接展示 content，不进行结构转换。
启用视觉增强时，预览请求等待所选模型或工具完成识别，返回识别后的分段；
关闭视觉增强或识别失败时，正文使用不含扩展名的文件名，预览生成无需客户端轮询。
`putBatchCreateImageDocuments` 通过 PUT `image/batch_create` 提交 ImageDocumentImportPayload，返回 DocumentItem[]。
未生成预览时，提交 `{ file_id_list, doc_strategy }`，ID 使用上一步上传成功的图片文件 ID，并传当前处理策略；
已预览时提交 `{ file_id_list }`，使用生成结果的 `source_file_id`，服务端保留已有预览的策略和识别结果。
图片支持 JPG、JPEG、PNG、WEBP、BMP；共享范围尚未装配图片上传和导入接口，不回退到 Workspace。
System 资源管理接口前缀为 `/system/resource/knowledge/<knowledgeId>/document/image`；
生成预览 POST `preview`，批量添加 PUT `batch_create`。
is_active 为 false 时保留，“全部”省略；tags 传叶子 ID 数组或 NO_TAG，按 tags[] 序列化。
状态使用 DOCUMENT_TASK_STATE 与 DOCUMENT_TASK_TYPE，不用通用 STATE_TYPES；非任务状态省略 task_type。
status_meta 可空，aggs 为 `{ status, count }[]`，state_time 按任务和状态索引；null 聚合状态按忽略处理。

putDocument 统一更新名称、启停及设置，不按字段重复封装；名称最多 128。
单项设置 meta 保留来源，批量 allow_download 在顶层。任务载荷通常用 id_list／state_list，
生成用 document_id_list，标签用 document_ids／tag_ids，迁移及批量导出直接传 ID 数组。

| 操作         | 协议差异                                                                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| 创建         | PUT batch_create；空白名称与解析后内容使用同一方法，返回 DocumentItem[]                                     |
| 文本预览     | POST split_by_file_ids，JSON `{ file_id_list, doc_strategy }`，复用已上传文件；响应 content 转为 paragraphs |
| 文本直接导入 | POST import，JSON `{ file_id_list, doc_strategy }`，服务端解析并创建，不先 split 或再次上传                 |
| 表格／QA     | POST table_by_file_ids／qa_by_file_ids，提交 `{ file_id_list }`，模板 GET 支持 excel／csv                   |
| Web          | POST web，提交 source_url_list、selector、doc_strategy                                                      |
| 飞书         | POST lark/<id>/<folderToken>/doc_list，读取 files／has_more／next_page_token；import 提交文档数组           |
| 向量化       | 单项 PUT <documentId>/refresh，批量 batch_refresh；state_list 可选全部或排除成功                            |
| 分词         | 单项 PUT <documentId>/tokenize，批量 batch_tokenize，全部七种状态                                           |
| 取消任务     | 单项 PUT <documentId>/cancel_task，提交 `{ type }`；批量 batch_cancel_task                                  |
| 同步         | 单项 <documentId>/sync 不传体，批量 batch_sync 传 `{ id_list }`；飞书批量 lark/<id>/\_batch，均 PUT         |
| 导出         | 单项 GET <documentId>/export 或 export_zip；批量 POST batch_export 或 batch_export_zip，直接传 ID 数组      |

除文档生成问题的批量协议外，不以单元素批量接口代替单项。导出文件名优先服务端，
缺失时单项使用文档名、批量使用知识库名加 xlsx／zip。

分段协议类型在 types/paragraph.ts，分页支持 title、content，后端按 position 和创建时间排列。

| 方法                                                         | 协议                                                                                      |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| postParagraph                                                | title、content、is_active、可选 problem_list；position 指定插入，默认首位                 |
| getParagraphDetail／putParagraph                             | 返回 ParagraphDetail 对象，不按数组解析；正文更新不提交 problem_list，启停仅传 is_active  |
| putParagraphPosition                                         | PUT adjust_position，query paragraph_id、new_position，无请求体                           |
| postParagraphProblem／getParagraphProblems                   | <paragraphId>/problem，提交 content 或读取已关联问题                                      |
| putAssociateParagraphProblem／putUnassociateParagraphProblem | association／unassociation，query paragraph_id、problem_id，仅改变关联                    |
| putMigrateParagraphs                                         | PUT migrate/knowledge/<targetId>/document/<targetId>，`{ id_list }`，目标不能是当前文档   |
| putGenerateParagraphQuestions                                | PUT batch_generate_related，ParagraphGeneratePayload + paragraph_id_list，不传 state_list |
| putBatchDeleteParagraphs                                     | PUT batch_delete，`{ id_list }`，服务端清理关联与索引                                     |

标题最多 256，后端内容上限 102400；界面限制见 View 文档。
问题候选在 knowledge/problem.ts 的 getProblemsPage，支持 content 搜索，分页记录类型为 ProblemItem。
Workspace 共享 Paragraph API 仅 getParagraphPage、getParagraphDetail，不补问题查询或维护。

### 知识库问题

四范围 `knowledge/problem.ts` 使用各自知识库前缀追加 `/<knowledgeId>/problem`，
由知识库及文档详情上下文的 `resourceApi.problem` 选择，不固定 Workspace。
`getProblemsPage(knowledgeId, page, query)` 返回 `ResponsePage<ProblemItem>`，query 支持 content 和 order_by。
排序字段为 paragraph_count、hit_num、last_hit_time、create_time、update_time，降序在字段名前加 `-`。
`ProblemItem` 包含 id、content、paragraph_count、hit_num、last_hit_time、create_time、update_time；
分段已有问题仍使用轻量 `ParagraphProblem`，不要求包含列表统计字段。

Workspace、System 资源管理、System 共享提供完整问题 API：
`postProblems` 直接提交内容字符串数组，`putProblem` 提交 `{ content }`，单项 DELETE 使用问题 ID，
`putBatchDeleteProblems` 直接提交问题 ID 数组；单个问题内容最多 256 字符。
`getProblemDetail` 返回 `ProblemParagraph[]`，包含分段字段及 knowledge_id、document_name、knowledge_type、
document_resource_type、document_image_id；来源元数据由后端补齐，图片详情使用 document_image_id 读取原图。
取消关联复用 Paragraph API 的 `putUnassociateParagraphProblem`，不调用问题或分段删除接口。
Workspace 共享仅有 `getProblemsPage`，不补造详情或写接口，不回退其他范围。

### 标签与文档关联

四范围 tags.ts 按上述知识库前缀维护；Workspace 共享只 getKnowledgeTags，其余范围提供维护和关联。
公共类型为 KnowledgeTagGroup 及 types/knowledge.ts 的载荷，文档关联不混用标签删除。

| 方法                        | 路径／载荷                                                                              |
| --------------------------- | --------------------------------------------------------------------------------------- |
| getKnowledgeTags            | GET <id>/tags，非分页分组；可写范围可传 name，共享无查询参数；值可含 doc_count          |
| postKnowledgeTags           | POST tags，直接提交 `{ key, value }[]`，兼容创建组及新增值                              |
| putKnowledgeTag             | PUT tags/<tagId>，完整 id、key、value；重命名保留 value，改单值保留 key，不模拟多行编辑 |
| deleteKnowledgeTag          | key 删除整组，one 删除单值                                                              |
| putBatchDeleteKnowledgeTags | PUT tags/batch_delete，直接 ID 数组                                                     |
| postImportKnowledgeTags     | POST tags/import，FormData 单个 file，XLS／XLSX；跳过重复组合，校验整份文件后写入       |
| exportKnowledgeTagTemplate  | GET tags/template/export，下载标签模板.xlsx                                             |
| getDocumentTags             | GET document/<documentId>/tags，支持 name                                               |
| postBatchAddDocumentTags    | POST document/batch_add_tag，`{ document_ids, tag_ids }`                                |
| putDeleteDocumentTags       | PUT document/<documentId>/tags/batch_delete，直接标签 ID 数组，仅解除关联               |
| putUnlinkTagDocuments       | PUT tag/<tagId>/docs_delete，`{ id_list }`，取消同一标签的文档关联                      |

标签名称／值上限 64／128；导入第一行“标签、标签值”，空行跳过，所有工作表统一校验。
关联文档复用 getDocumentPage，resource_type: document、tags: [tagId]；未关联另传 tag_exclude: true。

### 工作空间共享资源查询

`workspace/shared/` 按最终资源文件拆分：`model.ts` 提供 `getModelList`，`tool.ts` 提供
`getToolPage`、`getAllTool`，`knowledge/knowledge.ts` 提供 `getKnowledgePage`、`getAllKnowledge`、`getKnowledgeDetail`。
上述资源查询沿用 `/system/shared/workspace/<workspaceId>/<resource>`，工作空间 ID 在调用时读取。
调用方直接导入对应资源文件，与普通工作空间 API 同时使用时分别命名为
`SharedModelApi`、`SharedToolApi`、`SharedKnowledgeApi`；目录不提供聚合入口。

`workspace/shared/knowledge/document.ts` 提供 `getDocumentPage(knowledgeId, page, query)`，
请求 `/system/shared/workspace/<workspaceId>/knowledge/<knowledgeId>/document/<currentPage>/<pageSize>`。
共享与普通知识库文档查询统一使用 `ParamsPage`、`ResponsePage<DocumentItem>` 和 `Dict<unknown>`，
不传 loading，不保留 v2 的 `Result` 或下划线分页参数。两个文件各自默认导出 API 对象。

`workspace/shared/knowledge/tags.ts` 提供只读的 `getKnowledgeTags(knowledgeId)`，
请求 `/system/shared/workspace/<workspaceId>/knowledge/<knowledgeId>/tags`，返回 `KnowledgeTagGroup[]`。
与普通工作空间标签 API 同时使用时，分别导入为 `SharedTagsApi` 与 `TagsApi`。

共享知识库 `getKnowledgeDetail(knowledgeId)` 请求知识库资源 `/<knowledgeId>`，返回 `KnowledgeDetail`。

Workspace 共享知识库详情由 `resourceScope: 'workspace-shared'` 选择上述完整共享 API 对象；
普通详情继续使用 `workspace/knowledge/`。共享详情和文档查询不使用 System 共享资源管理 API，
也不回退到普通 Workspace 知识库接口。文档创建者选项沿用共享列表的 System `common.ts` 查询。

### 资源对话用户授权

资源对话用户接口按四种范围维护 `chat-user.ts`，同一范围供智能体、知识库页面选用，不与 System 对话端用户管理接口混用：

- `workspace/chat-user.ts`：`/workspace/{workspaceId}/{resource_type}/{resource_id}`。
- `workspace/shared/chat-user.ts`：`/system/shared/workspace/{workspaceId}/{resource_type}/{resource_id}`，仅查询。
- `system/resource-management/chat-user.ts`：`/system/resource/knowledge/{resource_type}/{resource_id}`。
- `system/shared-resources/chat-user.ts`：`/system/shared/knowledge/{resource_type}/{resource_id}`。

后三套接口保留联调 TODO；Workspace 共享在 V2 只核对到 KNOWLEDGE 查询，不能据此认定共享智能体接口已支持。
System 前缀中的额外 `knowledge` 段暂按 V2 保留，不能依据普通资源接口自行删减。
资源类型使用 `RESOURCE_TYPE.APPLICATION / KNOWLEDGE` 的大写值；后台按原值读写授权记录，不会将小写转换为大写。
仓库中的 `system_manage/urls.py` 已注册普通 Workspace 授权路径，其他范围需在提供对应接口的后端环境联调。

通过 `user_group` 查询和保存组自动授权，通过 `user_group_id/<groupId>` 保存逐用户授权，
分页查询在其后追加 `/<currentPage>/<pageSize>`；沿用 `ParamsPage`、`ResponsePage` 和原有数组请求体。
调用方直接读取已解包数据并管理 loading；共享只读 API 不补写方法以凑齐接口集合。
公共类型维护在 `types/chat-user.ts`，经 `@/api/types` 导出；用户组已授权人数读取 `authorized_count`，不用分页用户数据推算全组人数。

智能体对话用户页通过 `application-detail/context.ts` 的 `resourceApi.chatUser` 选择 Workspace 或
System 资源管理 API，不包含 Workspace 共享和 System 共享。知识库对话用户页通过详情 context
的 `resourceApi.chatUser` 选择四套现有完整 API，传 `RESOURCE_TYPE.KNOWLEDGE` 和上下文知识库 ID。
共有查询方法为必填，部分范围缺失的保存方法按 ScheduledSync、Tags、Document 同样的规则标记为可选，
调用使用 `?.`；缺失方法不发请求、不提示保存成功，不回退普通 Workspace，不修改现有接口协议。

### 智能体对话日志

智能体详情 context 仅装配 Workspace 和 System 资源管理的完整 Application、Overview、Access、ChatLog、
Workflow 与 ChatUser API。System 智能体接口统一使用 `/system/resource/application` 前缀，
详情 GET、配置 PUT 使用 `/<applicationId>`，发布 PUT 使用 `/<applicationId>/publish`；
概览统计使用 GET `application_stats`；用户排行分页、汇总与导出约定见上文“智能体概览”，待后台对齐。
发布历史使用 GET `/<applicationId>/application_version`，版本编辑使用 PUT 追加版本 ID。
DebugPanel 与日志正文仍使用现有 Workspace conversation／聊天记录实现，尚未按 System 范围适配。

`workspace/application/chat-log.ts` 和 `system/resource-management/application/chat-log.ts` 使用 Admin 请求客户端，
前缀分别为 `/workspace/<workspaceId>/application` 和 `/system/resource/application`。日志分页请求
`/<applicationId>/chat/<currentPage>/<pageSize>`，导出使用 `postExportExcel` 请求
`/<applicationId>/chat/export`，查询包含日期、摘要或用户及点赞、点踩下限；
导出请求体为 `{ select_ids }`，空数组表示导出当前筛选结果。
日志业务类型经 `@/api/types` 导出，来源枚举经 `@/api/enums` 导出，loading 由调用方维护。
Workspace 清除策略通过 PUT `batch_clean_time` 提交当前智能体的单元素 `id_list`、`clean_time`、
`file_clean_time`；System 沿用 v2 的单个智能体 PUT `/<applicationId>` 保存两个清除天数字段。
成功后页面刷新应用详情。
添加知识库通过 POST `/<applicationId>/add_knowledge` 提交 `ChatLogAddKnowledgePayload`
（`knowledge_id`、`document_id`、`chat_ids`），将所选对话的问答写入目标文档。
知识库及目标文档选项通过当前范围 Knowledge／Document API 查询，文档使用 `getAllDocuments(knowledgeId)`。
聊天记录与标注接口保留在同一 API 文件；日志详情使用现有 `LogConversation`，其聊天记录查询仍使用 Workspace API。

简易智能体详情的 `model`、`stt_model`、`tts_model`、`long_term_model` 为模型 ID 响应别名，
`knowledge_list` 为已关联知识库快照；保存映射到对应的 `*_model_id` 字段（主模型为 `model_id`）。
语音及长期记忆模型的空 ID 使用 `null`，不提交空 UUID 字符串；简易设置不将详情的 `work_flow`
回传，避免触发工作流配置提取。

### 智能体发布渠道

`admin/workspace/application/access.ts` 和 `admin/system/resource-management/application/access.ts`
独立维护发布渠道接口，前缀分别为 `/workspace/<workspaceId>/application/<applicationId>/platform`
与 `/system/resource/application/<applicationId>/platform`，沿用 v2 协议。
GET `/status` 返回按平台标识索引的 `[是否已配置, 是否启用]`；POST `/status` 提交
`{ type, status }`。GET、POST `/<type>` 查询与保存对应平台配置，不由通用 application.ts 转发。
平台标识由 `APPLICATION_ACCESS_PLATFORM` 定义，业务类型在 `types/application.ts` 经公共入口导出。
公众号配置包含布尔值 `is_certification`，其余表单字段为字符串；配置保存保留未编辑字段。
回调地址沿用 Admin API base 下的 `/chat/<type>/<applicationId>`，不使用独立 Chat API base。
这些接口依赖部署端提供对应的平台接入服务。

### 知识库外部检索服务

四个知识库范围分别在自己的 `external-retrieval.ts` 中维护配置接口，仅资源前缀与写入能力不同：

- Workspace：`/workspace/<workspaceId>/knowledge/<knowledgeId>`。
- Workspace 共享：`/system/shared/workspace/<workspaceId>/knowledge/<knowledgeId>`。
- System 资源管理：`/system/resource/knowledge/<knowledgeId>`。
- System 共享资源：`/system/shared/knowledge/<knowledgeId>`。

`getKnowledgeExternalRetrieval(knowledgeId)` 通过 GET `<资源前缀>/external_service` 查询配置；
`putKnowledgeExternalRetrieval(knowledgeId, payload)` 通过 PUT 同一路径保存开关，Workspace 共享只提供查询。
工作空间 ID 在调用时由 API 内读取，四套均使用 Admin 请求封装，不返回占位 null 或回退其他范围。

查询返回 `enabled`、`authentication`、`api_url`、`api_example`、`mcp_url`、`mcp_config`；
`api_example` 为后台生成的完整 API 调用示例文本（string），前端仅展示和复制，不拼接请求内容。
保存只更新 payload 传入的 `enabled` 或 `authentication`，保留未提交字段，并返回包含最新 `api_example` 的完整配置。
响应与提交类型共用 `types/knowledge-external-retrieval.ts`，通过 `@/api/types` 导入；请求层统一解包 `data`。
页面通过 Knowledge Detail Context 的 `resourceApi.externalRetrieval` 按四范围选择完整 API，
实现加载、开关保存、失败重试、回显与只读内容复制；Workspace 共享不发送保存请求。

### 知识库定时同步

`setting/scheduled-sync/` 页面调用设置查询、保存和日志分页接口；保存返回的规范化配置用于回填。

四个知识库范围分别在自己的 `scheduled-sync.ts` 中维护接口，由 `views/knowledge-detail/context.ts`
按资源范围装配为 `resourceApi.scheduledSync`。Workspace、System 资源管理、System 共享资源提供查询、保存及日志分页；
Workspace 共享版本只提供设置查询和日志分页。定时同步设置页通过 `useKnowledgeDetailContext()`
取得当前范围的查询 API 和可管理范围的保存 API，不回退其他范围，也不为只读范围补写接口。

`workspace/knowledge/scheduled-sync.ts` 提供 `getKnowledgeSyncSetting`、`putKnowledgeSyncSetting`，
分别通过 GET、PUT `/<knowledgeId>/sync_setting` 查询和保存 Web、飞书及工作流知识库同步设置。
`KnowledgeSyncSetting` 定义在 `types/knowledge-sync.ts`，包含 `enabled`、`schedule_type`、
`sync_type` 及当前周期的时间、日期、间隔或 Cron 字段；`time` 为 HH:mm 数组，
每周日期为 1–7，每月日期为 1–31。服务端校验至少 5 分钟的频率，保存不立即发起同步。
`getKnowledgeSyncLogPage(knowledgeId, page)` 查询 `/<knowledgeId>/sync_log/<currentPage>/<pageSize>`，
使用 `ResponsePage<KnowledgeSyncLog>`，返回文档计数、消息、四种执行状态、毫秒及秒数耗时，
仅包含定时任务。周期类型统一复用 `enums/schedule.ts` 的 `SCHEDULE_TYPE`，
触发器、长期记忆及知识库同步共享同一协议值；日志状态使用 `enums/knowledge.ts` 的 `KNOWLEDGE_SYNC_STATUS`，为 `running`、`success`、
`failure`、`skipped` 字符串；`KnowledgeSyncStatus` 与 `KnowledgeSyncLog` 经 `@/api/types` 导入。

### 知识库权限与详情范围

Workspace 和 System 资源管理的 `getKnowledgeDetail(knowledgeId, section?)` 可传 `setting` 或 `document_strategy`，
对应后台独立的设置／策略查看权限；普通详情会去除未授权的配置元数据。
`getKnowledgeMcpConfig` 使用 `/<knowledgeId>/mcp_config`，仅获取 MCP 配置，独立于外部服务设置权限。
文档和图片复用的操作接口按持久化资源类型鉴权；批量图片操作未传 `resource_type` 时由服务端解析实际类型。
