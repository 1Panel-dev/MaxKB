# 公共组件使用约定

本文档维护公共 UI 与业务组件的选型、接口和使用约束。工作流专属规则见
[WORKFLOW_README.md](../workflow-canvas/WORKFLOW_README.md)，样式规则见
[STYLE_README.md](../styles/STYLE_README.md)。

## 选型与目录

依次检查全局 Mk 组件、业务组件、手动导入的共享 UI，最后使用 Element Plus；已有同类封装时
直接复用，例如 `MkDialog`、`MkDrawer`、`MkDropdown`、`MkIcon`、`MkTable`。先用现有 Props、
事件、插槽和样式适配，无法满足必要行为时再新增组件；无明确需求不引入新 UI 库。

| 位置                                   | 用途                                   | 使用方式         |
| -------------------------------------- | -------------------------------------- | ---------------- |
| `global/`                              | 高频、稳定的基础组件                   | Vue 模板自动注册 |
| `business/<component-name>/`           | 跨页面复用的固定业务组件，不加 Mk 前缀 | 显式导入         |
| `<component-name>/`                    | 尚未纳入全局的共享组合 UI              | 显式导入         |
| `views/<feature>/`、`workflow-canvas/` | 功能或画布专属组件                     | 留在所属功能内   |

Vite 仅扫描 `src/components/global`，当前没有 `globsExclude` 配置；其中的内部组件文件也在
扫描范围内，但使用方仍应通过父组件的插槽使用 `Action`、`ActionDropdown`、`Header`、`Footer`，
不直接依赖内部组件。自动注册仅适用于模板，脚本类型、常量及 Element Plus 图标需显式导入。
`src/components.d.ts` 由 Vite 开发服务或构建生成，不手动修改。

Element Plus 已在 Admin、Chat 入口注册。使用前先检查原生 API，避免重复实现已有能力。

手动组件从具体入口导入；动态表单通过自己的公开入口导入：

```ts
import SelectModel from '@/components/business/select-model/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import { MkDynamicsForm, MkDynamicsFormConstructor } from '@/components/mk-dynamics-form'
```

## 通用规则

- 目录使用 kebab-case，默认入口为 `index.vue`，通过 `defineOptions` 声明 PascalCase 多单词组件名。
  Markdown 编辑器、CodeMirror 和 Logo 按下文的专用入口使用。
- Props、Emits、Slots 保持类型化。类型归属遵循 [API_README.md](../api/API_README.md)，
  API 与组件共用类型从 `@/api/types` 导入。
- 样式默认 `scoped`；组件专属样式留在组件目录，应用级规则放在 `src/styles`。
- 不编写 `aria-label`；按钮前添加简短中文用途注释，已有注释不重复添加。
- `global` 不创建仅用于二次导出的聚合入口。
- `el-input-number` 设置 `controls-position="right"` 时，同时设置 `align="left"`。
- Tooltip、Popover、Popconfirm、Dropdown 的触发插槽只保留一个有实际布局盒的根节点；
  多个元素用 `span` 或 `div` 包裹，不使用 `template` 或 `display: contents` 代替。
- 业务弹窗 `open()` 先重置再回填，关闭动画结束的 `closed` 统一清理表单、校验和临时状态。
  父级负责校验或请求时，子组件提交数据后由父级成功调用 `close()`，失败保持打开。
- 仅登录表单支持回车提交；其他业务表单使用 `@submit.prevent`，保存、添加由按钮触发。
  自定义 `submit` 事件不等于原生表单提交。

## 全局 UI 组件

### MdEditor、MdEditorMagnify、MdPreview

位于 `global/markdown-editor/`，底层 Props、事件通过 `$attrs` 透传，语言来自 User Store。

- `MdEditor` 默认关闭 Prettier，提供 `defFooters` 插槽。
- `MdEditorMagnify` 接收字符串 `v-model` 和 `title`，弹窗确认后回写并触发 `submitDialog`；
  关闭丢弃草稿。通过 `useFormItem()` 触发外层 `change` / `blur` 校验，
  `:validate-event="false"` 可关闭；这一能力不适用于普通 `MdEditor` 或 `MdPreview`。
- `MdPreview` 默认关闭代码折叠，用 `model-value` 传入只读内容。

Admin、Chat 入口调用 `configureMarkdownEditor()` 配置本地高亮、KaTeX、Mermaid、ECharts、
图片裁剪、全屏和 Prettier，避免运行时加载 CDN；图标随依赖打包，不维护旧图标脚本。
共享样式在 `md-editor.scss`，由 `config.ts` 引入；编辑器覆盖限定在 `mk-markdown-editor`，
挂载到 body 的上标浮层使用独立的 `markdown-sup-popover`。
编辑边框复用 Element Plus Input 的悬浮、焦点变量，只读与禁用不触发；滚动条保留编辑器原有
滚动节点，使用 Element Plus Scrollbar 变量和 6px 宽度，不额外隐藏轨道。

### MkCollapse

`v-model:expanded` 可控制展开状态；未绑定时沿用 `defaultExpanded` 的内部状态。
`destroyOnCollapse` 默认 `true`，设为 `false` 时折叠只隐藏内容，适用于需要保留参数表单及校验的场景。

标题折叠区，`title` 或 `label` 插槽提供标题，默认插槽提供内容。
`defaultExpanded` 默认 `true`，仅设置初始状态；点击标题内部切换，当前不提供展开状态事件。
`indicatorPosition` 默认 `before`，可设为 `after`；`triggerClass`、`triggerStyle` 调整触发区。
内容使用 `v-if`，收起会卸载内部组件。

