# 国际化规则

`src/locales` 负责界面语言、语言包和入口初始化。当前支持 `zh-CN`、`en-US` 与 `zh-Hant`，
默认及缺失文案回退为简体中文。语言包暂随入口加载，新增语言时再评估按需加载。

## 繁体中文规范

`zh-Hant` 以 `zh-CN` 的当前中文原文为唯一文案依据，只做繁简转换，不从英文反译，也不替换为地区用词或改写原意。例如“智能体／用户／访问／共享／配置／文件”对应“智能體／用戶／訪問／共享／配置／文件”，不改成“智慧體／使用者／存取／共用／設定／檔案”。
三语 key 和排列保持一致；繁体保留简体原文的英文、技术缩写、占位变量、标点、空格及换行结构。修改简体文案时同步更新对应繁体；业务协议值、代码片段与用户输入仍保持原样，不通过新增翻译函数或运行时转换处理。

## 分类

按“业务域 → 对象或场景 → 文案用途”组织；文件按业务域划分，不对应组件目录。
各语言使用相同的业务文件或目录结构。

| 业务域        | 内容                                             |
| ------------- | ------------------------------------------------ |
| common        | 无业务含义的操作、基础校验、界面偏好和通用错误页 |
| upload        | 文件选择、上传提示、校验、状态、后缀与头像上传   |
| auth          | 登录、退出、找回密码、身份认证                   |
| authorization | 资源权限、工作空间授权及对话用户授权             |
| overview      | 首页快捷创建、资源概况、监控统计及排行           |
| application   | 智能体创建、配置、发布、版本                     |
| knowledge     | 知识库、文档、分段、问题、标签、检索             |
| model         | 模型、供应商、模型参数与连接测试                 |
| dynamicForm   | 动态表单控件类型及配置器的固定界面文案           |
| resource      | 关联关系、共享状态、数据源、MCP 配置及模板中心   |
| execution     | 执行记录、执行详情及执行结果                     |
| folder        | 文件夹操作、排序、表单提示和删除确认             |
| tool          | 工具、MCP、Skill 管理                            |
| trigger       | 触发器、定时与事件配置、执行任务                 |
| workflow      | 画布、节点、变量、调试与执行展示                 |
| chat          | 对话输入、消息操作、历史会话与对话状态           |
| workspace     | 工作空间、成员、空间级设置                       |
| user          | 系统用户属性、用户管理及角色分配                 |
| userGroup     | 系统与对话用户组、组成员、分配及继承权限说明     |
| chatUser      | 对话用户管理、本地来源及 Token 配额              |
| role          | 系统角色管理、角色类型及权限配置                 |
| portal        | 门户名称、访问设置与跨域配置                     |
| email         | SMTP 邮箱配置、发件人及加密说明                  |
| system        | 系统分组菜单及系统管理内共用文案                 |

`common/` 是平台公共能力的分类目录，包含 `index.json`、`upload.json`、`dynamic-form.json`、`auth.json`、`authorization.json` 和 `execution.json`。`common/index.json` 只维护通用操作、标签、状态和提示，其他文件分别使用 `upload`、`dynamicForm`、`auth`、`authorization`、`execution` 命名空间，不增加 `common` 前缀。文件夹、资源及其他业务模块保持独立，不因多处复用就移入 `common/`。

`common/auth.json` 负责身份认证，`common/authorization.json` 负责授权。共用的“按用户组／按用户”使用 `authorization.byGroup` / `byUser`，自动授权、已授权及授权操作使用同级的 `autoAuthorization`、`authorized`、`authorize`。资源授权界面、操作权限和工作空间授权分别归 `resource`、`permission`、`workspace` 分组，引用为 `authorization.<分组>.<用途>`。用户与用户组的共用字段仍复用 `user`、`userGroup`。

`common/execution.json` 维护跨业务执行展示：`records` 包含执行记录入口、资源类型和执行时间，`details` 包含执行详情标题、输入／输出及错误等详情字段，`result` 包含执行结果标题及成功／失败提示。调用使用 `execution.<分组>.<用途>`，工具、知识库、触发器和工作流节点共用。输入与输入参数、输出与输出参数、错误信息与错误日志分别保留原文案；节点专属字段仍归对应节点分组，通用执行状态继续复用 `common.status`。

### Key 结构

翻译 key 最多四层，包含业务域命名空间。业务域内部的共用字段使用 `<业务域>.fields.<字段>.<用途>`，
场景专属字段使用 `<业务域>.<场景>.<字段>.<用途>`；不同时叠加场景、fields 和 validation。
字段文案使用 label、placeholder、description，以及同级的 requiredMessage、invalidMessage、
lengthMessage、mismatchMessage 等校验提示，不再建立字段内的 validation 层。
placeholder 与 requiredMessage 用途独立，即使当前文案相同也分别定义，不互相替代或复用。
无法归属字段的校验可以使用 `<业务域>.<场景>.validation.<规则>`。
操作、结果提示等按需使用 actions、messages、dialogs、states、options、empty，仍遵守四层上限。

### 认证文案

auth.fields 维护共用的用户名、密码、验证码、邮箱和确认密码；captcha.label 仅用于图片验证码
替代文本。找回密码专属的长度提示使用 auth.forgotPassword.password.lengthMessage，
确认密码匹配提示使用 auth.fields.confirmPassword.mismatchMessage。不改变各页面已有校验条件。
系统和智能体 API Key 的删除确认归 `auth.apiKey.delete`，名称使用列表中的掩码标识，不展示完整密钥。
登录按钮使用 `auth.login.label`；忘记密码入口归 `auth.forgotPassword.label`，找回密码页面标题及修改密码按钮共用同组的 `changePassword`。
认证方式及钉钉、飞书、企业微信名称统一归 `auth.methods`，与 `login` 同级维护；登录、用户来源、扫码配置和授权列表共用这些名称。协议值对应的响应式名称统一使用共享 `LOGIN_METHOD_LABELS`，配置中直接调用 `t`；LDAP 在登录页及配置中统一显示为 `LDAP`。各场景的完整业务名称与配置说明仍归所属业务，本地创建来源与“账号登录”保持各自含义。

### 通用与业务文案边界

归属以业务含义判断：知识库检索模式归 knowledge，知识库检索节点归 workflow。
系统资源管理复用原业务域，不复制到 system。多处使用不等于通用；相同中文但业务语义
不同可以使用不同 key。通用添加、编辑、删除、取消、保存和上传文件操作归 common.actions，
仅有展示文案的通用标签归 common.labels，例如“创建者”“操作”和“问题”。触发器任务输入及执行详情中的“问题”共用 `common.labels.question`；“用户问题”“检索问题”等完整名称保留各自文案。名称、标题与描述直接归 common.name、common.title 和 common.description，
字段的 label、placeholder 和实际使用的 requiredMessage 放在一起，表单、表头和筛选器共用 label。
通用配置文案集中在 `common.configuration`：`label` 为“配置”，`title` 为带 `{name}` 的配置标题，`unconfigured` 为“未配置”；认证配置与智能体发布渠道共用，不再分别放入 actions、dialogs 和 status。
`common.status` 维护状态标签 `label`、启用状态标签 `activeLabel`、通用启停选项 `enabled` / `disabled`，以及排队、执行、成功、失败、取消中和已取消等通用状态。
通用布尔值“是／否”使用 `common.options.yes` / `no`，不替代业务专属的启用／禁用状态。通用选项“引用／自定义”使用 `common.options.reference` / `custom`，触发器参数、文档分段节点和 LLM 工具声明共用；“引用变量”“引用参数”等完整名称仍归各自业务，不缩写或拼接。
用户、文档和图片中的“启用状态”统一使用 `common.status.activeLabel`，英文为 `Enabled status`；标签表示 `is_active` 的启用／禁用状态。
文档、同步日志和执行记录复用这些状态文案；索引中、生成中、同步中、触发失败等专属文案保留在所属业务。
“执行成功／执行失败”等完整结果提示保留业务含义，不替换为“成功／失败”。
创建时间与更新时间使用 `common.labels.createTime` / `updateTime`，英文为 `Create time` / `Update time`；卡片中“创建于”的说明使用 `common.labels.createdOn`。
流程步骤的“上一步／下一步”使用 `common.actions.previous` / `next`，记录切换的“上一个／下一个”使用 `common.actions.previousItem` / `nextItem`。
通用日期范围预设及起止日期占位归 `common.dateRange`，音视频播放失败提示归 `common.messages`。
通用周期、星期、间隔单位与 Cron 字段及校验归 `common.schedule`；日期数字、时刻及间隔数值在使用处组合。
通用文件选择、上传提示和校验归 `common/upload.json`，文件类型名称归 `upload.types`，上传进度和结果汇总归 `upload.status`。
头像设置、图片上传说明及校验归 `upload.avatar`；文件后缀编辑的操作和提示归 `upload.extension`。
“文件不能为空”使用 `upload.emptyContentMessage`，“不能上传空文件”继续使用 `emptyFileMessage`；“上传失败”使用 `upload.status.uploadFailed`，不缩成通用“失败”。
业务模板、文件内容要求和导入说明归各自业务域。
“请输入模型名称”等指明业务对象的提示，以及发布状态、任务处理阶段等业务选项归对应业务域。
“调试”作为通用操作统一使用 `common.actions.debug`，调试结果、运行状态及请求错误等提示仍归所属业务。
通用操作结果归 common.messages，通用对话框标题归 common.dialogs；业务专属确认句仍留在所属业务域。
通用确认按钮遵守下文“文案硬性规范”。“编辑成功”“设置成功”“保存成功”和“发送成功”分别使用 `editSuccess`、`settingsSuccess`、`saveSuccess`、`sendSuccess`，批量操作的完整成功提示使用对应 `batch*Success`，保留原结果提示用词。
“关联”的英文和翻译 key 统一使用 `relate` 词族：关联操作使用 `Relate` / `relate`，取消关联使用 `Unrelate` / `unrelate`，已关联／未关联标签使用 `Related` / `related`、`Unrelated` / `unrelated`；成功提示使用 `Related successfully` / `Unrelated successfully`，对应 key 为 `relateSuccess` / `unrelateSuccess`。文件名保持不变；网页链接仍使用 `link`。
用户内容、用户保存的提示词、协议枚举和已保存节点名称保留原文。

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

## 目录与命名空间

分类目录只整理文件，业务名称决定翻译命名空间。分类目录在配置中显式登记，目前为 `common/` 和 `system/`；
`knowledge/`、`application/` 等仍是业务目录，不自动忽略目录层级。

- 分类目录直属的 `index.json` 使用分类目录自身的命名空间，例如 `common/index.json` → `common`、`system/index.json` → `system`。
- 其他文件跳过分类目录后，使用第一个业务文件或业务目录名作为命名空间，例如 `common/upload.json` → `upload`，`system/user.json`、`system/user/password.json` → `user`。
- 普通单文件使用文件名，普通业务目录使用目录名，例如 `model.json` → `model`、`knowledge/document.json` → `knowledge`。
- 去掉 `.json` 后将短横线命名转换为驼峰，例如 `system/user-group.json` → `userGroup`。
- 命名空间之后的 key 由 JSON 内容决定，子文件名不自动增加层级。JSON 不重复包裹命名空间，分文件可按业务对象组织字段。

| 文件位置                    | JSON 内容示例                                   | 调用 key                       |
| --------------------------- | ----------------------------------------------- | ------------------------------ |
| `common/index.json`         | `{ "actions": { "save": "…" } }`                | `common.actions.save`          |
| `common/upload.json`        | `{ "selectFile": "…" }`                         | `upload.selectFile`            |
| `common/dynamic-form.json`  | `{ "types": { "textInput": "…" } }`             | `dynamicForm.types.textInput`  |
| `common/auth.json`          | `{ "fields": { "captcha": { "label": "…" } } }` | `auth.fields.captcha.label`    |
| `common/authorization.json` | `{ "resource": { "title": "…" } }`              | `authorization.resource.title` |
| `common/execution.json`     | `{ "records": { "title": "…" } }`               | `execution.records.title`      |
| `system/index.json`         | `{ "menu": { "identity": "…" } }`               | `system.menu.identity`         |
| `system/user.json`          | `{ "username": { "label": "…" } }`              | `user.username.label`          |
| `system/workspace.json`     | `{ "title": "…" }`                              | `workspace.title`              |
| `system/user/password.json` | `{ "password": { "label": "…" } }`              | `user.password.label`          |
| `knowledge/document.json`   | `{ "document": { "title": "…" } }`              | `knowledge.document.title`     |

同一业务只保留一个文件或一套分文件目录，不同时保留 `system/user.json` 与 `system/user/`，也不在其他分类下重复定义 `user`。
同一命名空间内各文件的 JSON 顶层字段不能重复，加载时不会深层合并同名对象。拆文件时保留业务字段结构，调用 key 不变。
三种语言使用相同的分类和业务文件结构，新增文件由 Vite 自动收集，无需逐项维护 import。

