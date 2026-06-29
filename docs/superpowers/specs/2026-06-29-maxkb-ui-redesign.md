# MaxKB UI 全面改版设计文档

## 概述

将 MaxKB 平台的 UI 从当前的渐变蓝紫色风格全面改版为 macOS/iOS 风格的毛玻璃现代设计。涵盖配色体系、布局结构、组件样式、暗色模式和动效系统。

## 设计决策记录

| 维度 | 决定 |
|------|------|
| 视觉方向 | 毛玻璃/现代感 (macOS/iOS 风) |
| 改版范围 | 全面改版（配色 + 布局 + 组件） |
| 主色调 | 浪潮蓝 `#1A6DFF` |
| Logo | 登录页大 logo + 导航栏小 logo，使用 `ui/src/assets/logo/logo.png` |
| 暗色/亮色 | 同时支持，用户可切换 |
| 动效 | 适度型（毛玻璃 + 过渡 + 悬停动效） |
| 推进策略 | 先做一个完整页面作为样板，确认后推广到其他页面 |
| 实现方案 | CSS 变量驱动 + 现有 Element Plus 架构增强 |

---

## 1. 色彩体系与设计令牌

### 1.1 主色调系统

以浪潮蓝 `#1A6DFF` 为核心，派生完整色阶。在 `ui/src/styles/variables.scss` 中扩展：

| 令牌 | 亮色值 | 暗色值 | 用途 |
|------|--------|--------|------|
| `--primary-50` | `#E8F0FE` | — | 悬停背景 |
| `--primary-100` | `#C5D9FC` | — | 选中背景 |
| `--primary-200` | `#93B8F9` | — | 边框高亮 |
| `--primary-300` | `#6097F6` | — | 图标装饰 |
| `--primary-400` | `#3D7DF3` | `#5A94F5` | 次要按钮 |
| `--primary-500` | `#1A6DFF` | `#3D85FF` | 主按钮、链接 |
| `--primary-600` | `#1558D9` | `#5A94F5` | 按钮 hover |
| `--primary-700` | `#0F43B3` | `#7AAAFF` | 按钮 active |

### 1.2 背景色系统

```
亮色模式:
  导航栏背景: rgba(255, 255, 255, 0.72) + backdrop-filter: blur(20px)
  侧边栏背景: rgba(255, 255, 255, 0.56) + backdrop-filter: blur(16px)
  内容区背景: #F5F7FA
  卡片背景:   rgba(255, 255, 255, 0.8) + backdrop-filter: blur(12px)

暗色模式:
  导航栏背景: rgba(30, 30, 30, 0.72) + backdrop-filter: blur(20px)
  侧边栏背景: rgba(30, 30, 30, 0.56) + backdrop-filter: blur(16px)
  内容区背景: #1E1E1E
  卡片背景:   rgba(44, 44, 46, 0.8) + backdrop-filter: blur(12px)
```

### 1.3 文字色系统

```
亮色:  主文字 #1D2129 / 次文字 #4E5969 / 禁用 #C9CDD4
暗色:  主文字 #E5E6EB / 次文字 #A6A6A6 / 禁用 #4E4E4E
```

---

## 2. 布局与导航

### 2.1 顶部导航栏

- 高度：`56px` → `64px`
- 背景：渐变色 → 毛玻璃白色 `rgba(255,255,255,0.72) + blur(20px)`
- 底部：`1px solid rgba(0,0,0,0.06)` 半透明分割线
- Logo 区域：左侧放置浪潮 logo（`ui/src/assets/logo/logo.png`），蓝色图标 + "MaxKB" 文字
- 导航菜单：居中排列，选中态用底部 2px 蓝色指示条
- 右侧操作区：升级按钮、通知图标、头像

### 2.2 左侧边栏

- 背景：`rgba(255,255,255,0.56) + blur(16px)` 毛玻璃
- 宽度：保持 `240px`，折叠时 `64px`
- 菜单项：圆角 `8px`，选中背景 `primary-50`
- 与内容区间无实线分割，通过背景色差区分
- 收起/展开按钮：圆形小按钮，位于分割线中间

### 2.3 内容区

