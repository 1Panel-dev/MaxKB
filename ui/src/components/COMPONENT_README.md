# components 目录说明

本文档是项目公共组件规则的唯一依据。新增、修改、移动或使用公共组件前，应先阅读本文档。

`src/components` 只存放跨页面或跨业务模块复用的 UI 组件。仅在单个功能内使用的组件，应放在
对应的 `views/<feature>/components` 中。

## 组件选型

按以下顺序选择组件：

1. 首先检查 `src/components/global`，优先使用全局自动注册的 Mk 封装组件。
2. 全局组件无法满足时，检查 `src/components` 中需要手动导入的共享组件。
3. 没有对应 Mk 组件时，再使用 Element Plus 现成组件。
4. 通过 Props、事件、插槽、公开方法、Tailwind class 或必要的样式覆盖适配设计稿。
5. 现有组件无法满足必要的结构或行为时，再新增自定义组件。

已有全局 Mk 组件封装相同能力时，业务页面和业务组件必须使用该封装，不要绕过它直接使用
底层 Element Plus 组件，也不要在功能目录重复封装。例如对话框使用 `MkDialog`、抽屉使用
`MkDrawer`、下拉菜单使用 `MkDropdown`、图标使用 `MkIcon`、标准表格使用 `MkTable`。

Element Plus 已在 `src/main.ts` 和 `src/chat.ts` 中全局注册，Vue 模板可以直接使用。Element Plus
图标需要从 `@element-plus/icons-vue` 显式导入。

使用 Element Plus 前应先检查其原生 API，不重复实现已有能力。例如菜单跳转优先使用
`el-menu` 的 `router` 属性，不要监听 `select` 后手动调用 Router。

没有明确需求时，不要引入新的 UI 组件库。

## 目录与注册方式

```text
src/components/
├── COMPONENT_README.md
├── global/                       # 高频、稳定的基础组件，自动注册
│   ├── mk-complex-search/
│   │   └── index.vue             # 字段选择与输入或枚举条件组合搜索框
│   ├── mk-dialog/
│   │   └── index.vue             # 统一对话框关闭行为和内容滚动布局
│   ├── mk-dropdown/
│   │   ├── index.vue             # 下拉容器
│   │   ├── mk-dropdown-menu.vue  # 下拉菜单容器
│   │   └── mk-dropdown-item.vue  # 菜单项布局和选中状态
│   ├── mk-drawer/
│   │   └── index.vue             # 统一抽屉关闭行为和内容滚动布局
│   ├── mk-filterable-dropdown/
│   │   └── index.vue             # 带搜索过滤和滚动列表的下拉选择
│   ├── mk-icon/
│   │   └── index.vue             # SVG Symbol 与 Element Plus 图标统一入口
│   ├── mk-search-input/
│   │   └── index.vue             # 带默认搜索图标的输入框
│   ├── mk-status-label/
│   │   └── index.vue             # 布尔状态图标和文案
│   ├── mk-table/
│   │   └── index.vue             # 表格、分页、列宽拖拽和批量操作
│   └── mk-tag-group/
│       └── index.vue             # 标签折叠和剩余标签浮层
├── mk-search-list/
│   └── index.vue                 # 搜索框与剩余空间滚动列表，手动导入
├── mk-workspace-dropdown/
│   └── index.vue                 # 工作空间选择下拉框，手动导入
└── mk-workspace-relation-tags/
    └── index.vue                 # 标签及关联工作空间展示，手动导入
```

Vite 的 `unplugin-vue-components` 只扫描 `src/components/global`。该目录中的组件可以直接在
Vue 模板中使用，不需要手动导入。其他共享组件必须从具体文件路径导入：

```ts
import MkSearchList from '@/components/mk-search-list/index.vue'
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
import MkWorkspaceRelationTags from '@/components/mk-workspace-relation-tags/index.vue'
```

自动注册只适用于 Vue 模板。脚本中的类型、常量和 Element Plus 图标仍需显式导入。自动生成
的声明位于 `src/components.d.ts`，不要手动修改；通过开发服务、类型检查或生产构建刷新。

## 组件约定

- 高频、稳定、跨多数页面使用的基础组件放入 `global`。
- 使用页面较少、有明确业务含义或依赖较重的共享组件放在
  `components/<component-name>`，由使用方手动导入。
