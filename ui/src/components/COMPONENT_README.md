# components 目录说明

本文档是项目公共组件规则的唯一依据。新增、修改、移动或使用公共组件前，应先阅读本文档。

`src/components` 存放跨页面或跨业务模块复用的 UI 组件与业务组件。仅在单个功能内使用的组件，
应放在对应的 `views/<feature>/components` 中。

## 组件选型

按以下顺序选择组件：

1. 首先检查 `src/components/global`，优先使用全局自动注册的 Mk 封装组件。
2. 涉及固定跨页面业务时，检查 `src/components/business` 中手动导入的业务组件。
3. 以上组件无法满足时，检查 `src/components` 直属目录中手动导入的共享 UI 组件。
4. 没有对应 Mk 组件时，再使用 Element Plus 现成组件。
5. 通过 Props、事件、插槽、公开方法、Tailwind class 或必要的样式覆盖适配设计稿。
6. 现有组件无法满足必要的结构或行为时，再新增自定义组件。

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
├── business/                     # 跨页面复用的业务组件，不使用 Mk 前缀
│   ├── folder-tree/              # Workspace 文件夹虚拟树及固定 CRUD 业务
│   │   ├── index.vue
│   │   ├── FolderFormDialog.vue
│   │   ├── MoveToDialog.vue
│   │   ├── VirtualizedTree.vue
│   │   └── types.ts
│   ├── model-select/
│   │   └── index.vue             # 按供应商分组的模型选择器
│   ├── workspace-dropdown/
│   │   └── index.vue             # 工作空间选择下拉框
│   └── workspace-relation-tags/
│       └── index.vue             # 标签及关联工作空间展示
├── global/                       # 高频、稳定的基础组件，自动注册
│   ├── mk-complex-search/
│   │   └── index.vue             # 字段选择与输入或枚举条件组合搜索框
│   ├── mk-collapse/
│   │   └── index.vue             # 带标题和过渡动画的折叠内容区
│   ├── mk-dialog/
│   │   └── index.vue             # 统一对话框关闭行为和内容滚动布局
│   ├── mk-dropdown/
│   │   ├── index.vue             # 下拉容器
│   │   ├── mk-dropdown-menu.vue  # 下拉菜单容器
│   │   └── mk-dropdown-item.vue  # 菜单项布局和选中状态
│   ├── mk-drawer/
│   │   └── index.vue             # 统一抽屉关闭行为和内容滚动布局
│   ├── mk-empty/
│   │   └── index.vue             # 普通无数据与搜索无匹配的统一空状态
│   ├── mk-filterable-dropdown/
│   │   └── index.vue             # 带搜索过滤和滚动列表的下拉选择
│   ├── mk-icon/
│   │   └── index.vue             # SVG Symbol 与 Element Plus 图标统一入口
│   ├── mk-infinite-scroll/
│   │   └── index.vue             # 分页列表滚动触底加载与结束状态
│   ├── mk-list-item/
│   │   └── index.vue             # 列表与业务分组列表复用的行结构
│   ├── mk-view-layout/
│   │   ├── index.vue             # 路由页面标题、操作区和内容区统一结构
│   │   ├── layout-batch-footer.vue # 页面与表格共用的批量选择底栏
│   │   └── layout-aside.vue      # 页面可选左侧栏结构
│   ├── mk-search-input/
│   │   └── index.vue             # 带默认搜索图标的输入框
│   ├── mk-status-label/
│   │   └── index.vue             # 布尔状态图标和文案
│   ├── mk-table/
│   │   ├── index.vue             # 表格、分页、列宽拖拽和批量操作
│   │   ├── mk-table-filter.vue   # 表头多选筛选器
│   │   └── mk-table-more-dropdown.vue # 表格操作列 More 下拉菜单
│   └── mk-tag-group/
│       └── index.vue             # 标签折叠和剩余标签浮层
├── mk-date-range/
│   ├── index.vue                 # 日期预设与自定义日期区间组合筛选器，手动导入
│   └── types.ts                  # 日期筛选结果类型
├── mk-drag-upload/
│   └── index.vue                 # 拖拽上传与已选文件卡片，手动导入
├── mk-dynamics-form/
│   ├── index.ts                  # 动态表单、表单配置器及组件内类型的公开入口
│   ├── index.vue                 # 根据字段配置渲染和校验动态表单
│   ├── type.ts                   # 组件内部及调用方共享的字段配置类型
│   ├── enums.ts                  # 字段类型和显隐比较选项
│   ├── FormItem.vue              # 字段组件调度层，仅供组件内部使用
│   ├── items/                    # 运行时字段实现，仅供组件内部使用
│   └── constructor/              # 字段配置器、变量选择器及配置项实现
├── mk-search-list/
│   └── index.vue                 # 搜索框与剩余空间滚动列表，手动导入
├── mk-form-list/
│   └── index.vue                 # 可动态增删的表单行列表，手动导入
├── mk-logo/
│   ├── LogoFull.vue              # 带产品名称的完整 Logo，手动导入
│   └── LogoIcon.vue              # 不带产品名称的图形 Logo，手动导入
├── codemirror-editor/
│   ├── python.vue                # 内置 pylint 诊断和全屏编辑的 Python 编辑器
│   └── Json.vue                  # 支持格式化、语法诊断和全屏编辑的 JSON 输入框
└── mk-source-card/
│   ├── index.vue                 # 来源资源的统一卡片结构，手动导入
│   ├── mk-source-card-action.vue # 卡片悬浮操作容器
│   └── mk-source-card-action-dropdown.vue # 卡片 More 下拉菜单
```

Vite 的 `unplugin-vue-components` 只扫描 `src/components/global`。该目录中的组件可以直接在
Vue 模板中使用，不需要手动导入。其他共享组件必须从具体文件路径导入：

```ts
import MkSearchList from '@/components/mk-search-list/index.vue'
import MkFormList from '@/components/mk-form-list/index.vue'
import MkDateRange from '@/components/mk-date-range/index.vue'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { MkDynamicsForm, MkDynamicsFormConstructor } from '@/components/mk-dynamics-form'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import LogoIcon from '@/components/mk-logo/LogoIcon.vue'
import PythonCodeEditor from '@/components/codemirror-editor/python.vue'
import JsonInput from '@/components/codemirror-editor/Json.vue'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import FolderTree from '@/components/business/folder-tree/index.vue'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import ModelSelect from '@/components/business/model-select/index.vue'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import WorkspaceRelationTags from '@/components/business/workspace-relation-tags/index.vue'
```

自动注册只适用于 Vue 模板。脚本中的类型、常量和 Element Plus 图标仍需显式导入。自动生成
的声明位于 `src/components.d.ts`，不要手动修改；通过开发服务、类型检查或生产构建刷新。

## 组件约定

- 高频、稳定、跨多数页面使用的基础组件放入 `global`。
- 跨页面复用且依赖业务类型、固定业务接口或领域交互的组件放入 `business/<component-name>`，
  由使用方手动导入。业务组件不使用 `Mk` 前缀，也不再按 Workspace 等上级领域增加额外目录。
- 不依赖固定业务的共享组合 UI 组件放在 `components/<component-name>`，由使用方手动导入。
- 一个公共组件默认使用一个 kebab-case 目录，入口统一为 `index.vue`；`codemirror-editor` 按语言
  提供 `python.vue` 和 `Json.vue` 两个专用入口，`mk-logo` 按完整 Logo 与图形 Logo 提供
  `LogoFull.vue` 和 `LogoIcon.vue` 两个专用入口。
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

### MkCollapse

带标题触发器和展开过渡动画的内容折叠组件。组件内部维护展开状态，`default-expanded` 设置初始
状态且默认为 `true`；点击标题行会切换状态，不向外回传展开状态。默认插槽放置折叠内容，标题
默认使用 `title` 属性，也可通过 `label` 插槽自定义；标题触发层可通过 `trigger-class` 和
`trigger-style` 自定义 class 和行内样式。指示图标默认显示在标题前，通过
`indicator-position="after"` 可改为显示在标题后的线性上、下箭头。

```vue
<MkCollapse title="系统管理员">
  <div>折叠内容</div>