- 背景：`#F5F7FA`
- 内边距：保持 `24px`
- 页面标题：字号 `20px`，字重 `600`，底部间距加大

### 2.4 卡片样式

```
背景:   rgba(255, 255, 255, 0.8)
模糊:   backdrop-filter: blur(12px)
边框:   1px solid rgba(255, 255, 255, 0.6)
圆角:   12px
阴影:   0 2px 12px rgba(0, 0, 0, 0.04)
Hover:  阴影增强 0 4px 20px rgba(0, 0, 0, 0.08)，上移 2px
```

---

## 3. 核心组件样式

### 3.1 按钮

```
主按钮:   背景 #1A6DFF，圆角 8px，高度 36px
          hover: #1558D9 + 上浮 1px
          active: #0F43B3
          点击时 scale(0.97) 微缩动效
次要按钮: 边框 1px solid #1A6DFF，文字蓝色，背景透明
          hover: 背景 primary-50
幽灵按钮: 背景 transparent，文字主色
          hover: 背景 primary-50
```

### 3.2 输入框 / 搜索框

```
背景:     rgba(255, 255, 255, 0.8)
边框:     1px solid rgba(0, 0, 0, 0.1)
圆角:     8px
聚焦态:   边框 primary-500，外发光 box-shadow: 0 0 0 3px rgba(26, 109, 255, 0.12)
过渡:     0.2s ease
```

### 3.3 下拉菜单 / 弹出层

```
背景:     rgba(255, 255, 255, 0.88)
模糊:     backdrop-filter: blur(20px)
圆角:     12px
阴影:     0 8px 32px rgba(0, 0, 0, 0.12)
边框:     1px solid rgba(255, 255, 255, 0.6)
菜单项:   圆角 6px，hover 背景 primary-50，间距增大
```

### 3.4 对话框 / 弹窗

```
背景:     白色
遮罩:     rgba(0, 0, 0, 0.4) + backdrop-filter: blur(4px)
圆角:     16px
阴影:     0 16px 48px rgba(0, 0, 0, 0.16)
进入动画: scale(0.95) → scale(1) + opacity 0→1，0.25s ease-out
```

### 3.5 表格

```
表头:     背景 rgba(0, 0, 0, 0.02)，字重 600
行间:     1px solid rgba(0, 0, 0, 0.04)
Hover:    整行背景 primary-50，0.15s 过渡
外容器:   圆角 12px
```

### 3.6 标签 / Tag

```
圆角:     6px
背景:     rgba 透明度版本
字号:     12px，字重 500
内边距:   2px 8px
```

---

## 4. 登录页

### 4.1 布局

- 左右分栏：左侧 45% / 右侧 55%
- 左侧背景：渐变 + 毛玻璃质感背景
  - 底色：`linear-gradient(135deg, #E8F0FE 0%, #C5D9FC 50%, #E5E0FA 100%)`
  - 叠加半透明圆形装饰元素（柔和光斑效果）
  - 中央放置大尺寸浪潮 logo + "MaxKB" + slogan
- 右侧表单区：白色/透明，无明显边框
- 表单卡片：`rgba(255,255,255,0.6) + blur(16px)`，圆角 `16px`，内边距 `40px`
- 阴影：`0 8px 32px rgba(0, 0, 0, 0.06)`

### 4.2 表单细节

```
输入框:   半透明背景 + 柔和边框
按钮:     全宽主按钮，圆角 8px，背景 #1A6DFF
链接:     primary-500 色，hover 加下划线
```

### 4.3 暗色模式

- 左侧渐变：`linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%)`
- 右侧表单卡片背景变深，文字反白
- Logo 保持不变

---

## 5. 动效与过渡

### 5.1 全局过渡规范

```
基础过渡:  all 0.2s ease
页面切换:  opacity + translateY(8px) → opacity:1 translateY(0)，0.3s ease-out
菜单展开:  height/width 过渡 0.25s ease-in-out
```

### 5.2 毛玻璃进场动画

页面首次加载时，导航栏和侧边栏毛玻璃从 `blur(0)` → `blur(20px)` 渐进，时长 `0.5s`。

### 5.3 卡片与列表项

