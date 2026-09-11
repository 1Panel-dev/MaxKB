# Workflow Canvas 目录说明

本文档维护 `src/workflow-canvas/` 的职责、目录边界与开发约定；规则或对外接口变化时同步更新。

## 职责边界

`workflow-canvas` 是基于 LogicFlow 的工作流画布模块，负责：

- 初始化和销毁 LogicFlow，注册节点、边与画布插件。
- 渲染、校验和导出图数据，提供添加节点、清空画布、适应视口等画布操作。
- 提供所有节点共用的容器、级联选择器、连线、快捷键、校验及 Teleport 基础能力。
- 维护节点定义、菜单分组、类型映射、图标和节点内部交互。

画布页面位于 `src/views/workflow/`，负责路由参数、页面头部及加载、保存、发布编排，
详见“View 接入约定”；画布模块不承载路由或 Layout。

## 目录结构

```text
src/workflow-canvas/
├── component/          # NodeAdd、NodeSearch、节点设置及预留的 NodeControl
├── config/             # 节点数据、映射、常量及预留的本地化配置
├── details/            # 执行详情：顶层分发入口与公共卡壳，节点内容由 nodes/*/details/ 提供
├── core/               # 稳定的画布内核与所有节点共用的基础能力
│   ├── edge/           # 普通边、循环边及边删除按钮
│   └── node-container/ # 节点容器、锚点按钮及私有的条件、操作下拉组件
├── icons/              # 节点图标及图标解析工具
├── node-menu/          # 按模式组织基础组件、数据源、工具与智能体菜单
├── nodes/              # 已迁入节点的注册文件和 Vue 实现
├── plugins/            # 仅供画布使用的 LogicFlow 插件
├── store/              # 按资源范围适配查询接口，提供缓存及在途请求去重
├── index.vue           # 画布入口组件 WorkflowCanvas
├── style.scss          # 画布内 LogicFlow 全局样式覆盖
├── types.ts            # 画布协议类型和枚举
└── WORKFLOW_README.md  # 本文档
```

### `core/`

`core` 是配置完成后应保持稳定的基础层。`node-container/index.vue` 提供节点的
通用结构与交互能力，属于核心代码；连线、快捷键、公共校验、Teleport 和节点公共工具也放在
这里。`node-container/` 内的条件和操作下拉组件是节点容器的私有实现，不作为画布可复用组件
单独引用；`edge/` 集中维护边的 LogicFlow 注册配置、模型、视图和删除按钮，主画布和循环体均注册
`AppEdge`、`LoopEdge`，默认边为 `app-edge`，`loop-edge` 用于连接循环节点与循环体。只有某项行为是全部或大多数节点
都必须遵守的画布规则时，才修改 `core`。新增普通节点不应要求调整核心层。

节点内需要跟随画布缩放的浮层应保留 `teleported="false"`。如果浮层可能与后绘制的 SVG 锚点
重叠，使用 `core/utils.ts` 的 `createAnchorGuard()`，通过唯一 key 同步各浮层的
`visible-change` 状态，并在节点组件卸载时调用 `reset()`；不要通过 Teleport 到 `body` 或增加
`z-index` 绕过画布的缩放和 SVG 绘制顺序。

`component/NodeCascader.vue` 提供上游变量选择，已在内部统一管理下拉层的锚点保护，使用方无需重复接入。
组件在选值回写及 Vue 更新完成后触发表单校验，清空统一回写空数组；`validateEvent` 默认为
`true`，设为 `false` 可关闭自动校验。
下拉展开时通过 `document` 捕获阶段的 `pointerdown` 处理外部点击，排除组件内部的输入框和
未 Teleport 的下拉面板；关闭及卸载时移除监听。不要移除节点容器的鼠标事件隔离来恢复外部关闭，
以免操作表单时触发画布拖拽。
节点内容区、标题操作区和节点菜单在冒泡阶段拦截 `pointerdown`，避免表单或列表排序同时启动
LogicFlow 的节点拖拽；仅拦截 `mousedown` 无法隔离当前版本的 Pointer Events。不要在捕获阶段
拦截，以免阻断内部排序手柄；也不要拦截 `pointerup`，保留已启动拖拽的结束事件。节点标题区域
继续允许正常拖动节点。
同一节点的多个 `createAnchorGuard()` 实例共享浮层状态，最后一个浮层关闭或卸载后才恢复
节点原本的 `hittable` 状态。

锚点按钮与 `el-tooltip` 集中在 `core/node-container/NodeAnchor.vue`。`workflow-node.ts` 负责
锚点坐标、连接状态，并将 LogicFlow 组件的挂载、Props 更新和卸载同步到现有 Vue Teleport
容器；`teleport.connect()` 的可选第五个参数用于传入组件 Props。节点容器
保留菜单开关与外部点击关闭逻辑，不维护锚点 tooltip 的状态或虚拟触发器。

画布弹窗统一使用 `MkDialog`，由公共组件负责打开时挂载、关闭动画结束后卸载。
保留业务 `open()`、`close()` 和 `closed` 流程，不在调用处根据可见状态直接卸载。

