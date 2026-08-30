# styles 本地说明

本文档是项目样式规则的唯一依据。涉及布局、间距、尺寸、排版、颜色、主题、Tailwind、Sass 或 Element Plus 样式的修改，应先阅读本文档。

本项目由 Vite 原生处理 Sass，不要添加 Webpack 使用的 `sass-loader`。

## 文件职责与加载顺序

- `tailwind.css`：引入 Tailwind 并映射 Tailwind 主题 Token。
- `index.scss`：仅作为全局 Sass 聚合入口。
- `variables.scss`：统一定义 `--mk-*` 运行时主题变量。
- `element-plus.scss`：配置 Element Plus Sass，并将其 CSS 变量映射到项目主题变量。
- `app.scss`：定义字体、基础元素样式和应用级默认样式。

`tailwind.css` 内部按照 `@import`、`@theme`、`@custom-variant`、`@layer base`、
`@layer components`、`@utility` 的顺序组织；不存在的部分直接省略。`@theme` 内部按照颜色、
背景图片、间距、排版分组，每组通过注释标明职责，不将不同类型的 Token 混合排序。

`src/main.ts` 和 `src/chat.ts` 应按以下顺序加载样式：

```ts
import 'element-plus/dist/index.css'
import './styles/tailwind.css'
import './styles/index.scss'
```

项目样式必须位于 Element Plus 官方样式之后，确保 `element-plus.scss` 中的 CSS 变量映射可以生效。Tailwind 必须与 Sass 入口分开，不要在 `index.scss` 中引入 Tailwind，避免 Tailwind 经过 Sass 处理而产生构建警告或错误结果。

## 基础样式

不要使用会影响所有元素间距的宽泛重置规则，例如：

```scss
* {
  margin: 0;
  padding: 0;
}
```

这类规则会破坏 Element Plus 组件的默认间距。仅设置必要的基础规则，例如统一 `box-sizing`、清除 `body` 默认外边距和定义应用级布局。

## 默认字号

项目正文和大部分界面文字默认使用 `14px / 22px`（字号/行高），统一由 `variables.scss` 中的 `--mk-font-size-base` 和 `--mk-line-height-base` 提供，`body` 直接使用这两个变量。

Tailwind 在 `tailwind.css` 中显式重写了项目字号及对应行高：

| Tailwind 类 | 字号 | 行高 | 配置来源                                        |
| ----------- | ---- | ---- | ----------------------------------------------- |
| `text-sm`   | 12px | 20px | Tailwind 固定值                                 |
| `text-base` | 14px | 22px | `--mk-font-size-base` / `--mk-line-height-base` |
| `text-lg`   | 16px | 24px | Tailwind 固定值                                 |
| `text-xl`   | 18px | 26px | Tailwind 固定值                                 |

使用字号工具类时会同时应用表中的字号和行高。例如，`text-lg` 等价于 `font-size: 16px; line-height: 24px`。

普通正文直接继承 `body` 的 `14px / 22px`，不需要重复添加 `text-base`。仅在元素需要明确覆盖继承字号或行高时使用以上工具类；如设计稿对行高另有明确要求，再使用 `leading-*` 单独覆盖。

## 标题层级

全局标题样式统一定义在 `app.scss`。业务页面按照内容层级直接使用 `h1` 至 `h6`，不再重复添加
字号、行高和字重 class：

| 标签 | 设计层级 | 字号/行高 | 字重 |
| ---- | -------- | --------- | ---- |
| `h1` | 一级标题 | 24px/32px | 600  |
| `h2` | 二级标题 | 20px/28px | 500  |
| `h3` | 三级标题 | 18px/26px | 500  |
| `h4` | 四级标题 | 16px/24px | 500  |
| `h5` | 五级标题 | 16px/24px | 400  |
| `h6` | 辅助标题 | 14px/22px | 500  |

标题默认清除浏览器 margin。布局、颜色、省略等非排版需求仍可通过 class 补充：

```html
<h1>页面标题</h1>
<h2 class="truncate text-primary" title="完整的内容标题">完整的内容标题</h2>
```

设计规范中的特大标题为 `30px/38px/600`，仅用于特殊页面级展示，不占用 `h1` 至 `h6`
的常规内容层级。

## 文本省略

使用 `truncate`、`line-clamp-*` 等工具类省略文本时，必须在同一元素补充原生 `title` 属性，
使鼠标悬停时可以查看完整内容。动态文本使用 `:title` 绑定，组合文本应复用同一个格式化结果，
确保页面显示内容与 `title` 完全一致。

```vue
<span class="truncate" :title="workspace.name">{{ workspace.name }}</span>
<p class="line-clamp-2" :title="description">{{ description }}</p>
```