## JSON 键顺序

- 同一语言包的键按含义分组，简体、繁体和英文采用相同的排列顺序，方便逐项对照。
- `common/index.json` 的顶层顺序为 `labels` → `name` → `title` → `description` → `status` → `options` → `dateRange` → `schedule` → `parameters` → `configuration` → `actions` → `dialogs` → `messages` → `placeholders` → `validation` → `empty`。
- 字段内先放 `label`，再放 `placeholder`，最后放 `requiredMessage` 等校验提示。状态组先放 `label`、`activeLabel`，再放 `enabled`、`disabled`。其他组沿用现有顺序。

## 使用约定

- key 使用表达业务含义的英文 camelCase，不使用中文、数字序号或 misc 等模糊分类。
- 接入翻译时保留原有文案和名称，不为复用现有 key 擅自改写；“问题”与“用户问题”等不同名称分别维护。上文“文案硬性规范”列明的操作确认句和通用确认按钮必须按规范统一。
- 文件归类、命名空间与分文件合并规则见上文“目录与命名空间”。
- 纯标签、数量单位、固定比例、编号和倒计时只翻译文字，数字、名称及固定格式在使用处组合；
  作为固定格式分隔符的问号、冒号不单独建立翻译键，三种语言使用相同的显示格式。只有文件名和错误原因等数据的组合不建立翻译键。
  例如“已选 3/10”只翻译“已选”。操作确认句属于完整句子，按上文固定格式整体翻译，标点随句子维护。
- 模板和代码中的列表分隔符、括号等固定标点沿用原有写法，不按语言添加判断，也不为标点单独读取 locale；完整翻译句子中的标点随文案维护。
- 数量限制、校验说明等完整句子整体翻译，必要的动态内容保留命名参数；不机械拆散语句。
  单复数按实际数量选择，展示的数字仍可由模板直接输出。代码示例和提示词协议中的花括号保留原有语义。
- 英文界面采用简洁、明确的表达。通用输入、选择占位分别使用 Please enter、Please select，
  不使用省略号；明确对象时使用 Enter a model name、Select a model 等完整短语，不统一添加 Please。
  无具体对象的通用必填校验使用 This field is required；具体字段校验仍优先写明对象。
  按钮使用 Save 等动作词，成功提示使用 Saved successfully。短标签和占位提示使用句首大写，
  通常不加句号；通用确认按钮固定使用 `Ok`，占位与校验仍保留独立 key。
- 组件显式导入 useI18n，并使用全局作用域的 t；不使用自动注入的 $t。
- 每批范围内的界面文案都在使用处直接调用 `t`，包括已有函数中的校验、确认和结果提示。直接替换文案无需单独确认。
  不新增用于处理翻译的辅助函数。遇到无法直接使用 `t` 的场景，先向用户说明原因和方案，确认后再处理该处。
- 依赖语言的选项和校验规则在 computed 或执行时翻译，不在模块初始化时固化翻译结果。
- 共享展示配置使用 `reactive` 自动解包属性上的 `computed(() => t('...'))`，调用方直接读取 `label`、`description` 或名称映射，不需要 `.value` 或再次翻译。
  不增加 `labelKey`、`descriptionKey` 等翻译属性，也不维护平行的翻译 key 映射、手写 getter 或翻译辅助函数。
  配置只读；首次读取文案须在 `createAppI18n` 完成之后。复制或派生展示数据时保留响应式计算，避免固化当前语言。
- 不为语言切换添加重新校验表单的 watch；已有错误提示在下次正常校验时更新。
  响应式规则变化不自动触发校验，表单使用 :validate-on-rule-change="false"。
- 三种语言使用相同的文件路径、翻译键、字段类型和命名插值参数。
- 入口完成国际化初始化后，普通 TS 工具可从 `@/locales` 导入 `t`，在函数执行时翻译。

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

## 接入范围与变更边界

Admin 登录与找回密码页面支持三语切换，错误页暂不接入翻译。复用的账号与扫码组件同时影响 Chat 登录和
外观预览；平台配置的品牌文案保持原值，第三方扫码界面由 SDK 提供。Element Plus 日期组件及 Markdown 编辑器、预览已接入三语。各业务域已接入范围及分类见下文；未接入部分保留原文，不把整站三语支持视为全部完成。
新增翻译仍按用户指定范围执行，每批完成后等待用户检查，未经确认不扩展下一批。

## 资源选择弹窗

智能体、工具和知识库选择弹窗的标题分别复用 `application.title`、`tool.title` 和 `knowledge.title`。
“已选”复用 `common.labels.selected`，数量直接在模板中展示；清空、取消和确定复用 `common.actions`。
知识库选择中的 Embedding 模型一致性提示归 `knowledge.help.embeddingModelHint`，在 `knowledge/index.json` 维护。
工具弹窗的自定义 `title` 由调用方提供最终展示文字，未传入时直接使用 `t('tool.title')`；文件夹和资源名称保留原有展示规则。

## 模型列表

模型列表分类使用 model.categories，供应商字段使用 model.provider.label / placeholder；
卡片和下载／删除提示使用 model 语言包，操作按钮引用 common，
授权入口引用 authorization，关联资源入口引用 resource。模型类型协议值不变，constants/model.ts 的 MODEL_TYPE_LABELS 提供共用响应式名称，
类型名称与说明统一维护在 model.types.<类型>.label / description，保持四层结构。
系统模型页与工作流默认模型设置共用同一类型映射。
“AI 模型”的标签、占位和必填提示统一归 `model.json` 的 `ai` 分组，工作流、智能体设置、长期记忆设置和生成问题弹窗直接使用 `model.ai.label`、`placeholder`、`requiredMessage`。`model.title` 的“模型”、`model.select.placeholder` 的“请选择模型”以及各业务的长期记忆／语音模型提示保留各自文案；默认模型来源仍归 `workflow.defaultModel`。
内置分类标题按 provider 标识响应式翻译，不改写接口供应商名称。
供应商选择、模型创建与编辑抽屉、高级参数表及独立参数设置抽屉已接入三语。
高级参数表的控件类型名称读取 `common/dynamic-form.json`，加载到 dynamicForm 命名空间，
不改写接口字段描述或已保存的参数配置。切换语言不重取接口、不重新初始化表单，
也不主动校验；模型创建与编辑通过透传 validate-on-rule-change=false 禁止规则变化自动校验。
参数表中的参数、显示名称、组件类型、默认值和必填列复用 dynamicForm.fields；动态表单中的模型类型
复用 model.fields.type 及模型类型翻译映射。系统资源管理与系统共享资源的模型页固定文案同样复用
model、common、resource、authorization，工作空间名称字段标签使用 workspace.title。工作空间模型、系统资源模型、
系统共享模型和系统模型授权路由标题复用 model.title；侧栏菜单随当前语言更新，其他业务路由仍按批次处理。
MkResourceCard、MkComplexSearch、MkEmpty 的默认创建信息、占位和空状态文案使用 common；
自定义属性、插槽及接口返回内容保持原值。授权、关联资源、工作空间授权弹窗及表头筛选器的内部文案
仍按各自共享组件批次处理。

## 工具列表

工作空间、系统资源管理和系统共享资源的工具菜单，以及普通工具类型名称共用 `tool.title`。列表标题“工具”使用 `tool.title`，“全部工具”使用 `tool.categories.all`。
Skill、工作流和 MCP 的类型名称使用各自分组的 `label`，与表单文案一起维护在 `tool.json` 中。数据源的通用名称、选择标题及类型标签统一归 `resource.dataSource`，分别使用 `label`、`selectTitle`、`typeLabel`；工具类型、创建入口、工作流菜单、导入与调试共用这些文案。知识库工作流导入与调试中不支持查询数据源文件的提示使用同组的 `documentsUnavailableMessage`。
内置目录用 tool.categories，按文件夹 ID 选择译文。自建文件夹名称、工具名称和描述直接展示接口值，类型筛选和请求使用原协议值。
工具列表和输入参数共用 `tool.source.label`、`tool.source.custom`。工具列表的“工具商店”复用 `tool.store.title`，输入参数的“引用参数”使用 `tool.source.reference`。
启停、删除和版本更新的工具专属提示归 tool；通用操作、启停状态和操作结果归 common。
资源共享标签、MCP 服务配置归 `resource`，执行记录入口复用 `execution.records`，触发器入口复用 `trigger.title`。
工具商店的内置分类、搜索结果计数和应用工具文案归 `tool.store`。工具名称的专属占位和校验归 `tool.fields.name`。
商店自定义分类、工具名称、描述和 README 使用接口原文。
普通工具的创建、编辑、复制标题使用 `tool.createTitle`、`tool.editTitle`、`tool.duplicateTitle`，代码必填提示归 `tool.fields.code`。调试入口、运行状态和缺省错误提示归 `tool.debug`。
调试参数的占位与必填提示分别使用 `common.placeholders.inputField` 和 `common.validation.inputFieldRequired`，通过 `{label}` 传入参数名。执行输出和接口错误详情按原文展示。
Skill 表单的标题、名称提示和 ZIP 文件要求归 `tool.skill`。文件大小提示通过 `{size}` 读取校验上限，拖入、选择、更换文件和空文件提示复用 `upload`。
工作流工具的创建、编辑、复制标题及工作流名称提示归 `tool.workflow`。复制工具时在原名称后追加 `common.name.copySuffix`，三语均使用“名称 + 空格 + 副本后缀”。
MCP 工具表单的标题、名称提示、传输方式说明和配置校验归 `tool.mcp`。配置字段复用 `resource.mcpConfig.title`，JSON 示例与用户填写的配置保留原文。
技能区域的 MCP 设置弹窗同样使用 `tool.mcp`：标题、引用方式、自定义服务名称和工具选择字段分别归 `settingsTitle`、`reference`、`customService`、`tools`；自定义来源复用 `tool.source.custom`。配置的必填、传输说明复用 `tool.mcp.config`，仅检查 JSON 语法的提示使用 `invalidJsonMessage`，要求 JSON 对象的工具表单继续使用 `invalidMessage`，各处校验条件保持原样。
数据源工具的表单标题、名称提示和代码必填提示归 `tool.dataSource`。Python 模板和用户编辑的代码作为表单数据原样提交。
工具表单的启动参数、输入参数、输出参数和 Python 代码区分别归 `tool.initParams`、`tool.inputParams`、`tool.outputParams` 和 `tool.pythonCode`。
工具使用时的可见性说明归 `tool.help`：输入和输出参数共用 `shownWhenUsed`，Python 代码区使用 `hiddenWhenUsed`。输出结果标签使用 `tool.outputParams.result`，固定变量 `{result}` 直接在模板展示。
参数表头及提示说明复用 `dynamicForm.fields`，模型和工具共用 `common.parameters.add`、`common.parameters.edit`。自定义工具节点原有“参数说明／请输入参数说明”使用 `tool.inputParams.description`，不替换为“参数提示说明”。
自定义工具节点、工具库节点和工作流工具节点同样复用工具表单文案；参数值的输入与选择提示归 `dynamicForm.fields.parameter`，
输入使用 `placeholder` / `requiredMessage`，选择使用 `selectPlaceholder` / `selectRequiredMessage`。
执行详情中的“输入／输出”使用 `execution.details.input` / `output`，“输入参数／输出参数”使用同组的 `inputParams` / `outputParams`，按原标题选择。
工作流工具节点的自定义输入标题保留原值，缺省标题使用 `tool.inputParams.title`；来源选项使用 `tool.source`，
空状态使用 `common.empty.default`，嵌套执行详情标题使用 `execution.details.title`。来源中的“引用”使用 `tool.source.referenceShortLabel`，“引用参数”继续使用 `tool.source.reference`。
参数来源只翻译选项标签，`reference`、`custom` 和数据类型沿用协议值。

## 智能体