- 一个公共组件使用一个 kebab-case 目录，入口统一为 `index.vue`。
- 组件名使用 PascalCase；目录名使用 kebab-case，例如 `MkIcon` 对应
  `mk-icon/index.vue`。
- `index.vue` 必须通过 `defineOptions({ name: 'ComponentName' })` 声明多单词组件名，避免
  ESLint 将名称推断为 `index`。
- Props、Emits 和 Slots 保持类型化。
- 组件类型归属遵循 `src/api/API_README.md`；API 与组件共用的业务类型从
  `@/api/types` 导入。
- 组件样式默认使用 `scoped`；明确的全局规则放入 `src/styles`。
- `global` 不创建仅用于二次导出的 `components/index.ts`。

### 浮层触发节点

Element Plus 使用 `ElOnlyChild` 处理浮层触发器。`el-tooltip`、`el-popover`、
`el-popconfirm`、`MkDropdown` 及其封装组件的触发插槽必须只渲染一个有效根节点。多个并列
元素需要使用具有实际布局盒的 `span` 或 `div` 包裹；不要使用 `template` 或
`display: contents`，否则浮层无法可靠计算触发区域。

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

## 自动注册组件

### MkDialog

全局对话框组件，统一使用 `el-scrollbar` 包裹内容并为默认插槽提供 `p-6` 内边距。默认显示关闭
按钮、关闭时销毁内容，同时禁止点击遮罩或按 Escape 关闭；这些默认行为可以通过同名 Props
覆盖。Element Plus Dialog 的其他属性和事件通过 `$attrs` 透传，`header`、`subtitle`、默认和
`footer` 插槽保持可用。`subtitle` 位于标题下方的 Header 区域，并统一使用
`mb-6 text-sm text-N600` 样式；仅使用 `subtitle` 时，组件仍会按照 Element Plus 原生的标题
ID 和样式类渲染 `title`。内容区域超出最大高度后显示滚动条。

```vue
<MkDialog v-model="visible" title="创建工作空间" width="600">
  <template #subtitle>创建后可继续添加工作空间成员。</template>
  <el-form>...</el-form>
  <template #footer>
    <el-button @click="visible = false">取消</el-button>
    <el-button type="primary">创建</el-button>
  </template>
</MkDialog>
```

### MkDrawer

全局抽屉组件，统一使用 `el-scrollbar` 包裹内容并为默认插槽提供 `p-6` 内边距。默认显示关闭
按钮、关闭时销毁内容，同时禁止点击遮罩或按 Escape 关闭；这些默认行为可以通过同名 Props
覆盖。Element Plus Drawer 的其他属性和事件通过 `$attrs` 透传，`header`、默认和 `footer`
插槽保持可用。

```vue
<MkDrawer v-model="visible" title="创建用户" size="600">
  <el-form>...</el-form>
  <template #footer>
    <el-button @click="visible = false">取消</el-button>
    <el-button type="primary">创建</el-button>
  </template>
</MkDrawer>
```

业务 Dialog 和 Drawer 的状态生命周期保持一致：`open()` 先调用 `resetData()`，再回填编辑数据并
显示浮层；`close()` 先关闭浮层，再调用 `resetData()`；组件同时监听 `closed` 调用
`resetData()`，确保点击右上角关闭按钮时也完成清理。`resetData()` 应统一重置表单、提交状态、
临时选项和表单校验，不把清理逻辑散落在 `open()`、取消按钮或提交成功回调中。

### MkComplexSearch

用于在多个字段之间切换搜索条件。`fields` 使用 `@/api/types` 中的 `OptionItem<string>[]`；字段
包含 `options` 时使用下拉选择，否则使用文本输入。输入或选择完成时，`change` 返回
`{ [field]: value }`；切换字段或清空条件时返回 `undefined`。

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

### MkDropdown、MkDropdownMenu、MkDropdownItem

普通下拉菜单使用 `MkDropdown`，不要在业务代码中直接组合 `el-dropdown`、
`el-dropdown-menu` 和 `el-dropdown-item`。`MkDropdown` 默认 `persistent: false`，其余
Element Plus Dropdown 属性和事件通过 `$attrs` 传入，并暴露 `handleOpen()`、
`handleClose()`。

