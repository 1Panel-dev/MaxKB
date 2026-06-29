# MaxKB UI 全面改版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 MaxKB 平台的 UI 从渐变蓝紫色风格全面改版为 macOS/iOS 风格的毛玻璃现代设计，支持亮色/暗色模式切换。

**Architecture:** 通过 CSS 变量驱动 + Element Plus 覆盖增强的方式实现。在现有 SCSS 架构上扩展毛玻璃 tokens、暗色变量和动效 mixins，逐步替换导航栏、侧边栏、登录页和首页的样式。

**Tech Stack:** Vue 3, Element Plus, SCSS, Pinia, `use-element-plus-theme`, CSS `backdrop-filter`

## Global Constraints

- 主色调：浪潮蓝 `#1A6DFF`（替换原 `#3370FF`）
- Logo 文件：`ui/src/assets/logo/logo.png`
- 暗色模式通过 `[data-theme="dark"]` 属性选择器实现
- 毛玻璃效果使用 `backdrop-filter: blur()` 实现
- 保持 Element Plus 组件兼容性
- 首页作为样板页先行验证

---

## Task 1: 更新 CSS 变量与设计令牌

**Files:**
- Modify: `ui/src/styles/variables.scss`

**Interfaces:**
- Consumes: 无（基础任务）
- Produces: 所有后续任务依赖的 CSS 自定义属性

- [ ] **Step 1: 重写 variables.scss，定义完整的设计令牌系统**

替换 `ui/src/styles/variables.scss` 的全部内容：

```scss
:root {
  --app-base-px: 8px;

  /* ===== 主色色阶 ===== */
  --primary-50: #E8F0FE;
  --primary-100: #C5D9FC;
  --primary-200: #93B8F9;
  --primary-300: #6097F6;
  --primary-400: #3D7DF3;
  --primary-500: #1A6DFF;
  --primary-600: #1558D9;
  --primary-700: #0F43B3;

  /* ===== 背景色（亮色模式） ===== */
  --bg-glass-nav: rgba(255, 255, 255, 0.72);
  --bg-glass-sidebar: rgba(255, 255, 255, 0.56);
  --bg-content: #F5F7FA;
  --bg-card: rgba(255, 255, 255, 0.8);
  --bg-card-solid: #ffffff;
  --bg-hover: rgba(0, 0, 0, 0.04);

  /* ===== 文字色 ===== */
  --text-primary: #1D2129;
  --text-secondary: #4E5969;
  --text-disabled: #C9CDD4;
  --text-placeholder: #8F959E;

  /* ===== 边框 ===== */
  --border-color: rgba(0, 0, 0, 0.08);
  --border-color-light: rgba(0, 0, 0, 0.04);

  /* ===== 毛玻璃参数 ===== */
  --blur-nav: blur(20px);
  --blur-sidebar: blur(16px);
  --blur-card: blur(12px);
  --blur-dropdown: blur(20px);
  --blur-overlay: blur(4px);

  /* ===== 阴影 ===== */
  --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.04);
  --shadow-card-hover: 0 4px 20px rgba(0, 0, 0, 0.08);
  --shadow-dropdown: 0 8px 32px rgba(0, 0, 0, 0.12);
  --shadow-dialog: 0 16px 48px rgba(0, 0, 0, 0.16);

  /* ===== 圆角 ===== */
  --app-border-radius-small: 6px;
  --app-border-radius-base: 8px;
  --app-border-radius-large: 12px;
  --app-border-radius-xlarge: 16px;

  /* ===== 布局 ===== */
  --app-layout-bg-color: var(--bg-content);
  --app-view-bg-color: var(--bg-card-solid);
  --app-view-padding: 24px;
  --app-header-height: 64px;
  --app-header-padding: 0 24px;
  --sidebar-width: 240px;
  --app-main-height: calc(100vh - var(--app-header-height) - var(--app-view-padding) * 2 - 40px);

  /* ===== 文字色（兼容旧变量） ===== */
  --app-text-color-secondary: var(--text-secondary);
  --app-text-color-disable: var(--text-disabled);
  --app-input-color-placeholder: var(--text-placeholder);
  --app-border-color-dark: var(--text-disabled);

  /* ===== Tag ===== */
  --tag-default-bg: rgba(26, 109, 255, 0.12);
  --tag-default-color: #1A6DFF;
  --tag-success-bg: rgba(52, 199, 36, 0.12);
  --tag-success-color: #2CA91F;
  --tag-warning-bg: rgba(255, 136, 0, 0.12);
  --tag-warning-color: #D97400;
  --tag-danger-bg: rgba(245, 74, 69, 0.12);

  /* ===== Card ===== */
  --card-width: 330px;
  --card-min-height: 166px;
  --card-min-width: 220px;

  /* ===== AI Chat ===== */
  --dialog-bg-gradient-color:
    linear-gradient(188deg, rgba(232, 240, 254, 0.2) 39.6%, rgba(197, 217, 252, 0.2) 94.3%), #eff0f1;

  /* ===== 资源授权 ===== */
  --setting-left-width: 280px;

  /* ===== 过渡 ===== */
  --transition-base: all 0.2s ease;
  --transition-slow: all 0.3s ease-out;
}

/* ===== 暗色模式 ===== */
[data-theme="dark"] {
  --primary-50: rgba(26, 109, 255, 0.16);
  --primary-100: rgba(26, 109, 255, 0.24);
  --primary-200: rgba(26, 109, 255, 0.32);
  --primary-300: #5A94F5;
  --primary-400: #5A94F5;
  --primary-500: #3D85FF;
  --primary-600: #5A94F5;
  --primary-700: #7AAAFF;

  --bg-glass-nav: rgba(30, 30, 30, 0.72);
  --bg-glass-sidebar: rgba(30, 30, 30, 0.56);
  --bg-content: #1E1E1E;
  --bg-card: rgba(44, 44, 46, 0.8);
  --bg-card-solid: #2C2C2E;
  --bg-hover: rgba(255, 255, 255, 0.08);

  --text-primary: #E5E6EB;
  --text-secondary: #A6A6A6;
  --text-disabled: #4E4E4E;
  --text-placeholder: #6B6B6B;

  --border-color: rgba(255, 255, 255, 0.1);
  --border-color-light: rgba(255, 255, 255, 0.06);

  --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.2);
  --shadow-card-hover: 0 4px 20px rgba(0, 0, 0, 0.32);
  --shadow-dropdown: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-dialog: 0 16px 48px rgba(0, 0, 0, 0.5);

  --app-layout-bg-color: var(--bg-content);
  --app-view-bg-color: var(--bg-card-solid);

  --tag-default-bg: rgba(61, 133, 255, 0.2);
  --tag-default-color: #5A94F5;

  --dialog-bg-gradient-color:
    linear-gradient(188deg, rgba(26, 109, 255, 0.08) 39.6%, rgba(44, 44, 46, 0.8) 94.3%), #2C2C2E;
}
```

