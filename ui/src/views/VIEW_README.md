# views 目录说明

本文档是页面职责和页面功能代码组织规则的唯一依据。新增、移动、删除页面，改变页面职责，或
调整页面专用代码的位置前，应先阅读并同步更新本文档。

## 放置规则

- 当前新增功能暂不接入前端权限判断，包括按权限隐藏入口、禁用控件或拦截操作，等待用户明确
  指令后再增加。已有功能的权限逻辑不随新功能开发移除；导入或创建后的用户资料刷新继续保留。
- `views/<feature>/` 是页面功能边界。每个独立功能页面使用自己的目录，路由页面和该页面专用
  代码放在同一目录或其子目录中，不要把多个无关页面平铺在上级目录。
- 路由级 Vue 组件统一命名为 `index.vue`。一个功能目录只有一个入口页时直接使用
  `views/<feature>/index.vue`；同级存在多个入口页时，先按业务职责拆分子目录，再在各自目录中使用
  `index.vue`，例如 `system/resource-management/model/index.vue` 与
  `system/resource-management/tool/index.vue`。
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
  后再评估是否采用相同结构。按明确需求，文档页使用 `knowledge-detail/library/document/action-dropdown/`
  集中维护行操作、批量操作及其专属弹窗；不因此扩展其他普通页面的目录规则。
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
  `system/identity/groups/index.vue`，不要创建无业务含义的分组目录。
- 页面脚本中的状态、计算属性和处理方法按照同一业务流程集中放置，并使用简短的业务备注划分
  列表查询、批量操作等流程。流程较长的函数应在确认、请求、刷新等关键阶段添加说明，重点解释
  Promise 返回、执行顺序和业务约束，不为含义明确的单行代码逐句添加注释。
- 同类业务页面的模板必须在各操作入口前添加简短的中文 HTML 备注，覆盖顶部操作、行操作、
  更多菜单项和批量操作，例如 `<!-- 导入用户 -->`、`<!-- 创建用户 -->`、`<!-- 编辑 -->`、
  `<!-- 修改用户密码 -->`、`<!-- 更多 -->`、`<!-- 删除 -->`、`<!-- 批量设置角色 -->`。
  备注紧邻对应按钮、菜单项或封装后的入口组件；批量操作明确标注“批量”，名称按实际业务职责
  填写。今后新增或调整同类页面时统一补齐，不因操作已封装为组件或按钮已有文案而省略。
- 下拉菜单中包含自带 Dialog 或 Drawer 的 Action 时，使用公共组件的延迟保留机制：
  `MkTableMoreDropdown` 和资源卡片菜单默认启用，直接使用 `MkDropdown` 时传入 `persistent`。
  公共组件在首次展开后保留菜单，页面不自行维护菜单挂载状态或通过 `visible-change` 控制保留。
  仅调用页面方法、且浮层挂载在菜单外的操作不需要保留菜单。
- Dialog 生命周期遵循 `COMPONENT_README.md` 的挂载方式规则：常驻实例在 `closed` 清理，
  关闭后卸载的实例依赖重新初始化，`open()` 不重复清空，只处理业务回填和查询。
- 页面模板的事件绑定不直接调用 Dialog、Drawer 等组件实例暴露的 `open()` 方法。应在对应业务
  流程的方法区域定义语义明确的 `handleOpenXxx` 处理函数，由处理函数调用组件实例的 `open()`，
  模板只绑定该处理函数；创建和编辑共用同一浮层时，可通过处理函数的可选参数区分操作场景。
- 表单联动或请求明确由当前组件的用户交互触发时，优先绑定组件的 `change` 等语义事件，并在
  `handleXxxChange` 方法中处理副作用，不使用 `watch` 间接监听同一个 `v-model`。只有变化来源不
  受当前组件事件控制时，例如监听父级 Props、异步配置或多个响应式来源，才使用 `watch`。

参考结构：

```text
src/views/<feature>/<page>/
├── index.vue                     # 路由级页面
├── FeatureEditDrawer.vue         # 页面抽屉，统一以 Drawer.vue 结尾
├── components/                   # 页面拆分出的普通子组件
│   └── FeatureSetting.vue
├── create-feature/               # 创建流程的入口、弹窗和配套组件
│   └── CreateFeatureDialog.vue
└── constants.ts                  # 仅供该功能使用的常量
```

不需要为了匹配示例创建空目录；有对应代码时再创建。

## 四类特殊资源

`application`、`knowledge`、`model`、`tool` 是需要同时支持 Workspace 普通资源、Workspace 共享资源、System 资源管理和
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

这套资源范围规则只适用于上述四类特殊资源，不扩展到普通 System 设置、身份管理或其他页面。

当前智能体列表按卡片展示、菜单 Action 和页面批量流程分层维护：

```text
src/views/application/
├── index.vue
├── application-card/
│   ├── ApplicationCard.vue        # 智能体卡片展示、选择状态和 Action 插槽
│   └── action-dropdown/
│       ├── index.ts
│       ├── DeleteApplicationAction.vue
│       ├── ExportApplicationAction.vue
│       ├── MoveApplicationAction.vue
│       ├── SettingApplicationAction.vue
│       └── TriggerApplicationAction.vue
├── create-application/
│   ├── AdvancedCreateDialog.vue      # 高级智能体创建弹窗
│   ├── CreateApplicationDropdown.vue # 简易、高级和导入创建入口
│   └── SimpleCreateDialog.vue        # 简易智能体创建弹窗
└── template.ts

src/views/application-detail/
├── index.vue                      # 提供工作空间智能体详情上下文并组合资源详情布局
├── context.ts                      # 智能体详情子路由共享数据与刷新能力
├── overview/
│   └── index.vue                    # 智能体概览内容
└── setting/
    └── index.vue                    # 简易智能体设置内容
```

`ApplicationCard` 只维护展示内容、批量选择状态和 `action-dropdown` 插槽；`ApplicationView` 组合
设置、触发器、移动、导出和删除 Action，并管理批量选择、批量移动和批量删除流程。需要请求的 Action 接收
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

`application/components/ButtonCreateApplication.vue` 支持通过 `trigger` Prop 配置下拉触发方式，
默认为 `click`，传入 `hover` 时悬停展开，也支持响应式切换；同名 `trigger` 插槽用于自定义触发内容，
自定义触发区域统一使用全宽和手型光标。

工作流模板中心的公共 UI 放在 workflow 下，application、knowledge 列表与工作流分别提供业务入口：

```text
src/views/workflow/components/template-store/
├── TemplateStoreDialog.vue        # 模板列表、搜索、加载及空状态
├── TemplateStoreDetailDrawer.vue  # 模板详情与使用入口
└── components/
    └── TemplateCard.vue           # 模板卡片及详情抽屉的按需挂载
```

公共组件接收 `WorkflowStoreTemplate`，不调用 API、不依赖资源创建弹窗。
`TemplateStoreDialog` 接收 `templates`、`resource`、`loading`；`resource` 为
`application` / `knowledge` / `tool`，只决定卡片与详情图标。通过 `open()` 打开并发送空关键词
`search`，名称搜索发送去除首尾空格后的关键词；使用模板统一发出 `use(template)`。
列表平铺模板，不展示分类导航、锚点或分类文字。`loading` 期间禁止搜索和使用，成功后由业务入口
调用 `close()`；取消或失败保留模板中心。详情在关闭动画结束后卸载。

`application/components/ButtonTemplateStore.vue` 调用智能体模板查询接口，整理描述字段，
记录打开时的目标 `folderId`，收到 `use` 后按需挂载 `AdvancedCreateDialog`。
创建弹窗关闭后卸载，取消创建时保留模板中心；创建成功沿用原流程进入智能体工作流。
`create-application/AdvancedCreateDialog.open(template?)` 同时承接普通高级创建与商店模板创建。
传入模板时回填名称、描述，隐藏内置模板选择并提交 `work_flow_template`；无参数时保留空白和知识库问答助手选择，
提交 `work_flow` 及开场白。创建成功刷新用户基础资料并进入智能体工作流，提交期间禁止重复提交与关闭。
`ApplicationView` 在批量选择按钮之后、创建入口之前组合 `components/ButtonTemplateStore.vue`，
传入当前文件夹 ID，批量选择模式下隐藏。

`workflow/application/ButtonTemplateStore.vue` 负责工作流页按钮、模板查询和弹窗实例，
通过 `v-model:loading` 与页面共用加载状态，查询和应用模板均使用该状态；
发出 `open`、`use`，通过 `close()` 供 View 在应用成功后关闭。View 负责覆盖确认、提交模板及重载画布。
`workflow/tool/ButtonTemplateStore.vue` 使用相同的公共 UI，查询工具工作流模板接口并整理描述字段。
工具 View 在确认覆盖后提交 `work_flow_template`，重新加载工具与工作流详情，更新默认模型、画布和
保存基准，成功后关闭模板中心；打开模板中心时关闭调试。
`workflow/knowledge/ButtonTemplateStore.vue` 按相同边界查询知识库模板，由知识库 View 确认覆盖、重载详情并关闭弹窗。

知识库列表按相同方式维护卡片、菜单 Action 和批量流程：

