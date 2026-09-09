# Workflow Canvas 目录说明

本文档是 `src/workflow-canvas/` 的职责、目录边界和维护方式的唯一依据。调整画布基础能力、
节点配置、节点实现或对外接口前，应先阅读并同步更新本文档。

## 职责边界

`workflow-canvas` 是基于 LogicFlow 的工作流画布模块，负责：

- 初始化和销毁 LogicFlow，注册节点、边与画布插件。
- 渲染、校验和导出图数据，提供添加节点、清空画布、适应视口等画布操作。
- 提供所有节点共用的容器、级联选择器、连线、快捷键、校验及 Teleport 基础能力。
- 维护节点定义、菜单分组、类型映射、图标和节点内部交互。

该目录不负责路由页面、页面头部、Layout、保存或发布等页面动作，也不直接承载业务接口调用。
所有使用本模块渲染的画布页面统一放在 `src/views/workflow/`；View 负责路由参数、页面头部、
页面级按钮以及后续的数据加载和保存编排，`WorkflowCanvas` 只负责画布区域。

## 目录结构

```text
src/workflow-canvas/
├── component/          # 画布内可复用的控制、搜索和节点设置组件
├── config/             # 节点数据、映射、常量及预留的本地化配置
├── details/            # 执行详情：顶层分发入口与公共卡壳，节点内容由 nodes/*/details/ 提供
├── core/               # 稳定的画布内核与所有节点共用的基础能力
│   ├── edge/           # 普通边、循环边及边删除按钮
│   └── node-container/ # 节点容器、锚点按钮及私有的条件、操作下拉组件
├── icons/              # 节点图标及图标解析工具
├── node-menu/          # 基础组件、工具和智能体节点菜单及其菜单配置
├── nodes/              # 已迁入节点的注册文件和 Vue 实现
├── plugins/            # 仅供画布使用的 LogicFlow 插件
├── store/              # 按资源范围适配查询接口，提供缓存及在途请求去重
├── index.vue           # 画布入口组件 WorkflowCanvas
├── style.scss          # 画布内 LogicFlow 全局样式覆盖
├── types.ts            # 画布协议类型和枚举
└── WORKFLOW_README.md  # 本文档
```

### `core/`

`core` 是配置完成后应保持稳定的基础层。`node-container/index.vue` 和 `NodeCascader.vue` 是节点的
通用结构与交互能力，属于核心代码；连线、快捷键、公共校验、Teleport 和节点公共工具也放在
这里。`node-container/` 内的条件和操作下拉组件是节点容器的私有实现，不作为画布可复用组件
单独引用；`edge/` 集中维护边的 LogicFlow 注册配置、模型、视图和删除按钮，普通边由画布入口
显式注册，未接入的边类型不得仅因目录调整而改变注册状态。只有某项行为是全部或大多数节点
都必须遵守的画布规则时，才修改 `core`。新增普通节点不应要求调整核心层。

节点内需要跟随画布缩放的浮层应保留 `teleported="false"`。如果浮层可能与后绘制的 SVG 锚点
重叠，使用 `core/utils.ts` 的 `createAnchorGuard()`，通过唯一 key 同步各浮层的
`visible-change` 状态，并在节点组件卸载时调用 `reset()`；不要通过 Teleport 到 `body` 或增加
`z-index` 绕过画布的缩放和 SVG 绘制顺序。

`NodeCascader` 已在内部统一管理下拉层的锚点保护，使用方无需重复接入。
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

画布中的所有弹窗（包括节点重命名、字段编辑和参数设置）统一使用 `MkDialog`，
由公共组件负责打开时挂载、关闭动画结束后卸载，避免每个节点提前生成隐藏 Dialog DOM。
保留业务弹窗的 `open()`、`close()` 和 `closed` 清理流程，不在调用处直接用可见状态卸载弹窗。

### `config/`

`config` 是随业务持续维护的配置层，增加、删除或调整节点时通常会更新：

