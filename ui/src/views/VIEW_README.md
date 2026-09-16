# views 目录说明

本文档是页面职责和页面功能代码组织规则的唯一依据。新增、移动、删除页面，改变页面职责，或
调整页面专用代码的位置前，应先阅读并同步更新本文档。

## 放置规则

- 当前新增功能暂不接入前端权限判断，包括按权限隐藏入口、禁用控件或拦截操作，等待用户明确
  指令后再增加。已有功能的权限逻辑不随新功能开发移除；导入或创建后的用户资料刷新继续保留。
- `views/<feature>/` 是页面功能边界。每个独立功能页面使用自己的目录，路由页面和该页面专用
  代码放在同一目录或其子目录中，不要把多个无关页面平铺在上级目录。
- 路由级 Vue 组件统一使用 `PascalCase` 并以 `View.vue` 结尾，例如
  `UserListView.vue`。
- 页面按钮组件遵循 [COMPONENT_README.md](../components/COMPONENT_README.md) 的 `Button` 前缀命名规则，
  文件名、导入名和模板引用保持一致。
- 页面拆分出的普通子组件统一放在当前功能目录的 `components/` 中，不与路由页面或 Drawer
  混放。属于同一业务流程的入口、Dialog 和配套组件可以使用职责明确的业务目录集中维护，例如
  `create-application/`；Dialog 文件使用 `PascalCase` 并以 `Dialog.vue` 结尾。
- 页面使用的 Drawer 放在当前功能目录中，文件使用 `PascalCase` 并以 `Drawer.vue` 结尾，
  例如 `AddMemberDrawer.vue`。Drawer 不放入 `components/`。
- `action-dropdown/` 目录目前只优先用于 `application`、`knowledge`、`model`、`tool` 四类特殊
  资源，用于维护跨 Workspace、System 资源管理或 System 共享资源复用的卡片 Action。其他业务
  暂不主动创建这类目录，操作入口和配套流程优先留在所属页面或组件中；出现明确的跨范围共享需求
  后再评估是否采用相同结构。
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
  画布内部行为遵循 `src/workflow-canvas/WORKFLOW_README.md`，不移入 View。
- 页面目录存在多个层级时，目录名应表达业务层级，例如
  `system/identity/groups/UserGroupListView.vue`，不要创建无业务含义的分组目录。
- 页面脚本中的状态、计算属性和处理方法按照同一业务流程集中放置，并使用简短的业务备注划分
  列表查询、批量操作等流程。流程较长的函数应在确认、请求、刷新等关键阶段添加说明，重点解释
  Promise 返回、执行顺序和业务约束，不为含义明确的单行代码逐句添加注释。
- 同类业务页面的模板必须在各操作入口前添加简短的中文 HTML 备注，覆盖顶部操作、行操作、
  更多菜单项和批量操作，例如 `<!-- 导入用户 -->`、`<!-- 创建用户 -->`、`<!-- 编辑 -->`、
  `<!-- 修改用户密码 -->`、`<!-- 更多 -->`、`<!-- 删除 -->`、`<!-- 批量设置角色 -->`。
  备注紧邻对应按钮、菜单项或封装后的入口组件；批量操作明确标注“批量”，名称按实际业务职责
  填写。今后新增或调整同类页面时统一补齐，不因操作已封装为组件或按钮已有文案而省略。
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
├── create-feature/               # 创建流程的入口、弹窗和配套组件
│   └── CreateFeatureDialog.vue
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
- 单文件菜单 Action 直接放在 `action-dropdown/`；包含专属 Drawer、Dialog 或其他配套文件的 Action
  使用 `<action-name>-action/` 业务目录。专属浮层点击时按需挂载，并在 `closed` 后卸载；多个 Action
  共用的浮层才提升到最近共同功能目录。

资源卡片的共享外壳使用全局自动注册的 `MkSourceCard`，模板无需手动导入。其操作插槽约定
以 `../components/COMPONENT_README.md` 为准；各资源的业务 Card 与 Action 继续显式导入。

这套三范围资源规则只适用于上述四类特殊资源，不扩展到普通 System 设置、身份管理或其他页面。

当前智能体列表按卡片展示、菜单 Action 和页面批量流程分层维护：

```text
src/views/application/
├── ApplicationView.vue
├── application-card/
│   ├── ApplicationCard.vue        # 智能体卡片展示、选择状态和 Action 插槽
│   └── action-dropdown/
│       ├── index.ts
│       ├── DeleteApplicationAction.vue
│       ├── ExportApplicationAction.vue
│       ├── MoveApplicationAction.vue
│       └── SettingApplicationAction.vue
├── create-application/
│   ├── AdvancedCreateDialog.vue      # 高级智能体创建弹窗
│   ├── CreateApplicationDropdown.vue # 简易、高级和导入创建入口
│   └── SimpleCreateDialog.vue        # 简易智能体创建弹窗
└── template.ts

src/views/application-detail/
├── WorkspaceApplicationDetail.vue # 提供工作空间智能体详情上下文并组合资源详情布局
├── context.ts                      # 智能体详情子路由共享数据与刷新能力
├── overview/
│   └── OverviewView.vue             # 智能体概览内容
└── setting/
    └── SimpleSettingView.vue        # 简易智能体设置内容
```

