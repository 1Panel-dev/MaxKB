# 国际化规则

`src/locales` 负责界面语言、语言包和入口初始化。当前支持 `zh-CN`、`en-US` 与 `zh-Hant`，
默认及缺失文案回退为简体中文。语言包暂随入口加载，新增语言时再评估按需加载。

## 分类

按“业务域 → 对象或场景 → 文案用途”组织；文件按业务域划分，不对应组件目录。
当前仅建立实际使用的 auth.json；common 等业务包在有文案接入时创建，不保留空包。

| 业务域      | 内容                                             |
| ----------- | ------------------------------------------------ |
| common      | 无业务含义的操作、基础校验、界面偏好和通用错误页 |
| auth        | 登录、退出、找回密码、身份认证                   |
| navigation  | 导航菜单、面包屑、浏览器页面标题                 |
| application | 智能体创建、配置、发布、版本                     |
| knowledge   | 知识库、文档、分段、问题、标签、检索             |
| model       | 模型、供应商、模型参数与连接测试                 |
| tool        | 工具、MCP、Skill 管理                            |
| workflow    | 画布、节点、变量、调试与执行展示                 |
| chat        | 对话输入、消息操作、历史会话与对话状态           |
| workspace   | 工作空间、成员、空间级设置                       |
| system      | 用户、角色、系统配置、许可证                     |

业务域内按实际对象拆分，如 knowledge.document；末级按用途使用：
`title`、`description`、`actions`、`fields`、`validation`、`messages`、`dialogs`、
`states`、`options`、`empty`。fields 内使用字段名下的 label、placeholder、description。

归属以业务含义判断：知识库检索模式归 knowledge，知识库检索节点归 workflow。
系统资源管理复用原业务域，不复制到 system。多处使用不等于通用；相同中文但业务语义
不同可以使用不同 key。用户内容、提示词、协议枚举和已保存节点名称不进入语言包。

## 使用约定

- key 使用表达业务含义的英文 camelCase，不使用中文、数字序号或 misc 等模糊分类。
- JSON 文件不重复包裹业务域，由 index.ts 挂载命名空间；各语言保持相同 key 与插值参数。
- 完整句子整体翻译，动态内容使用命名参数；不用片段拼接句子。
- 组件显式导入 useI18n，并使用全局作用域的 t；不使用自动注入的 $t。
- 依赖语言的选项和校验规则在 computed 或执行时翻译，不在模块初始化时固化翻译结果。
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
