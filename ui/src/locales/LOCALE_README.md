# 国际化规则

`src/locales` 负责界面语言、语言包和入口初始化。当前支持 `zh-CN`、`en-US` 与 `zh-Hant`，
默认及缺失文案回退为简体中文。语言包暂随入口加载，新增语言时再评估按需加载。

## 分类

按“业务域 → 对象或场景 → 文案用途”组织；文件按业务域划分，不对应组件目录。
各语言使用相同的业务文件或目录结构。

| 业务域      | 内容                                             |
| ----------- | ------------------------------------------------ |
| common      | 无业务含义的操作、基础校验、界面偏好和通用错误页 |
| upload      | 文件选择、上传提示、校验、状态、后缀与头像上传   |
| auth        | 登录、退出、找回密码、身份认证                   |
| application | 智能体创建、配置、发布、版本                     |
| knowledge   | 知识库、文档、分段、问题、标签、检索             |
| model       | 模型、供应商、模型参数与连接测试                 |
| dynamicForm | 动态表单控件类型及配置器的固定界面文案           |
| resource    | 跨资源授权、关联关系及共享状态等公共业务         |
| folder      | 文件夹操作、排序、表单提示和删除确认             |
| tool        | 工具、MCP、Skill 管理                            |
| trigger     | 触发器、定时与事件配置、执行任务                 |
| workflow    | 画布、节点、变量、调试与执行展示                 |
| chat        | 对话输入、消息操作、历史会话与对话状态           |
| workspace   | 工作空间、成员、空间级设置                       |
| system      | 用户、角色、系统配置、许可证                     |

翻译 key 最多四层，包含业务域命名空间。业务域内部的共用字段使用 `<业务域>.fields.<字段>.<用途>`，
场景专属字段使用 `<业务域>.<场景>.<字段>.<用途>`；不同时叠加场景、fields 和 validation。
字段文案使用 label、placeholder、description，以及同级的 requiredMessage、invalidMessage、
lengthMessage、mismatchMessage 等校验提示，不再建立字段内的 validation 层。
placeholder 与 requiredMessage 用途独立，即使当前文案相同也分别定义，不互相替代或复用。
无法归属字段的校验可以使用 `<业务域>.<场景>.validation.<规则>`。
操作、结果提示等按需使用 actions、messages、dialogs、states、options、empty，仍遵守四层上限。

auth.fields 维护共用的用户名、密码、验证码、邮箱和确认密码；captcha.label 仅用于图片验证码
替代文本。找回密码专属的长度提示使用 auth.forgotPassword.password.lengthMessage，
确认密码匹配提示使用 auth.fields.confirmPassword.mismatchMessage。不改变各页面已有校验条件。

归属以业务含义判断：知识库检索模式归 knowledge，知识库检索节点归 workflow。
系统资源管理复用原业务域，不复制到 system。多处使用不等于通用；相同中文但业务语义
不同可以使用不同 key。通用添加、编辑、删除、取消、保存和上传文件操作归 common.actions，
仅有展示文案的通用标签归 common.labels，例如“创建者”和“操作”。名称与描述直接归 common.name 和 common.description，
字段的 label、placeholder 和实际使用的 requiredMessage 放在一起，表单、表头和筛选器共用 label。
`common.status` 维护状态标签 `label`、通用启停选项 `enabled` / `disabled`，以及排队、执行、成功、失败、取消中和已取消等通用状态。
文档、同步日志和执行记录复用这些状态文案；索引中、生成中、同步中、触发失败等专属文案保留在所属业务。
“执行成功／执行失败”等完整结果提示保留业务含义，不替换为“成功／失败”。
创建时间与更新时间使用 `common.labels.createTime` / `updateTime`，英文为 `Create time` / `Update time`；卡片中“创建于”的说明使用 `common.labels.createdOn`。
流程步骤的“上一步／下一步”使用 `common.actions.previous` / `next`，记录切换的“上一个／下一个”使用 `common.actions.previousItem` / `nextItem`。
通用日期范围预设及起止日期占位归 `common.dateRange`，音视频播放失败提示归 `common.messages`。
通用周期、星期、间隔单位与 Cron 字段及校验归 `common.schedule`；日期数字、时刻及间隔数值在使用处组合。
通用文件选择、上传提示和校验归 `upload.json`，上传进度和结果汇总归 `upload.status`。
头像设置、图片上传说明及校验归 `upload.avatar`；文件后缀编辑的操作和提示归 `upload.extension`。
业务模板、文件内容要求和导入说明归各自业务域。
“请输入模型名称”等指明业务对象的提示，以及发布状态、任务处理阶段等业务选项归对应业务域。
通用操作结果归 common.messages，通用对话框标题归 common.dialogs；业务专属确认句仍留在所属业务域。
“关联”的英文和翻译 key 统一使用 `relate` 词族：关联操作使用 `Relate` / `relate`，取消关联使用 `Unrelate` / `unrelate`，已关联／未关联标签使用 `Related` / `related`、`Unrelated` / `unrelated`；成功提示使用 `Related successfully` / `Unrelated successfully`，对应 key 为 `relateSuccess` / `unrelateSuccess`。文件名保持不变；网页链接仍使用 `link`。
用户内容、用户保存的提示词、协议枚举和已保存节点名称保留原文。

