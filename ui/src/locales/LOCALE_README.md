# 国际化规则

本文维护 `src/locales` 的目录、命名空间、文案归属和使用规则。当前支持 `zh-CN`、`zh-Hant`、`en-US`，默认语言及缺失文案回退为简体中文。
文档描述当前实现，不作为翻译进度清单；页面行为、组件接口和画布协议分别见 [页面规则](../views/VIEW_README.md)、[组件规则](../components/COMPONENT_README.md)、[工作流规则](../workflow-canvas/WORKFLOW_README.md)。

## 目录与命名空间

按业务含义组织语言包，不按页面或组件位置复制文案。三种语言使用相同的文件路径、key、字段类型和排列顺序。
`common/`、`system/` 是分类目录，只整理文件，不增加调用前缀；`application/`、`knowledge/`、`workflow/` 是业务目录，目录名就是命名空间。

### 公共能力

| 文件                        | 命名空间        | 职责                                               |
| --------------------------- | --------------- | -------------------------------------------------- |
| `common/index.json`         | `common`        | 通用操作、字段、状态、校验、空状态、日期和周期     |
| `common/auth.json`          | `auth`          | 登录、退出、找回／修改密码、认证方式及认证配置     |
| `common/authorization.json` | `authorization` | 资源权限、工作空间授权、对话用户授权               |
| `common/api-key.json`       | `apiKey`        | API Key 列表、编辑、有效期、跨域及删除确认         |
| `common/resource.json`      | `resource`      | 关联资源、共享状态、数据源选择、MCP 配置和模板中心 |
| `common/upload.json`        | `upload`        | 文件选择、上传状态、格式／大小校验、头像和后缀编辑 |
| `common/dynamic-form.json`  | `dynamicForm`   | 动态表单控件、字段配置、显隐条件和比较符           |
| `common/execution.json`     | `execution`     | 跨业务执行记录、执行详情、结果和取消执行           |

`resource` 只维护跨资源共用能力；智能体、知识库、工具、模型的业务文案仍归各自业务域。
授权归 `authorization`，身份认证归 `auth`，API Key 管理归 `apiKey`，不因页面相邻或多处使用而混放。

### 系统业务

| 文件                      | 命名空间     | 职责                                                 |
| ------------------------- | ------------ | ---------------------------------------------------- |
| `system/index.json`       | `system`     | 系统管理标题、菜单分组及系统内共用的成员文案         |
| `system/user.json`        | `user`       | 用户字段、创建／编辑、密码、导入、角色与用户组分配   |
| `system/user-group.json`  | `userGroup`  | 系统／对话用户组及成员关系                           |
| `system/workspace.json`   | `workspace`  | 工作空间名称、全部／默认空间、创建、重命名及成员移除 |
| `system/role.json`        | `role`       | 角色、继承关系及权限配置                             |
| `system/chat-user.json`   | `chatUser`   | 对话用户管理、来源、导入说明与 Token 配额            |
| `system/email.json`       | `email`      | SMTP 账户、发件人和 SSL／TLS                         |
| `system/appearance.json`  | `appearance` | 平台外观、主题色、登录品牌配置与预览说明             |
| `system/operate-log.json` | `operateLog` | 操作日志、API 详情及清除策略                         |

### 其他业务

| 位置            | 命名空间      | 职责                                             |
| --------------- | ------------- | ------------------------------------------------ |
| `layout.json`   | `layout`      | 头部、头像菜单、关于弹窗、默认 slogan 和收起导航 |
| `overview.json` | `overview`    | 首页资源概况、快捷创建、监控及共用排行           |
| `application/`  | `application` | 智能体列表、创建、设置、概览、日志与发布渠道     |
| `knowledge/`    | `knowledge`   | 知识库、文档、图片、分段、标签、检索、同步和设置 |
| `model.json`    | `model`       | 模型分类、供应商、类型说明、表单及参数           |
| `tool.json`     | `tool`        | 工具、Skill、工作流、MCP、数据源表单及调试       |
| `trigger.json`  | `trigger`     | 定时／事件触发器、请求参数、执行任务及触发失败   |
| `folder.json`   | `folder`      | 文件夹创建、移动、排序和删除                     |
| `workflow/`     | `workflow`    | 画布、节点、变量、提示词、调试与执行展示         |
| `portal.json`   | `portal`      | 门户入口、名称、访问设置、智能体选择与历史清空   |
| `chat.json`     | `chat`        | 对话共用文案；按已确认的功能范围维护             |

### 加载规则

- 分类目录直属的 `index.json` 使用分类目录名，例如 `common/index.json` → `common`、`system/index.json` → `system`。
- 分类目录内的业务文件使用文件名，例如 `common/resource.json` → `resource`、`common/api-key.json` → `apiKey`、`system/user.json` → `user`。
- 普通业务目录使用目录名，例如 `knowledge/document.json` → `knowledge`；子文件名不进入 key。
- 短横线文件名转换为 camelCase 命名空间。JSON 不重复包裹命名空间，例如 `common/resource.json` 直接维护 `relations`，调用为 `resource.relations.title`。
- 同一业务只保留单文件或一套分文件目录，不同时维护同名文件与目录，也不跨分类重复定义同一命名空间。
- 同一命名空间的不同文件不得重复定义 JSON 顶层字段；加载采用浅合并，不会深层合并同名对象。拆文件应搬完整分组，保持调用 key 不变。
- Vite 自动收集语言文件，新增或移动文件不逐项维护 import，不增加加载辅助函数。

## Key 结构与排序

翻译 key 最多四层，包含命名空间。使用表达业务含义的英文 camelCase，不使用中文、数字序号或 `misc` 等模糊分类。