```
列表加载:  逐项延迟入场，每项间隔 50ms，translateY(12px) + opacity:0 → 原位
卡片 Hover: transform: translateY(-2px) + shadow 增强，0.2s
卡片点击:  scale(0.98) → scale(1)，0.15s
```

### 5.4 侧边栏

```
展开/折叠: width 0.25s ease-in-out
图标旋转:  0.2s rotate
菜单项切换: 背景色 0.15s，选中指示条滑动 0.25s
```

### 5.5 弹窗与抽屉

```
弹窗:     scale(0.95) → scale(1) + opacity 0→1，0.25s ease-out
遮罩:     opacity 0→1，0.2s
抽屉:     translateX(100%) → translateX(0)，0.3s ease-out
下拉菜单: opacity 0→1 + translateY(-4px) → translateY(0)，0.2s
```

### 5.6 主题切换动画

亮色 ↔ 暗色切换时，所有颜色通过 `transition: background-color 0.3s, color 0.3s, border-color 0.3s` 平滑过渡。

---

## 6. 暗色模式实现

### 6.1 技术方案

通过 `[data-theme="dark"]` 属性选择器 + CSS 变量覆盖实现：

```scss
:root {
  // 亮色变量（默认）
  --bg-glass-nav: rgba(255, 255, 255, 0.72);
  --bg-glass-sidebar: rgba(255, 255, 255, 0.56);
  --bg-content: #F5F7FA;
  --bg-card: rgba(255, 255, 255, 0.8);
  --text-primary: #1D2129;
  --text-secondary: #4E5969;
  // ... 其他变量
}

[data-theme="dark"] {
  --bg-glass-nav: rgba(30, 30, 30, 0.72);
  --bg-glass-sidebar: rgba(30, 30, 30, 0.56);
  --bg-content: #1E1E1E;
  --bg-card: rgba(44, 44, 46, 0.8);
  --text-primary: #E5E6EB;
  --text-secondary: #A6A6A6;
  // ... 其他变量
}
```

### 6.2 主题切换入口

在用户头像下拉菜单中添加"亮色/暗色/跟随系统"选项。主题偏好存储在 `localStorage`，通过 Pinia theme store 管理。

### 6.3 Element Plus 暗色适配

通过 `use-element-plus-theme` 包或手动覆盖 `--el-color-*` 变量，确保所有 Element Plus 组件在暗色模式下正确显示。

---

## 7. Logo 展示

### 7.1 登录页

- 左侧区域中央放置大尺寸浪潮 logo（`logo.png`），宽度约 `200px`
- Logo 下方显示 "MaxKB" 文字和一句话 slogan

### 7.2 顶部导航栏

- 左侧放置小尺寸浪潮 logo，高度约 `32px`
- Logo 右侧显示 "MaxKB" 文字

### 7.3 文件引用

使用 `ui/src/assets/logo/logo.png` 作为 logo 源文件。

---

## 8. 需修改的核心文件

| 文件 | 改动内容 |
|------|----------|
| `ui/src/styles/variables.scss` | 新增毛玻璃 tokens、暗色变量、主色色阶 |
| `ui/src/styles/element-plus.scss` | 更新 Element Plus 覆盖（按钮、输入框、弹窗等） |
| `ui/src/styles/app.scss` | 全局过渡、动效 mixin |
| `ui/src/styles/index.scss` | 引入新增的 SCSS 文件 |
| `ui/src/layout/layout-template/index.scss` | 导航栏毛玻璃背景 |
| `ui/src/layout/layout-header/UserHeader.vue` | 导航栏布局改造 + logo 展示 |
| `ui/src/layout/layout-header/SystemHeader.vue` | 系统导航栏同步改造 |
| `ui/src/layout/components/sidebar/index.vue` | 侧边栏毛玻璃背景 |
| `ui/src/layout/components/sidebar/SidebarItem.vue` | 菜单项样式更新 |
| `ui/src/stores/modules/theme.ts` | 暗色模式支持 |
| `ui/src/utils/theme.ts` | 新增暗色主题定义 |
| `ui/src/views/login/` | 登录页全面改版 |
| `ui/src/views/home/` | 首页卡片样式更新（样板页） |
