# Types 目录说明

`src/types` 统一管理项目中可复用的 TypeScript 类型，业务代码只允许从 `@/types` 导入类型。

```text
src/types/
├── index.ts                # 唯一公共入口
├── complex-search.ts       # 组合搜索组件字段、选项和值类型
├── current-user.ts         # 当前登录用户类型
├── external-login.ts       # 第三方登录和扫码登录类型
├── filterable-dropdown.ts  # 可过滤下拉组件类型
├── layout.ts               # 应用布局和菜单类型
├── login.ts                # 普通登录、登录配置及页面交互类型
├── platform-info.ts        # 平台版本、许可和外观类型
├── request.ts              # 请求协议、分页和 loading 类型
├── router.ts               # Router 范围与 RouteMeta 扩展
├── system-user.ts          # 系统用户管理类型
└── workspace.ts            # 工作空间类型
```

## 书写规则

- `index.ts` 只负责导出各领域类型文件，不直接堆放具体类型声明。
- 类型文件按具体业务、API 资源或组件能力命名，并尽量与对应实现文件保持一致，例如
  `login.ts`、`external-login.ts`、`current-user.ts`、`workspace.ts` 和
  `filterable-dropdown.ts`；禁止使用 `api.ts`、`component.ts`、`business.ts`、`common.ts`
  等范围过大的文件名。
- 请求响应包装、分页、loading 等基础设施类型写入 `request.ts`；具体接口的请求和响应类型写入
  对应业务文件，不按“API 类型”集中。
- 公共组件类型按具体组件能力命名，例如可过滤下拉选项写入 `filterable-dropdown.ts`；新增其他
  组件类型时建立对应能力文件，不把所有组件声明集中到同一文件。
- 页面、组件、Store、Router 和 API 统一使用 `import type { ... } from '@/types'`。
- 禁止从 `@/api/**/types`、`@/components/**/types`、相对路径 `./types` 等位置导入共享类型。
- 仅在单个文件内部使用的实现类型可以就近声明，但不得导出；一旦跨文件使用，就移动到
  `src/types` 并通过 `@/types` 导入。
- 使用 `interface` 描述对象结构，使用 `type` 描述联合类型、交叉类型、工具类型结果或别名。
- 类型名称必须体现业务含义，避免使用 `Data`、`Item`、`Info` 等缺少上下文的通用名称。
