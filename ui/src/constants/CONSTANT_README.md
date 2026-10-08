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
`KNOWLEDGE_TYPE_MAP`，将数字转换为 `BASE`、`WEB`、`LARK`、`WORKFLOW` 字符串，
供前端判断及知识库详情路由 `type` 参数使用，地址不传数字；`KNOWLEDGE_TYPE_LABELS` 按这些字符串提供展示文案。提交接口时仍使用数字枚举值。
字符串标识统一由 `KNOWLEDGE_TYPE_KEY` 维护，映射、文案和业务判断均引用该常量，避免重复写裸字符串。

```ts
const knowledgeType = KNOWLEDGE_TYPE_MAP[knowledge.type]
const isWebKnowledge = knowledgeType === KNOWLEDGE_TYPE_KEY.WEB
const knowledgeTypeLabel = KNOWLEDGE_TYPE_LABELS[knowledgeType]
```

`resource-authorization.ts` 的 `RESOURCE_PERMISSION_OPTIONS` 统一维护权限标签和说明；
资源授权页面与资源用户授权抽屉按版本和根目录约束筛选选项。

`knowledge.ts` 的 `KNOWLEDGE_SYNC_OPTIONS` 统一维护增量同步、替换同步和整体同步的值、文案及说明，
手动同步弹窗与定时同步设置直接复用，日志同步方式标签也从这些选项读取。

`schedule.ts` 的 `SCHEDULE_OPTION` 统一提供触发器、长期记忆与知识库定时同步的周期级联选项，
包含周期文案、执行时间和间隔数值；使用方只读，配置回填与校验仍由各自组件维护。
周期类型统一使用 `api/enums/schedule.ts` 的 `SCHEDULE_TYPE`，经 `@/api/enums` 导入。

`state.ts` 的 `EXECUTION_STATUS_OPTIONS` 维护触发器、工具和知识库工作流执行记录共用的
中文文案与图标类型，仅包含 `PENDING`、`STARTED`、`SUCCESS`、`FAILURE`、`REVOKE`、
`REVOKED`、`TRIGGER_ERROR` 七种接口状态，列表筛选及执行详情复用该配置。新增状态只需在业务配置中补齐展示，
不修改 `MkStatusLabel`。文档任务使用 `views/knowledge-detail/library/document/status.ts` 的独立配置，
筛选查询仍映射 `DOCUMENT_TASK_STATE` 与 `DOCUMENT_TASK_TYPE`，不提交展示状态键。

`document.ts` 的 `DOCUMENT_HIT_HANDLING_LABELS` 维护文档命中处理方式的展示文案，
映射键引用 API 枚举 `DOCUMENT_HIT_HANDLING`。

`file-type.ts` 维护图片、文档、视频和音频的文件扩展名常量，扩展名统一使用大写。
使用方判断文件类型时先将后缀转换为大写，再与对应常量匹配。
