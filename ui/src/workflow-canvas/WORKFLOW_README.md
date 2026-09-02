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
├── component/          # 画布内可复用的控制、菜单和搜索组件
├── config/             # 节点数据、菜单、映射、常量及预留的本地化配置
├── core/               # 稳定的画布内核与所有节点共用的基础能力
├── icons/              # 节点图标及图标解析工具
├── nodes/              # 已迁入节点的注册文件和 Vue 实现
├── plugins/            # 仅供画布使用的 LogicFlow 插件
├── index.vue           # 画布入口组件 WorkflowCanvas
├── style.scss          # 画布内 LogicFlow 全局样式覆盖
├── types.ts            # 画布协议类型和枚举
└── README.md           # 本文档
```

### `core/`

`core` 是配置完成后应保持稳定的基础层。`NodeContainer.vue` 和 `NodeCascader.vue` 是节点的
通用结构与交互能力，属于核心代码；连线、快捷键、公共校验、Teleport 和节点公共工具也放在
这里。只有某项行为是全部或大多数节点都必须遵守的画布规则时，才修改 `core`。新增普通节点
不应要求调整核心层。

节点内需要跟随画布缩放的浮层应保留 `teleported="false"`。如果浮层可能与后绘制的 SVG 锚点
重叠，使用 `core/utils.ts` 的 `createAnchorGuard()`，通过唯一 key 同步各浮层的
`visible-change` 状态，并在节点组件卸载时调用 `reset()`；不要通过 Teleport 到 `body` 或增加
`z-index` 绕过画布的缩放和 SVG 绘制顺序。

### `config/`

`config` 是随业务持续维护的配置层，增加、删除或调整节点时通常会更新：

- `node-data.ts`：节点的静态定义和默认属性，只存放数据。
- `menu.ts`：不同画布模式下的菜单分组和可选节点。
- `node-mapping.ts`：节点类型到配置数据的映射、模式匹配和默认节点集合。
- `constants.ts`：仅供工作流画布使用的稳定常量。
- `locale.ts`：预留的节点文案本地化配置；国际化接入前不参与当前逻辑。

配置数据中的函数应提取到对应职责文件，不把行为逻辑混入 `node-data.ts`。当前尚未接入国际化
的文案直接使用中文，不从 `@/locales` 引入 `t`。

### `nodes/`

每个已实现节点使用一个目录，目录中包含 LogicFlow 注册文件 `index.ts` 和节点视图
`index.vue`。节点注册由 `index.vue` 中的 `import.meta.glob('./nodes/**/index.ts')` 自动收集，
不要再维护一份逐项导入列表。

节点自身的表单、状态和专属校验留在节点目录；多个节点共享且属于画布基础协议的能力才上移到
`core`。节点应复用 `core/NodeContainer.vue`，需要选择上游节点字段时复用
`core/NodeCascader.vue`。

## View 接入约定

- 所有画布路由页面均放在 `src/views/workflow/`，并以 `XxxWorkflowView.vue` 命名，例如
  `ApplicationWorkflowView.vue`。未来的智能体画布、知识库画布等都遵守此规则。
- View 在 `MkWorkflow` 外部组织页面头部和页面级操作。添加组件、保存、发布、调试等按钮不能
  放进 `workflow-canvas/index.vue`。
- 画布页面需要独立全屏展示时，由 `src/router/admin/workflow/` 配置不挂载业务 Layout 的路由；
  画布模块不处理路由。
- View 通过 Props 传入图数据，通过组件实例暴露的方法操作画布。接口接入后，加载、保存及错误
  处理仍由 View 或其所属业务层编排，不在节点和画布核心中直接发请求。

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
4. 在 `config/menu.ts` 中加入适用画布模式的菜单分组。
5. 在 `nodes/<node-type>/` 中实现注册文件和节点视图，并按需增加 `icons/` 图标。
6. 确认节点能被自动注册、从菜单添加、正确连线、校验并导出图数据。

节点协议值统一使用 `WorkflowNodeType` 等枚举或画布常量，不在判断和映射中重复书写
`ai-chat-node`、`tool-node` 等字符串字面量。

## 当前迁移范围

- 已实现并注册：基本信息、开始、AI 对话、意图识别、文本转语音、判断器、指定回复。
- `config/node-mapping.ts` 保留节点类型映射，以及基本信息和开始节点的默认数据集合。
- `NodeMenu` 根据当前工作流模式直接渲染 `config/menu.ts` 返回的菜单分组；页面“添加组件”和节点锚点菜单均支持点击创建与拖拽到画布创建。
- `ApplicationWorkflowView` 已接入详情加载、默认工作流、手动与自动保存、发布以及未保存退出确认。
- 调试、发布历史、模板中心、完整国际化、枚举补充和其他尚未迁入的节点组件后续再接入。

## 检查

修改后至少运行与改动范围相符的检查：

```bash
npm run type-check
npm run lint
git diff --check
```

若当前迁移中的预留文件仍存在已知类型错误，应在交付说明中明确区分，不要通过改变现有画布业务
逻辑来绕过。