### `config/`

`config` 是随业务持续维护的配置层，增加、删除或调整节点时通常会更新：

- `node-data.ts`：节点的静态定义和默认属性，只存放数据。
- `node-mapping.ts`：节点类型到配置数据的映射、模式匹配和默认节点集合。知识库的
  `defaultKnowledgeNodes` 使用本地文件数据源；`defaultApplicationNodes` 使用基本信息与开始，
  `defaultToolNodes` 使用工具基本信息与工具开始，均作为空工作流的初始节点。
- `constants.ts`：仅供工作流画布使用的稳定常量。
- `locale.ts`：预留的节点文案本地化配置；国际化接入前不参与当前逻辑。

配置数据中的函数应提取到对应职责文件，不把行为逻辑混入 `node-data.ts`。当前尚未接入国际化
的文案直接使用中文，不从 `@/locales` 引入 `t`。

### `node-menu/`

`node-menu` 集中维护画布节点选择菜单。`menu.ts` 定义不同画布模式下的基础组件分组；
`BasicNodeMenu.vue` 负责基础组件搜索和列表；`ResourceNodeMenu.vue` 负责工具、数据源与智能体的文件夹、
搜索和资源列表；`index.vue` 只负责 Tabs 和事件汇总。`component/NodeAdd.vue` 负责画布左上角的
悬浮入口与菜单显隐；画布入口传入 `workflowMode` 并完成节点创建。左上角和锚点菜单均支持点击与拖拽添加。

工作流 Store 的 `getToolListWithShared` 用于包含已授权共享工具的选项查询，MCP 节点使用
`tool_type: 'MCP'` 筛选；AI 对话的 `McpSettingDialog` 每次打开通过
`store.force.getToolListWithShared` 刷新同类选项，关闭或重新打开后忽略旧响应，通过 `loaded`
将工具详情提供给资源区回显；取消不修改已选配置。文件夹菜单继续使用 `getAllTool`，不复用这一路查询。

知识库及知识库循环模式的“数据源”页签复用工具资源菜单和工具文件夹，通过 `dataSource`
区分查询：数据源传 `tool_type: TOOL_TYPE.DATA_SOURCE`，普通工具传
`tool_type_list: [TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW]`。当前工作空间使用 `ToolApi.getAllTool`，
共享目录使用 `SharedApi.getAllTool`；菜单只展示启用且类型匹配的资源。
数据源点击和拖拽共用节点构造，使用 `tool-lib-node`，写入 `kind: WorkflowKind.DataSource`、
`condition: 'OR'`、`tool_lib_id` 与输入参数初始值；引用参数初始化为空数组，其余为空字符串。
各资源页签通过独立的 KeepAlive key 保留目录和搜索状态，数据源不会进入智能体查询分支。

基础菜单通过 `getMenuNodes(workflowMode)` 选择，资源页签与基础菜单分别控制：

| 模式                              | 资源页签     | 基础菜单                                                                                            |
| --------------------------------- | ------------ | --------------------------------------------------------------------------------------------------- |
| `Application` / `ApplicationLoop` | 工具、智能体 | 应用节点组；循环模式以 Continue、Break 替代循环节点                                                 |
| `Knowledge` / `KnowledgeLoop`     | 数据源、工具 | 数据源、文档分段、知识库写入等；循环模式以 Continue、Break 替代循环节点                             |
| `Tool` / `ToolLoop`               | 工具         | 普通工具模式含检索和文档分段；循环模式使用独立的 `toolLoopMenuNodes`，含本地/Web 数据源与知识库写入 |

不要从页签是否存在推断节点能否粘贴；粘贴还使用 `config/node-mapping.ts` 的
`workflowModelDict` 过滤资源节点。

### 画布工具与快捷键

左上角工具栏挂载 `NodeAdd` 和 `NodeSearch`。搜索按 `properties.stepName` 忽略大小写匹配，
选中并聚焦结果；`Ctrl/Cmd + F` 打开，Enter 或上下按钮循环切换，Escape 关闭并清空选择。
`NodeControl.vue` 文件存在，但主画布中的控制栏尚未挂载；Dagre 和框选插件已注册。

`core/shortcut.ts` 负责复制、粘贴及删除：粘贴针对当前活动画布，重新生成节点、边及锚点关联 ID，
按模式过滤节点，并按鼠标位置平移。Backspace 删除前检查受保护节点并确认，循环辅助边不能单独删除。
当前 `Ctrl/Cmd + Z` 回调为空，`Ctrl/Cmd + Y` 调用 `redo()`，不要将撤销描述为已接入。

### 资源查询（`store/`）

`useWorkflowStore(apiType)` 是画布查询适配器，不是 Pinia Store。它自动收集 `store/api/*/index.ts`，
按范围、方法与查询参数缓存结果并复用在途请求；`store.force.xxx()` 跳过已完成缓存，仍复用同键在途请求。
主画布从 `resourceScope` 注入读取范围（默认 `workspace`），通过节点上下文传递为 `apiType`。