</MkCollapse>

<MkCollapse :default-expanded="false" trigger-class="rounded-md bg-gray-50">
  <template #label>
    <strong>自定义标题</strong>
  </template>
  <div>折叠内容</div>
</MkCollapse>

<MkCollapse indicator-position="after">
  <template #label><h6>高级设置</h6></template>
  <div>高级设置内容</div>
</MkCollapse>
```

### MkEmpty

全局空状态组件，基于 `el-empty` 统一图片和默认文案。`type` 默认为 `default`，展示“暂无数据”；
搜索无匹配时使用 `type="search"`。可通过 `description`、`image`、`image-size` 覆盖默认内容，
其余 Element Plus Empty 属性通过 `$attrs` 透传，默认、`image` 和 `description` 插槽保持可用。

```vue
<MkEmpty />
<MkEmpty type="search" />
```

### MkDialog

全局对话框组件，Header 高度统一为 `60px`，使用 `el-scrollbar` 包裹内容并为默认插槽提供 `p-6`
内边距。默认显示关闭按钮、关闭时销毁内容，同时禁止点击遮罩或按 Escape 关闭；这些默认行为可以
通过同名 Props 覆盖。Element Plus Dialog 的其他属性和事件通过 `$attrs` 透传，`header`、
`subtitle`、默认和 `footer` 插槽保持可用。`subtitle` 位于标题下方的 Header 区域，并统一使用
`mt-2 text-N600` 样式；仅使用 `subtitle` 时，组件仍会按照 Element Plus 原生的标题 ID 和样式类
渲染 `title`。内容区域超出最大高度后显示滚动条。

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

全局抽屉组件，默认通过 Element Plus 的 `append-to-body` 挂载到 `body`，避免受到父级容器的定位、
层级和隐藏状态影响；统一使用 `el-scrollbar` 包裹内容并为默认插槽提供 `p-6` 内边距。通过
`content-class` 可以覆盖内容容器样式；全高布局可传入 `content-class="h-full p-0"`，再由
`MkViewLayout` 管理内边距和滚动区域。默认显示关闭按钮、关闭时销毁内容，同时禁止点击遮罩或按
Escape 关闭；这些默认行为可以通过同名 Props 覆盖。Element Plus Drawer 的其他属性和事件通过
`$attrs` 透传，`header`、默认和 `footer` 插槽保持可用。

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
显示浮层；取消、提交成功或其他关闭操作通常直接将 `v-model` 绑定的可见状态设为 `false`。当浮层
只负责收集数据，而提交数据的接收校验或异步请求由父组件负责时，可以向父组件暴露 `close()`，由
父组件在数据接收或请求成功后关闭浮层，校验拒绝或请求失败时保持浮层打开。组件统一监听 `closed`
调用 `resetData()`，确保所有关闭路径都在关闭动画结束后完成清理。`resetData()` 应统一重置表单、
提交状态、临时选项和表单校验，不把清理逻辑散落在 `open()`、取消按钮或提交成功回调中。

### MkComplexSearch

用于在多个字段之间切换搜索条件。`fields` 中的基础字段使用 `@/api/types` 中的
`OptionItem<string>`；字段包含 `options` 时使用下拉选择，否则使用文本输入。选项字段配置
`remoteMethod` 后自动启用远程搜索，并由该方法异步加载当前字段的选项。输入或选择完成时，`change` 返回
`{ [field]: value }`；选项字段配置 `multiple: true` 时启用多选并返回值数组。切换字段或清空条件时
返回 `undefined`。

```vue
<MkComplexSearch
  :fields="[
    { label: '用户名', value: 'username' },
    {
      label: '状态',
      value: 'enabled',
      multiple: true,
      options: [
        { label: '启用', value: true },
        { label: '禁用', value: false },
      ],
    },
  ]"
  @change="loadUsers($event)"
