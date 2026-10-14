# views 目录说明

本文档是页面职责和页面功能代码组织规则的唯一依据。新增、移动、删除页面，改变页面职责，或
调整页面专用代码的位置前，应先阅读并同步更新本文档。

## 放置规则

- 创建、保存或提交表单时，使用页面／弹窗内容容器的 loading 遮罩，或仅使用提交按钮的 loading，
  不使用 `el-form.disabled` 或给每个字段、子表单逐项传入提交状态的 `disabled`。
  方法入口保留重复提交保护，关闭、取消及步骤切换仍可按提交状态禁用；权限、只读、字段联动和
  选项加载等业务禁用条件继续保留，不与提交 loading 混用。

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
  集中维护行操作、批量操作及其专属弹窗；分段页按明确需求使用 `document-detail/action-dropdown/`，
  按迁移和生成问题分组维护批量按钮与单项菜单 Action，不因此扩展其他普通页面的目录规则。
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
│       ├── EmbeddingKnowledgeAction.vue # 提交知识库向量化任务
│       ├── GenerateQuestionsAction.vue # 知识库生成关联问题
│       ├── sync-knowledge-action/       # Web 知识库同步入口与方式选择弹窗
│       ├── KeywordIndexKnowledgeAction.vue # 分词索引入口
│       ├── McpConfigKnowledgeAction.vue # MCP 配置查询、展示与复制
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
组合单项转移、删除 Action，并管理批量选择、全选、批量转移与批量删除。工作空间共享知识库保持只读，
不传操作插槽并传入 `disabled`；System 共享知识库页传入 `shared`、不传 `disabled`，保留共享标识，
并组合同步、向量化、生成问题、设置、分词索引、MCP 配置、关联资源、导出及删除等菜单操作。
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
设置菜单由 Workspace、System 资源管理和 System 共享知识库列表各自使用 `MkDropdownItem` 渲染，
通过页面的 `handleOpenKnowledgeSetting` 跳转，不单独封装 Action，也不新增权限判断。
通用类型进入各自的 `workspace-knowledge-setting`、`system-resource-knowledge-setting`、
`system-shared-knowledge-setting`，其他类型进入对应前缀的 `knowledge-base-setting`。
三个入口均传入知识库 ID 和 `KNOWLEDGE_TYPE_MAP[knowledge.type]`；仅 Workspace 传入当前
`workspaceId`。点击阻止事件冒泡，避免同时进入卡片详情；Workspace 共享知识库仍不展示操作菜单。
“设置”之后依次组合 `KeywordIndexKnowledgeAction` 和 `McpConfigKnowledgeAction`，接收完整
Knowledge API 并复用页面操作 loading。分词索引不增加确认弹窗，调用成功后只提示“操作成功”；
`McpConfigKnowledgeAction` 内直接查询 MCP 配置字符串，通过 `MkDialog` 只读展示并提供悬浮复制，
配置为空时禁用复制，关闭动画结束后清理配置；弹窗外壳由 `MkDialog` 按需挂载和卸载。
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
表单挂载时不请求视觉选项；开启视觉增强、切换增强策略或回填已启用的策略时，模型增强只加载
视觉模型和供应商，工具增强只加载工具。两类请求分别维护 loading，模型刷新只请求模型及供应商。
视觉模型和工具选项按当前资源范围选择 Workspace、System 资源管理或 System 共享资源的完整 API，
通过 `isSystemResource()`、`isSystemSharedResource()` 判断，供应商继续使用共用 Provider API。

`ButtonCreateKnowledge` 内聚四类创建浮层 Ref 和打开动作，列表页传入目标 `folderId`，通过
`refresh` 刷新列表。入口支持 `trigger` 插槽替换默认创建按钮，下拉使用 `persistent`。默认使用
Workspace 知识库 API；System 共享知识库页传入完整 System 共享知识库 API，创建、导入与工作流创建
均不读取工作空间 ID。创建入口及模板中心只接收一个完整 Knowledge API，工作流创建也使用该对象的
`postKnowledgeWorkflow`；已创建知识库的工作流画布接口仍由 `workspace/knowledge/workflow.ts` 维护。
各创建浮层接收 `folderId`，通过 `open()` 打开；工作流额外接受可选的商店模板。共用的
`KnowledgeBaseForm` 负责名称、描述、Embedding 模型必填校验以及工作空间和共享模型查询，
根据资源范围在组件内部选择模型接口：System 资源管理使用 System Model API，
System 共享使用 System 共享 Model API，Workspace 普通与共享资源均使用 Workspace Model API，
通过 `getModelListWithShared({ model_type: 'EMBEDDING' })` 加载模型选项；
Workspace 普通与共享场景均合并当前工作空间模型与已授权共享模型，
复用 `SelectModel`，允许创建模型后刷新选项。Web、飞书的特有字段留在对应弹窗中。
模型加载后仅在未选择时默认选中首个可用模型；重置表单时恢复该默认值，无可用模型时保持为空。
刷新选项不覆盖用户选择或设置页回填的模型。
创建前校验表单，提交期间禁止重复提交和关闭；成功后刷新用户基础资料并通知列表刷新，
普通类型将接口返回的 `knowledge.type` 通过 `KNOWLEDGE_TYPE_MAP` 转为字符串后进入文档列表，工作流进入画布。常驻弹窗在关闭动画结束后清理表单，打开时只回填本次模板与显示，工作流模板使用
`cloneDeep` 隔离；创建流程默认使用 Workspace API，不通过路由字符串推测 System 范围；System
共享页通过入口显式传入对应 API，创建成功后仅刷新共享列表，不进入工作空间详情或工作流路由。
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
│       └── McpConfigAction.vue      # MCP 配置查询、展示与复制
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
`InitParamDialog`，`McpConfigAction` 获取 MCP 工具详情后，在 Action 内通过 `MkDialog` 只读展示
`code ?? ''` 并提供悬浮复制，配置为空时禁用复制，关闭动画结束后清理配置。
弹窗外壳由 `MkDialog` 按需挂载和卸载。工作流 Action 进入
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
├── knowledge/
│   └── index.vue
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

`KnowledgeSharedView` 使用 System 共享知识库 API，复用 `KnowledgeCard`、创建入口和模板中心。
卡片点击通过页面的 `handleOpenKnowledge` 进入 `system-shared-knowledge-detail`，
携带知识库 ID 和由 `KNOWLEDGE_TYPE_MAP` 转换的类型。资源管理知识库表格在向量化按钮旁组合
`icon_admin_outlined` 详情按钮，进入 `system-resource-knowledge-detail`。两个入口不携带 Workspace ID。
创建、模板创建和导入均使用 System 共享接口；Web 同步、向量化、关联问题、分词索引、
MCP 配置、关联资源、导出与删除通过复用 Action 组合，设置菜单由页面直接跳转到 System 共享设置页。
授权工作空间暂保留 TODO，不组合工作空间专用的文件夹移动或批量操作。

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

`system/identity/workspaces/index.vue` 的成员表按用户合并选择框、姓名和用户名，
通过 `MkTable.selectionGroupKey="user_id"` 联动当前页同一用户的角色记录；
行标识仍使用 `user_relation_id:role_id`，底栏按选中记录行数统计，不按用户数统计。
批量移除确认说明记录数与涉及用户数，请求按 `user_relation_id` 去重，不按用户 ID 丢弃角色记录。
列表加载前清空选择，覆盖搜索、分页、工作空间切换及操作后的刷新；不新增跨页选择或修改接口协议。

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

| 页面                                            | 功能说明                                                             |
| ----------------------------------------------- | -------------------------------------------------------------------- |
| `application/index.vue`                         | 工作空间智能体目录与智能体卡片页面                                   |
| `application-detail/index.vue`                  | 工作空间智能体详情上下文与资源详情布局                               |
| `application-detail/overview/index.vue`         | 智能体概览内容                                                       |
| `application-detail/setting/index.vue`          | 简易智能体设置内容                                                   |
| `workflow/application/index.vue`                | 智能体工作流页面头部与全屏画布                                       |
| `workflow/knowledge/index.vue`                  | 知识库工作流加载、自动保存、发布历史、模板覆盖、导出、调试与全屏画布 |
| `workflow/tool/index.vue`                       | 工具工作流页面头部与全屏画布                                         |
| `chat/index.vue`                                | Chat 入口的对话页面                                                  |
| `error/index.vue`                               | Admin 未匹配路由和全局 404 页面                                      |
| `home/index.vue`                                | Workspace 首页                                                       |
| `knowledge/index.vue`                           | 工作空间知识库目录与知识库卡片页面                                   |
| `knowledge-detail/index.vue`                    | 知识库详情页面                                                       |
| `knowledge-detail/external-retrieval/index.vue` | 外部检索服务开关、API 地址与调用示例、MCP 配置的只读展示及复制 |
| `knowledge-detail/library/tags/index.vue`       | 标签分组查询、创建、重命名、单值编辑、删除与关联文档管理             |
| `knowledge-detail/workflow-transform/index.vue` | 非工作流知识库转换说明、确认与进入画布                               |
| `document-detail/index.vue`                     | 普通 Workspace 文档分段查询、目录定位、批量操作、新增、编辑与详情    |

