# views 目录说明

本文档是页面职责和页面功能代码组织规则的唯一依据。新增、移动、删除页面，改变页面职责，或
调整页面专用代码的位置前，应先阅读并同步更新本文档。

## 放置规则

- `views/<feature>/` 是页面功能边界。每个独立功能页面使用自己的目录，路由页面和该页面专用
  代码放在同一目录或其子目录中，不要把多个无关页面平铺在上级目录。
- 路由级 Vue 组件统一使用 `PascalCase` 并以 `View.vue` 结尾，例如
  `UserListView.vue`。
- 页面拆分出的普通子组件统一放在当前功能目录的 `components/` 中，不与路由页面、Dialog 或
  Drawer 混放。
- 页面使用的 Dialog 统一放在当前功能目录的 `dialog/` 中，文件使用 `PascalCase` 并以
  `Dialog.vue` 结尾，例如 `UserPwdDialog.vue`。
- 页面使用的 Drawer 放在当前功能目录中，文件使用 `PascalCase` 并以 `Drawer.vue` 结尾，
  例如 `AddMemberDrawer.vue`。Drawer 不放入 `components/` 或 `dialog/`。
- 卡片 Action 独占且由 Action 自主管理的 Drawer 或 Dialog，与 Action 一起放入
  `<card-name>/action-dropdown/<action-name>/`；页面通过卡片的 `action-dropdown` 插槽组合操作，
  不直接导入或调用这些浮层。
- 仅供一个页面使用的代码放在该页面功能目录；同一功能下多个页面复用的代码放在它们最近的
  共同功能目录中。
- 不要为了复用一个页面内部实现而提前移动到 `src/components`。
- 页面类型的归属和复用遵循 `src/api/API_README.md`；API 与页面共用的业务类型从
  `@/api/types` 导入。页面常量可使用 `constants.ts`；其他逻辑文件应按具体职责命名，避免
  `helpers.ts` 等含义模糊的名称。
- 只有代码确实跨多个功能复用时，才按对应专项规则上移到 `src/components`、`src/constants`、
  `src/utils`、`src/stores` 或 `src/api`。
- 所有使用 `src/workflow-canvas/` 渲染画布的路由页面统一放在 `views/workflow/`。这些页面负责
  路由参数、页面头部、保存或发布等页面动作以及后续接口编排；LogicFlow 初始化、节点注册和
  画布内部行为遵循 `src/workflow-canvas/README.md`，不移入 View。
- 页面目录存在多个层级时，目录名应表达业务层级，例如
  `system/identity/groups/UserGroupListView.vue`，不要创建无业务含义的分组目录。
- 页面脚本中的状态、计算属性和处理方法按照同一业务流程集中放置，并使用简短的业务备注划分
  列表查询、批量操作等流程。流程较长的函数应在确认、请求、刷新等关键阶段添加说明，重点解释
  Promise 返回、执行顺序和业务约束，不为含义明确的单行代码逐句添加注释。
- 页面模板的事件绑定不直接调用 Dialog、Drawer 等组件实例暴露的 `open()` 方法。应在对应业务
  流程的方法区域定义语义明确的 `handleOpenXxx` 处理函数，由处理函数调用组件实例的 `open()`，
  模板只绑定该处理函数；创建和编辑共用同一浮层时，可通过处理函数的可选参数区分操作场景。
- 表单联动或请求明确由当前组件的用户交互触发时，优先绑定组件的 `change` 等语义事件，并在
  `handleXxxChange` 方法中处理副作用，不使用 `watch` 间接监听同一个 `v-model`。只有变化来源不
  受当前组件事件控制时，例如监听父级 Props、异步配置或多个响应式来源，才使用 `watch`。

参考结构：

```text
src/views/<feature>/<page>/
├── FeatureListView.vue           # 路由级页面，统一以 View.vue 结尾
├── FeatureEditDrawer.vue         # 页面抽屉，统一以 Drawer.vue 结尾
├── components/                   # 页面拆分出的普通子组件
│   └── FeatureSetting.vue
├── dialog/                       # 页面弹窗，统一放在独立目录
│   ├── CreateFeatureDialog.vue   # 创建弹窗，统一以 Dialog.vue 结尾
│   └── DeleteFeatureDialog.vue   # 删除弹窗
└── constants.ts                  # 仅供该功能使用的常量
```

不需要为了匹配示例创建空目录；有对应代码时再创建。

## 四类特殊资源

`application`、`knowledge`、`model`、`tool` 是需要同时支持 Workspace、System 资源管理和
System 共享资源的四类特殊资源。它们统一遵循以下页面组织规则：

- 可跨范围复用的资源卡片保留在对应基础资源目录的 `<resource>-card/` 中；System 页面复用该
  卡片，不在 `views/system/` 复制展示组件。