/>

<MkComplexSearch
  :fields="[
    { label: '名称', value: 'name' },
    { label: '创建者', value: 'create_user', options: creatorOptions, remoteMethod: loadCreatorOptions },
  ]"
  @change="loadResources($event)"
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
<MkFilterableDropdown v-model="selectedWorkspaceId" :options="workspaces" :props="{ label: 'name', value: 'id' }" @select="handleWorkspaceSelect">
  <template #default="{ text }">
    <button type="button">{{ text }}</button>
  </template>
  <template #option="{ option }">
    <span class="truncate" :title="option.name">{{ option.name }}</span>
  </template>
</MkFilterableDropdown>
```

### MkViewLayout

路由页面及全高浮层的通用内容结构，统一提供满高弹性布局及可选左侧栏。标题优先使用 `title`
Prop，未传入时读取当前路由的 `meta.title`；显式传入 `title=""` 可隐藏默认标题。`aside`
作用域插槽提供 `title` 和对应区域的 `Header` 包装组件，
默认作用域插槽另外提供主内容区的 `Footer` 包装组件；插槽未渲染 `Header` 时，组件会自动显示当前
标题，页面需要添加操作区或自定义标题时再显式渲染 `Header`。Header 固定在主内容区顶部，其余
默认插槽内容由组件统一放入
`el-scrollbar`，页面不要再为整个主内容区嵌套滚动容器；Tabs、树或其他局部区域需要独立滚动时
仍可自行使用 `el-scrollbar`。渲染 `Footer` 后固定在主内容区底部，不占用左侧栏空间，适合放置页面
或全高 Drawer 右侧内容的操作按钮。页面可以在同一个插槽中组织标题、内容、底栏和空状态，并只写
一次业务状态判断。传入 `aside` 插槽后才会渲染左侧栏；左右结构上方的独立内容放入 `top` 插槽。
页面加载状态通过 `loading` Prop 传入，由组件将 Element Plus Loading 遮罩绑定到整个布局根节点。
主内容区滚动时通过 `scroll` 事件返回 `scrollTop` 和 `scrollLeft`；需要由分类导航等外部交互定位
主内容时，通过组件 Ref 调用公开的 `setScrollTop()`。`getScrollContainer()` 返回主内容区实际滚动
元素，可传给 `el-anchor` 等需要显式滚动容器的组件。
默认插槽没有渲染 `Header` 时会自动显示当前标题；显式渲染后则由页面控制标题内容。`collapsible`
默认为 `false`；传入后，展开状态仅在鼠标移入侧栏或焦点进入侧栏时显示收起按钮，收起状态始终显示
展开按钮。收起时释放侧栏宽度，页面不需要自行维护折叠状态。

主内容区固定保留 `px-6` 水平留白。内置滚动容器会抵消两侧留白，再为滚动内容补回 `24px`
水平间距，使滚动条贴齐主区域右边界，并允许 `MkTable` 的底部操作栏延伸至完整主区域宽度。

卡片等非表格列表需要批量操作时，页面在批量选择模式下渲染 `Footer`，通过
`v-model:batch-selection` 绑定选中项唯一值数组，`batch-values` 传入当前列表全部唯一值，并提供
`footer-batch-actions` 插槽中的业务按钮；布局会复用 `LayoutBatchFooter`，统一显示全选、半选、
已选数量和取消按钮。点击取消会清空选择，并由 `Footer` 触发 `batch-cancel`。未提供
`footer-batch-actions` 时，`Footer` 仍渲染普通底栏。`footer-batch-actions` 作用域同时提供
`batchSelection`，业务按钮需要当前选择时可以直接读取。

```vue
<MkViewLayout :loading="loading" collapsible>
  <template #aside>左侧列表</template>
  <template #default>右侧内容</template>