|
| `knowledge-detail/setting/base/index.vue` | 知识库基本信息、来源配置与上传限制设置 |
| `knowledge-detail/setting/document-strategy/index.vue` | Web 知识库文档处理策略回填、校验与保存 |
| `knowledge-detail/setting/scheduled-sync/index.vue` | Web、飞书与工作流知识库定时同步设置与日志 |
| `login/index.vue` | Admin 登录页面 |
| `login/forgot-password/index.vue` | 忘记密码页面 |
| `model/index.vue` | 工作空间模型目录与模型卡片页面 |
| `system/identity/groups/index.vue` | 用户组列表页面 |
| `system/identity/resource-authorization/index.vue` | 工作空间用户组与用户的分类资源授权页面 |
| `system/identity/roles/index.vue` | 角色列表页面 |
| `system/identity/users/index.vue` | 用户列表页面 |
| `system/identity/workspaces/index.vue` | 工作空间列表页面 |
| `system/chat-management/user-groups/index.vue` | 对话用户组及组成员管理页面 |
| `system/chat-management/users/index.vue` | 对话用户列表、配额及用户导入管理页面 |
| `system/chat-management/portal-setting/index.vue` | 门户基本信息、访问开关、认证配置、跨域地址编辑与门户预览 |
| `system/settings/theme/index.vue` | 系统外观设置和登录外观预览页面 |
| `system/settings/authentication/index.vue` | 系统登录及认证源配置页面 |
| `system/settings/email/index.vue` | 系统邮件 SMTP 服务配置页面 |
| `system/operate-logs/index.vue` | 系统操作日志查询与清理页面 |
| `system/resource-management/model/index.vue` | System 模型分页、筛选、编辑、授权与删除 |
| `system/resource-management/tool/index.vue` | System 工具分页、筛选、维护与工作流入口 |
| `system/shared-resources/model/index.vue` | System 共享模型查询与模型卡片页面 |
| `system/shared-resources/tool/index.vue` | System 共享工具查询与工具维护页面 |
| `trigger/index.vue` | 工作空间触发器查询、新建、编辑及单项和批量启停、删除 |
| `tool/index.vue` | 工作空间工具目录与工具卡片页面 |

身份与权限用户组页（`system/identity/groups/index.vue`）的成员顶部搜索仅提供用户名、姓名；
用户来源使用 `MkTableFilter mode="single"` 放在表头，与搜索条件合并后向接口传 `source`。
筛选变化回到第一页；选择“全部”移除来源条件，保留用户名、姓名搜索。

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
`applicationId`、`selectedId`、`disabled` 和 `visible`，接收 `update:visible`、`open`、`preview`、
`restore` 事件。每次打开重新查询，编辑成功后关闭弹窗并重新调用 `getWorkflowVersions` 刷新列表，
不向页面发送更新事件；保存失败保留弹窗与草稿。所在 `MkDropdown` 设置 `persistent`，避免收起菜单时销毁面板入口。

`workflow/components/publish-history/PublishHistoryDrawer.vue` 为纯 UI 面板，接收 `versions`、`loading`、
`saving`、`selectedId`，保留传入顺序并将首项标为“最近发布”，显示标题、发布人及创建时间。
内部管理编辑与更新说明弹窗，通过 `submit(payload, versionId)` 交给业务组件保存，成功后由业务组件
调用 `closeEdit()` 关闭编辑弹窗。通过 `preview`、`restore` 通知业务组件，不接收 API、不查询数据，
也不操作路由或画布。面板复用 `MkDrawer`，通过 `v-model` 控制显隐，宽度 320，使用
`top-header`、`h-layout-content` 留出页面头部，不显示遮罩、不锁定滚动，内部复用 Drawer 的滚动区。
抽屉实例保留，由 `MkDrawer` 延迟渲染并在关闭动画结束后销毁内容，不再额外维护挂载状态或转发
`close` / `closed` 事件。页面在 `update:visible` 事件与头部返回方法中统一处理显隐，关闭时立即恢复草稿并清理预览；
恢复版本时先清空草稿快照再关闭，保留已恢复的版本。编辑弹窗的 `closeEdit()` 仅用于保存成功后关闭表单。

同目录 `EditPublishVersionDialog.vue` 只维护表单副本与校验。`mode` 默认为 `edit`，显示“编辑”，
通过 `open(version)` 回填；`mode="publish"` 显示“发布内容”，通过 `open()` 打开空白表单。通过
`submit(payload)` 提交、`close()` 关闭，外部传入 `saving`。标题必填且最多 64 字，更新说明最多
1000 字，标题拒绝纯空白；两种模式的提交按钮均显示“发布”。编辑请求由业务组件执行，
不创建新发布；提交期间使用表单内容 loading 遮罩，保留关闭保护，不设置表单 disabled。
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