当前 `workspace` 适配模型、供应商、模型参数、MCP 工具、共享工具选项、工具详情和标签查询；
`system-resource` 仅接入模型列表与参数表单且沿用 Workspace API，`system-shared`、
`workspace-shared` 为空占位，不能据目录名认定已支持完整 System 或共享范围。
节点资源查询可调用此适配器或既有业务 API；工作流加载、保存与发布仍由 View 编排，核心层不承载请求。

### 表格文本省略

`workflow-canvas/` 内所有表格及列禁止使用 `show-overflow-tooltip`（包括 `showOverflowTooltip` 写法）。
需要省略的文本通过列的默认插槽渲染，统一使用 `span.block.truncate` 并绑定原生 `title`；
标题与展示内容使用同一字段或格式化结果，参考 `nodes/base-node/component/user-input/UserInputTable.vue`。

```vue
<el-table-column prop="field" label="参数">
  <template #default="{ row }">
    <span class="block truncate" :title="row.field">{{ row.field }}</span>
  </template>
</el-table-column>
```

### `nodes/`

每个已实现节点使用一个目录，目录中包含 LogicFlow 注册文件 `index.ts` 和节点视图
`index.vue`。节点注册由 `index.vue` 中的 `import.meta.glob('./nodes/**/index.ts')` 自动收集，
不要再维护一份逐项导入列表。

### 通用节点规则

节点自身的表单、状态和专属校验留在节点目录；多个节点共享且属于画布基础协议的能力才上移到
`core`。节点应复用 `core/node-container/index.vue`，需要选择上游节点字段时复用
`component/NodeCascader.vue`。

复杂节点中的普通表单区块直接放在节点 `index.vue`，避免为简单字段读写增加 Props、Emits 和
中间 computed。独立弹窗、资源选择等具有完整交互边界的能力放在节点目录的 `component/` 下；
节点入口负责统一写回节点属性和执行节点级校验。

固定字段写入统一使用直接赋值，例如 `model.properties.node_data = value`、
`model.validate = validate`，不使用 Lodash `set`。写入嵌套字段前保留必要的父对象初始化；
Vue `computed` 的 `set` 和原生 `Map.set()` 按各自 API 正常使用。

默认值补齐和旧数据兼容在节点初始化阶段执行，`computed` getter 只读取数据，不修改节点属性、
调用会修改数据的归一化方法，或通过 Lodash、类型断言绕过检查。容器私有下拉组件通过类型化的
更新事件通知 `NodeContainer` 写回条件、禁用状态和节点名称，不直接修改 Props 中的字段。
节点表单使用 `defaultForm` 与接口返回的 `savedForm` 一次性生成完整数据；模型来源、数组和嵌套
配置等兼容字段在同一次赋值中显式归一化，不连续修改 `node_data` 的单个字段。
支持直接输出给用户的节点使用 `is_result` 保存“返回内容”开关；该设置只在应用、应用循环、
工具和工具循环模式展示。新节点和旧节点缺失字段时的处理沿用 v2 对应节点行为；AI 对话和
问题优化节点会在旧数据缺少该字段且节点位于流程末尾时启用返回内容。

字段表格通过类型化 `v-model` 编辑列表，负责增删改、排序和重名检查；字段弹窗通过
`submit(data, index?)` 提交，表格或节点写回后调用 `close()`，在 `closed` 时重置编辑状态。
节点入口负责输出字段同步、刷新事件和下游失效引用清理，表格与弹窗不直接读写节点模型。
非登录表单使用 `@submit.prevent`，保存和添加由按钮触发。

设置弹窗打开时重置并用 `cloneDeep` 生成草稿，校验通过并保存后回写；取消不修改节点，
关闭动画结束后清理草稿与校验。带开关的设置组件由节点入口按开关挂载。

### 模型选择

单模型选择复用 `SelectModel` 的 `canEditParams` 和 `v-model:model-params`，由其维护参数按钮、
弹窗及切换模型后的默认值。`ToolWorkflowView`、`KnowledgeWorkflowView` 提供
`getModelParamsForm` 注入接口；`ApplicationWorkflowView` 当前未提供该注入。Teleport 节点继承
页面上下文，默认模型抽屉单独提供参数接口，核心层不选择业务接口。
AI 对话及基本信息的语音组件通过局部更新事件回写，父节点合并最新数据，避免连续更新被旧 Props 覆盖。
语音输入、播放参数分别使用 `stt_model_params_setting`、`tts_model_params_setting`。

三类工作流页面将详情加载或保存成功后的配置通过 `defaultModelSettings` 传给画布，节点通过
`WorkflowNodeModel.getDefaultModelConfig(type)` 读取；默认配置不使用 `provide/inject`，
不写入节点持久化数据，也不覆盖自定义配置。默认来源显示已保存的模型 ID 和参数，
使用禁用且隐藏参数按钮的 `SelectModel`；自定义来源编辑节点配置，引用来源使用 `NodeCascader`。