`dropdown` 插槽内使用 `MkDropdownMenu` 和 `MkDropdownItem`。下拉触发器必须只有一个有效根
节点。

```vue
<MkDropdown trigger="click" placement="bottom-end">
  <button type="button">打开菜单</button>
  <template #dropdown>
    <MkDropdownMenu>
      <MkDropdownItem :icon="Setting">设置</MkDropdownItem>
    </MkDropdownMenu>
  </template>
</MkDropdown>
```

菜单项左侧为 Element Plus 图标时通过 `icon` 传入；使用 `MkIcon` 或自定义结构时使用 `icon`
插槽。可选中菜单项传入 `selectable`，通过 `selected` 控制选中状态；开启后所有同组菜单项都会
预留右侧勾选位。

```vue
<MkDropdownItem selectable :selected="option.value === selectedValue">
  {{ option.label }}
</MkDropdownItem>
```

### MkFilterableDropdown

带搜索过滤和滚动列表的下拉选择。组件不限制选项字段，默认使用 `label` 作为展示和搜索字段、
`value` 作为唯一值；数据结构不同时通过 `props.label` 和 `props.value` 映射，使用方式与
`MkSearchList` 一致。原始选项类型会贯穿 `options`、作用域插槽和 `select` 事件。
`emptyText` 默认为“暂无匹配结果”。默认插槽接收 `selectedOption` 和 `text`，`option` 插槽接收
当前原始选项；选择后先更新 `v-model`，再通过 `select` 返回未经转换的原始选项。

```vue
<MkFilterableDropdown
  v-model="selectedWorkspaceId"
  :options="workspaces"
  :props="{ label: 'name', value: 'id' }"
  @select="handleWorkspaceSelect"
>
  <template #default="{ text }">
    <button type="button">{{ text }}</button>
  </template>
  <template #option="{ option }">
    <span class="truncate">{{ option.name }}</span>
  </template>
</MkFilterableDropdown>
```

### MkIcon

统一渲染 MaxKB SVG Symbol 和 Element Plus 图标：

- MaxKB 图标通过完整 Symbol ID 传给 `name`。
- Element Plus 图标组件通过 `icon` 传入。
- `name` 和 `icon` 二选一；均未传入时显示 `icon-404`。
- `size` 默认为 `16px`，仅在需要其他尺寸时传入。
- `gradient` 仅用于 SVG Symbol，启用后使用项目主题渐变。
- 不直接使用 Unicode、Font Class 或裸 `<svg><use>`。
- `src/assets/iconfont.js` 只允许整体替换，不要手动编辑；Symbol ID 变化时同步更新所有引用。

```vue
<MkIcon name="icon_left_outlined" />
<MkIcon name="icon_home_filled" gradient />
<MkIcon :icon="Setting" :size="20" color="#3370ff" />
```

### MkSearchInput

带默认搜索图标的输入框。`placeholder` 默认为“搜索”，组件固定支持清空；`v-model`、其他属性
和事件传递给 Element Plus Input。可通过 `prefix` 覆盖搜索图标，`prepend`、`append` 和
`suffix` 插槽也会透传。

```vue
<MkSearchInput v-model="searchKeyword" placeholder="搜索工作空间" />
```

### MkStatusLabel

用于展示布尔状态。`active` 控制启用或禁用，默认文案为“已启用”和“已禁用”；通过
`activeText`、`inactiveText` 修改业务文案。

```vue
<MkStatusLabel :active="row.is_active" />
<MkStatusLabel :active="task.completed" active-text="已完成" inactive-text="未完成" />
```

### MkTable

标准表格组件，组合 Element Plus Table、可选分页、列宽拖拽和批量选择操作栏。`data` 和
`paginationConfig` 由组件接收，其余 Table 属性和事件通过 `$attrs` 传入，列继续使用
`el-table-column`。

分页配置可省略；省略时不显示分页器。`pageSizes` 默认为 `[10, 20, 50, 100]`：

```ts
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  pageSizes: [10, 20, 50, 100],
  total: 0,
})
```

使用 `v-model:pagination-config` 接收页码和每页数量变化，也可以监听 `current-change` 和
`size-change`。切换每页数量时，组件会同时将 `currentPage` 重置为 `1`，页面只需在
`size-change` 中重新加载数据，不要重复修改页码。

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

