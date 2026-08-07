# components 目录说明

本文档是项目组件规则的唯一依据。新增、修改、移动或使用公共组件前，应先阅读本文档。

`src/components` 存放跨页面、跨业务模块复用的 UI 组件。高频组件放在自动注册的 `global` 中；其他共享组件直接与 `global` 并列，使用时手动引入。仅在单个业务模块中复用的组件应放在对应功能目录下。

没有明确需求时，不要引入新的 UI 组件库。

## Element Plus

Element Plus 已在 `src/main.ts` 和 `src/chat.ts` 中全局注册，Vue 模板可以直接使用 Element Plus 组件，无需单独注册：

```vue
<el-button type="primary">保存</el-button>
```

Element Plus 图标不是全局组件。需要作为属性传递或在脚本中使用时，仍须从 `@element-plus/icons-vue` 显式导入。

页面实现应尽量优先使用项目已有的 Mk 公共组件；没有对应 Mk 组件时，优先使用 Element Plus
现成组件。视觉样式不符合设计稿时，应基于现有组件通过 Props、Slots、Tailwind class 或
必要的样式覆盖进行改造，不要重复手写 Element Plus 已经提供的结构、状态和交互。只有现有
组件无法满足必要的结构或行为时，才新增自定义组件。

使用 Element Plus 组件时，应先检查并优先使用组件原生提供的 Props、事件、插槽、公开方法
和交互模式，不要自行重复实现已有能力。例如菜单跳转优先使用 `el-menu` 的 `router` 属性，
而不是监听 `select` 后手动调用路由。只有原生 API 无法满足需求时，才补充自定义逻辑。

### 单一触发节点

Element Plus 使用 `ElOnlyChild` 处理浮层触发器。`el-tooltip`、`el-popover`、
`el-popconfirm`、`MkDropdown` 和基于它封装的下拉组件，其默认触发插槽或 `reference` 插槽
必须只渲染一个有效根节点。多个并列按钮、标签或文本需要先用一个具有实际布局盒的 `span`
或 `div` 包裹；不要使用 `template` 或 `display: contents` 充当包裹层，否则浮层无法可靠计算
触发区域的位置和尺寸。

```vue
<el-popover trigger="hover">
  <template #reference>
    <span class="inline-flex items-center gap-1">
      <el-tag>管理员</el-tag>
      <el-tag>+2</el-tag>
    </span>
  </template>
  <div>浮层内容</div>
</el-popover>
```

创建或评审组件、页面时，应同时检查直接使用的 Element Plus 浮层组件，以及转发触发插槽的
项目封装组件，确保每一层最终都向 Element Plus 传递单一有效节点。

## 自动注册

Vite 使用 `unplugin-vue-components`，但只扫描 `src/components/global`。该目录中的组件可以直接在 Vue 模板中使用，无需手动 `import`：

```vue
<MkIcon name="icon_left_outlined" />
```

自动生成的组件类型声明位于 `src/components.d.ts`。不要手动修改该文件；新增、删除或移动组件后，通过开发服务或生产构建刷新声明。

除 `src/components/global` 外，`components` 下的其他组件目录都不参与扫描，必须显式导入。自动注册也只适用于 Vue 模板；脚本逻辑、类型、常量以及传给组件的 Element Plus 图标仍需正常导入。

## 目录约定

```text
src/components/
├── COMPONENT_README.md
├── global/                   # 高频、稳定的基础组件，自动注册
│   ├── mk-complex-search/
│   │   └── index.vue         # 字段选择与输入/枚举条件组合搜索框
│   ├── mk-dropdown/
│   │   ├── index.vue             # 统一下拉菜单箭头和弹层间距
│   │   ├── mk-dropdown-menu.vue  # 统一下拉菜单容器
│   │   └── mk-dropdown-item.vue  # 统一菜单项图标、内容和选中状态布局
│   ├── mk-filterable-dropdown/
│   │   └── index.vue         # 带搜索过滤和滚动列表的下拉框
│   ├── mk-icon/
│   │   └── index.vue         # MaxKB SVG Symbol 与 Element Plus 图标统一入口
│   ├── mk-search-list/
│   │   └── index.vue         # 统一搜索框与剩余空间滚动列表布局
│   ├── mk-search-input/
│   │   └── index.vue         # 统一搜索图标并透传 ElInput 属性和事件
│   ├── mk-status-label/
│   │   └── index.vue         # 统一启用、禁用状态的图标与文案
│   ├── mk-tag-group/
│   │   └── index.vue         # 折叠展示标签组并提供可配置浮层
│   └── mk-table/
│       └── index.vue         # 统一表格样式与分页布局
├── mk-workspace-dropdown/    # 工作空间选择下拉框，选项和点击业务由使用方提供
│   └── index.vue
└── user-selector/            # 低频共享组件示例，使用方手动引入
    └── index.vue
```