AI 对话、意图识别、问题优化、参数提取、图片理解、视频理解、图片生成、文生视频、图生视频、
语音转文本、文本转语音和多路召回复用 `component/node-model-select/index.vue` 的 `NodeModelSelect`：

- 接收 `nodeModel`、只读 `formData`、`modelType`、`label`、`options`、`providerOptions`；
  默认字段为 `model_id_type`、`model_id`、`model_id_reference`、`model_params_setting`，
  语音节点通过类型化 `fields` 映射 STT/TTS 字段。
- 通过 `update` 提交实际字段的局部更新，由节点合并最新数据；初始化、旧数据兼容和选项查询仍归节点。
- 内部表单项加入节点外层表单，节点统一调用 `formRef.validate()`。
- 切换来源清空引用和旧校验，保留自定义模型与参数；来源和模型下拉统一维护锚点保护。
- `canEditParams` 默认 `true`，仅配置参数字段时启用；`canAdd` 默认 `false`，通过 `refresh` 通知重新查询。

多路召回通过 `fields` 映射 `reranker_model_id*`，不配置参数字段，设置 `:can-edit-params="false"`，
保留独立检索参数弹窗；开启 `canAdd`，添加模型后重新查询重排模型，默认模型同样必填。
基本信息中的语音设置和长期记忆保持各自实现，不接入 `NodeModelSelect`。

### 检索范围

知识库检索与文档标签检索的范围区块使用 `component/node-search-scope/index.vue` 的 `NodeSearchScope`。
组件通过 `formData` 接收 `NodeSearchScopeData`、通过 `selectedKnowledge` 接收包含 ID 回退的
知识库快照，`nodeModel` 仅用于变量选择和浮层锚点保护。`update` 提交范围字段的局部变更，
`update:knowledge` 提交选择或移除后的知识库列表；节点保留快照、关联 ID 和不可见关联的清理逻辑。
组件复用 `SelectKnowledgeDialog`，保留相同 Embedding 模型约束。切换范围保留配置，切换知识库/
文档列表清空引用；引用的必填与有效性校验通过组件内的表单项加入节点外层表单，自定义范围不校验
隐藏引用，也不新增知识库必填限制。文档标签的加载与过滤仍归文档标签检索节点。

### 节点专属约定

#### 工具与字段表格

自定义工具的参数列表、Python 代码与返回内容由节点入口维护；
`nodes/tool-custom-node/component/FieldSetting.vue` 封装添加按钮与参数弹窗，编辑入口调用
`open(data, index)`。新增与编辑按来源重置参数值，保留旧节点位于流程末尾时的返回内容兼容逻辑。

工作流工具节点在入口维护输入参数与返回内容，参数定义通过工作流 Store 强制刷新工具详情，
按 `field` 保留已配置来源和值，同步输入、输出标题及最新输出名称；节点卸载后忽略旧响应。
输入参数保留引用与自定义两种来源，切换到引用时重置为空路径，自定义按数据类型初始化，
数组与字典复用 `JsonInput`。节点只在表单项声明必填规则，统一调用 `formRef.validate()`，
由输入组件触发表单项校验，不维护组件 Ref Map 或重复调用组件暴露的校验方法；来源下拉维护锚点保护。
旧节点缺少返回内容开关时继续沿用无后继节点即开启的兼容规则。

字段编辑除通用规则外，保留以下业务约束：

- 基本信息：用户输入与接口传参交叉检查重名，校验显隐引用；删除字段时同步清理直接展示设置。
- 工具基本信息：字段与标题写回 `properties` 顶层，变更后刷新工具开始节点变量并清空下游缓存；
  工具开始保留 `global` / `output` 分组及旧字段 `name` 回退。
- 参数提取：模型引用与输入变量均检查引用有效性；默认模型读取 `LLM`，新节点使用默认来源，
  旧节点缺少来源字段时保留自定义语义。

#### 知识库与数据源

本地文件与 Web 数据源节点使用统一节点模型和容器，输出分别保留 `file_list` 与 `document_list`。
本地文件节点在初始化时补齐文件格式、数量和大小限制，保留自定义格式；表单校验必选格式和
1–1000 范围的整数限制。格式选择器不 Teleport，并接入锚点保护。Web 节点没有可编辑配置，
不再保留未使用的文档引用表单，也不改写已有 `node_data`。

知识库写入节点使用统一 `WorkflowNodeModel`、`NodeContainer` 和 `NodeCascader`，保留
`node_data.document_list` 引用协议；必填和引用有效性校验统一由表单执行。初始化补齐引用数组，
仅在旧配置未声明 `is_result` 且节点位于流程末端时设为 `true`，不覆盖已保存的输出设置。

知识库基本信息节点同样由节点入口管理 `properties.user_input_field_list`、`user_input_config`，
`UserInputFieldTable` 通过 `v-model` / `v-model:config` 编辑文档设置和标题，使用 `MkTable` 排序。
字段弹窗复用 `MkDynamicsFormConstructor`，保留原有七种输入类型及旧 input/select/date 字段兼容，
标题和字段弹窗统一使用 `MkDialog`。增删、编辑及排序后同步 `config.globalFields` 并失效下游缓存，
输出固定保留 `global.knowledge`，复制引用使用 `copyText`；输出计算不再修改节点数据。