```text
src/views/knowledge/
├── index.vue
├── knowledge-card/
│   ├── KnowledgeCard.vue
│   └── action-dropdown/
│       ├── index.ts
│       ├── SettingKnowledgeAction.vue   # 跳转知识库设置
│       ├── EmbeddingKnowledgeAction.vue # 提交知识库向量化任务
│       ├── GenerateQuestionsAction.vue # 知识库生成关联问题
│       ├── sync-knowledge-action/       # Web 知识库同步入口与方式选择弹窗
│       ├── KeywordIndexKnowledgeAction.vue # 分词索引入口
│       ├── mcp-config-action/           # MCP 配置入口与专属只读弹窗
│       ├── ExportKnowledgeAction.vue    # Excel、文档 ZIP 与知识库包导出
│       ├── MoveKnowledgeAction.vue
│       └── DeleteKnowledgeAction.vue
├── components/
│   ├── ButtonCreateKnowledge.vue        # 知识库创建菜单与弹窗入口
│   └── ButtonTemplateStore.vue          # 知识库模板中心与模板创建入口
├── create-knowledge/
│   ├── CreateBaseKnowledgeDialog.vue     # 通用知识库创建
│   ├── WebKnowledgeDrawer.vue            # Web 站点配置与两步创建抽屉
│   ├── CreateLarkKnowledgeDialog.vue     # 飞书应用配置与创建
│   ├── CreateWorkflowKnowledgeDialog.vue # 工作流知识库创建
│   └── components/
│       └── KnowledgeBaseForm.vue         # 名称、描述与 Embedding 模型表单
└── template.ts
```

`KnowledgeCard` 只负责展示、选择状态和 `action-dropdown` 插槽；页面传入完整 Knowledge API，
组合单项转移、删除 Action，并管理批量选择、全选、批量转移与批量删除。共享知识库不展示这些操作。
`GenerateQuestionsAction` 在非共享知识库菜单提供“生成问题”，复用公共
`GenerateQuestionsDialog`，打开时固定知识库 ID，提交知识库生成接口；共用页面 loading，
成功提示并关闭，失败保留表单。不新增权限判断。
`EmbeddingKnowledgeAction` 在非共享知识库菜单中提供“向量化”，接收完整 Knowledge API，
直接调用 `putReEmbeddingKnowledge`，提交成功后提示“提交成功”；复用页面操作 loading，
阻止重复提交并在请求结束后恢复，不额外增加权限判断或配置弹窗。
`SyncKnowledgeAction` 仅在非共享 Web 知识库菜单展示，不增加权限判断。专属弹窗按需挂载、
关闭后卸载，默认“增量同步”，也支持“替换同步”和“整体同步”；增量同步提示跳过未更新文档、
更新已变更文档的分段，其他方式展示数据覆盖提示；调用
`putSyncWebKnowledge`，成功提示“同步任务发送成功”并关闭。复用页面操作 loading，
提交期间禁止重复提交和关闭，失败保留弹窗与当前选择。
`SettingKnowledgeAction` 暂不增加权限判断，点击后携带当前
`workspaceId`、知识库 ID 和 `KNOWLEDGE_TYPE_MAP[knowledge.type]`，通用类型跳转
`workspace-knowledge-setting`，其他类型直接跳转 `workspace-knowledge-base-setting`；
阻止事件冒泡，避免同时触发卡片详情跳转。
“设置”之后依次组合 `KeywordIndexKnowledgeAction` 和 `McpConfigKnowledgeAction`，接收完整
Knowledge API 并复用页面操作 loading。分词索引不增加确认弹窗，调用成功后只提示“操作成功”；
MCP 配置沿用工具的只读文本与悬浮复制交互，专属弹窗按需挂载、关闭后卸载。
两者接口暂为本地占位，MCP 返回空文本，分词索引模拟成功，尚不执行服务端操作。
`ExportKnowledgeAction` 接收完整 Knowledge API，暂不增加权限判断；悬停“导出”展开右侧
子菜单，分别导出文档 Excel、文档 ZIP 和可再次导入的知识库包。
导出复用页面操作 loading，防止重复请求，结束或失败后恢复；共享知识库不展示该入口。
子菜单使用默认挂载方式，不查询父级浮层或指定 `append-to`；Action 不额外解析下载错误并弹出提示。
切换文件夹退出批量模式，搜索或刷新列表清空选择。转移复用公共 `MoveToDialog`：单项飞书知识库
调用 `putLarkKnowledge`，其他类型调用 `putKnowledge`，只提交 `folder_id`；成功后通过 `move`
更新卡片所属目录，在具体目录转出时通过 `delete` 移除卡片，在全部目录或转入当前目录时保留。
批量转移与删除使用对应批量接口，成功后退出选择模式并刷新列表。

`knowledge/components/ButtonTemplateStore.vue` 在非共享、非批量选择模式下展示于创建入口前，
查询知识库模板并记录打开时的目标文件夹。选择模板后按需挂载 `WorkflowKnowledgeDialog`，
回填模板名称与描述，仍需选择向量模型；提交沿用 `work_flow_template`。创建成功关闭模板中心、
刷新列表并进入知识库工作流，取消创建保留模板中心；创建弹窗在 `closed` 后卸载。

`WebKnowledgeDrawer` 使用底部两步抽屉，基本信息校验后进入文档处理策略，支持返回修改。
`create-knowledge/components/DocumentStrategyForm.vue` 维护分段、视觉增强和标题问题索引，
通过 `doc_strategy` 提交；智能分段默认策略与后端一致，高级分段使用与触发器类型相同的卡片外壳，
在选中卡片内展开配置，默认选择一级至四级标题标识、500–4096 分段长度、256 子块长度并开启自动清洗。
分段标识支持自定义正则表达式，留空使用后端默认规则；启用视觉增强后必须选择模型或工具。
视觉模型和工具选项按当前资源范围选择 Workspace、System 资源管理或 System 共享资源的完整 API，
通过 `isSystemResource()`、`isSystemSharedResource()` 判断，供应商继续使用共用 Provider API。

`ButtonCreateKnowledge` 内聚四类创建浮层 Ref 和打开动作，列表页传入目标 `folderId`，通过
`refresh` 刷新列表。入口支持 `trigger` 插槽替换默认创建按钮，下拉使用 `persistent`。
各创建浮层接收 `folderId`，通过 `open()` 打开；工作流额外接受可选的商店模板。共用的
`KnowledgeBaseForm` 负责名称、描述、Embedding 模型必填校验以及工作空间和共享模型查询，
根据 `isSystemSharedResource()` 选择 System 共享 Model API 或 Workspace Model API，
通过 `getModelListWithShared({ model_type: 'EMBEDDING' })` 一次加载模型选项，
复用 `SelectModel`，允许创建模型后刷新选项。Web、飞书的特有字段留在对应弹窗中。
模型加载后仅在未选择时默认选中首个可用模型；重置表单时恢复该默认值，无可用模型时保持为空。
刷新选项不覆盖用户选择或设置页回填的模型。
创建前校验表单，提交期间禁止重复提交和关闭；成功后刷新用户基础资料并通知列表刷新，
普通类型将接口返回的 `knowledge.type` 通过 `KNOWLEDGE_TYPE_MAP` 转为字符串后进入文档列表，工作流进入画布。常驻弹窗在关闭动画结束后清理表单，打开时只回填本次模板与显示，工作流模板使用
`cloneDeep` 隔离；创建流程使用 Workspace API，不通过路由字符串推测 System 范围。
飞书创建沿用扩展接口 `/lark/save`，部署环境需要提供该接口。
“导入创建”沿用智能体和工具的菜单文件选择交互，调用 `postKnowledgeImport` 上传文件及当前
`folderId`，导入成功后先刷新用户基础资料，再通知知识库列表刷新。上传期间禁止重复导入，
请求结束后清理文件列表，允许重新选择同一文件；文件内容由后端校验。

当前工具页面按工具类型组织维护表单，共用的参数和代码设置保留在
`tool-form/component/` 中：