## JSON 键顺序

- 同一语言包的键按含义分组，简体、繁体和英文采用相同的排列顺序，方便逐项对照。
- `common.json` 的顶层顺序为 `labels` → `name` → `description` → `status` → `dateRange` → `schedule` → `parameters` → `actions` → `dialogs` → `messages` → `placeholders` → `validation` → `empty`。
- 字段内先放 `label`，再放 `placeholder`，最后放 `requiredMessage` 等校验提示。状态组先放 `label`，再放 `enabled`、`disabled`。其他组沿用现有顺序。

## 使用约定

- key 使用表达业务含义的英文 camelCase，不使用中文、数字序号或 misc 等模糊分类。
- Vite 自动收集语言目录下的 JSON。单文件业务使用文件名作为命名空间，如 `dynamic-form.json` 对应 `dynamicForm`。分文件的业务使用第一级目录名，如 `knowledge/document.json` 归入 `knowledge`。分文件直接写各自负责的业务字段，同一业务的顶层字段只在一个文件中定义。
- 纯标签、数量单位、固定比例、编号和倒计时只翻译文字，数字、名称及固定格式在使用处组合；
  问号、作为分隔符的冒号不单独翻译，三种语言使用相同的显示格式。只有文件名和错误原因等数据的组合不建立翻译键。
  例如“已选 3/10”只翻译“已选”；单项确认标题翻译操作文字，使用处追加 `: 名称?`。
- 数量限制、校验说明等完整句子整体翻译，必要的动态内容保留命名参数；不机械拆散语句。
  单复数按实际数量选择，展示的数字仍可由模板直接输出。代码示例和提示词协议中的花括号保留原有语义。
- 英文界面采用简洁、明确的表达。通用输入、选择占位分别使用 Please enter、Please select，
  不使用省略号；明确对象时使用 Enter a model name、Select a model 等完整短语，不统一添加 Please。
  无具体对象的通用必填校验使用 This field is required；具体字段校验仍优先写明对象。
  按钮使用 Save 等动作词，成功提示使用 Saved successfully。短标签和占位提示使用句首大写，
  通常不加句号；占位与校验仍保留独立 key。
- 组件显式导入 useI18n，并使用全局作用域的 t；不使用自动注入的 $t。
- 每批范围内的界面文案都在使用处直接调用 `t`，包括已有函数中的校验、确认和结果提示。直接替换文案无需单独确认。
  不新增用于处理翻译的辅助函数。遇到无法直接使用 `t` 的场景，先向用户说明原因和方案，确认后再处理该处。
- 依赖语言的选项和校验规则在 computed 或执行时翻译，不在模块初始化时固化翻译结果。
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

## 分批迁移