`trigger/index.vue` 负责列表查询、当前页选择、单项启停/删除及批量操作，通过
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
`image/`、`tags/`；文档专属组件及 Action 随 `document/` 集中维护。其他页面继续放在
`knowledge-detail/` 下的 `recall-test/`、`question/`、`dictionary/`、`chat-user/`、`external-retrieval/`。
对话用户已实现按用户组查询及授权，接口与交互规则见“智能体与知识库对话用户”章节。
容器通过 `knowledge-detail/context.ts` 装配资源范围、知识库 ID、设置所需的完整业务 API 对象和返回列表路由，
并提供只读详情与替换能力。详情入口、setting 与 library 的 API 选择集中在该上下文。
Action、Drawer、Dialog 继续通过 props 接收完整 API。设置页复用已加载详情，保存成功后
更新容器数据，同步名称等展示。基本信息复用创建流程的 `KnowledgeBaseForm`，类型配置和校验留在
`setting/base/index.vue` 中，通用知识库标题为“设置”，其他类型为“基础设置”。
通用知识库只有单个设置菜单；Web 的设置分组包含基础设置、文档处理策略、定时同步，
飞书和工作流包含基础设置、定时同步。`setting/document-strategy/` 复用
`DocumentStrategyForm`，通过 `setStrategy()` 回填详情的 `doc_strategy` 为独立草稿，
通过 `validate()` 和 `getStrategy()` 校验并单独保存该字段。保存成功合并接口返回数据到详情上下文，
失败保留草稿，保存期间使用内容容器 loading 遮罩和按钮 loading，不禁用表单字段。
方法入口防止重复提交。标题栏通过 Teleport 展示下次同步生效说明，
保存不立即发起同步。智能分段回填时保留高级分段的编辑默认值，提交仍使用智能分段的固定策略。
`setting/scheduled-sync/` 维护“同步设置”和“同步日志”两个页签。进入页面和切换知识库时，
通过 `SyncApi.getKnowledgeSyncSetting` 回填独立草稿，后台默认值为关闭、每日 01:00、增量同步。
未读取成功前不允许保存默认草稿，重新进入页面可重试查询。
同步周期复用 `el-cascader` 和 `SCHEDULE_OPTION`，支持每日、每周、每月、间隔和 Cron。
周日期使用 1（周一）至 7（周日），同步间隔至少 5 分钟；前端校验周期，完整 Cron 校验由后台完成。
保存使用内容 loading 与按钮 loading，入口防止重复提交，不禁用各表单字段。
`putKnowledgeSyncSetting` 成功后，以后台返回值更新草稿和详情 `meta.sync_setting`；失败保留草稿。
同步方式复用 `constants/knowledge.ts` 的 `KNOWLEDGE_SYNC_OPTIONS`，按当前来源描述三种方式。
`components/SyncLogTable.vue` 在日志页签按需挂载，接收知识库 ID 和 `index.vue` 传入的完整同步 API 对象，
通过 `api.getKnowledgeSyncLogPage` 调用分页日志接口；接口仅返回定时任务触发的记录，手动同步不写入此日志。
日志表格沿用同步时间、同步内容、同步方式、同步状态、耗时五列，不新增操作入口。
同步内容按“共 N 个文档（已同步、跳过、删除、失败）”展示，仅附加非零的跳过、删除和失败计数；
跳过执行时直接展示原因，后台结果信息通过同步内容的悬停提示查看。
状态复用 `MkStatusLabel`，同步中使用 `loading`，成功和失败分别使用 `success`、`failure`，
不配置跳过状态；完整同步使用“完整同步”标签。
进入日志页签、切换知识库和分页时查询，不做定时刷新。
设置菜单的类型筛选由路由维护；基础设置和文档策略通过上下文接入 Workspace 与 System 管理接口，
定时同步通过同步上下文接入四个资源范围的查询接口，Workspace 共享资源保持只读，不新增前端权限判断。
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
无排序入口。非共享文档显示选择列，只支持当前页选择，翻页、切换每页条数、搜索或筛选变化时清空；
选中后通过 `footer-batch-actions` 展示批量操作。右侧固定操作列提供启停、向量化、分词索引和更多菜单，
运行或排队中的任务切换为取消入口。Web、飞书提供同步；工作流知识库仅为 `meta.source_type=web`
的文档提供单项同步，沿原 Web 数据源分支执行提取、分段并只合并所选文档，不抓取链接或清理其他来源。
手动同步通过工作流执行记录跟踪任务与合并结果，不写入定时同步日志。
本地上传的工作流文档不提供同步入口。普通与工作流文档提供原文下载和替换。
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
`MigrateDocumentAction` 选择目标知识库；`setting-tags/DocumentTagsAction.vue` 内部管理标签设置抽屉的挂载、打开和关闭。
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
公共弹窗按需挂载、关闭后卸载，不负责选择提交接口。段落页复用公共弹窗时关闭
`showParagraphScope`，由段落按钮提交段落接口，不扩展公共弹窗的接口分支。
设置操作集中在 `document/action-dropdown/setting/`，通过上层 `index.ts` 导出两个入口。
`SettingDocumentAction` 接收单个 `document`，展示菜单项；`BatchSettingDocumentAction` 接收
`documentIds`，展示批量设置按钮。入口文案由 `label` 传入，单项图标由可选 `icon` 传入。
两个入口通过 `v-model:loading` 共用页面操作状态，打开时固定操作目标，分别调用单项和批量设置接口。
共用的 `DocumentSettingDialog.vue` 负责表单回填、校验和提交数据，按需挂载、关闭动画结束后卸载；
弹窗通过 `batch` 参数区分批量模式，批量入口显式传入；文档地址和选择器仅在 `!batch` 且为 Web 知识库时显示。
单项保留文档原有 `meta`，批量使用默认配置并将 `allow_download`
放在顶层。请求与成功关闭由 Action 负责，成功通知页面刷新，失败保留表单。
标签操作集中在 `document/action-dropdown/setting-tags/`。`DocumentTagsDrawer.vue` 管理单篇文档的标签关联，
由 `DocumentTagsAction` 按需挂载、关闭后卸载；仅提供添加、搜索、单值删除及批量删除，不提供编辑和分页。
抽屉每次打开都查询最新关联；增删后立即刷新自身列表，Action 记录成功变更，关闭后再通过 `refresh` 通知文档页刷新。
查询使用 `DocumentApi.getDocumentTags`，搜索使用单一 `MkSearchInput`，通过 `change` 将关键词作为 `name` 请求接口，清空时省略该参数；
查询前清除勾选，直接展示接口返回的分组，不再本地过滤。选择列和标签名单元格合并；
通过 `MkTable selection-group-key="key"` 联动组内标签值，已选数量按标签值行数统计；标签值列复用 `border-l!` 展示与合并标签列之间的分隔线。
单项及批量删除均直接调用 `putDeleteDocumentTags`，不弹二次确认；仅移除当前文档关联，不调用知识库标签删除接口。
`AddTagDialog.vue` 为标签列、抽屉与批量操作栏共用的下拉式添加弹窗，接收完整 Document API 和知识库 ID。
三个入口分别由 `DocumentTags`、`DocumentTagsDrawer`、`BatchDocumentTagsAction` 管理弹窗实例，不通过页面 Ref 打开。
候选项使用 `tagsApi.getKnowledgeTags`，按返回顺序截取前 100 个标签组，然后由 `el-select filterable` 本地搜索；
右侧显示所选组的全部标签值，切换标签名清空本行标签值，不增加远程搜索或自动扩展候选范围。
单篇与批量均允许选择已关联标签值和重复选择，不为禁选查询文档已有标签，也不区分 `batch` 模式。
表单复用 `MkFormList`，至少一行，字段只做必填校验；提交前检查标签值归属，失效时用 `MsgError` 提示“请重新选择标签值”并保留选择。
通过 `postAddDocumentTags` 提交所选 ID，由后台去重并追加关联。
下拉 footer 复用模型选择器的创建入口，直接打开输入式 `tags/components/CreateTagDialog.vue`；
标签名入口调用 `open()`；标签值下拉始终可展开，未选标签时点击“创建标签值”也调用 `open()` 创建标签，
已选标签时调用 `open(key)` 新增标签值，不合并两类弹窗的模式。
弹窗每次打开都查询候选；内部创建成功后重载前 100 组候选，保留当前选择，不自动选中新数据。
候选查询的 `queryLoading` 仅用于两个 `el-select` 的加载状态及下拉内创建入口禁用；表单遮罩、提交与取消只使用提交 `loading`。
`BatchDocumentTagsAction.vue` 使用普通按钮外放在底部批量操作栏，内部按需挂载 `AddTagDialog`，打开时固定知识库和文档 ID，
即使只勾选一篇，也按批量添加处理。添加成功后关闭并立即通知刷新；取消关闭时只通知卸载，不刷新。
三个外层标签入口只通过 `refresh` 通知页面刷新，沿用文档列表原有轮询，不为标签浮层单独暂停。
页面不持有标签浮层 Ref 或控制其挂载。标签维护入口通过上下文的完整写接口控制，
目前仅 Workspace 普通资源提供维护 API；Workspace 共享只读，System library 的文档与标签 API 尚未提供，
不显示维护入口，也不回退 Workspace 请求。
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
分别调用 Web 或飞书的单项、批量同步接口；工作流 Web 文档复用单项接口，由后台启动工作流，
确认内容说明沿原提取、分段配置同步，提交成功提示“同步任务发送成功”。共用页面 loading，成功后通知页面刷新。
直接请求的 Action 通过 `v-model:loading` 共用页面操作状态，各 Action 自行管理请求、
防重复提交、成功提示与失败处理，不额外抽取统一请求封装；需要刷新时发出 `refresh`，导出与下载不发出。
`DeleteDocumentAction` 单个删除传 `document`，确认框展示文档名称并调用单个删除接口；
批量删除传 `batch` 和 `document-ids`，确认框展示数量并调用批量删除接口。
删除后分页总数和页码回退由页面重新查询服务端处理，不在 Action 中维护分页数据。
启停开关直接使用页面内的 `el-switch`，由页面 `handleChangeActive` 管理请求，
接口成功后刷新列表回显，不在请求前切换状态，不单独封装 Action。
页面保留列表、多选、任务状态展示判断与刷新方法，不维护各 Action 的请求流程。
`DocumentStatus` 和标签列组件 `DocumentTags` 继续留在 `document/components/`，后者同时管理本入口的添加弹窗。
弹窗 Ref 和打开方法由对应 Action 或标签列入口组件维护，页面只传参、处理刷新。行内更多菜单使用 `MkTableMoreDropdown`；批量操作栏使用
`MkDropdown` 搭配非 text 的 More 图标按钮和 `MkDropdownMenu`，点击展开。
批量 More 开启 `hide-when-empty`，按标准菜单插槽判断空内容，不强制开启 `persistent`；不检查业务 Action 内部的条件渲染。
不新增前端权限判断；Workspace 共享文档不展示选择列、操作列及批量操作，标签列保留禁用的添加按钮。
文档分页接口维护在 `workspace/knowledge/document.ts`，页面管理 loading。文件状态表头使用
`MkDropdown` 单选筛选全部、成功、失败、索引中、分词索引中、排队中和生成中；查询组合
`status` 与可选的 `task_type`，切换选项清除旧任务类型并回到第一页，保留名称和创建者条件。