```text
src/views/tool/
├── index.vue
├── components/
│   ├── ButtonCreateTool.vue     # 工具创建入口
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
│       ├── ExecutionRecordToolAction.vue
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

`tool-card/action-dropdown/ExecutionRecordToolAction.vue` 维护执行记录入口，两个抽屉
`ExecutionRecordDrawer.vue` 和 `ExecutionDetailDrawer.vue` 统一放在 `workflow/tool/execution-record/`。
Workspace 的自定义工具和工作流工具菜单
展示“执行记录”，页面传入工具的完整 Workflow API；点击后挂载抽屉，关闭动画结束后卸载。
列表使用 `MkComplexSearch`、`MkTable` 和 `MkStatusLabel`，支持触发来源名称、类型、状态筛选；
接口按执行时间倒序返回。详情保留输入、输出、错误及工作流节点详情，支持上一条／下一条跨页浏览。

`ToolCard` 仅在非 `disabled`、非批量选择模式下发出 `click` 事件。`ToolView` 点击工作流工具进入
工作流画布（支持 Ctrl / Command 新标签页打开），其他类型复用编辑 Action 打开对应表单。
`EditToolAction` 通过 `defineExpose` 暴露 `handleOpenToolForm()`；列表按工具 ID 保存组件 ref，
卡片点击通过 ref 调用，与编辑菜单共用同一表单实例，保存后继续局部更新卡片。

各类型表单只维护本类型特有字段和流程，并统一放在 `tool/tool-form/`；创建入口和编辑 Action
共同复用这些表单。启动参数、输入参数、Python 内容等已有表单片段应从
`tool/tool-form/component/` 复用，
不在类型目录中重复实现。`ToolCodeGenerate` 的生成入口默认隐藏，只由普通自定义工具表单通过
`showGenerate` 显式开启。`python-code/CodeGenerate.vue` 直接复用公共业务组件
`GenerateContent`，在普通编辑区及放大编辑器的 `header-extra` 插槽提供生成入口，
不再单独封装 Python 生成组件。`ToolFormDrawer` 只绑定代码并传入完整 `toolForm`，不管理生成弹窗。
`CodeGenerate` 内部按当前资源范围选择 Tool/Model API，从 `toolForm` 读取工作空间及参数定义，
打开时复制启动参数与输入参数。表单中的 `workspace_id` 仅供生成时筛选模型，保存工具前移除。
`CodeGenerate` 维护模型选择、参数设置、v2 工具代码模板及 `generate_code` 请求载荷，通过
`request` 属性提供请求函数、`header-extra` 插槽放置模型选择；替换时移除外层 Python Markdown
代码围栏，普通编辑区直接回写表单草稿，放大编辑器通过 `header-extra` 的 `replaceCode` 回调
替换全屏草稿，点击“确定”后再同步表单。公共组件统一处理 `ConversationStream`、停止、重新生成和输入交互，
不接收工具表单、不判断资源范围，不维护原始输入、暂停或继续状态。

`ToolFormDrawer` 通过 `MkEditAvatar` 暂存确认后的头像文件；保存校验通过后先调用 Admin
`postUploadFile`，将返回地址写入 `toolForm.icon` 再提交工具。恢复默认时直接提交空字符串，
未更换图片时不上传；上传失败保留文件供重试，上传成功后清空暂存文件，避免工具保存失败后重复上传。

工具列表页面通过 `ToolCard` 的 `actions` 和 `action-dropdown` 插槽组合
操作；编辑 Action 负责按 `TOOL_TYPE` 打开对应类型表单，启动参数 Action 获取工具详情后打开
`InitParamDialog`，MCP 配置 Action 获取 MCP 工具详情后打开 `McpConfigDialog`。工作流 Action 进入
独立的工具工作流画布；创建工作流工具后直接进入该画布，其他类型表单创建成功后通过 `refresh`
事件刷新列表。编辑成功后通过 `update` 事件返回接口响应的完整工具数据，由页面局部更新对应卡片；不要
把不同工具类型的字段重新合并到一个通用表单中。所有调用 `postTool` 创建工具的流程在接口成功后
先调用 `auth.loadAuthBaseProfile()` 刷新当前用户基础资料，再执行成功提示以及列表刷新或工作流页面
跳转；`putTool` 编辑流程不触发该刷新。跨资源范围复用且需要请求的 Action 和表单接收页面传入的完整 Tool API，不额外
维护逐方法接口类型；`ApplyStoreToolDialog` 内聚商店应用请求，提交时通过
`isSystemSharedResource()` 选择 System 共享资源或 Workspace 的 Tool API 和 Tool Store API，
覆盖工作流模板及商店工具两个分支；历史内置工具由 ToolStore 提供，不再从数据库加载。
工具启用状态由 Workspace 工具页和 System 共享工具页通过 `ToolCard` 的 `actions` 插槽组合
`ToolStatusSwitch`，页面直接传入对应 Tool API 和操作 loading，并通过 `update` 事件替换列表数据。
`ToolCard` 不再接收 Tool API，仅提供操作插槽；版本更新仍通过卡片的 loading 和 update 通道处理。工具批量选择状态、
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
├── model/
│   └── index.vue
└── tool/
    └── index.vue
```

`ToolSharedView` 使用 System 共享工具 API，复用 `ToolCard` 和编辑、启动参数、MCP 配置、
导出、删除 Action。列表使用 `MkInfiniteScroll` 分页加载，支持类型、名称和创建者筛选；
创建与删除后重新查询，编辑和启停成功后替换对应卡片数据。
`ButtonCreateTool` 可接收完整 `api`，默认使用 Workspace Tool API；`showWorkflow` 默认开启，
共享页开启工作流创建，创建后进入 `system-shared-workflow-tool`。共享页支持普通工具、Skills、MCP、数据源及
导入创建，工作流卡片点击进入画布（支持 Ctrl / Command 新标签页），编辑菜单仍修改基础信息。共享页不组合工作空间专用的移动、授权和触发器入口。

System 用户页面按业务流程归拢操作入口和专属 Dialog。入口组件管理弹窗 Ref、打开动作并转发
`refresh`；列表页负责查询、批量选择和刷新策略，创建与编辑共用的 `UserFromDrawer` 仍由页面管理。