- 卡片负责展示、固定的卡片内交互以及 `actions`、`action-dropdown` 等组合插槽，不读取路由
  Scope，也不自行选择 API；固定交互需要请求时，使用页面传入的完整业务 API 对象。
- 页面根据当前 `resourceScope` 组合本场景需要的 Action，并显式传入中文 `label`、当前资源数据和
  完整业务 API 对象；不在 Card 内维护菜单数组或 API Map。
- 多个范围共用的 Action 跟随基础资源卡片维护；仅供 Workspace 使用的 Action 留在对应基础资源
  目录；仅供 System 资源管理或 System 共享资源使用的 Action 放在对应 System 页面功能目录的
  `<resource>-card/action-dropdown/`。
- 每个菜单 Action 使用独立业务目录。Action 独占的 Drawer 或 Dialog 与 Action 放在同一目录，
  点击时按需挂载，并在 `closed` 后卸载；多个 Action 共用的浮层才提升到最近共同功能目录。

这套三范围资源规则只适用于上述四类特殊资源，不扩展到普通 System 设置、身份管理或其他页面。

当前工具页面按工具类型组织维护表单，共用的参数和代码设置保留在工具功能目录的
`components/` 中：

```text
src/views/tool/
├── ToolView.vue
├── McpConfigDialog.vue           # MCP 工具配置查看弹窗
├── components/                    # 工具创建与编辑共用的表单片段
│   ├── ToolCreateDropdown.vue     # 工具创建入口
│   ├── init-field/
│   ├── input-field/
│   └── python-code/
├── tool-form/                     # 各类型工具创建、编辑表单
│   ├── DataSourceFormDrawer.vue
│   ├── McpFormDrawer.vue
│   ├── SkillToolFormDrawer.vue
│   ├── WorkflowFormDialog.vue
│   └── tool-custom/
├── tool-card/
│   ├── index.vue                  # 工具卡片展示与操作插槽
│   ├── InitParamDialog.vue        # 启用工具前配置启动参数
│   ├── UpdateVersionButton.vue    # 根据页面传入的商店数据检测并更新工具版本
│   └── action-dropdown/           # 工作空间工具菜单 Action
│       ├── index.ts
│       ├── copy-tool/
│       ├── delete-tool/
│       ├── edit-tool/
│       └── export-tool/
└── tool-store/                    # 工具商店入口、详情与添加流程
    └── ToolStoreOpenButton.vue    # 工具商店入口
```

各类型表单只维护本类型特有字段和流程，并统一放在 `tool/tool-form/`；创建入口和编辑 Action
共同复用这些表单。启动参数、输入参数、Python 内容等已有表单片段应从 `tool/components/` 复用，
不在类型目录中重复实现。`ToolCodeSetting` 的生成入口默认隐藏，只由普通自定义工具表单通过
`showGenerate` 显式开启。工具列表页面通过 `ToolCard` 的 `actions` 和 `action-dropdown` 插槽组合
操作；编辑 Action 负责按 `TOOL_TYPE` 打开对应类型表单。各类型表单创建成功后通过 `refresh` 事件
刷新列表，编辑成功后通过 `update` 事件返回接口响应的完整工具数据，由页面局部更新对应卡片；不要
把不同工具类型的字段重新合并到一个通用表单中。所有调用 `postTool` 创建工具的流程在接口成功后
先调用 `auth.loadAuthBaseProfile()` 刷新当前用户基础资料，再执行成功提示和页面刷新；`putTool` 编辑
流程不触发该刷新。需要请求的 Action 和表单接收页面传入的完整 Tool API，不额外维护逐方法接口
类型。工具启用状态属于固定的卡片内交互，由 `ToolCard`
使用页面传入的 Tool API 更新，并通过 `update` 事件通知页面替换列表数据。工具批量选择状态和
批量删除流程由 `ToolView` 管理；`ToolCard` 只把选择模式与选中状态传给 `MkSourceCard`。
工具商店列表由 `ToolView` 统一加载并经 `ToolCard` 传给 `UpdateVersionButton`，卡片和更新按钮
不重复请求商店列表。

System 共享资源页面统一放在 `views/system/shared-resources/`。页面负责 System 范围的资源查询、
筛选和页面动作；资源卡片、供应商列表等可复用展示能力继续使用对应 Workspace 功能目录中的
组件，不在共享资源目录复制实现。两个页面共用的资源卡片 Action 跟随对应 Workspace 功能维护；
只被 Workspace 页面使用的 Action 保留在 Workspace 功能目录，只被 System 共享资源页面使用的
Action 放入 `views/system/shared-resources/<card-name>/action-dropdown/`。每个 Action 使用独立业务目录，
对应的菜单文案由使用页面通过 `label` 显式传入。