文档详情页面及其专属组件统一放在 `views/document-detail/`，与 `knowledge/`、`knowledge-detail/` 平级。
普通 Workspace 文档行点击进入 `document-detail/index.vue`，选择列、名称编辑及行操作
保留自身交互。分段页与知识库详情容器路由同级，复用 `MkViewLayout` 的顶部栏、侧栏和主区滚动；
顶部展示接口查询的文档名称、标题／内容搜索、批量选择和添加分段，主区使用 `MkInfiniteScroll`
按组件配置的每页数量加载分段，显示接口返回的筛选结果总数。侧栏按服务端位置排列已加载分段，
点击定位正文，滚动同步高亮；批量全选仅覆盖已加载分段，追加加载不清空已有勾选。
搜索、新增后通过 `refreshParagraphs()` 重置到第一页，显示首次加载状态并回到顶部；
编辑、启停局部替换卡片，删除、迁移局部移除，保留其他已加载数据和滚动位置。
局部移除后，下一次滚动请求按剩余列表长度定位服务端分页，必要时拼接相邻两页，避免漏载。
正文使用 `MdPreview`；第一页加载完成且无分段时展示空态。
左侧目录和右侧卡片分别通过 `useSortable` 绑定同一份分段数组，拖拽图标使用与 `MkFormList`
一致的 link 按钮、`text-N600` 和 `h-8!`。左右图标均仅在悬浮所属目录项／卡片或获得焦点时显示，
绝对定位在所属目录项／卡片右侧并向外露出 8px，不占据布局空间；目录图标垂直居中。
左右均可按住整条目录项／整张卡片或拖拽图标排序，只允许在已加载分段中排序。
右侧整体过滤悬浮操作区，并过滤正文链接及拖拽图标以外的按钮，保留原有点击行为；
普通点击卡片仍打开详情，位置保存期间不打开详情；左侧点击手柄不触发目录定位。
左侧使用普通 `div.paragraph-directory-row` 作为排序行，手柄与 `ElAnchorLink` 并列。
页面局部 `v-disable-link-drag` 指令将 `ElAnchorLink` 内部的 a 设为 `draggable=false`，
不使用 `dragstart.prevent`，避免原生链接拖出浏览器，并让整条目录项正常参与 Sortable 排序。
拖拽后两侧同步重排，通过目标分段原有的真实 `position` 提交位置接口，搜索不改变位置语义。
成功后同步移动区间内已加载分段的 `position`，失败恢复原顺序；不重新查询或重置列表。
批量模式、分段加载、删除确认或提交、弹窗打开、位置保存以及不足两条时禁用拖拽。
拖拽和保存期间暂停滚动补页，保存时仅在标题栏显示状态，不使用整页 loading 遮挡落位动画；
保存锁继续禁止再次拖拽和修改操作。与 `MkFormList` 一致，两侧使用普通 DOM 容器，
右侧以普通 `div.paragraph-sort-row` 承载卡片，由 `useSortable` 统一提供 150ms 位移动画；
不在可排序元素上叠加 `TransitionGroup`，也不直接对带默认过渡样式的 `ElCard` 做位移动画。
批量选择支持点击整张卡片或复选框切换勾选、全选、取消、“迁移至”、“生成问题”和“删除”；
复选框阻止点击冒泡，避免重复切换。`document-detail/action-dropdown/migrate/` 集中维护
批量按钮 `BatchMigrateParagraphAction`、单项菜单 `MigrateParagraphAction` 和 `ParagraphMigrateDialog`，沿用 chat-log 添加知识库的知识库／文档
选择样式，保留知识库和文档图标；迁移 API 由分段页传入完整 Paragraph API 对象。
打开时固定所选分段 ID，选择知识库后查询全部文档并排除当前文档，允许迁移至同知识库其他文档。
知识库和文档必选，成功关闭动画结束后通过 `success(paragraphIds)` 返回本次迁移的固定 ID，
页面局部移除对应分段、扣减总数并移除对应勾选，不重载列表；失败保留表单。
`document-detail/action-dropdown/generate-questions/` 维护批量按钮 `BatchGenerateQuestionsAction`
和单项菜单 `GenerateQuestionsAction`，
接收页面传入的完整 Paragraph API，打开时固定知识库、文档和勾选分段。复用公共
`GenerateQuestionsDialog` 并传入 `showParagraphScope=false`，仅提交生成配置和所选分段 ID，
不传 `state_list`；生成问题属于异步任务，提交成功关闭后仅清空选择，不重载列表；失败保留配置。
批量删除按钮和请求逻辑直接维护在 `document-detail/index.vue`，不单独拆分组件。
确认前固定所选分段与所属文档，确认后提交批量删除接口；成功从本地列表移除本次删除的分段、
扣减总数并移除对应勾选，保留其他卡片与滚动位置。
取消或失败保留选择，确认及请求期间阻止重复操作。
`document-detail/paragraph-dialog/` 维护两个独立弹窗，以本地组件组合左右布局：

- `CreateParagraphDialog.vue` 组合 `components/ParagraphForm.vue` 与 `components/ParagraphQuestions.vue`，
  管理添加请求，底部提供取消和添加；`open(position?)` 可指定插入位置，默认添加到文档首位。
- `EditParagraphDialog.vue` 组合 `ParagraphForm`、`ParagraphPreview` 与 `ParagraphQuestions`，
  支持 `open(paragraph, initialMode?)`，初始模式默认为 `detail`，也可传入 `edit`。
  详情点击编辑进入表单；取消编辑回到原详情，保存成功回到更新后的详情。
- `ParagraphForm` 使用 `v-model` 接收标题和正文，通过 `validate()` 暴露校验；标题最多 256 字符，
  内容必填且最多 100000 字符。正文使用 `MdEditor`，默认关闭预览，提供 Markdown 工具栏及字数统计；
  通过必填的 `knowledgeId` 将图片上传到当前知识库，复用 `FileApi` 和 `FILE_SOURCE_TYPE.KNOWLEDGE`。
  提交由 Dialog 编排。
- `ParagraphPreview` 只展示标题、Markdown 正文、召回次数和最近召回时间；Dialog 管理使用 `mk-paragraph-card` 样式的详情卡片容器及绝对定位的编辑按钮。
- `ParagraphQuestions` 沿用 v2 的添加及移除流程：点击加号显示 `el-select`，使用远程搜索、
  `allow-create` 和首项默认选择，选择已有问题或输入新问题后立即添加；失焦取消输入。
  问题去除首尾空格、非空、最多 256 字符且不重复，已关联候选不可重复选择。
  候选通过 `ProblemApi.getProblemsPage` 查询第一页 100 条；已有分段分别调用创建或关联接口，
  添加或解除关联成功后重新查询当前分段问题。列表使用卡片，左侧显示问题文字，右侧提供移除按钮；移除只解除关联，
  不删除问题本身。无 `paragraphId` 时维护 `{ content }` 本地草稿并随新增分段提交。
  问题输入状态和请求 loading 均在组件内部维护，不向 Dialog 传递 `adding` 或 `loading`，
  不阻止分段创建、正文保存、取消或关闭。新增分段只提交已加入列表的问题草稿；
  问题请求失败保留输入与现有问题。