```text
src/views/system/identity/users/
├── index.vue
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
`index.vue` 只组合入口组件。

资源授权页面的 `UserGroupAuthorizationList` 通过人数链接打开共享业务组件
`components/business/resource-authorization-drawer/user-group/UserGroupMembersDrawer.vue`，按用户组所属工作空间查询成员，提供用户名、姓名搜索和分页，
并使用 `MkTagGroup` 折叠展示角色；点击人数不切换当前授权对象。

## 文件命名

| 文件职责     | 命名格式                            | 示例                                |
| ------------ | ----------------------------------- | ----------------------------------- |
| 路由页面     | `index.vue`                         | `system/identity/users/index.vue`   |
| 抽屉         | `XxxDrawer.vue`                     | `AddMemberDrawer.vue`               |
| 弹窗         | `XxxDialog.vue`                     | `CreateOrUpdateWorkspaceDialog.vue` |
| 页面普通组件 | 按具体业务职责使用 `PascalCase.vue` | `UserGroupSetting.vue`              |

不要使用缺少组件职责后缀的页面文件名，也不要把 Dialog 命名为 Drawer 或把 Drawer 命名为
Dialog。新增或重命名文件时，应同步更新所有导入和页面功能登记。

## 页面功能登记

| 页面                                                                   | 功能说明                                                             |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `application/index.vue`                                                | 工作空间智能体目录与智能体卡片页面                                   |
| `application-detail/index.vue`                                         | 工作空间智能体详情上下文与资源详情布局                               |
| `application-detail/overview/index.vue`                                | 智能体概览内容                                                       |
| `application-detail/setting/index.vue`                                 | 简易智能体设置内容                                                   |
| `workflow/application/index.vue`                                       | 智能体工作流页面头部与全屏画布                                       |
| `workflow/knowledge/index.vue`                                         | 知识库工作流加载、自动保存、发布历史、模板覆盖、导出、调试与全屏画布 |
| `workflow/tool/index.vue`                                              | 工具工作流页面头部与全屏画布                                         |
| `chat/index.vue`                                                       | Chat 入口的对话页面                                                  |
| `error/index.vue`                                                      | Admin 未匹配路由和全局 404 页面                                      |
| `home/index.vue`                                                       | Workspace 首页                                                       |
| `knowledge/index.vue`                                                  | 工作空间知识库目录与知识库卡片页面                                   |
| `knowledge-detail/index.vue`                                           | 知识库详情页面                                                       |
| `knowledge-detail/setting/base/index.vue`                             | 知识库基本信息、来源配置与上传限制设置                               |
| `knowledge-detail/setting/document-strategy/index.vue`                | Web 知识库文档处理策略占位页面                                       |
| `knowledge-detail/setting/scheduled-sync/index.vue`                   | Web、飞书与工作流知识库定时同步占位页面                              |
| `login/index.vue`                                                      | Admin 登录页面                                                       |
| `login/forgot-password/index.vue`                                     | 忘记密码页面                                                         |
| `model/index.vue`                                                      | 工作空间模型目录与模型卡片页面                                       |
| `system/identity/groups/index.vue`                                    | 用户组列表页面                                                       |
| `system/identity/resource-authorization/index.vue`                    | 工作空间用户组与用户的分类资源授权页面                               |
| `system/identity/roles/index.vue`                                     | 角色列表页面                                                         |
| `system/identity/users/index.vue`                                     | 用户列表页面                                                         |
| `system/identity/workspaces/index.vue`                                | 工作空间列表页面                                                     |
| `system/chat-management/user-groups/index.vue`                        | 对话用户组及组成员管理页面                                           |
| `system/chat-management/users/index.vue`                              | 对话用户列表、配额及用户导入管理页面                                 |
| `system/chat-management/portal-setting/index.vue`                     | 门户基本信息、访问开关、认证配置、跨域地址编辑与门户预览             |
| `system/settings/theme/index.vue`                                     | 系统外观设置和登录外观预览页面                                       |
| `system/settings/authentication/index.vue`                            | 系统登录及认证源配置页面                                             |
| `system/settings/email/index.vue`                                     | 系统邮件 SMTP 服务配置页面                                           |
| `system/operate-logs/index.vue`                                       | 系统操作日志查询与清理页面                                           |
| `system/resource-management/model/index.vue`                          | System 模型分页、筛选、编辑、授权与删除                              |
| `system/resource-management/tool/index.vue`                           | System 工具分页、筛选、维护与工作流入口                              |
| `system/shared-resources/model/index.vue`                              | System 共享模型查询与模型卡片页面                                    |
| `system/shared-resources/tool/index.vue`                               | System 共享工具查询与工具维护页面                                    |
| `trigger/index.vue`                                                    | 工作空间触发器查询、新建、编辑及单项和批量启停、删除                 |
| `tool/index.vue`                                                       | 工作空间工具目录与工具卡片页面                                       |

## 备注要求

门户设置的 `components/ButtonEditPortal.vue`、`ButtonPortalAuthSetting.vue` 和
`ButtonPortalCorsSetting.vue` 分别封装对应按钮、浮层及表单状态，通过 `disabled` 接收页面统一的
编辑限制。页面使用 `perm.system.portal.edit()` 判断门户编辑权限，无权限时禁用配置、复制按钮、
访问开关及浮层表单和按钮，保存入口同步校验权限。认证组件使用 `MkDrawer`，
打开时与系统 `LoginSetting` 共用 `AuthSettingApi.getLoginSetting()`，通过返回的 `login_methods`
生成登录方式选项，复用登录方式标签，初始保留账号登录。提供默认登录方式及验证码与账号锁定设置；默认方式
仅可选已勾选项，取消勾选当前默认项时回退到首个可选项。认证组件暴露 `open()` 供首次开启认证
时联动打开；当前认证配置仅保存到页面内存，取消不回写，刷新后恢复默认配置，待接口接入后持久化。
跨域组件通过 `v-model` 接收地址数组，弹窗按一行一个地址编辑；保存时清理行首尾空白和空行，
取消不回写，关闭后清理草稿。空数组表示不限制来源的配置意图；目前地址仅保存在页面内存，
尚未对接 `cors_config` 或实际跨域策略。

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

## 工作流自动保存

`ApplicationWorkflowView` 使用 `workflowAutoSave:application:<applicationId>` 浏览器存储开关，
`ToolWorkflowView` 使用 `workflowAutoSave:tool:<toolId>`，
`KnowledgeWorkflowView` 使用 `workflowAutoSave:knowledge:<knowledgeId>`，按资源类型与资源 ID 独立记录，
不读取旧的全局 `workflowAutoSave` 开关。默认关闭，开启后每
60 秒检查并保存未保存的画布改动。加载、保存、发布、发布历史和退出确认期间跳过，关闭开关或卸载页面时
清理定时器；仅开启时写入存储，关闭开关时删除当前资源的存储项。自动保存复用页面保存流程，不弹成功提示；成功更新保存时间和本次提交的图快照，
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

同目录 `EditPublishVersionDialog.vue` 只维护表单副本与校验。`mode` 默认为 `edit`，显示“编辑”，
通过 `open(version)` 回填；`mode="publish"` 显示“发布内容”，通过 `open()` 打开空白表单。通过
`submit(payload)` 提交、`close()` 关闭，外部传入 `saving`。标题必填且最多 64 字，更新说明最多
1000 字，标题拒绝纯空白；两种模式的提交按钮均显示“发布”。编辑请求由业务组件执行，
不创建新发布；提交期间禁止编辑表单和关闭弹窗。
`DescriptionDialog.vue` 通过 `open(content)` 展示纯文本更新说明并保留换行，空内容显示
“暂无更新说明”。两个弹窗均不依赖业务 API，复用 `MkDialog` 的延迟挂载和关闭销毁能力。

`workflow/tool/ButtonPublishHistory.vue` 为工具提供独立业务入口，调用工具 `tool_version` API，
编辑成功后重新查询列表。复用 `PublishHistoryDrawer`、历史模式头部与预览/恢复交互。
工具头部采用默认模型设置、带图标的保存、发布和更多菜单；更多菜单包含发布历史与自动保存。
工具历史模式下返回仅退出预览，恢复版本回到编辑态后由手动或自动保存持久化；版本接口未返回
默认模型配置，预览与恢复保留当前配置。
`workflow/knowledge/ButtonPublishHistory.vue` 使用独立 `knowledge_version` API，复用相同 UI 和预览/恢复流程，
编辑成功只重新查询列表；知识库版本同样不含默认模型配置，不引入通用 API 适配层。

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
模型 API 对象。Workspace 模型页传入 `ModelApi`，System 共享模型页传入 `SystemSharedModelApi`；
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

`trigger/index.vue` 负责列表查询、跨页选择、单项启停/删除及批量操作，通过
`trigger/trigger-form/TriggerFormDrawer.vue` 共用新建和编辑流程，编辑时查询详情并保留任务 ID、参数、
启用状态及 meta。定时支持每日、每周、每月、间隔和五段 Cron；事件支持 URL、Token 和请求参数。
任务选择复用 `SelectApplicationDialog` 与 `SelectToolDialog`，工具限定自定义和工作流类型。
`trigger/trigger-form/request-parameters/RequestParameters.vue` 用 `MkTable` 展示事件请求参数，
表格包含参数、数据类型、描述、必填开关和编辑/删除操作，标题栏的加号打开新增 Dialog，
同目录 `RequestParameterDialog.vue` 负责新增、编辑及参数名必填与重名校验；确认后回写，取消保留原值。
`trigger/trigger-form/task-execution/` 直接按三个场景组织任务执行组件：

- `TriggerTaskExecution.vue`：触发器页面的多任务分组、选择、移除、折叠与校验；组件内管理
  智能体和工具选择弹窗，使用 `v-model` 回写任务、`v-model:loading` 同步加载状态，提供 `validate`、`reset`。
- `ToolTaskExecution.vue`：资源入口固定当前工具，只编辑参数，不允许增删或替换执行资源。
- `ApplicationTaskExecution.vue`：资源入口固定当前智能体，遵循相同的单任务约束。
- `TaskParameterForm.vue`：三个组件共用的参数表单，接收按资源类型区分的 `resource`，内部生成
  智能体或工具字段，统一处理自定义输入、事件引用、默认值及校验；字段描述类型保留在文件内。

参数初始化只补全缺失值，不覆盖已有自定义配置；切回定时或移除全部事件参数时，引用参数恢复自定义默认值。
智能体包含 Question、启用的文件类型、用户输入和接口参数；工具包含普通输入和工作流用户输入。
抽屉采用类型卡片选择，选中卡片内显示配置，触发周期与 Cron 通过切换按钮切换；新建时需选择周期。
任务 UI 使用 `MkCollapse` 分组和紧凑资源卡片，保存前展开任务并校验所有参数，包括折叠的任务。
`TriggerFormDrawer` 负责请求与保存，通过可选 `resource` 区分普通触发器和固定资源模式；
资源模式使用传入的完整 `resourceApi`，将资源详情中的单任务转换为内部任务数组，保存时保留任务 ID 和参数。
加载工具任务时补查完整工具详情和必要的工作流定义，避免后端摘要缺少工作流输入字段。
接口失败保持抽屉打开并禁止提交不完整详情，提交期间禁止关闭抽屉。

`trigger/resource-trigger/ResourceTriggerDialog.vue` 负责资源端的触发器列表弹窗，接收完整
`ResourceTriggerApi` 和资源上下文（所属工作空间、资源类型、资源 ID），展示名称、周期和空状态。
添加、编辑按需挂载 `TriggerFormDrawer`，保存成功刷新列表，抽屉关闭后卸载；移除调用资源关联删除接口。
工具菜单的 `tool/tool-card/action-dropdown/TriggerToolAction.vue` 为自定义工具、工作流工具提供入口，
智能体菜单通过 `application/application-card/action-dropdown/TriggerApplicationAction.vue` 提供相同入口，
由 `ApplicationView` 传入完整 `ResourceTriggerApi` 和当前智能体，固定当前智能体为执行资源。
两个入口均在点击后挂载列表弹窗，关闭后卸载，暂不增加权限判断。

`trigger/components/TriggerTaskPopover.vue` 接收分页记录的 `tasks`，在任务列按智能体和工具
展示数量标签，悬浮时分组显示资源图标及名称；无任务时显示 `-`，不发起额外请求。

`trigger/execution-record/TriggerTaskRecordDrawer.vue` 通过列表操作列打开，负责执行记录分页、
名称/状态/类型筛选、执行时间排序及跨页浏览。`ExecutionDetailDrawer.vue` 根据当前记录查询详情，
展示智能体问答、工具输入输出、触发错误及工作流节点详情；状态展示通过共享 `EXECUTION_STATUS_OPTIONS` 向 `MkStatusLabel` 传入 `type + label`，筛选复用同一配置的文案。

## 查看关联资源 Action

模型、知识库、应用、工具卡片的 `action-dropdown/` 分别提供
`RelatedResourcesModelAction`、`RelatedResourcesKnowledgeAction`、
`RelatedResourcesApplicationAction`、`RelatedResourcesToolAction`，在更多菜单展示“查看关联资源”。
工作空间列表保留已有入口行为；System 共享模型页增加该 Action，不新增权限判断。
页面传入完整 `RelatedResourcesApi` 和当前资源。Action 点击后按需挂载
`RelatedResourcesDrawer`，传入对应 `RESOURCE_TYPE` 和包含 `workspace_id` 的资源快照；
工作空间 ID 来自资源数据，缺失时提示并停止打开，关闭后卸载抽屉。
共享模型页只传入模型数据、文案和完整 System 共享关联资源 API，不传 `shared` 或工作空间显示标记。
共享模型允许缺少 `workspace_id`；抽屉内部仅在 System 共享资源且为企业版或专业版时显示工作空间列与筛选。
抽屉调用接口时不传工作空间 ID，
Workspace API 内部通过 `getWorkspaceId()` 读取当前路由工作空间。
模型及非工作流工具默认展示“引用此资源的资源”，其他资源默认展示“依赖的资源”。
资源名称仅展示文本，暂不支持打开目标资源。

知识库工作流页面使用 `WorkflowMode.Knowledge` 和 `WorkflowMode.KnowledgeLoop`，空画布使用本地文件数据源节点。
页面只通过 `getKnowledgeDetail` 返回的 `work_flow` 加载画布数据，发布前先校验并保存；返回知识库详情时检查未保存改动。

`KnowledgeCard` 在非批量选择模式下通过 `click` 通知列表进入知识库详情。
`knowledge-detail/index.vue` 查询并展示知识库名称，复用
`ResourceDetailLayout` 生成资料库、工作流、检索优化、授权与集成、设置目录，返回列表时恢复所属文件夹。
资料库包含文档、图片、标签管理；检索优化包含召回测试、问题、自定义分词；授权与集成包含
对话用户、外部检索服务。资料库页面统一放在 `knowledge-detail/library/` 下，包含 `document/`、
`image/`、`tag/`；文档专属组件及 Action 随 `document/` 集中维护。其他页面继续放在
`knowledge-detail/` 下的 `recall-test/`、`question/`、`dictionary/`、`chat-user/`、`external-retrieval/`。
图片、标签管理及这五个页面暂只展示占位内容。
容器通过 `knowledge-detail/context.ts` 提供只读详情与替换能力；设置页复用已加载详情，保存成功后
更新容器数据，同步名称等展示。基本信息复用创建流程的 `KnowledgeBaseForm`，类型配置和校验留在
`setting/base/index.vue` 中，通用知识库标题为“设置”，其他类型为“基础设置”。
通用知识库只有单个设置菜单；Web 的设置分组包含基础设置、文档处理策略、定时同步，
飞书和工作流包含基础设置、定时同步。`setting/document-strategy/` 与
`setting/scheduled-sync/` 分别承接文档处理策略和定时同步，当前仅展示占位内容。
设置菜单的类型筛选由路由维护，不在 View 中重复维护菜单。
当前设置页仅接入 Workspace 路由和 API，暂不增加前端权限判断。
更换向量模型需确认，先保存再重新向量化，整条流程禁止重复提交；向量化失败时保留原模型比较基准，
允许再次保存重试。Web、飞书设置保留未编辑的 `meta` 字段，上传限制使用详情顶层值。
`knowledge-detail/library/document/index.vue` 维护文档列表查询、多选和文档操作，使用 `MkComplexSearch`、`MkTable`。
搜索只提供名称 `name` 和创建者 `create_user`；创建者通过 Workspace `CommonApi.getAllUsers`
加载，支持按 `nick_name` 远程搜索。列表使用 `documentData`、`paginationConfig`、`documentQuery`，
查询方法为 `loadDocuments`，搜索处理为 `handleSearchChange`，搜索变化后回到第一页。
文档名称列显式导入非全局 `MkEditName`，名称上限 128 字符，保存成功后按文档 ID 更新当前行的
名称与更新时间；失败交由组件保留草稿。共享文档只读展示名称，列不叠加表格溢出提示。
名称校验通过 `validate` 回调拒绝 `: \ / ? * [ ]`，命中任一字符时弹出提示并阻止保存。

文档页通过 `onMounted` 加载文档列表，创建者选项在展开下拉或输入关键词时通过 `remoteMethod`
按需加载，不在进入页面时预加载；其他列表页的同类创建者筛选遵循相同方式。不额外监听路由重置状态。切换工作空间
整页加载并返回知识库列表；当前知识库与共享资源入口均从其他页面进入，挂载时初始化筛选和分页。
普通与共享文档列表沿用 v2 的 6 秒轮询间隔，在请求结束后安排下一次静默刷新，保留当前筛选、
分页和勾选，不显示列表 loading；操作请求期间推迟轮询，失败后继续重试，卸载时停止且不再重新调度。
无排序入口。非共享文档显示选择列，按文档 ID 跨页保留选择，搜索或筛选变化时清空；
选中后通过 `footer-batch-actions` 展示批量操作。右侧固定操作列提供启停、向量化、分词索引和更多菜单，
运行或排队中的任务切换为取消入口。Web、飞书提供同步，普通与工作流文档提供原文下载和替换。
单项与批量操作共用页面请求状态，删除和同步先确认，成功后清空选择并刷新，导出和下载保留选择。
文档页及其 Action 的知识库类型统一读取响应式路由参数 `route.params.type`，使用
`KNOWLEDGE_TYPE_KEY` 判断，不从详情或文档数据读取类型，也不通过 `knowledgeType` Prop 传递。
Web 来源地址与选择器仅在单项设置中编辑，批量设置不展示这两个字段。
文档操作统一放在 `document/action-dropdown/`，通过该目录 `index.ts` 导出，页面显式组合各 Action。
文档页行操作使用 `MkTableMoreDropdown` 默认的延迟保留机制，批量操作菜单显式设置 `persistent`；
首次展开才挂载菜单内容，收起后保留 Action 及其弹窗，生命周期统一由公共组件管理。
文档状态展示、筛选配置和任务运行状态判断统一维护在 `document/status.ts`。
文档任务是否排队或执行中通过其中的 `isDocumentTaskRunning(document, taskType)` 判断，
页面及 Action 不重复解析状态字符串；文档或任务状态缺失时返回 `false`。
`EmbeddingDocumentAction` 负责单项向量化与取消向量化，`BatchEmbeddingAction` 负责批量向量化按钮，`GenerateQuestionsAction` 负责单项生成问题与取消生成，`BatchGenerateQuestionsAction` 负责批量生成问题，`SettingDocumentAction` 负责召回及来源设置，
`MigrateDocumentAction` 选择目标知识库，`DocumentTagsAction` 添加已有标签和移除文档标签关联；
生成问题复用公共配置弹窗，其余 Action 按下文维护各自专属弹窗。组件接收完整 Document API、知识库 ID、文档 ID 或文档数组及禁用状态，
点击时快照本次操作对象，内部管理弹窗和请求，成功后通过 `refresh` 通知页面刷新，失败保留输入。
迁移操作集中在 `document/action-dropdown/migrate/`，`MigrateDocumentAction.vue` 负责入口与弹窗按需挂载，
`DocumentMigrateDialog.vue` 负责目标知识库查询、选择及迁移请求；关闭动画结束后卸载，失败保留输入。
Action 继续通过上层 `action-dropdown/index.ts` 导出，单项与批量入口共用；入口文案由必填 `label` 传入，
图标由可选 `icon` 传入，不传时不显示图标。
单项向量化仅传 `document`，内部判断排队或执行状态，固定展示行内图标按钮，分别调用单项向量化和取消接口。
批量向量化仅传 `document-ids`，使用独立的 `BatchEmbeddingAction` 普通按钮；
批量取消向量化继续使用 `BatchCancelTaskAction` 菜单项，单项和批量请求均通过 `v-model:loading` 共用页面操作状态。
向量化相关文件集中在 `document/action-dropdown/embedding/`，包含两个 Action 和共用的 `DocumentEmbeddingDialog.vue`；
Action 仍通过上层 `action-dropdown/index.ts` 导出，弹窗仅在目录内部使用，管理分段范围与确认事件，
请求和成功关闭由各自 Action 负责；打开时快照文档目标，失败保留范围选择。
生成问题相关 Action 集中在 `document/action-dropdown/generate-questions/`，通过上层 `index.ts` 导出。
`GenerateQuestionsAction` 接收单个 `document`，内部判断任务状态并处理生成与单项取消，通过 `display` 区分菜单与图标按钮。
`BatchGenerateQuestionsAction` 接收 `documentIds`，使用独立的批量生成按钮；批量取消继续使用 `BatchCancelTaskAction`。
单项与批量复用公共 `GenerateQuestionsDialog`，Action 打开时保存知识库、文档 ID 快照，
提交同一文档批量接口并通过 `refresh` 刷新状态；通过 `v-model:loading` 复用页面操作状态。
公共弹窗按需挂载、关闭后卸载，不负责选择提交接口。当前尚无段落页，后续段落入口复用公共
弹窗时关闭 `showParagraphScope`，由段落 Action 提交段落接口，不扩展公共弹窗的接口分支。
设置操作集中在 `document/action-dropdown/setting/`，通过上层 `index.ts` 导出两个入口。
`SettingDocumentAction` 接收单个 `document`，展示菜单项；`BatchSettingDocumentAction` 接收
`documentIds`，展示批量设置按钮。入口文案由 `label` 传入，单项图标由可选 `icon` 传入。
两个入口通过 `v-model:loading` 共用页面操作状态，打开时固定操作目标，分别调用单项和批量设置接口。
共用的 `DocumentSettingDialog.vue` 负责表单回填、校验和提交数据，按需挂载、关闭动画结束后卸载；
弹窗通过 `batch` 参数区分批量模式，批量入口显式传入；文档地址和选择器仅在 `!batch` 且为 Web 知识库时显示。
单项保留文档原有 `meta`，批量使用默认配置并将 `allow_download`
放在顶层。请求与成功关闭由 Action 负责，成功通知页面刷新，失败保留表单。
标签组件通过 `manageTags` 区分标签管理与批量添加。
分词索引集中在 `document/action-dropdown/tokenize/`：`TokenizeDocumentAction` 接收单个 `document`，
按运行状态调用单项分词或取消接口；`BatchTokenizeAction` 接收 `documentIds`，仅调用批量分词接口。
两个 Action 均处理全部分段状态，通过 `v-model:loading` 共用页面操作状态，成功后通知页面刷新。
`BatchCancelTaskAction`、
`ExportDocumentAction`、`DownloadDocumentAction`、`ReplaceDocumentAction` 和 `DeleteDocumentAction`
分别负责任务取消、导出、下载、替换与删除，单项和批量入口复用对应组件。
导出操作集中在 `document/action-dropdown/export/`，通过上层 `index.ts` 导出。
`ExportDocumentAction` 接收 `label` 和单个 `document`；`BatchExportDocumentAction` 接收 `label`、
`documentIds`。两个 Action 直接从路由读取 `knowledgeId`，批量 Action 从详情上下文读取知识库名称
作为下载回退文件名，页面不再传 `knowledge-id` 或 `knowledge-name`。
两个 Action 分别调用单项、批量的 Excel/ZIP 接口，批量仅选一个文档时仍调用批量接口。
知识库类型仍只从路由读取。行操作与批量操作均只组合一个“导出”入口，
悬停展开“导出文档 Excel”“导出文档 ZIP”，不再从页面传入 `format`。
子菜单使用默认挂载方式，不指定 `append-to`；下载复用页面 loading，保留列表和勾选状态，
不额外解析下载错误或提示成功，请求结束后统一恢复 loading。
同步操作集中在 `document/action-dropdown/sync/`，通过上层 `index.ts` 导出。
`SyncDocumentAction` 接收 `label` 和单个 `document`，`BatchSyncDocumentAction` 接收 `label` 和
`documentIds`（模板使用 `:document-ids`），不使用 `documents` 或 `batch`。单项 Web 文档同步前校验来源地址；确认前固定本次目标与路由类型，
分别调用 Web 或飞书的单项、批量同步接口，共用页面 loading，成功后通知页面刷新。
直接请求的 Action 通过 `v-model:loading` 共用页面操作状态，各 Action 自行管理请求、
防重复提交、成功提示与失败处理，不额外抽取统一请求封装；需要刷新时发出 `refresh`，导出与下载不发出。
`DeleteDocumentAction` 单个删除传 `document`，确认框展示文档名称并调用单个删除接口；
批量删除传 `batch` 和 `document-ids`，确认框展示数量并调用批量删除接口。
删除后分页总数和页码回退由页面重新查询服务端处理，不在 Action 中维护分页数据。
启停开关直接使用页面内的 `el-switch`，由页面 `handleChangeActive` 管理请求，
接口成功后刷新列表回显，不在请求前切换状态，不单独封装 Action。
页面保留列表、多选、任务状态展示判断与刷新方法，不维护各 Action 的请求流程。
`DocumentStatus`、`DocumentTags` 等纯展示组件继续留在 `document/components/`。
页面不再维护这些弹窗 Ref 和打开方法。行内更多菜单使用 `MkTableMoreDropdown`；批量操作栏使用
`MkDropdown` 搭配非 text 的 More 图标按钮和 `MkDropdownMenu`，点击展开。
批量 More 开启 `hide-when-empty`，按标准菜单插槽判断空内容，不强制开启 `persistent`；不检查业务 Action 内部的条件渲染。
不新增前端权限判断；共享文档不展示选择列及操作入口。
文档分页接口维护在 `workspace/knowledge/document.ts`，页面管理 loading。文件状态表头使用
`MkDropdown` 单选筛选全部、成功、失败、索引中、分词索引中、排队中和生成中；查询组合
`status` 与可选的 `task_type`，切换选项清除旧任务类型并回到第一页，保留名称和创建者条件。

文档详情路由暂未启用，System 知识库详情路由暂未注册。

`KnowledgeWorkflowView` 复用 `ButtonDefaultModelSetting`，从知识库详情读取默认模型配置，
随工作流保存提交并将配置传入画布；支持应用到所有节点，保存失败回滚至已保存配置。

## 智能体复制 Action

`application/application-card/action-dropdown/copy-application-action/` 提供 `CopyApplicationAction`
和 `CopyApplicationDialog`。列表按 `application.workspace.copy(id)` 控制入口，传入完整应用 API、
源应用及当前文件夹 ID。点击后查询完整详情，深拷贝配置并移除原 ID 等资源元数据，名称默认追加
“副本”，确认后创建到打开时的当前文件夹。复制成功刷新列表及用户权限，简易应用进入设置页，
工作流应用进入画布；请求失败保留表单。弹窗按需挂载，在 `closed` 后卸载。

`workflow/application/index.vue` 在默认模型设置之前引用 `ButtonTemplateStore`，
通过 `open` 关闭调试面板，通过 `use(template)` 执行覆盖确认和请求；加载、保存或发布期间禁止打开。
页面确认覆盖后提交 `work_flow_template`，重新加载详情、画布和已保存基准；完成后通过按钮组件的
`close()` 关闭模板中心并提示成功。取消或失败保留模板中心。

## 智能体工作流调试

调试对话面板已内聚到会话模块:`@/conversation-panel/view/debug/index.vue` 自带面板显隐、
放大/还原(放大/关闭按钮由 `@/conversation-panel/components/header/debug/index.vue` 提供)及局部样式，
通过 `open()`、`close()` 控制,关闭时重置放大状态,保留关闭动画。
`ApplicationWorkflowView` 直接渲染调试按钮和 `<DebugPanel ref="debugPanelRef" />`(即上述 debug 视图),
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

## 工具工作流调试

`workflow/tool/index.vue` 在默认模型设置后提供调试按钮，先校验画布，有未保存改动时
保存成功后再打开调试。打开默认模型设置或发布历史时关闭调试抽屉。
`tool/debug/DebugDrawer.vue` 接收 `toolId`，通过 `open(graph)` 从已保存图的工具基础节点读取输入字段，
管理字符串、整数、浮点数、布尔值及 JSON 数组/对象参数，校验后交给 `ResultDrawer` 运行。
`ResultDrawer.vue` 负责 SSE 消费、流式回复、输出参数和节点执行详情，复用现有
`ConversationStream`、回复块聚合与渲染组件、`ExecutionDetailContent`，不使用 v2 的动态 API 或聊天 Store。
运行结束后读取执行记录；表单节点通过同一 `chat_record_id` 和 `position` 续跑。
运行期间禁止重复执行，返回参数保留输入，再次运行创建新记录；关闭或卸载中断前端读取，
不表示服务端任务已停止。两个抽屉复用 `MkDrawer`，关闭动画期间保持挂载。

## 工具工作流返回导航

`workflow/tool/navigation.ts` 统一提供 `goBack(folderId?)`，使用资源上下文判断返回范围：
System 资源管理返回 `system-resource-tools`，System 共享资源返回 `system-shared-tools`，
Workspace 返回 `workspace-tools` 并携带当前 `workspaceId` 和可选 `folderId` query，
由工具列表的 `FolderTree` 恢复所属目录。工具 View 只负责历史预览退出、未保存确认及保存后退出，
不再维护路由跳转细节。

## 工具工作流导出

`ToolWorkflowView` 更多菜单底部提供“导出工作流”，复用 `ToolApi.exportTool` 下载 `.tool` 文件。
存在未保存画布改动时先保存，保存失败不发起导出；导出期间禁止重复操作并暂停自动保存。
文件内容由后端从已保存工作流生成，沿用公共下载方法的文件名与错误响应处理。

## 工作流页面加载状态

application、tool、knowledge 的 WorkflowView 统一使用一个 `loading` 控制整页遮罩和操作禁用，
不再拆分 `saving`、`publishing`、`exporting` 或 `openingDebug`。最外层操作负责开启状态并在
`finally` 中释放；内部保存、加载详情方法只返回 Promise，不修改 loading。发布的校验、保存、发布，
模板覆盖及重新加载，以及调试前保存、导出前保存均保持完整流程的 loading。
自动保存同样复用该状态；历史显隐和退出确认属于交互状态，独立维护。抽屉内部请求状态仍由抽屉管理。

### 知识库工作流导航与导出

`workflow/knowledge/navigation.ts` 统一返回入口：Workspace 将详情中的 `type` 通过 `KNOWLEDGE_TYPE_MAP` 转为字符串后返回当前知识库详情，详情尚未加载时使用 `WORKFLOW`；System 资源管理和共享资源返回各自知识库列表。
历史模式下返回只退出预览；普通编辑态返回保留未保存确认。更多菜单的导出工作流先保存未提交改动，
再调用专用 `.kbwf` 导出接口；保存失败不导出。知识库原有文件上传、数据源表单与任务轮询调试流程保持独立。

## 智能体工作流发布

`ApplicationWorkflowView` 直接管理发布按钮与 `EditPublishVersionDialog` 的发布模式，
点击后先校验画布，通过后调用弹窗的 `open()` 打开“发布内容”表单；
校验失败不打开弹窗。表单通过 `submit` 将标题和更新说明交给 `ApplicationWorkflowView`。
页面复用整页 `loading`，提交时保存当前工作流、调用发布接口，映射 `name` 为
`publish_name`，更新说明使用 `publish_desc`。成功后更新详情与保存时间，关闭弹窗并提示；
保存或发布失败保留表单以便重试。旧 `ApplicationPublishDialog` 不再使用。

## 工作空间首页

`home/index.vue` 组合快捷创建、资源概况、使用统计和 Top 5 排行榜。首页按当前路由
`workspaceId` 重新挂载各业务区，切换工作空间时清理旧筛选、数据和抽屉。
首页普通组件放在 `home/components/`；排行榜流程集中在 `home/ranking/`，包含
`HomeRankings.vue` 和 `RankingDrawer.vue`。
排行配置与展示计算保留在各自组件内，不单独维护首页 `constants.ts`、`statistics.ts`。
`HomeView` 向 `HomeResourceOverview` 传入完整首页 API 对象，组件通过 `typeof HomepageApi`
约束 `api` Prop 并调用 `props.api`。资源概况、使用统计和排行均由 `HomeView` 显式传入
`workspaceId`，排行榜继续向详情抽屉传递；调用首页接口时逐次传入此 ID，不在 API 内读取路由。
顶部切换工作空间时统一整页加载，重载统计数据并清理旧筛选与排行榜详情，统计组件无需额外设置工作空间 key。

快捷创建通过插槽复用智能体、知识库、工具和模型的现有入口，目标文件夹为当前工作空间根目录；
保留创建流程中的用户资料刷新及详情／工作流导航，停留首页的成功操作刷新资源概况与智能体选项。
资源卡片使用命名路由进入当前工作空间的对应列表。

`HomeView` 管理监控区的智能体列表查询、选择器和 `applicationId`，向 `HomeStatistics`
传入完整 `HomepageApi` 与选中的 ID。统计组件监听工作空间和智能体 ID 变化加载数据，
通过 `application` 插槽提供 `loading`，由 View 渲染选择器并控制请求期间禁用。
选择器通过 `remote-method` 按名称请求前 200 个智能体；选项和选中值复用 `ApplicationIcon`，
全部智能体使用 `icon_all_outlined`。清空回到全部，已选智能体图标独立保留，避免搜索结果变化后丢失。

统计区、排行榜和详情抽屉直接复用 `MkDateRange`，将 `change` 的 `startTime`、`endTime`
映射为接口的 `start_time`、`end_time`。默认查询与组件的过去 7 天预设一致，结束日期为当天。
抽屉初始查询继承排行日期，通过 `MkDateRange.defaultValue` 同步回填日期选择器；
公共组件暂不支持禁用。智能体筛选仅影响使用统计。
活跃用户汇总是每日活跃人数之和，标为“累计活跃人次”；反馈展示点赞和点踩数量。
`HomeStatistics` 直接使用公共 `MkLineChart`，传入日期和指标系列；实例、尺寸监听和销毁由
`MkEchart` 管理，不再保留首页专用图表包装组件。

排行榜详情继承打开时的日期与排行类型，独立维护名称搜索、分页和导出；搜索、日期及页容量
变化重置页码，排名包含分页偏移。占比使用工作空间同期总量，不用 Top 5 或搜索结果合计替代。
各业务区分别维护 loading 和失败状态，失败不伪装为零数据；首页不新增前端权限控制。

`application/components/ButtonCreateApplication.vue`、`knowledge/components/ButtonCreateKnowledge.vue`
与 `tool/components/ButtonCreateTool.vue` 支持 `trigger`（默认 `click`）、
`popperStyle`、`popperClass` 和 `fitTriggerWidth`，三者保持相同的触发与浮层配置约定。
`popperClass` 同时应用到浮层和菜单。
默认菜单保持固定宽度；传入 `popperStyle.width` 或 `popperClass` 时，菜单填满浮层，宽度由调用方控制。
`fitTriggerWidth` 默认关闭，只有显式开启时才在展开时测量自定义触发器宽度，并覆盖 `popperStyle.width`；
首页快捷创建开启此配置，其他页面不因使用触发器插槽而自动等宽。`w-full` 样式类不触发测量。

首页排行榜卡片由 `home/components/ranking/RankingCard.vue` 渲染，接收 `title`、`records`、
`loading`、排行类型 `kind` 及总量 `total`，名称读取与占比计算由卡片内部处理；`detail` 事件交给父组件打开抽屉，`description` 插槽提供
`record`、`index`，由父组件定义每行说明文案。

排行榜 API 由 `HomeView` 传入 `HomeRankings`，再传给 `RankingDrawer`。两者的 `api`
均使用 `typeof HomepageApi` 约束，查询、汇总和导出统一通过 `props.api` 调用。

## 知识库工作流执行记录

`workflow/knowledge/ButtonExecutionRecord.vue` 封装更多菜单入口、抽屉挂载与打开逻辑，接收
`knowledgeId`，菜单属性（如 `divided`）透传到 `MkDropdownItem`，内部提供知识库 Workflow API。
`workflow/knowledge/execution-record/` 维护记录列表和详情抽屉，由该按钮组件打开，
关闭动画结束后卸载。列表复用 `MkComplexSearch`、`MkTable` 和 `MkStatusLabel`，支持发起人、
状态筛选及跨页浏览，每 6 秒刷新；关闭或卸载停止轮询。待执行、执行中任务经确认后取消，成功刷新列表。
抽屉接收完整知识库 Workflow API；详情查询复用调试任务接口，使用 `ExecutionDetailContent` 展示节点结果。

## 智能体详情占位页面

`application-detail/integration/index.vue` 承接接入第三方，目前仅展示占位内容，
标题及详情框架继续由 `ResourceDetailLayout` 提供。设置菜单按资源类型选择现有简易设置页面
或高级智能体全屏工作流，不另建高级设置 View。

## System 资源管理模型与工具

`system/resource-management/model/index.vue` 与 `tool/index.vue` 使用
`MkViewLayout`、`MkComplexSearch` 和 `MkTable` 展示跨工作空间资源。
模型操作列使用 `EditModelAction display="button"` 展示编辑按钮，其余操作放入 `MkTableMoreDropdown`；
`EditModelAction` 透传 `display` 给 `MkAction`，默认保持菜单模式，内部管理编辑抽屉，保存后发出 `refresh`。
模型和工具仅编辑、资源授权四个 Action 使用 `MkAction` 并透传显式 `display`，默认菜单模式；
其他业务 Action 继续使用 `MkDropdownItem`，页面按现有布局显式选择按钮或菜单。
工具操作列保留独立启停开关，
其余操作放入 `MkTableMoreDropdown`。菜单开启 `persistent`，业务 Action 使用 `MkDropdownItem`，
保留各自 API、权限条件、事件和浮层生命周期。资源管理页保留带引用提示和分页回退的独立删除流程。
名称、类型、创建者（工具另含来源）筛选和工作空间表头筛选变化后回到第一页；分页大小变化由
`MkTable` 重置页码。工作空间列及选项查询只在企业版开启，`workspace_ids` 沿用 JSON 数组字符串。
页面使用 v3 的 System 权限方法保留迁移前已有的操作权限，不增加创建、导入、批量或复制入口。
删除保留资源引用数量提示，删除末页最后一条后退回上一页。

模型复用编辑抽屉、参数设置、授权和关联资源 Action；工具复用各类型编辑表单、启停、启动参数、
MCP 配置、授权、导出、触发器和执行记录。页面显式传入对应 System 业务 API。
商店工具只修改名称，不开放模板代码编辑；编辑与启停合并返回数据，保留列表中的工作空间等展示字段。
工具维护表单的 API 联合包含 System 资源对象，该范围没有 `postTool`，不通过伪造创建接口满足类型。

资源管理中的工作流进入 `system-resource-workflow-tool`，由 `ToolWorkflowView` 选择 System
工具、工作流和模型 API，并把工作流 API 传给发布历史与调试抽屉；返回资源管理工具列表。
`TriggerToolAction` 和 `ResourceTriggerDialog` 透传可选 `toolApi`、`toolWorkflowApi`，
由 `TriggerFormDrawer` 查询当前资源的完整输入定义；未传时保持 Workspace 默认接口。

工具工作流按三种 `resourceScope` 选择完整工具、工作流与模型 API，并透传到默认模型、历史、调试抽屉。
System 两种工作流入口只传 `toolId`，不传路由工作空间；共享范围默认模型选项使用共享模型列表。

## 资源详情页自定义标题栏

标题栏能力统一放在 `layout/ResourceDetailLayout.vue`，不另建 Header 组件或注入上下文。
Layout 预留整个右侧标题栏的 `headerTarget`，通过 `RouterView` 作用域插槽将 `headerTarget`
和当前路由 `title` 作为 props 直接传给子页面，不修改路由配置。
详情子页面从该 Vue 文件导入 `ResourceDetailPageProps` 并声明 props。普通页面无需编写标题栏模板，
由 Layout 显示默认路由标题。需要自定义的页面通过 `defineExpose({ customHeader: true })` 声明，
再使用 `<Teleport v-if="headerTarget" :to="headerTarget">` 组合标题、搜索与操作。
Layout 读取当前页面实例的声明决定是否显示默认标题；默认和自定义标题模式均保留挂载位置，不增加路由字段。
不需要标题栏的页面通过 `defineExpose({ hideHeader: true })` 隐藏整个主区 Header，包括挂载位置和留白；
`hideHeader` 优先于 `customHeader`，未声明时保持原有标题行为，切换页面后按当前实例恢复。
Layout 保留标题栏固定位置和外层间距，页面负责内部布局。
切换子页面时随 Teleport 卸载清理内容，不需要注册计数或 DOM 检测。
资源入口只负责详情数据和侧栏 `resource-header`，无需转发标题栏属性。
文档页将标题与搜索放入标题栏，表格在正文中独立显示 loading。

普通资料库（`KNOWLEDGE_TYPE.BASE`）的非共享文档页通过 MkTable 的 `body-prepend` 插槽展示
公共 `MkQuickCreate`，类型读取已有知识库详情上下文，不重复请求详情。
页面通过 `@create="handleCreateDocument"` 接收名称，管理创建请求及 `creatingDocument`，通过 `loading` 传给组件。
创建成功后调用组件 `close()`、显示成功提示、保留筛选条件并回到第一页刷新，刷新失败不恢复已提交草稿。
组件只维护输入及空名称禁用，创建失败时页面不关闭组件，保留草稿供重试。
入口独立于文档数组，在空列表中同样显示，不计入分页或批量选择；不新增前端权限判断。

文档页的筛选选项、状态和事件集中在 `// 过滤项` 下：文件状态、启用状态、召回处理显式使用
`MkTableFilter mode="single"`，标签使用 `mode="cascader"`。文件状态按 v2 提供成功、失败、
索引中、分词索引中、排队中、生成中，同时映射 `status` 与可选 `task_type`；切换到非任务状态
或全部时清除任务类型。启用状态保留布尔 `false`，召回处理复用 `DOCUMENT_HIT_HANDLING_LABELS`。
标签首次打开时按普通／共享范围查询知识库标签，成功后通过非空选项复用缓存（始终包含“无标签”），
不额外维护 loaded 标记；普通布尔请求锁防止重复请求，失败释放后下次打开可重试。
标签级联沿用 MkTableFilter 默认的父子独立选择和隐藏复选框外观；组件内部保留原始勾选，
对外将父组转换为叶子值并去重。页面直接将回写的叶子标签 ID 数组用于查询，
“无标签”使用 `NO_TAG`；页面不维护父组展开或去重逻辑。
任一筛选确认或重置后回到第一页查询，保留其他筛选和名称／创建者搜索条件。
标签列使用页面专属 `components/DocumentTags.vue`，接收 `document`，展示标签数量，
悬浮时显示标签名与值，长文本省略并保留 title。数量优先读取 `tag_count`，缺省时使用标签数组长度，
无标签时仅显示添加入口。添加按钮阻止点击冒泡，通过 `add(documentId)` 通知调用方；
当前文档页尚未接入添加弹窗与保存接口，不新增权限判断。