- 高频、稳定、跨多数页面使用的基础组件放入 `global`。
- 使用页面较少、有明显业务含义或依赖较重的共享组件直接放在 `components/<component-name>`。
- 仅属于一个功能模块的组件放入 `views/<feature>/components` 等所属功能目录。
- 一个公共组件使用一个 kebab-case 目录。
- 组件入口统一使用 `index.vue`。
- 组件名使用 PascalCase；目录名使用 kebab-case，例如 `MkIcon` 对应 `mk-icon/index.vue`。
- 使用 `index.vue` 作为入口时，必须通过 `defineOptions({ name: 'ComponentName' })` 显式声明多单词组件名，避免 ESLint 将组件名推断为 `index`。
- 组件内部实现、Props 和事件保持类型化。
- 组件专用类型保留在组件实现中；组件目录内多个文件共用时放在该组件的 `types.ts`，出现重复
  声明时提取到最近共同目录的 `common.ts`。只有同一业务类型还被 API 使用时，才放入
  `src/types` 并从 `@/types` 导入。
- 组件样式默认使用 `scoped`；只有明确的全局规则才放入 `src/styles`。
- `global` 组件不要创建只用于二次导出的 `components/index.ts`，模板组件由自动注册插件解析。
- 除 `global` 外的共享组件必须从具体路径手动导入，让依赖关系在使用文件中可见。

## MkFilterableDropdown

`MkFilterableDropdown` 是自动注册的带搜索过滤和滚动列表的共享下拉框。触发器通过默认插槽
传入；菜单项需要自定义图片、图标或其他业务内容时，使用 `option` 作用域插槽并通过当前 `option` 渲染。
未传入 `option` 插槽时默认显示 `option.label`。选项以 `@/types` 中的 `OptionItem` 作为最小约束，
可以附加业务字段；组件泛型会保留具体类型。选择菜单项时，组件先更新 `v-model`，再通过
`select` 事件返回完整的 `option`。

```vue
<MkFilterableDropdown v-model="selectedValue" :options="options">
  <template #default="{ text }">
    <button type="button">{{ text }}</button>
  </template>
  <template #option="{ option }">
    <div class="flex items-center gap-2">
      <img :src="option.logoUrl" class="size-4 shrink-0 rounded-sm object-cover" />
      <span class="min-w-0 flex-1 truncate">{{ option.label }}</span>
    </div>
  </template>
</MkFilterableDropdown>
```

```ts
const options = [{ label: '工作空间', logoUrl: '/workspace.png', value: 'workspace' }]
```

## MkWorkspaceDropdown

`MkWorkspaceDropdown` 统一工作空间下拉框的图标和触发器布局，需要从
`@/components/mk-workspace-dropdown/index.vue` 手动导入。使用方通过 `options` 传入当前页面
可用的工作空间，通过 `v-model` 控制选中值，并在 `select` 中实现路由切换、重新加载数据
等页面业务；公共组件内部不读取用户 Store，也不执行导航。

```vue
<MkWorkspaceDropdown
  v-model="selectedWorkspaceId"
  :options="workspaceOptions"
  @select="handleWorkspaceSelect"
/>
```

## MkDropdown

项目内的普通下拉菜单使用全局自动注册的 `MkDropdown`，不要直接使用 `el-dropdown`。它基于 Element Plus Dropdown，并统一提供以下默认值：

- `showArrow: false`：弹层不显示箭头。
- `offset: 4`：触发器与弹层保持 `4px` 间距。

> **UI 规范：以上两个值为项目统一固定值，业务组件不得修改或覆盖。** 如需调整，必须先更新统一 UI 规范，再修改 `MkDropdown`；禁止在调用处传入 `show-arrow`、`offset` 或通过 `popper-options` 覆盖间距。

除上述两个固定配置外，其他 Element Plus Dropdown 属性和 `default`、`dropdown` 插槽会原样透传。

`MkDropdown` 的 `dropdown` 插槽内必须使用 `MkDropdownMenu` 和 `MkDropdownItem`，禁止与
`el-dropdown-menu`、`el-dropdown-item` 混用。Element Plus 原始组件只允许出现在对应
Mk 组件的内部实现中。

### 菜单分组

`MkDropdownMenu` 内一律禁止使用 `MkDropdownItem` 的 `divided` 属性。该属性将分割线绘制在带有菜单内边距的菜单项上，无法满足项目分割线布局规范。需要菜单分组时，应在菜单外层结构中使用独立的 `el-divider`，不要通过 `divided` 实现。