`ApplicationCard` 只维护展示内容、批量选择状态和 `action-dropdown` 插槽；`ApplicationView` 组合
设置、移动、导出和删除 Action，并管理批量选择、批量移动和批量删除流程。需要请求的 Action 接收
页面传入的完整 Application API。单项移动在具体目录中通过 `delete` 通知页面局部移除卡片，在
“全部智能体”中保留卡片；移动弹窗复用公共 `MoveToDialog`。非批量选择状态点击卡片时，卡片通过
`click` 事件通知 `ApplicationView` 进入详情路由。`WorkspaceApplicationDetail` 返回列表时根据详情的
`folder` 字段写入 `folderId` query，由 `FolderTree` 恢复所属文件夹；列表切换文件夹时只清除该
query，不写入新的文件夹 ID，进入详情时也不携带该 query。`WorkspaceApplicationDetail` 负责工作
空间智能体详情上下文，共享的返回入口、二级导航和右侧子路由结构由
`layout/ResourceDetailLayout.vue` 维护。详情子路由通过
`useApplicationDetailContext()` 读取只读详情；接口返回完整详情时调用 `replaceApplicationDetail()`
局部替换，接口只返回布尔值或部分数据时调用 `refreshApplicationDetail()` 重新获取详情。切换二级
菜单不会重新挂载详情容器，也不会自动重复请求详情。

智能体模板中心参照工具商店按列表、卡片、详情和创建流程组织：

```text
src/views/application/template-store/
├── TemplateStoreDialog.vue        # 模板列表、搜索与工作流覆盖确认
├── TemplateStoreDetailDrawer.vue  # 模板详情与使用入口
└── components/
    └── TemplateCard.vue           # 模板卡片及详情抽屉的按需挂载
```

模板中心直接平铺全部模板，支持名称搜索，不展示分类导航、分类锚点或卡片分类文字。
`TemplateStoreDialog.open(folderId)` 接收创建目标目录，默认用于模板创建；
工作流模式传入 `source="work_flow"`，选择模板后发出 `use(template)`，由工作流页面处理确认和请求。
弹窗不接收智能体 ID 或 API；页面通过 `applying` 传入忙碌状态，成功后调用 `close()`，失败保留弹窗。
卡片负责打开详情抽屉，卡片和详情的使用操作统一通过 `use(template)` 交给 `TemplateStoreDialog`。
模板中心按 `source` 选择创建智能体或覆盖工作流，统一管理一份 `AdvancedCreateDialog`，
传入目标 `folderId`，创建成功后关闭模板中心并通知刷新；配套浮层在 `closed` 后卸载。
`create-application/AdvancedCreateDialog.open(template?)` 同时承接普通高级创建与商店模板创建。
传入模板时回填名称、描述，隐藏内置模板选择并提交 `work_flow_template`；无参数时保留空白和知识库问答助手选择，
提交 `work_flow` 及开场白。创建成功刷新用户基础资料、发出 `refresh` 并进入智能体工作流，
提交期间禁止重复提交与关闭，关闭后清理草稿并发出 `closed`。
`ApplicationView` 在批量选择按钮之后、创建入口之前组合
`components/ButtonTemplateStore.vue`，位置及样式与工具商店入口一致，批量选择模式下隐藏。
入口传入当前文件夹 ID，转发创建成功的 `refresh` 事件刷新智能体列表。

知识库列表按相同方式维护卡片、菜单 Action 和批量流程：

```text
src/views/knowledge/
├── KnowledgeView.vue
├── knowledge-card/
│   ├── KnowledgeCard.vue
│   └── action-dropdown/
│       ├── index.ts
│       ├── SettingKnowledgeAction.vue   # 跳转知识库设置
│       ├── ExportKnowledgeAction.vue    # Excel、文档 ZIP 与知识库包导出
│       ├── MoveKnowledgeAction.vue
│       └── DeleteKnowledgeAction.vue
├── create-knowledge/
│   ├── CreateKnowledgeDropdown.vue       # 知识库创建菜单与弹窗入口
│   ├── CreateBaseKnowledgeDialog.vue     # 通用知识库创建
│   ├── CreateWebKnowledgeDialog.vue      # Web 站点配置与创建
│   ├── CreateLarkKnowledgeDialog.vue     # 飞书应用配置与创建
│   ├── CreateWorkflowKnowledgeDialog.vue # 工作流知识库创建
│   └── components/
│       └── KnowledgeBaseForm.vue         # 名称、描述与 Embedding 模型表单
└── template.ts
```