Admin 登录与找回密码页面支持三语切换，错误页暂不接入翻译。复用的账号与扫码组件同时影响 Chat 登录和
外观预览；平台配置的品牌文案保持原值，第三方扫码界面由 SDK 提供。Element Plus 日期组件及 Markdown 编辑器、预览已接入三语。其余界面、路由标题及业务日期格式
按模块接入，允许过渡期保留原中文。每批完成后等待用户检查，未经确认不扩展下一批。

## 资源选择弹窗

智能体、工具和知识库选择弹窗的标题分别复用 `application.title`、`tool.title` 和 `knowledge.title`。
“已选”复用 `common.labels.selected`，数量直接在模板中展示；清空、取消和确定复用 `common.actions`。
知识库选择中的 Embedding 模型一致性提示归 `knowledge.help.embeddingModelHint`，在 `knowledge/index.json` 维护。
工具弹窗的自定义 `title` 由调用方提供最终展示文字，未传入时直接使用 `t('tool.title')`；文件夹和资源名称保留原有展示规则。

## 模型列表

模型列表分类使用 model.categories，供应商字段使用 model.provider.label / placeholder；
卡片和下载／删除提示使用 model 语言包，操作按钮引用 common，
授权和关联资源入口引用 resource。模型类型协议值不变，constants/model.ts 的 MODEL_TYPE_MESSAGE_KEYS 提供共用翻译 key，
类型名称与说明统一维护在 model.types.<类型>.label / description，保持四层结构。
系统模型页与工作流默认模型设置共用同一类型映射；工作流 LLM 的“AI 模型”场景文案保留。
内置分类标题按 provider 标识响应式翻译，不改写接口供应商名称。
供应商选择、模型创建与编辑抽屉、高级参数表及独立参数设置抽屉已接入三语。
高级参数表的控件类型名称读取 dynamic-form.json，加载到 dynamicForm 命名空间，
不改写接口字段描述或已保存的参数配置。切换语言不重取接口、不重新初始化表单，
也不主动校验；模型创建与编辑通过透传 validate-on-rule-change=false 禁止规则变化自动校验。
参数表中的参数、显示名称、组件类型、默认值和必填列复用 dynamicForm.fields；动态表单中的模型类型
复用 model.fields.type 及模型类型翻译映射。系统资源管理与系统共享资源的模型页固定文案同样复用
model、common、resource，工作空间名称字段标签使用 workspace.title。工作空间模型、系统资源模型、
系统共享模型和系统模型授权路由标题复用 model.title；侧栏菜单随当前语言更新，其他业务路由仍按批次处理。
MkResourceCard、MkComplexSearch、MkEmpty 的默认创建信息、占位和空状态文案使用 common；
自定义属性、插槽及接口返回内容保持原值。授权、关联资源、工作空间授权弹窗及表头筛选器的内部文案
仍按各自共享组件批次处理。

## 工具列表