- [ ] **Step 2: 验证变量系统无语法错误**

运行 SCSS 编译检查：

```bash
cd ui && npx sass --no-source-map --load-path=src src/styles/variables.scss /dev/null 2>&1 | head -20
```

Expected: 无错误输出或仅 deprecation warnings（非 error）

- [ ] **Step 3: Commit**

```bash
git add ui/src/styles/variables.scss
git commit -m "feat(ui): redefine design tokens for glassmorphism UI redesign

Replace all CSS custom properties with new glassmorphism-focused tokens:
- Inspur blue primary color scale (#1A6DFF)
- Glass background tokens with rgba transparency
- Dark mode variables via [data-theme=\"dark\"]
- Updated shadows, border-radius, transitions"
```

---

## Task 2: 新增毛玻璃 SCSS Mixins

**Files:**
- Create: `ui/src/styles/mixins.scss`
- Modify: `ui/src/styles/index.scss`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: `@mixin glass-nav`, `@mixin glass-sidebar`, `@mixin glass-card`, `@mixin glass-dropdown`, `@mixin glass-enter-animation`, `@mixin card-hover` 供后续任务使用

- [ ] **Step 1: 创建 mixins.scss 文件**

创建 `ui/src/styles/mixins.scss`：

```scss
// 毛玻璃导航栏
@mixin glass-nav {
  background: var(--bg-glass-nav);
  backdrop-filter: var(--blur-nav);
  -webkit-backdrop-filter: var(--blur-nav);
  border-bottom: 1px solid var(--border-color-light);
}

// 毛玻璃侧边栏
@mixin glass-sidebar {
  background: var(--bg-glass-sidebar);
  backdrop-filter: var(--blur-sidebar);
  -webkit-backdrop-filter: var(--blur-sidebar);
}

// 毛玻璃卡片
@mixin glass-card {
  background: var(--bg-card);
  backdrop-filter: var(--blur-card);
  -webkit-backdrop-filter: var(--blur-card);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: var(--app-border-radius-large);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

// 毛玻璃下拉菜单
@mixin glass-dropdown {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: var(--blur-dropdown);
  -webkit-backdrop-filter: var(--blur-dropdown);
  border-radius: var(--app-border-radius-large);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: var(--shadow-dropdown);
}

// 卡片 hover 效果
@mixin card-hover {
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
  &:active {
    transform: scale(0.98);
  }
}

// 毛玻璃进场动画
@mixin glass-enter-animation {
  animation: glass-enter 0.5s ease-out;
}

@keyframes glass-enter {
  from {
    backdrop-filter: blur(0);
    -webkit-backdrop-filter: blur(0);
  }
  to {
    backdrop-filter: var(--blur-nav);
    -webkit-backdrop-filter: var(--blur-nav);
  }
}

// 列表项逐项入场动画
@mixin list-item-enter($delay-step: 50ms) {
  @for $i from 1 through 20 {
    &:nth-child(#{$i}) {
      animation-delay: #{$delay-step * ($i - 1)};
    }
  }
  animation: list-item-enter 0.3s ease-out both;
}

@keyframes list-item-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 暗色模式下的 dropdown 覆盖
[data-theme="dark"] {
  .glass-dropdown {
    background: rgba(44, 44, 46, 0.88);
    border-color: rgba(255, 255, 255, 0.08);
  }
}
```

- [ ] **Step 2: 在 index.scss 中引入 mixins**

在 `ui/src/styles/index.scss` 的 `@use './variables.scss';` 之后添加：

```scss
@use './mixins.scss';
```

完整的 `index.scss` 内容：

```scss
@use 'element-plus/dist/index.css';
@use './element-plus.scss';
@use './variables.scss';
@use './mixins.scss';
@use './app.scss';
@use './component.scss';
@use './md-editor.scss';
@import 'nprogress/nprogress.css';
@import 'md-editor-v3/lib/style.css';
```

- [ ] **Step 3: 验证编译**

```bash
cd ui && npx sass --no-source-map --load-path=src src/styles/index.scss /dev/null 2>&1 | head -20
```

Expected: 无 error 输出

- [ ] **Step 4: Commit**

```bash
git add ui/src/styles/mixins.scss ui/src/styles/index.scss
git commit -m "feat(ui): add glassmorphism SCSS mixins

Add reusable mixins for glass effects: nav, sidebar, card, dropdown.
Include enter animations and list item stagger animations."
```

---

## Task 3: 更新 Element Plus 组件覆盖样式

**Files:**
- Modify: `ui/src/styles/element-plus.scss`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: 所有 Element Plus 组件的新样式

- [ ] **Step 1: 重写 element-plus.scss**

替换 `ui/src/styles/element-plus.scss` 的全部内容：