### MkEmpty

基于 `el-empty`。`type="default"` 显示“暂无数据”，搜索无匹配使用 `type="search"`。
`description`、`image`、`image-size` 可覆盖默认值，其他属性及默认、`image`、`description` 插槽透传。

### MkDialog

布尔 `v-model` 控制显示，默认宽度 `600`、挂载到 body、显示关闭按钮、关闭后销毁，
禁止点击遮罩和 Escape 关闭。其余 Dialog 属性、事件通过 `$attrs` 透传。
提供默认、`header`、`subtitle`、`footer` 插槽；`subtitle` 不替代标题，`header` 透出原生关闭与标题参数。
内容由 `el-scrollbar` 包裹，容器为 `px-6 dialog-content`，通过 `contentClass` 调整；
最大高度由全局 Dialog 样式控制。

外壳首次打开才挂载，默认在 `closed` 后卸载。`:destroy-on-close="false"` 可保留首次打开后的实例。
调用方不要用 `v-if="visible"` 提前卸载，避免跳过关闭动画和清理。

### MkDrawer

布尔 `v-model` 控制显示，默认宽度 `700`、挂载到 body、显示关闭按钮、关闭后销毁内容，
禁止点击遮罩和 Escape 关闭；原生属性、事件通过 `$attrs` 覆盖或透传。
提供默认、`header`、`footer` 插槽，内容使用 `el-scrollbar` 和 `p-6`，可用 `contentClass` 调整。
全高内容可传 `content-class="h-full p-0"` 并复用 `MkViewLayout`。
Drawer 没有 `MkDialog` 的外壳挂载控制；需要按需挂载时，由业务在 `closed` 后卸载。

### MkComplexSearch

`fields` 使用 `OptionItem<string>`，附加 `multiple`、`remoteMethod`。
有 `options` 时渲染选择器，否则渲染文本输入；`remoteMethod(query)` 由调用方更新选项，组件管理加载状态。
`change` 返回 `{ [field]: value }`，多选返回数组；清空返回 `undefined`，切换字段仅在原条件非空时通知清空。

### MkDropdown、MkDropdownMenu、MkDropdownItem

`MkDropdown` 默认 `persistent: false`，透传 Dropdown 属性、事件，公开 `handleOpen()`、`handleClose()`。
`dropdown` 插槽内组合 `MkDropdownMenu`、`MkDropdownItem`，不在业务中重复组装底层组件。
菜单项通过 `icon` Prop 传 Element Plus 图标，或使用 `icon` 插槽；`selectable` 预留勾选位，
`selected` 控制选中。触发器遵循单根节点规则。

### MkViewLayout

满高页面布局，`loading` 覆盖整个根节点。`title` 默认读取路由标题，传空字符串隐藏；
提供 `aside` 插槽时才渲染侧栏，`collapsible` 开启内部折叠，`top` 放左右区域上方的内容。

- `aside` 插槽提供 `title`、`Header`；默认插槽提供 `title`、`Header`、`Footer`。
- 未显式渲染 `Header` 时自动显示标题；`Header`、`Footer` 固定，正文由内置 `el-scrollbar` 滚动。
  不重复包裹整个主内容区，局部树、Tabs 等可独立滚动。
- `scroll` 返回 `{ scrollTop, scrollLeft }`；公开 `setScrollTop()`、`getScrollContainer()`。
- 主区水平留白为 24px，滚动容器抵消外层留白后补回内容间距，滚动条贴右边缘。
- `Footer` 无批量插槽时显示普通底栏；提供 `footer-batch-actions` 后复用批量底栏，
  用 `v-model:batch-selection` 绑定唯一值数组，`batch-values` 传当前列表全部值。
  插槽提供 `batchSelection`；取消清空选择并触发 `batch-cancel`。

```vue
<MkViewLayout :loading="loading">
  <template #default="{ title, Header, Footer }">
    <component :is="Header"><h4>{{ title }}</h4></component>
    <ResourceList />
    <component :is="Footer" v-if="batchMode"
      v-model:batch-selection="selectedIds" :batch-values="resourceIds"
      @batch-cancel="batchMode = false">
      <template #footer-batch-actions="{ batchSelection }">
        <!-- 删除选中资源 -->
        <el-button :disabled="!batchSelection.length" @click="removeResources(batchSelection)">删除</el-button>
      </template>
    </component>
  </template>
</MkViewLayout>
```

### MkIcon

`name` 接收完整 SVG Symbol ID，`icon` 接收显式导入的 Element Plus 图标，二选一；
均未提供时显示 `icon-404`。`size` 默认 16，支持 `color`；`gradient` 仅用于 Symbol 主题渐变。
不直接使用 Unicode、Font Class 或裸 `<svg><use>`。`src/assets/iconfont.js` 仅整体替换，
Symbol ID 变化时同步引用。

资源图标使用 `ApplicationIcon`、`KnowledgeIcon`、`ToolIcon`、`TriggerIcon`。
智能体无自定义图标时回退默认图标；知识库兼容数字和字符串类型，通过 `KNOWLEDGE_TYPE_MAP`
映射，未知类型回退默认。触发器 `SCHEDULED` 使用定时图标，其他类型使用事件图标。

### MkInfiniteScroll

