# constants 目录说明

`src/constants` 只存放大部分页面或多个业务模块都会使用的共享常量。只被个别页面、组件或
业务模块使用的常量，应保留在所属代码附近，不要提前提升为全局常量。

共享常量按照明确的业务领域或能力拆分文件，例如：

```text
src/constants/
├── CONSTANT_README.md
├── folder.ts
└── validation.ts
```

不要创建收集无关常量的通用文件，也不要为了统一导出而新增只做二次转发的 `index.ts`。
常量名称使用能够表达所属领域和用途的全大写命名，使用方从具体文件直接导入。

后端字段的固定枚举值不是前端展示常量，应在对应的 `src/api/enums/<domain>.ts` 中维护，并
统一从 `@/api/enums` 导入。`constants` 只维护标签、颜色、选项等前端映射；映射的键应引用
API 枚举值。例如角色类型和登录方式以 `src/api/enums` 为唯一数据源，`constants/auth.ts`
只维护它们的展示文案。