两个 Dialog、`ParagraphForm` 和 `ParagraphQuestions` 均不提供或传递 `disabled` Prop；
详情模式通过悬浮编辑入口进入表单，问题区始终提供添加与移除入口。
每个 Dialog 统一使用一个 `loading` 管理自身加载和提交、内容遮罩、按钮状态及重复操作保护；
问题请求使用子组件内部独立的 `loading`，只覆盖右侧问题区。提交状态不作为表单 `disabled`。
两个 Dialog 均接收完整 Paragraph API 和知识库／文档 ID，打开时固定目标，点击时挂载、关闭动画结束后卸载。
详情加载失败提供重试；请求失败保留草稿。正文保存不提交 `problem_list`，也不使用保存响应回填问题列表，
避免覆盖并行的问题操作；取消编辑不撤销即时保存的问题关联。
新增成功关闭弹窗并通知页面清空搜索、从第一页重新加载；编辑成功通过 `success(paragraph)`
返回保存响应，页面通过 `handleReplaceParagraph()` 按 ID 局部替换，标题和内容不再匹配当前搜索时局部移除。
分段卡片在非批量模式点击打开详情弹窗，批量模式点击切换勾选；批量生成问题使用 `action-dropdown` 导出的 `BatchGenerateQuestionsAction`。
非批量卡片右上角使用与文档导入预览相同的 sticky 悬浮操作区和白色阴影 Card，
提供启停、直接编辑及上方插入；更多菜单提供单段生成问题、迁移、移动位置与删除。
更多菜单及移动位置子菜单通过 `visible-change` 维护各自展开状态，展开期间对应操作 Card
保持显示；关闭后恢复悬浮或焦点显隐，刷新、切换批量模式及移除对应分段时清理状态。
该状态只控制操作区显隐，菜单与业务弹窗的挂载仍由 `MkDropdown` 的 `persistent` 管理。
`BatchGenerateQuestionsAction` 和 `BatchMigrateParagraphAction` 直接渲染批量按钮；
`GenerateQuestionsAction` 和 `MigrateParagraphAction` 直接渲染单项 `MkDropdownItem`；
`GenerateQuestionsAction` 的入口文案由页面通过必填 `label` 传入。
四个 Action 各自管理目标快照、入口和弹窗，不提供触发插槽，也不通过批量 Action 包装单项操作；
单项与批量迁移复用 `ParagraphMigrateDialog`，生成问题复用公共 `GenerateQuestionsDialog`。
页面通过 `action-dropdown/index.ts` 导入并组合，弹窗均点击后挂载、关闭动画结束后卸载；
更多菜单使用 `persistent` 保留 Action 实例，迁移弹窗关闭后由重新挂载初始化状态。
启停仅提交 `is_active`，成功后复用局部替换方法；单段删除确认后调用独立 DELETE 接口并局部移除。
`action-dropdown/MoveParagraphAction.vue` 封装位置菜单及四个方向选项，接收 `label` 和 `disabled`，
通过 `move(direction)` 通知页面执行移动，通过 `visible-change` 通知页面维护操作 Card 显隐；
方向类型 `ParagraphMoveDirection` 放在同目录 `types.ts`，由 `index.ts` 类型导出。
位置菜单包含置于顶部、上移、下移、置于底部，页面先查询完整文档分段顺序再调整位置，
不按搜索结果计算相邻位置；调整成功后仅查询并替换当前已加载范围，保留分页与滚动位置。
Workspace 共享及 System 分段路由已注册并保持来源导航；各范围分段 API 接入暂缓。

System 资源管理与共享资源已注册共用知识库详情路由，
列表导航已接入。System 详情路由在 System 根路由的 children 汇总，通过详情父路由的 `hideSidebar: true` 隐藏系统管理 Sidebar，保留系统 Header 和知识库详情目录；
容器使用上下文选定的详情 API，并返回各自 System 列表。System 基础设置、策略保存使用对应 Knowledge API，
基础表单 `KnowledgeBaseForm` 内部根据资源范围选择完整模型 API，不接收外部 `modelApi`；
Workspace 普通与共享资源均使用 Workspace 模型选项接口，System 资源管理使用 System 模型接口，
System 共享使用系统共享模型接口。
四种范围的定时同步查询和日志均使用各自现有 Sync API；Workspace 普通和 System 两种范围支持保存，
Workspace 共享只读，不发送保存请求，不回退 Workspace 接口。
library 通过 `useKnowledgeLibraryContext` 装配现有文档、标签 API；System 两种范围未提供对应模块，
保持未接入状态，不回退 Workspace。Workspace 共享仅查询，普通 Workspace 提供已有维护接口。
路由结构及来源配置见 `src/router/ROUTE_README.md`。

### 资料库标签管理

`knowledge-detail/library/tags/index.vue` 复用详情布局的 `customHeader` 与 Teleport，
维护搜索、导入入口、创建入口和标签表格，不嵌套页面布局或修改路由。
通过 `workspace/knowledge/knowledge.ts` 查询分组，使用单一 `MkSearchInput`，通过 `change` 将关键词作为 `name` 请求接口；
清空时省略该参数，搜索后回到第一页并清除勾选，不在前端过滤匹配结果。
对接口返回结果先按标签组分页，再展开各组标签值，分页总数为返回的标签组数。
`MkTable` 合并选择列和标签名，通过 `selection-group-key="key"` 联动当前页同组标签值；
批量底栏按实际选中标签值行数／当前页标签值总行数统计，不按标签组计数。
删除提交全部选中标签值 ID，批量确认数量与底栏已选行数一致；标签、标签值及批量删除统一提示关联资源上的标签也会删除。
标签名旁提供新增值、编辑标签、删除标签；行末提供编辑值和删除值，
数量链接打开同目录 `TagDocumentDrawer.vue`。

`library/tags/components/CreateTagDialog.vue` 为顶部创建和标签旁新增值共用的创建弹窗，
接收知识库 ID 与完整 Tags API，参考添加成员流程复用 `MkDialog`、`el-form` 和 `MkFormList`。
创建允许多行标签名与值；新增值通过 `open(key)` 回填并锁定标签名，新增行沿用该名称。
顶部创建标题为“创建标签”，传入标签名时标题为“添加标签值”。
两个入口统一通过 `postKnowledgeTags` 提交标签数组，提交前检查表单内重复组合，沿用模型参数的 `MsgError` 消息提示并保留输入；
与知识库已有标签重复的组合由后端跳过，接口错误由请求层统一提示。
同目录 `EditTagDialog.vue` 共用标签重命名和单值编辑，通过 `open(tag, field)` 回填独立草稿。
重命名只显示标签名；编辑值只显示一行并锁定标签名。两个入口均提交完整 `id`、`key`、`value`，
请求路径 ID 与载荷 ID 一致，仅修改当前编辑字段，未编辑字段原样保留。
两种编辑均使用 `putKnowledgeTag`，不提供增删行或多行编辑，不组合多个请求模拟保存。
两个弹窗均保留 `MkDialog` 默认 600px 宽度，标签名最多 64 字、标签值最多 128 字，
校验必填与纯空白，提交时清理可编辑字段首尾空格。各自维护 loading、防重复提交与关闭保护；
成功后提示、关闭并发出 `refresh`，失败保留草稿；常驻实例在 `closed` 清理草稿和校验。
后续文档入口直接复用上述弹窗，不复制创建和编辑逻辑。

`library/tags/components/ButtonImportTags.vue` 在同一组件内维护导入按钮与弹窗，
复用 `MkDialog`、`el-form` 和 `MkDragUpload`，不再单独拆分导入 Dialog。
支持单个 XLS、XLSX 文件的选择、拖拽、更换、删除及必填校验，关闭后清理文件和校验状态。
接收知识库 ID 与完整 Tags API，页面监听 `refresh` 重新查询标签列表；已预接提交 loading、重复提交保护、
成功提示和关闭弹窗，失败保留文件。模板下载有独立 loading 和重复点击保护，下载期间禁止提交与关闭，
结束后恢复状态，不关闭弹窗或刷新列表。导入调用 Tags API 的 `postImportKnowledgeTags`，
通过单个 `file` 字段提交原始文件；模板下载调用 `exportKnowledgeTagTemplate`，复用请求层文件下载。
模板第一行为“标签、标签值”，每行填写一个组合；后端校验整份文件并跳过重复组合，错误包含工作表及行号。

`TagDocumentDrawer.vue` 接收知识库 ID 与完整 Document API，通过 `open(tag)` 固定当前标签，
以“已关联文档／未关联文档”两页签共用表格，提供搜索、启用状态筛选、分页、单个与批量关联／取消关联；创建时间仅展示，不提供排序入口。
启用状态复用 `MkTableFilter mode="single"`，支持全部、已启用、已禁用；查询传布尔 `is_active`，全部时省略。
名称或状态筛选后回到第一页并清空选择，切换页签时重置筛选条件。
文档图标和时间格式沿用文档列表，状态使用 `MkStatusLabel`；批量操作放在顶部，不再显示页面批量底栏。
搜索、分页和页签切换清空选择，关联变更后重新查询并通知标签页刷新数量，末页为空时回退。
抽屉在 `closed` 重置标签、筛选、分页和选择，不新增权限判断或共享范围接口。
文档页标签候选查询通过资料库上下文选择当前范围 Tags API，共享标签查询保持原接口；普通文档标签入口使用上述独立添加弹窗与抽屉。

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

### 知识库工作流导航与导入导出