分页列表的滚动触底加载组件，使用 `IntersectionObserver` 监听组件所在滚动区域的底部，不依赖
Element Plus 的 `v-infinite-scroll`。组件通过 `v-model` 管理已经加载的列表数据，通过 `load`
传入按页请求方法，并在内部管理页码、首次加载、数据追加、加载状态、结束状态和过期请求。请求
方法接收 `{ currentPage, pageSize }`，返回包含 `records`、`current`、`size` 和 `total` 的分页结果。
默认每页加载 30 条，可通过 `pageSize` 修改。组件挂载后自动加载第一页，之后只在底部哨兵随
用户滚动进入可视区域时加载下一页。查询条件变化时通过组件暴露的 `reset()` 重新加载。
首次加载或 `reset()` 请求第一页时，组件只显示加载状态；第一页完成且列表为空后才渲染 `empty`
插槽，避免请求过程中短暂显示空状态。已有数据时继续渲染默认插槽，并在触底请求期间保留列表。

### MkListItem

统一列表行、选中态及悬浮操作区。仅自定义内容时传 `active` 并监听 `click` 即可。
数据驱动时传 `row`，`labelField` 默认 `name`，`index` 默认 0；默认插槽提供 `{ row, index, active }`。
`action`、`action-dropdown` 提供 `{ row, index }`，有可渲染下拉项时优先下拉，否则显示普通操作。
下拉插槽直接放 `MkDropdownItem`，组件提供 More 触发器并隔离行点击；空菜单不显示入口。

### MkSearchInput

默认搜索图标、placeholder“搜索”，固定支持清空。`v-model`、其他 Input 属性和事件透传；
`prefix` 可覆盖图标，`prepend`、`append`、`suffix` 插槽可用。

### MkSlider

全局滑块组件，组合 `el-slider` 和 `el-input-number`，默认显示数值输入框，控制按钮固定在
右侧，输入内容左对齐。输入框的 `controls` 固定为 `true`，始终显示加减按钮；
`show-input-controls` 不作为组件配置使用，调用方无需传入，传入也不会改变按钮显隐。
其余 Element Plus Slider Props 和 `update:modelValue`、`input`、`change` 事件保持可用；
`class`、`style` 作用于外层布局。通过 `:show-input="false"` 隐藏输入框。
`range` 或 `step="mark"` 模式不显示
单值输入框；垂直模式下输入框位于滑块下方。输入框与滑块共用范围、步长、禁用状态，
输入框清空并提交后回退到最小值，表单变更校验由滑块统一触发。

### MkStatusLabel

`active` 控制布尔状态，默认“已启用 / 已禁用”；用 `activeText`、`inactiveText` 修改文案。

### MkTable

标准表格组件，组合 Element Plus Table、可选分页、列宽拖拽和批量选择操作栏。`data` 和
`paginationConfig` 由组件接收，其余 Table 属性和事件通过 `$attrs` 传入，列继续使用
`el-table-column`。

`paginationConfig` 包含 `currentPage`、`pageSize`、`total` 和可选 `pageSizes`；不传则隐藏分页器，
`pageSizes` 默认 `[10, 20, 50, 100]`。

使用 `v-model:pagination-config` 接收页码和每页数量变化，也可以监听 `current-change` 和
`size-change`。切换每页数量时，组件会同时将 `currentPage` 重置为 `1`，页面只需在
`size-change` 中重新加载数据，不要重复修改页码。

`maxTableHeight` 表示窗口中除表格外需要扣除的高度，默认为 `250`；组件会在窗口尺寸变化时
重新计算 `max-height`。传入 `resizable` 后启用列宽拖拽，并隐藏为拖拽借用的原生边框视觉。
`resizable` 采用白名单式启用：只有需求明确指定的页面级表格才能开启；未明确指定的表格，以及
Dialog、Drawer、Popover、嵌套区域等其他大、小表格均禁止开启。

传入 `size="small"` 时，组件会为内部 `el-table` 添加 `small` class；组件仅提供该样式钩子，
不内置对应样式。

行拖拽排序通过 `sortable` 按需开启，开启后可从整行任意位置开始拖动，不添加独立的排序图标列。
使用 `v-model:data` 接收新顺序；也可使用 `:data` 和 `@update:data` 自行写回。
`row-key` 支持字段路径或函数，默认为 `id`，排序要求每行键值唯一且
为字符串或数字。

`sort-change` 在实际顺序变化后返回 `{ oldIndex, newIndex, data }`，不要在回调里再次移动数组。
分页场景只调整当前传入页的数据，索引从 `0` 开始；跨页位置、接口保存和失败回滚由业务负责。
有活动列排序、表头筛选、展开行或树形数据时暂停拖拽，避免显示行与数据索引不一致。
虚拟表格、跨页和跨列表拖拽不属于该接口。排序工具不会深拷贝普通表格的行对象；工作流使用方应在
数据写回边界自行 `cloneDeep`，保持 LogicFlow 的可观察树约束。

表头需要多选筛选时使用 `MkTableFilter`。`label` 设置表头文案，`options` 接收
`OptionItem<string>[]`，必填 `v-model` 绑定已选字符串数组；打开时复制为草稿，确认或重置后
写回并触发 `change`。过长的选项文案会显示省略号，悬停时可查看完整文案。

表格操作列需要 More 菜单时使用 `MkTableMoreDropdown`。组件统一提供点击型、右下定位的 More
按钮以及 `MkDropdownMenu`，默认插槽中直接放置 `MkDropdownItem`；插槽为空，或其中的条件菜单项
均未渲染时，不显示 More 触发器。其他 Dropdown 属性和事件通过 `$attrs` 传入，菜单容器样式通过
`menu-class` 设置。

