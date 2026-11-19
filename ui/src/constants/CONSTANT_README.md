# constants 目录说明

`src/constants` 只存放大部分页面或多个业务模块都会使用的共享常量。只被个别页面、组件或
业务模块使用的常量，应保留在所属代码附近，不要提前提升为全局常量。

共享常量按明确业务领域或能力拆分，不维护会过时的逐文件目录树。

不要创建收集无关常量的通用文件，也不要为了统一导出而新增只做二次转发的 `index.ts`。
常量名称使用能够表达所属领域和用途的全大写命名，使用方从具体文件直接导入。

`folder.ts` 的 `FOLDER_ENTRY_ID.ALL` 在读取时取当前路由的工作空间 ID，无工作空间上下文时使用 `default`。
共享入口的 `FOLDER_ENTRY_ID.SHARED` 固定为 `shared`。目录名称的翻译归属见[国际化规则](../locales/LOCALE_README.md#文件夹)。

后端枚举与类型归属统一见 [API_README.md](../api/API_README.md#枚举与类型组织)。`constants` 只维护标签、颜色、选项等前端映射；映射的键应引用
API 枚举值。例如角色类型和登录方式以 `src/api/enums` 为唯一数据源，`constants/auth.ts`
只维护它们的展示文案。
共享展示配置使用 `reactive` 包裹对象或数组，动态文案属性直接使用 `computed(() => t('...'))`。
调用方按普通属性读取译文，无需 `.value` 或再次调用 `t`；不增加翻译 key 属性、平行 key 映射或翻译辅助函数。
配置只读，首次读取文案必须在入口完成 `createAppI18n` 之后；依赖语言的复制、映射应留在 computed 或执行时，不能在模块顶层取出文案快照。
登录方式共用 `LOGIN_METHOD_LABELS`，角色类型共用 `ROLE_TYPE_LABELS`，分别按 API 枚举读取 `auth.methods` 和 `role.types`。
用户来源的本地创建／本地导入名称由对应业务覆盖，未知来源保留接口原文；筛选选项保留协议值与既有顺序。
`SCAN_FIELD_LABELS` 只维护扫码配置中的固定英文参数名；回调地址单独展示并直接使用 `auth.fields.callbackUrl.label`。

知识库类型的接口值保持为 `KNOWLEDGE_TYPE` 中的数字。`constants/knowledge.ts` 提供
`KNOWLEDGE_TYPE_MAP`，将数字转换为 `BASE`、`WEB`、`LARK`、`WORKFLOW` 字符串，
供前端判断及知识库详情路由 `type` 参数使用，地址不传数字；类型名称与说明读取 `knowledge.base`、
`knowledge.web`、`knowledge.lark` 和 `knowledge.workflow` 的翻译。提交接口时仍使用数字枚举值。
字符串标识统一由 `KNOWLEDGE_TYPE_KEY` 维护，映射、文案和业务判断均引用该常量，避免重复写裸字符串。

`model.ts` 的 `MODEL_TYPE_LABELS` 提供模型类型的响应式名称，供模型业务、系统模型页、工作流默认模型设置和动态表单模型控件使用；协议值保持不变。

`tool.ts` 的 `TOOL_TYPE_OPTIONS` 为工作空间及系统工具列表提供有序的 `value` 和 `label`，筛选继续使用原 `value`，“全部”对应空字符串。

`resource-authorization.ts` 的 `RESOURCE_PERMISSION_OPTIONS` 统一维护权限协议值、`label` 和可选的 `description`；资源授权页面与抽屉按版本和根目录约束筛选，名称和说明归 `authorization.permission`。

`knowledge.ts` 的 `KNOWLEDGE_SYNC_OPTIONS` 提供同步方式的协议值、响应式名称和说明；手动同步、定时同步和同步日志共用。
`KNOWLEDGE_SEARCH_MODE_OPTIONS` 统一维护向量、全文和混合检索的 `value`、`label` 和 `description`，选项值引用 `KNOWLEDGE_SEARCH_MODE`，文案归 `knowledge.retrieval`；召回测试、智能体设置与工作流知识库检索节点直接读取。

`knowledge.ts` 的 `KNOWLEDGE_IMAGE_EXTENSIONS` 维护知识库上传和召回测试支持的图片扩展名，
`KNOWLEDGE_IMAGE_ACCEPT` 和 `KNOWLEDGE_IMAGE_TYPE_LABEL` 由它派生，供文件选择、校验与提示使用。
此配置独立于聊天、工作流等场景使用的通用文件类型配置。

`schedule.ts` 的 `SCHEDULE_OPTION` 统一提供触发器、长期记忆与知识库定时同步的周期级联选项，
包含周期文案、执行时间和间隔数值；使用方只读，配置回填与校验仍由各自组件维护。
周期、星期及间隔单位的 `label` 随语言更新，每月日期由数字和日期单位组合；调用方直接读取，不重复映射翻译或修改共享选项及其子项。
周期类型统一使用 `api/enums/schedule.ts` 的 `SCHEDULE_TYPE`，经 `@/api/enums` 导入。

`state.ts` 的 `EXECUTION_STATUS_OPTIONS` 维护触发器、工具和知识库工作流执行记录共用的响应式 `label` 与图标类型，包含 `PENDING`、`STARTED`、`SUCCESS`、`FAILURE`、`REVOKE`、`REVOKED`、`TRIGGER_ERROR` 七种接口状态。
通用状态文案归 `common.status`，触发失败归 `resource.executionRecords.status.triggerFailed`。新增状态在业务配置中补齐展示，不修改 `MkStatusLabel`。
文档任务使用 `views/knowledge-detail/library/document/status.ts` 的独立配置，筛选查询仍映射 `DOCUMENT_TASK_STATE` 与 `DOCUMENT_TASK_TYPE`，不提交展示状态键。

`document.ts` 的 `DOCUMENT_HIT_HANDLING_LABELS` 按 API 枚举 `DOCUMENT_HIT_HANDLING` 提供响应式名称，文档和图片的列表筛选、表格单元格及文档设置共用。
`DOCUMENT_SPLIT_PATTERNS` 保存与后端一致的固定标识及正则值，供工作流 Agent 识别参数，不随语言变化。
`DOCUMENT_SPLIT_PATTERN_OPTIONS` 在同一文件提供文档策略表单与工作流分段节点共用的响应式标签，正则值引用固定定义；`#`、`-` 等纯符号原样展示，提交时使用正则 `value`。

`file-type.ts` 维护图片、文档、视频和音频的文件扩展名常量，扩展名统一使用大写。
使用方判断文件类型时先将后缀转换为大写，再与对应常量匹配。

`application.ts` 的 `APPLICATION_DISPLAY_SETTING_DEFAULT` 维护智能体显示设置默认值，专业版显示设置弹窗的
初始与恢复默认、调试面板（社区版或接口未返回的字段）共用；常量只读，使用方修改前先深拷贝。