- `node-data.ts`：节点的静态定义和默认属性，只存放数据。
- `node-mapping.ts`：节点类型到配置数据的映射、模式匹配和默认节点集合。
- `constants.ts`：仅供工作流画布使用的稳定常量。
- `locale.ts`：预留的节点文案本地化配置；国际化接入前不参与当前逻辑。

配置数据中的函数应提取到对应职责文件，不把行为逻辑混入 `node-data.ts`。当前尚未接入国际化
的文案直接使用中文，不从 `@/locales` 引入 `t`。

### `node-menu/`

`node-menu` 集中维护画布节点选择菜单。`menu.ts` 定义不同画布模式下的基础组件分组；
`BasicNodeMenu.vue` 负责基础组件搜索和列表；`ResourceNodeMenu.vue` 负责工具与智能体的文件夹、
搜索和资源列表；`index.vue` 只负责 Tabs 和事件汇总。`component/AddNode.vue` 负责画布右上角的
悬浮入口、菜单显隐，以及点击添加和拖拽添加事件；画布入口传入 `workflowMode` 并完成节点创建。

工作流 Store 的 `getToolListWithShared` 用于包含已授权共享工具的选项查询，MCP 节点使用
`tool_type: 'MCP'` 筛选；AI 对话的 `McpSettingDialog` 每次打开通过
`store.force.getToolListWithShared` 刷新同类选项，关闭或重新打开后忽略旧响应，通过 `loaded`
将工具详情提供给资源区回显；取消不修改已选配置。文件夹菜单继续使用 `getAllTool`，不复用这一路查询。

### `nodes/`

每个已实现节点使用一个目录，目录中包含 LogicFlow 注册文件 `index.ts` 和节点视图
`index.vue`。节点注册由 `index.vue` 中的 `import.meta.glob('./nodes/**/index.ts')` 自动收集，
不要再维护一份逐项导入列表。

工作流中的单模型选择统一使用 `SelectModel` 的 `canEditParams` 和 `v-model:model-params`，
由公共组件维护参数按钮、弹窗和切换模型后的默认值，节点不再单独创建参数弹窗或请求默认值。
AI 对话及基本信息的语音子组件通过局部更新事件回写字段，父节点合并更新，避免模型 ID 与参数
连续更新时被旧 Props 覆盖。语音输入使用 `stt_model_params_setting`，语音播放使用
`tts_model_params_setting`，其他模型节点使用各自已有的参数字段。
`ApplicationWorkflowView` 和 `ToolWorkflowView` 提供 `getModelParamsForm` 注入接口，画布中的
Vue Teleport 节点继承页面上下文；画布核心不负责模型参数接口选择。
智能体页面将详情加载或保存成功返回的配置通过 `defaultModelSettings` Props 传给画布。
`WorkflowNodeModel.getDefaultModelConfig(type)` 通过画布的配置读取函数获取对应模型，不使用
默认配置的 `provide/inject`，也不写入节点持久化数据。AI 对话、意图识别、问题优化、语音、
图片、视频及参数提取相关节点在默认来源下读取保存后的对应模型 ID 和参数，使用禁用且隐藏参数按钮的
`SelectModel` 展示；自定义来源继续编辑节点自身配置，引用来源使用 `NodeCascader`。默认配置
只用于解析当前使用的模型，不覆盖节点保存的自定义配置。