- 字段的标签、占位、说明和校验提示同级维护，如 `label`、`placeholder`、`description`、`requiredMessage`、`invalidMessage`、`lengthMessage`，不加 `validation` 层。
- `placeholder` 与 `requiredMessage` 用途独立，文案相同也保留不同 key。
- 普通字段可直接归业务域，如 `user.username.label`；已有 `fields` 或场景分组时沿用清晰的业务结构，不机械套用统一层级。
- `common.name`、`common.title`、`common.description`、`common.content` 集中维护通用字段的标签、占位及已有校验；纯标签归 `common.labels`，状态归 `common.status`。
- 简单入口文案可以平级。只有完整对象或场景才增加分组，不为组件名、文件名或单条文案额外包一层。
- 三语键按含义分组，顺序一致。字段内按 `label` → `placeholder` → `description` → 校验提示排列；状态组先放标签，再放各状态。
- `common/index.json` 顶层顺序为 `labels` → `name` → `title` → `description` → `content` → `status` → `options` → `dateRange` → `relativeTime` → `schedule` → `parameters` → `configuration` → `actions` → `dialogs` → `messages` → `error` → `placeholders` → `validation` → `empty`。其他业务沿用现有业务分组顺序。

## 文案与复用边界

只翻译已有文案，不为复用 key 改写中文或扩大含义。多处使用不等于通用，相同中文也可能属于不同业务。
用户输入、接口返回的实体名称、代码、协议值、已保存提示词和节点数据保留原文。

| 文案                                                                              | 归属或使用规则                                                                                           |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 添加、编辑、删除、保存、取消、导出、调试等通用操作                                | `common.actions`                                                                                         |
| 创建者、操作、创建／更新时间、问题、语言、备注、来源、数据类型、IP 地址、API 文档 | `common.labels`                                                                                          |
| 名称、标题、描述、内容                                                            | `common.name`、`common.title`、`common.description`、`common.content`                                    |
| 带对象的配置标题、未配置                                                          | `common.configuration`，标题通过 `{name}` 传参                                                           |
| 通用成功／失败、排队、执行、启停状态                                              | `common.status`；启用状态标签使用 `activeLabel`                                                          |
| 通用操作成功、完成等结果                                                          | `common.messages`，保留编辑／设置／保存／发送等不同含义                                                  |
| 通用操作失败、请求、网络、权限、服务及音视频播放错误                              | `common.error`，复用原文案，不改写接口返回或具体错误信息                                                 |
| 引用／引用参数／引用变量／自定义、是／否                                          | `common.options`；带具体业务对象的完整名称按实际展示含义维护                                             |
| 日期范围、星期、周期、间隔单位和 Cron                                             | `common.dateRange`、`common.schedule`                                                                    |
| 输入／输出、输入参数／输出参数、错误信息／错误日志                                | 分别使用 `execution.details` 中对应 key，不互相替换                                                      |
| 用户问题／问题／检索问题                                                          | 分别维护，执行详情原来是“问题”时不能改成“用户问题”                                                       |
| 回答内容／AI 回答内容                                                             | `workflow.answer.label`／`workflow.answer.aiLabel`，英文分别为 `Response content`／`AI response content` |
| 默认值和用户内容                                                                  | 默认值在初始化或恢复默认时按当前语言读取；已有值和编辑草稿不随语言重写                                   |

独立选项“自定义”统一使用 `common.options.custom`，“其他”统一使用 `common.labels.other`；完整名称、说明及不同含义的业务文案仍归对应业务，不为统一翻译修改选项值。
“引用”“引用参数”“引用变量”分别使用 `common.options.reference`、`referenceParameter`、`referenceVariable`，同级维护；引用变量的占位、校验及错误说明仍归 `workflow.referenceVariable`。
MCP 设置的来源选项在已有上下文中直接显示“引用”，复用 `common.options.reference`，来源配置值保持原样。
通用“结果”标签使用 `common.labels.result`；执行结果、条件结果、问题优化结果等完整名称保留业务文案。
输入、输出、输入参数和输出参数的通用标签，包括工具表单与调试标题，复用 `execution.details`；角色表头的“权限”复用 `authorization.permission.label`，知识库设置的“对话用户授权”复用 `authorization.chatUserTitle`。

复制到剪贴板和复制资源生成副本统一使用 `copy` 命名及 `Copy` 词族：通用按钮使用 `common.actions.copy`，复制成功使用 `common.messages.copySuccess`，已复制使用 `common.messages.copied`；业务标题使用 `application.copy.title`、`tool.copyTitle` 等对应业务 key。英文分别为 `Copy`、`Copied successfully`、`Copied`、`Copy agent`、`Copy tool`。表示重复名称、字段或文件的校验仍使用 `duplicate`，不属于复制操作。

### 语言与术语

#### 繁体中文

`zh-Hant` 以 `zh-CN` 的当前中文原文为唯一文案依据，只做繁简转换，不从英文反译，也不替换为地区用词或改写原意。例如“智能体／用户／访问／共享／配置／文件”对应“智能體／用戶／訪問／共享／配置／文件”，不改成“智慧體／使用者／存取／共用／設定／檔案”。
三语 key 和排列保持一致；繁体保留简体原文的英文、技术缩写、占位变量、标点、空格及换行结构。修改简体文案时同步更新对应繁体；业务协议值、代码片段与用户输入仍保持原样，不通过新增翻译函数或运行时转换处理。

#### 英文

英文界面采用简洁的 Sentence case：页面、弹窗、菜单、按钮、表头及字段通常只将第一个单词首字母大写；品牌、专名和技术缩写保留规定写法。
新增或调整拼接时检查完整英文的大小写、词形和语序；需要完整译文时直接建立 key，不用 `.toLowerCase()` 等运行时转换处理翻译文案。用户明确保留的既有 `Logo`、`TOP5` 等写法不批量调整。