`workflow/knowledge/navigation.ts` 统一返回入口：Workspace 将详情中的 `type` 通过 `KNOWLEDGE_TYPE_MAP` 转为字符串后返回当前知识库详情，详情尚未加载时使用 `WORKFLOW`；System 资源管理和共享资源返回各自知识库详情；Workspace 共享也返回共享详情。
历史模式下返回只退出预览；普通编辑态返回保留未保存确认。更多菜单的导出工作流先保存未提交改动，
再调用专用 `.kbwf` 导出接口；保存失败不导出。知识库原有文件上传、数据源表单与任务轮询调试流程保持独立。
更多菜单在“导出工作流”上方依次提供“导入文档”和“导入工作流”。导入文档要求工作流已发布，
复用文档页的 `WorkflowImportDocumentDrawer`，按需挂载并在关闭动画结束后卸载；发布成功即时更新
本页发布状态。导入工作流选择单个 `.kbwf` 文件，确认覆盖后上传，不先保存旧草稿；确认及请求期间
暂停自动保存，成功重新加载图、默认模型设置、保存时间与保存基准。取消或请求失败保留当前画布，
文件选择使用 `el-upload`，关闭自动上传与文件列表展示；选择后调用 `clearFiles()`，
允许再次选择同一个文件。不增加权限判断。

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

## 知识库工作流转换与执行记录

### 知识库工作流转换

`knowledge-detail/workflow-transform/index.vue` 承接 Workspace 非工作流知识库的“工作流”入口，
路由统一使用 `workflow-entry`（`workspace-knowledge-workflow`），不另设转换路由。
复用详情布局并隐藏标题栏，展示 v2 转换说明与工作流示例图。知识库详情从已有上下文读取，
路由 `beforeEnter` 将工作流类型直接重定向至全屏画布，页面不监听类型跳转。
转换需确认不可回退，页面管理 loading 与重复提交保护，
通过 `useKnowledgeSettingContext()` 的 `resourceApi.knowledge.postTransformWorkflow` 提交
深拷贝后的 `knowledge/template.ts` 默认模板，按上下文选择 Workspace、System 资源管理或
System 共享管理 Knowledge API；成功后进入画布，失败保留转换页。
四种范围的路由与画布跳转已配置；API 保留原实现，Workspace 共享和 System 工作流接口接入暂缓。

### 执行记录

`workflow/knowledge/ButtonExecutionRecord.vue` 封装更多菜单入口、抽屉挂载与打开逻辑，接收
`knowledgeId`，菜单属性（如 `divided`）透传到 `MkDropdownItem`，内部提供知识库 Workflow API。
`workflow/knowledge/execution-record/` 维护记录列表和详情抽屉，由该按钮组件打开；
工作流文档页在“导入文档”左侧使用 `knowledge-detail/library/document/components/ButtonExecutionRecord.vue`
封装“执行记录”按钮与同一个记录抽屉，页面传入当前知识库 ID 与完整知识库 Workflow API，
按钮组件维护抽屉挂载状态和打开逻辑。两个入口均在点击时挂载抽屉，
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
文档页将标题、搜索与上传入口放入标题栏，表格在正文中独立显示 loading。

通用知识库的非共享文档页在标题栏使用 `document/upload-document/ButtonUploadDocument.vue`，
提供文本文件、表格和 QA 问答对菜单。页面通过 `api` 传入完整 Document API，由按钮转交抽屉，
模板下载、文本解析和文档导入均调用传入的 API。点击后按需挂载 `UploadDocumentDrawer.vue`，
使用全屏底部抽屉，关闭动画结束后卸载。文件支持多选、拖拽和文件夹选择，最多 50 个文件，
同时遵循知识库的文件数量、单文件大小限制；文件卡片支持下载和删除。
上传区复用公共 `MkDragUpload` 的多文件模式；多文件组件负责文件夹选择、上传汇总及两列卡片。
抽屉通过 `provide('upload')` 提供 Admin `FileApi.postUploadFile`，使用 `TEMPORARY_120_MINUTE`
上传临时文件，由多文件组件维护实际传输进度、重试及取消；页面通过公开的 `uploadingCount`
阻止上传中进入下一步或导入，没有成功文件时提示，上传结束后仅处理 `success` 文件。
页面通过 `accept`、`limit`、`sizeLimit` 提供校验规则，由多文件组件校验格式、大小、空文件和重复选择；
大小超限保留不可重试的失败卡片，网络失败可重试。移除成功文件时，多文件组件直接
调用 `FileApi.deleteFile(file_id)` 删除服务端临时文件；上传中文件由组件取消请求。
具体上传接口与导入请求仍由本页负责。
文本分段解析接口仍提交原始文件。表格和 QA 导入从成功文件的 `file_id` 获取上传结果，
提交 `{ file_id_list }` 到对应的 `table_by_file_ids` / `qa_by_file_ids` 接口，不重复上传文件；
缺少文件 ID 时提示重新上传，不回退到再次上传原始文件。
文本上传分为文件选择和文档处理策略两步，复用 `DocumentStrategyForm`，首次进入第二步才挂载，
开启视觉增强后按当前策略加载选项，返回上一步保留策略及已加载选项；
策略页的“生成预览”按当前策略解析文件，进入 `upload-document/DocumentImportPreview.vue`，
使用 `MkViewLayout` 的侧栏切换文档、正文展示分段，复用其主区滚动和固定标题；
支持本地编辑和删除，编辑须保存或取消后再导入。
分段编辑使用同目录的 `EditParagraphDialog.vue`，复用添加分段的 `ParagraphForm` 与
`ParagraphQuestions`，提供 Markdown 编辑、知识库图片上传和关联问题草稿；不传入已有分段 ID，
保存仅更新当前导入草稿，不创建分段或立即写入问题关联，取消不修改预览。
编辑弹窗按需挂载，关闭动画结束后卸载；关联问题随最终导入的 `problem_list` 提交。
预览仍属于第二步，返回策略页保留设置，重新生成时以新的解析结果替换预览。
预览导入直接批量创建编辑后的分段，保留来源文件及处理策略，不再次解析。
策略页“开始导入”将已上传的 `file_id_list` 与当前 `doc_strategy` 一次提交到 `document/import`，
由服务端读取已有文件直接解析并入库，不再次上传文件；缺少文件 ID 时提示重新上传。
不调用预览接口或在前端传递分段结果；解析和入库在同一事务内完成，空分段结果提示失败。
表格、QA 直接调用各自导入接口，支持下载 Excel、CSV 模板。
选择文件阶段显示实际上传状态，导入成功后关闭、清空搜索和表格筛选，并回到第一页重新加载；
失败保留文件与策略。
不新增权限判断或修改共享文档的查询边界。