AI 对话、意图识别、问题优化、参数提取、图片理解、视频理解、图片生成、文生视频、图生视频、
语音转文本、文本转语音和多路召回这 12 个节点统一使用 `component/node-model-select/index.vue` 的
`NodeModelSelect`。组件接收 `nodeModel`、只读 `formData`、`modelType`、`label`、`options` 和
`providerOptions`；默认字段为 `model_id_type`、`model_id`、`model_id_reference` 与
`model_params_setting`，语音节点通过类型化的 `fields` 映射 STT/TTS 字段。组件通过 `update`
提交实际字段的局部更新，节点合并最新数据后写回；初始化、旧数据兼容和选项查询仍由节点负责。
组件内部的 `el-form-item` 注册到节点外层表单，节点只需调用原有 `formRef.validate()`。
默认来源检查保存后的默认模型，自定义来源检查模型 ID，引用来源检查必填并调用
`NodeCascader.validate()` 检查引用有效性。切换来源清空引用与旧校验，保留自定义模型和参数。
来源及模型下拉由组件统一维护锚点保护；参数按钮与默认参数加载继续复用 `SelectModel`。
多路召回通过 `fields` 映射 `reranker_model_id*`，不提供参数字段，并设置 `canEditParams` 为
`false`，仅保留独立的检索参数弹窗；模型校验统一遵循上述规则，包括默认模型必填。
`canEditParams` 默认为 `true`，仅配置参数字段时启用；`canAdd` 默认为 `false`，多路召回开启后
通过 `refresh` 重新查询重排模型，保留添加模型能力。
基本信息中的语音设置和长期记忆保持各自实现，不接入该组件。

知识库检索与文档标签检索的范围区块使用 `component/node-search-scope/index.vue` 的 `NodeSearchScope`。
组件通过 `formData` 接收 `NodeSearchScopeData`、通过 `selectedKnowledge` 接收包含 ID 回退的
知识库快照，`nodeModel` 仅用于变量选择和浮层锚点保护。`update` 提交范围字段的局部变更，
`update:knowledge` 提交选择或移除后的知识库列表；节点保留快照、关联 ID 和不可见关联的清理逻辑。
组件复用 `SelectKnowledgeDialog`，保留相同 Embedding 模型约束。切换范围保留配置，切换知识库/
文档列表清空引用；引用的必填与有效性校验通过组件内的表单项加入节点外层表单，自定义范围不校验
隐藏引用，也不新增知识库必填限制。文档标签的加载与过滤仍归文档标签检索节点。

节点自身的表单、状态和专属校验留在节点目录；多个节点共享且属于画布基础协议的能力才上移到
`core`。节点应复用 `core/node-container/index.vue`，需要选择上游节点字段时复用
`core/NodeCascader.vue`。

复杂节点中的普通表单区块直接放在节点 `index.vue`，避免为简单字段读写增加 Props、Emits 和
中间 computed。独立弹窗、资源选择等具有完整交互边界的能力放在节点目录的 `component/` 下；
节点入口负责统一写回节点属性和执行节点级校验。

自定义工具节点的参数列表、Python 代码与返回内容由节点入口维护，参数弹窗放在
`tool-custom-node/component/InputFieldDialog.vue`，同时封装标题栏的添加按钮，编辑入口调用其 `open(data, index)`。
组件通过 `submit(data, index?)` 提交，节点写回后
调用 `close()`。新增与编辑参数继续按来源重置参数值，保留旧节点在流程末尾时的返回内容兼容逻辑。

变量拆分节点的 `VariableFieldTable` 通过 `v-model` 接收 `VariableField[]`，只负责列表增删改、
重名检查和编辑弹窗，不接收节点模型或读写 `node_data`。节点入口在列表写回时同步输出字段并
清理下游失效引用；字段类型由该组件目录的 `types.ts` 统一定义。
`VariableFieldDialog` 与 `GroupFieldDialog` 使用 `submit(data, index?)` 提交，表格通过重名检查并
写回列表后调用 `close()`；关闭动画结束时通过 `closed` 重置表单，添加与编辑共用同一提交流程。

参数提取节点的默认模型读取 `LLM` 配置，新节点默认选择“默认模型”，旧节点缺少来源字段时
保留“自定义”语义。默认模型仅用于展示与校验，不覆盖节点保存的自定义模型和参数。

参数提取节点遵循相同边界：`component/parameters-field` 内的 `ParametersFieldTable` 通过
`v-model` 编辑 `ParameterField[]`，弹窗只通过 `submit(data, index?)` 提交，节点入口同步输出
字段和下游引用。模型引用与输入变量的有效性校验接入节点表单规则，调用 `NodeCascader.validate()`
保留失效引用检查；节点级 `validate()` 统一调用表单校验。所有非登录表单仅使用 `@submit.prevent`，
保存或添加由按钮触发。