- 通用输入／选择占位使用 `Please enter`、`Please select`，不加省略号；有具体对象时使用 `Enter a model name`、`Select a model` 等完整短语，不统一加 Please。
- 通用必填提示使用 `This field is required`；具体字段优先写明对象，placeholder 与校验仍保留独立 key。
- “知识库”使用 `knowledge`，不加 base／bases；“分段”使用 `segment`／`segments`，代码 key 和文件名仍可沿用 `paragraph`；“子块”使用 `sub-chunk`。
- 自定义分词使用 `term`，标题为 `Custom term`，创建入口为 `Create term`。
- “关联”使用 `relate` 词族：`Relate`、`Unrelate`、`Related`、`Unrelated`；结果为 `Related successfully`／`Unrelated successfully`。网页链接仍使用 `link`。
- 创建时间／更新时间使用 `Create time`／`Update time`。概览中的“对话次数”使用 `Chats`。
- `LLM`、`AI`、`API Key`、`URL`、`MCP`、`MaxKB` 等固定缩写或名称按原样展示；带普通中文词的完整名称仍需翻译其文字部分。

### 数字、标点和插值

- 数字、固定比例、编号、倒计时和纯格式不单独翻译，例如“已选 3/10”只翻译“已选”。不为单独冒号、问号、括号或分隔符建立 key，也不按语言增加标点判断。
- 完整确认句、校验说明及数量限制整体翻译，名称、数量和原因通过 `{name}`、`{count}`、`{reason}` 等命名参数传入。
- 英文数量按实际值处理单复数，格式化后的显示数字与单复数判断数量分别传入。繁体保留简体原文的标点及格式。
- 固定 JSON、正则、文件后缀、URL、变量路径和代码示例保留原样；只有其中的界面说明进入语言包。
- 不能只按中文相同就拼接英文；“AI 回答内容”直接调用完整 key，不再拼接 `AI`。

## 文案硬性规范

以下规则适用于所有业务页面、共享组件和工作流界面，新增及整理现有翻译时必须遵守。
本节列明的操作确认句和通用确认按钮按以下规范统一；其他文案仍须保留原有名称和含义，不得借统一规范擅自改写。

### 删除确认

| 场景     | 简体中文固定格式                                      | 示例                       |
| -------- | ----------------------------------------------------- | -------------------------- |
| 单个删除 | `是否删除XXX：XXX？`，依次填写对象类型、对象名称      | `是否删除文档：使用指南？` |
| 批量删除 | `是否删除选中的X个XXXX？`，依次填写所选数量、对象类型 | `是否删除选中的3个文档？`  |

- 中文使用全角冒号 `：` 和问号 `？`，对象名称、数量与固定文字之间不额外加空格；批量格式统一保留“选中的”和量词“个”。
- 对象类型使用对应业务的准确名称，单个删除展示实际对象名称，批量数量使用本次选中的删除对象数。
- 删除确认句保留在所属业务域的 `delete` 分组，完整翻译并直接调用 `t()`；名称和数量分别使用 `{name}`、`{count}` 插值，不新增翻译辅助函数，也不将不同业务拼成通用删除句。
- 三种语言保持相同含义及插值参数；繁体遵循对应中文格式，英文使用英文语序和标点。标点随完整句子维护，不在使用处按语言判断或拼接不同标点。
- 删除风险、关联影响等必要说明保留在正文，不替代上述确认句。此规则约束已有删除确认文案，不新增确认流程，也不将“移除”“解除关联”等其他操作改成删除。

### 工具更新确认

工具更新确认采用同样的单个对象格式：`是否更新工具：{name}？`，英文为 `Update tool: {name}?`，繁体为 `是否更新工具：{name}？`。
完整句子使用 `tool.updateVersion.title`，直接调用 `t('tool.updateVersion.title', { name: tool.name })`；名称保持原值，不在调用处追加冒号或问号。更新影响说明仍使用 `tool.updateVersion.description`。

### 文档同步确认

单个文档同步使用 `knowledge.document.sync.title`：`是否同步文档：{name}？`；批量同步使用同组 `batchTitle`：`是否同步选中的{count}个文档？`。
完整句子直接调用 `t()`，分别传入原文档名称与本次选中的文档数量；英文批量文案按数量区分 `document` / `documents`。标点随三语句子维护，不在调用处追加。同步说明及工作流文档的专属说明仍归同组，保留原同步流程。

### 成员移除确认

单个成员移除使用 `system.member.removeTitle`：`是否移除成员：{name}？`；按成员数量批量移除使用 `system.member.batchRemoveTitle`：`是否移除选中的{count}个成员？`。
用户组、对话用户组、角色和工作空间复用单个标题；按人数批量移除时传入实际人数，英文区分 `member` / `members`。完整句子直接调用 `t()`，名称和数量保持原有来源，调用处不再追加标点。
工作空间按记录批量移除使用 `workspace.delete.batchRemoveTitle` 的完整问句“是否移除选中记录对应的成员？”，保留记录与成员的区别；人数和记录数继续由 `batchRemoveDescription` 分别说明，计数及移除逻辑保持原样。

### 确认按钮

通用确认按钮统一使用 `common.actions.comfirm`，不再区分“确认”和“确定”，不另建同义 key。

| 语言      | 固定文案 |
| --------- | -------- |
| `zh-CN`   | `确定`   |
| `zh-Hant` | `確定`   |
| `en-US`   | `Ok`     |