```scss
:root {
  --el-color-primary: #1A6DFF;
  --el-color-success: #34c724;
  --el-text-color-primary: #1D2129;
  --el-text-color-primary-rgb: 29, 33, 41;
  --el-border-radius-base: 8px;
  --el-menu-item-height: 45px;
  --el-border-color: rgba(0, 0, 0, 0.08);
}

[data-theme="dark"] {
  --el-color-primary: #3D85FF;
  --el-text-color-primary: #E5E6EB;
  --el-text-color-primary-rgb: 229, 230, 235;
  --el-border-color: rgba(255, 255, 255, 0.1);
}

// ===== Avatar =====
.el-avatar {
  --el-avatar-bg-color: var(--el-color-primary);
  --el-avatar-size-small: 33px;
  --el-avatar-border-radius: 8px;
  cursor: pointer;
  flex-shrink: 0;
}

.el-icon {
  flex-shrink: 0;
}

// ===== Card =====
.el-card {
  --el-card-padding: calc(var(--app-base-px) * 2);
  --el-card-border-radius: var(--app-border-radius-large);
  background: var(--bg-card) !important;
  backdrop-filter: var(--blur-card);
  -webkit-backdrop-filter: var(--blur-card);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: var(--shadow-card) !important;
  --el-border-color-light: var(--border-color);
  overflow: visible;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &.is-never-shadow {
    border: 1px solid var(--border-color);
    box-shadow: none !important;
  }
  .el-card__body {
    overflow: inherit;
  }
  &.is-hover-shadow:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover) !important;
  }
}

[data-theme="dark"] .el-card {
  border-color: rgba(255, 255, 255, 0.08);
}

// ===== Tree =====
.el-tree {
  background: none;
  color: var(--text-primary);
  font-weight: 400;
}
.el-tree-node__content {
  border-radius: var(--app-border-radius-base);
  padding: 7px 0;
  &:hover {
    background: var(--bg-hover);
  }
}
.el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content {
  background: var(--primary-50);
  color: var(--el-color-primary);
  font-weight: 500;
}
.el-tree-node__expand-icon {
  color: var(--text-secondary);
  font-size: 16px;
}

// ===== Button =====
.el-button {
  --el-button-font-weight: 400;
  --el-button-text-color: var(--text-primary);
  padding: 5px 12px;
  transition: all 0.2s ease;

  &.is-text {
    padding: 4px !important;
    font-size: 16px;
    max-height: 24px;
    &:not(.is-disabled):hover {
      background: var(--bg-hover);
    }
  }
  &:focus {
    background-color: none;
    border-color: none;
  }
  &:focus-visible {
    outline: none !important;
  }
  &.is-link:focus {
    background: none;
    border: none;
  }
  &.is-link:not(.is-disabled):hover {
    color: var(--el-color-primary);
  }
  &:active {
    transform: scale(0.97);
  }
}
.el-button--text {
  border: none !important;
  &:focus {
    border: none !important;
  }
}
.el-button--large {
  font-size: 16px;
}
.el-button--primary {
  --el-button-text-color: var(--el-color-white);
  --el-button-bg-color: #1A6DFF;
  --el-button-border-color: #1A6DFF;
  &:hover {
    --el-button-hover-bg-color: #1558D9;
    --el-button-hover-border-color: #1558D9;
  }
  &:active {
    --el-button-active-bg-color: #0F43B3;
    --el-button-active-border-color: #0F43B3;
  }
}

// ===== Dropdown =====
.el-dropdown {
  color: var(--text-primary);
}
.el-dropdown-menu__item {
  color: var(--text-primary);
  font-weight: 400;
  padding: 8px 12px;
  min-width: 80px;
  border-radius: 6px;
  margin: 2px 6px;
  transition: background 0.15s ease;

  i {
    margin-right: 8px;
  }
  &:not(.is-disabled):focus,
  &:not(.is-active):focus {
    background-color: var(--primary-50);
    color: var(--text-primary);
  }
  &.is-active,
  &.is-active:hover {
    color: var(--el-color-primary);
    background: var(--primary-50);
  }
  &.active {
    color: var(--el-color-primary);
  }
}

// ===== Popper (dropdown container) =====
.el-popper {
  --el-popper-border-radius: var(--app-border-radius-large);
  background: rgba(255, 255, 255, 0.88) !important;
  backdrop-filter: var(--blur-dropdown);
  -webkit-backdrop-filter: var(--blur-dropdown);
  border: 1px solid rgba(255, 255, 255, 0.6) !important;
  box-shadow: var(--shadow-dropdown) !important;

  .el-popper__arrow::before {
    background: rgba(255, 255, 255, 0.88) !important;
    border-color: rgba(255, 255, 255, 0.6) !important;
  }
}

[data-theme="dark"] .el-popper {
  background: rgba(44, 44, 46, 0.88) !important;
  border-color: rgba(255, 255, 255, 0.08) !important;

  .el-popper__arrow::before {
    background: rgba(44, 44, 46, 0.88) !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
  }
}

// ===== Message =====
.el-message {
  --el-message-close-icon-color: var(--text-secondary);
}
.el-message__content {
  word-break: break-all;
}
.el-message-box {
  --el-messagebox-font-size: 16px;
  --el-messagebox-width: 475px;
  padding: 24px;
  .el-message-box__header {
    padding: 0;
  }
  .el-message-box__title {
    word-break: break-all;
    width: 95%;
  }
}
.el-message-box__content {
  padding: 24px 0;
  color: var(--text-primary);
  font-weight: 400;
}
.el-message-box__btns {
  padding: 0;
  button {
    min-width: 80px;
    &:nth-child(2) {
      margin-left: 12px;
    }
  }
  button.danger {
    background: var(--el-color-danger);
    border: var(--el-color-danger);
    color: #ffffff;
  }
}
.el-message-box__headerbtn {
  right: 10px;
  top: 16px;
  .el-message-box__close {
    font-size: 20px;
  }
}

// ===== Drawer =====
.el-drawer {
  .el-drawer__header {
    padding: 16px 24px;
    margin: 0;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
  }
  .el-drawer__body {
    padding: 16px 24px;
  }
  .el-drawer__footer {
    border-top: 1px solid var(--border-color);
    padding: 16px 24px;
  }
}

// ===== Table =====
.el-table {
  --el-table-header-bg-color: rgba(0, 0, 0, 0.02);
  --el-table-text-color: var(--text-primary);
  --el-table-border-color: rgba(0, 0, 0, 0.04);
  --el-table-row-hover-bg-color: var(--primary-50);
  font-weight: 400;

  thead {
    color: var(--text-secondary);
    th {
      font-weight: 600;
    }
  }
  th.el-table__cell {
    border-top: var(--el-table-border);
  }
  .el-table__cell {
    padding: 12px 0;
  }
  .el-checkbox {
    height: 23px;
  }
  tr.highlight {
    background: var(--el-table-current-row-bg-color);
  }
}
.el-table--border,
.el-table--border::before,
.el-table--border::after,
.el-table--border td,
.el-table--border th {
  border-right: none !important;
  background-color: var(--bg-card-solid);
}
.el-table__border-left-patch {
  display: none !important;
}

[data-theme="dark"] .el-table {
  --el-table-header-bg-color: rgba(255, 255, 255, 0.04);
  --el-table-border-color: rgba(255, 255, 255, 0.06);
}

// ===== Dialog =====
.el-dialog {
  --el-dialog-padding-primary: 24px;
  --el-dialog-border-radius: var(--app-border-radius-xlarge);
  --el-dialog-title-font-size: 16px;
  box-shadow: var(--shadow-dialog);
  .el-dialog__body {
    color: var(--text-primary);
  }
}
.el-dialog__headerbtn {
  top: 12px;
  right: 8px;
  .el-dialog__close {
    font-size: 20px;
    color: var(--text-secondary);
  }
}

.el-overlay {
  backdrop-filter: var(--blur-overlay);
  -webkit-backdrop-filter: var(--blur-overlay);
}

@media only screen and (max-width: 768px) {
  .el-dialog {
    width: 90% !important;
  }
}

// ===== Form =====
.el-form {
  --el-form-inline-content-width: 100%;
}
.el-form-item {
  margin-bottom: 16px;
  .el-form-item {
    margin-bottom: 16px;
    &:last-child {
      margin-bottom: 0px;
    }
  }
}
.el-form-item__label {
  display: block;
  font-weight: 400;
  width: 100% !important;
  color: var(--text-primary);
}
.el-form-item__content {
  font-weight: 400 !important;
  color: var(--text-primary);
}
.el-form-item__error {
  position: unset;
  font-size: 14px;
}
.el-form--label-top .el-form-item .el-form-item__label {
  padding-right: 0;
}

.el-divider__text {
  background: var(--bg-content);
}

// ===== Input =====
.el-input {
  --el-input-text-color: var(--text-primary);
  --el-input-border-color: rgba(0, 0, 0, 0.1);
  --el-input-bg-color: var(--bg-card);
  transition: all 0.2s ease;

  .el-input__wrapper {
    border-radius: var(--app-border-radius-base);
    transition: all 0.2s ease;
    &:hover {
      box-shadow: 0 0 0 1px var(--border-color) inset;
    }
    &.is-focus {
      box-shadow: 0 0 0 1px var(--el-color-primary) inset, 0 0 0 3px rgba(26, 109, 255, 0.12);
    }
  }
}
.el-input .el-input__password {
  color: var(--text-secondary) !important;
}
.el-input-group__prepend div.el-select .el-select__wrapper {
  background: var(--bg-card-solid);
  &:hover {
    background: var(--bg-card-solid);
  }
  .el-select__placeholder {
    color: var(--el-text-color-regular);
  }
}

[data-theme="dark"] .el-input {
  --el-input-border-color: rgba(255, 255, 255, 0.1);
}

// ===== Cascader =====
.el-cascader-node {
  padding-left: 2px;
}
.el-cascader-node__prefix {
  right: 10px;
  left: auto;
}

// ===== Anchor =====
.el-anchor {
  --el-anchor-font-size: 14px;
}

// ===== Breadcrumb =====
.el-breadcrumb__separator.el-icon {
  font-size: 12px;
}

// ===== Tag =====
.el-tag {
  --el-tag-font-size: 12px;
  padding: 2px 8px;
  font-weight: 500;
  border-radius: 6px;
}
.el-tag--small {
  --el-tag-font-size: 12px;
}
.el-tag--plain.el-tag--info {
  color: var(--text-secondary);
  font-weight: 500;
  border-color: rgba(0, 0, 0, 0.08);
}
.el-tag.never {
  background: none;
}
.el-check-tag {
  font-weight: 400;
  padding: 7px 8px;
  color: var(--text-primary);
  background-color: var(--bg-hover);
  border-radius: 6px;
}
.el-check-tag.el-check-tag--primary.is-checked {
  background: var(--primary-50);
  color: var(--el-color-primary);
}

// ===== Select =====
.el-select__selected-item {
  color: var(--text-primary);
  font-weight: 400;
  .el-tag {
    color: var(--text-primary);
    background-color: var(--bg-hover);
    height: 24px;
    font-size: 14px;
    font-weight: 400;
  }
}
.el-select__caret {
  color: var(--text-secondary);
}
.el-select__wrapper.is-disabled .el-select__caret {
  color: var(--text-disabled);
}

// ===== Textarea =====
.el-textarea {
  --el-input-text-color: var(--text-primary);
}

// ===== Pagination =====
.el-pagination .el-select {
  width: 105px;
}
.el-pagination__total {
  color: var(--text-primary);
}

// ===== Checkbox =====
.el-checkbox {
  --el-checkbox-font-weight: 400;
  --el-checkbox-text-color: var(--text-primary);
}
.el-checkbox__input.is-checked + .el-checkbox__label {
  color: var(--text-primary);
}

// ===== Radio =====
.el-radio {
  --el-radio-font-weight: 400;
  color: var(--text-primary);
}
.el-radio__input.is-checked + .el-radio__label {
  color: var(--text-primary);
}

// ===== Tabs =====
.el-tabs__header {
  margin: 0 0 12px;
}
.el-tabs__item {
  padding: 0 14px;
  transition: color 0.2s ease;
}
.el-tabs__nav-wrap:after {
  height: 1px;
}
.el-tabs__active-bar {
  height: 3px;
  background: var(--el-color-primary);
}

// ===== Upload =====
.el-upload {
  --el-upload-dragger-padding-horizontal: 32px;
}

// ===== Switch =====
.el-switch__core {
  border: 1px solid var(--text-disabled);
  background: var(--text-disabled);
}

// ===== Progress =====
.el-progress-bar__inner {
  background: linear-gradient(90deg, rgba(26, 109, 255, 0.3) 0%, #1A6DFF 100%);
}

// ===== Scrollbar =====
.el-scrollbar__thumb {
  background-color: rgba(0, 0, 0, 0.12);
  border-radius: 3px;
  &:hover {
    background-color: rgba(0, 0, 0, 0.2);
  }
}
[data-theme="dark"] .el-scrollbar__thumb {
  background-color: rgba(255, 255, 255, 0.12);
  &:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }
}

// ===== Loading =====
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.7);
}
[data-theme="dark"] .el-loading-mask {
  background-color: rgba(30, 30, 30, 0.7);
}
```

