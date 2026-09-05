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
├── component/          # 画布内可复用的控制和搜索组件
├── config/             # 节点数据、映射、常量及预留的本地化配置
├── core/               # 稳定的画布内核与所有节点共用的基础能力
│   ├── edge/           # 普通边、循环边及边删除按钮
│   └── node-container/ # 节点容器、锚点按钮及私有的条件、操作下拉组件
├── icons/              # 节点图标及图标解析工具
├── node-menu/          # 基础组件、工具和智能体节点菜单及其菜单配置
├── nodes/              # 已迁入节点的注册文件和 Vue 实现
├── plugins/            # 仅供画布使用的 LogicFlow 插件
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
同一节点的多个 `createAnchorGuard()` 实例共享浮层状态，最后一个浮层关闭或卸载后才恢复
节点原本的 `hittable` 状态。

锚点按钮与 `el-tooltip` 集中在 `core/node-container/NodeAnchor.vue`。`workflow-node.ts` 负责
锚点坐标、连接状态，并将 LogicFlow 组件的挂载、Props 更新和卸载同步到现有 Vue Teleport
容器；`teleport.connect()` 的可选第五个参数用于传入组件 Props。节点容器
保留菜单开关与外部点击关闭逻辑，不维护锚点 tooltip 的状态或虚拟触发器。

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

### `nodes/`

每个已实现节点使用一个目录，目录中包含 LogicFlow 注册文件 `index.ts` 和节点视图
`index.vue`。节点注册由 `index.vue` 中的 `import.meta.glob('./nodes/**/index.ts')` 自动收集，
不要再维护一份逐项导入列表。

工作流中的单模型选择统一使用 `ModelSelect` 的 `canEditParams` 和 `v-model:model-params`，
由公共组件维护参数按钮、弹窗和切换模型后的默认值，节点不再单独创建参数弹窗或请求默认值。
AI 对话及基本信息的语音子组件通过局部更新事件回写字段，父节点合并更新，避免模型 ID 与参数
连续更新时被旧 Props 覆盖。语音输入使用 `stt_model_params_setting`，语音播放使用
`tts_model_params_setting`，其他模型节点使用各自已有的参数字段。
`ApplicationWorkflowView` 和 `ToolWorkflowView` 提供 `getModelParamsForm` 注入接口，画布中的
Vue Teleport 节点继承页面上下文；画布核心不负责模型参数接口选择。
智能体页面将详情加载或保存成功返回的配置通过 `defaultModelSettings` Props 传给画布。
`WorkflowNodeModel.getDefaultModelConfig(type)` 通过画布的配置读取函数获取对应模型，不使用
默认配置的 `provide/inject`，也不写入节点持久化数据。AI 对话和意图识别节点在默认来源下读取保存后的
`LLM` 模型 ID 和参数，使用禁用且隐藏参数按钮的 `ModelSelect` 展示；自定义来源继续编辑
节点自身配置，引用来源使用 `NodeCascader`。默认配置只用于解析当前使用的模型，不覆盖节点
保存的自定义配置；两个节点各自在节点内维护模型设置，并按当前来源检查实际模型或引用变量。

节点自身的表单、状态和专属校验留在节点目录；多个节点共享且属于画布基础协议的能力才上移到
`core`。节点应复用 `core/node-container/index.vue`，需要选择上游节点字段时复用
`core/NodeCascader.vue`。

包含多块独立配置的复杂节点，在节点目录的 `component/` 下按业务能力建立子目录。子组件负责
各自的表格、表单和弹窗交互，通过 Props 和 Emits 传递数据；节点 `index.vue` 负责统一写回节点
属性、执行节点级校验和发送画布事件，不直接堆叠各业务块的页面逻辑。

AI 对话节点的系统提示词和用户提示词统一使用全局 `MdEditorMagnify`，不再维护本地放大编辑器。
提示词设置保留 AI 生成入口、字段回写和节点滚轮处理；用户提示词在编辑器失焦或放大编辑确认后
显式触发表单校验。