英文必须为首字母大写的 `Ok`，不使用 `OK`、`ok` 或 `Confirm`。此规则限定独立的通用确认按钮，不改写“确认密码”等业务字段，也不将“删除”“保存”等明确动作按钮改成通用确认按钮。

## 使用约定

### 直接使用 t

Vue 组件显式导入 `useI18n`，使用 `useI18n({ useScope: 'global' })`；不使用自动注入的 `$t`。
普通 TS 在入口完成初始化后从 `@/locales` 导入 `t`，在函数执行或响应式展示配置中读取译文。

- 界面、已有函数中的校验、确认和结果提示均直接调用 `t()`。直接替换文案无需另行确认。
- 不新增翻译辅助函数、手写 getter、`labelKey`／`descriptionKey` 属性或平行 key 映射；无法直接使用 `t()` 时先说明原因和方案，得到用户确认后处理。
- 共享展示配置使用 `reactive` 自动解包属性上的 `computed(() => t(...))`，调用方直接读 `label`、`description`，不增加 `.value` 或再次翻译。
- 文案首次读取须在 `createAppI18n` 完成之后，不在模块初始化时固化翻译结果。派生展示数据要保留响应式计算。
- 校验规则使用 computed 或在校验执行时翻译；表单使用 `:validate-on-rule-change="false"`。不添加语言切换后重新校验表单的 watch，已有错误在下次正常校验时更新。
- 切换语言只更新展示，保留选择、分页、编辑草稿和已初始化默认内容；只有服务端提供翻译数据的明确场景重新查询。

### 服务端翻译与重新查询

角色权限配置在切换语言时重新查询权限名称，按权限 ID 保留当前角色未保存的勾选；切换角色时重新读取该角色的勾选状态。
操作日志在切换语言时重新加载列表和菜单选项，保留筛选、排序和页码，不重复加载工作空间选项。
其他页面不因翻译而新增请求、计时器或语言监听。

## 语言状态

Admin 和 Chat 各自在独立页面调用 `createAppI18n` 创建实例并连接自己的 User Store。模块导出的 `t` 来自当前页面创建的实例。
Store 是语言状态来源，通过 setLanguage 更新，不能直接修改 Vue I18n 的 locale。
App.vue 通过当前 locale 配置 Element Plus，并注册 Day.js 的 zh-cn、zh-tw 日期语言包；
英文使用内置 en。日期组件按当前 Element Plus 语言读取日期文案，不修改时区及原始值。
初始化同时维护 html.lang。Markdown 编辑器与预览读取当前应用的 locale，繁体映射为 zh-TW，
语言包在入口通过 configureMarkdownEditor 注册，不跟随语言切换重复初始化或重建编辑器。

两个入口继续共用 MaxKB-locale。初始化按本地缓存、浏览器语言、默认中文选择；
英语变体归一为 en-US；zh-Hant、zh-TW、zh-HK、zh-MO 归一为 zh-Hant，
显式 zh-Hans 优先使用简体，其余语言回退 zh-CN。Element Plus 的繁体映射为 zh-tw。Admin 加载账号后继续采用账号语言。
跨标签页缓存变化同步到当前 Store。请求头复用原请求层的 user.language。
登录前的语言选择只保存本地；头部菜单调用当前账号语言接口，成功后同步 Store、
用户档案和本地偏好，不刷新页面。Admin 后续加载账号时继续采用已保存的账号语言。