`KnowledgeCard` 只负责展示、选择状态和 `action-dropdown` 插槽；页面传入完整 Knowledge API，
组合单项转移、删除 Action，并管理批量选择、全选、批量转移与批量删除。共享知识库不展示这些操作。
`SettingKnowledgeAction` 暂不增加权限判断，点击后携带当前
`workspaceId` 和知识库 ID 跳转 `workspace-knowledge-setting`；阻止事件冒泡，避免同时触发卡片详情跳转。
`ExportKnowledgeAction` 接收完整 Knowledge API，暂不增加权限判断；悬停“导出”展开右侧
子菜单，分别导出文档 Excel、文档 ZIP 和可再次导入的知识库包。
导出复用页面操作 loading，防止重复请求，结束或失败后恢复；共享知识库不展示该入口。
切换文件夹退出批量模式，搜索或刷新列表清空选择。转移复用公共 `MoveToDialog`：单项飞书知识库
调用 `putLarkKnowledge`，其他类型调用 `putKnowledge`，只提交 `folder_id`；成功后通过 `move`
更新卡片所属目录，在具体目录转出时通过 `delete` 移除卡片，在全部目录或转入当前目录时保留。
批量转移与删除使用对应批量接口，成功后退出选择模式并刷新列表。

`CreateKnowledgeDropdown` 内聚四类创建弹窗 Ref 和打开动作，列表页传入目标 `folderId`，通过
`refresh` 刷新列表。入口支持 `trigger` 插槽替换默认创建按钮，下拉使用 `persistent`。
各弹窗接收 `folderId`，通过 `open()` 打开；工作流额外接受可选的商店模板。共用的
`KnowledgeBaseForm` 负责名称、描述、Embedding 模型必填校验以及工作空间和共享模型查询，
通过 `ModelApi.getModelListWithShared({ model_type: 'EMBEDDING' })` 一次加载模型选项，
复用 `SelectModel`，允许创建模型后刷新选项。Web、飞书的特有字段留在对应弹窗中。
模型加载后仅在未选择时默认选中首个可用模型；重置表单时恢复该默认值，无可用模型时保持为空。
刷新选项不覆盖用户选择或设置页回填的模型。
创建前校验表单，提交期间禁止重复提交和关闭；成功后刷新用户基础资料并通知列表刷新，
普通类型进入文档列表，工作流进入画布。每次打开及关闭动画结束后清理表单，工作流模板使用
`cloneDeep` 隔离；创建流程使用 Workspace API，不通过路由字符串推测 System 范围。
飞书创建沿用扩展接口 `/lark/save`，部署环境需要提供该接口。
“导入创建”沿用智能体和工具的菜单文件选择交互，调用 `postKnowledgeImport` 上传文件及当前
`folderId`，导入成功后先刷新用户基础资料，再通知知识库列表刷新。上传期间禁止重复导入，
请求结束后清理文件列表，允许重新选择同一文件；文件内容由后端校验。

当前工具页面按工具类型组织维护表单，共用的参数和代码设置保留在
`tool-form/component/` 中：

```text
src/views/tool/
├── ToolView.vue
├── components/
│   ├── CreateToolDropdown.vue     # 工具创建入口
│   └── ButtonToolStore.vue    # 工具商店入口
├── tool-form/                     # 各类型工具创建、编辑表单
│   ├── DataSourceFormDrawer.vue
│   ├── McpFormDrawer.vue
│   ├── SkillToolFormDrawer.vue
│   ├── WorkflowFormDialog.vue
│   ├── component/                 # 工具表单共用片段
│   │   ├── init-field/
│   │   ├── input-field/
│   │   └── python-code/
│   └── tool-custom/
├── tool-card/
│   ├── ToolCard.vue               # 工具卡片展示与操作插槽
│   ├── InitParamDialog.vue        # 配置工具启动参数
│   ├── ToolStatusSwitch.vue       # 工具启停及启动参数配置入口
│   ├── ButtonUpdateVersion.vue    # 根据页面传入的商店数据检测并更新工具版本
│   └── action-dropdown/           # 工作空间工具菜单 Action
│       ├── index.ts
│       ├── CopyToolAction.vue
│       ├── DeleteToolAction.vue
│       ├── EditToolAction.vue
│       ├── ExportToolAction.vue
│       ├── InitParamAction.vue
│       ├── MoveToolAction.vue
│       ├── ToolWorkflowAction.vue
│       └── mcp-config-action/
│           ├── McpConfigAction.vue
│           └── McpConfigDialog.vue # MCP 工具配置查看弹窗
└── tool-store/                    # 工具商店列表、详情与添加流程
    ├── component/
    │   └── ToolStoreCard.vue      # 商店工具卡片及详情、添加入口
    ├── StoreToolFormDialog.vue    # 商店工具应用表单及提交
    ├── ToolStoreDetailDrawer.vue  # 商店工具详情
    └── ToolStoreDialog.vue        # 商店分类、查询及添加成功后的列表刷新
```