## 样式实现优先级

- 业务组件的布局、间距、尺寸、排版、颜色和常见交互状态优先使用 Tailwind 工具类。
- 能直接组合工具类表达时，不要新增仅供单个元素使用的自定义 class，也不要为其新增 `<style>` 规则。
- Element Plus 组件可通过 `class`、`popper-class` 等属性直接传入 Tailwind 工具类；覆盖组件默认样式时按需使用 Tailwind 的 `!` important 修饰符。
- `el-avatar` 内部图片默认宽度为 `100%`；需要改变图片宽度时，统一在 `img` 上使用行内 `style="width: ..."`。
- 仅在 Tailwind 无法清晰表达、必须使用复杂选择器、需要深层穿透，或样式确实会被多处共享时编写 Sass/CSS。此时 class 应使用有业务含义的名称，组件样式默认保持 `scoped`。
- 运行时主题颜色仍以 `variables.scss` 的 `--mk-*` 变量为唯一数据源，并优先使用已映射的 `text-N900`、`text-N600`、`bg-primary` 等语义工具类。
- 只添加会实际改变当前布局、样式或交互的 class。不要习惯性追加无效或重复的工具类；添加前应结合元素默认样式、父级布局和现有 class 判断其是否必要。

CSS、SCSS 先按照 `/* button */`、`/* dropdown */` 等业务注释划分样式分组，每个注释及其
下方相关样式视为一个整体。业务分组之间按照项目确定的组件优先级、基础依赖和现有业务顺序
排列，不按业务名称字母排序，也不能为了格式化移动整个业务分组。新增样式应放入所属的现有
业务分组；没有对应分组时，再根据业务优先级确定新分组位置。

同一业务分组内部的选择器按名称字母顺序排列；同一声明块内的属性按属性名字母顺序排列，
CSS 自定义属性同样按变量名排序。嵌套选择器、伪类和媒体查询放在普通属性声明之后。

示例：

```vue
<div class="flex items-center gap-2 rounded-md px-3 py-2 text-N900 hover:bg-gray-100">
  菜单项
</div>
```

## 常用布局工具类

稳定重复使用的布局组合统一定义在 `tailwind.css`。当前提供：

| 工具类            | 作用                                       |
| ----------------- | ------------------------------------------ |
| `absolute-center` | 绝对定位，相对最近的定位祖先水平和垂直居中 |
| `flex-between`    | 横向排列，两侧贴边，并在垂直方向居中       |
| `flex-center`     | 横向排列，在水平和垂直两个方向居中         |
| `flex-col-center` | 纵向排列，在水平和垂直两个方向居中         |
| `flex-wrap`       | 横向排列，自动换行，行间距为 8px           |

```vue
<div class="relative h-40">
  <div class="absolute-center">居中内容</div>
</div>

<div class="flex-between">
  <span>左侧</span>
  <span>右侧</span>
</div>

<div class="flex-center">
  <span>居中内容</span>
</div>

<div class="flex-col-center">
  <MkIcon name="icon_home_filled" />
  <span>首页</span>
</div>

<div class="flex-wrap">
  <span>选项一</span>
  <span>选项二</span>
</div>
```

仅在布局语义与工具类完全一致时使用。需要覆盖排列方向或对齐方式的响应式布局继续组合 Tailwind
原子类，不为少量差异继续增加相似工具类。

## 常用交互工具类

`group-hover-visible` 用于列表项、卡片等父级带有 `group` 的悬浮操作区。操作区默认透明且不响应
鼠标事件；距离操作区最近的 `group` 悬浮或内部获得焦点时显示并恢复交互，外层 `group` 不会越过
内层 `group` 触发操作区。该工具类只负责显隐，布局继续由使用方组合。

```html
<div class="group">
  <div>始终显示的内容</div>
  <div class="group-hover-visible ml-auto flex items-center">悬浮操作</div>
</div>
```

## 状态圆点

成功与失败状态的圆点样式统一由 `app.scss` 提供。根据业务状态使用 `mk-dot-success` 或
`mk-dot-danger`，文字和圆点的布局继续由使用方通过 Tailwind 组合。

```html
<span class="inline-flex items-center gap-2">
  <span class="mk-dot-success"></span>
  <span>成功</span>
</span>
```

## 进行中动态点

进行中状态文案使用全局 `mk-dotting` 类，通过 `::after` 生成循环变化的省略号。类名直接放在
文案元素上，不额外添加仅用于点号的空节点；伪元素预留固定宽度，避免动画过程中正文位置抖动。

```html
<span class="mk-dotting">下载中</span>
```