`src/main.ts`、`src/chat.ts` 的 import、样式、初始化和插件注册顺序始终保持，新增国际化内容也不得重排。
错误页文案使用 `common.error.noPermission`／`noService`，404 数字保持原样。共享组件的修改授权遵循 [组件规则](../components/COMPONENT_README.md#公共组件修改边界)，每批只处理用户指定范围，完成后说明检查结果和下一步，等待用户检查。

## 公共能力与资源组件

### 资源选择弹窗

智能体、工具、知识库选择弹窗的标题分别复用 `application.title`、`tool.title`、`knowledge.title`；清空、取消和确定复用 `common.actions`，已选数量只翻译 `common.labels.selected`。
工具弹窗由调用方传入自定义标题时直接显示最终文案；知识库 Embedding 模型一致性说明归 `knowledge.help.embeddingModelHint`。资源和文件夹名称保留接口原值。

### 资源与授权

- `resource.relations` 维护查看关联资源、关联资源、依赖和被依赖；资源名称映射复用四类业务的 `title`，通用字段复用 `common`、`workspace`。方向协议、筛选与接口返回内容保持原样。
- `resource.dataSource` 维护数据源名称、选择标题、类型标签和文件查询不支持提示；`mcpConfig`、`templateStore` 分别维护 MCP 配置与模板中心。模板名称、描述、README 和配置 JSON 保留原文。
- `authorization.resource`、`permission`、`workspace` 分别维护资源授权、权限选项和工作空间授权；系统与资源授权抽屉复用同一套权限选项。
- 智能体两种范围和知识库四种范围的“对话用户授权”目录使用 `authorization.chatUserTitle`；系统对话用户管理仍使用 `chatUser.title`。
- 自动授权、已授权、授权及按用户／用户组复用 `authorization` 顶层对应 key；已授权人数只翻译标签，数量与固定分隔符在模板组合。

### API Key 与执行展示

`apiKey` 维护编辑标题、安全提示、知道了、删除确认、`expiration` 和 `cors`；备注、启用状态、日期、操作及结果复用 `common`。`API Key`、`Base URL` 固定显示，API 文档标签使用 `common.labels.apiDoc`，复制提示使用 `common.messages.copied`。
翻译不改变密钥遮罩、复制内容、跨域按行解析、有效期计算和删除后的分页回退；保留向上取整及七天到期提示边界，不添加计时器或重置草稿。

对话用户的唯一密钥说明、“我的 API Key”及 MCP 服务类型名称归 `apiKey.chatUser`；MCP 配置标题复用 `resource.mcpConfig.title`，重新生成和复制结果复用 `common`。密钥、服务地址、配置 JSON、协议值及 `<CHAT_USER_API_KEY>` 占位保持原样。

`execution.records`、`details`、`result`、`cancel` 供工作流、知识库、工具和触发器共用。触发失败属于 `trigger.taskExecution.triggerFailed`，不放到通用执行状态；未知状态、接口错误和执行内容保留原文。

### 文件夹

`folder.json` 维护 `actions`、`sort`、`delete`；移动入口、批量操作和弹窗标题统一使用 `folder.actions.moveTo`。
名称、描述、搜索占位和结果提示复用 `common`；授权入口复用 `authorization.resource.title`，资源分类复用对应业务的 `categories.all`／`shared`。用户创建的文件夹名称保留原文。

### 上传与动态表单

上传文案归 `upload`：文件类型使用 `types`，头像设置与图片说明使用 `avatar`，状态使用 `status`，后缀编辑使用 `extension`。
智能体显示设置与外观设置的通用图片大小限制复用 `upload.imageSizeMessage`，大小上限由调用方传入。
动态表单上传数量说明复用 `upload.limits`，按实际数量选择英文单复数。
“文件不能为空”与“不能上传空文件”、“上传失败”与“失败”保留各自完整含义；业务模板和文件内容要求留在业务域。

`dynamicForm` 维护控件类型、字段配置、选项、显隐条件、帮助、比较符、上传及树形配置。字段与模型参数表头共用 `fields`，比较值按输入／选择控件使用对应占位和校验。
参数标识与显示名称使用 `fields.parameter`／`fields.displayName`，数据中的 `field`、`label` 属性保持原样；显示名称统一使用“显示名称”，不缩成“显示名”。
默认值及生成规则中的通用长度范围校验复用 `common.validation.lengthRange`，不在动态表单中重复定义长度提示。
动态表单的“基本信息”复用 `common.labels.basicInfo`；智能体显示设置与外观设置的“恢复默认”复用 `common.actions.restoreDefault`。
控件名称统一读取 `DYNAMIC_FORM_TYPES`，比较符统一读取 `dynamicForm.operators` 的响应式名称；协议值、顺序、用户选项标签、字段说明与序列化结果不翻译。
通用操作、结果及参数添加／编辑标题复用 `common`；树形选项删除确认使用 `dynamicForm.tree.delete.title`。

## 应用布局与概览

### 应用布局

`layout.json` 的升级、返回工作空间、项目地址、用户手册、论坛求助和收起导航使用平级 key。门户入口复用 `portal.label`。关于弹窗归 `layout.about`，不按头部／头像组件另包一层。
系统管理标题复用 `system.title`，默认工作空间复用 `workspace.default`；修改密码、退出登录使用 `auth.changePassword.title`／`auth.logout.label`，语言标签使用 `common.labels.language`，语言选项统一读取 `LOCALE_OPTIONS`。

关于弹窗的版本名称、授权字段和到期提示分别归 `layout.about.editions`、`fields`、`expiration`。授权主体、日期、版本号、序列号和备注保留接口原文；版权公司名称使用 `layout.about.company`，简体为“杭州飞致云信息科技有限公司”，繁体按简体转换，英文为 `FIT2CLOUD`。年份、版权符号、括号及既有到期计算保持原样。
默认品牌欢迎语归 `layout.slogan`；接口返回和用户编辑的品牌内容不翻译。

### 首页与智能体概览

`overview.json` 维护 `title`、`resources`、`quickCreate`、`monitoring`、`ranking`。工作空间首页、系统首页与智能体概览共用概览标题，监控及排行文案也共用；数据口径和查询流程保持原样。
首页资源卡片保留“大语言／向量”简称，英文为 `LLM`／`Embedding`。全部工作空间复用 `workspace.all`，全部智能体复用 `application.categories.all`。
排行中的“均 Tokens/轮”“均 Tokens/次”“人均对话轮次”分别使用对应文案，保留既有 `TOP5` 和统计口径。

`application/overview.json` 维护 `application.overview`：Web／后端 API 访问、链接重置确认及 `embed`、`accessRestriction`、`display`。基本信息、复制、启停和重新生成复用 `common`，去对话复用 `application.actions.chat`。
嵌入模式只翻译名称和说明，iframe／script、URL 参数与 HTML 转义保持原样；访问限制复用 `auth.loginSettings`，保留自己的数值范围和白名单解析。
显示设置的社区版、商业版与预览共用文案，语言选项使用 `LOCALE_OPTIONS`。默认免责声明按初始化或恢复默认时的语言读取；已保存内容和编辑草稿不重写。

### 门户

门户专属文案集中在根目录 `portal.json`，统一使用 `portal` 命名空间，包含入口名称、名称与访问配置、智能体选择及门户清空说明。智能体管理中的上下架操作和结果提示归 `application.portal`，“已上架”状态归 `application.status.onPortal`。普通对话与门户共用的新建对话、历史记录、分享、删除及清空基础提示继续复用 `chat`；智能体名称、通用操作及搜索占位分别复用 `application`、`common`，不复制到门户语言包。

### 对话

`chat.json` 保持单文件。顶层按基础名称与角色 → `actions` → `history`／`delete` → `message` → `upload`／`urlUpload` → `voice` → `feedback`／`knowledgeSource` → `share`／`export` → `improve` 排列；组内按字段、操作、状态及提示的使用关系排列，三语顺序一致。`share` 集中维护分享入口、标题、复制链接和分享页提示；`knowledgeSource` 集中维护知识来源及其 PDF 文档预览文案，不另设 `documentPreview` 分组。
`message` 平铺维护输入提示、回复及思考状态、工具调用数量、文件差异提示、消息异常、消息表单状态、对话记录空状态和 URL 缺少参数提示，不额外嵌套 `toolCall`、`form` 或 `userForm`。
`actions` 平铺维护“更多设置”、放大／还原、关闭调试、设置及侧栏展开／收起等界面操作，使用 `chat.actions`，关闭调试使用 `closeDebug`；通用操作仍复用 `common.actions`，清空成功复用 `common.messages.clearSuccess`。
`voice` 平铺维护录音、转文字及朗读的状态、操作和异常提示，不另设 `reading` 分组。
查看标注与修正内容统一归 `chat.improve`；查看标注标题使用 `markTitle`，内容字段与分段表单共用 `common.content`，不在业务中重复定义。

## 模型与工具

### 模型

`model.json` 的分类使用 `categories`，供应商使用 `provider`，类型名称和说明使用 `types.<类型>.label`／`description`。`MODEL_TYPE_LABELS` 提供共用响应式名称，类型协议值不变。
“AI 模型”的标签、占位及必填提示统一使用 `model.ai`，模型、长期记忆和语音等不同场景的完整名称分别保留。普通“模型”与选择模型占位继续使用 `model.title`、`model.select.placeholder`。
模型参数字段与控件类型复用 `dynamicForm`；名称及代码等专属提示、创建与删除确认归 `model`，通用操作复用 `common`。
动态表单内置供应商的中文名称归 `model.provider`，在现有选项生成函数中直接读取当前语言；纯英文品牌、供应商标识、图标和顺序保留原样，接口返回的名称不在前端改写。

### 工具

`tool.json` 维护列表、分类、创建／编辑／复制、参数、调试和删除等业务；普通工具名称直接用 `tool.title`，不另设 `custom` 类型分组。
Skill、工作流、MCP、数据源分别归 `skill`、`workflow`、`mcp`、`dataSource`，名称和表单文案集中在同组，不单独拆目录。

| 内容                         | 归属                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| 名称、代码等字段提示         | `tool.fields`                                                                              |
| 来源标签、自定义、引用参数   | `tool.source`，保留引用与引用参数的区别                                                    |
| 商店分类、搜索计数和应用入口 | `tool.store`；接口分类、README 和资源内容保留原文                                          |
| 参数配置与 Python 代码       | `tool.initParams`、`inputParams`、`pythonCode`；输入／输出参数标题复用 `execution.details` |
| 使用时显示／代码区隐藏说明   | `tool.help`                                                                                |
| 调试运行、状态和错误提示     | `tool.debug`；调试操作复用 `common.actions.debug`                                          |
| 版本更新与删除／禁用影响     | `tool.updateVersion`、`delete`、`disable`                                                  |

MCP 的 JSON 配置校验区分“语法有效”与“必须为对象”，不为复用文案改变原校验条件。Python 模板、用户代码和参数说明保持原文。
工作流工具节点可复用工具参数文案；输入／输出、输入参数／输出参数按原名称选择 `execution.details` 对应 key。复制名称按“原名称 + 空格 + `common.name.copySuffix`”组合，并保留原长度限制。

## 智能体

`application/` 内文件合并为 `application` 命名空间；各文件顶层分组互不重复。

| 文件            | 主要分组与职责                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `index.json`    | 列表、分类、简易／高级类型、创建、模板、复制、状态、门户上下架、导出和删除                                                      |
| `settings.json` | `settings`、`prompt`、`knowledgeSetting`、`skills`、`prologue`、`longTermMemory`、`fileUpload`、`speechInput`、`speechPlayback` |
| `overview.json` | `overview`：访问、链接、嵌入、访问限制和显示设置                                                                                |
| `chat-log.json` | `chatLog`：表头、反馈、来源、清除策略与添加知识库                                                                               |
| `access.json`   | `access`：发布渠道、连接方式、回调及渠道配置                                                                                    |

- 菜单与资源名称复用 `application.title`。完整类型名称、简称、创建标题及说明分别使用 `simple`／`advanced` 中的对应字段。
- 名称和描述提示归 `application.fields`，描述使用应用场景、用途和示例的完整占位；模板归 `application.template`，不再包 `create`。
- 设置中的模型选择复用 `model.ai`，系统／用户提示词、历史与思考复用 `workflow`；知识库参数复用 `knowledge.retrieval`，周期与 Cron 复用 `common.schedule`。
- 默认开场白、用户提示词、问题优化和无引用分段回答分别归 `application.prologue.defaultValue`、`application.prompt.userDefaultValue`、`application.knowledgeSetting.problemOptimization.defaultValue`、`application.knowledgeSetting.noReferences.defaultValue`。用户提示词保留“使用中文回答”的语义；`{data}`、`{question}`、`{memory}` 和 `<data></data>` 通过命名参数原样传入。
- 技能名称与输出执行过程归 `application.skills`；MCP 服务配置复用 `tool.mcp`。对话文件上传使用 `application.fileUpload` 与 `upload.types`。
- 对话日志的来源复用 `auth.methods` 及完整业务来源名称；清除策略保留输入框顺序和英文单复数，目标知识库／文档复用对应业务字段。
- 发布渠道各平台使用统一标签，Slack 也保留语言包 key；协议值、后台地址、配置字段和用户内容不翻译。固定英文字段名保持原样，通用占位与校验仍分别维护。

## 知识库

`knowledge/` 合并为 `knowledge` 命名空间。文案按业务含义归属，页面可交叉引用：文档字段归 `document`，分段字段归 `paragraph`，不以页面目录名机械划分。

| 文件             | 主要分组与职责                                                      |
| ---------------- | ------------------------------------------------------------------- |
| `index.json`     | 列表、类型、创建、菜单、共用字段、统计、操作、生成问题和分段范围    |
| `document.json`  | `document`、`image`：列表、上传、预览、迁移、处理状态及图片相关文案 |
| `paragraph.json` | `paragraph`：分段字段、关联问题、位置、操作与删除                   |
| `tag.json`       | `tags`：标签管理、导入及关联文档                                    |
| `question.json`  | `question`：问题管理、关联分段与详情                                |
| `retrieval.json` | `retrieval`、`hitTest`、`externalRetrieval`                         |
| `settings.json`  | `baseSettings`、`documentStrategy`                                  |
| `sync.json`      | 按 `sync`、`scheduledSync`、`syncLog` 排列                          |
| `termbase.json`  | `termbase`：自定义分词                                              |

- 类型归 `base`、`web`、`lark`、`workflow`，名称、说明、创建标题共用同组；仅有菜单名称的功能集中在 `knowledge.menu`，按显示顺序排列。
- 统计与单位复用 `knowledge.stats`；“最近一次召回时间”与“最后一次召回时间”保留各自文案。生成问题与向量化共用 `knowledge.paragraphScope`。
- 生成问题字段、校验和内置默认提示词归 `knowledge.generateQuestions`，模型复用 `model.ai`；默认提示词只在无已保存配置时按当前语言初始化，变量和标签原样传入。
- 分段标识使用 `knowledge.documentStrategy.splitPatterns`，由 `DOCUMENT_SPLIT_PATTERN_OPTIONS` 提供响应式文字；正则与纯符号保留原值，agent 参数标识不翻译。
- 同步方式、定时计划和日志分别归 `sync`、`scheduledSync`、`syncLog`；同步专属状态与计数共用 `syncLog.status`，通用成功／失败复用 `common.status`。
- 召回测试、智能体设置和工作流检索共用 `KNOWLEDGE_SEARCH_MODE_OPTIONS`；检索参数归 `knowledge.retrieval`，测试文案归 `knowledge.hitTest`，接口结果保留原文。
- 文档、图片、分段迁移入口共用 `knowledge.actions.migrate`／`migrateTo`；目标知识库使用 `knowledge.fields.targetKnowledge`，目标文档使用 `knowledge.document.targetDocument`，标签、占位、必填提示分别维护。
- 文件状态和召回处理归 `knowledge.document.status`／`hitHandling`；统计、资源名称、上传校验分别复用 `knowledge.stats`、对应业务域、`upload`。
- 基础设置归 `knowledge.baseSettings`；图片处理和索引增强复用 `knowledge.documentStrategy`。外部检索归 `knowledge.externalRetrieval`，其 API 示例与 MCP 配置内容保持接口原文。

## 工作流

`workflow/` 使用 `workflow` 命名空间；每个顶层分组由一个文件维护，调用 key 不含文件名。

| 文件                        | 主要分组与职责                                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `index.json`                | 工作流标题及跨节点共用的参数、变量、用户输入、文档、检索、历史、思考、回答与返回内容                                            |
| `layout.json`               | 平级的 `layout`、`menu`、`defaultModel`、`publishHistory`                                                                       |
| `prompt.json`               | `systemPrompt`、`userPrompt`、`positivePrompt`、`negativePrompt`、`promptGeneration`                                            |
| `ai-generation.json`        | `aiGeneration`：面板、示例需求、工具活动名称和已接入的引擎错误                                                                  |
| `nodes.json`                | `node`、`start`、`aiChat` 及未单独分文件的节点                                                                                  |
| `llm-node.json`             | `llm`，含工具声明                                                                                                               |
| `loop-node.json`            | `loop`、`loopStart`、`loopBody`、`loopContinue`、`loopBreak`                                                                    |
| `tool-node.json`            | `toolStart`、`mcp`、`customTool`、`tool`、`toolWorkflow`                                                                        |
| `knowledge-node.json`       | `searchKnowledge`、`searchDocument`、`documentExtract`、`reranker`、`documentSplit`、`localFile`、`webSource`、`knowledgeWrite` |
| `data-processing-node.json` | `variableAssign`、`variableAggregation`、`variableSplitting`、`parameterExtraction`                                             |

### 配置与展示边界

- 不修改 `node-data.ts` 的数据属性名或结构，不增加翻译 key 属性，也不创建独立展示映射。菜单、搜索和 AI 节点目录直接读取定义中的 `label`／`text`。
- 节点默认名称、字段及缺省内容通过响应式配置读取当前语言；创建／复制节点时转为普通数据。已创建节点名称、保存的配置、模板内容、用户变量和提示词不随界面语言重写。
- 开始节点名称及内置字段归 `workflow.start`，历史复用 `workflow.history`。默认引用由既有 `START_NODE_REFERENCES` 提供，保留双层花括号及字段名；用户已保存的引用不重建。
- `workflow.userInput` 维护用户输入配置；节点设置标题使用 `workflow.node.setting`，接口传参及基本信息必填／唯一性提示归 `workflow.node`。工具基本信息参数复用 `dynamicForm`、`common.title`、`tool.inputParams` 和 `execution.details`。
- `LLM` 节点名称固定显示，不建立名称翻译 key。上下文和工具声明归 `workflow.llm`；通用模型标签复用 `model.ai`，提示词复用 `workflow` 对应共用分组。
- 历史 `history`、思考 `thinking` 和技能 `application.skills` 不放进提示词分组；“回答内容”与“AI 回答内容”直接使用各自完整 key。
- 检索问题、范围和文档共用字段归 `workflow.searchQuestion`、`searchScope`、`document`；检索参数及策略复用 `knowledge.retrieval`、`knowledge.documentStrategy`。
- “最大引用字符数”与“最多引用字符数”、“参数输出”与“输出参数”、“回复内容”与“回答内容”、“负向提示词”与“提示词(负向)”保留各自原名称，不为复用 key 统一改写。
- 节点条件比较符复用 `dynamicForm.operators`；参数格式、有效引用及比较值按原含义校验，输入与选择提示分别维护。示例 JSON、媒体地址、文件名、后缀和变量路径保留原样。
- 执行详情共用 `execution.details`，节点专属字段归对应节点；字段协议值、模型输出、实际名称、错误内容及消息角色不翻译。
- 工作流的“文档列表”标签共用 `workflow.document.list`，用于检索范围及节点输出字段；数据中的 `document_list` 标识保持原样。
- “知识库列表”标签归 `knowledge.list`，工作流检索范围及节点输出字段直接复用；数据中的 `knowledge_list` 标识保持原样。
- 调试操作使用 `common.actions.debug`，工具调试文案归 `tool.debug`；生成、发布、版本历史和默认模型各自归对应分组，不随语言切换运行、保存、重置或请求历史。

### Agent 长期排除范围

`src/workflow-canvas/nodes/**/agent.ts` 和 `src/workflow-canvas/ai-generate/impl/**` 中的 agent 内容不做国际化，今后也不作为遗漏补翻译。
内部提示词、规划指令、工具／参数 schema 说明、模型纠错信息和回传模型的结果保留原文，不新增 `t()`、国际化导入、key 属性或绑定辅助函数。
生成面板、示例需求、工具活动标签及 `workflow.aiGeneration.errors` 的引擎终止错误属于界面展示，保留现有翻译；不能以排除 agent 为由撤回这些界面文案。

## 触发器

`trigger.json` 维护定时／事件类型、创建编辑、请求参数与执行任务，菜单和资源触发器入口共用 `trigger.title`。
周期选项读取 `SCHEDULE_OPTION`，日期、星期及 Cron 复用 `common.schedule`；协议值、引用来源、`body` 路径和用户参数保持原样。
内置问题使用 `common.labels.question`，文件类型使用 `upload.types`，引用／自定义使用 `common.options`；无效事件引用归 `trigger.taskExecution.invalidReferenceMessage`。
执行记录复用 `execution`，触发失败、触发任务和触发器入参分别归 `trigger.taskExecution.triggerFailed`、`task`、`triggerInput`。触发器、工具和知识库记录共用 `EXECUTION_STATUS_OPTIONS` 的响应式名称。

## 系统管理

系统业务的文件与命名空间见前文。业务标题继续使用各域的 `title`，系统分组使用 `system.menu`，不为系统资源管理复制模型、知识库、工具或智能体的语言包。

| 内容                       | 归属与约束                                                                                                       |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 系统共用成员入口与移除标题 | `system.member`，保留“成员”与账号“用户”的区别                                                                    |
| 用户密码与确认密码         | `user.password`、`user.confirmPassword`；长度范围复用 `common.validation.lengthRange`                            |
| 用户／用户组分配方式       | `user.assignment`，追加／替换仍提交原布尔协议值                                                                  |
| 用户及对话用户导入         | 共用 `user.import`，对话用户专属来源说明归 `chatUser.import`；冲突名称保持原文                                   |
| 对话用户配额               | `chatUser.quota`；数值与 `/` 不翻译，周期复用 `common.schedule`，保留原换算规则                                  |
| 系统用户组与对话用户组     | 共用 `userGroup`；明确显示“对话用户组”时使用 `system.menu.chatUserGroup`                                         |
| 角色类型与继承             | `role.types`、`role.inheritedRole`，实际角色名称保留接口原值                                                     |
| 认证协议和平台名称         | `auth.methods`；本地创建来源仍使用对应用户业务的 `source.local`                                                  |
| 系统／对话用户认证页面标题 | `system.menu.userAuthentication`／`system.menu.chatUserAuthentication`                                           |
| 认证字段与配置             | `auth.fields`、`auth.loginSettings`、各协议分组；LDAP 名称统一为 `LDAP`                                          |
| 邮箱设置                   | `email`；固定 SMTP 英文字段名不翻译，密码复用 `auth.fields.password`                                             |
| 门户设置                   | `portal.json` 的 `name`、`access`、`cors`；默认名称在初始化时读取，已保存名称不翻译，新建对话复用 `chat.newChat` |
| 外观设置                   | `appearance`，预览菜单复用 `layout`、`auth`、`role`；默认 slogan 归 `layout.slogan`                              |
| 操作日志                   | `operateLog`；状态、工作空间和操作复用公共文案，接口翻译数据按语言重新加载                                       |

成员移除的影响和统计归各自业务的 `delete`，工作空间的成员人数与关系记录数分别保留；不把用户组、角色、空间关系的“移除”改成“删除”。
用户名、角色、用户组、工作空间及授权对象名称保留接口原文；未知登录来源按原值显示。语言切换不重新请求这些选项或清空未保存授权。

外观的主题名归 `appearance.colors`，颜色值及图片映射保持原样；默认 slogan 随语言提供，初始化或恢复默认后形成普通草稿，用户编辑内容不重写。已保存的登录品牌内容也用于外观预览，不能按界面语言改写。
操作日志菜单、内容及角色权限名称由服务端按当前语言提供；清除策略当前的“天之前的对话记录”措辞保持不变，不借翻译修改业务含义。