包含 `type="selection"` 的选择列时，选择数据会显示页面底部操作栏。批量按钮放入
`footer-batch-actions` 插槽，当前选择通过 `selection-change` 返回。组件暴露 `tableRef` 和
`clearSelection()`。操作栏与 `MkViewLayout` 复用 `LayoutBatchFooter`，统一全选、半选、数量和
取消行为；它在主内容滚动区域内吸附于页面底部，不随表格内容滚出可视区域。

### MkTagGroup

始终渲染首个标签，更多标签折叠为 `+N`，悬浮展示剩余内容。
`tags` 默认空数组，空数组仍会渲染空标签；无需占位时由调用方控制显隐。
`popoverDisabled` 只禁用浮层，不改变折叠结果。
`type` 沿用 Element Plus Tag 的类型，默认 `info`，仅配置首个标签；`+N` 和浮层内标签保持 `info`。
`size` 沿用 Element Plus Tag 的尺寸类型，统一作用于首个标签、`+N` 和浮层内标签；
传入 `size="small"` 显示小尺寸标签，不传时沿用 Element Plus 的默认尺寸继承行为。

### MkSourceCard

等高资源卡片，`title` 必填，`nick_name`、`create_time` 提供创建信息；
`icon`、`title`（透出 `{ title }`）、`subtitle`、`tag` 插槽可覆盖头部，默认插槽放详情。
`footer` 提供常驻内容及 `Action`、`ActionDropdown`：前者是悬浮/焦点操作容器，后者包裹 More 菜单，
内部直接放 `MkDropdownItem`，空菜单隐藏入口。仅需要开关或按钮时使用 `Action` 即可。
无有效 `footer` 内容时不渲染底栏，默认内容区不额外保留底部间距；有底栏时保留 16px 分隔。
`ActionDropdown` 固定 `persistent`，其管理的业务浮层应打开时挂载、`closed` 后卸载。

`selectable` 开启卡片选择，`selected` Prop 控制选中，`selected` 事件返回新状态。
点击卡片或复选框切换，`Action` 在选择模式下不渲染；页面负责选择集合、批量操作和特殊内容显隐。
`disabled` 只控制指针和阴影，不阻止点击或选择；需要禁用交互时由使用方处理。

```vue
<MkSourceCard title="工作流工具" :selectable="batchMode" :selected="selected" @selected="selected = $event">
  <template #footer="{ Action, ActionDropdown }">
    <MkStatusLabel :active="enabled" />
    <component :is="Action">
      <component :is="ActionDropdown">
        <MkDropdownItem @click="editTool">编辑</MkDropdownItem>
      </component>
    </component>
  </template>
</MkSourceCard>
```

### MkFormList

用于多个业务字段组成的动态表单行，负责重复行布局、添加、删除和可选排序，不管理业务字段、校验规则或
选项请求。通过 `v-model` 传入行数据，`defaultItem` 创建新行，`minRows` 默认值为 `1`，控制删除时保留的最小行数；
允许删除到空列表时传入 `:min-rows="0"`。组件不会自动补齐初始行。默认插槽
提供 `item`、`index`，业务组件在插槽中继续声明
`el-form-item`、字段路径和校验规则。

`addText` 设置添加按钮文案，`showAddButton` 默认为 `true`；添加入口由业务布局单独提供时传入
`:show-add-button="false"`。`firstRowHasLabel` 默认为 `true`：第一行删除按钮使用 `mt-8`，后续行
使用 `mt-0.5`；并列表单项没有 label 时传入 `:firstRowHasLabel="false"`。删除成功后通过
`remove(item, index)` 返回被删除的行数据和原索引，业务组件可处理关联状态，不需要再次修改列表。
增删时使用 Lodash `cloneDeep` 回写独立的行数据，新增行也独立克隆 `defaultItem`，避免共享嵌套
引用及重复挂载 LogicFlow 的 MobX 可观察对象。调用方应使用业务 ID 识别行，不依赖对象引用保持不变。

表单行排序通过 `sortable` 开启，同时必须提供稳定且唯一的 `item-key`（字段名或取键函数）。
组件自带拖拽手柄，添加按钮位于排序容器之外，不需要业务再包拖拽指令或放置手柄。
不足两行或键值无效时禁用拖拽。排序与增删一样深拷贝写回，
`sort-change` 返回 `{ oldIndex, newIndex, data }`。校验规则和字段路径继续由默认插槽提供。

新行包含业务 ID 时，`default-item` 应传工厂函数，在每次点击添加时生成新 ID；普通无 ID 数据
仍可传默认对象。

## 手动导入的共享 UI

### MkFilterableDropdown

带搜索过滤和滚动列表的下拉选择。组件不限制选项字段，默认使用 `label` 作为展示和搜索字段、
`value` 作为唯一值；数据结构不同时通过 `props.label` 和 `props.value` 映射，使用方式与
`MkSearchList` 一致。原始选项类型会贯穿 `options`、作用域插槽和 `select` 事件。
`emptyText` 默认为“暂无匹配结果”。默认插槽接收 `selectedOption` 和 `text`，`option` 插槽接收
当前原始选项；选择后先更新 `v-model`，再通过 `select` 返回未经转换的原始选项。

### MkTagsEdit