- [ ] **Step 2: 验证编译**

```bash
cd ui && npx sass --no-source-map --load-path=src src/styles/element-plus.scss /dev/null 2>&1 | head -20
```

Expected: 无 error 输出

- [ ] **Step 3: Commit**

```bash
git add ui/src/styles/element-plus.scss
git commit -m "feat(ui): update Element Plus overrides for glassmorphism style

Update all component overrides with new design tokens:
- Glass card, dropdown, dialog backgrounds
- Inspur blue primary color
- Updated border-radius, shadows, transitions
- Dark mode support via [data-theme=\"dark\"]
- Input focus glow effect"
```

---

## Task 4: 更新全局样式与过渡动画

**Files:**
- Modify: `ui/src/styles/app.scss`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: 全局过渡样式、主题切换动画、暗色模式 body 背景

- [ ] **Step 1: 更新 app.scss 中的关键样式**

在 `app.scss` 中修改以下部分（保留其他工具类不变）：

1. 更新 body 颜色引用：

```scss
body {
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  font-family: 'PingFang SC', AlibabaPuHuiTi !important;
  font-size: 14px;
  font-style: normal;
  font-weight: 500;
  height: 100%;
  margin: 0;
  padding: 0;
  color: var(--text-primary);
  background-color: var(--bg-content);
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

2. 更新 `h2` 标题字重：

```scss
h2 {
  font-size: 20px;
  font-weight: 600;
}
```

3. 更新 avatar 样式中的硬编码颜色：

```scss
.avatar-blue {
  background: #1A6DFF;
}
```

4. 在文件末尾添加主题切换过渡和暗色模式全局样式：

```scss
// ===== 主题切换全局过渡 =====
* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

// 排除不需要过渡的元素
.no-transition,
.el-dialog,
.el-drawer,
.el-loading-mask,
.el-popper {
  transition: none !important;
}

// ===== 暗色模式全局覆盖 =====
[data-theme="dark"] {
  body {
    background-color: var(--bg-content);
    color: var(--text-primary);
  }

  // 暗色滚动条
  ::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.12);
  }
  ::-webkit-scrollbar-track {
    background-color: transparent;
  }
}

// 自定义主题（非默认色时的 header）
.custom-header {
  background: var(--primary-50) !important;
}
```

- [ ] **Step 2: 验证编译**

```bash
cd ui && npx sass --no-source-map --load-path=src src/styles/app.scss /dev/null 2>&1 | head -20
```

Expected: 无 error 输出

- [ ] **Step 3: Commit**

```bash
git add ui/src/styles/app.scss
git commit -m "feat(ui): update global styles with transitions and dark mode

