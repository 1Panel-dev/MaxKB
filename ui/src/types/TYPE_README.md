# Types 目录说明

本文档是 TypeScript 类型归属、复用和去重规则的唯一依据。

`src/types` 不集中存放所有类型，只存放同时被 API 层和对应 View 或 Component 使用的跨层业务
类型。API、Router、Layout、View 或 Component 内部专用的类型，应保留在所属目录或实现文件
中。

## 判断流程

新增或移动类型前，按以下顺序判断：

1. 只在一个文件中使用：直接在该文件中声明，不导出。
2. 只在同一个业务边界内跨文件使用：放在该边界的 `types.ts`；存在多处重复声明时，提取到
   最近共同目录的 `common.ts`。
3. 只属于 API、Router 或 Layout：分别放在 `api`、`router` 或 `layout` 的对应目录中，不放入
   `src/types`。
4. 同一个业务类型同时被 API 和 View 或 Component 使用：放入 `src/types/<domain>.ts`，通过
   `src/types/index.ts` 导出，使用方统一从 `@/types` 导入。

Store 或其他模块需要某个类型时，仍按类型的业务所有权判断位置，不能仅因“跨文件使用”就移入
`src/types`。

## 各目录的类型归属

- API 专用的请求参数、响应包装、请求配置和基础设施类型，放在对应 API 文件、资源目录的
  `types.ts`，或该 API 业务域的 `common.ts`。
- Router 专用的 `RouteMeta` 扩展、路由 Scope 和导航生成类型，放在 `src/router` 的对应目录。
- Layout 专用的布局模式、菜单和应用框架类型，放在 `src/layout` 的对应目录。
- View 专用类型放在页面文件或所属功能目录；Component 专用类型放在组件实现或组件目录。
- 只有 API 返回或接收的业务模型还需要被 View 或 Component 直接使用时，才提升到
  `src/types`。

## `src/types` 结构

```text
src/types/
├── index.ts                # 跨层共享类型的唯一公共入口
├── common.ts               # 多个公共组件共同使用的通用选项类型
├── login.ts                # 认证 API 与登录页面共用的业务类型
├── system-user.ts          # 系统用户 API 与用户管理页面共用的业务类型
└── workspace.ts            # 当前用户与工作空间 API 共用的业务类型
```

不要为了匹配示例创建空文件。

## 去重规则

- 新增类型前先搜索是否已有等价声明，优先复用或扩展已有类型。
- 同一业务边界内出现重复类型时，提取到最近共同目录的 `common.ts`，使用方从该文件导入。
- `common.ts` 只收纳该目录下多个文件真正共用的类型，不得成为无关声明的集合。
- API 与 View/Component 出现同一业务类型时，不保留两份声明；将唯一声明移到
  `src/types/<domain>.ts`。
- 名称相同但业务含义或字段约束不同的类型不要强行合并，应使用明确的领域名称区分。

## 导入与书写规则

- `src/types/index.ts` 只导出跨层共享类型，不直接声明类型。
- 使用方统一从 `@/types` 导入 `src/types` 中的类型；领域内部类型从所属文件直接导入，不通过
  `src/types/index.ts` 二次转发。
- 类型文件按明确业务域命名。`common.ts` 仅用于已经确认的重复声明，不作为默认文件名。
- 使用 `interface` 描述对象结构，使用 `type` 描述联合类型、交叉类型、工具类型结果或别名。
- 类型名称必须体现业务含义，避免使用 `Data`、`Item`、`Info` 等缺少上下文的通用名称。