工作空间、系统资源管理和系统共享资源的工具菜单，以及普通工具类型名称共用 `tool.title`。列表标题“工具”使用 `tool.title`，“全部工具”使用 `tool.categories.all`。
Skill、工作流、MCP 和数据源的类型名称使用各自分组的 `label`，与表单文案一起维护在 `tool.json` 中。
内置目录用 tool.categories，按文件夹 ID 选择译文。自建文件夹名称、工具名称和描述直接展示接口值，类型筛选和请求使用原协议值。
工具列表和输入参数共用 `tool.source.label`、`tool.source.custom`。工具列表的“工具商店”复用 `tool.store.title`，输入参数的“引用参数”使用 `tool.source.reference`。
启停、删除和版本更新的工具专属提示归 tool；通用操作、启停状态和操作结果归 common。
资源共享标签、MCP 服务配置及执行记录入口归 resource，触发器入口复用 `trigger.title`。
工具商店的内置分类、搜索结果计数和应用工具文案归 `tool.store`。工具名称的专属占位和校验归 `tool.fields.name`。
商店自定义分类、工具名称、描述和 README 使用接口原文。
普通工具的创建、编辑、复制标题使用 `tool.createTitle`、`tool.editTitle`、`tool.duplicateTitle`，代码必填提示归 `tool.fields.code`。调试入口、运行状态和缺省错误提示归 `tool.debug`。
调试参数的占位与必填提示分别使用 `common.placeholders.inputField` 和 `common.validation.inputFieldRequired`，通过 `{label}` 传入参数名。执行输出和接口错误详情按原文展示。
Skill 表单的标题、名称提示和 ZIP 文件要求归 `tool.skill`。文件大小提示通过 `{size}` 读取校验上限，拖入、选择、更换文件和空文件提示复用 `upload`。
工作流工具的创建、编辑、复制标题及工作流名称提示归 `tool.workflow`。复制工具时在原名称后追加 `common.name.copySuffix`，三语均使用“名称 + 空格 + 副本后缀”。
MCP 工具表单的标题、名称提示、传输方式说明和配置校验归 `tool.mcp`。配置字段复用 `resource.mcpConfig.title`，JSON 示例与用户填写的配置保留原文。
数据源工具的表单标题、名称提示和代码必填提示归 `tool.dataSource`。Python 模板和用户编辑的代码作为表单数据原样提交。
工具表单的启动参数、输入参数、输出参数和 Python 代码区分别归 `tool.initParams`、`tool.inputParams`、`tool.outputParams` 和 `tool.pythonCode`。
工具使用时的可见性说明归 `tool.help`：输入和输出参数共用 `shownWhenUsed`，Python 代码区使用 `hiddenWhenUsed`。输出结果标签使用 `tool.outputParams.result`，固定变量 `{result}` 直接在模板展示。
参数表头及提示说明复用 `dynamicForm.fields`，模型和工具共用 `common.parameters.add`、`common.parameters.edit`。
参数来源只翻译选项标签，`reference`、`custom` 和数据类型沿用协议值。

## 智能体

`application/` 按业务场景拆分语言文件，合并为同一个 `application` 命名空间。`index.json` 维护列表、卡片、类型、创建与复制表单、发布状态及基础操作。
工作空间列表、系统资源管理列表和资源授权分类共用 `application.title`，内置文件夹共用 `application.categories`；自建文件夹、智能体名称和描述展示原值。
`application.simple` / `advanced` 的 `label` 用于创建菜单中的完整类型名称，`shortLabel` 用于筛选与卡片标签，`createTitle` 用于创建弹窗，`description` 用于类型说明；提交仍使用 `APPLICATION_TYPE` 的原协议值。
创建与复制表单在 `application/index.json` 中维护：名称和描述提示归 `application.fields`，描述占位统一使用包含应用场景、用途和示例的完整说明；模板选项归 `application.template`，知识库问答助手的名称与说明归其 `assistant` 分组，复制标题归 `application.duplicate`。字段标签、通用按钮和成功提示复用 `common`；创建副本使用 `common.messages.duplicateSuccess`，复制到剪贴板使用 `common.messages.copied`。
复制名称按“原名称 + 空格 + `common.name.copySuffix`”组合，并根据当前语言后缀的长度保留 64 字符限制。表单中的用户内容、模板中心返回的名称与描述、创建时写入的默认提示词和工作流模板配置保持原值。
发布和门户上架状态归 `application.status`，发布时间归 `application.publishTime`，门户上下架操作及提示归 `application.portal`。名称、创建者、创建时间和通用操作复用 `common`，工作空间列复用 `workspace.title`。
智能体导出入口及 Skills 访问地址提示归 `application.export`，删除确认归 `application.delete`；错误原因、导出文件名和 MCP 配置内容保留原值。
MCP、资源授权、关联资源和模板中心入口复用 `resource`，触发器入口复用 `trigger.title`，文件夹移动入口复用 `folder`；保存、导入、删除、移动、复制和导出失败提示复用 `common`。
对话日志的语言文件为 `application/chat-log.json`，使用 `application.chatLog`。工作空间和系统资源管理的日志路由与页面共用 `title`；表头归 `labels`，用户反馈筛选归 `feedback`，来源标签与选项归 `source`。来源通过常量维护协议值到翻译 key 的映射，在展示时统一调用 `t`，Slack 在三语中均保留品牌名；未知来源保留接口原值。
单个和批量清除策略共用 `cleanStrategy`，标题使用 `title`，天数输入框前后的说明分别使用对应的 `Prefix` / `Suffix`，保留原交互顺序并按天数处理英文单复数。添加到知识库的按钮和弹窗共用 `addKnowledge.title`，知识库与目标文档字段复用 `knowledge.fields.targetKnowledge` / `knowledge.document.target`。通用操作、成功提示和详情翻页复用 `common`；摘要、用户名、知识库与文档名称展示原值。
发布渠道使用 `application/access.json` 中的 `access` 分组，两种资源范围的菜单共用 `application.access.title`；渠道名称与说明分别归各渠道的 `label` / `description`，配置入口归 `actions`，未配置状态归 `states`，抽屉标题使用 `configurationTitle`。卡片和抽屉通过已有渠道标识 `platform.key` 统一调用 `t`，Slack 同样使用 `label`，三语文案均为品牌名；功能本地 `platforms.ts` 维护平台标识、图标、配置字段与后台链接，不重复维护渠道名称和说明。
连接方式及共用说明归 `access.connection`，回调地址与填写引导归 `access.callback`，平台后台名称归 `access.consoles`；特定渠道的字段名、连接说明、认证状态和后台路径指引归对应渠道分组。固定英文参数名称直接使用 `label`，需要翻译的字段只提供 `labelKey`；抽屉在现有 computed 中通过 `t` 生成显示标签。连接选项使用 `labelKey` / `tipKey`，保留原有的 `ws`、`stream`、`callback` 协议值。输入占位与必填提示分别复用 `common.placeholders.inputField` / `common.validation.inputFieldRequired`，语言切换不主动触发表单校验。平台协议值、配置字段名、默认连接方式、必填条件、回调地址与外部链接保持原值；启停、保存和复制成功提示复用 `common.messages`。