- Update body background and text color to use new tokens
- Add global theme transition for smooth color changes
- Add dark mode scrollbar and body overrides
- Update h2 weight, avatar-blue color"
```

---

## Task 5: 更新主题系统支持暗色模式

**Files:**
- Modify: `ui/src/utils/theme.ts`
- Modify: `ui/src/stores/modules/theme.ts`

**Interfaces:**
- Consumes: 无
- Produces: `setDarkMode(mode)` action，`isDarkMode` getter 供后续组件使用

- [ ] **Step 1: 更新 theme.ts 工具函数**

在 `ui/src/utils/theme.ts` 中，更新 `defaultSetting` 并添加暗色模式相关函数：

```typescript
import { t } from '@/locales'

export const themeList = [
  {
    label: t('theme.default'),
    value: '#1A6DFF',
    loginBackground: 'default',
  },
  {
    label: t('theme.orange'),
    value: '#FF8800',
    loginBackground: 'orange',
  },
  {
    label: t('theme.green'),
    value: '#00B69D',
    loginBackground: 'green',
  },
  {
    label: t('theme.purple'),
    value: '#7F3BF5',
    loginBackground: 'purple',
  },
  {
    label: t('theme.red'),
    value: '#F01D94',
    loginBackground: 'red',
  },
]

export function getThemeImg(val: string) {
  if (!val) return 'default'
  return themeList.filter((v) => v.value === val)?.[0]?.loginBackground || 'default'
}

export const defaultSetting = {
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: t('theme.defaultSlogan'),
}

export const defaultPlatformSetting = {
  showUserManual: true,
  userManualUrl: t('layout.userManualUrl'),
  showForum: true,
  forumUrl: t('layout.forumUrl'),
  showProject: true,
  projectUrl: 'https://github.com/1Panel-dev/MaxKB',
}

export function hexToRgba(hex?: string, alpha?: number) {
  if (!hex) {
    return ''
  } else {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
}

// ===== 暗色模式 =====
export type DarkModeType = 'light' | 'dark' | 'system'

const DARK_MODE_KEY = 'MaxKB-dark-mode'

export function getDarkMode(): DarkModeType {
  return (localStorage.getItem(DARK_MODE_KEY) as DarkModeType) || 'light'
}

export function setDarkMode(mode: DarkModeType) {
  localStorage.setItem(DARK_MODE_KEY, mode)
  applyDarkMode(mode)
}

export function applyDarkMode(mode?: DarkModeType) {
  const currentMode = mode || getDarkMode()
  const root = document.documentElement

  if (currentMode === 'dark') {
    root.setAttribute('data-theme', 'dark')
  } else if (currentMode === 'light') {
    root.removeAttribute('data-theme')
  } else {
    // system: follow OS preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      root.setAttribute('data-theme', 'dark')
    } else {
      root.removeAttribute('data-theme')
    }
  }
}

export function initDarkMode() {
  applyDarkMode()
  // Listen for OS theme changes when in system mode
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (getDarkMode() === 'system') {
      applyDarkMode('system')
    }
  })
}
```

- [ ] **Step 2: 更新 theme store**

替换 `ui/src/stores/modules/theme.ts`：

```typescript
import { defineStore } from 'pinia'
import { cloneDeep } from 'lodash'
import { useElementPlusTheme } from 'use-element-plus-theme'
import ThemeApi from '@/api/system-settings/theme'
import {
  getDarkMode,
  setDarkMode as setDarkModeUtil,
  applyDarkMode,
  initDarkMode,
  type DarkModeType,
} from '@/utils/theme'
import type { Ref } from 'vue'

export interface themeStateTypes {
  themeInfo: any
  darkMode: DarkModeType
}

const defaultColor = '#1A6DFF'

const useThemeStore = defineStore('theme', {
  state: (): themeStateTypes => ({
    themeInfo: null,
    darkMode: getDarkMode(),
  }),
  getters: {
    isDarkMode(): boolean {
      const root = document.documentElement
      return root.getAttribute('data-theme') === 'dark'
    },
  },
  actions: {
    isDefaultTheme() {
      return !this.themeInfo?.theme || this.themeInfo?.theme === defaultColor
    },

    setTheme(data?: any) {
      const { changeTheme } = useElementPlusTheme(this.themeInfo?.theme || defaultColor)
      changeTheme(data?.['theme'] || defaultColor)
      this.themeInfo = cloneDeep(data)
    },

    setDarkMode(mode: DarkModeType) {
      this.darkMode = mode
      setDarkModeUtil(mode)
    },

    async theme(loading?: Ref<boolean>) {
      return await ThemeApi.getThemeInfo(loading).then((ok) => {
        this.setTheme(ok.data)
        // Apply dark mode on init
        initDarkMode()
      })
    },
  },
})

export default useThemeStore
```

- [ ] **Step 3: Commit**

```bash
git add ui/src/utils/theme.ts ui/src/stores/modules/theme.ts
git commit -m "feat(ui): add dark mode support to theme system

- Add DarkModeType (light/dark/system) with localStorage persistence
- Add applyDarkMode() to set [data-theme] on document root
- Update theme store with darkMode state and setDarkMode action
- Update default primary color to #1A6DFF
- Listen for OS prefers-color-scheme changes"
```

---

## Task 6: 更新布局模板样式

**Files:**
- Modify: `ui/src/layout/layout-template/index.scss`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: 毛玻璃导航栏和内容区背景

- [ ] **Step 1: 重写布局模板 SCSS**

替换 `ui/src/layout/layout-template/index.scss`：

```scss
.app-layout {
  background-color: var(--bg-content);
  height: 100%;
}

.app-header {
  background: var(--bg-glass-nav);
  backdrop-filter: var(--blur-nav);
  -webkit-backdrop-filter: var(--blur-nav);
  border-bottom: 1px solid var(--border-color-light);
  position: fixed;
  width: 100%;
  left: 0;
  top: 0;
  z-index: 100;
  animation: glass-header-enter 0.5s ease-out;
}

@keyframes glass-header-enter {
  from {
    backdrop-filter: blur(0);
    -webkit-backdrop-filter: blur(0);
  }
  to {
    backdrop-filter: var(--blur-nav);
    -webkit-backdrop-filter: var(--blur-nav);
  }
}

.app-main {
  position: relative;
  height: 100%;
  padding: var(--app-header-height) 0 0 !important;
  box-sizing: border-box;
  overflow: auto;
  &.isExpire {
    padding-top: calc(var(--app-header-height) + 40px) !important;
  }
}

// 暗色模式下导航栏
[data-theme="dark"] .app-header {
  background: var(--bg-glass-nav);
  border-bottom-color: rgba(255, 255, 255, 0.06);
}