基本信息节点的用户输入、接口传参和会话变量分别由 `UserInputTable`、`ApiParameterTable`、
`ConversationVariableTable` 通过 `v-model` 编辑，使用小尺寸 `MkTable` 支持排序。字段弹窗只负责
收集和校验单个字段，通过 `submit(data, index?)` 提交；表格完成重名检查和写回后调用 `close()`。
节点入口深拷贝写回列表并发送原有字段刷新事件，保留显隐条件引用校验。用户输入与接口传参继续
交叉检查参数重名；`UserInputSettingDialog` 独立维护直接展示参数设置，删除字段时由表格清理对应设置。

基本信息节点的 `component/FileUploadSetting.vue` 同时封装文件上传设置按钮与弹窗，
通过 `v-model` 接收 `FileUploadSettingData`。节点入口根据上传开关挂载组件，并在配置写回后发送
`refreshFileUploadConfig` 刷新开始节点文件变量；弹窗打开时重置并深拷贝草稿，确认时保留上传方式
的表单必填校验，取消不修改节点，关闭动画结束后统一清理草稿与校验状态。
文件类型与其他文件选择复用手动导入的 `MkCardCheckbox`；扩展名编辑复用非全局组件
`MkTagsEdit`，通过 `v-model` 编辑草稿的 `otherExtensions`，文件类型中已有的扩展名通过
`reservedTags` 传入用于重复检查。文件上传设置通过 `normalizeTag` 传入去除一个前导点并转为
大写的扩展名规则，通过 `addText` 设置“添加后缀名”。组件内部阻止点击冒泡，避免增删扩展名时切换文件类型；
输入临时状态随弹窗内容卸载而清理。

表单收集节点的 `component/form-setting/FormSettingTable` 通过 `v-model` 编辑动态表单的
`FormField[]`，负责增删改、排序和重名检查；`FormFieldDialog` 复用 `MkDynamicsFormConstructor`，
通过 `submit(data, index?)` 提交，由表格写回后调用 `close()`，关闭动画结束时重置编辑状态。
节点入口负责旧数据默认值补齐、输出字段同步、下游引用清理和显隐条件引用校验；上游字段选项与
节点 ID、名称通过 Props 传入，弹窗只补充当前编辑字段之前的表单字段，不直接读取节点模型。
当前表单的显隐引用使用真实节点 ID，与 v2 的引用路径一致；保留 `self` 标记供动态表单从本地值取数。
节点初始化时将旧 `self-form` 引用转换为当前节点 ID，并为 v2 的当前节点引用补齐 `self`，不改动上游引用。

AI 对话节点的 `component/resource-setting` 仅渲染技能卡片内的 MCP、工具、Skills 和智能体分组，
各分组直接在入口使用 `MkCollapse`，不再拆分普通列表子组件，仅选择弹窗独立封装。
工具和 Skills 的添加入口复用 `SelectToolDialog`，智能体入口使用 `SelectApplicationDialog`；
Skills 仅查询 SKILL 类型，选择器排除当前路由对应的智能体或工具。确认后同时更新执行用的
ID 数组及 `tool_list`、`skill_tool_list`、`application_list` 回显快照；移除时同步清理快照，
取消不更新节点，旧数据缺少快照时继续显示 ID。
标题、输出执行过程开关与 `mk-white-card` 由节点入口维护。组件通过 `setting`
读取资源配置、通过 `update` 提交局部变更；资源选项由 Props 传入，未接入数据源时默认为空数组，
已关联但缺少详情的资源保留 ID 回退展示。