`application/` 按业务场景拆分语言文件，合并为同一个 `application` 命名空间。`index.json` 维护列表、卡片、类型、创建与复制表单、发布状态及基础操作。
工作空间列表、系统资源管理列表和资源授权分类共用 `application.title`，内置文件夹共用 `application.categories`；自建文件夹、智能体名称和描述展示原值。
`application.simple` / `advanced` 的 `label` 用于创建菜单中的完整类型名称，`shortLabel` 用于筛选与卡片标签，`createTitle` 用于创建弹窗，`description` 用于类型说明；提交仍使用 `APPLICATION_TYPE` 的原协议值。
创建与复制表单在 `application/index.json` 中维护：名称和描述提示归 `application.fields`，描述占位统一使用包含应用场景、用途和示例的完整说明；模板选项归 `application.template`，知识库问答助手的名称与说明归其 `assistant` 分组，复制标题归 `application.duplicate`。字段标签、通用按钮和成功提示复用 `common`；创建副本使用 `common.messages.duplicateSuccess`，复制到剪贴板使用 `common.messages.copied`。
复制名称按“原名称 + 空格 + `common.name.copySuffix`”组合，并根据当前语言后缀的长度保留 64 字符限制。表单中的用户内容、模板中心返回的名称与描述和工作流模板配置保持原值。
简易智能体创建在提交时直接通过 `t` 读取当前语言的默认内容，与设置缺省值共用 `application/settings.json` 中的开场白、用户提示词和问题优化提示词。用户提示词统一使用 `application.prompt.userDefaultValue`，保留“使用中文回答”的语义；协议变量、标签与换行结构保持原样。
智能体设置使用 `application/settings.json`：模型设置、高级设置的分区标题与未保存提示归 `application.settings`，开场白标签归 `application.prologue.label`。基本信息中的名称标签复用 `common.name.label`，占位及校验复用 `application.fields.name`；描述标签复用 `common.description.label`，占位复用 `application.fields.description.placeholder`。设置菜单与页面标题共用 `common.labels.settings`；保存、发布按钮及结果提示复用 `common.actions` / `messages`，表单校验失败提示使用 `common.validation.formInvalid`。切换语言不重置设置草稿或主动触发校验。
AI 模型的共用标签、占位及必填提示归 `model.ai`；系统／用户提示词的共用标签、说明及校验归 `workflow.systemPrompt`、`workflow.userPrompt`，历史聊天记录标签归 `workflow.history`，提示词生成界面归 `workflow.promptGeneration`，输出思考及标签设置归 `workflow.thinking`，提示词相关文案集中维护在 `workflow/prompt.json`，历史聊天记录及输出思考配置归 `workflow/index.json`。简易智能体的提示词变量说明和知识库引用选项归 `application/settings.json` 中的 `application.prompt`；变量通过 `t` 的参数原样传入 `{data}`、`{question}`、`{memory}`。用户已保存的提示词、模型返回内容及提示词生成组件的内置请求模板保持原值。`GenerateContent` 的替换、重新生成、生成中和失败提示分别复用 `common.actions`、`common.status` 与 `common.messages`，服务端错误原文透传。
智能体的知识库关联空状态、无引用分段时的回答策略和问题优化归 `application/settings.json` 中的 `application.knowledgeSetting`；通用“参数设置”弹窗标题使用 `common.parameters.settingsTitle`，智能体与工作流共用。检索模式、相似度、召回分段数和最多引用字符数共用 `knowledge.retrieval`，选项直接读取 `KNOWLEDGE_SEARCH_MODE_OPTIONS` 的响应式名称和说明。问题优化的用户提示词标签复用 `workflow.userPrompt.label`；问题优化提示词和指定回答的占位与初始内容共用对应的 `defaultValue`，必填校验独立维护。
默认开场白、用户提示词、问题优化提示词及指定回答分别归 `application.prologue.defaultValue`、`application.prompt.userDefaultValue`、`application.knowledgeSetting.problemOptimization.defaultValue` 和 `application.knowledgeSetting.noReferences.defaultValue`。通过现有初始化流程或模板直接调用 `t` 读取当前语言，不另存默认内容的翻译 key 常量，不新增翻译辅助函数；`{data}`、`{question}` 及 `<data></data>` 通过参数原样传入。详情回填沿用原有缺省条件，已有内容不重新翻译；指定回答默认值在打开参数弹窗时初始化。语言切换更新占位提示，保留已初始化内容及用户草稿，不重新校验。未保存状态使用详情回填时的配置快照比较，不随语言切换重新生成默认内容。
长期记忆的开关、说明、弹窗标题、模型提示、触发方式、轮次和周期字段归 `application/settings.json` 的 `application.longTermMemory`，说明中的记忆变量由调用处原样传入。AI 模型标签复用 `model.ai.label`，周期、星期、间隔单位与 Cron 字段及校验复用 `common.schedule`。触发卡片与周期选项在 computed 中直接调用 `t`，级联选项基于只读的 `SCHEDULE_OPTION` 生成，不改写协议值或共享常量；每月日期按数字与单位组合。保留模型补选、5–100 整数轮次、周期路径与 Cron 五字段校验，以及切换触发方式时已有的校验流程；语言切换不触发校验或重置草稿。
智能体的语音输入和播放设置归 `application/settings.json` 的 `application.speechInput`、`application.speechPlayback`：标签、自动发送／播放与播放方式在各组维护，模型占位和必填提示归各组的 `model`。这是智能体对话配置，工作流智能体的同类设置可复用；语音转文本、文本转语音节点自身的文案归 `workflow`。显示文案直接调用 `t`，播放方式协议值、模型筛选和开关清理行为保持原样。
技能区域的标题和输出执行过程文案集中在 `application.skills`，分别使用 `label`、`outputExecution`；资源分组和选择器标题复用 `tool.title`、`tool.skill.label`、`tool.mcp.label`、`application.title`。缺少名称时，在模板中显示 `resource.selected` 或“已选 MCP”并追加原 ID；这些缺省显示文案不写入资源名称或回显快照，实际资源名称保留原文。MCP 来源及 JSON 配置不随语言切换改变，弹窗不因翻译后的规则更新而重新校验。
对话文件上传的开关、上传方式、数量与大小配置归 `application/settings.json` 的 `application.fileUpload`；文件类型名称复用 `upload.types`。工作流智能体的基本信息节点同样引用这组智能体配置。
发布和门户上架状态归 `application.status`，发布时间归 `application.publishTime`，门户上下架操作及提示归 `application.portal`。名称、创建者、创建时间和通用操作复用 `common`，工作空间列复用 `workspace.title`。
智能体导出入口及 Skills 访问地址提示归 `application.export`，删除确认归 `application.delete`；错误原因、导出文件名和 MCP 配置内容保留原值。
MCP、关联资源和模板中心入口复用 `resource`，资源授权入口复用 `authorization.resource.title`，触发器入口复用 `trigger.title`，文件夹移动入口复用 `folder`；保存、导入、删除、移动、复制和导出失败提示复用 `common`。
对话日志的语言文件为 `application/chat-log.json`，使用 `application.chatLog`。工作空间和系统资源管理的日志路由与页面共用 `title`；表头归 `labels`，用户反馈筛选归 `feedback`，来源标签与业务专属选项归 `source`。来源中的企业微信、飞书、钉钉纯名称复用 `auth.methods`，Slack 复用 `application.access.slack.label`；微信公众号与企业微信机器人保留完整来源名称。来源通过 `CHAT_LOG_SOURCE_LABELS` 提供协议值到响应式名称的映射，配置中直接调用 `t`；未知来源保留接口原值。
单个和批量清除策略共用 `cleanStrategy`，标题使用 `title`，天数输入框前后的说明分别使用对应的 `Prefix` / `Suffix`，保留原交互顺序并按天数处理英文单复数。添加到知识库的按钮和弹窗共用 `addKnowledge.title`，知识库与目标文档字段复用 `knowledge.fields.targetKnowledge` / `knowledge.document.targetDocument`。通用操作、成功提示和详情翻页复用 `common`；摘要、用户名、知识库与文档名称展示原值。
发布渠道使用 `application/access.json` 中的 `access` 分组，两种资源范围的菜单共用 `application.access.title`；渠道名称与说明分别归各渠道的 `label` / `description`，配置入口、未配置状态与抽屉标题复用 `common.configuration`。卡片和抽屉通过已有渠道标识 `platform.key` 统一调用 `t`，Slack 同样使用 `label`，三语文案均为品牌名；功能本地 `platforms.ts` 维护平台标识、图标、配置字段与后台链接，不重复维护渠道名称和说明。
连接方式及共用说明归 `access.connection`，回调地址与填写引导归 `access.callback`，平台后台名称归 `access.consoles`；特定渠道的字段名、连接说明、认证状态和后台路径指引归对应渠道分组。固定英文参数名称直接使用 `label`，需要翻译的字段在响应式配置中直接调用 `t`；抽屉读取显示标签。连接选项使用响应式 `label` / `tip`，保留原有的 `ws`、`stream`、`callback` 协议值。输入占位与必填提示分别复用 `common.placeholders.inputField` / `common.validation.inputFieldRequired`，语言切换不主动触发表单校验。平台协议值、配置字段名、默认连接方式、必填条件、回调地址与外部链接保持原值；启停、保存和复制成功提示复用 `common.messages`。

## 工作流

`workflow/` 是业务目录，统一挂载为 `workflow`；文件名不进入调用 key，不与同级 `workflow.json` 并存。
`index.json` 维护工作流标题及跨节点共用的输入、变量、文档、检索、回答与返回内容字段。菜单中的 AI 能力、业务逻辑、数据处理和其他分组归 `workflow.menu`，数据源与知识库分组分别复用 `resource.dataSource.label`、`knowledge.title`；共用用户输入标题、参数校验、全局变量及会话变量分别使用 `userInput`、`parameters`、`globalVariables`、`conversationVariables`；接口传参等节点文案归 `nodes.json` 的 `node`。
执行结果及共用详情文案复用 `common/execution.json` 中的 `execution.result`、`execution.details`；数据源名称、选择文案及文件查询不支持提示统一归 `resource.dataSource`。节点详情中的“输入／输出”“输入参数／输出参数”“历史记录”分别使用 `execution.details.input` / `output`、`inputParams` / `outputParams`、`history`；“本次对话／回答”使用 `currentChat` / `answer`；公共容器的“错误日志”标题使用 `execution.details.errorLog`，错误正文保留接口原文。

### 编辑页面与共用配置分工

- `layout.json` 维护 `menu`、`layout`、`defaultModel`、`publishHistory` 四个并列分组；节点添加面板分类使用 `workflow.menu.*`，`layout` 维护工作流页面框架及操作区文案：添加、搜索、缩放、布局、保存时间、自动保存、调试和退出确认，调用为 `workflow.layout.*`。
- `layout.json` 的 `defaultModel` 维护默认模型来源、选择、设置和批量应用，调用保持 `workflow.defaultModel.*`。
- `layout.json` 的 `publishHistory` 维护版本历史、发布内容及更新说明，调用保持 `workflow.publishHistory.*`。
- `ai-generation.json` 的 `aiGeneration` 维护 AI 生成面板、示例需求及工具活动标签，调用为 `workflow.aiGeneration.*`。
- `prompt.json` 维护 `systemPrompt`、`userPrompt`、`positivePrompt`、`negativePrompt`、`promptGeneration`，各组调用保持原有 key，不增加 `prompt` 层级。
- 节点专属文案归节点文件，历史聊天记录 `history`、输出思考 `thinking` 及其他跨节点共用字段留在 `index.json`。分文件不增加命名空间层级，同一顶层分组只由一个文件维护。

### 节点语言包分工

所有文件合并到 workflow 命名空间，文件名不增加翻译层级；同一节点跨画布模式共用文案。
同一顶层分组只由一个文件维护，不在 nodes.json 或其他文件重复定义。

| 文件                      | 顶层分组                                                                                                                                        |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| nodes.json                | 节点共用文案及未独立拆分节点，如 aiChat、start                                                                                                  |
| llm-node.json             | llm；含 LLM 工具声明                                                                                                                            |
| loop-node.json            | loop、loopStart、loopBody、loopContinue、loopBreak                                                                                              |
| tool-node.json            | toolStart、mcp、customTool、tool、toolWorkflow；资源管理文案仍属 tool 业务域                                                                    |
| knowledge-node.json       | searchKnowledge、searchDocument、documentExtract、reranker、documentSplit、localFile、webSource、knowledgeWrite；知识库资源和策略仍属 knowledge |
| data-processing-node.json | variableAssign、variableAggregation、variableSplitting、parameterExtraction                                                                     |

参数提取、循环参数、用户输入参数和变量字段的格式提示分别使用
`workflow.parameterExtraction.parameters.invalidMessage`、`workflow.loopStart.variables.invalidMessage`、
`workflow.userInput.invalidParameterMessage`、`workflow.variable.invalidMessage`，保留原校验含义。