// 非默认主题时
.custom-header {
  background: var(--primary-50) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
```

- [ ] **Step 2: Commit**

```bash
git add ui/src/layout/layout-template/index.scss
git commit -m "feat(ui): update layout template with glassmorphism header

- Replace gradient header with glassmorphism background
- Add backdrop-filter blur animation on page load
- Update dark mode border color for header"
```

---

## Task 7: 更新导航栏组件

**Files:**
- Modify: `ui/src/layout/layout-header/UserHeader.vue`
- Modify: `ui/src/layout/layout-header/SystemHeader.vue`

**Interfaces:**
- Consumes: logo.png from `ui/src/assets/logo/logo.png`
- Produces: 新的导航栏布局，包含浪潮 logo

- [ ] **Step 1: 更新 UserHeader.vue**

替换 `ui/src/layout/layout-header/UserHeader.vue` 的 template 和 style 部分：

```vue
<template>
  <div class="app-top-bar-container flex-center">
    <div class="logo-container flex align-center">
      <img src="@/assets/logo/logo.png" alt="logo" class="header-logo" />
      <span class="logo-text">MaxKB</span>
    </div>

    <div class="flex-between w-full">
      <div class="ml-24 flex align-center w-120">
        <el-divider
          class="mr-8"
          direction="vertical"
          v-if="hasPermission(EditionConst.IS_EE, 'OR')"
        />
        <WorkspaceDropdown
          v-if="hasPermission(EditionConst.IS_EE, 'OR')"
          :data="user.workspace_list"
          :currentWorkspace="currentWorkspace"
          @changeWorkspace="changeWorkspace"
        />
      </div>
      <TopMenu></TopMenu>
      <TopAbout class="mr-12"></TopAbout>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import type { WorkspaceItem } from '@/api/type/workspace'
import useStore from '@/stores'
const router = useRouter()
const route = useRoute()

const { user } = useStore()
const currentWorkspace = computed(() => {
  return user.workspace_list.find((w) => w.id == user.workspace_id)
})

function changeWorkspace(item: WorkspaceItem) {
  const {
    meta: { activeMenu },
  } = route as any
  if (item.id === user.workspace_id) return
  user.setWorkspaceId(item.id || 'default')
  if (activeMenu.includes('application') && route.path != '/application') {
    router.push('/application')
  } else if (activeMenu.includes('knowledge') && route.path != '/knowledge') {
    router.push('/knowledge')
  } else {
    window.location.reload()
  }
}
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}

.logo-container {
  gap: 10px;
}

.header-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #1A6DFF 0%, #3D7DF3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
```

- [ ] **Step 2: 更新 SystemHeader.vue**

替换 `ui/src/layout/layout-header/SystemHeader.vue` 的 template 和 style 部分：

```vue
<template>
  <div class="app-top-bar-container flex-center">
    <div class="logo-container flex align-center">
      <img src="@/assets/logo/logo.png" alt="logo" class="header-logo" />
      <span class="logo-text">MaxKB</span>
    </div>

    <div class="flex-between w-full align-center">
      <h4><el-divider class="ml-16 mr-16" direction="vertical" />{{ $t('views.system.title') }}</h4>
      <div class="flex align-center mr-8">
        <TopAbout type="system"></TopAbout>
        <el-divider class="ml-8 mr-8" direction="vertical" />
        <el-button
          link
          @click="goHome"
          style="color: var(--text-primary)"
          v-if="
            hasPermission(
              [
                RoleConst.USER.getWorkspaceRole,
                RoleConst.EXTENDS_USER.getWorkspaceRole,
                RoleConst.EXTENDS_WORKSPACE_MANAGE.getWorkspaceRole,
                RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              ],
              'OR',
            )
          "
        >
          <AppIcon class="mr-8" iconName="app-workspace" style="font-size: 16px"></AppIcon>
          {{ $t('views.workspace.toWorkspace') }}</el-button
        >
      </div>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import { RoleConst } from '@/utils/permission/data'
import Avatar from './avatar/index.vue'
import TopAbout from './top-about/index.vue'
import { useRouter } from 'vue-router'
import { hasPermission } from '@/utils/permission'

const router = useRouter()
const goHome = () => {
  router.push('/')
}
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}

.logo-container {
  gap: 10px;
}

.header-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #1A6DFF 0%, #3D7DF3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add ui/src/layout/layout-header/UserHeader.vue ui/src/layout/layout-header/SystemHeader.vue
git commit -m "feat(ui): redesign header with Inspur logo and glassmorphism

- Replace SVG logo with inspur logo.png
- Add gradient text 'MaxKB' branding
- Update header height to 64px via CSS variable
- Update color references to new tokens"
```

---

## Task 8: 更新侧边栏样式

**Files:**
- Modify: `ui/src/layout/components/sidebar/index.vue`
- Modify: `ui/src/layout/components/sidebar/SidebarItem.vue`

**Interfaces:**
- Consumes: CSS variables from Task 1, mixins from Task 2
- Produces: 毛玻璃侧边栏

- [ ] **Step 1: 更新侧边栏容器样式**

替换 `ui/src/layout/components/sidebar/index.vue` 的 `<style>` 部分：

```vue
<template>
  <div class="sidebar-container">
    <div v-if="showBreadcrumb">
      <AppBreadcrumb />
    </div>
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu :default-active="activeMenu" router>
        <sidebar-item
          v-hasPermission="menu.meta?.permission"
          v-for="(menu, index) in subMenuList"
          :key="index"
          :menu="menu"
          :activeMenu="activeMenu"
        >
        </sidebar-item>
      </el-menu>
    </el-scrollbar>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getChildRouteListByPathAndName } from '@/router/index'
import SidebarItem from './SidebarItem.vue'
import AppBreadcrumb from './../breadcrumb/index.vue'

const route = useRoute()

const showBreadcrumb = computed(() => {
  const { meta } = route as any
  return meta?.breadcrumb
})

const subMenuList = computed(() => {
  const { meta } = route
  return getChildRouteListByPathAndName(meta.parentPath, meta.parentName)
})

const activeMenu = computed(() => {
  const { path, meta } = route
  return meta.active || path
})
</script>

<style lang="scss" scoped>
.sidebar-container {
  padding: 8px;
  height: 100%;
}
</style>

<style lang="scss">
.sidebar-container {
  .el-menu {
    height: 100%;
    border: none;
    background: none;
    max-height: calc(100vh - 100px);
  }
}
</style>
```

- [ ] **Step 2: 更新 SidebarItem 样式**

替换 `ui/src/layout/components/sidebar/SidebarItem.vue` 的 `<style>` 部分：

```scss
<style scoped lang="scss">
.sidebar-item {
  .sidebar-icon {
    font-size: 20px;
    margin-top: -2px;
  }
  .el-menu-item {
    padding: 13px 12px 13px 8px !important;
    font-weight: 500;
    border-radius: var(--app-border-radius-base);
    transition: all 0.15s ease;
    &:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }
  }
  :deep(.el-sub-menu__title) {
    padding: 13px 12px 13px 10px !important;
    &:hover {
      background: none;
      color: var(--el-color-primary);
    }
  }
  .el-sub-menu {
    .el-menu-item {
      padding-left: 43px !important;
    }
  }
  .el-menu-item.is-active {
    color: var(--el-color-primary);
    background: var(--primary-50);
  }
}
</style>
```

- [ ] **Step 3: 更新 LayoutContainer 组件中的侧边栏背景**

查找并更新 `ui/src/components/layout-container/index.vue`（或等效文件），确保侧边栏容器使用毛玻璃背景：

在 layout-container 的侧边栏部分的 style 中添加：

```scss
.sidebar-wrapper {
  background: var(--bg-glass-sidebar);
  backdrop-filter: var(--blur-sidebar);
  -webkit-backdrop-filter: var(--blur-sidebar);
  transition: width 0.25s ease-in-out;
}
```

- [ ] **Step 4: Commit**

```bash
git add ui/src/layout/components/sidebar/index.vue ui/src/layout/components/sidebar/SidebarItem.vue
git commit -m "feat(ui): update sidebar with glassmorphism background