## 触发器

`trigger.json` 维护触发器业务，管理列表、工作空间和系统资源管理中的智能体／工具入口及资源触发器弹窗共用 `trigger.title`。
定时与事件类型分别归 `scheduled` / `event`，名称使用 `label`；任务、下次执行时间等展示标签归 `labels`，删除确认与影响说明归 `delete`。
名称、描述、创建信息、启停状态、通用操作和成功提示复用 `common`；任务分组名称复用 `application.title` / `tool.title`，执行记录入口复用 `resource.executionRecords.title`。
资源触发器的周期摘要复用 `common.schedule`，只翻译周期、星期和单位，日期数字、时刻和间隔值在使用处组合；Cron 表达式、触发器名称和描述保持原值。
类型和状态选项响应当前语言，筛选与启停请求仍使用原有协议值；已有周期摘要函数在执行时直接调用 `t`。
创建／编辑标题使用 `createTitle` / `editTitle`，名称字段归 `fields.name`；触发周期归 `scheduled.period`，事件地址与令牌校验归 `event`。
请求参数的标题、名称、数据类型及校验归 `requestParameters`，参数与必填表头复用 `dynamicForm.fields`；任务执行标签和必选提示归 `taskExecution`，内置问题、文件类型及参数来源归 `taskParameters`。
周期级联选项在 computed 中翻译 `SCHEDULE_OPTION` 的 `labelKey`，不改写共享常量；Cron 字段与校验复用 `common.schedule.cron`。输入占位与必填提示分别使用 `common.placeholders.inputField` / `common.validation.inputFieldRequired`。
任务参数只翻译内置展示标签；用户定义的参数名、`body` 路径、数据类型、引用来源值和默认值保持原样。语言切换不初始化任务参数，不自动触发表单校验。
执行记录与详情标题、资源类型、执行时间、错误信息归 `resource.executionRecords`，触发失败使用 `resource.executionRecords.status.triggerFailed`；触发任务和触发器入参归 `trigger.executionRecords`。
触发器、工具和知识库工作流执行记录的状态筛选与展示通过 `EXECUTION_STATUS_OPTIONS` 的 `labelKey` 调用 `t`，通用状态复用 `common.status`；名称、状态表头、耗时、操作和记录翻页复用 `common`，资源类型名称复用 `application.title` / `tool.title`。
查询、排序和跨页浏览使用原协议值，未知状态及接口返回的任务名称、入参和错误内容保留原文；节点内部详情文案随工作流节点批次接入。