`maxTableHeight` 表示窗口中除表格外需要扣除的高度，默认为 `250`；组件会在窗口尺寸变化时
重新计算 `max-height`。传入 `resizable` 后启用列宽拖拽，并隐藏为拖拽借用的原生边框视觉。
需要显示 Element Plus 原生边框时直接使用 `el-table`。

包含 `type="selection"` 的选择列时，选择数据会显示页面底部操作栏。批量按钮放入
`footer-batch-actions` 插槽，当前选择通过 `selection-change` 返回。组件暴露 `tableRef` 和
`clearSelection()`。

```vue
<MkTable :data="systemUsers" @selection-change="selectedUsers = $event">
  <el-table-column type="selection" width="40" />
  <el-table-column prop="username" label="用户名" />
  <template #footer-batch-actions>
    <el-button type="danger" plain @click="removeUsers(selectedUsers)">删除</el-button>
  </template>
</MkTable>
```

### MkTagGroup

用于在表格等紧凑区域折叠字符串标签。始终显示第一个标签；存在更多标签时显示 `+N`，悬停
后在浮层中展示剩余标签。`tags` 默认为空数组，`popoverDisabled` 只禁用浮层，不改变折叠
结果。

```vue
<MkTagGroup :tags="roleNames" />
<MkTagGroup :tags="roleNames" popover-disabled />
```

## 手动导入组件

### MkSearchList

组合搜索框和占满剩余空间的滚动列表。传入 `data` 时，组件默认按 `name` 过滤并按
`id` 识别选中项；数据字段不同时，通过 `props` 中的 `label`、`value` 建立字段映射。`row` 插槽接收
`row`、`index` 和 `active`。`action` 插槽用于普通行操作，`action-dropdown` 插槽用于下拉菜单；
两者均接收 `row`、`index`。操作区默认隐藏，鼠标移入列表项或操作区获得焦点时显示，
且不会触发列表项选中。下拉菜单的打开和关闭由 `MkDropdown` 管理。点击列表项会触发
`click(row, index)`，
过滤结果每批渲染 50 条，滚动到底部后自动追加下一批。组件必须放在具有明确高度的纵向 Flex 容器中。

Props 和模型：

| 名称            | 类型                                   | 默认值       | 说明                                                 |
| --------------- | -------------------------------------- | ------------ | ---------------------------------------------------- |
| `v-model`       | `string`                               | `''`         | 搜索关键词                                           |
| `data`          | `T[]`                                  | —            | 列表全量数据，由组件在前端过滤                       |
| `defaultActive` | `string \| number`                     | `''`         | 初始选中项对应的唯一值                               |
| `emptyText`     | `string`                               | `'暂无数据'` | 空列表和无搜索结果的提示                             |
| `props`         | `{ label?: keyof T; value?: keyof T }` | `{}`         | 字段映射，`label` 默认为 `name`，`value` 默认为 `id` |

插槽和事件：

| 名称              | 参数                                         | 说明                                                  |
| ----------------- | -------------------------------------------- | ----------------------------------------------------- |
| `row`             | `{ row: T, index: number, active: boolean }` | 自定义列表项主体；未提供时显示 label 字段             |
| `action`          | `{ row: T, index: number }`                  | 自定义普通行操作；仅在未提供 `action-dropdown` 时渲染 |
| `action-dropdown` | `{ row: T, index: number }`                  | 自定义点击型下拉菜单；使用组件内置 More 触发器        |
| `empty`           | 无                                           | 自定义空状态                                          |
| `click`           | `(row: T, index: number)`                    | 列表项点击事件                                        |

使用备注：

- `props.value` 对应的值应在列表中唯一，同时用于渲染 key 和选中判断。
- 默认搜索只匹配 `props.label` 对应字段，忽略大小写和关键词首尾空格。
- `data` 应传入全量数据；组件内的 50 条分批仅用于控制 DOM 渲染数量，不替代后端分页。
- 搜索词或数据源变化时，渲染范围和滚动位置会重置到第一批。
- 提供 `action-dropdown` 时，组件内部使用固定 More 按钮和点击型、非 Teleport 的
  `MkDropdown`。
