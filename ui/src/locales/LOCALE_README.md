# 国际化规则

`src/locales` 负责界面语言、语言包和入口初始化。当前支持 `zh-CN`、`en-US` 与 `zh-Hant`，
默认及缺失文案回退为简体中文。语言包暂随入口加载，新增语言时再评估按需加载。

## 分类

按“业务域 → 对象或场景 → 文案用途”组织；文件按业务域划分，不对应组件目录。
当前建立实际使用的 auth、model、common、resource、dynamicForm、workspace 语言包；其他业务包按需创建，不保留空包。

| 业务域      | 内容                                             |
| ----------- | ------------------------------------------------ |
| common      | 无业务含义的操作、基础校验、界面偏好和通用错误页 |
| auth        | 登录、退出、找回密码、身份认证                   |
| application | 智能体创建、配置、发布、版本                     |
| knowledge   | 知识库、文档、分段、问题、标签、检索             |
| model       | 模型、供应商、模型参数与连接测试                 |
| dynamicForm | 动态表单控件类型及配置器的固定界面文案           |
| resource    | 跨资源授权、关联关系及文件夹等公共业务           |
| tool        | 工具、MCP、Skill 管理                            |
| workflow    | 画布、节点、变量、调试与执行展示                 |
| chat        | 对话输入、消息操作、历史会话与对话状态           |
| workspace   | 工作空间、成员、空间级设置                       |
| system      | 用户、角色、系统配置、许可证                     |

翻译 key 最多四层，包含业务域命名空间。共用字段使用 `<业务域>.fields.<字段>.<用途>`，
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
通用展示标签归 common.labels，不为简单标签再嵌套 label；
通用操作结果归 common.messages，通用对话框标题归 common.dialogs；业务专属确认句仍留在所属业务域。
用户内容、提示词、协议枚举和已保存节点名称不进入语言包。

## 使用约定

- key 使用表达业务含义的英文 camelCase，不使用中文、数字序号或 misc 等模糊分类。
- JSON 文件不重复包裹业务域，由 index.ts 挂载命名空间；各语言保持相同 key 与插值参数。
- 完整句子整体翻译，动态内容使用命名参数；不用片段拼接句子。
- 英文界面采用简洁、明确的表达。通用输入、选择占位分别使用 Please enter、Please select，
  不使用省略号；明确对象时使用 Enter a model name、Select a model 等完整短语，不统一添加 Please。
  无具体对象的通用必填校验使用 This field is required；具体字段校验仍优先写明对象。
  按钮使用 Save 等动作词，成功提示使用 Saved successfully。短标签和占位提示使用句首大写，
  通常不加句号；占位与校验仍保留独立 key。
- 组件显式导入 useI18n，并使用全局作用域的 t；不使用自动注入的 $t。
- 依赖语言的选项和校验规则在 computed 或执行时翻译，不在模块初始化时固化翻译结果。
- 不为语言切换添加重新校验表单的 watch；已有错误提示在下次正常校验时更新。
  响应式规则变化不自动触发校验，表单使用 :validate-on-rule-change="false"。
- 新增业务包时更新 index.ts 的所有语言及 MessageSchema，以中文结构约束翻译 key。
- 非组件代码通过调用方传入翻译能力，不依赖某个入口的全局国际化单例。

## 语言状态

Admin 和 Chat 分别调用 createAppI18n，连接自己的 User Store；该模块不导入任何 Store。
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

## 动态表单

`dynamic-form.json` 挂载为 `dynamicForm`，维护配置器基本信息、控件类型、选项配置、显隐条件、
固定帮助文案，以及运行时控件的缺省提示；通用操作、结果提示和对话框标题复用 common。
同一字段的标签、占位和校验集中到 fields；通用占位提示复用 common.placeholders，
通用输入校验复用 common.validation，占位与校验分别定义 key。模型类型复用 model.fields.type；
模型参数表的参数、显示名称、组件类型和默认值复用 dynamicForm.fields。控件类型使用 types，
条件比较方式使用 operators，上传与树形配置的专属文案分别使用 upload、tree；仍遵守四层上限。
控件类型定义统一来自 DYNAMIC_FORM_TYPES，由调用方翻译 labelKey；下拉选项响应式生成，
表格按 value 查找显示文案。控件类型协议值与比较符枚举不翻译，不把当前语言保存到配置。
用户输入、接口字段说明、选项标签及已有序列化规则原样保留；配置器 getData() 继续输出原协议，
不将当前语言写入配置。其他共享组件的内部文案和 Demo 按其各自批次处理。
