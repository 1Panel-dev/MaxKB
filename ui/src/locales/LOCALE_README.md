# 国际化规则

`src/locales` 负责界面语言、语言包和入口初始化。当前支持 `zh-CN`、`en-US` 与 `zh-Hant`，
默认及缺失文案回退为简体中文。语言包暂随入口加载，新增语言时再评估按需加载。

## 分类

按“业务域 → 对象或场景 → 文案用途”组织；文件按业务域划分，不对应组件目录。
当前运行时接入 auth.json、common.json、components.json、model.json、dynamic-form.json，以及 system 下的 identity.json、resource-management.json、shared-resources.json；
其余已提取的中文业务包用于分批接入，不保留空包。

每种语言的公共及资源业务文件放在语言目录根部；系统专属文案集中到 `system/`：

```text
zh-CN/
├── common.json
├── auth.json
├── layout.json
├── navigation.json
├── dynamic-form.json
├── components.json
├── home.json
├── application.json
├── knowledge.json
├── tool.json
├── model.json
├── trigger.json
├── workflow.json
└── system/
    ├── identity.json
    ├── chat-management.json
    ├── settings.json
    ├── operate-logs.json
    ├── resource-management.json
    └── shared-resources.json
```

`home.json` 收录工作空间和系统概览共用内容；资源业务包供工作空间与系统入口复用。
`system/resource-management.json` 和 `system/shared-resources.json` 仅收录系统专属文案。
`layout.json` 收录管理端头部、侧栏操作、头像菜单、工作空间切换和关于弹窗文案；修改密码表单
归 `auth.json`，通用按钮和语言字段复用 `common.json`。
`navigation.json` 收录管理端菜单与路由标题，按主导航、系统、资源详情和工作流归类；
工作空间和系统入口的同类菜单共用 key，不按路由文件复制。设置、资源授权复用 `common.actions`，
登录复用 `auth.login.actions.submit`；导航标题与业务页面文案分别维护，后续按语义评估复用。
`components.json` 收录 `src/components/` 中普通 UI 与业务组件的专属文案，按组件用途分组。
源码位于 `constants/`、`utils/` 时仍按用途归类：复制反馈、错误页和跨模块执行状态
归 `common.json`；修改密码与登录 SDK 提示归 `auth.json`；资源文件夹入口、授权选项归
`components.folder`、`components.resourceAuthorization`；文档命中处理和分段标识归 `knowledge.json`；
角色类型、主题颜色分别归 `system/identity.json`、`system/settings.json`。修改密码的必填提示可复用
`common.form.inputField` 与对应字段名，长度限制复用 `common.validation.lengthRange`；找回密码
已有的确认密码必填提示继续复用。配置默认值中的免责声明、平台标语与用户配置不自动翻译。
`mk-dynamics-form/` 的字段类型、构造器、显隐条件、上传和校验文案统一归入 `dynamic-form.json`，
单项和批量使用场景共用该语言包；通用操作仍复用 `common.json`，不收录演示页专属内容。
`workflow.json` 收录 `views/workflow/` 与 `workflow-canvas/` 的界面文案，按编辑器、发布历史、
调试、执行记录、画布、节点及 AI 生成分组；节点专属文案放在 `nodes.<节点名>`，跨节点表单与
配置文案按 `parameters`、`model`、`variables` 等用途归类。已有公共、资源业务及动态表单文案
复用所属语言包；内部 AI 提示词、Schema 指令、默认对话内容及用户保存的节点数据不作为界面翻译。
文件名使用小写连字符；接入时由 `index.ts` 将系统文件挂载到 `system` 下的 camelCase 命名空间，
例如 `system.identity`、`system.resourceManagement`；`dynamic-form.json` 使用 `dynamicForm` 命名空间。
其他语言补充对应业务包时保持相同目录结构。

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
按模块接入，允许过渡期保留原中文。模型目录的列表、卡片、创建／编辑和参数设置外层已接入三语；
动态表单组件的固定文案、默认输入提示和前端校验已接入三语；历史字段配置与后端下发的文案保留原值。
其他共享组件内部文案按所属批次处理，供应商与用户配置名称保留原值。
系统资源管理与共享资源的模型页面已接入三语。资源卡片、空状态、搜索及表头筛选的固定文案，
资源授权、关联资源和授权工作空间弹窗已接入三语；其他组件和导航文案按所属批次处理。
components.json 与 system/identity.json 已具备三语配置，尚未替换的页面继续保留原文案。
模型类型统一使用 `MODEL_TYPE_LABELS` 保存翻译键，各引用处通过 `t()` 获取文案。
每批完成后等待用户检查，未经确认不扩展下一批。