## 知识库列表

英文界面将“知识库”统一译为 `knowledge`，独立标题写作 `Knowledge`，例如“全部知识库”为 `All knowledge`。
“分段”的英文统一使用 `segment` / `segments`，按语境使用单复数和句首大写；文件名、翻译 key 及代码字段继续沿用 `paragraph`。用于向量检索的“子块”使用 `child chunk`，与完整分段区分。
工作空间、系统资源管理和系统共享资源的知识库菜单与列表标题共用 `knowledge.title`。四类知识库分别归 `knowledge.base`、`knowledge.web`、`knowledge.lark` 和 `knowledge.workflow`。类型筛选、类型列和创建菜单共用各组的 `label`，菜单说明使用 `description`，创建弹窗标题使用 `createTitle`。筛选请求沿用数字类型值。
卡片的文档数、字符数和图片数使用 `knowledge.stats`，按实际数量选择单复数。向量化和分词索引归 `knowledge.actions`；同步入口使用 `knowledge.sync.label`。
跨资源的模板中心文案归 `resource.templateStore`。模板名称、描述和 README 展示接口原文；缺少说明时与工具商店共用 `common.empty.noDetails`。
手动同步、定时同步及日志共用 `knowledge.sync` 中的同步方式。向量化和生成问题共用的分段范围在 `knowledge/index.json` 中维护，使用 `knowledge.paragraphScope`。生成问题入口、弹窗字段、校验和内置默认提示词归 `knowledge.generateQuestions`；按钮、任务标签与弹窗标题共用 `title`，取消生成使用 `cancel`，均在 `knowledge/generate-questions.json` 维护。无已保存配置时按打开弹窗时的语言填入默认提示词，保留 `{data}` 与 `<question></question>`。提交时使用编辑框中的原文。
导出格式与源文件说明归 `knowledge.export`，单个及批量删除的确认标题归 `knowledge.delete`。
Web 创建的根地址与选择器归 `knowledge.fields`。创建、文档上传、导入和设置共用的分段规则、图片处理与索引增强文案归 `knowledge.documentStrategy`。
分段标识的文字选项归 `knowledge.documentStrategy.splitPatterns`，在 `knowledge/settings.json` 中维护。文档策略表单与工作流分段节点在展示时翻译 `DOCUMENT_SPLIT_PATTERN_OPTIONS` 的 `labelKey`；纯符号、Agent 参数识别用的 `label` 及正则 `value` 保留原值。

## 知识库详情

