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
│   ├── mk-dropdown/
│   │   ├── index.vue             # 统一下拉菜单箭头和弹层间距
│   │   ├── mk-dropdown-menu.vue  # 统一下拉菜单容器
│   │   └── mk-dropdown-item.vue  # 统一菜单项图标、内容和选中状态布局
│   └── mk-icon/
│       └── index.vue         # MaxKB SVG Symbol 与 Element Plus 图标统一入口
├── mk-filterable-dropdown/   # 带搜索过滤和滚动列表的下拉框，使用方手动导入
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
- 组件样式默认使用 `scoped`；只有明确的全局规则才放入 `src/styles`。
- `global` 组件不要创建只用于二次导出的 `components/index.ts`，模板组件由自动注册插件解析。
- 除 `global` 外的共享组件必须从具体路径手动导入，让依赖关系在使用文件中可见。

## MkFilterableDropdown

`MkFilterableDropdown` 是带搜索过滤和滚动列表的低频共享下拉框，需要从
`@/components/mk-filterable-dropdown/index.vue` 手动导入。触发器通过默认插槽传入；菜单项
需要自定义图片、图标或其他业务内容时，使用 `option` 作用域插槽并通过当前 `option` 渲染。
未传入 `option` 插槽时默认显示 `option.label`。

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

`MkIcon` 统一承载 MaxKB SVG Symbol 和 Element Plus 图标。未传入 `size` 时默认使用 `16px`；传入 `size` 时覆盖默认值。`size`、`color` 的其他行为与 `el-icon` 保持一致。

### MaxKB SVG Symbol

通过完整的 Symbol ID 引用：

```vue
<MkIcon name="icon_left_outlined" />
<MkIcon name="icon_start_outlined" :size="20" color="#3370ff" />
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
- `size` 默认为 `16px`，仅在需要其他尺寸时显式传入。
- MaxKB 图标使用 `name`，Element Plus 图标组件使用 `icon`。
- 不直接使用 Unicode、Font Class 或裸 `<svg><use>`。
- 更新图标时直接覆盖 `src/assets/iconfont.js`。
- 保持 Symbol ID 稳定；ID 变化时必须同步修改所有对应的 `MkIcon name`。

## 新增公共组件

1. 根据使用范围选择 `global`、`components` 直属组件目录或所属功能目录。
2. 在对应目录的 `<component-name>/index.vue` 创建组件。
3. 使用类型化 Props、Emits 和 Slots。
4. `global` 组件在模板中直接使用；其他共享组件和功能组件由使用方手动导入。
5. 运行类型检查及两个入口的生产构建。
6. 如果新增了通用约定或调整目录结构，同步更新本文件。