</MkViewLayout>

<MkViewLayout :loading="loading">
  <template #aside="{ title, Header }">
    <component :is="Header">
      <h4>{{ title }}</h4>
      <el-button text type="primary">创建</el-button>
    </component>
    左侧列表
  </template>
  <template #default="{ title, Footer, Header }">
    <template v-if="selectedItem">
      <component :is="Header">
        <h4>{{ title }}</h4>
      </component>
      右侧内容
      <component :is="Footer">
        <el-button>取消</el-button>
        <el-button type="primary">保存</el-button>
      </component>
    </template>
    <MkEmpty v-else />
  </template>
</MkViewLayout>
```

```vue
<MkViewLayout>
  <template #default="{ Footer }">
    <ResourceCard
      v-for="resource in resources"
      :key="resource.id"
      :selectable="batchSelectionMode"
      :selected="selectedResourceIds.includes(resource.id)"
    />

    <component
      :is="Footer"
      v-if="batchSelectionMode"
      v-model:batch-selection="selectedResourceIds"
      :batch-values="resourceIds"
      @batch-cancel="batchSelectionMode = false"
    >
      <template #footer-batch-actions="{ batchSelection }">
        <el-button type="primary" plain>移动到</el-button>
        <el-button type="danger" plain :disabled="!batchSelection.length">删除</el-button>
      </template>
    </component>
  </template>
</MkViewLayout>
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
<MkIcon name="icon_left_outlined" class="text-danger!" />
<MkIcon name="icon_home_filled" gradient />
<MkIcon :icon="Setting" :size="20" />
```

### MkInfiniteScroll

分页列表的滚动触底加载组件，使用 `IntersectionObserver` 监听组件所在滚动区域的底部，不依赖
Element Plus 的 `v-infinite-scroll`。组件通过 `v-model` 管理已经加载的列表数据，通过 `load`
传入按页请求方法，并在内部管理页码、首次加载、数据追加、加载状态、结束状态和过期请求。请求
方法接收 `{ currentPage, pageSize }`，返回包含 `records`、`current`、`size` 和 `total` 的分页结果。
默认每页加载 20 条，可通过 `pageSize` 修改。组件挂载后自动加载第一页，之后只在底部哨兵随
用户滚动进入可视区域时加载下一页。查询条件变化时通过组件暴露的 `reset()` 重新加载。

```vue
<MkInfiniteScroll ref="infiniteScrollRef" v-model="resources" :load="loadResourcePage">
  <ResourceCard v-for="resource in resources" :key="resource.id" :resource="resource" />
</MkInfiniteScroll>
```

### MkListItem

提供列表行的统一间距、悬停状态、选中状态和可选操作区。仅自定义默认插槽时，可以只传
`active` 并监听 `click`；不需要补充无实际用途的 `row`、`label-field` 或 `index`。

```vue
<MkListItem :active="active" @click="handleSelect()">
  <MkIcon name="icon_assigned_outlined" :size="20" />
  <span>共享模型</span>