手动导入 `@/components/mk-tags-edit/index.vue`，通过必填的 `string[]` 类型 `v-model`
编辑标签。可选 `reservedTags` 接收保留标签数组，默认为空；组件检查保留值与当前列表的
重复项，并提示“该标签已存在”。输入失焦或按回车时去除首尾空格，空值不添加；默认保留大小写
和前导点。业务需要格式化时通过 `normalizeTag(tag)` 传入转换函数，在重复检查前执行。
`addText` 默认为“添加标签”。组件内部维护输入框显隐与自动聚焦，根节点阻止点击冒泡；外部间距通过 `class` 设置。

### MkCardCheckbox

卡片式复选组件，手动导入 `@/components/mk-card-checkbox/index.vue`，不参与全局注册。
通过布尔 `v-model` 管理选中状态，`label` 必填并作为复选框的无障碍名称；`disabled` 禁止切换。
默认插槽放置图标、标题、描述等内容。卡片统一维护悬停阴影、选中边框及右侧复选框，
点击卡片或复选框均更新一次 `v-model` 并触发 `change(checked)`；复选框保留原生键盘操作。
插槽中的输入框、按钮等独立交互区域使用 `@click.stop`，避免操作时切换卡片。
其余卡片属性和样式通过 `$attrs` 透传到 `el-card`。
知识库、工具（含 Skills）、智能体选择弹窗，以及动态表单配置器的添加知识库列表统一使用
该组件。集合选择通过 `:model-value` 与 `@update:model-value` 接入原有业务选择逻辑，
保留筛选、跨目录选择和已选快照；不要同时监听 `change` 重复更新同一集合。

### LogoFull、LogoIcon

`LogoFull` 展示带产品名称的完整 Logo，`LogoIcon` 展示不带产品名称的图形 Logo，使用时分别从
`@/components/mk-logo/LogoFull.vue` 和 `@/components/mk-logo/LogoIcon.vue` 显式导入。两个组件在
默认主题下展示内置蓝紫渐变 Logo，自定义主题下使用 Theme Store 中的当前主题色。`LogoFull`
还会优先展示 Theme Store 中配置的 `loginLogo`。两个组件都只接收可选的 `height`，其余主题与
Logo 数据统一从 Theme Store 获取。

### MkDateRange

组合日期预设下拉框和自定义日期区间选择器。默认显示“过去 7 天”，仅在用户修改筛选条件时通过
`change` 返回 `{ startTime, endTime }`；组件挂载时不主动触发 `change`。预设日期的 `endTime` 为
空字符串，自定义日期清空时两个字段均为空字符串。组件不绑定具体接口字段，使用方负责初始化
默认查询参数，并将筛选结果映射为业务查询参数。

### MkDragUpload

组合拖拽选择区和已选文件卡片，通过 `v-model` 管理 Element Plus `UploadUserFile[]`。`accept`
直接传给上传控件；`dragText`、`selectText`、`tipText` 和 `replaceText` 可替换展示文案。组件只负责
文件选择与展示，使用方通过 `change` 执行校验和上传，通过 `remove` 清理业务数据；`download`
作用域插槽提供当前文件，由使用方按业务需要放置下载按钮。组件暴露 `clearFiles()`，用于请求失败
或表单重置时清空上传控件内部状态。

### PythonCodeEditor

入口 `codemirror-editor/python.vue`。

Python 与 JSON 编辑器通过 `<style lang="scss" scoped src="./style.scss">` 共享组件目录内的
样式，使用 `mk-codemirror` 容器和 `:deep()` 限定 CodeMirror 内部节点的覆盖范围。普通编辑器
与全屏弹窗内容分别提供该容器，默认高度为 `210px`，调用方可通过透传的 `style` 覆盖；全屏
编辑器单独设置高度。不在全局 `app.scss` 中覆盖 `.cm-editor`。

基于 CodeMirror 6 的 Python 代码编辑器，通过 `v-model` 管理代码，并在组件内部调用工具 pylint
接口生成诊断。组件最多展示 50 条诊断，并在代码停止输入 500ms 后检查。编辑器提供内置全屏
入口；全屏确认时更新 `v-model` 并触发 `submit-dialog`，`header-extra` 插槽用于添加全屏标题栏操作。

### JsonInput

入口 `codemirror-editor/Json.vue`。

JSON 专用输入框，通过 `v-model` 接收并回传解析后的 JSON 值，内置 JSON 语法诊断、格式化和全屏
编辑。与 `MdEditorMagnify` 一样，通过 `useFormItem()` 触发外层表单项校验，不在组件内部创建
表单项。内容变化时触发 `change`，失焦和全屏确认后触发 `blur`；`validateEvent` 默认为 `true`，
设为 `false` 可关闭自动触发。无效输入也会触发校验，不能仅监听解析后的 `v-model`。

组件暴露 `format()` 和 `validateRules()`。JSON 语法规则统一由 `validateRules` 校验编辑器原始
文本，空白或无效 JSON 提示“请输入正确的 JSON 格式”；外层 `rules` 接入该方法后，表单提交
也会检查语法。无法解析的输入不会覆盖最后一次有效的 `v-model` 值，不要直接对已经解析的
`value` 再调用 `JSON.parse(value)`。必填等业务规则继续放在外层表单项。

### MkSearchList