固定字段写入统一使用直接赋值，例如 `model.properties.node_data = value`、
`model.validate = validate`，不使用 Lodash `set`。写入嵌套字段前保留必要的父对象初始化；
Vue `computed` 的 `set` 和原生 `Map.set()` 按各自 API 正常使用。

默认值补齐和旧数据兼容在节点初始化阶段执行，`computed` getter 只读取数据，不修改节点属性、
调用会修改数据的归一化方法，或通过 Lodash、类型断言绕过检查。容器私有下拉组件通过类型化的
更新事件通知 `NodeContainer` 写回条件、禁用状态和节点名称，不直接修改 Props 中的字段。

## View 接入约定

- 所有画布路由页面均放在 `src/views/workflow/`，并以 `XxxWorkflowView.vue` 命名，例如
  `ApplicationWorkflowView.vue`。未来的智能体画布、知识库画布等都遵守此规则。
- View 在 `MkWorkflow` 外部组织页面头部的保存、发布、调试等页面级操作；添加组件属于画布操作，
  由 `MkWorkflow` 内的 `AddNode` 统一提供。
- 画布页面需要独立全屏展示时，由 `src/router/admin/workflow/` 配置不挂载业务 Layout 的路由；
  画布模块不处理路由。
- View 通过 Props 传入图数据，通过组件实例暴露的方法操作画布。接口接入后，加载、保存及错误
  处理仍由 View 或其所属业务层编排，不在节点和画布核心中直接发请求。
- View 向 `MkWorkflow` 传入 `workflowMode`；`MkWorkflow` 将它用于右上角添加组件菜单，并桥接给
  LogicFlow 节点内部的锚点菜单。

`MkWorkflow` 当前对外暴露的方法包括：

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
6. 确认节点能被自动注册、从菜单添加、正确连线、校验并导出图数据。

节点协议值统一使用 `WorkflowNodeType` 等枚举或画布常量，不在判断和映射中重复书写
`ai-chat-node`、`tool-custom-node` 等字符串字面量。

## 当前迁移范围

- 已实现并注册：基本信息、开始、AI 对话、意图识别、文本转语音、知识库检索、判断器、指定回复、智能体、
  自定义工具和工具库工具。
- 知识库检索节点在 `component/search-scope/` 和 `component/search-setting/` 中分别维护检索范围
  与参数配置，节点入口统一写回数据并独立校验范围引用和问题引用。知识库选择复用
  `KnowledgeSelectionDialog`，保留相同 Embedding 模型约束；移除关联只清理明确取消的 ID，
  不丢弃全量关联中当前用户不可见的知识库。检索模式协议复用 `KNOWLEDGE_SEARCH_MODE`。
- `config/node-mapping.ts` 保留节点类型映射，以及基本信息和开始节点的默认数据集合。
- `NodeMenu` 使用 Element Plus Tabs 组织基础组件、工具和智能体；基础组件直接渲染 `node-menu/menu.ts` 返回的菜单分组，工具和智能体复用 Workspace 文件夹树加载可用资源。画布右上角的 `AddNode` 和节点锚点菜单均支持点击创建与拖拽到画布创建。
- `ApplicationWorkflowView` 已接入详情加载、默认工作流、手动与自动保存、发布以及未保存退出确认。
- `ToolWorkflowView` 已接入工具模式、工具专属默认节点、详情加载、手动保存以及未保存退出确认。
- 工具工作流调试和发布、发布历史、模板中心、完整国际化、枚举补充和其他尚未迁入的节点组件后续再接入。

## 检查

修改后至少运行与改动范围相符的检查：

```bash
npm run type-check
npm run lint
git diff --check
```

若当前迁移中的预留文件仍存在已知类型错误，应在交付说明中明确区分，不要通过改变现有画布业务
逻辑来绕过。
