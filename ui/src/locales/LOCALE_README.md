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
common.status 维护状态标签 label 和通用启停选项 enabled、disabled。
通用日期范围预设及起止日期占位归 `common.dateRange`，音视频播放失败提示归 `common.messages`。
通用文件选择、上传提示和校验归 `upload.json`，上传进度和结果汇总归 `upload.status`。
头像设置、图片上传说明及校验归 `upload.avatar`；文件后缀编辑的操作和提示归 `upload.extension`。
业务模板、文件内容要求和导入说明归各自业务域。
“请输入模型名称”等指明业务对象的提示，以及发布状态、执行状态等业务选项归对应业务域。
通用操作结果归 common.messages，通用对话框标题归 common.dialogs；业务专属确认句仍留在所属业务域。
用户内容、用户保存的提示词、协议枚举和已保存节点名称保留原文。

## JSON 键顺序

- 同一语言包的键按含义分组，简体、繁体和英文采用相同的排列顺序，方便逐项对照。
- `common.json` 的顶层顺序为 `labels` → `name` → `description` → `status` → `dateRange` → `parameters` → `actions` → `dialogs` → `messages` → `placeholders` → `validation` → `empty`。
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
资源共享标签、MCP 服务配置、触发器及执行记录入口归 resource。
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

## 知识库列表

英文界面将“知识库”统一译为 `knowledge`，独立标题写作 `Knowledge`，例如“全部知识库”为 `All knowledge`。
工作空间、系统资源管理和系统共享资源的知识库菜单与列表标题共用 `knowledge.title`。四类知识库分别归 `knowledge.base`、`knowledge.web`、`knowledge.lark` 和 `knowledge.workflow`。类型筛选、类型列和创建菜单共用各组的 `label`，菜单说明使用 `description`，创建弹窗标题使用 `createTitle`。筛选请求沿用数字类型值。
卡片的文档数、字符数和图片数使用 `knowledge.stats`，按实际数量选择单复数。同步、向量化、生成问题和分词索引归 `knowledge.actions`。
跨资源的模板中心文案归 `resource.templateStore`。模板名称、描述和 README 展示接口原文；缺少说明时与工具商店共用 `common.empty.noDetails`。
手动同步、定时同步及日志共用 `knowledge.sync` 中的同步方式。向量化和生成问题共用的分段范围在 `knowledge/index.json` 中维护，使用 `knowledge.paragraphScope`。生成问题弹窗的字段、校验和内置默认提示词归 `knowledge.generateQuestions`。无已保存配置时按打开弹窗时的语言填入默认提示词，保留 `{data}` 与 `<question></question>`。提交时使用编辑框中的原文。
导出格式与源文件说明归 `knowledge.export`，单个及批量删除的确认标题归 `knowledge.delete`。
Web 创建的根地址与选择器归 `knowledge.fields`。创建、文档上传、导入和设置共用的分段规则、图片处理与索引增强文案归 `knowledge.documentStrategy`。
分段标识的文字选项归 `knowledge.documentStrategy.splitPatterns`，在 `knowledge/settings.json` 中维护。文档策略表单与工作流分段节点在展示时翻译 `DOCUMENT_SPLIT_PATTERN_OPTIONS` 的 `labelKey`；纯符号、Agent 参数识别用的 `label` 及正则 `value` 保留原值。

## 知识库详情

`knowledge/index.json` 维护列表、知识库类型、创建、共用文案及尚未独立分文件的业务文案。仅有菜单名称、尚未形成独立业务分组的功能集中在 `knowledge.menu`，按菜单显示顺序排列，使用 `knowledge.menu.<名称>`。
`tag.json` 维护标签管理与文档标签设置，使用 `knowledge.tags`。`document.json` 维护文档列表、上传与预览，使用 `knowledge.document`；图片列表、上传、详情及校验文案同文件存放，使用与 `document` 平级的 `image` 分组，引用为 `knowledge.image`。`paragraph.json` 维护分段字段、校验、关联问题、列表操作及删除确认，使用 `knowledge.paragraph`；分段列表与导入预览共用 `knowledge.paragraph.empty`，数量单位复用 `knowledge.stats`。`settings.json` 维护文档处理策略和同步，生成问题弹窗归 `generate-questions.json`。
标签导入标题、模板和格式限制归 `knowledge.tags.import`，关联文档标题及页签归 `knowledge.tags.documents`；文档字段复用 `knowledge.document`，通用关联操作及结果提示复用 `common`，文件选择校验复用 `upload`。
翻译按业务含义归属，不与页面目录一一对应：分段字段和操作归 `knowledge.paragraph`，文档字段、操作及流程说明归 `knowledge.document`，页面可交叉引用。
导入预览删除分段使用 `knowledge.paragraph.delete.confirm`；继续导入前的编辑未完成提示保留在 `knowledge.document.preview`。文档召回处理和删除文档的影响说明仍归 `knowledge.document`。
跨对象共用的召回次数、最后一次召回时间归 `knowledge.stats.retrievalCount` / `lastRetrievedAt`，文档列表和分段预览共用。
文档、图片与分段的迁移入口共用 `knowledge.actions.migrate` / `migrateTo`，成功提示共用 `knowledge.messages.migrateSuccess`。迁移目标知识库使用 `knowledge.fields.targetKnowledge`，目标文档使用 `knowledge.document.target`，占位与必填提示分别维护。分段位置菜单归 `knowledge.paragraph.position`；新增、保存和移动成功提示复用 `common.messages`。
四种资源范围的详情菜单和页面标题共用路由中的翻译 key：已整理的业务引用所属分组的 `title`，例如 `knowledge.document.title`、`knowledge.tags.title` 和 `knowledge.documentStrategy.title`；仅有菜单名称的功能引用 `knowledge.menu`，不重复定义标题。“设置”复用 `common.labels.settings`。
文档列表的文件状态和进度归 `knowledge.document.status`，召回处理选项归 `knowledge.document.hitHandling`。筛选项和行内展示共用译文，接口接收原有状态、任务类型和召回处理值。
图片菜单与页面标题共用 `knowledge.image.title`。图片处理配置复用 `knowledge.documentStrategy`，上传限制、格式说明和上传校验复用 `upload`；文档状态、召回处理及共用文档操作继续引用 `knowledge.document`，统计字段引用 `knowledge.stats`。接口返回的图片名称、标签、模型和工具名称保留原文。
工作流文档导入的操作归 `knowledge.document.import`。导入与调试共用的数据源、默认用户输入标题和执行结果归 `workflow.json`，分别使用 `workflow.dataSource`、`workflow.userInput` 和 `workflow.executionResult`。

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