```vue
<MkDropdown trigger="click" placement="bottom-end">
  <button>打开菜单</button>
  <template #dropdown>
    <MkDropdownMenu>
      <MkDropdownItem>菜单项</MkDropdownItem>
    </MkDropdownMenu>
  </template>
</MkDropdown>
```

### 菜单项布局

需要左侧图标或选中勾的菜单项使用 `MkDropdownItem`。左侧为 Element Plus
图标时，通过 `icon` 属性传入；使用 `MkIcon` 或需要自定义结构时，通过 `icon` 插槽传入。
两种方式都会由 `MkDropdownItem` 放入统一的左侧图标区域并使用 `N600` 颜色，不影响菜单项
其他位置的图标。普通菜单不传
`selectable`；可选中菜单传入 `selectable`，并通过 `selected` 控制当前项。开启
`selectable` 后，未选中的菜单项也会预留勾选位，保证同组文字对齐。默认插槽是可自定义的
中间内容区域，不会强制添加文字省略；需要省略时由插槽内容自行添加 `truncate`。

```vue
<MkDropdownItem :icon="Setting">设置</MkDropdownItem>
<MkDropdownItem>
  <template #icon>
    <MkIcon name="icon_setting_outlined" />
  </template>
  设置
</MkDropdownItem>
<MkDropdownItem selectable :selected="item.value === selectedValue">
  {{ item.label }}
</MkDropdownItem>
```

## MkIcon

`MkIcon` 统一承载 MaxKB SVG Symbol 和 Element Plus 图标。`name` 和 `icon` 均未传入时默认显示
`icon-404`。未传入 `size` 时默认使用 `16px`；传入 `size` 时覆盖默认值。`gradient` 仅用于
SVG Symbol，启用后使用项目主题渐变填充。`size`、`color` 的其他行为与 `el-icon` 保持一致。

### MaxKB SVG Symbol

通过完整的 Symbol ID 引用：

```vue
<MkIcon name="icon_left_outlined" />
<MkIcon name="icon_start_outlined" :size="20" color="#3370ff" />
<MkIcon name="icon_home_filled" gradient />
```

SVG Symbol 由 `src/assets/iconfont.js` 提供。该文件由 iconfont 平台定期生成，只允许整体替换，不要手动修改。

### Element Plus 图标

只导入 Element Plus 图标本身，`MkIcon` 无需导入：

```vue
<script setup lang="ts">
import { Setting } from '@element-plus/icons-vue'
</script>

<template>
  <MkIcon :icon="Setting" :size="20" color="#3370ff" />
</template>
```

### 使用约定

- `name` 和 `icon` 二选一。
- `name` 和 `icon` 均未传入时使用 `icon-404`。
- `gradient` 仅用于 SVG Symbol；是否启用由调用方根据组件状态和主题状态决定。
- `size` 默认为 `16px`，仅在需要其他尺寸时显式传入。
- MaxKB 图标使用 `name`，Element Plus 图标组件使用 `icon`。
- 不直接使用 Unicode、Font Class 或裸 `<svg><use>`。
- 更新图标时直接覆盖 `src/assets/iconfont.js`。
- 保持 Symbol ID 稳定；ID 变化时必须同步修改所有对应的 `MkIcon name`。

## MkSearchInput

项目内带搜索图标的输入框使用全局自动注册的 `MkSearchInput`。组件默认 placeholder 为“搜索”
并支持清空，在 `prefix` 插槽显示搜索图标；`v-model`、其他属性和事件直接传递给 Element Plus
Input，因此可以继续使用 `el-input` 的原生能力。传入 `prefix` 插槽时可以覆盖默认搜索图标，
`prepend`、`append` 和 `suffix` 插槽也会继续透传。

```vue
<MkSearchInput v-model="searchKeyword" placeholder="搜索工作空间" />
```

## MkStatusLabel

布尔状态使用全局自动注册的 `MkStatusLabel` 展示。通过 `active` 控制启用或禁用状态；默认文案为
“已启用”和“已禁用”，可通过 `active-text`、`inactive-text` 按业务语义修改。

```vue
<MkStatusLabel :active="row.is_active" />
<MkStatusLabel :active="task.completed" active-text="已完成" inactive-text="未完成" />
```

## MkTagGroup

标签数组在表格等紧凑区域中使用全局自动注册的 `MkTagGroup` 折叠展示。组件显示第一个标签，
其余标签收起为 `+N`；默认仅悬停 `+N` 打开浮层，并在浮层中展示剩余标签。传入
`trigger-area="all"` 后，悬停第一个标签或 `+N` 均可打开浮层。`popover-disabled` 只禁用浮层，
不改变标签折叠结果。需要展示表格等业务内容时使用 `popover` 作用域插槽。

```vue
<MkTagGroup :tags="roleNames" />

<MkTagGroup :tags="roleNames" trigger-area="all" :popover-width="600">
  <template #popover="{ tags }">
    <el-table :data="getRoleTableData(tags)" />
  </template>
</MkTagGroup>
```