</MkListItem>
```

数据驱动使用时传入 `row`。`label-field` 默认读取 `name`，`index` 默认为 `0`；未提供默认插槽时
组件显示对应字段文本。`action` 和 `action-dropdown` 插槽需要配合 `row` 使用，并接收 `row`、
`index`。`action-dropdown` 由组件统一渲染 More 触发器、`MkDropdown` 和 `MkDropdownMenu`，插槽中
直接放置 `MkDropdownItem`；插槽为空，或其中的条件菜单项均未渲染时，不显示 More 触发器。

```vue
<MkListItem :active="currentRole?.id === role.id" :row="role" @click="selectRole(role)" />
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
const paginationConfig = ref({ currentPage: 1, pageSize: 20, pageSizes: [10, 20, 50, 100], total: 0 })
```

使用 `v-model:pagination-config` 接收页码和每页数量变化，也可以监听 `current-change` 和
`size-change`。切换每页数量时，组件会同时将 `currentPage` 重置为 `1`，页面只需在
`size-change` 中重新加载数据，不要重复修改页码。

```vue
<MkTable v-model:pagination-config="paginationConfig" :data="currentPageUsers" :max-table-height="280" resizable row-key="id">
  <el-table-column prop="name" label="姓名" />
</MkTable>
```

`maxTableHeight` 表示窗口中除表格外需要扣除的高度，默认为 `250`；组件会在窗口尺寸变化时
重新计算 `max-height`。传入 `resizable` 后启用列宽拖拽，并隐藏为拖拽借用的原生边框视觉。
`resizable` 采用白名单式启用：只有需求明确指定的页面级表格才能开启；未明确指定的表格，以及
Dialog、Drawer、Popover、嵌套区域等其他大、小表格均禁止开启。

传入 `size="small"` 时，组件会为内部 `el-table` 添加 `small` class；组件仅提供该样式钩子，
不内置对应样式。

表头需要多选筛选时使用 `MkTableFilter`。`label` 设置表头文案，`options` 接收
`OptionItem<string>[]`，`v-model` 绑定已选值；初始不选择任何选项，确认或重置后通过 `change`
返回筛选值。过长的选项文案会显示省略号，悬停时可查看完整文案。

```vue
<el-table-column prop="menu" min-width="140">
  <template #header>
    <MkTableFilter
      v-model="selectedMenus"
      label="操作菜单"
      :options="menuOptions"
      @change="loadRecords()"
    />
  </template>
</el-table-column>
```

表格操作列需要 More 菜单时使用 `MkTableMoreDropdown`。组件统一提供点击型、右下定位的 More
按钮以及 `MkDropdownMenu`，默认插槽中直接放置 `MkDropdownItem`；插槽为空，或其中的条件菜单项
均未渲染时，不显示 More 触发器。其他 Dropdown 属性和事件通过 `$attrs` 传入，菜单容器样式通过
`menu-class` 设置。

```vue
<MkTableMoreDropdown menu-class="w-40">
  <MkDropdownItem>配额设置</MkDropdownItem>
  <MkDropdownItem divided @click="deleteUser(row)">删除</MkDropdownItem>
</MkTableMoreDropdown>
```

包含 `type="selection"` 的选择列时，选择数据会显示页面底部操作栏。批量按钮放入
`footer-batch-actions` 插槽，当前选择通过 `selection-change` 返回。组件暴露 `tableRef` 和
`clearSelection()`。操作栏与 `MkViewLayout` 复用 `LayoutBatchFooter`，统一全选、半选、数量和
取消行为；它在主内容滚动区域内吸附于页面底部，不随表格内容滚出可视区域。

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

### LogoFull、LogoIcon

`LogoFull` 展示带产品名称的完整 Logo，`LogoIcon` 展示不带产品名称的图形 Logo，使用时分别从
`@/components/mk-logo/LogoFull.vue` 和 `@/components/mk-logo/LogoIcon.vue` 显式导入。两个组件在
默认主题下展示内置蓝紫渐变 Logo，自定义主题下使用 Theme Store 中的当前主题色。`LogoFull`
还会优先展示 Theme Store 中配置的 `loginLogo`。两个组件都只接收可选的 `height`，其余主题与
Logo 数据统一从 Theme Store 获取。

```vue
<script setup lang="ts">
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import LogoIcon from '@/components/mk-logo/LogoIcon.vue'
</script>

<template>
  <LogoFull />
  <LogoFull height="36" />
  <LogoIcon class="h-8" />
</template>
```

### MkDateRange

组合日期预设下拉框和自定义日期区间选择器。默认显示“过去 7 天”，仅在用户修改筛选条件时通过
`change` 返回 `{ startTime, endTime }`；组件挂载时不主动触发 `change`。预设日期的 `endTime` 为
空字符串，自定义日期清空时两个字段均为空字符串。组件不绑定具体接口字段，使用方负责初始化
默认查询参数，并将筛选结果映射为业务查询参数。

```vue
<script setup lang="ts">
import { ref } from 'vue'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import { beforeDay } from '@/utils/time'

const dateQuery = ref({ start_time: beforeDay(7), end_time: '' })

function handleDateRangeChange({ startTime, endTime }: MkDateRangeValue) {
  dateQuery.value = { start_time: startTime, end_time: endTime }
  loadRecords()
}
</script>