基本信息节点的接口传参标题使用 `workflow.node.apiParameters.title`，节点必填／唯一性校验使用 `workflow.node.baseRequiredMessage` / `baseUniqueMessage`，统一在 `nodes.json` 的 `node` 分组维护。用户输入标题、当前表单、外置参数设置、其他参数收纳菜单标题及用户输入参数格式校验统一归 `workflow.userInput`，在 `index.json` 维护；遵守四层上限。共用参数校验和会话变量继续复用 `workflow.parameters`、`workflow.conversationVariables`。
工具基本信息节点的输入／输出参数表头、占位及通用操作复用 `dynamicForm.fields`、`common`，输入参数的数据类型复用 `tool.inputParams.dataType`；输入／输出标题设置与分段表单的标题字段复用 `common.title`，占位与必填提示保留独立 key。显示名称的标签、占位及已有必填提示统一复用 `dynamicForm.fields.displayName`，输出字段的显示名称保持可选；重名提示复用 `workflow.parameters.duplicateMessage`，参数名及原有冒号在使用处组合。缺省用户输入与输出参数标题分别复用 `workflow.userInput.title`、`tool.outputParams.title`，按初始化或重置草稿时的语言读取；已保存的标题、字段名称、描述和数据类型协议值保持原样，语言切换不重置配置或主动校验。
知识库基本信息节点的文档设置标题复用 `knowledge.document.settings.title`，字段表头、参数操作和标题设置复用 `dynamicForm.fields` 与 `common.title`；组件类型沿用 `DYNAMIC_FORM_TYPES` 的响应式名称，固定知识库输出使用 `knowledge.title`。用户保存的标题、字段、默认值与变量引用保持原样，语言切换不重置配置或主动校验。
工具开始节点及变量选择器的全局变量分组复用 `workflow.globalVariables.title`，参数输出分组使用 `workflow.toolStart.outputLabel`，保留“参数输出”原名；执行详情的输入参数标题复用 `execution.details.inputParams`。用户字段标签、值及 `global` / `output` 协议值保持原样。
知识库节点的共用字段、检索问题和范围，以及跨节点变量、引用和参数文案继续归 index.json。
节点共用的“结果”标签归 `workflow.node.result`；专属输出字段随节点分组维护，图片和视频类型复用 `upload.types`。循环开始的名称、下标与循环元素统一归 `workflow.loopStart`，循环内嵌定义与独立定义共用；循环体名称归 `workflow.loopBody`。
快捷键的节点复制／删除限制归 `workflow.node.copyDisabledMessage` / `deleteDisabledMessage`；粘贴数据的 JSON、对象、字段及节点格式提示归 `workflow.layout.paste`。在原处理函数中直接调用 `t`，节点名称及数组下标通过命名参数传入，保留 `nodes`、`edges`、`id` 协议字段；不修改保护范围、数据校验条件、异常类型或粘贴位置计算。
画布结构校验直接在原校验分支调用 `t`：开始节点的必填与唯一性提示归 `workflow.start`，基本信息节点的对应提示归 `workflow.node.baseRequiredMessage` / `baseUniqueMessage`，流程外节点、后继缺失、分支连接、不可用及结束节点限制归 `workflow.node.validation`。节点名称、分支类型及原有名称分隔符保持原值，校验条件与抛错类型不变；变量选择器的全局／会话分组分别复用 `workflow.globalVariables.title`、`workflow.conversationVariables.title`。
节点容器的禁用与资源不可用提示归 `workflow.node`，异常捕获与异常信息归 `workflow.node.exception`；执行条件标题、前置说明归 `workflow.node.executionCondition`，所有／任一选项复用 `workflow.condition.match`。默认输出参数标题复用 `execution.details.outputParams`，已保存的输出标题保持原值；不因语言切换修改启用、异常开关、执行条件或连线。
节点操作菜单的名称与来源标签归 `workflow.node.name`、`workflow.node.source`；重命名、复制、删除、启用状态和按钮复用 `common`。节点搜索共用名称占位，搜索空结果、缩放、适应视口、全部节点展开／收起、自动布局及失败提示归 `workflow/layout.json` 的 `layout`。节点添加入口与锚点的添加／连接提示同样归 `workflow.layout`，保留“添加组件”“点击添加节点”“拖拽连接节点”的原有名称和两行提示结构。计数比例与既有节点名称保留原值，语言切换不重置搜索、选中节点或画布状态。
节点菜单与快捷键的删除确认共用 `workflow.node.delete`，单个展示原节点名称，批量展示实际选中的节点数；节点保护与删除流程保持原样。
循环开始的变量标题和内置参数禁用提示归 `workflow.loopStart.variables`。参数、显示名称复用 `dynamicForm.fields`，添加／编辑及按钮复用 `common`，重名提示复用 `workflow.parameters`，循环参数格式提示使用 `workflow.loopStart.variables.invalidMessage`。内置字段常量通过响应式配置直接调用 `t`，输出区使用 `loopStart.index`、`item`，详情中的“循环项／循环下标”使用 `currentItem`、`currentIndex`，复制提示使用 `copyParameter`；字段选择器的循环变量分组在读取时调用 `t`。保留 `index`、`item`、`loop` 协议值、用户字段及复制引用，语言切换不重置表单或主动校验。
循环节点的类型、数组、次数和设置／详情标题归 `workflow.loop`，配置与执行详情共用文案。详情按循环类型显示数组或次数标签，已知类型使用 `type` 中的名称，未知类型保留原值；数组内容、次数、轮次编号及子节点执行数据保持原样，变量选择占位复用 `workflow.variable.selectPlaceholder`。无限循环缺少 Break 的提示归 `workflow.loop.validation.breakRequired`，在原有校验分支中直接调用 `t`。语言切换不重置循环配置或主动校验。
节点输出字段及执行详情中的“回答内容”统一使用 `index.json` 中的 `workflow.answer.label`；需要“AI 回答内容”时，在使用处直接拼接固定前缀 `AI `，不增加翻译 key 或辅助函数。LLM 直接使用共用标签，数据字段的 `answer`、`content` 协议值和已有节点内容保持原样。
节点输出字段及执行详情中的“思考过程”共用 `workflow.thinking.process`，与输出思考开关和标签设置一起归 `index.json` 的 `thinking`；`reasoning_content` 数据字段保持原样。
语音转文本配置中的“语音文件”使用 `workflow.speechToText.audioFile`，执行详情中的“音频文件”使用 `workflow.audioFile.label`（`index.json`）；缺省音频名称复用 `upload.types.audio`，实际文件名、URL、图标后缀及文件引用示例保持原样。语音转文本和文本转语音的模型标签分别归 `workflow.speechToText.model.label`、`workflow.textToSpeech.model.label`；文本转语音的输入内容标签归 `workflow.textToSpeech.content.label`，配置和执行详情共用。节点设置、返回内容和选择校验复用现有共用文案，语言切换不重置配置或自动触发校验。
意图识别的输入标签及意图分类配置归 `workflow.intent.input`、`workflow.intent.categories`，输出分类仍使用 `workflow.intent.category`。AI 模型标签复用 `model.ai.label`，历史记录、占位和校验复用现有共用文案。默认“其他”分类在节点初始化、表单及 AI 配置补齐分支时直接调用 `t`，已有分类内容、ID、`isOther` 标记和连线保持原样，切换语言不重写分支数据或主动校验。
问题优化节点的内置系统提示词归 `workflow.questionOptimization.systemPrompt.defaultValue`，在节点初始化时直接调用 `t`，按原有缺省条件填入；已有提示词保持原值，编号与换行结构沿用原文。AI 模型标签复用 `model.ai.label`，系统／用户提示词、历史记录、返回内容及执行详情标题复用相应公共文案，用户提示词的默认变量引用仍使用 `START_NODE_REFERENCES.question`；语言切换不重置内容或主动校验。
指定回复节点的回复格式与内容归 `workflow.reply.format`、`workflow.reply.content`；配置中的“回复类型”使用 `format.typeLabel`，执行详情中的“回复格式”使用 `format.label`，回复内容共用 `content.label`；引用变量及返回内容复用工作流共用文案。格式选项在原有名称映射中通过响应式配置直接调用 `t`，保留 `TEXT`、`HTML`、`TOOL` 协议值。示例的 JSON 字段和 HTML 标签留在代码中，只翻译说明及示例内容；变量引用通过 `{reference}` 原样传入，已保存回复与执行结果保持原值。
表单收集的输出内容字段、配置标题和未提交状态归 `workflow.form.content`、`configuration`、`notSubmitted`，输出字段名称复用 `formData`；说明中的 `{ form }` 通过命名参数原样传入。字段表头、添加／编辑及按钮复用 `dynamicForm.fields` 和 `common`，重名与失效引用提示复用 `workflow.parameters.duplicateMessage`、`workflow.referenceVariable.missingMessage`。已有字段、默认值、输出模板及显隐引用保持原值，语言切换不重置配置或主动校验；执行详情保留原提交状态判断和括号格式。
变量的通用标签、输入占位、必填／重名提示及添加／编辑操作统一归 `index.json` 中的 `workflow.variable`，赋值、聚合和拆分节点直接复用；输入变量标签归 `workflow.variable.input`，参数提取的“请选择输入变量”使用该组的 `requiredMessage`。普通变量选择的占位与校验使用 `workflow.variable.selectPlaceholder` / `selectRequiredMessage`；明确写“请选择引用变量”的位置使用 `workflow.referenceVariable.placeholder` / `requiredMessage`，变量拆分保留“请选择变量”。引用变量继续归 `workflow.referenceVariable`，节点专属的变量列表和配置留在各自节点分组。
变量赋值的目标变量标签复用 `workflow.variable.label`，赋值文案归 `workflow.variableAssign.value`，自定义赋值的输入占位复用 `common.placeholders.input`；引用标签复用 `workflow.referenceVariable.label`，原有“请选择变量”的占位及必填提示使用 `workflow.variable.selectPlaceholder` / `selectRequiredMessage`，通用输入／选择必填和 JSON 格式提示复用 `common.validation`。执行详情共用输入／输出参数标题，变量名称、值、类型及原有括号和冒号按原数据展示。`string`、`num`、`json`、`bool`、`null`、`true`、`false` 保留协议名称，语言切换不重置赋值配置或主动校验。
变量聚合的策略、分组操作和字典键名归 `workflow.variableAggregation.strategy`、`group`、`key`；首个非空值策略的配置选项使用 `firstNonNull`，详情完整说明使用 `firstNonNullDescription`。变量字段复用 `workflow.variable`，显示名称、变量格式校验和通用按钮复用已有文案；分组输入标题按“原分组名称 + 输入参数”组合。策略协议及旧值兼容、默认 `Group1` 标识、分组名称、变量引用、字典键和执行值保持原样，语言切换不重置配置或主动校验。
变量拆分的拆分变量列表与 JSON Path 提示归 `workflow.variableSplitting`；输入变量、变量字段与添加／编辑操作复用 `workflow.variable`，显示名称、变量格式校验、选择提示及通用按钮复用已有文案。节点创建与编辑变量后的“结果”输出标签共用 `workflow.node.result`，执行详情复用输入／输出参数标题；JSON Path 示例通过命名参数原样传入，表达式、变量标识、用户显示名称、文档链接和执行数据保持原值，语言切换不重置配置或主动校验。
参数提取的提取参数列表与参数类型归 `workflow.parameterExtraction.parameters`、`type`；参数、显示名称、描述、模型和添加／编辑操作复用已有文案，格式校验使用 `workflow.parameterExtraction.parameters.invalidMessage`，重名校验复用 `workflow.parameters.duplicateMessage`。节点创建与参数编辑后的“结果”输出标签共用 `workflow.node.result`，执行详情复用输入／输出参数标题；`string`、`number`、`object`、`boolean`、`array` 类型值、参数标识、用户显示名称、描述和模型来源规则保持原样，语言切换不重置配置或主动校验。
知识库检索的图片字段归 `workflow.searchKnowledge.image`；参数摘要与设置弹窗共用 `knowledge.retrieval`，模式选项沿用 `KNOWLEDGE_SEARCH_MODE_OPTIONS`，未知模式值保留原文。知识库检索、文档标签检索与多路召回的问题标签、占位和必填提示共用 `index.json` 中的 `workflow.searchQuestion`；知识来源显示开关共用同文件的 `workflow.showInSources`。范围名称、自定义选项、关联提示和列表来源归 `workflow.searchScope`，引用文案与校验复用 `workflow.referenceVariable`。示例只翻译 `common.labels.example`，JSON 和资源 ID 原样保留。范围协议、选择状态、关联数据、数值范围及检索模式切换时的相似度规则保持原样，语言切换不重置配置或主动校验。
检索节点执行详情的“检索内容”标题共用 `execution.details.retrievalContent`，知识库检索结果标题复用 `workflow.searchKnowledge.result`。图片／文本向量标签归 `knowledge.retrieval.imageVector`、`textVector`，召回测试与工作流详情共用；检索问题、分段内容、标题、知识库及文档名称保留接口原文，排序、相似度数值、图片预览和来源文件操作沿用原有规则。
多路召回的重排内容字段与 Score 阈值说明归 `workflow.reranker.content`、`score`，配置、参数摘要、弹窗及详情共用对应标签；重排模型复用 `model.types.reranker.label`，检索参数及召回分段数复用 `knowledge.retrieval`；“最大引用字符数”使用 `workflow.reranker.maxReferenceCharacters`，不替换为检索配置中的“最多引用字符数”。详情复用检索内容与图片／文本向量标签，结果标题沿用 `workflow.reranker.result`。保留模型来源、变量引用、数值范围、检索结果顺序及来源文件操作，语言切换不重置配置或主动校验。
文档标签检索的自动／手动设置与说明归 `workflow.searchDocument.searchMode`，值或变量占位归 `value.placeholder`；条件匹配和添加条件复用 `workflow.condition`，标签选择复用 `knowledge.tags.key.selectPlaceholder`。比较符名称复用 `dynamicForm.operators`，节点常量使用响应式配置，AI schema 延迟读取比较符说明；选项范围、顺序、`auto`／`custom`、`AND`／`OR` 和比较符协议值保持原样。标签与实际值按接口或用户输入展示，不随语言切换重新查询或清空；执行详情只翻译输出参数标题，`knowledge_list`、`document_list` 及名称分隔格式保留原样。
文档内容提取与文档分段的文档字段共用 `index.json` 中的 `workflow.document`，旧执行记录的缺省文件名称复用文档字段标签，编号在使用处组合。内容提取与 Web 数据源的预览限制说明共用 `workflow.document.characterPreviewHint`；节点设置、输出参数标题及字符单位复用已有文案。实际文件名、内容、来源及变量引用保持原值，文档内容预览沿用 500 字符限制，语言切换不重置当前文档或主动校验。
文档分段的策略字段、配置来源、子分块长度及其说明、关联问题开关归 `workflow.documentSplit`，“子分块长度”使用 `childChunkLength.label`；智能／高级策略名称、分段标识、分段长度和自动清洗复用 `knowledge.documentStrategy`，问答对名称复用 `knowledge.document.upload.qaLabel`。策略常量通过响应式配置直接调用 `t`，配置与详情按原属性读取。保留策略与来源协议值、正则标识、数值范围、条件校验和前 5 个分段的预览规则，实际文件名、标题与正文保持原值，语言切换不重置选择或配置。
知识库写入的输入内容字段归 `index.json` 中的 `workflow.inputContent`，文档分段详情共用其 `label`；写入内容标题归 `workflow.knowledgeWrite.content`。两个节点的文档分段预览限制共用 `workflow.document.paragraphPreviewHint`，字符单位复用 `knowledge.stats.characters`。保留引用有效性校验、旧配置的末端输出默认值和执行数据，规则在 computed 中直接调用 `t`，语言切换不主动校验或重置配置与文档选择。
本地文件数据源的格式、文件数量及大小限制归 `workflow.localFile.format`、`fileCount`、`fileSize`，执行详情复用同组的 `fileList`。范围校验通过命名参数传入上下限，大小标签的 `MB` 与括号保留在模板中；格式后缀、自定义格式、默认值和 1–1000 整数范围保持原样。规则在 computed 中直接调用 `t`，语言切换不重置配置或主动校验，文件名称及下载行为沿用执行数据。
Web 数据源的无配置提示归 `workflow.webSource.noConfiguration`，详情的选择器与文档地址复用 `knowledge.fields.selector.label`、`knowledge.document.sourceUrl.label`，输入／输出参数及预览说明复用工作流共用文案。URL、选择器、文档名称和正文保持原值，沿用文档选择与预览截取逻辑，不因语言变化重置选择。
智能体节点配置中的“用户问题”复用 `workflow.start.question`，执行详情中的“问题”使用 `common.labels.question`，分别保留原有名称。文档字段复用 `workflow.document`，图片、音频、视频类型及缺省名称复用 `upload.types`，执行详情中的“其他”使用 `common.labels.other`。按字段名称选择的占位及必填提示分别使用 `common.placeholders.selectField`、`common.validation.selectFieldRequired`，动态参数占位复用 `dynamicForm.fields.parameter.selectPlaceholder`。原有字段名称由既有规则读取后直接传入 `{label}`，不翻译用户字段、变量路径或执行内容；语言切换不重新加载智能体配置、重置引用或主动校验。
图片与视频生成的正向提示词标签、必填提示及负向提示词标签、说明归 `prompt.json` 中的 `workflow.positivePrompt`、`workflow.negativePrompt`。图片生成的模型标签、正向提示词说明和负向提示词占位分别归 `workflow.imageGenerate.model`、`positivePrompt`、`negativePrompt`；执行详情中的“负向提示词”使用 `workflow.negativePrompt.detailLabel`，配置中的“提示词(负向)”仍使用 `label`；回答内容复用共用标签，本次对话标题复用 `execution.details.currentChat`。已有提示词、变量引用及生成结果保持原值，语言切换不重置内容或主动校验。
视频生成的负向提示词占位共用 `workflow.negativePrompt.videoPlaceholder`。图生视频和文生视频的模型标签、正向提示词说明分别归 `workflow.imageToVideo`、`workflow.textToVideo`。首／尾帧字段归 `workflow.imageToVideo`，配置使用 `firstFrame.label`、`lastFrame.label`，详情标题和图片缺省名称中的“首帧／末帧”使用各字段的 `shortLabel`，首帧必填与尾帧可选规则保持原样。实际文件名、媒体地址、引用路径和文件引用示例不进入语言包。
LLM 节点名称固定使用 `LLM`，不建立名称翻译 key；其上下文标签、说明、占位及必填提示归 `workflow.llm.context`；AI 模型标签复用 `model.ai.label`，系统／用户提示词及返回内容复用工作流共用文案。保留上下文开关与用户提示词必填条件，切换语言不重置节点配置或自动触发表单校验。
LLM 工具声明归 `workflow.llm`：声明及来源使用 `tools`，工具名称、描述、参数和数据类型分别使用 `toolName`、`toolDescription`、`toolParameters`、`dataType`，JSON 解析和导入使用 `jsonParse`、`toolImport`。参数基础字段与必填标签复用 `dynamicForm.fields`，“添加工具参数／编辑工具参数”使用 `workflow.llm.toolParameters.addTitle` / `editTitle`，通用操作复用 `common`，参数重名提示复用 `workflow.parameters.duplicateMessage`。OpenAI 类型值、函数名和 JSON 结构保留原样，导入示例的说明文字直接调用 `t`，不把整段 JSON 放入语言包。
LLM 执行详情的系统／用户提示词及回答内容标题复用工作流共用字段，上下文、结束原因、拒答内容和工具调用标题复用 `workflow.llm`，不另设详情分组。节点名称、提示词及模型输出正文、消息角色、结束原因协议值和工具调用 JSON 按执行数据原样展示；`tokens`、`s` 和占位符 `-` 保持原样。
MCP 节点的服务配置名称、配置／引用必填提示、获取工具结果提示、工具参数标题和变量设置弹窗标题归 `tool-node.json` 中的 `workflow.mcp`，配置与执行详情共用工具参数标题。原有 `MCP Server Config` 名称保留；引用 MCP、自定义来源及 MCP 工具必填提示复用 `tool.mcp` / `tool.source`，引用变量与选择占位复用工作流共用文案，输入提示、空状态和按钮复用 `common`。工具名称、参数名及说明由 MCP 接口提供，JSON 示例、配置中的变量引用与执行结果保持原值；在原有函数或模板中直接调用 `t`，语言切换不重新请求工具、改写节点数据或主动校验。
AI 对话、图片理解及视频理解的智能体与知识库执行详情中，思考过程使用 `workflow.thinking.process`，AI 回答内容按共用标签组合；本次对话、系统／用户提示词复用工作流共用字段，“历史记录”使用 `execution.details.history`，图片／视频标签及缺省名称复用 `upload.types`。各模式保留已有区块与显隐条件，消息角色、正文、实际文件名及媒体地址按执行数据原样展示；视频图标使用的 `video.mp4` 保持原样。图片和视频理解的视觉模型标签复用 `model.types.image.label`，用户提示词、输出思考与返回内容复用工作流共用文案，媒体选择占位和必填提示分别复用 `common.placeholders.select`、`common.validation.selectRequired`；语言切换不重置配置或自动校验。
按已处理的业务范围增加文件；知识库、工具专属节点与画布控制、执行详情分别按职责归组，不为每个组件新建文件。
节点配置文案归 `workflow`，资源实体名称、创建和管理操作仍复用 `application`、`knowledge`、`tool`；同名中文不作为归类依据。
节点设置标题归 `nodes.json` 的 `workflow.node.setting`，返回内容开关归 `index.json` 的 `workflow.returnContent`；历史记录来源选项复用 `workflow.node.title`（`nodes.json`）和 `workflow.title`（`index.json`），保留 `NODE`、`WORKFLOW` 协议值。知识库四种资源范围的工作流入口菜单共用 `workflow.title`。节点系统／用户提示词的占位使用 `workflow.systemPrompt.placeholder`、`workflow.userPrompt.placeholder`，通过 `{reference}` 原样传入 `START_NODE_REFERENCES.question`。AI 对话的视觉开关归 `workflow.aiChat.vision`，图片／视频标签复用 `upload.types`，技能标题与输出执行过程复用 `application.skills`；语言切换只更新展示，不重置已保存提示词和节点配置。
工具执行记录与详情的触发来源标签使用 `execution.records.triggerSource`，来源类型名称复用 `application.title`、`knowledge.title`、`tool.title`、`trigger.title`；原来源映射使用响应式配置直接调用 `t`，筛选与表格共用。工作空间标签复用 `workspace.title`，其余执行字段和翻页复用 `execution`、`common`；保留来源协议值、名称、范围显示条件及查询流程。
知识库工作流执行记录与详情复用 `execution.records`、`execution.details`，发起人标签使用 `execution.records.initiator`；取消执行入口和完整确认句归 `execution.cancel`。耗时、状态、操作和记录翻页复用 `common`，发起人姓名、日期和秒数保持原样，翻译不改变轮询、排序、分页或取消请求流程。
工具工作流调试的输入／输出参数及执行详情标题复用 `execution.details`，参数占位复用 `dynamicForm.fields.parameter`，调试标题复用 `common.actions.debug`，运行按钮与结果、调试结果标题、回答中及调试请求错误归 `tool.debug`。JSON 数组与对象输入要求复用 `common.validation.jsonArrayRequired` / `jsonObjectRequired`；回复内容标签复用 `workflow.reply.content.label`。用户参数名、协议类型、服务端错误和流式内容保持原值，语言切换不触发校验、运行或重置输入。
AI 生成引擎缺少模型、轮次上限及流式／单轮响应不完整等本地终止错误归 `workflow.aiGeneration.errors`；在原错误分支直接调用 `t`，轮次上限通过 `{max}` 传入。服务端错误原文优先，模型指令及回喂模型的工具结果保留原值。
AI 生成面板的说明、示例需求、状态及工具活动名称归 `ai-generation.json` 的 `workflow.aiGeneration`，面板标题复用 `workflow.layout.aiGenerate`，生成中复用 `common.status.generating`。原工具名称映射使用响应式配置直接调用 `t`，未知工具名保留协议值；示例需求响应当前语言，已发送需求、模型回复、工具参数及历史活动按事件发生时的内容保留，不新增翻译辅助函数或语言监听。内部模型指令不在此批翻译。
工作流资源范围不支持流式补全时，原 Store 请求分支直接调用 `workflow.layout.streamingUnavailableMessage`，通过 `{scope}` 保留范围协议值；不新增翻译辅助函数或改动请求能力判断。
工作流模板应用与文件导入共用 `workflow.layout.overwriteMessage`，通过 `{name}` 传入模板名或去除扩展名后的文件名；应用成功、工作流导入／导出入口、文件格式提示和导出失败归 `workflow.layout`，导入成功复用 `common.messages.importSuccess`。知识库未发布时的文档导入限制归 `knowledge.workflow.documentImportUnavailableMessage`。模板、文件名称、扩展名校验及覆盖流程保持原样。
工作流页面头部的保存时间、自动保存、AI 生成和未保存退出确认归 `workflow.layout`，保存／发布／调试按钮及成功提示复用 `common`；模板中心、默认模型与发布历史入口复用各自标题，恢复按钮复用 `workflow.publishHistory.restore`。保存时间只翻译标签，日期和分隔符保持原格式；语言切换不触发保存、发布或恢复版本。
工作流三种资源共用的发布历史、版本内容及更新说明文案归 `workflow.publishHistory`；标题字段复用 `common.title`，编辑／发布按钮及修改成功提示复用 `common`。版本名称、发布人、日期和更新说明正文保持原值，语言切换不重查历史或重置草稿。
默认模型设置抽屉与入口的标题、说明、应用到所有节点及未保存确认归 `workflow.defaultModel`；通用按钮和提示标题复用 `common`。模型类型读取 `MODEL_TYPE_LABELS`，AI 模型名称使用 `model.ai.label`。入口自定义 `label` 优先，缺省时直接调用 `t`；模型来源、草稿比较、保存和批量应用流程保持原样。
节点模型选择组件的默认模型、自定义和未配置提示复用 `workflow.defaultModel`，带模型名称的默认配置校验使用 `selectRequiredMessage`；引用变量的标签、占位和校验提示归 `workflow.referenceVariable`。`NodeCascader` 的未选择、引用错误和引用不存在提示分别使用 `requiredMessage`、`invalidMessage`、`missingMessage`；用户输入的显隐引用校验复用 `missingMessage`。自定义模型的占位与必填校验分别复用 `common.placeholders.selectField`、`common.validation.selectFieldRequired`，通过 `{label}` 接收调用方的展示名称。组件在模板或校验执行时直接调用 `t`，保留来源协议和原校验条件，不随语言切换重置选择或主动校验。
国际化不得更改 `node-data.ts` 的数据属性名或结构，也不得增加属性。菜单名称、说明与搜索直接读取节点定义的 `label`、`text`，与 AI 节点目录共用，不维护独立的节点展示映射。各模式的菜单分组在 `reactive` 配置的 `label` 中通过 `computed(() => t(...))` 翻译，界面与 AI 目录直接读取 `group.label`。点击和拖拽仍传递原节点配置，菜单展示与搜索不修改节点名称、属性或变量路径。
节点菜单的“基础组件”页签使用 `workflow.menu.basicComponents`，工具、智能体和数据源页签分别复用 `tool.title`、`application.title`、`resource.dataSource.label`；按名称搜索的占位复用 `common.placeholders.searchByName`，资源卡片的智能体类型标签复用 `application.advanced.shortLabel` / `simple.shortLabel`。页签协议值、筛选条件和资源名称保持原样，切换语言不重新请求资源。
开始节点的默认名称、用户问题及内置全局字段默认标签在 `node-data.ts` 中通过 `reactive` 与 `computed(() => t(...))` 提供；组件初始化及字段回填时直接调用 `t`，共用 `workflow.start` 文案，历史聊天记录复用 `workflow.history.label`。默认名称使用 `workflow.start.label`；节点内置的默认用户问题引用及提示示例统一读取 `config/constants.ts` 的 `START_NODE_REFERENCES.question`，常量通过响应式配置拼接当前语言的节点名称，保留双层花括号及 `.question` 字段。该默认配置不负责已打开节点的实时语言切换，已有节点名称、已保存提示词、字段协议值和用户自定义字段沿用原值。