手动导入 `mk-search-list/index.vue`，放在有明确高度的纵向 Flex 容器中。
`v-model` 为搜索词；`data` 传全量数组，默认按 `name` 忽略大小写与首尾空格过滤，以 `id` 识别行。
`props.label` / `props.value` 可映射字段，唯一值不能重复。`defaultActive` 设置选中值，后续变更也会同步。
每批渲染 50 条，搜索或数据变化重置滚动位置；这是前端分批渲染，不替代接口分页。

默认插槽提供 `{ row, index, active }`。`action`、`action-dropdown` 的
参数与优先级沿用 `MkListItem`，下拉直接放 `MkDropdownItem`。`click(row, index)` 返回原始行。
`empty` 可自定义空态；默认空数据使用 `emptyText`（“暂无数据”），有搜索词时显示“没有找到相关内容”。

```vue
<MkSearchList v-model="keyword" :data="workspaces" :props="{ label: 'displayName', value: 'workspaceId' }" @click="selectWorkspace">
  <template #default="{ row, active }">
    <span :class="{ 'font-medium': active }">{{ row.displayName }}</span>
  </template>
  <template #action-dropdown="{ row }">
    <MkDropdownItem @click="editWorkspace(row)">编辑</MkDropdownItem>
  </template>
</MkSearchList>
```

### MkDynamicsForm、MkDynamicsFormConstructor

`MkDynamicsForm` 根据字段配置渲染动态表单，统一维护字段值、默认值、显隐规则和表单校验；
`MkDynamicsFormConstructor` 用于新增或编辑单个字段配置。该组件族位于 `components` 直属目录，
使用方必须从 `@/components/mk-dynamics-form` 手动导入，不安装为 Vue 插件，也不全局注册其内部
字段组件。

组件专用类型和选项常量维护在 `mk-dynamics-form/type.ts` 与 `mk-dynamics-form/constant.ts`，不放入
项目级 `api/types`、`api/enums` 或 `constants`。使用方统一从组件 `index.ts` 获取公开组件、类型
和字段类型选项，不深层导入内部文件。

组件 TypeScript 类型使用 PascalCase 和单数语义，例如 `FormField`、`DynamicFormValue`、
`VisibilityCompareOperator`；数组和集合变量使用复数业务名称。Vue 脚本中的 Props、事件参数和
局部变量使用 camelCase，模板属性使用 kebab-case。`input_type`、`default_value`、
`visibility_rules` 等服务端字段协议保持 snake_case，不在组件边界内改名。

公开入口包括 `dynamicFormTypeOptions`；`FormItem.vue`、`FormItemLabel.vue`、`items/` 和配置器子目录均为内部实现。

`MkDynamicsForm` 的主要 Props 为 `modelValue`、`renderData`、`otherParams`、`view`、
`defaultItemWidth` 和 `parentField`，公开 `validate()`、`render()`、`initDefaultData()` 与
`ruleFormRef`。`MkDynamicsFormConstructor` 接收 `modelValue`、`fieldTypeOptions`、
`enableVisibility` 和 `leftOptions`，其中 `leftOptions` 使用 `VisibilityFieldOption[]`；公开
`validate()`、`getData()` 与 `render()`。

启用显隐设置时，配置器将 Tabs 导航与内容分开，只继承容器的最大高度，内容较少时自然撑开。
`el-scrollbar` 及其内部滚动容器使用可收缩的 Flex 布局，并覆盖默认的百分比高度；达到最大高度后
仅内容区滚动，Tabs 保持固定。普通 `MkDialog` 已提供内容最大高度，调用方不需要设置固定高度。
两个表单通过 `v-show` 切换并保持挂载，确保未选中的页签也能回填、取值和校验。

字段配置中的动态校验器和表格行表达式属于受信任的服务端协议，只允许加载可信配置；普通业务
输入不得作为脚本传入。

单选、多选、MultiRow、RadioRow 和卡片单选配置器的自定义选项中，标签和选项值的必填校验跟随字段的“是否必填”；每行通过
`option_list.<index>.label`、`option_list.<index>.value` 参与配置表单校验。编辑中的不完整行
保留在表单内，仅两项都填写且非纯空白的选项进入默认值选择区和 `getData()` 返回的 `option_list`。
初始化、空配置回填和切回自定义赋值时保留一行空白选项。卡片单选仅在存在完整选项时显示默认值卡片区。
引用变量模式继续保留变量路径，不应用自定义选项过滤。
MultiRow、RadioRow 的配置器与运行时复用字段组件，分别使用复选按钮组、单选按钮组，保留原生
禁用、键盘和校验行为；仅展示完整选项，输出仍为 `MultiRow`、`RadioRow`。

动态表单的 Model 字段使用 `SelectModel`，将 `attrs.provider_list` 中的模型快照映射为
扁平 `ModelItem[]`，由选择器统一分组和展示供应商。旧快照未保存状态时保留可选行为，已保存的
状态按 `SelectModel` 的可用性规则处理。切换模型一次性回写 `model_id` 和深拷贝后的
`model_params_setting`；清空时回写空 ID 和空参数，避免修改原配置中的参数对象。

Knowledge 配置器复用 `SelectKnowledgeDialog` 选择可选知识库，沿用文件夹、共享资源查询及
相同 Embedding 模型约束。打开时传入已选快照，确认后回写可选知识库并清理已取消 ID 对应的
默认值；取消不修改配置。

Model 配置器的默认模型也使用 `SelectModel`，仅展示已选的可选模型，不开启参数设置入口。
选择时将模型 ID 转换为包含已配置参数的 `default_value` 对象，清空时重置为空对象。

## 跨页面业务组件