<MkDateRange @change="handleDateRangeChange" />
```

### MkDragUpload

组合拖拽选择区和已选文件卡片，通过 `v-model` 管理 Element Plus `UploadUserFile[]`。`accept`
直接传给上传控件；`dragText`、`selectText`、`tipText` 和 `replaceText` 可替换展示文案。组件只负责
文件选择与展示，使用方通过 `change` 执行校验和上传，通过 `remove` 清理业务数据；`download`
作用域插槽提供当前文件，由使用方按业务需要放置下载按钮。组件暴露 `clearFiles()`，用于请求失败
或表单重置时清空上传控件内部状态。

```vue
<script setup lang="ts">
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
</script>

<MkDragUpload v-model="fileList" accept=".zip" tip-text="支持格式：ZIP，大小不超过 100 MB" @change="handleFileChange" @remove="handleFileRemove">
  <template #download="{ file }">
    <el-button link @click="handleDownload(file)">下载</el-button>
  </template>
</MkDragUpload>
```

### PythonCodeEditor

基于 CodeMirror 6 的 Python 代码编辑器，通过 `v-model` 管理代码，并在组件内部调用工具 pylint
接口生成诊断。组件最多展示 50 条诊断，并在代码停止输入 500ms 后检查。编辑器提供内置全屏
入口；全屏确认时更新 `v-model` 并触发 `submit-dialog`，`header-extra` 插槽用于添加全屏标题栏操作。

```vue
<script setup lang="ts">
import PythonCodeEditor from '@/components/codemirror-editor/python.vue'

const code = defineModel<string>({ required: true })
</script>

<PythonCodeEditor v-model="code" title="工具内容（Python）" />
```

### JsonInput

JSON 专用输入框，通过 `v-model` 接收并回传解析后的 JSON 值，内置 JSON 语法诊断、格式化和全屏
编辑。组件暴露 `validateRules`，可直接接入 Element Plus 表单自定义校验器；无法解析的输入不会
覆盖最后一次有效的 `v-model` 值。

```vue
<script setup lang="ts">
import JsonInput from '@/components/codemirror-editor/Json.vue'

const config = defineModel<unknown>({ required: true })
</script>

<JsonInput v-model="config" title="配置（JSON）" />
```

### MkSourceCard

用于模型、工具等带来源信息的等高资源卡片。`title` 提供默认标题，`nick_name` 和 `create_time`
提供固定样式的创建信息；`subtitle` 插槽也始终应用 `text-sm text-N600`。默认插槽放置资源详情，
`footer` 插槽作为左侧常驻内容并始终贴在卡片底部；无论是否传入内容，底部都会保留固定位置。
`footer` 作用域提供 `Action` 和 `ActionDropdown`。左侧常驻内容与 `Action` 写在同一个插槽内；
`Action` 是卡片悬浮或内部获得焦点时显示的右侧操作容器，可以只放开关或按钮。
需要 More 菜单时，再将 `ActionDropdown` 放入 `Action`，组件会统一渲染 `MkDropdownMenu`，默认
插槽中直接放置 `MkDropdownItem`；插槽为空，或其中的条件菜单项均未渲染时，不显示 More 触发器。
`ActionDropdown` 固定开启 `persistent`，避免菜单关闭后销毁由菜单项管理的 Drawer 或 Dialog；
浮层本身应在打开时按需挂载，并在 `closed` 后卸载，避免每张卡片都长期保留隐藏的浮层节点。
传入 `selectable` 后，卡片进入选择模式：复选框固定在右上角，`tag` 插槽仍正常渲染并为复选框
预留位置；点击卡片或复选框会通过 `selected` 事件返回新的选择状态，页面通过 `selected` Prop
传回当前状态，选中卡片统一显示主题色边框和浅色背景。业务内容需要在选择模式下由复选框替代时，
由业务卡片根据 `selectable` 控制该内容是否渲染；例如工具卡片选择时隐藏“更新版本”入口。
选择模式下，`MkSourceCard` 提供的 `Action` 不渲染任何内容，业务卡片不需要重复判断
`selectable`；选择集合、全选、批量接口和页面底部操作栏仍由使用页面管理。
需要自定义头部时可
通过 `icon`、`title`、`subtitle` 和 `tag` 插槽覆盖对应区域；`title` 插槽提供 `{ title }`，
便于在保留标题文案的同时追加状态图标等内容。

```vue
<script setup lang="ts">
import MkSourceCard from '@/components/mk-source-card/index.vue'
</script>

<MkSourceCard title="大语言模型" nick_name="管理员" create_time="2026-08-17">
  <template #icon><ProviderIcon /></template>
  <template #title="{ title }">
    <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
    <MkIcon name="icon_warning_filled" />
  </template>
  <ul>资源详情</ul>
  <template #footer="{ Action, ActionDropdown }">
    <span>左侧常驻内容</span>
    <component :is="Action">
      <el-switch size="small" />
      <component :is="ActionDropdown">
        <MkDropdownItem>编辑</MkDropdownItem>
        <MkDropdownItem>删除</MkDropdownItem>
      </component>
    </component>
  </template>
