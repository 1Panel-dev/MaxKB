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

知识库类型的接口值保持为 `KNOWLEDGE_TYPE` 中的数字。`constants/knowledge.ts` 提供
`KNOWLEDGE_TYPE_MAP`，将数字转换为 `BASE`、`WEB`、`LARK`、`YUQUE`、`WORKFLOW` 字符串，
供前端判断；`KNOWLEDGE_TYPE_LABELS` 按这些字符串提供展示文案。提交接口时仍使用数字枚举值。
字符串标识统一由 `KNOWLEDGE_TYPE_KEY` 维护，映射、文案和业务判断均引用该常量，避免重复写裸字符串。

```ts
const knowledgeType = KNOWLEDGE_TYPE_MAP[knowledge.type]
const isWebKnowledge = knowledgeType === KNOWLEDGE_TYPE_KEY.WEB
const knowledgeTypeLabel = KNOWLEDGE_TYPE_LABELS[knowledgeType]
```

`resource-authorization.ts` 的 `RESOURCE_PERMISSION_OPTIONS` 统一维护权限标签和说明；
资源授权页面与资源用户授权抽屉按版本和根目录约束筛选选项。