#### 基本信息设置

`component/LongTermSetting.vue` 封装长期记忆按钮与弹窗，通过 `v-model` 接收 `LongTermSetting`，
模型与供应商选项由节点传入；保存时仅合并长期记忆配置。

默认来源通过 `defaultModelSetting` 接收保存后的 `LLM` 配置，使用禁用的 `SelectModel` 展示，
未配置默认模型时阻止弹窗保存；自定义来源保留节点自己的模型与参数。
长期记忆触发方式使用 `MkSourceCard` 展示定时与轮次两种单选卡片，仅在选中卡片内展开配置。
周期与执行时间沿用 v2 的联动级联选择器，切换按钮在周期设置和 Cron 表达式之间切换；保留每日、每周、每月、
按间隔及按轮次的原有保存协议，轮次输入使用 `el-input-number`，范围为 5–100。
轮次、完整周期及 Cron 表达式均接入表单校验；切换触发方式或周期/Cron 模式后，清理隐藏字段提示并校验当前配置。

`component/FileUploadSetting.vue` 封装文件上传按钮与弹窗，通过 `v-model` 接收
`FileUploadSettingData`，确认时校验上传方式必填；节点写回后发送 `refreshFileUploadConfig`
刷新开始节点文件变量。

文件类型与其他文件选择复用手动导入的 `MkCardCheckbox`；扩展名编辑复用非全局组件
`MkTagsEdit`，通过 `v-model` 编辑草稿的 `otherExtensions`，文件类型中已有的扩展名通过
`reservedTags` 传入用于重复检查。文件上传设置通过 `normalizeTag` 传入去除一个前导点并转为
大写的扩展名规则，通过 `addText` 设置“添加后缀名”。组件内部阻止点击冒泡，避免增删扩展名时切换文件类型；
输入临时状态随弹窗内容卸载而清理。

#### 表单收集

`component/form-setting/FormSettingTable` 编辑 `FormField[]`，`FormFieldDialog` 复用
`MkDynamicsFormConstructor`，遵循通用表格提交规则。节点入口补齐旧数据、同步输出和下游引用、
校验显隐条件；上游字段及节点 ID、名称通过 Props 传入，弹窗只补充当前编辑字段之前的表单字段。

当前表单的显隐引用使用真实节点 ID，与 v2 的引用路径一致；保留 `self` 标记供动态表单从本地值取数。
节点初始化时将旧 `self-form` 引用转换为当前节点 ID，并为 v2 的当前节点引用补齐 `self`，不改动上游引用。

#### AI 对话与提示词

AI 对话节点的 `component/resource-setting` 仅渲染技能卡片内的 MCP、工具、Skills 和智能体分组，
各分组直接在入口使用 `MkCollapse`，不再拆分普通列表子组件，仅选择弹窗独立封装。
工具和 Skills 的添加入口复用 `SelectToolDialog`，智能体入口使用 `SelectApplicationDialog`；
Skills 仅查询 SKILL 类型，选择器排除当前路由对应的智能体或工具。确认后同时更新执行用的
ID 数组及 `tool_list`、`skill_tool_list`、`application_list` 回显快照；移除时同步清理快照，
取消不更新节点，旧数据缺少快照时继续显示 ID。
标题、输出执行过程开关与 `mk-white-card` 由节点入口维护。组件通过 `setting`
读取资源配置、通过 `update` 提交局部变更；资源选项由 Props 传入，未接入数据源时默认为空数组。

AI 对话节点的提示词、历史记录、视觉理解和输出思考表单直接在节点入口维护，统一使用全局
`MdEditorMagnify` 和节点表单样式；`component/PromptGenerate.vue` 同时封装生成按钮与弹窗，
接收 `modelId`、`disabled`、`modelOptions` 和 `providerOptions`，内部读取当前路由的智能体 ID。
弹窗顶部复用 `SelectModel`，仅修改本次生成使用的模型；主体展示最新结果与主题输入框，支持停止和重新生成。
重新生成复用上次请求消息，关闭时终止请求并在关闭动画结束后清理会话；点击替换后通过 `replace` 交由节点回写系统提示词。
生成接口沿用智能体已保存的参数，弹窗不提供独立模型参数设置。
AI 对话、图片理解和视频理解统一复用 `component/ThinkingSetting.vue`，后续同类入口也应复用。
组件通过 `v-model` 接收 `types.ts` 的 `ReasoningSettingData`，由节点的输出思考开关以 `v-if` 挂载，
遵循通用设置弹窗规则；开始、结束标签当前不设必填。

问题优化、图片理解和视频理解节点的系统提示词与用户提示词，以及图片、文生视频和图生视频
节点的正向与负向提示词同样使用 `MdEditorMagnify`，必填字段由所在节点表单统一校验。

#### 检索与文档处理