</MkSourceCard>
```

批量选择模式由页面显式控制：

```vue
<MkSourceCard :selectable="batchSelectionMode" :selected="selected" title="工作流工具" @selected="selected = $event">
  <p>工具描述</p>
</MkSourceCard>
```

只需要悬浮显示开关时，可以不使用 `ActionDropdown`：

```vue
<MkSourceCard title="大语言模型" nick_name="管理员" create_time="2026-08-17">
  <template #footer="{ Action }">
    <span>左侧常驻内容</span>
    <component :is="Action">
      <el-switch size="small" />
    </component>
  </template>
</MkSourceCard>
```

### MkFormList

用于多个业务字段组成的动态表单行，只负责重复行布局、添加和删除，不管理业务字段、校验规则或
选项请求。通过 `v-model` 传入行数据，`defaultItem` 创建新行，列表始终至少保留一行。默认插槽
提供 `item`、`index`，业务组件在插槽中继续声明
`el-form-item`、字段路径和校验规则。

```vue
<script setup lang="ts">
import MkFormList from '@/components/mk-form-list/index.vue'

const roleSettings = defineModel<{ roleId: string; workspaceIds: string[] }[]>({ required: true })
</script>

<MkFormList v-model="roleSettings" add-text="添加角色" :default-item="{ roleId: '', workspaceIds: [] }">
  <template #default="{ index, item }">
    <el-form-item
      class="flex-1"
      :label="index===0 ? '角色' : ''"
      :prop="`roleSettings.${index}.roleId`"
    >
      <el-select v-model="item.roleId" />
    </el-form-item>
  </template>
</MkFormList>
```

`addText` 设置添加按钮文案，`showAddButton` 默认为 `true`；添加入口由业务布局单独提供时传入
`:show-add-button="false"`。`firstRowHasLabel` 默认为 `true`：第一行删除按钮使用 `mt-8`，后续行
使用 `mt-0.5`；并列表单项没有 label 时传入 `:first-row-has-label="false"`。删除成功后通过
`remove(item, index)` 返回被删除的行数据和原索引，业务组件可处理关联状态，不需要再次修改列表。

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
  `MkDropdown`，并统一包裹 `MkDropdownMenu`；插槽中直接放置 `MkDropdownItem`，无可渲染菜单项时
  不显示 More 触发器。
- `action` 和 `action-dropdown` 二选一；同时提供且下拉插槽有可渲染菜单项时优先渲染
  `action-dropdown`，否则渲染 `action`。

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
<MkSearchList v-model="searchKeyword" :data="workspaces" :props="{ label: 'displayName', value: 'workspaceId' }" @click="selectWorkspace">
  <template #row="{ row: workspace, active }">
    <span :class="{ 'font-medium': active }">{{ workspace.displayName }}</span>
  </template>
  <template #action-dropdown="{ row: workspace }">
    <MkDropdownItem @click="editWorkspace(workspace)">
      编辑 {{ workspace.displayName }}
    </MkDropdownItem>
  </template>
</MkSearchList>
```

上例中，搜索匹配 `displayName`，`workspaceId` 用于 key 和选中判断。`row` 负责
自定义主体内容，`action-dropdown` 负责每行的下拉菜单内容，由组件显示固定 More 按钮。
`props` 中未传的字段保留默认值，例如只传
`:props="{ label: 'title' }"` 时，唯一值字段仍为 `id`。

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

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { Dict } from '@/api/types'
import { MkDynamicsForm, type DynamicFormValue, type FormField } from '@/components/mk-dynamics-form'

const formFields = ref<FormField[]>([])
const formValue = ref<Dict<DynamicFormValue>>({})
</script>

<template>
  <MkDynamicsForm v-model="formValue" :render-data="formFields" />
