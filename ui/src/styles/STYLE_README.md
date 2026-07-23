# styles 本地说明

本文档是项目样式规则的唯一依据。涉及布局、间距、尺寸、排版、颜色、主题、Tailwind、Sass 或 Element Plus 样式的修改，应先阅读本文档。

本项目由 Vite 原生处理 Sass，不要添加 Webpack 使用的 `sass-loader`。

## 文件职责与加载顺序

- `tailwind.css`：引入 Tailwind 并映射 Tailwind 主题 Token。
- `index.scss`：仅作为全局 Sass 聚合入口。
- `variables.scss`：统一定义 `--mk-*` 运行时主题变量。
- `element-plus.scss`：配置 Element Plus Sass，并将其 CSS 变量映射到项目主题变量。
- `app.scss`：定义字体、基础元素样式和应用级默认样式。

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

## 样式实现优先级

- 业务组件的布局、间距、尺寸、排版、颜色和常见交互状态优先使用 Tailwind 工具类。
- 能直接组合工具类表达时，不要新增仅供单个元素使用的自定义 class，也不要为其新增 `<style>` 规则。
- Element Plus 组件可通过 `class`、`popper-class` 等属性直接传入 Tailwind 工具类；覆盖组件默认样式时按需使用 Tailwind 的 `!` important 修饰符。
- 仅在 Tailwind 无法清晰表达、必须使用复杂选择器、需要深层穿透，或样式确实会被多处共享时编写 Sass/CSS。此时 class 应使用有业务含义的名称，组件样式默认保持 `scoped`。
- 运行时主题颜色仍以 `variables.scss` 的 `--mk-*` 变量为唯一数据源，并优先使用已映射的 `text-N900`、`text-N600`、`bg-primary` 等语义工具类。
- 只添加会实际改变当前布局、样式或交互的 class。不要习惯性追加无效或重复的工具类；添加前应结合元素默认样式、父级布局和现有 class 判断其是否必要。

CSS、SCSS 同一声明块内的属性统一按属性名字母顺序排列。CSS 自定义属性同样按变量名排序；
嵌套选择器、伪类和媒体查询放在普通属性声明之后。

示例：

```vue
<div class="flex items-center gap-2 rounded-md px-3 py-2 text-N900 hover:bg-gray-100">
  菜单项
</div>
```

## Tailwind 中的 `p`（padding）

- Tailwind 默认间距标尺中，`1` 个单位等于 `0.25rem`。
- 在浏览器根字号为默认的 `16px` 时：`0.25rem = 4px`。
- 因此，`p-1` 即 `4px`，`p-2` 即 `8px`。

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
  --mk-primary-rgb: 51 112 255;
}
```

修改主题色时，修改 `--mk-primary`。如果代码使用了 RGB 通道变量，也要同步修改 `--mk-primary-rgb`：

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

### Tailwind 渐变背景

渐变值属于背景图片，不能注册到只接受普通颜色的 `--color-*` 命名空间。需要使用 `--background-image-*`：

```css
@theme {
  --background-image-layout-gradient: var(--mk-layout-gradient);
}
````

注册后通过 `bg-layout-gradient` 使用：

```html
<div class="bg-layout-gradient">页面布局</div>
```

### Element Plus

`element-plus.scss` 已将 `--el-color-primary` 映射到 `--mk-primary`，按钮、链接、选中态等 Element Plus 组件会自动使用主题色。

Element Plus 所需的 `light-3` 至 `light-9` 和 `dark-2` 色阶使用 `color-mix()` 根据主题色生成。业务代码通常不需要直接修改 `--el-color-primary-*`。

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
  box-shadow: 0 4px 12px rgb(var(--mk-primary-rgb) / 20%);
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
