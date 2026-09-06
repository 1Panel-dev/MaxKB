# utils 目录说明

`src/utils` 只存放大部分页面或多个业务模块都会使用的通用函数。只被个别页面、组件或业务
模块使用的函数，应保留在所属代码附近，不要提前提升为全局工具。

工具函数按照明确的业务领域或能力拆分文件，例如：

```text
src/utils/
├── UTILS_README.md       # utils 目录的放置、拆分、命名和注释规则
├── array.ts              # 跨页面复用的数组转换、筛选、去重等处理函数
├── clipboard.ts          # 剪贴板文本复制和成功反馈
├── file.ts               # 文件后缀识别、类型白名单校验和图标匹配
├── message.ts            # Element Plus 全局消息提示的统一封装
├── number.ts             # 跨页面复用的数字计算、转换和格式化函数
├── resource-context.ts   # 当前路由的资源范围和工作空间上下文判断
├── time.ts               # 跨页面复用的日期时间计算与格式化函数
├── use-responsive.ts     # 需要同步组件状态时使用的响应式屏幕判断
├── use-sortable.ts       # 列表排序、动态容器绑定和可选的独立数据写回
└── vnode.ts              # Vue 插槽 VNode 的可渲染内容判断
```

## 使用约定

- 每个工具文件顶部必须注明该文件负责的领域和用途。
- 每个导出的函数必须使用 JSDoc 注明用途；参数、返回值或边界行为不直观时，应一并说明。
- 文件内部含义明确且只服务于单个导出函数的局部辅助函数，不需要重复添加无信息量的注释。
- 文件名应准确表达所属领域或能力，不使用 `common.ts`、`helpers.ts` 等含义模糊的名称。
- 变量和函数名称应体现具体用途，避免脱离上下文的简称。
- 不要创建收集无关函数的通用文件。
- 不要为了统一导出而新增只做二次转发的 `index.ts`，使用方从具体文件直接导入。
- 依赖 Vue 响应式状态或生命周期的通用组合式函数可以使用 `use-*.ts` 命名。
- 仅改变样式的响应式需求优先使用 Tailwind；只有需要改变组件状态时才使用响应式工具函数。

## 拖拽排序

同一列表内的拖拽排序统一使用 `use-sortable.ts` 的 `useSortable`，底层为 VueDraggablePlus；
不要在业务代码中直接初始化 SortableJS 或重复实现 DOM 还原和数组移动。目录树继续使用
`@he-tree/vue` 的树形拖拽协议。

```ts
import { ref } from 'vue'
import { useSortable } from '@/utils/use-sortable'

const rowContainer = ref<HTMLElement>()
const taskRows = ref([
  { id: 'a', name: '任务 A' },
  { id: 'b', name: '任务 B' },
])
const sortDisabled = ref(false)

useSortable(rowContainer, taskRows, () => ({
  handle: '.task-drag-handle',
  draggable: '> .task-row',
  disabled: sortDisabled.value,
  onReorder: ({ oldIndex, newIndex, data }) => {
    // data 已经完成排序，可在这里保存新顺序，不要再次 splice。
  },
}))
```

容器的直属可拖动元素应与数组逐项对应，Vue 渲染使用稳定业务 ID 作为 `key`；添加按钮等
操作元素放在行容器之外。容器参数支持模板 Ref 或返回 HTMLElement 的 getter，适配 `v-if`
和表格内部 `tbody`；组件更新时检查是否需要重新绑定，卸载时自动销毁。外部代码重建内部 DOM
时可调用返回的 `refresh()`，也提供 `pause()`、`resume()`；响应式禁用优先通过 `disabled` 配置。
配置可传对象、Ref 或 getter，默认动画 `150ms`，拖拽占位使用 `opacity-40`。

普通 Vue 数组排序保留行对象引用；LogicFlow/MobX 可观察树的数据需要开启
`cloneOnUpdate: true`，或在业务 computed setter 中使用 Lodash `cloneDeep` 后写回。
库的 `clone` 选项不等同于普通排序写回时深拷贝整个数组。`onReorder` 只在实际顺序变化时触发，
返回 `{ oldIndex, newIndex, data }`，索引基于当前列表，从 `0` 开始。

MkTable、MkFormList 的排序优先使用其公开属性；普通列表再直接接入该工具。本工具只处理
同一列表排序，不开放跨列表 `group` 和绕过默认同步的 `customUpdate`；特殊业务置换规则应另行
评估，不直接套用普通移动语义。

## 资源上下文

`application`、`knowledge`、`model`、`tool` 是使用资源上下文的四类特殊资源。工作空间 id 和这
四类资源的当前路由范围统一通过 `resource-context.ts` 读取。Workspace API、权限等非组件代码使用
`getWorkspaceId()` 获取当前工作空间；页面和组件使用 `isWorkspaceResource()`、
`isSystemResource()`、`isSystemSharedResource()` 区分 Workspace、System 资源管理和 System 共享
资源。资源范围只读取路由 `meta.resourceScope`，不要根据 path 或路由名称重复判断，也不要把这些
判断扩展到普通 System 页面。

## VNode 插槽内容判断

组件需要根据插槽是否存在真实渲染内容决定是否显示触发器或操作区时，使用
`vnode.ts` 导出的 `hasRenderableSlotContent()`。该函数会递归检查 Fragment，并忽略空白文本、
注释和空 Fragment；不要仅通过 `$slots.xxx` 判断带 `v-if` 的条件插槽是否有可见内容。

## 消息提示

轻量反馈按需从 `utils/message.ts` 导入 `MsgSuccess`、`MsgInfo`、`MsgWarning` 或 `MsgError`，
不要在业务代码和请求层直接调用 `ElMessage`。
消息默认显示关闭按钮并在 `3000ms` 后关闭；特殊场景通过第二个参数覆盖 Element Plus 消息
选项。确认操作统一按需导入 `MsgConfirm(title, message, options?)`，默认提供确认、取消按钮和
warning 类型；输入和普通警告弹窗继续直接使用 `ElMessageBox`。

```ts
/** 提供跨页面复用的数组处理函数。 */

/** 根据指定字段对数组进行去重。 */
export function uniqueBy() {
  // ...
}
```