`knowledge/index.json` 维护列表、知识库类型、创建、共用文案及尚未独立分文件的业务文案。仅有菜单名称、尚未形成独立业务分组的功能集中在 `knowledge.menu`，按菜单显示顺序排列，使用 `knowledge.menu.<名称>`。
`tag.json` 维护标签管理与文档标签设置，使用 `knowledge.tags`。`document.json` 维护文档列表、上传与预览，使用 `knowledge.document`；图片列表、上传、详情及校验文案同文件存放，使用与 `document` 平级的 `image` 分组，引用为 `knowledge.image`。`paragraph.json` 维护分段字段、校验、关联问题、列表操作及删除确认，使用 `knowledge.paragraph`；分段列表与导入预览共用 `knowledge.paragraph.empty`，数量单位复用 `knowledge.stats`。`settings.json` 维护基础设置与文档处理策略；`sync.json` 按 `sync`、`scheduledSync`、`syncLog` 的顺序维护同步方式、定时同步与同步日志。生成问题弹窗归 `generate-questions.json`。
基础设置标题、上传限制和更换向量模型确认归 `knowledge.baseSettings`，四种资源范围的基础设置路由共用 `knowledge.baseSettings.title`；类型名称与说明复用知识库类型分组，Web 字段复用 `knowledge.fields`，飞书凭据的固定字段名使用通用输入占位与校验。文档策略的同步生效说明归 `knowledge.documentStrategy.syncHint`。
同步入口、同步方式与共用提示归 `knowledge.sync`，`label` 用于“同步”按钮及任务标签，`title` 用于“同步知识库”弹窗；定时同步字段、开关说明和业务校验归 `knowledge.scheduledSync`，菜单共用其 `title`；日志表头和已知跳过原因归 `knowledge.syncLog`，同步专属状态与结果计数标签共用 `knowledge.syncLog.status`，均在 `knowledge/sync.json` 维护，成功／失败状态及失败计数标签复用 `common.status`。统计按“文档: 数量 (已同步: 数量, …)”组合，各语言保持顺序和格式一致；接口返回的未知原因与错误详情保留原文。
标签导入标题、模板和格式限制归 `knowledge.tags.import`，关联文档标题及页签归 `knowledge.tags.documents`；文档字段复用 `knowledge.document`，通用关联操作及结果提示复用 `common`，文件选择校验复用 `upload`。
问题列表、创建、详情及问题与分段的关联文案归 `knowledge.question`，在 `knowledge/question.json` 维护；四种资源范围的菜单与列表共用 `title`，详情抽屉标题使用 `detailTitle`。输入占位、多行输入说明和长度校验归 `content`，关联分段入口、数量标签及无关联分段时的空状态归 `paragraphs`，创建按钮和弹窗共用 `actions.create`。关联弹窗的文档／图片页签和分段详情复用各自业务域；召回统计及字符单位复用 `knowledge.stats`，时间、通用操作、记录切换及成功提示复用 `common`。
自定义分词的标题、用途说明、词语字段及创建入口归 `knowledge.termbase`，在 `knowledge/termbase.json` 维护；英文沿用 v2 的 `term` 用词，标题为 `Custom term`，创建入口为 `Create term`。四种资源范围的菜单与列表共用 `title`，创建按钮和弹窗共用 `actions.create`。词语标签、单行与多行输入占位归 `content`；时间、通用操作及创建／删除／导出成功提示复用 `common`。词语内容和导出文件名保持原值。
检索参数、模式名称及说明归 `knowledge.retrieval`；召回测试标题、输入、结果及空状态归 `knowledge.hitTest`，两组在 `knowledge/retrieval.json` 维护。召回测试菜单与页面共用 `knowledge.hitTest.title`。召回测试、智能体设置与工作流知识库检索节点共用 `KNOWLEDGE_SEARCH_MODE_OPTIONS`，在模板或 computed 中直接通过 `t` 翻译 `labelKey` / `descriptionKey`，提交仍使用协议值。图片上传限制、格式标签、校验及失败状态复用 `upload`，结果分段详情标题复用 `knowledge.paragraph.detailTitle`；查询内容与接口返回的分段、文档名称保留原文。
翻译按业务含义归属，不与页面目录一一对应：分段字段和操作归 `knowledge.paragraph`，文档字段、操作及流程说明归 `knowledge.document`，页面可交叉引用。
对话用户授权属于跨资源业务，标题、用户组分组、用户字段、来源标签及授权状态归 `resource.chatUserAuthorization`。智能体的工作空间／系统资源管理菜单与知识库四种资源范围的菜单共用其 `title`；保存按钮和成功提示复用 `common`，钉钉、飞书和企业微信名称复用 `auth.login.options`。搜索与来源筛选的选项在 computed 中生成；用户名、用户组名称和未知来源保留原文，筛选与授权请求使用原协议值。已授权人数在模板中按“已授权 数量”组合，不建立数量格式翻译键。
外部检索服务的标题、开关及说明、API 调用示例标签和加载失败提示归 `knowledge.externalRetrieval`，在 `knowledge/retrieval.json` 维护；四种资源范围的菜单共用 `title`。MCP 配置标题复用 `resource.mcpConfig.title`，重新加载、保存和复制成功提示复用 `common`。接口返回的 API 示例及 MCP 配置保持原文，只按既有规则对齐访问地址；调用复制工具时传入当前语言的成功提示。
导入预览删除分段使用 `knowledge.paragraph.delete.confirm`；继续导入前的编辑未完成提示保留在 `knowledge.document.preview`。文档召回处理和删除文档的影响说明仍归 `knowledge.document`。
跨对象共用的召回次数、最后一次召回时间归 `knowledge.stats.retrievalCount` / `lastRetrievedAt`，文档列表和分段预览共用。
文档、图片与分段的迁移入口共用 `knowledge.actions.migrate` / `migrateTo`，成功提示共用 `knowledge.messages.migrateSuccess`。迁移目标知识库使用 `knowledge.fields.targetKnowledge`，目标文档使用 `knowledge.document.target`，占位与必填提示分别维护。分段位置菜单归 `knowledge.paragraph.position`；新增、保存和移动成功提示复用 `common.messages`。
四种资源范围的详情菜单和页面标题共用路由中的翻译 key：已整理的业务引用所属分组的 `title`，例如 `knowledge.document.title`、`knowledge.tags.title` 和 `knowledge.documentStrategy.title`；仅有菜单名称的功能引用 `knowledge.menu`，不重复定义标题。“设置”复用 `common.labels.settings`。
文档列表的文件状态标题、专属处理阶段和进度归 `knowledge.document.status`，通用状态复用 `common.status`；召回处理选项归 `knowledge.document.hitHandling`。筛选项和行内展示共用译文，接口接收原有状态、任务类型和召回处理值。
图片菜单与页面标题共用 `knowledge.image.title`。图片处理配置复用 `knowledge.documentStrategy`，上传限制、格式说明和上传校验复用 `upload`；文档状态、召回处理及共用文档操作继续引用 `knowledge.document`，统计字段引用 `knowledge.stats`。接口返回的图片名称、标签、模型和工具名称保留原文。
工作流文档导入的操作归 `knowledge.document.import`。导入与调试共用的数据源、默认用户输入标题和执行结果专属文案归 `workflow.json`，分别使用 `workflow.dataSource`、`workflow.userInput` 和 `workflow.executionResult`；执行中和已取消复用 `common.status`。