智能体基本信息的名称、描述、开场白、长期记忆和语音设置复用 `application`；用户输入、接口参数和会话变量的字段标签、占位及必填提示复用 `dynamicForm.fields`，添加／编辑参数复用 `common.parameters`。
参数重复提示仅翻译文字，参数名和分隔符在调用处组合。周期选项直接读取 `SCHEDULE_OPTION` 的响应式标签，保留保存协议；切换语言不重新校验表单。
节点缺省开场白与用户输入标题分别复用 `application.prologue.defaultValue`、`workflow.userInput.title`，默认定义通过响应式配置读取，组件初始化时直接调用 `t`；基本信息名称复用 `common.labels.basicInfo`。表单默认输出内容归 `workflow.form.defaultContent`，通过命名参数原样传入 `{{form}}`。创建节点时复制为普通数据；已有图数据、模板内配置、节点名称及变量引用路径保留原文。长期记忆说明中的默认引用示例读取 `START_NODE_REFERENCES.memory`，再通过参数传入文案。
文件上传配置的类型名称在响应式展示配置中直接调用 `t`；开始节点在刷新文件字段时复用 `upload.types`，长期记忆字段复用 `application.longTermMemory.label`，只写入当前语言的普通字符串。文件后缀、大小单位、数量与原有拼接标点保持原样。
判断器及 Break／Continue 的比较符复用 `dynamicForm.operators`；`compareList` 的 `label` 通过响应式配置直接调用 `t`，按当前语言提供名称，比较符值与顺序保持原样。AI 条件 schema 的比较符说明延迟读取这些名称，不在模块初始化时固化译文。文件引用示例的标题复用 `common.labels.example`，JSON 数据由 `FILE_REFERENCE_EXAMPLE` 提供，不进入语言包。
判断器及 Break／Continue 的条件匹配和添加条件操作共用 `workflow.condition.match`、`workflow.condition.actions.addCondition`；匹配文案前后分别调用 `t`，中间保留所有／任一下拉框。判断器的添加分支和结果标题归同组的 `actions.addBranch`、`result`。变量选择复用 `workflow.referenceVariable`，比较值的占位与校验分别复用 `dynamicForm.fields.comparisonValue.placeholder`、`requiredMessage`；比较符选项直接读取 `compareList.label`。Break／Continue 执行详情的输出参数标题复用 `execution.details.outputParams`，是否退出／继续分别归 `workflow.loopBreak.isBreak`、`workflow.loopContinue.isContinue`。分支类型、ID、比较符与逻辑协议值、比较值及执行结果保持原值，语言切换不重置条件或自动校验。