</template>
```

公开入口包含 `MkDynamicsForm`、`MkDynamicsFormConstructor`、`dynamicFormTypeOptions` 和组件专用类型。`FormItem.vue`、`items/`、`constructor/items/` 与
`constructor/visibility/` 均为内部实现，业务代码不应深层导入。

`MkDynamicsForm` 的主要 Props 为 `modelValue`、`renderData`、`otherParams`、`view`、
`defaultItemWidth` 和 `parentField`，公开 `validate()`、`render()`、`initDefaultData()` 与
`ruleFormRef`。`MkDynamicsFormConstructor` 接收 `modelValue`、`fieldTypeOptions`、
`enableVisibility` 和 `leftOptions`，其中 `leftOptions` 使用 `VisibilityFieldOption[]`；公开
`validate()`、`getData()` 与 `render()`。

字段配置中的动态校验器和表格行表达式属于受信任的服务端协议，只允许加载可信配置；普通业务
输入不得作为脚本传入。

## 跨页面业务组件

业务组件可以调用其固定业务 API，但应将通用展示部分拆成内部纯 UI 组件；页面继续负责资源列表
查询、路由跳转等所属页面业务。业务组件必须显式导入，不参与全局自动注册。

### FolderTree

Workspace 的文件夹虚拟树业务组件。组件根据当前资源上下文和 `source` 调用统一文件夹接口，负责
文件夹树查询、搜索、排序、创建、编辑、移动和删除。通过 `v-model` 控制当前文件夹 ID，首次加载
完成后通过 `loaded` 返回该 ID 对应的完整文件夹，选择文件夹时触发 `select`。传入的 ID 不存在时，
优先回退到“全部”入口，否则回退到首个可用文件夹。`showAll`、`showShared` 分别控制全部和共享入口，
`rootLabel` 可覆盖根入口文案，`disabledFolderIds` 用于只选场景中禁用指定节点。

```vue
<script setup lang="ts">
import { RESOURCE_TYPE } from '@/api/enums'
import FolderTree from '@/components/business/folder-tree/index.vue'
</script>

<FolderTree v-model="currentFolderId" :source="RESOURCE_TYPE.TOOL" draggable @loaded="handleFolderLoaded" @select="handleFolderSelect" />
```

页面顶部需要触发根目录创建时，通过页面语义处理方法调用组件暴露的 `openCreate()`；外部数据变化
后可调用 `refresh()` 重新加载文件夹树。`MoveToDialog.vue` 每次打开都会重新挂载内部 `FolderTree`，
加载最新目录并复用相同的搜索和排序能力。
`VirtualizedTree.vue` 基于 `@he-tree/vue` 的 `Draggable` 实现虚拟渲染和拖拽交互，只负责树 UI，
不调用 API；不要替换为 Element Plus `el-tree-v2`。

### MoveToDialog

可复用的文件夹移动对话框。传入资源 `source` 和请求状态 `loading`，通过组件 Ref 调用
`open(currentFolderId)`。对话框每次打开都会重新查询文件夹树，并复用 `FolderTree` 的搜索与排序；
确认后通过 `submit` 返回目标文件夹 ID，使用方自行维护待移动资源，完成请求后调用 `close()`
关闭弹窗。

```vue
<MoveToDialog ref="moveToDialogRef" :loading="submitting" :source="RESOURCE_TYPE.TOOL" @submit="handleMoveFolder" />
```

### ModelSelect

按供应商分组展示模型，通过 `v-model` 控制模型 ID，并在选择变化时触发 `change`。`options` 使用
供应商标识作为键、模型数组作为值；组件根据 `modelType` 调用供应商接口补充分组名称和图标，
模型列表仍由使用方按当前业务上下文查询。

```vue
<script setup lang="ts">
import ModelSelect from '@/components/business/model-select/index.vue'
</script>

<ModelSelect v-model="selectedModelId" model-type="LLM" :options="modelOptions" placeholder="请选择模型" @change="handleModelChange" />
```

### WorkspaceDropdown

统一工作空间下拉框的图标和触发器布局。通过 `options` 传入工作空间选项，通过 `v-model`
控制选中值，选择后通过 `select` 返回完整选项。组件不读取 Store，也不执行导航；路由切换和
数据刷新由使用方处理。

```vue
<script setup lang="ts">
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
</script>

<WorkspaceDropdown v-model="selectedWorkspaceId" :options="workspaceOptions" @select="handleWorkspaceSelect" />
```

### WorkspaceRelationTags

用于展示标签组，并在悬浮表格中展示每个标签关联的工作空间。
`tags` 控制表格单元格中的折叠标签；`tagWorkspace` 使用标签名称作为键、工作空间
名称数组作为值；`tableRenderParams.property` 和 `tableRenderParams.value` 分别设置
悬浮表格的标签列与工作空间列标题。组件位于非全局目录，使用时需要手动导入。

```vue
<script setup lang="ts">
import WorkspaceRelationTags from '@/components/business/workspace-relation-tags/index.vue'
</script>

<WorkspaceRelationTags :table-render-params="{ property: '角色', value: '工作空间' }" :tags="user.role_name" :tag-workspace="user.role_workspace" />
```

## 新增公共组件

1. 根据使用范围选择 `global`、`components` 直属目录、`components/business` 或所属功能目录。
2. 默认在 `<component-name>/index.vue` 创建组件并声明多单词组件名；已有多入口约定的目录按其
   专用入口文件组织。
3. 使用类型化 Props、Emits 和 Slots。
4. `global` 组件在模板中直接使用；其他共享组件由使用方从具体路径导入。
5. 更新本文档中的目录树和组件说明。
6. 通过正常开发或构建流程刷新自动生成的组件声明。
7. 运行 ESLint、类型检查以及受影响入口的生产构建。