业务组件显式导入，可调用固定业务 API；页面保留自身的列表查询、路由和保存编排。

### FolderTree

Workspace 的文件夹虚拟树业务组件。组件根据当前资源上下文和 `source` 调用统一文件夹接口，负责
文件夹树查询、搜索、排序、创建、编辑、移动和删除。通过 `v-model` 控制当前文件夹 ID，首次加载
完成后通过 `loaded` 返回该 ID 对应的完整文件夹，选择文件夹时触发 `select`。传入的 ID 不存在时，
优先回退到“全部”入口，否则回退到首个可用文件夹。`showAll`、`showShared` 分别控制全部和共享入口，
`rootLabel` 可覆盖根入口文案，`disabledFolderIds` 用于只选场景中禁用指定节点。显示“全部”入口的
主目录树初始化时会读取字符串类型的 `folderId` query 并设置当前文件夹；用户选择文件夹时不把
新 ID 写入路由，但会清除已有的 `folderId`，避免刷新页面后恢复到旧文件夹。隐藏“全部”入口的
移动目录树继续以调用方传入的 `v-model` 为准。

可编辑文件夹的菜单提供“资源授权”，根据对应资源模块的 `folderAuth(folder.id)` 控制入口。
点击后复用 `ResourceAuthorizationDrawer`，传入当前 `source`，通过 `workspaceId` Prop 传入文件夹的 `workspace_id`，调用 `open(folder.id, folder)` 传入
原始完整文件夹子树；搜索过滤不缩减子资源授权范围。只读选择场景不挂载授权抽屉。

页面顶部需要触发根目录创建时，通过页面语义处理方法调用组件暴露的 `openCreate()`；外部数据变化
后可调用 `refresh()` 重新加载文件夹树。
`VirtualizedTree.vue` 基于 `@he-tree/vue` 的 `Draggable` 实现虚拟渲染和拖拽交互，只负责树 UI，
不调用 API；不要替换为 Element Plus `el-tree-v2`。

### MoveToDialog

可复用的文件夹移动对话框。传入资源 `source` 和请求状态 `loading`，通过组件 Ref 调用
`open(currentFolderId)`。对话框每次打开都会重新查询文件夹树，并复用 `FolderTree` 的搜索与排序；
确认后通过 `submit` 返回目标文件夹 ID，使用方自行维护待移动资源，完成请求后调用 `close()`
关闭弹窗。

### SelectKnowledgeDialog

关联知识库选择弹窗，手动导入 `@/components/business/select-knowledge-dialog/index.vue`。
通过 `open(knowledge)` 传入已选知识库快照，确认后通过 `submit` 返回新的选择；取消不修改调用方
数据，关闭后统一清理临时状态。选择数据直接基于 `KnowledgeItem` 声明为
`(Partial<KnowledgeItem> & { id: string })[]`，保留必需的 ID 并兼容缺少详情的旧数据，
不再维护弹窗专用类型文件。
组件采用 `MkViewLayout` 左右布局，搜索栏位于内容区右上角，刷新位于弹窗标题栏。
选项使用紧凑三列布局（窄屏减少列数），左侧图标与省略名称、右侧复选框。点击卡片或复选框
切换选择，选中后仅展示相同 Embedding 模型的选项，清空后恢复；悬停展示知识库详情。
复用只读 `FolderTree`，通过工作空间及共享 API 的 `getAllKnowledge` 一次加载当前查询的全部
知识库，不使用滚动分页。支持名称搜索和跨目录保留选择，调用方维护最终关联 ID 与快照。

### SelectApplicationDialog、SelectToolDialog

手动导入 `business/select-application-dialog/index.vue` 和 `business/select-tool-dialog/index.vue`。
两者沿用知识库选择弹窗的目录、名称搜索、三列卡片、悬停详情、跨目录选择和清空交互；
`open()` 接收已选资源对象数组，`submit` 返回深拷贝后的资源对象数组，兼容只有 ID 的旧数据。
每次打开先重置临时状态；取消不提交。

智能体通过 `getAllApplication` 全量查询已发布资源，不展示共享目录。工具通过工作空间或共享
`getAllTool` 全量查询，仅展示启用资源；`toolTypes` 默认包含自定义、工作流和内置工具，
Skills 场景传入 `[TOOL_TYPE.SKILL]`，并通过 `title` 指定标题。两者支持 `excludedIds`，
供调用方排除当前智能体或工具，避免直接自引用。弹窗不使用滚动分页。

### SelectModel

按供应商分组展示模型，单选 `v-model` 为字符串，`multiple` 模式为字符串数组，变化时触发 `change`。`options` 为
`ModelItem[]`，`providerOptions` 为 `ModelProviderItem[]`，模型列表和供应商列表均由使用方查询。

只有 `status === MODEL_STATUS.SUCCESS` 的选项可选，同供应商内可用模型排在前面。
`canEditParams` 默认 `false`，开启且为单选时显示参数按钮；多选不加载或修改参数。
参数按钮位于选择框右侧内部，与选择框共用外边框，并通过短竖线与下拉箭头分隔。
未选择模型或传入 `disabled` 时按钮禁用；点击打开组件内的 `ModelParamsDialog`。
通过 `v-model:model-params` 绑定参数：切换模型时加载默认值，清空模型时清空参数，弹窗确认后
回写配置，取消不修改已保存参数。参数表单依赖上层 `getModelParamsForm(modelId)` 注入；未提供时只得到空配置。
使用方开启参数入口后应绑定对应参数字段，并移除独立的参数按钮、弹窗和默认参数请求。
通过 Props 与事件回写设置的子组件，应分别发送模型 ID 和参数的局部更新，由父级合并，避免
同次交互连续更新时使用旧 Props 覆盖刚选中的模型。