文件状态的解析、聚合与展示统一放在文档页的 `components/DocumentStatus.vue`。组件接收 `status`、`statusMeta`，按从右起的任务位置解析向量化、生成问题、
同步、分词索引；聚合优先级为取消中、执行中、排队中、失败、取消完成、成功，
同优先级取字符串最左侧的任务，忽略 `n` 及未知状态；无有效任务时显示 `-`。
汇总与悬浮明细均复用 `MkStatusLabel`，通过文档本地 `status.ts` 的 `DOCUMENT_STATUS_OPTIONS`
传入图标类型和文案；`DOCUMENT_STATUS_FILTER_OPTIONS` 复用对应文案并维护筛选请求映射。
文档配置独立于执行记录配置。保持 v2 的取消完成显示成功规则，不修改通用状态语义。
悬浮内容按需渲染，展示各任务名称、状态、成功分段数／总数和时间；分段计数读取 `status_meta.aggs`，
成功数只累计状态 `2`，失败与取消完成的进度使用危险色。
时间读取 `state_time[taskType]` 的排队时间，取消完成读取取消完成时间；缺失元数据使用 0/0 并隐藏时间。


## Workspace 共享知识库详情

知识库列表根据当前目录进入普通或 `workspace-shared-knowledge-detail` 共享详情路由。
两者复用 `knowledge-detail/index.vue` 和文档页，由页面通过 `isWorkspaceSharedResource()`
选择 `workspace/knowledge/` 或 `workspace/shared/knowledge/` 的完整 API 对象。
共享详情目前仅提供资料库中的文档页，设置与工作流尚未接入共享接口，不注册对应共享入口。
容器监听工作空间、知识库和资源范围变化重新加载；共享详情返回列表携带 `folderId: 'shared'`，
普通详情继续恢复所属文件夹。文档创建者选项在共享范围使用 System `CommonApi`，普通范围使用
Workspace `CommonApi`；范围变化同时清空搜索控件、筛选、创建者选项与分页。