- Update sidebar menu item hover and active styles
- Use new CSS variable tokens for colors
- Add transition animations for menu items"
```

---

## Task 9: 更新登录页

**Files:**
- Modify: `ui/src/layout/login-layout/LoginLayout.vue`
- Modify: `ui/src/layout/login-layout/LoginContainer.vue`

**Interfaces:**
- Consumes: logo.png, CSS variables from Task 1
- Produces: macOS 风格的登录页，左侧渐变 + 大 logo，右侧毛玻璃表单

- [ ] **Step 1: 重写 LoginLayout.vue**

替换 `ui/src/layout/login-layout/LoginLayout.vue` 的 template 和 style：

```vue
<template>
  <div class="login-warp">
    <div class="login-container w-full h-full">
      <el-row class="container w-full h-full">
        <el-col :xs="0" :sm="0" :md="10" :lg="10" :xl="10" class="left-container">
          <div class="login-left-bg">
            <!-- 装饰性光斑 -->
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <!-- Logo 区域 -->
            <div class="login-brand">
              <img src="@/assets/logo/logo.png" alt="logo" class="login-logo" />
              <h1 class="login-title">MaxKB</h1>
              <p class="login-slogan">{{ newDefaultSlogan }}</p>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14" class="right-container flex-center">
          <el-dropdown trigger="click" type="primary" class="lang" v-if="lang">
            <template #dropdown>
              <el-dropdown-menu class="w-180">
                <el-dropdown-item
                  v-for="(lang, index) in langList"
                  :key="index"
                  :value="lang.value"
                  @click="changeLang(lang.value)"
                  class="flex-between"
                >
                  <span :class="lang.value === user.getLanguage() ? 'primary' : ''">{{
                    lang.label
                  }}</span>
                  <el-icon
                    :class="lang.value === user.getLanguage() ? 'primary' : ''"
                    v-if="lang.value === user.getLanguage()"
                  >
                    <Check />
                  </el-icon>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
            <el-button>
              {{ currentLanguage }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
          </el-dropdown>
          <slot></slot>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import useStore from '@/stores'
import { useLocalStorage } from '@vueuse/core'
import { langList, localeConfigKey, getBrowserLang } from '@/locales/index'
import { t } from '@/locales'

defineProps({
  lang: {
    type: Boolean,
    default: true,
  },
})
const { user, theme } = useStore()

const changeLang = (lang: string) => {
  useLocalStorage(localeConfigKey, getBrowserLang()).value = lang
  window.location.reload()
}

const currentLanguage = computed(() => {
  return langList.value?.filter((v: any) => v.value === user.getLanguage())?.[0]?.label
})

const newDefaultSlogan = computed(() => {
  const default_login = '强大易用的企业级智能体平台'
  if (!theme.themeInfo?.slogan || default_login == theme.themeInfo?.slogan) {
    return t('theme.defaultSlogan')
  } else {
    return theme.themeInfo?.slogan
  }
})
</script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;
  background: var(--bg-content);
}

.left-container {
  position: relative;
  overflow: hidden;
}

.login-left-bg {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E8F0FE 0%, #C5D9FC 50%, #E5E0FA 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

// 装饰性光斑
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
}
.orb-1 {
  width: 300px;
  height: 300px;
  background: rgba(26, 109, 255, 0.2);
  top: 10%;
  left: 10%;
}
.orb-2 {
  width: 250px;
  height: 250px;
  background: rgba(127, 59, 245, 0.15);
  bottom: 20%;
  right: 10%;
}
.orb-3 {
  width: 200px;
  height: 200px;
  background: rgba(197, 217, 252, 0.3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.login-brand {
  position: relative;
  z-index: 1;
  text-align: center;
}

.login-logo {
  width: 120px;
  height: auto;
  margin-bottom: 24px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: #1A6DFF;
  margin-bottom: 12px;
}

.login-slogan {
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 300px;
}

.right-container {
  position: relative;
  .lang {
    position: absolute;
    right: 20px;
    top: 20px;
  }
}

// 暗色模式左侧渐变
[data-theme="dark"] .login-left-bg {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
}

[data-theme="dark"] .login-title {
  color: #5A94F5;
}

[data-theme="dark"] .orb-1 {
  background: rgba(61, 133, 255, 0.15);
}
[data-theme="dark"] .orb-2 {
  background: rgba(127, 59, 245, 0.1);
}
[data-theme="dark"] .orb-3 {
  background: rgba(90, 148, 245, 0.1);
}
</style>
```

- [ ] **Step 2: 更新 LoginContainer.vue**

替换 `ui/src/layout/login-layout/LoginContainer.vue`：

```vue
<template>
  <div class="login-form-container p-24">
    <div class="login-title-section">
      <div class="mobile-logo text-center" v-if="!theme.themeInfo?.loginLogo">
        <img src="@/assets/logo/logo.png" alt="logo" class="mobile-logo-img" />
      </div>
      <div class="logo text-center" v-else>
        <slot name="logo">
          <LogoFull height="45px" />
        </slot>
      </div>
      <div class="sub-title text-center" v-if="subTitle">
        <el-text type="info">{{ subTitle }}</el-text>
      </div>
    </div>
    <div class="login-glass-card">
      <slot></slot>
    </div>
  </div>
</template>
<script setup lang="ts">
import useStore from '@/stores'

defineProps({
  title: String,
  subTitle: String,
})

const { theme } = useStore()
</script>
<style lang="scss" scoped>
.login-form-container {
  width: 480px;

  .login-title-section {
    margin-bottom: 32px;
    .sub-title {
      font-size: 16px;
      color: var(--text-secondary);
    }
  }
}

.mobile-logo-img {
  height: 40px;
  width: auto;
}

.login-glass-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--app-border-radius-xlarge);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  padding: 32px;
}