各类型表单只维护本类型特有字段和流程，并统一放在 `tool/tool-form/`；创建入口和编辑 Action
共同复用这些表单。启动参数、输入参数、Python 内容等已有表单片段应从
`tool/tool-form/component/` 复用，
不在类型目录中重复实现。`ToolCodeSetting` 的生成入口默认隐藏，只由普通自定义工具表单通过
`showGenerate` 显式开启。工具列表页面通过 `ToolCard` 的 `actions` 和 `action-dropdown` 插槽组合
操作；编辑 Action 负责按 `TOOL_TYPE` 打开对应类型表单，启动参数 Action 获取工具详情后打开
`InitParamDialog`，MCP 配置 Action 获取 MCP 工具详情后打开 `McpConfigDialog`。工作流 Action 进入
独立的工具工作流画布；创建工作流工具后直接进入该画布，其他类型表单创建成功后通过 `refresh`
事件刷新列表。编辑成功后通过 `update` 事件返回接口响应的完整工具数据，由页面局部更新对应卡片；不要
把不同工具类型的字段重新合并到一个通用表单中。所有调用 `postTool` 创建工具的流程在接口成功后
先调用 `auth.loadAuthBaseProfile()` 刷新当前用户基础资料，再执行成功提示以及列表刷新或工作流页面
跳转；`putTool` 编辑流程不触发该刷新。跨资源范围复用且需要请求的 Action 和表单接收页面传入的完整 Tool API，不额外
维护逐方法接口类型；固定服务于 Workspace 工具商店的 `StoreToolFormDialog` 直接内聚对应请求。
工具启用状态属于固定的卡片内交互，由 `ToolStatusSwitch`
使用卡片传入的 Tool API 更新，并通过 `update` 事件通知页面替换列表数据。工具批量选择状态、
批量移动和批量删除流程由 `ToolView` 管理；`MoveToolAction` 复用公共 `MoveToDialog` 完成单个工具移动，
在具体目录中通过 `delete` 通知页面局部移除卡片，在“全部工具”中保留卡片。`ToolCard` 只把选择模式与选中状态传给 `MkSourceCard`。
工具商店列表由 `ToolView` 统一加载并经 `ToolCard` 传给 `ButtonUpdateVersion`，卡片和更新按钮
不重复请求商店列表。`ToolStoreCard` 负责卡片展示与详情抽屉的按需挂载；卡片和详情中的
“应用”操作统一通过 `apply(tool)` 交给 `ToolStoreDialog`。
`ToolStoreDialog` 管理一份 `tool-store/StoreToolFormDialog.vue`，应用时按需挂载并传入目标
`folderId`，关闭动画结束后卸载；应用成功后关闭商店并发出 `refresh` 通知页面刷新。
`StoreToolFormDialog` 保留表单校验、各工具类型的提交请求及提交状态管理，根据打开时的新增或编辑
上下文完成请求。新增成功发出无数据的 `refresh` 事件；编辑成功通过 `update` 返回接口响应的完整工具数据。

System 共享资源页面统一放在 `views/system/shared-resources/`。页面负责 System 范围的资源查询、
筛选和页面动作；资源卡片、供应商列表等可复用展示能力继续使用对应 Workspace 功能目录中的
组件，不在共享资源目录复制实现。两个页面共用的资源卡片 Action 跟随对应 Workspace 功能维护；
只被 Workspace 页面使用的 Action 保留在 Workspace 功能目录，只被 System 共享资源页面使用的
Action 放入 `views/system/shared-resources/<card-name>/action-dropdown/`。Action 目录结构遵循单文件
扁平放置、多文件使用 `<action-name>-action/` 的规则，对应的菜单文案由使用页面通过 `label` 显式传入。

```text
src/views/system/shared-resources/
├── SharedModelview.vue
└── model-card/action-dropdown/
    ├── index.ts
    └── shared-model-info-action/
        ├── SharedModelInfoAction.vue
        └── SharedModelInfoDrawer.vue
```

System 用户页面按业务流程归拢操作入口和专属 Dialog。入口组件管理弹窗 Ref、打开动作并转发
`refresh`；列表页负责查询、批量选择和刷新策略，创建与编辑共用的 `UserFromDrawer` 仍由页面管理。

```text
src/views/system/identity/users/
├── UserListView.vue
├── UserFromDrawer.vue
├── components/
│   └── UserGroupSetting.vue
├── import-users/
│   ├── ButtonImportUsers.vue
│   └── ImportUsersDialog.vue
├── user-password/
│   ├── ButtonChangeUserPassword.vue
│   └── UserPwdDialog.vue
└── batch-set-user-role/
    ├── ButtonBatchSetUserRole.vue
    └── BatchSetUserRoleDialog.vue
```

`system/chat/users/` 同样使用 `import-users/`、`user-password/`，批量用户组设置放在
`batch-set-user-group/`（`ButtonBatchSetUserGroup.vue` 与 `BatchSetUserGroupDialog.vue`）；
单人和批量配额设置统一放在 `quota-settings/`（`ButtonQuotaSettings.vue` 与
`QuotaSettingsDialog.vue`）。配额入口通过 `dropdown` 区分行菜单与批量按钮，传入单个用户 ID
或选中用户 ID 数组。行操作菜单开启 `persistent`，避免菜单关闭时卸载其内部的配额弹窗。
两套用户页面保留各自业务 API 和导入成功后的查询刷新方式。

操作日志页面的清除策略入口与弹窗统一放在 `system/operate-logs/clean-strategy/`：
`ButtonCleanStrategy.vue` 管理打开动作和弹窗 Ref，`CleanStrategyDialog.vue` 负责策略查询与保存，
`OperateLogListView.vue` 只组合入口组件。