## Tailwind 中的 `p`（padding）

- Tailwind 默认间距标尺中，`1` 个单位等于 `0.25rem`。
- 在浏览器根字号为默认的 `16px` 时：`0.25rem = 4px`。
- 因此，`p-1` 即 `4px`，`p-2` 即 `8px`。

在 Sass/CSS 中覆盖 Element Plus 等第三方组件时，属性值能够自然对应 Tailwind 4px 基础
间距刻度时使用 `--spacing` 计算，包括 `padding`、`margin`、`gap` 以及基于间距刻度的
宽高。设计稿明确给出的 5px、7px、9px、11px、13px、18px、34px 等非 4px 整数倍值直接
使用 `px`，不要为了使用 `--spacing` 而换算成小数倍数。例如：

```scss
.example {
  gap: calc(var(--spacing) * 2);
  min-width: calc(var(--spacing) * 20);
  padding: 7px calc(var(--spacing) * 3);
}
```

圆角、边框宽度、字体尺寸、阴影偏移等不使用 Tailwind spacing scale 的固定尺寸使用 `px`；
零值直接写 `0`，不要写 `0px`。

## 滚动区域

组件内需要展示滚动条时优先使用 Element Plus 的 `el-scrollbar`，保持滚动条样式和交互一致。

## 布局尺寸

头部高度统一使用 Tailwind 的 `h-header`，侧边栏和主内容区域的高度统一使用
`h-layout-content`。侧边栏宽度使用 `w-sidebar` 和 `w-sidebar-expanded`。这些类通过
`tailwind.css` 的 `@theme` 映射到 `variables.scss` 中的布局变量。

侧边栏最窄宽度统一使用 `variables.scss` 中的 `--mk-sidebar-width`，系统侧边栏展开宽度
使用 `--mk-sidebar-expanded-width`。组件中通过对应的语义化 Tailwind 类引用，不要重复
写入 `68px`、`240px` 或对应的 Tailwind 固定宽度类。

Vue/HTML 标签的 `class` 和 `:class` 中禁止出现 `var()` 或基于 `var()` 的任意值写法。
需要引用 CSS 变量时，先在 `tailwind.css` 的 `@theme` 中注册语义化 Token，再使用生成的
Tailwind 类。

## 关于颜色变量

项目颜色变量统一定义在 `variables.scss` 中。业务代码以 `--mk-*` 变量为颜色数据源，不要在 Element Plus、Tailwind 和组件样式中分别维护同一个颜色值。

### 中性色文字 Token

`N900`、`N600` 沿用 Figma 原型中的 代号，代码与设计稿保持一致，不要自行改成其他命名：

| Figma Token | CSS 变量    | Tailwind 类 | 常用语义             |
| ----------- | ----------- | ----------- | -------------------- |
| `N900`      | `--mk-N900` | `text-N900` | 默认文字、主要内容   |
| `N600`      | `--mk-N600` | `text-N600` | 提示、说明和描述文字 |

示例：

```html
<p class="text-N900">默认正文</p>
<p class="text-N600">提示或描述信息</p>
```

这里描述的是一般使用原则；如果 Figma 对具体组件给出了明确颜色标注，应以对应原型为准。

### 主题色

当前主题色为：

```scss
:root {
  --mk-primary: #3370ff;
  --mk-primary-gradient-end: #7f3bf5;
  --mk-primary-gradient: linear-gradient(180deg, var(--mk-primary) 0%, var(--mk-primary-gradient-end) 100%);
  --mk-primary-rgb: 51 112 255;
}
```

修改主题色时，修改 `--mk-primary`。如果代码使用了 RGB 通道变量，也要同步修改 `--mk-primary-rgb`：
`--mk-primary-gradient` 是 CSS 渐变背景入口，`--mk-primary-gradient-end` 是 SVG 渐变终点。

运行时主题统一通过 Theme Store 的 `setTheme()` 更新。默认主题移除运行时的渐变变量覆盖，使用
`variables.scss` 中的蓝紫渐变；非默认主题将 `--mk-primary-gradient` 和
`--mk-primary-gradient-end` 都设为当前主题色，使 CSS 背景和 SVG 渐变统一显示为纯色。业务代码
不要直接写这些变量，也不要绕过项目变量写入 Element Plus 的 `--el-*` 主题变量。Element Plus
色阶继续由 `element-plus.scss` 基于 `--mk-primary` 映射生成。

普通 CSS 中直接使用：

```scss
.link {
  color: var(--mk-primary);
}
```

### Tailwind

`tailwind.css` 通过 Tailwind v4 的 `@theme` 将项目颜色变量注册为 Tailwind 颜色：