## 智能体对话用户

`application-detail/chat-user/index.vue` 通过 `hideHeader: true` 隐藏详情主区标题栏，负责工作空间智能体的用户组查询、
用户搜索和分页、自动授权及用户授权保存。内部使用普通 Flex 双栏容器，不嵌套 `MkViewLayout`；
外层 `ResourceDetailLayout` 统一负责标题栏显隐和整体滚动，内部视觉排列与 System 用户组页面对齐。
侧栏使用 `w-sidebar-expanded` 和 `MkSearchList`，由列表统一管理搜索、选中态、独立滚动和空态。
右侧展示组名、成员数和自动授权；下方工具栏左侧保存、右侧 `MkComplexSearch`，
用户列表复用 `MkTable` 及其高度约束，无用户组时显示空态，不额外添加主区滚动容器。
通过 `workspace/chat-user.ts` 请求；当前不接入 `perm`。勾选按当前用户组跨页保留，切换组时清空；
自动授权开启时禁用手动授权，切换成功后清空旧勾选并重新读取用户状态。筛选和用户组切换回到第一页，
页面通过 `onMounted` 加载用户组；切换工作空间由顶部入口整页加载，不额外监听路由重置状态，
也不为搜索组件设置工作空间或智能体 key。来源标签复用登录方式枚举与标签，兼容 `OAUTH2` 返回值。