资源授权页面的 `UserGroupAuthorizationList` 通过人数链接打开共享业务组件
`components/business/resource-authorization-drawer/user-group/UserGroupMembersDrawer.vue`，按用户组所属工作空间查询成员，提供用户名、姓名搜索和分页，
并使用 `MkTagGroup` 折叠展示角色；点击人数不切换当前授权对象。

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
| `application-detail/WorkspaceApplicationDetail.vue`                    | 工作空间智能体详情上下文与资源详情布局 |
| `application-detail/overview/OverviewView.vue`                         | 智能体概览内容                         |
| `application-detail/setting/SimpleSettingView.vue`                     | 简易智能体设置内容                     |
| `workflow/application/ApplicationWorkflowView.vue`                     | 智能体工作流页面头部与全屏画布         |
| `workflow/knowledge/KnowledgeWorkflowView.vue` | 知识库工作流加载、保存、发布与全屏画布 |
| `workflow/tool/ToolWorkflowView.vue`                                   | 工具工作流页面头部与全屏画布           |
| `chat/ChatView.vue`                                                    | Chat 入口的对话页面                    |
| `error/NotFoundView.vue`                                               | Admin 未匹配路由和全局 404 页面        |
| `home/HomeView.vue`                                                    | Workspace 首页                         |
| `knowledge/KnowledgeView.vue`                                          | 工作空间知识库目录与知识库卡片页面     |
| `knowledge-detail/setting/KnowledgeSettingView.vue` | 知识库基本信息、来源配置与上传限制设置 |
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
| `trigger/TriggerView.vue` | 工作空间触发器查询、新建、编辑及单项和批量启停、删除 |
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

## 工作流页面布局

`workflow/components/WorkflowViewLayout.vue` 由 `ApplicationWorkflowView`、`ToolWorkflowView` 和 `KnowledgeWorkflowView`
共同使用，统一全屏容器、页面头部、返回按钮、标题和保存时间展示。通过 `loading`、`title`、
`saveTime` 传入展示状态，点击返回按钮触发 `back` 事件。
标题前的 `icon` 插槽由各页面分别传入 `ApplicationIcon`、`ToolIcon`、`KnowledgeIcon`，
统一使用 32px 头像，并根据资源详情展示自定义图标或对应类型图标。

`actions` 插槽用于默认模型设置、保存、调试等页面操作，默认插槽放置画布及页面浮层；画布继续使用
`min-h-0 flex-1` 占满头部下方空间。页面保留画布 Ref、资源与模式配置、接口调用、保存和退出确认
逻辑，布局组件只负责展示。添加组件入口由画布右上角的 `AddNode` 统一提供，页面不再转发节点选择事件。

## 智能体工作流自动保存

`ApplicationWorkflowView` 使用 `workflowAutoSave:application:<applicationId>` 浏览器存储开关，
按资源类型和智能体独立记录，不读取旧的全局 `workflowAutoSave` 开关。默认关闭，开启后每
60 秒检查并保存未保存的画布改动。加载、保存、发布和退出确认期间跳过，关闭开关或卸载页面时
清理定时器；仅开启时写入存储，关闭开关时删除当前智能体的存储项。自动保存复用页面保存流程，不弹成功提示；成功更新保存时间和本次提交的图快照，
失败保留未保存状态供后续周期重试。请求期间继续编辑的内容不会被标记为已保存。

## 工作流发布历史

`workflow/application/ButtonPublishHistory.vue` 封装智能体发布历史菜单入口、
面板显隐、列表查询以及版本编辑请求。内部直接调用 application 的版本 API；页面仅传
`applicationId`、`selectedId`、`disabled` 和 `v-model:visible`，接收 `open`、`preview`、
`restore` 事件。每次打开重新查询，编辑成功后关闭弹窗并重新调用 `getWorkflowVersions` 刷新列表，
不向页面发送更新事件；保存失败保留弹窗与草稿。所在 `MkDropdown` 设置 `persistent`，避免收起菜单时销毁面板入口。

`workflow/components/publish-history/PublishHistoryDrawer.vue` 为纯 UI 面板，接收 `versions`、`loading`、
`saving`、`selectedId`，保留传入顺序并将首项标为“最近发布”，显示标题、发布人及创建时间。
内部管理编辑与更新说明弹窗，通过 `submit(payload, versionId)` 交给业务组件保存，成功后由业务组件
调用 `closeEdit()` 关闭编辑弹窗。通过 `preview`、`restore` 通知业务组件，不接收 API、不查询数据，
也不操作路由或画布。面板复用 `MkDrawer`，通过 `v-model` 控制显隐，宽度 320，使用
`top-header`、`h-layout-content` 留出页面头部，不显示遮罩、不锁定滚动，内部复用 Drawer 的滚动区。
抽屉实例保留，由 `MkDrawer` 延迟渲染并在关闭动画结束后销毁内容，不再额外维护挂载状态或转发
`close` / `closed` 事件。页面监听 `historyVisible`，关闭抽屉与头部返回统一恢复草稿并清理预览；
恢复版本时先清空草稿快照再关闭，保留已恢复的版本。编辑弹窗的 `closeEdit()` 仅用于保存成功后关闭表单。