Web、飞书和工作流知识库的非共享文档页在标题栏组合
`document/import-document/ButtonImportDocument.vue`，页面传入已有路由变量 `knowledgeId`、
`knowledgeType`（`KNOWLEDGE_TYPE_KEY` 标识），从详情上下文读取飞书 `folderToken` 和工作流图 `workflow`；
不传完整 `knowledge`，不重复查询知识库。
入口按类型挂载独立的 `WebImportDocumentDrawer.vue`、`LarkImportDocumentDrawer.vue`、
`WorkflowImportDocumentDrawer.vue`，关闭动画结束后卸载。
Web 和飞书使用全屏底部 Drawer，分别通过地址表单和飞书 `MkTable` 懒加载目录表格进入文档处理策略；
策略复用 `DocumentStrategyForm`，使用组件默认策略，不回显知识库策略，上一步保留草稿。
Web 抽屉只接收完整 Document API 与知识库 ID，地址和选择器初始为空；
飞书抽屉额外接收文件夹 Token，工作流抽屉只通过 Prop 接收知识库 ID，图数据在打开时通过
`open(workflow)` 传入并保存在抽屉本地；所有导入组件均不接收 `KnowledgeDetail`。
Web 地址按行去空白、去重并校验 HTTP/HTTPS；空选择器提交 `body`。
飞书按 `meta.folder_token` 查询目录并读取全部分页，已导入文档勾选且不可重复导入；
表格使用原生 `type="selection"` 选择列和名称列，表头全选覆盖当前已加载节点；
初始化仅加载根目录，文件夹默认收起，展开与收起由 Table 维护。
不重复保存表格选择状态，在下一步通过 `getSelectionRows()` 获取待导入文档。
文件夹持续保留懒加载标记，由 Table 维护层级和缩进，避免与普通树数据混用导致层级丢失。
原生选择维护已加载节点的父子联动与半选，勾选文件夹不请求子目录，只有展开时加载。
展开已选文件夹时新加载的节点继承勾选，加载期间禁止进入下一步。
正式导入沿用 v2，仅过滤已导入项，保留所选文件夹的名称、Token 和类型，不在前端递归展开文件夹。
两者提交成功关闭并刷新列表，失败保留输入、选择和策略。
工作流导入 Drawer 与 DebugDrawer 使用相同的三步 Action，直接引用
`views/workflow/knowledge/debug/action/` 的 DataSource、KnowledgeBase 和 Result，
有知识库用户输入字段时显示第二步；通过正式 `/upload_document` 接口执行已发布工作流。
上传提供临时文件、进度及取消能力，上传中阻止切换或提交，失败文件不提交；
`file_id` 与上传成功状态校验仅用于本地文件数据源；飞书等工具数据源的 `file_list`
保留远程文件或文件夹选择值，由后端工具负责下载，不要求本地上传 ID。
继续导入重建 Action 并清空载荷，提交及完成后通知列表刷新。不新增权限判断。
飞书扩展接口沿用 v2；当前仓库缺少 v3 飞书后端，新增的每文件 `doc_strategy` 字段需扩展端联调确认。

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
表头标签筛选每次展开时按普通／共享范围重新查询知识库标签，不因已有选项而跳过请求；
普通布尔请求锁防止重复请求，失败释放后下次打开可重试。
标签级联沿用 MkTableFilter 默认的父子独立选择和隐藏复选框外观；组件内部保留原始勾选，
对外将父组转换为叶子值并去重。页面直接将回写的叶子标签 ID 数组用于查询，
“无标签”使用 `NO_TAG`；页面不维护父组展开或去重逻辑。
任一筛选确认或重置后回到第一页查询，保留其他筛选和名称／创建者搜索条件。
标签列使用页面专属 `components/DocumentTags.vue`，接收 `document`、知识库 ID 和完整 Document API，展示标签数量，
悬浮时显示标签名与值，长文本省略并保留 title。数量优先读取 `tag_count`，缺省时使用标签数组长度，
添加按钮始终显示，通过 `disabled` 接收页面的 Workspace 共享只读状态，通过 `v-model:loading` 共用操作状态，不隐藏加号和“标签”文案；已有标签的悬浮查看不受影响。
添加按钮阻止点击冒泡，组件内部按需挂载并打开 `AddTagDialog`；打开方法同时检查只读、操作中和重复打开状态。
添加成功关闭弹窗后通过 `refresh` 通知页面刷新文档列表与数量；不新增权限判断。

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
两者复用 `knowledge-detail/index.vue` 和文档页；详情容器通过上下文选择对应详情 API，
文档页与标签页通过 `useKnowledgeLibraryContext` 选择普通或共享的现有完整 API 对象。
共享详情已补齐与其他三种范围一致的菜单，设置与工作流接口接入暂缓。
容器监听工作空间、知识库和资源范围变化重新加载；共享详情返回列表携带 `folderId: 'shared'`，
普通详情继续恢复所属文件夹。文档创建者选项在共享范围使用 System `CommonApi`，普通范围使用
Workspace `CommonApi`；范围变化同时清空搜索控件、筛选、创建者选项与分页。

## 知识库外部检索服务

`knowledge-detail/external-retrieval/index.vue` 由四个资源范围共用，复用详情布局的自定义标题栏，
当前仅直接调用普通 `workspace/knowledge/external-retrieval.ts`，不新增 context 配置。
通过 `isWorkspaceResource()` 限定请求范围；其他三个范围显示待接入提示、禁用开关，不回退普通 Workspace。
普通 Workspace 提供身份认证及服务启停开关；查询与提交共用内容 loading，
开关仅在保存成功后按完整响应回显，每次只提交变化字段，失败保留原状态。
API 地址、调用示例及 MCP 配置只读；后两个展示区参考工具 MCP 详情，使用文本域和悬浮复制按钮。
地址与调用示例均来自接口；调用示例直接绑定 `api_example` 字符串，不在前端拼接或执行检索；MCP 配置直接格式化接口结果。
四套 API 文件及联调 TODO 保留，均使用真实请求封装，不返回占位 null；其他范围的页面接入待后续处理。
查询失败不回填配置，不允许在未知配置上保存；页面不伪造配置或保存成功。

## 智能体与知识库对话用户

`application-detail/chat-user/index.vue` 与 `knowledge-detail/chat-user/index.vue` 分别维护智能体、知识库的用户组和用户授权，
使用对应路由 ID 及 `RESOURCE_TYPE.APPLICATION / KNOWLEDGE`；授权类型必须大写，与后台授权记录及对话端查询一致。
两页通过 `hideHeader: true` 隐藏详情标题栏，使用普通 Flex 双栏容器，不嵌套 `MkViewLayout`。
外层 `ResourceDetailLayout` 统一管理整体滚动；侧栏复用 `w-sidebar-expanded`、`MkSearchList` 的搜索、选中和空态。
“按用户组”列表通过插槽展示名称及自动授权状态；接口尚未返回组已授权人数，手动授权组显示“已授权 —”，不以当前页勾选数代替。
右侧第一行展示组名和用户查询总数；下方工具栏左侧为默认按姓名查询的 `MkComplexSearch` 及自动授权开关，右侧为保存。
顶部 `MkComplexSearch` 按姓名、用户名排列；用户来源只在表头使用 `MkTableFilter mode="single"` 筛选，向接口传 `source`。
用户名、姓名搜索与表头来源可组合查询，清空一处条件不影响另一处，不额外重置搜索组件。
筛选变更回到第一页，选择“全部”移除来源条件。保留 `MkTable` 分页及高度约束。

两页当前仅直接调用普通 `workspace/chat-user.ts`，分别传自己的资源类型和路由 ID，不配置到详情 context。
页面不判断资源范围，也不显示范围待接入提示；当前请求均使用 Workspace API，其他入口的 API 切换尚未接入。
其他范围的 API 文件及联调 TODO 保留，页面接入待后续处理。
当前不接入 `perm`。授权勾选只维护当前页，保存只提交当前页用户；翻页、筛选或切换组时重新读取服务端状态。
无修改、无用户或自动授权开启时禁用保存；保存失败保留勾选，成功更新已保存快照并刷新当前用户列表，保留当前组与页码。
自动授权切换立即保存，成功后更新组状态、清空旧用户与勾选快照，再查询用户；开启时禁用手动授权。
保存与自动授权切换不重新查询用户组，避免用户刷新依赖无关请求。筛选和切换用户组回到第一页。
用户组查询、用户查询与提交共用页面 loading；由各操作的最外层管理，内部查询不提前关闭遮罩。
查询和提交期间页面容器通过 inert 防止交叉操作。
页面通过 `onMounted` 加载用户组；工作空间切换由顶部入口整页加载，不额外监听路由重置。
来源标签沿用登录方式枚举与现有“本地创建”文案，兼容 `OAUTH2` 返回值。

## 智能体对话日志

`application-detail/chat-log/index.vue` 参考 `system/operate-logs`，通过 `customHeader` 和 Teleport
使用详情布局的标题栏，组合标题、`MkDateRange`、`MkComplexSearch`、导出和清除策略入口，
不嵌套 `MkViewLayout`。挂载时查询过去 7 天，搜索、日期和反馈筛选变化后回到第一页，
不监听工作空间路由参数，也不新增权限判断。
列表使用 `MkTable`，勾选用于导出和批量添加到知识库；无勾选时导出当前筛选结果。列表和导出使用同一组查询条件，
切换筛选或分页后清空旧选择。点赞、点踩最小值使用 `MkTableFilter mode="custom"` 的默认作用域插槽编辑，
页面只维护已生效值和全 0 的 `resetValue`；浮层、草稿、重置与确认由公共组件管理，确认或重置后重新查询。
自定义日期清空后清空列表并禁用导出，重新选择有效日期再查询。
来源枚举位于 `api/enums/chat-log.ts`，页面标签位于本功能的 `constants.ts`。

`chat-log/index.vue` 统一导入完整 ChatLog API 对象，通过 `api` Prop 传给清除策略与添加知识库
按钮，并继续透传至弹窗；子组件仅类型导入 ChatLog API。知识库及文档选项 API 暂由添加知识库弹窗直接导入。

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
`add-knowledge/` 集中维护 `ButtonAddKnowledge` 和 `AddKnowledgeDialog`，批量入口固定打开时的
对话 ID，弹窗参考 `DocumentMigrateDialog` 的顶部标签表单与带知识库图标的可搜索下拉框。
每次打开查询当前工作空间知识库，选择知识库后查询全部文档并清空旧文档选择；知识库与
文档必选，提交期间使用内容 loading。成功关闭、清空表格勾选并刷新标注数量，失败保留选择。