## 智能体对话日志

`application-detail/chat-log/index.vue` 参考 `system/operate-logs`，通过 `customHeader` 和 Teleport
使用详情布局的标题栏，组合标题、`MkDateRange`、`MkComplexSearch`、导出和清除策略入口，
不嵌套 `MkViewLayout`。挂载时查询过去 7 天，搜索、日期和反馈筛选变化后回到第一页，
不监听工作空间路由参数，也不新增权限判断。
列表使用 `MkTable`，勾选用于导出；无勾选时导出当前筛选结果。列表和导出使用同一组查询条件，
切换筛选或分页后清空旧选择。点赞、点踩最小值使用 `MkTableFilter mode="custom"` 的默认作用域插槽编辑，
页面只维护已生效值和全 0 的 `resetValue`；浮层、草稿、重置与确认由公共组件管理，确认或重置后重新查询。
自定义日期清空后清空列表并禁用导出，重新选择有效日期再查询。
来源枚举位于 `api/enums/chat-log.ts`，页面标签位于本功能的 `constants.ts`。

`clean-strategy/` 按操作日志页拆分 `ButtonCleanStrategy` 和 `CleanStrategyDialog`，
每次打开重新读取智能体详情；日志保留天数为 1–100000，文件保留天数不超过日志保留天数。
保存使用专用清除策略接口，只更新当前智能体，成功刷新详情上下文后关闭，失败保留弹窗。
详情上下文的 `refreshApplicationDetail(showLoading = true)` 默认显示整页 loading；
清除策略弹窗在打开和保存后均传 `false`，仅由弹窗自身的 loading 管理请求，避免内外重复遮罩。
传 `false` 的请求不修改外层 loading 的开始或结束状态。
点击日志行打开本功能的 `ChatLogDetailDrawer.vue`，选择列只处理勾选，不打开详情。
详情抽屉参考 v2 使用当前摘要作为标题，宽度为 `60%`，暴露 `open()`、`close()`。
页面按需挂载后调用 `open()`，在 `closed` 后清空当前记录并卸载，保留关闭动画。
底部上一条／下一条切换整条对话日志；页面负责当前记录、首尾禁用及跨列表分页查询，
跨页成功后同步列表页码并切换至首条／末条，失败保留原记录和页码，加载期间禁用切换。
正文暂时留空，不查询或展示聊天内容，也不显示聊天记录分页器。
添加到知识库的页面组件尚未接入。