同目录 `EditPublishVersionDialog.vue` 只维护表单副本与校验，通过 `open(version)` 回填、
`submit(payload)` 提交、`close()` 关闭，外部传入 `saving`。标题必填且最多 64 字，更新说明最多
1000 字；按钮沿设计显示“发布”，实际编辑请求由业务组件执行，不创建新发布。
`DescriptionDialog.vue` 通过 `open(content)` 展示纯文本更新说明并保留换行，空内容显示
“暂无更新说明”。两个弹窗均不依赖业务 API，复用 `MkDialog` 的延迟挂载和关闭销毁能力。

后续 knowledge、tool 在各自目录实现业务入口，复用 `PublishHistoryDrawer`（内部包含两个弹窗），不引入通用 API 适配层。

`ApplicationWorkflowView` 已接入更多菜单中的发布历史。打开时关闭调试，面板打开期间跳过
自动保存；首次预览保留当前画布草稿，切换版本不覆盖草稿，关闭预览恢复原草稿。
面板打开后头部保留智能体图标、名称与保存时间，操作区仅显示“恢复此版本”；未选择版本时禁用，
选择版本后启用。通过历史面板关闭按钮或头部返回按钮退出历史模式，并恢复常规头部操作。
这部分展示判断统一由 `WorkflowViewLayout` 的 `historyVisible`、`canRestoreVersion` Props 控制，
点击恢复发出 `restoreVersion`，页面负责具体画布恢复。常规 `actions` 插槽使用 `v-show` 保留实例，
避免历史模式下销毁菜单内的 `ButtonPublishHistory`。其他工作流不传这些 Props 时保持原头部展示。
恢复版本只将历史图数据放回编辑态，不立即保存或发布，后续沿用手动与自动保存流程。
服务端当前版本接口只返回工作流图，不返回历史默认模型设置，页面保留当前默认模型配置。
更新说明使用 `description` 字段，服务端支持要求见 `../api/API_README.md`。

## 工作流默认模型设置

`workflow/components/default-model-setting/ButtonDefaultModelSetting.vue` 负责顶部“默认模型设置”按钮与抽屉按需挂载，
由 `ApplicationWorkflowView` 在 `WorkflowViewLayout` 的 `actions` 插槽中接入。同目录的
`DefaultModelSettingDrawer.vue` 负责抽屉、模型查询、暂存表单及应用与关闭确认。入口挂载后
通过组件 Ref 调用 `open(settings)`；抽屉内部管理显隐，打开时先重置再回填配置，关闭动画结束后
清理状态并触发 `closed`，入口据此卸载。保存事件由入口转发。抽屉复用 `MkDrawer`，
顶部使用 `top-header` 留出页面头栏，高度使用
`h-layout-content`，不显示遮罩，也不阻挡头栏和左侧画布交互。表单由抽屉统一滚动，页脚固定显示
应用到所有节点、取消和保存。

通过 `modelValue` 接收详情配置；`disabled` 控制顶部按钮。
编辑及参数弹窗只修改抽屉副本，通过 `save(settings)` 提交副本；取消或关闭时选择不保存，
直接丢弃副本，详情中的原配置不受影响。API 与组件共用的模型类别
`DefaultModelType`、单项配置 `ModelConfig` 和按类别组织的 `DefaultModelSettingPayload` 维护在
`api/types/model.ts`，避免在组件 Props、Emits 和状态中重复展开工具类型。
`ApplicationWorkflowView` 用 `applicationDetail` 保存完整详情，用 `defaultModelSetting` 单独承接
模型配置，在详情加载或保存成功后从接口的 `default_model_setting` 深拷贝回填，缺省为空对象。
抽屉的 `save(settings)` 调用页面 `handleSaveDefaultModelSetting(settings)`，先暂存到
`defaultModelSetting`，再复用 `handleSave()` 和 `saveApplication` 将配置与 `work_flow` 一起提交。
页面顶部保存使用当前 `defaultModelSetting`；保存成功更新详情，失败则从详情深拷贝回滚配置，
提示错误并继续抛出异常，阻止保存并退出、保存后调试等成功分支。
点击保存后抽屉保持打开；`modelValue` 更新时刷新比较基准，`hasChanges` 自动重新计算。
提交时比较基准会暂时更新，失败回滚后恢复；抽屉编辑副本不被覆盖，保存期间继续编辑的内容仍保留。
页面将 `defaultModelSetting` 通过画布的 `defaultModelSettings` Props 传入，AI 对话节点通过节点 model
获取当前 `LLM` 模型及参数；提交期间使用暂存配置，失败后随页面回滚，不通过 `provide` 同步抽屉草稿。

模型查询通过必填的完整 `modelApi` 对象执行（类型使用 `typeof ModelApi`）；调用方负责选择 API，
组件不从 URL 推断资源范围。每次打开或刷新只查询一次模型列表，保存在 `models` 中，由
`getModelOptions(type)` 按 `model_type` 过滤。默认模型类型保留页面展示顺序，标签复用
`MODEL_TYPE_LABELS`。供应商列表通过当前公共供应商接口查询。模型选择及参数设置复用
`SelectModel`，通过 `canEditParams` 控制参数入口，重排序模型隐藏该入口。
默认模型抽屉开启 `canAdd`，创建成功后通过 `refresh` 重新加载模型列表。