AI 对话节点的提示词、历史记录、视觉理解和输出思考表单直接在节点入口维护，统一使用全局
`MdEditorMagnify` 和节点表单样式；AI 提示词生成使用独立弹窗。AI 对话、图片理解和视频理解节点的
输出思考设置统一复用 `component/ThinkingSetting.vue`，后续同类入口也应引用该组件。组件通过
`v-model` 接收 `types.ts` 中的共享配置类型 `ReasoningSettingData`；节点入口维护输出思考开关，
并根据开关用 `v-if` 挂载设置组件。弹窗打开时重置并深拷贝草稿，仅在校验通过并保存后回写，
取消不修改节点，关闭动画结束后重置草稿及校验状态。当前开始、结束标签未配置必填规则。
问题优化、图片理解和视频理解节点的系统提示词与用户提示词，以及图片、文生视频和图生视频
节点的正向与负向提示词同样使用 `MdEditorMagnify`，必填字段由所在节点表单统一校验。

文档内容提取、多路召回和文档标签检索节点使用统一的节点标题、`mk-gray-card`、表单必填标记与
`MkIcon`。多路召回的参数设置按钮与弹窗封装在节点 `component/SearchSetting.vue`，通过
`v-model` 接收检索参数，保存时深拷贝回写，取消不修改节点；弹窗复用 `MkDialog` 和 `MkSlider`。
重排内容使用 `MkFormList` 并隐藏内置添加按钮，由标题栏按钮深拷贝新增空引用，保留至少一行；
标签条件使用 `MkFormList`，设置 `minRows` 为 `0`，保留允许删除到空列表的语义。文档标签检索通过
`NodeSearchScope` 复用知识库选择，保留知识库快照及缺少详情的关联 ID；标签条件使用
`MkFormList` 并设置 `minRows` 为 `0`，节点模型统一将新建及已有节点宽度设为 `455`。
`store/api/workspace/index.ts` 独立维护 `getAllTags(knowledgeIds)`，使用 `knowledge_ids[]` 查询
所选知识库的全部文档标签，返回 `KnowledgeTagGroup[]`。文档标签选项通过工作流 Store 的 `force.getAllTags(knowledgeIds)` 查询，刷新时跳过已有标签缓存。
`ApplicationWorkflowView` 和 `ToolWorkflowView` 提供重排模型查询注入接口；新增模型后直接重新查询，
不读取已有模型列表缓存。
标签请求只回写当前关联知识库的结果，过期或节点卸载后的响应不再修改节点。

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

节点执行详情按三层组织，与画布节点注册同源，通过节点类型分发渲染：

- `details/index.vue`（`ExecutionDetailContent`）是顶层分发层：接收 `detail` 数组和 `workflowMode`，
  按 `index` 升序，逐项按节点类型渲染对应节点的详情组件。类型到详情组件的映射来自
  `import.meta.glob('../nodes/*/index.ts')` 收集的默认导出中的 `details` 字段，与画布节点注册同一份
  清单，不按目录名推断，也不再单独维护映射表。
- `details/DetailContainer.vue` 是纯布局卡壳（架子），不认识任何具体节点类型：提供 `#header` 具名
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

详情内的灰底标题块直接使用内联 Tailwind（`overflow-hidden rounded-md bg-N100` + `h5.px-3.py-2` +
`border-t border-dashed px-3 py-2 text-N900`），不引入独立的区块组件。只读 Markdown 回答复用全局
`MdPreview`，并在节点内通过 `:deep()` 覆盖其固定高度与背景以融入灰底。

循环节点的详情是唯一的递归点：它维护循环设置与轮次选择，选中某轮后把该轮的子节点数组交回顶层
`ExecutionDetailContent` 渲染（排序与类型分发由顶层负责），并对外层卡壳传 `show-content-on-error`
以便整体失败时仍能展开已执行的子节点。递归由数据驱动、逐层向下收敛（一个循环的轮次数据不含它
自身），执行详情是有限树因而必然终止；`details/index.vue` 与节点详情之间的循环 import 仅在渲染期
使用、不在模块求值期调用，属正常的组件递归引用。

## View 接入约定

- 所有画布路由页面均放在 `src/views/workflow/`，并以 `XxxWorkflowView.vue` 命名，例如
  `ApplicationWorkflowView.vue`。未来的智能体画布、知识库画布等都遵守此规则。
- View 在 `WorkflowCanvas` 外部组织页面头部的保存、发布、调试等页面级操作；添加组件属于画布操作，
  由 `WorkflowCanvas` 内的 `AddNode` 统一提供。