`canAdd` 默认为 `false`，开启后在下拉列表底部显示“添加模型”，复用 `ModelCreateButton` 的
供应商选择和模型创建流程。组件通过 `isWorkspaceResource()`、`isSystemSharedResource()` 读取
`resourceScope`：Workspace 传入 `ModelApi`，System 共享资源传入 `SystemSharedModelApi`；
其他范围暂不展示创建入口。创建成功后触发 `refresh`，使用方重新加载原业务范围的模型选项，
不自动替换选中模型。`footer` 插槽仅在 `canAdd` 且当前范围允许创建时生效。

### WorkspaceDropdown

`showRoleTags` 默认为 `true`，控制选项中的小尺寸角色标签组；传入 `:show-role-tags="false"` 隐藏。
角色名称读取 `WorkspaceItem.role_name`，缺省或为空时不展示标签组。长工作空间名称和首个角色标签
在行内省略，悬停查看完整文字；角色标签组最多占行宽的一半，保留 `+N` 浮层入口。

统一工作空间下拉框的图标和触发器布局。通过 `options` 传入工作空间选项，通过 `v-model`
控制选中值，选择后通过 `select` 返回完整选项。组件不读取 Store，也不执行导航；路由切换和
数据刷新由使用方处理。内部显式导入非全局的 `MkFilterableDropdown`，复用搜索与选项渲染能力。

### WorkspaceRelationTags

用于展示标签组，并在悬浮表格中展示每个标签关联的工作空间。
`tags` 控制表格单元格中的折叠标签；`tagWorkspace` 使用标签名称作为键、工作空间
名称数组作为值；`tableRenderParams.property` 和 `tableRenderParams.value` 分别设置
悬浮表格的标签列与工作空间列标题。

### ResourceAuthorizationDrawer

入口 `business/resource-authorization-drawer/index.vue`。传入 `type`、资源实际所属的 `workspaceId`，
通过 `open(id, folder?)` 打开；`isFolder`、`isRootFolder` 标记文件夹范围。工作空间不能从路由回退，
缺少时不挂载授权列表。`closed` 在关闭动画结束、临时状态清理后触发；当前没有对外 `refresh` 事件。

默认“按用户组”，支持名称搜索及查看成员；“按用户”支持姓名、用户名、权限及商业版本角色搜索。
两者支持跨页选择、单项和批量配置，搜索清空选择；切换标签重新挂载，保存期间禁止切换。
入口统一提交，成功后关闭配置弹窗并刷新当前列表，失败保留配置。
根目录隐藏“不授权”，已有该值按“查看”展示；包含子资源时传入完整文件夹子树，
按资源所属工作空间筛选可管理的文件夹 ID，无可管理目录时禁用该范围。

用户授权按 `isSystemResource()` 选择 System 或 Workspace API；用户组列表当前使用 Workspace API。
现有提交分支却使用所选的 `authorizationApi` 调用用户组保存，System API 尚无该方法，
因此不能将 System 用户组保存视为已支持。用户和用户组列表目前也没有请求版本校验。

### UserGroupMembersDrawer

手动导入 `business/resource-authorization-drawer/user-group/UserGroupMembersDrawer.vue`，通过 `open(userGroup)` 传入
`SystemUserGroup`，按其 `workspace_id` 查询成员。支持用户名、姓名搜索和分页，角色使用
`MkTagGroup` 展示；供系统资源授权页面和资源授权抽屉共同复用。

### RelatedResourcesDrawer

入口 `business/related-resources-drawer/index.vue`。传入完整 `api: typeof RelatedResourcesApi`，
通过 `open(resourceType, resource)` 传入含 `workspace_id` 的资源快照，用其所属工作空间查询。
`close()` 关闭，`closed` 在动画结束清理后触发。页面按范围选择真实 API，抽屉不拼接 System URL。

关系页签为“依赖 / 被依赖”，分别查询依赖的资源和引用当前资源的资源；模型、非工作流工具默认被依赖。
切换方向清空搜索、工作空间筛选与分页，资源名称当前仅展示，不提供跳转或相关回调。
`showWorkspace` 由调用方决定，开启后查询工作空间选项并提供多选筛选，`workspace_ids` 当前传 JSON 字符串。
供应商图标由抽屉查询后传给内部 `ResourceIcon`，模型供应商标识来自关系记录的 `icon`。
当前查询没有请求版本校验，不保证旧响应在切换或关闭后被忽略。

工作空间模型、知识库、应用、工具列表已分别通过 `RelatedResourcesModelAction`、
`RelatedResourcesKnowledgeAction`、`RelatedResourcesApplicationAction`、`RelatedResourcesToolAction` 接入。

## 维护与检查

新增或调整公共组件时，先确定目录及公开入口，按本文约定实现类型化接口；仅在接口、目录或使用规则变化时
同步对应章节，不记录内部函数清单。变更全局注册组件时，通过 Vite 开发或构建刷新声明。

Vue/TypeScript 改动运行定向 ESLint、类型检查及必要的入口构建；仅修改文档时检查引用、
Prettier 和 `git diff --check`，无需构建。`npm run lint` 尚无对应 `lint:*` 子脚本，使用定向 ESLint。