入口接收 `getGraphData` 函数并传给抽屉。“应用到所有节点”确认后，抽屉调用该函数获取最新图数据，
克隆后切换节点的模型来源，保留自定义模型 ID 和参数，递归处理循环体，并保留基本信息节点中
关闭的语音/长期记忆配置及浏览器语音播放模式。存在变更时触发 `applyToAll(graphData)`，入口
转发给 `ApplicationWorkflowView`，页面只负责通过自己的画布 Ref 渲染结果，抽屉不接收画布实例。
`disabled` 同时控制顶部入口和应用操作，确认完成后再次检查，避免保存期间修改画布。
该操作修改画布，由页面原有保存流程持久化，不自动提交抽屉内暂存的默认模型设置。

## 模型创建入口

`model/create-model/ButtonAddModel.vue` 和 `CreateModelDrawer.vue` 通过必填的 `api` 接收完整
模型 API 对象。Workspace 模型页传入 `ModelApi`，System 共享模型页传入 `SystemSharedApi`；
创建抽屉只调用传入的 API，不再自行判断资源范围。
`ButtonAddModel` 默认渲染主按钮，也支持通过默认作用域插槽的 `open()` 定制触发按钮，
`SelectModel` 的下拉页脚使用该插槽复用同一创建流程。创建成功后保留基础资料刷新，再触发
`refresh` 通知调用方重新加载模型列表。

## 资源授权 Action

四类资源卡片的 `action-dropdown/` 分别提供 `AuthorizeModelAction`、`AuthorizeToolAction`、
`AuthorizeKnowledgeAction` 和 `AuthorizeApplicationAction`，由列表页面组合，显式传入 `label`
和当前资源，保存成功后通过 `refresh` 刷新列表。Action 使用对应资源的 Workspace 或 System
`auth` 权限判断，共享资源不展示入口。点击后按需挂载公共 `ResourceAuthorizationDrawer`，
传入资源类型及 `workspaceId` Prop（来自资源数据的 `workspace_id`），调用 `open(resource.id)`；
Workspace 与 System 授权均使用该工作空间 ID，不读取路由工作空间。
在 `closed` 后卸载，不再复制授权表格或请求逻辑。

## 触发器维护

`trigger/TriggerView.vue` 负责列表查询、跨页选择、单项启停/删除及批量操作，通过
`trigger/trigger-form/TriggerFormDrawer.vue` 共用新建和编辑流程，编辑时查询详情并保留任务 ID、参数、
启用状态及 meta。定时支持每日、每周、每月、间隔和五段 Cron；事件支持 URL、Token 和请求参数。
任务选择复用 `SelectApplicationDialog` 与 `SelectToolDialog`，工具限定自定义和工作流类型。
`trigger/trigger-form/request-parameters/RequestParameters.vue` 用 `MkFormList` 展示和删除事件请求参数，
同目录 `RequestParameterDialog.vue` 负责新增、编辑及参数名必填与重名校验；确认后回写，取消保留原值。
`trigger/trigger-form/task-execution/parameters/` 内 `ApplicationParameter.vue` 与 `ToolParameter.vue`
分别生成智能体和工具字段，共用 `ParameterForm.vue` 的输入、事件引用、初始化和校验；
`types.ts` 仅维护跨组件使用的字段描述类型，不再单独拆分每个组件专用的参数工具文件。
初始化只补全缺失值，不覆盖已有自定义配置；切回定时或移除全部事件参数时，引用参数恢复自定义默认值。
智能体包含 Question、启用的文件类型、用户输入和接口参数；工具包含普通输入和工作流用户输入。
抽屉采用类型卡片选择，选中卡片内显示配置，触发周期与 Cron 通过切换按钮切换；新建时需选择周期。
`trigger/trigger-form/task-execution/TaskExecution.vue` 维护任务分组、展开收起、移除及参数表单，
组件内管理智能体与工具选择弹窗、资源详情加载和任务参数保留，通过 `v-model` 回写任务、
`v-model:loading` 同步加载状态、`change` 通知清理校验，并提供 `validate`、`expandAll`、`reset`。
任务 UI 沿用 AI Chat 技能区的 `MkCollapse` 分组和紧凑资源卡片，保存前先展开全部任务，待参数表单挂载后统一校验。
抽屉负责触发器详情查询与保存，将详情资源快照通过 `initialResources` 传入任务组件；
任务组件新增资源后展开任务，抽屉保存时调用分组组件校验全部参数。
保存时校验所有任务，包括折叠的任务；接口失败保持抽屉打开。

`trigger/components/TriggerTaskPopover.vue` 接收分页记录的 `tasks`，在任务列按智能体和工具
展示数量标签，悬浮时分组显示资源图标及名称；无任务时显示 `-`，不发起额外请求。

## 查看关联资源 Action