## 触发器

`trigger.json` 维护触发器业务，管理列表、工作空间和系统资源管理中的智能体／工具入口及资源触发器弹窗共用 `trigger.title`。
定时与事件类型分别归 `scheduled` / `event`，名称使用 `label`；任务、下次执行时间等展示标签归 `labels`，删除确认与影响说明归 `delete`。
名称、描述、创建信息、启停状态、通用操作和成功提示复用 `common`；任务分组名称复用 `application.title` / `tool.title`，执行记录入口复用 `execution.records.title`。
资源触发器的周期摘要复用 `common.schedule`，只翻译周期、星期和单位，日期数字、时刻和间隔值在使用处组合；Cron 表达式、触发器名称和描述保持原值。
类型和状态选项响应当前语言，筛选与启停请求仍使用原有协议值；已有周期摘要函数在执行时直接调用 `t`。
创建／编辑标题使用 `createTitle` / `editTitle`，名称字段归 `fields.name`；触发周期归 `scheduled.period`，事件地址与令牌校验归 `event`。
请求参数的标题、名称、数据类型及校验归 `requestParameters`，参数与必填表头复用 `dynamicForm.fields`；任务执行标签和必选提示归 `taskExecution`；内置“问题”复用 `common.labels.question`，文件类型复用 `upload.types`，来源选项复用 `common.options.reference` / `custom`，事件请求参数的无效引用提示归 `taskExecution.invalidReferenceMessage`。
周期级联选项直接读取 `SCHEDULE_OPTION` 的响应式 `label`，不改写共享常量；Cron 字段与校验复用 `common.schedule.cron`。输入占位与必填提示分别使用 `common.placeholders.inputField` / `common.validation.inputFieldRequired`。
任务参数只翻译内置展示标签；用户定义的参数名、`body` 路径、数据类型、引用来源值和默认值保持原样。语言切换不初始化任务参数，不自动触发表单校验。
执行记录标题、资源类型及执行时间归 `execution.records`，详情标题及错误信息归 `execution.details`，触发失败使用 `trigger.taskExecution.triggerFailed`；触发任务和触发器入参分别使用 `trigger.taskExecution.task` / `trigger.taskExecution.triggerInput`。
触发器、工具和知识库工作流执行记录的状态筛选与展示直接读取 `EXECUTION_STATUS_OPTIONS` 的响应式 `label`，通用状态复用 `common.status`；名称、状态表头、耗时、操作和记录翻页复用 `common`，资源类型名称复用 `application.title` / `tool.title`。
查询、排序和跨页浏览使用原协议值，未知状态及接口返回的任务名称、入参和错误内容保留原文；节点内部详情文案随工作流节点批次接入。

## 知识库列表

英文界面将“知识库”统一译为 `knowledge`，独立标题写作 `Knowledge`，例如“全部知识库”为 `All knowledge`。
“分段”的英文统一使用 `segment` / `segments`，按语境使用单复数和句首大写；文件名、翻译 key 及代码字段继续沿用 `paragraph`。用于向量检索的“子块”使用 `child chunk`，与完整分段区分。
工作空间、系统资源管理和系统共享资源的知识库菜单与列表标题共用 `knowledge.title`。四类知识库分别归 `knowledge.base`、`knowledge.web`、`knowledge.lark` 和 `knowledge.workflow`。类型筛选、类型列和创建菜单共用各组的 `label`，菜单说明使用 `description`，创建弹窗标题使用 `createTitle`。筛选请求沿用数字类型值。
卡片的文档数、字符数和图片数使用 `knowledge.stats`，按实际数量选择单复数。向量化和分词索引归 `knowledge.actions`；同步入口使用 `knowledge.sync.label`。
跨资源的模板中心文案归 `resource.templateStore`。模板名称、描述和 README 展示接口原文；缺少说明时与工具商店共用 `common.empty.noDetails`。
手动同步、定时同步及日志共用 `knowledge.sync` 中的同步方式。向量化和生成问题共用的分段范围在 `knowledge/index.json` 中维护，使用 `knowledge.paragraphScope`。生成问题弹窗的 AI 模型字段复用 `model.ai`，入口、其他字段、校验和内置默认提示词归 `knowledge.generateQuestions`；按钮、任务标签与弹窗标题共用 `title`，取消生成使用 `cancel`，均在 `knowledge/index.json` 维护。无已保存配置时按打开弹窗时的语言填入默认提示词，保留 `{data}` 与 `<question></question>`。提交时使用编辑框中的原文。
导出格式与源文件说明归 `knowledge.export`，单个及批量删除的确认标题归 `knowledge.delete`。
Web 创建的根地址与选择器归 `knowledge.fields`。创建、文档上传、导入和设置共用的分段规则、图片处理与索引增强文案归 `knowledge.documentStrategy`。
分段标识的文字选项归 `knowledge.documentStrategy.splitPatterns`，在 `knowledge/settings.json` 中维护。文档策略表单与工作流分段节点直接读取 `DOCUMENT_SPLIT_PATTERN_OPTIONS` 的响应式 `label`；纯符号与正则 `value` 保留原值，Agent 通过 `DOCUMENT_SPLIT_PATTERNS` 读取固定参数标识。

## 系统管理

`system/` 是分类目录。`system/index.json` 中的 `menu` 维护身份与权限、资源管理、共享资源、对话端管理和系统设置等分组标题，引用为 `system.menu`；已有业务标题继续复用各业务的 `title`。
同一文件的 `member` 维护系统管理内共用的成员标签、选择占位、必填提示和添加成员入口，使用 `system.member.label`、`placeholder`、`requiredMessage` 和 `add`；单项移除标题使用 `removeTitle`，按成员数量批量移除的标题使用 `batchRemoveTitle`。
工作空间、系统用户组、角色和对话用户组复用这些文案，添加成员按钮与弹窗标题共用 `system.member.add`；“用户名/姓名”“请选择对话用户”等具体选择说明保留业务含义，不统一替换为成员文案。
全项目通用操作及结果提示仍归 `common`，系统内共用文案归 `system`，各业务的成员关系、移除影响和权限回收说明保留在所属业务。
成员关系的移除与人数统计使用“成员”／“成員”／`member`，账号管理及用户名等账号属性保留用户语义。
用户管理使用 `system/user.json`，JSON 直接维护用户字段，引用为 `user`。
菜单与列表共用 `user.title`；创建／编辑标题、用户字段、角色分配和删除确认归该分组，
字段的 label、placeholder 和 requiredMessage 同级维护，不再叠加 fields，翻译 key 保持最多四层。
通用操作、状态、创建时间和结果提示复用 `common`，字符长度范围复用 `common.validation.lengthRange`，工作空间标签复用 `workspace.title`。
用户来源通过 `LOGIN_METHOD_LABELS` 读取认证方式及平台名称，本地来源使用 `user.source.local`；
页面在 computed 中调用 `t` 生成标签，筛选和表格使用同一组文案，不改写共享常量。未知来源及接口返回的角色、工作空间和用户组名称保留原文。
用户表单规则在 computed 中翻译，使用 `validate-on-rule-change=false`；语言切换不重置表单、不重新请求选项、不主动触发校验。
用户导入标题、说明、模板和导入结果归 `user.import`，文件选择校验及支持格式标签复用 `upload`；
重复用户名、姓名及邮箱提示归各字段的 `existsMessage`。成功及跳过人数按实际数量选择单复数，冲突用户名称保留原文。
导入来源选项在 computed 中翻译；非企业版的内置默认工作空间名称使用 `workspace.default`，接口返回的工作空间名称不替换。
默认密码、新密码及修改结果归 `user.password`，确认密码及匹配校验归同级的 `user.confirmPassword`；
角色设置入口归 `user.role`。用户角色与用户组分配的设置方式统一归 `user.assignment`，`label`、`append`、`replace` 分别维护设置方式、追加和替换；实际提交继续使用原有 `is_append` 布尔值。

对话用户管理使用 `system/chat-user.json`，命名空间为 `chatUser`；菜单与列表共用 `chatUser.title`，本地创建来源归 `chatUser.source.local`，配额入口、用量、到期时间及不限标签归 `chatUser.quota`。
创建／编辑标题、姓名、用户名、邮箱、手机号、默认密码和删除确认复用 `user`，操作、状态、日期及结果提示复用 `common`；来源筛选与表格在 computed 中使用同一组翻译，保留登录方式协议值和固定英文名称。
对话用户修改密码复用 `user.password` 与 `user.confirmPassword`，密码长度提示复用 `common.validation.lengthRange`；批量用户组分配复用 `user.assignment`，保存按钮及成功提示复用 `common`。
用量显示只翻译“不限”，数值与 `/` 在使用处组合。表单规则在 computed 中翻译，使用 `validate-on-rule-change=false`，切换语言保留筛选、选择和表单输入。
配额设置的方式选项、周期及 Tokens 上限字段和校验归 `chatUser.quota`；周期前缀“每”与天／周／月单位复用 `common.schedule.every` 和 `common.schedule.units`，英文单位按当前周期数量选择单复数，周期数值直接由输入控件显示。按钮复用 `common`，“配额设置成功”使用 `chatUser.quota.saveSuccess`，K 单位换算和配额请求参数沿用原有业务规则。
对话用户导入的专属说明归 `chatUser.import.description`；标题、模板、文件格式要求及成功／跳过人数复用 `user.import`，冲突提示复用用户字段的 `existsMessage`，来源字段与选项复用 `user.source` 及登录方式文案。来源协议值单独保存，选项在 computed 中翻译，切换语言不重选来源或重新请求选项；用户组及冲突用户名称保留原文。结果中的人数按实际数量选择单复数，用户名列表和结果分隔沿用固定标点，不按语言判断，也不为单独标点新增翻译键。