## 对话端单应用与门户对话页面

`views/chat/index.vue`（`chat-home`、`chat-home-detail`）与 `views/portal/index.vue`
（`portal-application`、`portal-application-chat`）分别渲染对话面板的 chat、portal 视图。页面只负责：

- 以 `auth.token` 作为面板的 `key`，token 变化（401 重新认证、登录）时重建面板并重新加载数据；
  token 被清除后不渲染面板，等待守卫重新认证。
- token 变化时重新加载当前对话用户档案，供侧栏账户入口展示。

对话面板 chat 模式的装配函数 `view/chat/index.ts` 通过 `ChatConversationRouting` 获取智能体 ID
与会话地址，单应用使用默认实现（智能体 ID 取自 `auth.applicationId`，地址为 `/:accessToken/c/:chatId`），
portal 模式传入门户实现（智能体 ID 取自路由 `applicationId`，地址为 `/portal/a/:applicationId/c/:chatId`）：

- 加载智能体名称与图标；切换智能体时停止当前生成，重新加载智能体信息与会话列表。
- 当前会话与地址双向同步：`currentChatId` 变化时替换地址，新建对话（ID 为空）去掉会话 ID；
  地址变化（含浏览器前进、后退）时切换到对应会话；初始地址带会话 ID 时打开该会话。
- 会话列表 Store 不感知路由；debug 模式的地址不含会话 ID，不做同步。
- 侧栏账户信息由 chat、debug 装配函数分别从各自入口的用户 Store 提供，侧栏组件不直接读取 Store。

portal 模式（`view/portal/`）复用 chat 模式装配，左侧使用 `left-sidebar/portal-conversation-list/`：
按智能体分组展示门户历史对话（`/v3/portal/chat`），每组最多显示最近 5 条。当前智能体的分组以会话列表
Store 为准，新建、重命名、删除即时生效；离开某个智能体时把其最新会话写回分组，并先用进入分组已有的会话填充会话列表，
避免列表加载完成前显示上一个智能体的会话。展开其他智能体的分组时
按智能体查询最近 5 条会话（`/v3/application/:id/chat/1/5`）刷新分组，失败时保留分组接口返回的会话。点击当前智能体的会话
直接切换，点击其他智能体的会话跳转到对应地址。
点击智能体行选中该智能体并进入其新建对话（`portal-application`），没有选中会话时该行高亮；点击右侧箭头只展开或收起会话。

门户首页 `portal-home` 也渲染该页面：地址中没有智能体时不请求会话与智能体信息，分组加载后替换到第一个
智能体的 `portal-application`；没有可访问的智能体时消息区显示“暂无可用智能体”空状态。
门户主区域使用 `main/portal-chat-panel`，不修改共用的 `main/chat-panel`：标题栏的新建对话使用门户侧栏 Store 的
`newConversation`，没有当前智能体时以空状态代替消息列表。没有当前智能体时，
chat 装配函数通过 `disabled` 禁用输入框与附件。

“全部智能体”（`portal-application-list`）在同一门户布局中把主区域换成 `main/portal-application-panel`：
按名称搜索（输入防抖 300ms）并以卡片展示智能体，点击卡片或悬停显示的“去对话”进入该智能体的新建对话。
卡片由 `components/portal-application-cards` 提供，全部智能体页与选择智能体抽屉共用。

侧栏“新建对话”与侧栏收起时标题栏的“新建对话”（门户视图向 `ChatHeader` 传入 `newConversation`）
在当前智能体中新建；没有当前智能体时（全部智能体页、门户首页空状态）打开 `SelectApplicationDrawer` 选择智能体，抽屉的搜索条件与结果独立于全部智能体页，每次打开重新查询。
抽屉自己管理显隐并暴露 `open()`；门户视图持有抽屉的 ref，通过 `createPortalConversation` 的
`openApplicationSelector` 传入门户侧栏 Store。Store 的 `newConversation` 有当前智能体时打开其
`portal-application` 地址，地址中会话 ID 清空后由 chat 装配函数的会话同步新建对话。

### 知识库详情上下文装配

上下文只维护共享详情数据、更新能力及多个子页面共用的接口。仅由单个子页面使用的接口，
在该页面内部按资源范围选择，不为单页接口增加 context 配置或转发 getter。
定时同步接口属于定时同步页自身职责；未提供对应范围接口时，不回退到 Workspace，
也不为 Workspace 共享只读资源增加写接口。同步接口由 `useKnowledgeSyncContext` 提供给定时同步页，
按现有四套 Sync API 的真实方法集合装配，不扩展接口。

`provideKnowledgeDetailContext` 在详情入口装配并提供上下文，`useKnowledgeDetailContext` 供子页读取。
基础设置和文档策略通过 `useKnowledgeSettingContext` 获取可管理范围的完整 Knowledge API 类型，
该设置上下文的 `resourceApi` 仅提供 `knowledge`；定时同步通过 `useKnowledgeSyncContext` 读取当前
`resourceApi.sync` 及可保存范围的 `requestSettingApi`。Workspace 共享只查询设置和日志，表单只读且不显示保存。
不在页面用方法是否存在判断可写能力；上下文边界排除 Workspace 共享只读范围，
共享设置路由已注册，API 上下文仍保留原有只读边界，写接口接入暂缓。
上下文按响应式 `resourceScope` 选择各范围现有完整 Knowledge、Sync API 对象，
统一通过响应式 `resourceApi.knowledge / sync` 提供接口，脚本调用不需要 `.value`；
详情查询与保存使用同一个完整 Knowledge API 对象，不存在的设置模块保持 undefined。
返回列表路由独立提供；不要在 setup 时解构 `resourceApi` 内的具体 API，以免固定为旧范围的对象。
不根据 URL 猜测来源，不为补齐方法集合构造请求，不让缺失模块回退 Workspace。
目前仅详情入口及 setting 下的基础设置、文档策略、定时同步页面采用上下文 API；
library 下的文档、标签与迁移入口通过 `useKnowledgeLibraryContext` 读取现有 API，
`resourceApi.document / tags` 是可选的查询模块；System 两种来源未提供时不发送请求。
与 sync 一致，维护接口只通过 `requestSettingApi` 提供，内部使用完整的 `document / tags / workflow / knowledge` API；
仅 Workspace 普通范围提供该维护入口，分别传给已有操作组件；不为共享或 System 补造写接口。共享标签页按现有无查询参数接口读取，
在本地按标签名称筛选，不展示维护入口；关联文档数量仅作文本展示。
同步日志通过完整 Sync API props 请求。展示组件不接收上下文 API。
System 飞书专用保存方法尚未提供，基础设置沿该范围现有 `putKnowledge` 协议；Workspace 飞书保留专用方法。

四套知识库详情菜单及来源导航已统一，`useKnowledgeNavigationContext` 仅维护路由名称与参数，
不配置 API。各范围接口存在差异，API 模块保持原实现；目前已补齐 sync 与 library 的现有接口装配与消费，
其他模块后续按每套真实接口分别接入，不将菜单完整度视为接口接入完成。

### 资料库上下文与只读范围

`useKnowledgeLibraryContext` 复用详情数据、知识库 ID 和响应式资源范围，文档及标签查询通过
`resourceApi.document / tags` 访问当前范围完整 API。缺失模块保持 undefined，页面展示未接入空态，
不轮询或发送 Workspace 请求。文档页切换知识库、工作空间或范围时清空筛选、分页和选择；标签页同时重置标签组。
Workspace 共享文档保留查询和标签展示，标签页保留标签组查询；只支持共享接口现有的方法。
创建标签弹窗必须由入口传入完整 Tags API，不再默认使用普通 Workspace；文档标签添加及迁移的
候选查询同样通过资料库上下文选择。图片页保持占位，不配置不存在的接口。

资料库所有消费方沿用 Sync 的双入口结构，包括文档页、标签页、文档标签添加弹窗、标签创建入口、
文档迁移弹窗以及传入 Action / Drawer 的 API：查询模块通过响应式 `resourceApi` getter 读取，
维护模块通过单个 `requestSettingApi` 读取，不再为各模块暴露独立 computed 入口。
方法内部选定完整业务 API 时继续使用局部变量 `requestApi`，它不属于新的上下文入口。