模型、知识库、应用、工具卡片的 `action-dropdown/` 分别提供
`RelatedResourcesModelAction`、`RelatedResourcesKnowledgeAction`、
`RelatedResourcesApplicationAction`、`RelatedResourcesToolAction`，在更多菜单展示“查看关联资源”。
列表页面按对应资源的 `workspace.relateMap(resource.id)` 控制入口权限，共享知识库、工具和模型不展示。
页面传入完整 `RelatedResourcesApi` 和当前资源。Action 点击后按需挂载
`RelatedResourcesDrawer`，传入对应 `RESOURCE_TYPE` 和包含 `workspace_id` 的资源快照；
工作空间 ID 来自资源数据，缺失时提示并停止打开，关闭后卸载抽屉。
模型及非工作流工具默认展示“引用此资源的资源”，其他资源默认展示“依赖的资源”。
资源名称仅展示文本，暂不支持打开目标资源。

知识库工作流页面使用 `WorkflowMode.Knowledge` 和 `WorkflowMode.KnowledgeLoop`，空画布使用本地文件数据源节点。
页面只通过 `getKnowledgeDetail` 返回的 `work_flow` 加载画布数据，发布前先校验并保存；返回知识库详情时检查未保存改动。

`KnowledgeCard` 在非批量选择模式下通过 `click` 通知列表进入知识库详情。
`knowledge-detail/WorkspaceKnowledgeDetailView.vue` 查询并展示知识库名称，复用
`ResourceDetailLayout` 生成“文档”、“工作流”和“设置”目录，返回列表时恢复所属文件夹。
容器通过 `knowledge-detail/context.ts` 提供只读详情与替换能力；设置页复用已加载详情，保存成功后
更新容器数据，同步名称等展示。基本信息复用创建流程的 `KnowledgeBaseForm`，类型配置和校验留在
设置页中。当前设置页仅接入 Workspace 路由和 API，暂不增加前端权限判断。
更换向量模型需确认，先保存再重新向量化，整条流程禁止重复提交；向量化失败时保留原模型比较基准，
允许再次保存重试。Web、飞书设置保留未编辑的 `meta` 字段，上传限制使用详情顶层值。
`knowledge-detail/document/DocumentListView.vue` 为文档列表子页面，目前保留占位内容；
文档详情作为同一容器的子路由。System 详情仍使用原有独立占位页面。

`KnowledgeWorkflowView` 复用 `ButtonDefaultModelSetting`，从知识库详情读取默认模型配置，
随工作流保存提交并将配置传入画布；支持应用到所有节点，保存失败回滚至已保存配置。

## 智能体复制 Action

`application/application-card/action-dropdown/copy-application-action/` 提供 `CopyApplicationAction`
和 `CopyApplicationDialog`。列表按 `application.workspace.copy(id)` 控制入口，传入完整应用 API、
源应用及当前文件夹 ID。点击后查询完整详情，深拷贝配置并移除原 ID 等资源元数据，名称默认追加
“副本”，确认后创建到打开时的当前文件夹。复制成功刷新列表及用户权限，简易应用进入设置页，
工作流应用进入画布；请求失败保留表单。弹窗按需挂载，在 `closed` 后卸载。

`workflow/application/ApplicationWorkflowView.vue` 直接维护头部的模板中心按钮和弹窗 Ref，
入口位于默认模型设置之前，监听弹窗的 `use(template)` 事件。
按钮复用 `application/template-store/TemplateStoreDialog.vue`，以 `source="work_flow"` 打开；
加载、保存或发布期间禁止打开。页面确认覆盖后提交 `work_flow_template`，重新加载详情、画布和
已保存基准；完成后关闭模板中心并提示成功。取消或失败保留模板中心。

## 智能体工作流调试

`workflow/application/debug/DebugPanel.vue` 封装调试对话、面板显隐、放大/还原及局部样式，
通过 `open()`、`close()` 控制，关闭时重置放大状态。对话内容只在面板打开时挂载，保留关闭动画。
`ApplicationWorkflowView` 直接渲染调试按钮和 `<DebugPanel ref="debugPanelRef" />`，
通过 `handleDebug` 在存在未保存改动时先保存，成功后调用面板的 `open()`。
打开模板中心或默认模型设置时，页面调用 `close()` 关闭调试。

## 智能体工作流返回导航

`workflow/application/navigation.ts` 的 `goBack(applicationId)` 读取当前资源范围的智能体详情父路由，
按子路由 `meta.order` 选择首个有名称、标题、未隐藏且通过 `meta.canAccess(params)` 的页面。
返回逻辑不固定概览、访问、访客或日志路径；新增、重命名和排序子页面只需维护路由配置。
未配置 `canAccess` 的详情页默认可访问；有权限或类型限制的页面必须显式配置。
当前概览使用 v3 `overviewRead` 权限；简易设置只允许 SIMPLE 类型及编辑权限，不作为工作流返回目标。
无可访问详情时回退对应列表。System 暂无详情父路由，当前回退 System 资源管理智能体列表。
`ApplicationWorkflowView` 保留未保存确认以及保存后退出流程，导航统一调用该工具函数。