```text
src/views/system/shared-resources/
├── SharedModelview.vue
└── model-card/action-dropdown/
    ├── index.ts
    └── shared-model-info/
        ├── SharedModelInfoAction.vue
        └── SharedModelInfoDrawer.vue
```

当前 System 用户页面示例：

```text
src/views/system/identity/users/
├── UserListView.vue               # 用户列表路由页面
├── UserFromDrawer.vue             # 用户表单抽屉
├── components/
│   └── UserGroupSetting.vue       # 用户组与工作空间异步联动设置
└── dialog/
    ├── BatchSetUserRoleDialog.vue # 批量设置用户角色弹窗
    └── UserPwdDialog.vue          # 修改用户密码弹窗
```

## 文件命名

| 文件职责     | 命名格式                            | 示例                                |
| ------------ | ----------------------------------- | ----------------------------------- |
| 路由页面     | `XxxView.vue`                       | `WorkspaceListView.vue`             |
| 抽屉         | `XxxDrawer.vue`                     | `AddMemberDrawer.vue`               |
| 弹窗         | `XxxDialog.vue`                     | `CreateOrUpdateWorkspaceDialog.vue` |
| 页面普通组件 | 按具体业务职责使用 `PascalCase.vue` | `UserGroupSetting.vue`              |

不要使用缺少组件职责后缀的页面文件名，也不要把 Dialog 命名为 Drawer 或把 Drawer 命名为
Dialog。新增或重命名文件时，应同步更新所有导入和页面功能登记。

## 页面功能登记

| 页面                                                                   | 功能说明                               |
| ---------------------------------------------------------------------- | -------------------------------------- |
| `application/ApplicationView.vue`                                      | 工作空间智能体目录与智能体卡片页面     |
| `workflow/ApplicationWorkflowView.vue`                                 | 智能体工作流页面头部与全屏画布         |
| `chat/ChatView.vue`                                                    | Chat 入口的对话页面                    |
| `error/NotFoundView.vue`                                               | Admin 未匹配路由和全局 404 页面        |
| `home/HomeView.vue`                                                    | Workspace 首页                         |
| `knowledge/KnowledgeView.vue`                                          | 工作空间知识库目录与知识库卡片页面     |
| `knowledge/KnowledgeDetailView.vue`                                    | 知识库详情页面                         |
| `knowledge/DocumentDetailView.vue`                                     | 知识库文档详情页面                     |
| `login/LoginView.vue`                                                  | Admin 登录页面                         |
| `login/ForgotPasswordView.vue`                                         | 忘记密码页面                           |
| `model/ModelView.vue`                                                  | 工作空间模型目录与模型卡片页面         |
| `system/identity/groups/GroupsListView.vue`                            | 用户组列表页面                         |
| `system/identity/resource-authorization/ResourceAuthorizationView.vue` | 工作空间用户组与用户的分类资源授权页面 |
| `system/identity/roles/RoleListView.vue`                               | 角色列表页面                           |
| `system/identity/users/UserListView.vue`                               | 用户列表页面                           |
| `system/identity/workspaces/WorkspaceListView.vue`                     | 工作空间列表页面                       |
| `system/chat/user-groups/GroupsListView.vue`                           | 对话用户组及组成员管理页面             |
| `system/chat/users/UserListView.vue`                                   | 对话用户列表、配额及用户导入管理页面   |
| `system/settings/theme/ThemeSettingView.vue`                           | 系统外观设置和登录外观预览页面         |
| `system/settings/authentication/AuthenticationView.vue`                | 系统登录及认证源配置页面               |
| `system/settings/email/EmailSettingsView.vue`                          | 系统邮件 SMTP 服务配置页面             |
| `system/operate-logs/OperateLogListView.vue`                           | 系统操作日志查询与清理页面             |
| `system/shared-resources/SharedModelview.vue`                          | System 共享模型查询与模型卡片页面      |
| `tool/ToolView.vue`                                                    | 工作空间工具目录与工具卡片页面         |

## 备注要求

- 新增路由级页面时，必须在“页面功能登记”中添加一条简洁、明确的功能说明。
- 页面职责改变、文件重命名或目录移动时，必须同步修改登记内容。
- 对职责不直观的页面专用 TypeScript 文件，在文件顶部用一句话说明负责的业务领域和用途。
- 注释说明“为什么”和业务约束，不重复描述能够从文件名、类型或代码直接看出的内容。

## 登录页实现约定

- Element Plus 登录表单通过 `formEl.validate((valid, fields) => {})` 回调处理校验结果。
- LDAP 与本地账号登录保留清晰的条件分支，请求结果使用 `.then().catch()` 处理；未经明确要求，
  不改写为 `try/catch` 或额外抽象登录提交流程。