知识库检索在入口维护范围、参数摘要、问题表单和关联数据；`component/SearchSetting.vue`
封装参数按钮与弹窗，通过 `v-model` 编辑并遵循通用设置弹窗规则。范围引用加入节点表单，
问题引用保留独立有效性检查；移除关联只清理明确取消的 ID，保留当前用户不可见的知识库。
检索模式协议复用 `KNOWLEDGE_SEARCH_MODE`。

文档内容提取、多路召回和文档标签检索节点使用统一的节点标题、`mk-gray-card`、表单必填标记与
`MkIcon`。多路召回的参数设置按钮与弹窗封装在节点 `component/SearchSetting.vue`，通过
`v-model` 接收检索参数，遵循通用设置弹窗规则，并复用 `MkSlider`。
重排内容使用 `MkFormList` 并隐藏内置添加按钮，由标题栏按钮深拷贝新增空引用，保留至少一行。文档标签检索通过
`NodeSearchScope` 复用知识库选择，保留知识库快照及缺少详情的关联 ID；标签条件使用
`MkFormList` 并设置 `minRows` 为 `0`，节点模型统一将新建及已有节点宽度设为 `455`。
`store/api/workspace/index.ts` 独立维护 `getAllTags(knowledgeIds)`，使用 `knowledge_ids[]` 查询
所选知识库的全部文档标签，返回 `KnowledgeTagGroup[]`。文档标签选项通过工作流 Store 的 `force.getAllTags(knowledgeIds)` 查询，刷新时跳过已有标签缓存。
多路召回优先使用 `getRerankerModels` 注入，当前页面未提供时回退到
`store.getModelList({ model_type: 'RERANKER' })`。添加模型后触发 `refreshModels()`，
该回退仍读取缓存，不能视为强制刷新。
标签请求只回写当前关联知识库的结果，过期或节点卸载后的响应不再修改节点。

文档分段节点使用 `WorkflowNodeModel` / `WorkflowNodeView` 注册，在入口维护智能、高级和问答对
三种策略。保留 `referencing` 来源协议、子分块长度默认 256、分段长度默认 4096，以及高级策略和
问答对策略下的字段显隐。文档与当前可见的配置引用仅在表单项声明数组必填规则，
由 `NodeCascader` 触发表单项校验，节点统一调用 `formRef.validate()`，不维护引用组件校验 Ref；
切换来源或策略保留字段值并清理校验和浮层保护。`constant.ts` 保存与后端
`DocumentSerializers.SplitPattern` 一致的固定标识选项，不依赖旧知识库路由或旧版动态 API，
仍支持按选择顺序递归分割和添加自定义标识。

#### 循环画布与导出

`loop-node` 展开后通过 `loop-body-node` 创建嵌套 LogicFlow；循环体继承父画布资源范围、
默认模型读取函数及 `loopWorkflowMode`，并修正坐标转换以计入父画布缩放。
`setLoopBody()` 将循环体位置写入父节点 `node_data.loop`，图数据写入 `node_data.loop_body`。
主画布 `getGraphData()` 先同步循环体，再从顶层结果排除 `LoopBodyNode` 和 `loop-edge`；
保存必须调用此方法，不能直接持久化主画布原始图数据。

循环体验证在节点表单校验后调用循环图校验；知识库循环使用 `KnowledgeWorkFlowInstance`，
其他循环使用 `WorkFlowInstance`。`loop_type === 'LOOP'` 时要求包含 Break，失败时聚焦循环体。

#### 循环控制

Break 和 Continue 节点在各自入口维护 `condition`、`condition_list` 条件表单，复用 `MkFormList`
完成增删，显式设置 `minRows` 为 `0`，保留 v2 的默认空列表及允许删除最后一项的行为。
多条条件时显示“所有／任一”；比较符复用 `config/constants.ts` 的 `compareList`，为空、不为空、
为真、不为真时隐藏比较值并跳过其必填校验，不改写已保存的比较值。节点级校验统一调用外层表单，
比较符和逻辑下拉保持 `teleported="false"`，通过 `createAnchorGuard()` 保护锚点。

### 节点列表排序

`MkFormList` 和 `MkTable` 均为全局自动注册组件，节点模板直接使用，无需手动导入；
组件 API 与注册规则以 `../components/COMPONENT_README.md` 为准。

普通节点列表、表单行和字段表格统一复用 VueDraggablePlus 支撑的共享排序能力：表单行使用
`MkFormList` 的 `sortable` 与稳定 `item-key`，字段表格使用 `MkTable` 的 `sortable` 与
`v-model:data`，其他列表使用 `@/utils/use-sortable`。不要在节点中直接创建 SortableJS 实例、
手动恢复排序 DOM，或在库已更新数组后再次移动数据。

MkFormList 的排序、增删均以 `cloneDeep` 回写；MkTable 保留普通行对象引用，因此工作流节点
在 computed setter 中深拷贝新数组后写回 `model.properties.node_data`，并执行原有字段同步。
带 ID 的新行使用 `default-item` 工厂函数，每次添加生成独立 ID。条件分支等保留锚点 ID、
固定末尾分支的特殊规则不能直接替换成普通列表移动。判断器仅将 IF / ELSE IF 分支放入排序容器，
卡片悬停时显示排序手柄；ELSE 独立渲染并固定末尾。排序后按位置更新分支名称，保留分支 ID，
并同步刷新锚点顺序与连线。