- `action` 和 `action-dropdown` 二选一；同时提供时优先渲染 `action-dropdown`，不渲染 `action`。

#### 默认字段示例

不传 `props` 时，数据项默认使用 `name` 作为展示和搜索文本，使用 `id` 作为渲染 key
和选中值。未提供 `row` 插槽时，列表项直接显示 `name`。

```vue
<script setup lang="ts">
import { ref } from 'vue'
import MkSearchList from '@/components/mk-search-list/index.vue'

interface SearchListItem {
  id: string
  name: string
}

const searchKeyword = ref('')
const selectedItem = ref<SearchListItem>()
const selectedIndex = ref(-1)
const searchItems: SearchListItem[] = [
  { id: '1', name: '管理员' },
  { id: '2', name: '普通用户' },
]

function selectItem(item: SearchListItem, index: number) {
  selectedItem.value = item
  selectedIndex.value = index
}
</script>

<MkSearchList v-model="searchKeyword" :data="searchItems" default-active="2" @click="selectItem" />
```

上例中：

- 搜索词匹配 `name`。
- `id === '2'` 的“普通用户”初始显示为选中状态。
- 点击后 `click` 返回完整数据项和当前索引。
- 超过 50 条时首次只渲染 50 条，滚动到底部再追加 50 条。

#### 自定义字段与操作区示例

业务数据不使用 `name/id` 时，通过 `props.label` 和 `props.value` 指定替代字段。

```vue
<MkSearchList
  v-model="searchKeyword"
  :data="workspaces"
  :props="{ label: 'displayName', value: 'workspaceId' }"
  @click="selectWorkspace"
>
  <template #row="{ row: workspace, active }">
    <span :class="{ 'font-medium': active }">{{ workspace.displayName }}</span>
  </template>
  <template #action-dropdown="{ row: workspace }">
    <MkDropdownMenu>
      <MkDropdownItem @click="editWorkspace(workspace)">
        编辑 {{ workspace.displayName }}
      </MkDropdownItem>
    </MkDropdownMenu>
  </template>
</MkSearchList>
```

上例中，搜索匹配 `displayName`，`workspaceId` 用于 key 和选中判断。`row` 负责
自定义主体内容，`action-dropdown` 负责每行的下拉菜单内容，由组件显示固定 More 按钮。
`props` 中未传的字段保留默认值，例如只传
`:props="{ label: 'title' }"` 时，唯一值字段仍为 `id`。

### MkWorkspaceDropdown

统一工作空间下拉框的图标和触发器布局。通过 `options` 传入工作空间选项，通过 `v-model`
控制选中值，选择后通过 `select` 返回完整选项。组件不读取 Store，也不执行导航；路由切换和
数据刷新由使用方处理。

```vue
<script setup lang="ts">
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
</script>

<MkWorkspaceDropdown
  v-model="selectedWorkspaceId"
  :options="workspaceOptions"
  @select="handleWorkspaceSelect"
/>
```

### MkWorkspaceRelationTags

用于展示标签组，并在悬浮表格中展示每个标签关联的工作空间。
`tags` 控制表格单元格中的折叠标签；`tagWorkspace` 使用标签名称作为键、工作空间
名称数组作为值；`tableRenderParams.property` 和 `tableRenderParams.value` 分别设置
悬浮表格的标签列与工作空间列标题。组件位于非全局目录，使用时需要手动导入。

```vue
<script setup lang="ts">
import MkWorkspaceRelationTags from '@/components/mk-workspace-relation-tags/index.vue'
</script>

<MkWorkspaceRelationTags
  :table-render-params="{ property: '角色', value: '工作空间' }"
  :tags="user.role_name"
  :tag-workspace="user.role_workspace"
/>
```

## 新增公共组件

1. 根据使用范围选择 `global`、`components` 直属目录或所属功能目录。
2. 在 `<component-name>/index.vue` 创建组件，并声明多单词组件名。
3. 使用类型化 Props、Emits 和 Slots。
4. `global` 组件在模板中直接使用；其他共享组件由使用方从具体路径导入。
5. 更新本文档中的目录树和组件说明。
6. 通过正常开发或构建流程刷新自动生成的组件声明。
7. 运行 ESLint、类型检查以及受影响入口的生产构建。
