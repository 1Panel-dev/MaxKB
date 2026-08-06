# System API

该目录按系统管理业务拆分 Admin API，例如用户、角色、工作空间、认证设置和外观设置。
每个业务使用独立文件，目录结构如下：

```text
system/
├── README.md
├── user-manage.ts
└── workspace.ts
```

- 每个接口单独导出，并在文件末尾提供默认 API 对象。
- 新增系统业务时直接创建同名 `.ts` 文件，不建立业务文件夹。
- 仅由 System API 使用的请求和响应类型保留在对应接口文件；多个 System API 文件重复使用时，
  提取到本目录的 `common.ts`。只有同一业务类型还被 View 或 Component 使用时，才移入
  `src/types` 并从 `@/types` 导入。
- 系统级资源与工作空间级同名资源分别维护，不跨业务域合并。