### 执行详情（`details/`）

节点执行详情与画布节点注册同源，通过节点类型分发：

- `details/index.vue`（`ExecutionDetailContent`）是顶层分发层：接收 `detail` 数组和 `workflowMode`，
  按 `index` 升序，逐项按节点类型渲染对应节点的详情组件。类型到详情组件的映射来自
  `import.meta.glob('../nodes/*/index.ts')` 收集的默认导出中的 `details` 字段，与画布节点注册同一份
  清单，不按目录名推断，也不再单独维护映射表。未注册详情的类型当前跳过渲染。
- `details/DetailContainer.vue` 是与节点类型无关的布局容器：提供 `#header` 具名
  插槽（透出折叠 `show`）、折叠体默认插槽承载节点内容，以及 `showContentOnError` 决定失败时是否仍
  展示内容（默认失败只显示错误日志块）。
- `details/BaseHeader.vue` 是公共头部：折叠箭头、节点图标、名称、耗时和状态图标；是否显示 tokens 由
  节点通过 `show-tokens` 布尔控制，tokens 数值由 `BaseHeader` 从 `data` 自行计算，容器不参与该判断。
- 详情载荷类型 `ExecutionNodeDetail` 在 `details/types.ts`，以开放索引签名承载各节点动态字段，仅显式
  声明外层卡片通用字段；分发和模式统一使用 `WorkflowMode` 枚举，不自造字符串联合类型。

每个节点的详情入口统一为 `nodes/<node-type>/details/index.vue`，并在该节点 `index.ts` 的默认导出中通过
`details` 字段注册（LogicFlow 注册忽略该额外字段）：

- 内容不随工作流模式变化的节点（如循环），`details/index.vue` 直接就是详情内容。
- 内容随模式不同的节点（如 AI 对话），`details/index.vue` 按 `workflowMode` 用映射分发到同目录下的
  `application.vue`、`knowledge.vue` 等模式文件，其它模式兜底到应用视图；各模式文件各自完整、自包含，
  共用部分不强行抽取。

文件类型图标复用 `@/utils/icon` 的 `getFileIconUrl`。
详情内的灰底标题块直接使用内联 Tailwind（`overflow-hidden rounded-md bg-N100` + `h5.px-3.py-2` +
`border-t border-dashed px-3 py-2 text-N900`），不引入独立的区块组件。只读 Markdown 回答复用全局
`MdPreview`，并在节点内通过 `:deep()` 覆盖其固定高度与背景以融入灰底。

循环详情是唯一递归点，负责循环设置和轮次选择，将选中轮次的子节点交给 `ExecutionDetailContent` 排序、分发，
并传 `show-content-on-error`，允许整体失败时查看已执行子节点。递归数据不得包含循环自身；
组件间的循环 import 仅在渲染期使用，不在模块求值期调用。

知识库检索详情按相似度降序展示 `paragraph_list`；多路召回分别展示 `document_list` 和
`result_list`，段落直接在节点详情中渲染并复用 `MdPreview`，不依赖 `ParagraphCard`。
文档标签检索展示知识库、文档名称；表单收集复用只读 `MkDynamicsForm`，并标记未提交状态。

## View 接入约定

- 所有画布路由页面均放在 `src/views/workflow/`，并以 `XxxWorkflowView.vue` 命名，例如
  `ApplicationWorkflowView.vue`、`KnowledgeWorkflowView.vue`。
- View 在 `WorkflowCanvas` 外部组织页面头部的保存、发布、调试等页面级操作；添加组件属于画布操作，
  由 `WorkflowCanvas` 内的 `NodeAdd` 统一提供。
- 画布页面需要独立全屏展示时，由 `src/router/admin/workflow/` 配置不挂载业务 Layout 的路由；
  画布模块不处理路由。
- View 通过 Props 或实例方法传入图数据，加载、保存及错误处理由 View 或所属业务层编排；
  当前三个页面加载完成后调用 `render()`，等待 Vue 更新后记录图快照并 `fitView()`。
- View 显式传入成对的 `workflowMode` / `loopWorkflowMode`，分别用于主画布和循环体菜单。
- 页面共用 `views/workflow/components/WorkflowViewLayout.vue`，由其展示标题、保存时间与返回入口，
  页面通过 `actions` 插槽提供按钮；当前三个路由均为 Workspace 全屏路由。

`WorkflowCanvas` 的 Props：

| Prop                   | 默认值                         | 用途                                                                 |
| ---------------------- | ------------------------------ | -------------------------------------------------------------------- |
| `data`                 | `null`                         | 挂载时的初始图数据；后续变化需显式调用渲染方法，当前没有监听自动重绘 |
| `workflowMode`         | `WorkflowMode.Application`     | 主画布模式                                                           |
| `loopWorkflowMode`     | `WorkflowMode.ApplicationLoop` | 循环体模式，不会根据主模式自动推导                                   |
| `defaultModelSettings` | 未设置                         | 节点按需读取的默认模型配置                                           |

