# MaxKB v3 Frontend

本文是 `ui/` 的共享开发规则入口。项目采用 Vue 3.5、TypeScript 6、Vite 8、Vue Router 5、
Pinia 3、Element Plus、Tailwind CSS 4 和 Sass；工作流画布基于 LogicFlow。

## 文档分工

修改或评审前读取涉及领域的文档。每条详细规则只在所属文档维护，其他文档通过链接引用；
更新时保留当前职责、公开接口及必要约束，不记录迁移步骤、改动历史或内部函数清单。

| 文档                                                         | 负责内容                             |
| ------------------------------------------------------------ | ------------------------------------ |
| [README.md](README.md)                                       | 开发、环境变量、命令与部署           |
| [STYLE_README.md](src/styles/STYLE_README.md)                | 样式、主题、布局与 Element Plus 覆盖 |
| [COMPONENT_README.md](src/components/COMPONENT_README.md)    | 共享组件边界、接口与使用约定         |
| [API_README.md](src/api/API_README.md)                       | 请求、业务 API、类型与枚举           |
| [ROUTE_README.md](src/router/ROUTE_README.md)                | 路由、导航、认证与资源范围           |
| [VIEW_README.md](src/views/VIEW_README.md)                   | 页面职责、功能本地组织与业务约束     |
| [WORKFLOW_README.md](src/workflow-canvas/WORKFLOW_README.md) | 画布内核、节点、资源查询与接入接口   |
| [CONSTANT_README.md](src/constants/CONSTANT_README.md)       | 共享展示常量                         |
| [LOCALE_README.md](src/locales/LOCALE_README.md)             | 国际化分类、语言状态与使用约定       |
| [UTILS_README.md](src/utils/UTILS_README.md)                 | 共享工具函数与组合式函数             |

新增专题规则文档时补充此索引；仅在目录、公开接口或使用规则变化时同步对应章节。
文档描述当前工作区的实现；已有未提交改动不得擅自覆盖或回退。

## 目录职责

| 位置                                    | 职责                                                     |
| --------------------------------------- | -------------------------------------------------------- |
| `admin.html` → `src/main.ts`            | Admin 入口                                               |
| `chat.html` → `src/chat.ts`             | Chat 入口，包含单应用与门户对话                          |
| `env/`                                  | 各入口环境配置                                           |
| `src/api/`                              | Admin / Chat 请求、业务接口、共享类型与后端枚举          |
| `src/components/`                       | 全局 UI、显式导入的共享 UI 与跨页面业务组件              |
| `src/layout/`                           | 应用头部、侧栏与资源详情布局                             |
| `src/views/`                            | 路由页面及功能本地代码；全屏画布页面在 `views/workflow/` |
| `src/conversation-panel/`               | 对话装配、流式处理、组件与局部状态                       |
| `src/workflow-canvas/`                  | LogicFlow、节点、画布配置与资源查询适配器                |
| `src/router/`                           | Admin / Chat 独立 Router                                 |
| `src/stores/admin/`、`src/stores/chat/` | 各入口独立 Pinia 实例和 Store                            |
| `src/permission/`                       | 权限策略、业务权限方法及 Admin `$perm` 插件              |
| `src/locales/`                          | 三语语言包、命名空间与各入口国际化初始化                 |
| `src/styles/`                           | 全局样式、主题变量与第三方样式集成                       |
| `src/constants/`、`src/utils/`          | 跨功能常量与工具                                         |
| `src/assets/`、`public/`                | 源码导入资源／需要保留原文件名和 URL 的静态文件          |

国际化基础及分类规则见 [LOCALE_README.md](src/locales/LOCALE_README.md)。文件放入现有功能边界，不创建平行的顶层结构。
各入口复用自己的 Pinia：Admin 使用 `@/stores/admin`，Chat 使用 `@/stores/chat` 的 `useStore()`；
Store 内部协调状态时可直接引用同入口的具体 Store，避免聚合入口循环依赖。
`src/stores/index.ts` 当前是 Admin 兼容入口，不能用它获取 Chat Store。

## 通用开发约束

- 新功能未经用户明确要求不增加权限判断；保留范围外既有权限逻辑。
- 未经用户明确指令不修改共享组件实现；具体边界见组件文档。
- 不编写 `aria-label`；操作入口前添加简短中文 HTML 用途注释，细则见组件文档。
- 变更现有行为前追踪调用流程与依赖；可能删除已有要求或引入回归时，先说明风险和安全方案，等待确认。
- Vue、Vue Router、Pinia API 显式导入，不恢复 API 自动导入。
- 深拷贝使用 Lodash `cloneDeep`，不使用 `structuredClone`。
- 类型化、数据驱动；变量以领域和用途命名，不使用脱离上下文的 `items`、`list`。
- 共享规则与功能本地实现分别按专题文档维护，不为单页需求提前提升公共代码。
- 不手工修改 `src/components.d.ts` 等生成文件，通过正常开发或构建流程生成。

## Import 顺序

`src/main.ts` 和 `src/chat.ts` 两个入口的现有顺序必须始终保留，包括 import、样式加载、
初始化和插件注册。新增代码也须保留已有语句的相对顺序，手工修改及自动修复均不得重排。

其余 Vue / TypeScript 文件按以下顺序排列导入，组间不加空行：

1. 框架与第三方依赖；`vue`、`vue-router`、`pinia` 固定优先，其他按路径排序。
2. 所有来源的 `import type` 集中排列，然后是 `@/api/enums` 枚举，最后是 API。
3. 组件与功能依赖：先 `@/` 共享组件和功能模块，再相对路径依赖。
4. 公共模块：常量、Store、工具、路由、国际化等。
5. `@/permission` 或其 `index.ts` 入口固定最后。

组内路径和命名导入成员按字母序排列；混合导入中的显式 `type` 成员拆为 `import type`。
不改写路径或导入别名。无绑定导入（如样式和初始化模块）、执行语句及注释作为排序边界，
保留其顺序与关联；带内部注释的导入声明保留成员写法。
仅含 inline type 成员的值导入保留原写法，避免改为 `import type` 后丢失模块初始化副作用。
规则由 `eslint-rules/import-order.mjs` 实现，通过 `npx eslint <文件或目录> --fix` 自动整理。
生成的声明文件不参与手工整理。

## 验证

只改文档：核对代码、路径引用、Prettier 格式及 `git diff --check`。
Vue / TypeScript 改动：运行定向 ESLint 和 `npm run type-check`；影响入口或构建时增加对应生产构建。
命令、Node 版本和 `lint` 脚本现状见 [README.md](README.md)。