[data-theme="dark"] .login-glass-card {
  background: rgba(44, 44, 46, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add ui/src/layout/login-layout/LoginLayout.vue ui/src/layout/login-layout/LoginContainer.vue
git commit -m "feat(ui): redesign login page with glassmorphism style

- Left panel: gradient background with decorative orbs and Inspur logo
- Right panel: glass-effect form card with blur backdrop
- Dark mode support for both panels
- Mobile responsive logo display"
```

---

## Task 10: 更新首页作为样板页

**Files:**
- Modify: `ui/src/views/home/index.vue`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: 使用新设计令牌的首页样板

- [ ] **Step 1: 更新首页样式**

替换 `ui/src/views/home/index.vue` 的 `<style>` 部分：

```vue
<template>
  <el-scrollbar>
    <div class="home p-16">
      <el-card style="--el-card-padding: 24px" class="home-card">
        <h4 class="mb-16">
          {{ $t('home.quickCreate') }}
        </h4>
        <QuickCreate />
      </el-card>

      <el-card style="--el-card-padding: 24px" class="mt-16 home-card">
        <h4 class="mb-16">
          {{ $t('home.resource') }}
        </h4>
        <ResourceAggregation />
      </el-card>
      <!-- 监听 -->
      <StatisticsCharts />
      <!-- 排行榜 -->
      <Ranking />

      <br />
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, shallowRef, nextTick } from 'vue'
import { useRoute } from 'vue-router'

import StatisticsCharts from './component/StatisticsCharts.vue'
import QuickCreate from './component/QuickCreate.vue'
import ResourceAggregation from './component/ResourceAggregation.vue'
import Ranking from './component/Ranking.vue'

const route = useRoute()
const {
  params: { id },
} = route as any

onMounted(() => {})
</script>
<style lang="scss" scoped>
.home {
  max-width: 1280px;
  margin: 0 auto;
  height: calc(var(--app-main-height) + 74px);
  box-sizing: border-box;
}

.home-card {
  background: var(--bg-card);
  backdrop-filter: var(--blur-card);
  -webkit-backdrop-filter: var(--blur-card);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: var(--app-border-radius-large);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
}

[data-theme="dark"] .home-card {
  border-color: rgba(255, 255, 255, 0.08);
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add ui/src/views/home/index.vue
git commit -m "feat(ui): update home page as glassmorphism design sample

- Apply glass card effects with backdrop-filter blur
- Add hover lift animation for cards
- Use new CSS variable tokens for colors and shadows
- Dark mode support"
```

---

## Task 11: 在头像下拉菜单中添加主题切换入口

**Files:**
- Modify: `ui/src/layout/layout-header/avatar/index.vue`

**Interfaces:**
- Consumes: `setDarkMode()` from theme store, `DarkModeType` from utils
- Produces: 用户可通过下拉菜单切换亮色/暗色/跟随系统

- [ ] **Step 1: 在头像下拉菜单中添加主题切换选项**

在 `ui/src/layout/layout-header/avatar/index.vue` 的 `el-dropdown-menu` 中，在语言切换之前添加主题切换下拉菜单：

在 `<template>` 中的 language dropdown-item 之前添加：

```vue
<el-dropdown-item
  style="padding: 0"
  @click.stop
>
  <el-dropdown class="w-full" trigger="hover" placement="left-start">
    <div class="flex-between w-full" style="line-height: 22px; padding: 12px 11px">
      <span>{{ $t('layout.theme') || '主题' }}</span>
      <el-icon>
        <ArrowRight />
      </el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu class="w-180">
        <el-dropdown-item
          v-for="(mode, index) in darkModeList"
          :key="index"
          :value="mode.value"
          @click="changeDarkMode(mode.value)"
          class="flex-between"
        >
          <span :class="mode.value === theme.darkMode ? 'primary' : ''">{{ mode.label }}</span>
          <el-icon
            :class="mode.value === theme.darkMode ? 'primary' : ''"
            v-if="mode.value === theme.darkMode"
          >
            <Check />
          </el-icon>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</el-dropdown-item>
```

在 `<script>` 中添加：

```typescript
const darkModeList = [
  { label: '浅色', value: 'light' as const },
  { label: '深色', value: 'dark' as const },
  { label: '跟随系统', value: 'system' as const },
]

const changeDarkMode = (mode: 'light' | 'dark' | 'system') => {
  theme.setDarkMode(mode)
}
```

- [ ] **Step 2: Commit**

```bash
git add ui/src/layout/layout-header/avatar/index.vue
git commit -m "feat(ui): add dark mode toggle to avatar dropdown menu

Add light/dark/system theme switcher in user dropdown."
```

---

## Task 12: 更新主题设置页面

**Files:**
- Modify: `ui/src/views/system-setting/theme/index.vue`

**Interfaces:**
- Consumes: `themeList` from `@/utils/theme` (updated primary color)
- Produces: 确保主题颜色选择器与新主色调一致

- [ ] **Step 1: 检查并更新主题设置页**

确认主题颜色选择器中的默认颜色已更新为 `#1A6DFF`（通过 theme.ts 中的 themeList 自动生效）。

如有硬编码的 `#3370FF`，替换为 `#1A6DFF`。

- [ ] **Step 2: Commit**

```bash
git add ui/src/views/system-setting/theme/index.vue
git commit -m "feat(ui): update theme settings for new primary color"
```

---

## Task 13: 全局扫描替换硬编码旧主色

**Files:**
- Multiple files across `ui/src/`

**Interfaces:**
- Consumes: 无
- Produces: 所有硬编码的 `#3370FF` / `#3370ff` 替换为 `#1A6DFF` 或使用 CSS 变量

- [ ] **Step 1: 搜索所有硬编码的旧主色**

```bash
cd ui && grep -rni '#3370ff\|#3370FF\|3370ff' src/ --include='*.vue' --include='*.scss' --include='*.ts' | grep -v node_modules | head -30
```

- [ ] **Step 2: 逐个替换**

对于 SCSS 文件中的替换为 `var(--el-color-primary)` 或 `#1A6DFF`。
对于 TypeScript 文件中的替换为 `#1A6DFF`。

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat(ui): replace hardcoded #3370FF with #1A6DFF across codebase

Global color migration from old primary to Inspur blue."
```

---

## Task 14: 端到端验证

**Files:**
- 无新增修改

**Interfaces:**
- Consumes: 所有前述 Task 的产出
- Produces: 确认编译通过，视觉效果符合设计

- [ ] **Step 1: 启动开发服务器验证**

```bash
cd ui && npm run dev
```

Expected: 开发服务器启动成功，无编译错误

- [ ] **Step 2: 浏览器验证清单**

1. 亮色模式：
   - 导航栏显示毛玻璃效果 + 浪潮 logo
   - 侧边栏半透明背景
   - 卡片有 blur 效果和 hover 动画
   - 登录页左侧渐变 + 大 logo，右侧毛玻璃表单
   - 首页卡片样式统一

2. 暗色模式：
   - 通过头像菜单切换到"深色"
   - 所有背景变为深色
   - 文字清晰可读
   - 导航栏和侧边栏保持毛玻璃效果

3. 主题切换：
   - 亮色 → 暗色切换动画平滑
   - 登录页在暗色模式下正确显示

- [ ] **Step 3: 最终 Commit（如有修复）**

```bash
git add -A
git commit -m "fix(ui): polish glassmorphism UI based on visual verification"
```