系统用户认证与对话用户认证的菜单、页面标题分别共用 `system.menu.userAuthentication` 和 `system.menu.chatUserAuthentication`。两处认证表单共用 `auth` 文案。扫码登录页签使用 `auth.qrCode.label`，平台配置入口与未配置状态复用 `common.configuration.label` / `unconfigured`，校验有效状态使用 `auth.qrCode.valid`；平台名称复用 `auth.methods`，保存成功提示复用 `common.messages.saveSuccess`。LDAP、CAS、OIDC、OAuth2、SAML2 等固定协议名称保留原文，页签选项在 computed 中翻译；切换语言保留当前页签、缓存的配置表单和平台启停状态，不重新请求配置。
登录设置归 `auth.loginSettings`，包含登录方式、默认方式、验证码、账号锁定和第三方用户默认角色分配；数字输入前后的说明使用对应的 `Prefix` / `Suffix`，英文按失败次数处理单复数，保留原控件顺序。账号锁定说明中的逗号随 `lockout.failureSuffix` 维护，模板不重复追加。角色、工作空间和用户组字段复用 `user`、`workspace`、`userGroup`；接口返回的选项名称保留原文。
扫码登录配置抽屉的标题使用 `common.configuration.title`，通过 `{name}` 传入已翻译的平台名称；回调地址标签归 `auth.fields.callbackUrl.label`，校验按钮及结果提示归 `auth.qrCode.validate` 和 `auth.qrCode.messages`。固定参数名沿用 `SCAN_FIELD_LABELS`，输入占位及必填提示复用 `common.placeholders.input` / `common.validation.inputFieldRequired`；字段名与接口值保持原样，回调地址仍由当前 API base 路径生成。表单使用 `validate-on-rule-change=false`，语言切换不重置草稿或主动触发校验。
LDAP 地址、绑定 DN、用户 OU、用户过滤器及属性映射归 `auth.ldap`，字段的 `label`、`placeholder`、`requiredMessage` 同级维护，密码复用 `auth.fields.password`。启用认证的完整文案使用 `auth.enableAuthentication`，以 `{provider}` 传入协议名称；保存、测试连接及结果提示复用 `common`。LDAP 表单的规则在 computed 中翻译，并关闭规则变化时自动校验；配置字段、连接测试与保存请求、属性映射内容及原校验条件保持原样。
CAS 验证地址归 `auth.cas.validateUrl`，回调地址及其占位、必填提示复用 `auth.fields.callbackUrl`；`ldpUri` 沿用固定字段名，输入占位与必填提示分别复用 `common.placeholders.inputField` / `common.validation.inputFieldRequired`。启用认证及保存提示复用 `auth.enableAuthentication` 和 `common`。CAS 表单使用响应式规则并关闭规则变化时自动校验；默认回调地址、验证地址回退、配置字段和提交接口保持原样。
认证协议共用的授权端、Token 端、用户信息端地址、客户端 ID／密钥及字段映射归 `auth.fields`，与回调地址保持同级。OIDC 的 `Scope`、`State` 和 Scope 示例保留原文；Scope 必填提示复用 `common.validation.inputFieldRequired`，State 输入占位复用 `common.placeholders.input`，配置值及默认字段映射不参与翻译。OAuth2 的“连接范围”标签、输入占位及必填提示归 `auth.oauth2.scope`，其余字段复用 `auth.fields`。
SAML2 的请求签名和断言签名开关归 `auth.saml2`；固定英文参数名保留原文，占位与必填提示复用通用字段提示，字段映射复用 `auth.fields.fieldMapping`。签名开关绑定、默认地址及提交配置保持原有实现。

邮箱设置使用 `system/email.json`，命名空间为 `email`；菜单与页面共用 `email.title`，SMTP 账户、发件人邮箱及 SSL／TLS 开关说明归该业务域。`SMTP Host`、`SMTP Port` 等固定字段名保留原文，占位与必填提示复用 `common.placeholders.inputField` / `common.validation.inputFieldRequired`；密码标签和必填提示复用 `auth.fields.password`，发件人密码占位归 `email.password.placeholder`。保存、测试连接及结果提示复用 `common`；表单规则在 computed 中翻译，关闭规则变化时自动校验，保留端口字符串转换、开关状态、校验条件和提交接口。

门户访问设置使用 `system/portal.json`，命名空间为 `portal`；菜单与页面共用 `portal.title`，门户名称归 `name`，访问方式及说明归 `access`，跨域配置归 `cors`。默认门户名称按进入页面时的语言初始化，接口返回的名称及编辑草稿保留原文；预览中的智能体分类和姓名复用 `application`、`user`，“新建对话”复用 `chat.newChat`。对话共用文案维护在各语言根目录的 `chat.json`，命名空间为 `chat`。登录配置复用 `auth.loginSettings`，至少选择一种登录方式的校验使用 `method.minSelectionMessage`；保留门户自己的数值范围、默认方式联动及保存字段。表单规则在 computed 中翻译，切换语言不重置草稿、不重新请求或主动校验；跨域示例地址与按行解析规则保持原样，按钮及保存提示复用 `common`。

工作空间管理使用 `system/workspace.json`，菜单与列表标题使用 `workspace.title`，创建／重命名标题和名称字段归 `workspace`，
删除工作空间与移除成员的专属文案统一归 `workspace.delete`：`title` / `description` 用于删除工作空间，`batchRemoveTitle` / `batchRemoveDescription` / `partialRemoveMessage` 用于按记录批量移除成员；成员单项移除标题复用 `system.member.removeTitle`。
成员列表的姓名、用户名和角色标签复用 `user`，添加成员的角色选择占位及校验复用 `user.role`；通用操作及结果提示复用 `common`。
批量移除确认的完整说明使用 `workspace.delete.batchRemoveDescription`，通过 `{memberCount}` 和 `{recordCount}` 展示成员人数与记录数；句中标点随语言维护，成员人数仍按用户 ID 去重，关系记录沿用原有计数方式。
搜索字段在 computed 中翻译；工作空间名称、成员姓名和角色名称按接口原文显示，不将实际名称替换为默认工作空间译文。

系统用户组和对话用户组的业务文案统一使用 `system/user-group.json`，命名空间为 `userGroup`。系统用户组菜单、列表标题及各用户表单中的“用户组”标签共用 `userGroup.title`；明确显示“对话用户组”的菜单、列表标题及表头共用 `system/index.json` 中的 `system.menu.chatUserGroup`。选择占位、必填提示和设置入口分别使用 `userGroup.placeholder`、`requiredMessage`、`set`，实际用户组名称保留接口原文。
创建／重命名标题及名称字段共用 `userGroup`，删除用户组与移除成员的说明统一归 `userGroup.delete`：确认标题共用 `title`，系统用户组的删除说明使用 `description`，对话用户组使用 `chatDescription`；移除成员时的继承权限回收说明共用 `removeDescription`。成员单项／批量移除标题复用 `system.member.removeTitle` / `batchRemoveTitle`，批量标题按实际人数处理单复数。
成员列表的姓名、用户名、角色和来源标签复用 `user`，登录方式品牌名称复用 `auth.methods`。搜索和来源选项在 computed 中翻译，保留协议值、顺序及筛选状态，未知来源和接口返回的名称展示原文。
系统用户组添加成员弹窗的“用户名/姓名”标签由 `user.username.label` 与 `user.name.label` 通过 `/` 组合，完整选择提示使用 `user.placeholder`，必填提示复用 `system.member.requiredMessage`；对话用户组添加成员弹窗的标签与必填提示分别使用 `chatUser.title`、`chatUser.requiredMessage`，选择占位同样复用 `user.placeholder`。添加成员标题均使用 `system.member.add`；成员选项姓名保留接口原文，远程搜索和已选用户缓存沿用原有流程。
通用操作及结果提示复用 `common`；名称校验保留必填、空白检查和长度限制，语言切换不主动触发校验。

角色管理使用 `system/role.json`，命名空间为 `role`。菜单与列表共用 `role.title`，创建／重命名标题、角色名称字段、继承角色说明、系统内置标记及删除确认归该业务域；权限配置页签标题使用 `role.permission.title`。
角色类型名称归 `role.types`，列表分组与继承角色选项共用 `ROLE_TYPE_LABELS`，配置中直接调用 `t`；协议值、选项顺序及接口返回的角色名称保持原样。搜索继续匹配实际角色名称，切换语言不重取角色列表或重置选择。
继承角色的通用选择占位复用 `user.role.placeholder`，专属必填提示使用 `role.inheritedRole.requiredMessage`；用户角色分配仍归 `user.role`。表单规则在 computed 中翻译，保留空白检查、必填条件和名称长度限制，使用 `validate-on-rule-change=false`。
权限配置表头归 `role.permission`，保存按钮和成功提示复用 `common`；表格中的分类、模块、操作对象及权限项名称由接口按当前语言返回。切换语言时重新加载权限数据，按权限 ID 保留当前角色未保存的勾选，不因语言变化重建表格；切换角色时重新读取勾选状态。
角色成员列表的用户名与姓名复用 `user`，工作空间标签复用 `workspace.title`，成员入口和单项／批量移除标题复用 `system.member`；批量移除标题按实际选择数量处理单复数，单项与批量结果共用 `common.messages.removeSuccess`。搜索字段在 computed 中翻译，保留筛选协议值。
添加角色成员的工作空间选择占位与必填提示复用 `user.workspace`，其余按钮和结果提示复用 `common`；成员及工作空间名称展示接口原文。保留版本与角色类型对应的工作空间显示条件、提交值及原有校验规则，语言切换不重置表单或重新加载选项。

系统资源授权入口和资源权限配置标题归 `authorization.resource`，“按用户组／按用户”页签复用 `authorization.byGroup` / `byUser`，提交成功提示复用 `common.messages.submitSuccess`。四类资源的菜单与页签共用各业务的 `title`，功能本地 `RESOURCE_AUTHORIZATION_LABELS` 维护协议值到响应式标题的映射，配置中直接调用 `t`。
共享资源授权抽屉复用同一套标题和页签，生效资源及当前资源／包含子文件夹选项归 `authorization.resource.scope`；权限字段、配置入口、权限选项名称与说明归 `authorization.permission`。`RESOURCE_PERMISSION_OPTIONS` 维护协议值、响应式 `label` 和可选的 `description`，配置中直接调用 `t`，抽屉与系统授权页面读取文案，不维护第二套中文选项。
授权列表及用户组成员抽屉的用户字段复用 `user`，用户组标签和成员数复用 `userGroup.title` / `memberCount`；登录方式品牌名复用 `auth.methods`，来源筛选和表格共用响应式标签。通用按钮及结果提示复用 `common`。
授权对象、资源和工作空间名称保留接口原文；语言切换不重取授权数据、不切换分类或授权对象，保留未提交的权限编辑状态。

System 共享知识库、模型、工具的工作空间授权弹窗归 `authorization.workspace`：标题、说明、选择区域标题及白名单／黑名单选项分别使用 `title`、`description`、`select`、`whiteList`、`blackList`。类型标签、全选、清空、取消、保存及操作成功提示复用 `common`；“已选”复用 `common.labels.selected`，直接与冒号及数量组合，不建立数量格式 key。工作空间名称展示接口原文，语言切换保留搜索、名单类型及勾选状态，提交沿用 `WHITE_LIST` / `BLACK_LIST` 协议值与工作空间 ID。

## 首页

`overview.json` 维护工作空间与系统首页的专属文案，按 `resources`、`quickCreate`、`monitoring`、`ranking` 分类。资源名称、发布状态、其他选项、已有创建操作及全部智能体选项复用对应业务域和 `common`，首页资源卡片的“大语言”“向量”保留原有简称并翻译，英文分别为 `LLM`、`Embedding`，不替换为完整模型类型名。
`HomeStatistics` 与智能体概览共用 `overview.monitoring`，统计卡片、图例及提示使用同一组译文，`Tokens` 保留原文。文案在模板或现有 computed 中直接调用 `t()`，不增加翻译辅助函数；系统首页“全部工作空间”选项复用 `workspace.all`，与快捷创建的默认模型供应商一起响应当前语言，接口返回的资源／空间名称保持原文。切换语言不重新请求统计、不清空筛选，也不改变统计口径或导航权限。