```css
@theme {
  --color-primary: var(--mk-primary);
}
```

变量名称与工具类名称的对应关系如下：

| Tailwind Token       | 来源变量       | 工具类后缀   |
| -------------------- | -------------- | ------------ |
| `--color-mk-primary` | `--mk-primary` | `mk-primary` |

`--color-*` 注册后可以组合生成文字、背景、边框、轮廓等颜色工具类：

```html
<button class="bg-primary text-white">确认</button>
<a class="text-primary">链接文字</a>
<div class="border border-primary">主题色边框</div>
<input class="outline-primary" />
```

交互状态直接添加 Tailwind 状态前缀：

```html
<button class="bg-primary hover:bg-primary/90 focus:ring-2 focus:ring-primary">确认</button>
```

在颜色类后添加 `/透明度`，可以使用主题色叠加透明效果：

```html
<div class="bg-primary/10">10% 主题色背景</div>
<div class="border border-primary/30">30% 主题色边框</div>
<span class="text-primary/70">70% 主题色文字</span>
```

透明度也可以使用任意值：

```html
<div class="bg-primary/[0.08]">8% 主题色背景</div>
```

业务组件优先使用这些语义类，不要直接写颜色值：

````

### 默认边框色

Tailwind v4 的 `border` 只设置边框宽度和样式，不提供 `--tw-border-color`。项目在
`tailwind.css` 的 `@layer base` 中，将默认 `border-color` 设置为 Element Plus 的
`--el-border-color`；该变量映射到 `--mk-N350`。

因此单独使用 `border` 时会与 Element Plus 组件保持一致；`border-primary`、
`border-black/15` 等显式颜色类仍会覆盖默认颜色。

### Tailwind 渐变背景

渐变值属于背景图片，不能注册到只接受普通颜色的 `--color-*` 命名空间。需要使用 `--background-image-*`：

例如：
```css
@theme {
  --background-image-layout-gradient: var(--mk-layout-gradient);
}
````

注册后通过 `bg-layout-gradient` 使用：

```html
<div class="bg-layout-gradient">页面布局</div>
```

`--mk-primary-gradient` 在默认主题下是渐变、非默认主题下是纯色，不能注册为只生成
`background-image` 的 Token。项目通过自定义 Utility 使用 `background` 简写同时兼容两种值：

```css
@utility bg-primary-gradient {
  background: var(--mk-primary-gradient);
}
```

需要主题渐变或主题纯色自动切换的背景统一使用 `bg-primary-gradient`。

### Element Plus

`element-plus.scss` 已将 `--el-color-primary` 映射到 `--mk-primary`，按钮、链接、选中态等 Element Plus 组件会自动使用主题色。

所有 `el-button` 的 `:active` 和 `.is-active` 视觉统一复用各自的 hover 样式，不额外加深背景、
边框或文字颜色；普通、plain、text、link、circle 及各语义类型按钮均遵循该规则。

Element Plus 所需的 `light-3` 至 `light-9` 和 `dark-2` 色阶使用 `color-mix()` 根据主题色生成。业务代码通常不需要直接修改 `--el-color-primary-*`。

项目内所有 Select 下拉弹层统一隐藏 Popper 箭头，并将 Element Plus 默认的 `12px` 偏移回收
`8px`，使触发器与弹层保持 `4px` 间距。该规则由 `element-plus.scss` 中的
`.el-select__popper` 统一维护，业务组件不需要重复传入 `show-arrow`、`offset` 或
`popper-class`。

Steps 默认使用数字和标题横向排列，并保留 Element Plus 的 `active` 状态管理。Steps 放在
Drawer 的 `header` 插槽内时，组合 `absolute-center` 和宽度工具类即可相对完整 Header 居中，
不受左侧标题和右侧关闭按钮影响。

```vue
<el-steps :active="0" class="absolute-center w-75!">
  <el-step title="选择供应商" />
  <el-step title="添加模型" />
</el-steps>
```

### 普通 CSS 中叠加透明度

使用 `color-mix()`，只依赖一个主题色变量：

```scss
.selected {
  background: color-mix(in srgb, var(--mk-primary) 10%, transparent);
  border-color: color-mix(in srgb, var(--mk-primary) 30%, transparent);
}
```

需要明确的 RGB alpha 写法时，可以使用 RGB 通道变量：

```scss
.selected {
  background: rgb(var(--mk-primary-rgb) / 10%);
}
```

### 后续切换主题

主题通过覆盖 `--mk-*` 变量实现，业务组件、Tailwind 和 Element Plus 会同步更新。

## 修改后检查

完成配置或样式修改后运行：

```bash
npm run type-check
npm run build-only
npm run build-only-chat
```