## 文件夹

`folder.json` 的 actions 维护创建文件夹、创建子文件夹、编辑文件夹等操作。将文件夹或资源移动到目标文件夹时，菜单、批量操作和弹窗标题统一使用 `folder.actions.moveTo`。
sort 维护目录树排序选项，
delete 维护删除确认。名称与描述的表单提示、通用按钮、字段标签、搜索占位和成功提示复用 common，
资源授权入口复用 resource。目录树与列表标题复用 application、knowledge 或 tool 的 categories.all / shared，
每个分类名称按完整短语翻译；用户创建的文件夹名称和描述按原值展示。

## 动态表单

`dynamic-form.json` 挂载为 `dynamicForm`，维护配置器基本信息、控件类型、选项配置、显隐条件、
固定帮助文案，以及运行时控件的缺省提示；通用操作、结果提示和对话框标题复用 common。
同一字段的标签、占位和校验集中到 fields；通用占位提示复用 common.placeholders，
缺省必填提示根据实际控件使用 common.validation 中带字段名的输入或选择提示。
显隐条件的比较值也按输入框或选择框区分提示，占位与校验分别定义 key。模型类型复用 model.fields.type；
模型参数表的参数、显示名称、组件类型和默认值复用 dynamicForm.fields。控件类型使用 types，
条件比较方式使用 operators，上传与树形配置的专属文案分别使用 upload、tree；仍遵守四层上限。
控件类型定义统一来自 DYNAMIC_FORM_TYPES，由调用方翻译 labelKey；下拉选项响应式生成，
表格按 value 查找显示文案。控件类型协议值与比较符枚举不翻译，不把当前语言保存到配置。
用户输入、接口字段说明、选项标签及已有序列化规则原样保留；配置器 getData() 继续输出原协议，
不将当前语言写入配置。其他共享组件的内部文案和 Demo 按其各自批次处理。