首页排行标题、排行类型、表头及数量说明归 `overview.ranking`，对话次数和活跃用户标签复用 `overview.monitoring`；详情与导出操作复用 `common`。卡片与详情抽屉共用排行类型名称，`TOP5` 固定显示，资源名称和用户名保留接口原文；均 Tokens/轮与人均对话轮次保持各自原有名称和统计口径。导出沿用现有接口，不新增成功提示、语言监听或翻译辅助函数。

智能体概览的 Web／后端 API 访问、链接重置确认及嵌入第三方、访问限制、显示设置入口归 `application/overview.json` 的 `application.overview`，与根目录的通用概览语言包区分。基本信息、复制、重新生成、已复制及启停状态复用 `common`，去对话复用 `application.actions.chat`；链接、访问凭证与接口流程保持原样。用户排行与首页共用 `overview.ranking`，用户对话排行标题使用 `userConversations`，表头“均 Tokens/次”使用 `tokensPerChat`，与首页“均 Tokens/轮”分别保留。排行选项在现有展示配置中直接调用 `t()`，切换语言不重取数据或重置筛选。

嵌入第三方弹窗复用入口的 `application.overview.embed.title`，全屏／浮窗／移动端模式与复制说明归同组；复制操作及“已复制”复用 `common`。模式选项在现有展示配置中直接调用 `t()`，生成的 iframe／script、URL 参数、HTML 转义及模式切换逻辑保持原样。

访问限制抽屉的客户端提问限制、身份认证说明、嵌入白名单及原有整数范围校验归 `application.overview.accessRestriction`；登录方式、默认登录方式、验证码和锁定账号文案复用 `auth.loginSettings`，分钟单位与保存结果复用 `common`。规则在现有 computed 中直接调用 `t()`，使用 `validate-on-rule-change=false`，不新增语言监听；数值范围、认证选项查询、授权条件、白名单按行解析及保存字段保持原样。白名单示例 URL 保留在使用处，不进入语言包。

显示设置的社区版、商业版及预览共用 `application.overview.display`，语言选项直接使用 `LOCALE_OPTIONS`；设置结果复用 `common.messages.settingsSuccess`。图片格式提示复用 `upload.avatar.formatMessage`，图片大小提示保留原“图片”用词；尺寸与大小通过插值传入，图片字段和开关选项使用响应式展示配置直接调用 `t()`。默认免责声明在 `APPLICATION_DISPLAY_SETTING_DEFAULT` 中按当前语言提供，初始化或恢复默认时深拷贝为普通草稿；接口回填的免责声明和用户编辑内容不随界面语言重写。预览缺省智能体名称复用 `overview.ranking.applicationName`，不改变图片生命周期、草稿保存协议或功能开关。

## 知识库详情

`knowledge/index.json` 维护列表、知识库类型、创建、共用文案及尚未独立分文件的业务文案。仅有菜单名称、尚未形成独立业务分组的功能集中在 `knowledge.menu`，按菜单显示顺序排列，使用 `knowledge.menu.<名称>`。
问题管理表头的“最近一次召回时间”使用 `knowledge.question.lastRetrievedAt`，其他位置的“最后一次召回时间”继续使用 `knowledge.stats.lastRetrievedAt`。
`tag.json` 维护标签管理与文档标签设置，使用 `knowledge.tags`。`document.json` 维护文档列表、上传与预览，使用 `knowledge.document`；图片列表、上传、详情及校验文案同文件存放，使用与 `document` 平级的 `image` 分组，引用为 `knowledge.image`。`paragraph.json` 维护分段字段、校验、关联问题、列表操作及删除确认，使用 `knowledge.paragraph`；分段列表与导入预览共用 `knowledge.paragraph.empty`，数量单位复用 `knowledge.stats`。`settings.json` 维护基础设置与文档处理策略；`sync.json` 按 `sync`、`scheduledSync`、`syncLog` 的顺序维护同步方式、定时同步与同步日志。生成问题弹窗文案归 `index.json` 中的 `generateQuestions` 分组。
基础设置标题、上传限制和更换向量模型确认归 `knowledge.baseSettings`，四种资源范围的基础设置路由共用 `knowledge.baseSettings.title`；类型名称与说明复用知识库类型分组，Web 字段复用 `knowledge.fields`，飞书凭据的固定字段名使用通用输入占位与校验。文档策略的同步生效说明归 `knowledge.documentStrategy.syncHint`。
同步入口、同步方式与共用提示归 `knowledge.sync`，`label` 用于“同步”按钮及任务标签，`title` 用于“同步知识库”弹窗；定时同步字段、开关说明和业务校验归 `knowledge.scheduledSync`，菜单共用其 `title`；日志表头和已知跳过原因归 `knowledge.syncLog`，同步专属状态与结果计数标签共用 `knowledge.syncLog.status`，均在 `knowledge/sync.json` 维护，成功／失败状态及失败计数标签复用 `common.status`。统计按“文档: 数量 (已同步: 数量, …)”组合，各语言保持顺序和格式一致；接口返回的未知原因与错误详情保留原文。
标签导入标题、模板和格式限制归 `knowledge.tags.import`，关联文档标题及页签归 `knowledge.tags.documents`；文档字段复用 `knowledge.document`，通用关联操作及结果提示复用 `common`，文件选择校验复用 `upload`。
问题列表、创建、详情及问题与分段的关联文案归 `knowledge.question`，在 `knowledge/question.json` 维护；四种资源范围的菜单与列表共用 `title`，详情抽屉标题使用 `detailTitle`。输入占位、多行输入说明和长度校验归 `content`，关联分段入口、数量标签及无关联分段时的空状态归 `paragraphs`，创建按钮和弹窗共用 `actions.create`。关联弹窗的文档／图片页签和分段详情复用各自业务域；召回统计及字符单位复用 `knowledge.stats`，时间、通用操作、记录切换及成功提示复用 `common`。
自定义分词的标题、用途说明、词语字段及创建入口归 `knowledge.termbase`，在 `knowledge/termbase.json` 维护；英文沿用 v2 的 `term` 用词，标题为 `Custom term`，创建入口为 `Create term`。四种资源范围的菜单与列表共用 `title`，创建按钮和弹窗共用 `actions.create`。词语标签、单行与多行输入占位归 `content`；时间、通用操作及创建／删除／导出成功提示复用 `common`。词语内容和导出文件名保持原值。
检索参数、模式名称及说明归 `knowledge.retrieval`；召回测试标题、输入、结果及空状态归 `knowledge.hitTest`，两组在 `knowledge/retrieval.json` 维护。召回测试菜单与页面共用 `knowledge.hitTest.title`。召回测试、智能体设置与工作流知识库检索节点共用 `KNOWLEDGE_SEARCH_MODE_OPTIONS`，直接读取响应式 `label` / `description`，提交仍使用协议值。图片上传限制、格式标签、校验及失败状态复用 `upload`，结果分段详情标题复用 `knowledge.paragraph.detailTitle`；查询内容与接口返回的分段、文档名称保留原文。
翻译按业务含义归属，不与页面目录一一对应：分段字段和操作归 `knowledge.paragraph`，文档字段、操作及流程说明归 `knowledge.document`，页面可交叉引用。
对话用户授权属于跨资源业务，自动授权、已授权及授权操作复用 `authorization.autoAuthorization`、`authorization.authorized`、`authorization.authorize`；智能体的工作空间／系统资源管理菜单与知识库四种资源范围的菜单共用 `chatUser.title`，用户组分组标题复用 `authorization.byGroup`。姓名、用户名和用户来源标签复用 `user.name.label`、`user.username.label`、`user.source.label`，本地创建来源复用 `chatUser.source.local`；保存按钮和成功提示复用 `common`，钉钉、飞书和企业微信名称复用 `auth.methods`。搜索与来源标签在 computed 中直接调用 `t`，筛选与表格共用同一组标签，不新增格式化翻译函数；保留 OAuth2 来源的兼容值和未知来源原文。用户名和用户组名称保留原文，筛选与授权请求使用原协议值；切换语言不重取用户列表或清空未保存的授权勾选。已授权人数在模板中按“已授权 数量”组合，不建立数量格式翻译键。
外部检索服务的标题、开关及说明、API 调用示例标签和加载失败提示归 `knowledge.externalRetrieval`，在 `knowledge/retrieval.json` 维护；四种资源范围的菜单共用 `title`。MCP 配置标题复用 `resource.mcpConfig.title`，重新加载、保存和复制成功提示复用 `common`。接口返回的 API 示例及 MCP 配置保持原文，只按既有规则对齐访问地址；调用复制工具时传入当前语言的成功提示。
导入预览与分段列表的单个删除共用 `knowledge.paragraph.delete.title`，使用分段标题，无标题时沿用 `-` 占位；继续导入前的编辑未完成提示保留在 `knowledge.document.preview`。文档与图片的删除确认及影响说明分别归 `knowledge.document.delete`、`knowledge.image.delete`，共用删除组件通过 `resourceType` 选择文案。
跨对象共用的召回次数、最后一次召回时间归 `knowledge.stats.retrievalCount` / `lastRetrievedAt`，文档列表和分段预览共用。
文档、图片与分段的迁移入口共用 `knowledge.actions.migrate` / `migrateTo`，成功提示共用 `knowledge.messages.migrateSuccess`。迁移目标知识库使用 `knowledge.fields.targetKnowledge`，目标文档使用 `knowledge.document.targetDocument`，占位与必填提示分别维护。分段位置菜单归 `knowledge.paragraph.position`；新增、保存和移动成功提示复用 `common.messages`。
四种资源范围的详情菜单和页面标题共用路由中的翻译 key：已整理的业务引用所属分组的 `title`，例如 `knowledge.document.title`、`knowledge.tags.title` 和 `knowledge.documentStrategy.title`；仅有菜单名称的功能引用 `knowledge.menu`，不重复定义标题。“设置”复用 `common.labels.settings`。
文档列表的文件状态标题、专属处理阶段和进度归 `knowledge.document.status`，通用状态复用 `common.status`；召回处理选项归 `knowledge.document.hitHandling`。筛选项和行内展示共用译文，接口接收原有状态、任务类型和召回处理值。
图片菜单与页面标题共用 `knowledge.image.title`。图片处理配置复用 `knowledge.documentStrategy`，上传限制、格式说明和上传校验复用 `upload`；文档状态、召回处理及共用文档操作继续引用 `knowledge.document`，统计字段引用 `knowledge.stats`。接口返回的图片名称、标签、模型和工具名称保留原文。
工作流文档导入的操作归 `knowledge.document.import`。导入与调试共用的数据源选择文案和文件查询不支持提示归 `resource.dataSource`，执行结果文案归 `common/execution.json` 中的 `execution.result`；默认用户输入标题使用 `workflow/index.json` 中的 `workflow.userInput`，执行中和已取消复用 `common.status`。

## 文件夹

`folder.json` 的 actions 维护创建文件夹、创建子文件夹、编辑文件夹等操作。将文件夹或资源移动到目标文件夹时，菜单、批量操作和弹窗标题统一使用 `folder.actions.moveTo`。
sort 维护目录树排序选项，
delete 维护删除确认。名称与描述的表单提示、通用按钮、字段标签、搜索占位和成功提示复用 common，
资源授权入口复用 authorization.resource.title。目录树与列表标题复用 application、knowledge 或 tool 的 categories.all / shared，
每个分类名称按完整短语翻译；用户创建的文件夹名称和描述按原值展示。

## 动态表单

`common/dynamic-form.json` 挂载为 `dynamicForm`，维护配置器基本信息、控件类型、选项配置、显隐条件、
固定帮助文案，以及运行时控件的缺省提示；通用操作、结果提示和对话框标题复用 common。
同一字段的标签、占位和校验集中到 fields；通用占位提示复用 common.placeholders，
缺省必填提示根据实际控件使用 common.validation 中带字段名的输入或选择提示。
参数标识与显示名称分别使用 `dynamicForm.fields.parameter`、`dynamicForm.fields.displayName`；表单数据仍使用原有的 `field`、`label` 属性。
显隐条件的比较值也按输入框或选择框区分提示，占位与校验分别定义 key。模型类型复用 model.fields.type；
模型参数表的参数、显示名称、组件类型和默认值复用 dynamicForm.fields。控件类型使用 types，
条件比较方式使用 operators，上传与树形配置的专属文案分别使用 upload、tree；仍遵守四层上限。
树形选项删除确认使用 `dynamicForm.tree.delete.title`，名称使用选项的显示标签。
控件类型定义统一来自 DYNAMIC_FORM_TYPES，label 在响应式配置中直接调用 t；下拉选项响应式生成，
表格按 value 查找显示文案。控件类型协议值与比较符枚举不翻译，不把当前语言保存到配置。
用户输入、接口字段说明、选项标签及已有序列化规则原样保留；配置器 getData() 继续输出原协议，
不将当前语言写入配置。未接入的共享组件和 Demo 保留原文，后续变更遵循接入范围约束。