`WorkflowCanvas` 当前对外暴露的方法包括：

| 方法              | 用途                                |
| ----------------- | ----------------------------------- |
| `addNode`         | 在画布中心添加指定节点              |
| `getGraphData`    | 获取规范化后的图数据                |
| `renderGraphData` | 创建新的 LogicFlow 实例并渲染图数据 |
| `render`          | 使用现有实例重新渲染图数据          |
| `clearGraphData`  | 清空画布                            |
| `fitView`         | 调整画布到合适视口                  |
| `validate`        | 并行调用节点校验，返回 Promise      |
| `onmousedown`     | 启动节点拖拽或执行节点回调          |

`getGraphData()` 在实例未初始化时返回 `undefined`；`validate()` 此时返回已完成的空数组 Promise，
有实例时汇总节点各自的校验，不额外执行顶层图结构校验。

当前 `renderGraphData()` 不主动销毁上一实例；普通数据加载使用 `render()`，不要将前者当作
已封装完整清理的重置方法。画布卸载时销毁当前实例并清理 Teleport。

默认模型入口由 `DefaultModelSettingButton` 延迟挂载抽屉；`save` 交由页面持久化配置。
“应用到所有节点”确认后深拷贝图数据，递归切换循环体及相关节点的模型来源，保留自定义模型和参数，
基本信息仅处理已启用的语音、长期记忆设置并保留浏览器语音。`apply-to-all` 由页面调用
`renderGraphData()` 更新画布，本身不保存图数据，也不提交抽屉中的模型草稿。

## 节点维护流程

新增或迁入节点时，按实际需要检查以下位置：

1. 在 `types.ts` 的 `WorkflowNodeType` 中声明稳定的 LogicFlow 节点类型值。
2. 在 `config/node-data.ts` 中添加节点静态配置。
3. 在 `config/node-mapping.ts` 中维护节点映射；需要作为初始节点时再加入默认节点集合。
4. 在 `node-menu/menu.ts` 中加入适用画布模式的菜单分组。
5. 在 `nodes/<node-type>/` 中实现注册文件和节点视图，并按需增加 `icons/` 图标。
6. 如需执行详情，在 `nodes/<node-type>/details/index.vue` 中实现，并在 `index.ts` 默认导出中通过
   `details` 字段注册；内容随模式变化时在该目录下按 `workflowMode` 分发到模式文件。
7. 确认节点能被自动注册、从菜单添加、正确连线、校验并导出图数据。

节点协议值统一使用 `WorkflowNodeType` 等枚举或画布常量，不在判断和映射中重复书写
`ai-chat-node`、`tool-custom-node` 等字符串字面量。

## 当前接入状态

以下按当前源码启用的行为记录；节点实现与详情覆盖分别以 `nodes/*/index.ts` 的模型注册和
`details` 字段为准，不以文件存在或注释中的预留代码判断完成。

| 页面                                      | 已接入                                                                       | 尚未启用                                       |
| ----------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------- |
| `application/ApplicationWorkflowView.vue` | 详情加载、默认节点、手动保存、默认模型设置、调试对话                         | 发布按钮目前仅校验，发布请求和自动保存均被注释 |
| `tool/ToolWorkflowView.vue`               | 工具与工作流详情加载、默认节点、手动保存、默认模型设置、校验后保存并发布     | 调试、自动保存                                 |
| `knowledge/KnowledgeWorkflowView.vue`     | 从知识库详情加载、本地文件默认节点、手动保存、默认模型设置、校验后保存并发布 | 调试、自动保存                                 |

三个页面的返回按钮均提供“保存并退出 / 直接退出”确认；选择保存时成功后才退出，
关闭确认框则留在当前页。当前没有路由离开或浏览器关闭守卫。
智能体调试使用 `Conversation` 的 `DEBUG` 模式，有未保存图改动时先保存，再打开右侧可放大的对话面板。
知识库默认模型已接入前端详情与保存协议，服务端持久化要求见 `../api/API_README.md` 的“知识库工作流”。

执行详情已包含知识库检索、多路召回、文档标签检索、表单收集和语音节点；文档分段、知识库写入、
本地/Web 数据源尚无 `details` 注册。基本信息类节点和循环体辅助节点同样未注册独立详情。
发布历史、模板中心、完整国际化尚未接入；资源范围适配的限制见“资源查询”。

## 检查

修改后至少运行与改动范围相符的检查：

```bash
npm run type-check
npx eslint <本次修改的Vue或TypeScript文件>
git diff --check
```

当前 `npm run lint` 尚未配置对应的 `lint:*` 子脚本，不能替代实际 ESLint 检查。
仅修改 Markdown 文档时，检查修改文件的 Prettier 格式、路径引用及 `git diff --check` 即可。

若当前迁移中的预留文件仍存在已知类型错误，应在交付说明中明确区分，不要通过改变现有画布业务
逻辑来绕过。