## MkComplexSearch

需要在多个字段间切换搜索条件时使用全局自动注册的 `MkComplexSearch`。通过 `fields` 配置
字段标签、字段值和可选的枚举项。未配置 `options` 时使用文本输入，
配置后使用下拉选择。输入或选择完成时，`change` 事件返回 `{ [field]: value }`；
切换字段或清空条件时返回 `undefined`。

需要在脚本中声明字段配置时，从 `@/types` 导入通用的 `OptionItem`。

```vue
<MkComplexSearch
  :fields="[
    { label: '用户名', value: 'username' },
    {
      label: '状态',
      value: 'enabled',
      options: [
        { label: '启用', value: true },
        { label: '禁用', value: false },
      ],
    },
  ]"
  @change="loadUsers($event)"
/>
```

## MkSearchList

页面侧栏中由搜索框和滚动内容组成的列表使用全局自动注册的 `MkSearchList`。组件通过
`v-model` 接收搜索关键词，统一提供可清空的搜索框、搜索图标和占满剩余高度的
`el-scrollbar`；列表过滤、分组、选中和操作等业务逻辑由默认插槽中的调用方负责。

```vue
<MkSearchList v-model="searchKeyword" placeholder="搜索工作空间">
  <button v-for="workspace in filteredWorkspaces" :key="workspace.id">
    {{ workspace.name }}
  </button>
</MkSearchList>
```

组件需要位于有明确高度的纵向 Flex 容器中，才能让内部滚动区域正确占用剩余空间。

## MkTable

项目内带分页的标准表格使用全局自动注册的 `MkTable`。组件组合 `el-table`、分页、可选的列宽
拖拽和批量选择操作栏；不需要分页的场景直接使用 `el-table`。

### 表格与分页

`data` 和 `paginationConfig` 由 `MkTable` 直接接收；其余 Element Plus Table
属性与事件通过 `$attrs` 透传，列继续使用 `el-table-column` 声明。分页参数统一放入
`paginationConfig`：

```ts
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  pageSizes: [10, 20, 50, 100],
  total: 0,
})
```

`pageSizes` 可省略，默认使用 `[10, 20, 50, 100]`。通过
`v-model:pagination-config` 接收页码和每页数量的变化，也可以监听 `current-change` 和
`size-change`。

```vue
<MkTable
  v-model:pagination-config="paginationConfig"
  :data="currentPageUsers"
  :max-table-height="280"
  resizable
  row-key="id"
>
  <el-table-column prop="name" label="姓名" />
</MkTable>
```

### 高度与列宽拖拽

组件使用窗口高度减去 `maxTableHeight` 计算表格 `max-height`，并在窗口尺寸变化时重新计算。
`maxTableHeight` 表示页面中除表格外需要扣除的高度，默认值为 `250`；页面应根据表格上方和
下方的实际占用空间传入。

`MkTable` 默认不开启列宽拖拽，也不提供原生边框样式。传入 `resizable` 后，组件借用 Element
Plus 的 `border` 开启列宽拖拽，但会隐藏表格外框和纵向列线，并为可拖拽的表头分隔线提供
悬停、拖动高亮效果。需要显示原生边框的场景直接使用 `el-table`。

### 批量选择

表格包含 `type="selection"` 的选择列时，勾选任意数据会在页面底部显示选择操作栏。底栏复选框
与表头全选状态同步，支持全选、取消全选和半选状态。组件统一显示“已选 n/当前数据总数”和
“取消”，“取消”会清空当前选择；业务操作按钮通过 `footer-batch-actions` 插槽传入，当前选择
通过 `selection-change` 事件返回。

```vue
<MkTable :data="systemUsers" @selection-change="selectedUsers = $event">
  <el-table-column type="selection" width="40" />
  <el-table-column prop="username" label="用户名" />

  <template #footer-batch-actions>
    <el-button @click="setRoles(selectedUsers)">设置角色</el-button>
    <el-button type="danger" plain @click="removeUsers(selectedUsers)">删除</el-button>
  </template>
</MkTable>
```

组件暴露 `tableRef` 和 `clearSelection()`；需要调用其他 Element Plus Table 方法时使用
`tableRef`。

## 新增公共组件

1. 根据使用范围选择 `global`、`components` 直属组件目录或所属功能目录。
2. 在对应目录的 `<component-name>/index.vue` 创建组件。
3. 使用类型化 Props、Emits 和 Slots。
4. `global` 组件在模板中直接使用；其他共享组件和功能组件由使用方手动导入。
5. 运行类型检查及两个入口的生产构建。
6. 如果新增了通用约定或调整目录结构，同步更新本文件。