- 画布页面需要独立全屏展示时，由 `src/router/admin/workflow/` 配置不挂载业务 Layout 的路由；
  画布模块不处理路由。
- View 通过 Props 传入图数据，通过组件实例暴露的方法操作画布。接口接入后，加载、保存及错误
  处理仍由 View 或其所属业务层编排，不在节点和画布核心中直接发请求。
- View 向 `WorkflowCanvas` 传入 `workflowMode`；`WorkflowCanvas` 将它用于右上角添加组件菜单，并桥接给
  LogicFlow 节点内部的锚点菜单。

`WorkflowCanvas` 当前对外暴露的方法包括：

| 方法              | 用途                        |
| ----------------- | --------------------------- |
| `addNode`         | 在画布中心添加指定节点      |
| `getGraphData`    | 获取规范化后的图数据        |
| `renderGraphData` | 重建 LogicFlow 并渲染图数据 |
| `render`          | 使用现有实例重新渲染图数据  |
| `clearGraphData`  | 清空画布                    |
| `fitView`         | 调整画布到合适视口          |
| `validate`        | 执行节点校验                |
| `onmousedown`     | 启动节点拖拽或执行节点回调  |

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

## 当前迁移范围

- 已实现并注册：基本信息、开始、AI 对话、意图识别、问题优化、语音转文本、文本转语音、图片生成、
  图片理解、文生视频、图生视频、视频理解、知识库检索、判断器、指定回复、智能体、自定义工具和
  工具库工具、工具工作流、MCP、文档内容提取、多路召回和文档标签检索，以及参数提取、表单收集、
  变量赋值、变量聚合、变量拆分、循环、循环体、循环开始、Break、Continue、工具基本信息和工具开始节点。
- 知识库检索节点在入口维护检索范围、参数摘要和问题表单，参数设置按钮与弹窗统一封装在
  `component/SearchSetting.vue`，通过 `v-model` 接收检索参数，仅在校验通过并保存后深拷贝回写；
  节点入口统一维护关联数据，范围引用加入节点表单校验，问题引用保留独立有效性检查。知识库选择复用
  `SelectKnowledgeDialog`，保留相同 Embedding 模型约束；移除关联只清理明确取消的 ID，
  不丢弃全量关联中当前用户不可见的知识库。检索模式协议复用 `KNOWLEDGE_SEARCH_MODE`。
- `config/node-mapping.ts` 保留节点类型映射，以及基本信息和开始节点的默认数据集合。
- `NodeMenu` 使用 Element Plus Tabs 组织基础组件、工具和智能体；基础组件直接渲染 `node-menu/menu.ts` 返回的菜单分组，工具和智能体复用 Workspace 文件夹树加载可用资源。画布右上角的 `AddNode` 和节点锚点菜单均支持点击创建与拖拽到画布创建。
- `ApplicationWorkflowView` 已接入详情加载、默认工作流、手动与自动保存、发布以及未保存退出确认。
- `ToolWorkflowView` 已接入工具模式、工具专属默认节点、详情加载、手动保存以及未保存退出确认。
- 执行详情已覆盖：判断器、指定回复、开始/应用、问题优化、意图识别、文档内容提取、参数提取、变量赋值、
  变量拆分、变量聚合、工具/自定义工具、MCP、工具开始、工具工作流、循环开始/继续/退出、图片理解、
  视频理解、图片生成、文生视频、图生视频。其中开始/应用、问题优化、意图识别为单文件；图片理解与视频理解
  按 `application.vue`/`knowledge.vue` 拆包；多路召回等以 `ParagraphCard` 渲染段落的节点（知识库检索、
  多路召回、文档分段、知识库写入）与表单收集节点暂未迁移。文件类型图标复用 `@/utils/icon` 的
  `getFileIconUrl`。
- 工具工作流调试和发布、发布历史、模板中心、完整国际化、枚举补充和其他尚未迁入的节点组件后续再接入。

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
