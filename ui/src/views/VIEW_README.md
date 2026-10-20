# 页面职责与组织

本文维护页面边界、功能本地目录和关键业务约束。请求协议见
[API_README.md](../api/API_README.md)，路由与导航见
[ROUTE_README.md](../router/ROUTE_README.md)，公共组件接口与生命周期见
[COMPONENT_README.md](../components/COMPONENT_README.md)，画布内部规则见
[WORKFLOW_README.md](../workflow-canvas/WORKFLOW_README.md)。

## 功能本地组织

- 路由页使用 `views/<feature>/index.vue`；多个独立页面按业务职责拆分子目录，不平铺无关页面。
- 普通子组件放在功能的 `components/`；Drawer 留在所属流程目录，命名 `XxxDrawer.vue`；
  Dialog 命名 `XxxDialog.vue`。按钮命名遵循组件文档，不把 Dialog 与 Drawer 混用。
- 完整业务流程可使用 `create-application/` 等目录，入口、浮层及配套逻辑一起维护。
- 单页类型、常量、函数留在功能内；同一功能复用代码放在最近共同目录。跨功能复用再按专题规则提升。
- TypeScript 文件名表达具体职责，顶部注明用途；注释解释业务约束和执行顺序。
- 脚本按列表查询、批量操作等业务流程组织状态和方法，较长流程在确认、请求、刷新等关键点添加备注。
- 模板不直接调用浮层 Ref 的 `open()`，通过 `handleOpenXxx` 语义方法打开。
- 用户交互触发的联动优先使用 `change` 等事件；父级 Props、异步配置或多个来源的变化才使用 `watch`。
- 创建、保存、提交使用内容容器或按钮 loading，不逐字段禁用，也不设置提交态的 `el-form.disabled`。
  入口保留重复提交保护，关闭、取消、步骤切换可按提交状态禁用；只读、权限、字段联动和选项加载禁用保留。
- 新功能权限边界遵循 [AGENTS.md](../../AGENTS.md)，创建或导入后原有用户基础资料刷新保留。
- 顶部、行内、菜单和批量操作前添加中文用途注释，批量操作明确标注“批量”。
- 菜单内含自带浮层的 Action 时复用组件的 `persistent`，不自行维护菜单挂载状态。
  常驻浮层与关闭后卸载浮层的清理遵循组件文档。

`action-dropdown/` 优先用于 application、knowledge、model、tool 四类跨范围资源。
文档和分段按现有需求使用各自 `action-dropdown/`，不据此扩展到所有普通页面。
单文件 Action 平铺，多文件流程放在职责明确的子目录；公共浮层才提升到最近共同功能目录。

## 页面功能索引

新增、移动、重命名或改变路由页职责时更新本表。路径均相对 `src/views/`；同一行列出的子目录
各自以 `index.vue` 为入口，不登记内部组件或函数。

| 功能目录                                                                              | 当前职责                                     |
| ------------------------------------------------------------------------------------- | -------------------------------------------- |
| `home/`、`system/home/`                                                               | 工作空间／系统首页统计、资源概况和排行       |
| `application/`、`knowledge/`、`model/`、`tool/`                                       | 工作空间资源列表、创建及维护                 |
| `application-detail/`                                                                 | 智能体详情上下文与资源详情布局               |
| `application-detail/overview/`、`setting/`                                            | 概览、简易智能体设置                         |
| `application-detail/chat-user/`、`chat-log/`                                          | 对话授权、日志与标注                         |
| `application-detail/access/`                                                          | 发布渠道配置、启停与回调地址                 |
| `knowledge-detail/`                                                                   | 四范围知识库详情、菜单与上下文               |
| `knowledge-detail/library/document/`、`tags/`                                         | 文档及标签维护                               |
| `knowledge-detail/library/image/`                                                     | 图片列表，复用文档操作                       |
| `knowledge-detail/hit-test/`                                                          | 召回测试参数、文本／图片查询及结果展示       |
| `knowledge-detail/question/`                                                          | 问题管理占位页                               |
| `knowledge-detail/termbase/`                                                          | 知识库自定义分词维护                         |
| `knowledge-detail/chat-user/`、`external-retrieval/`                                  | 对话授权与外部检索配置                       |
| `knowledge-detail/setting/base/`、`document-strategy/`、`scheduled-sync/`             | 基础设置、文档策略、定时同步与日志           |
| `knowledge-detail/workflow-transform/`                                                | 非工作流知识库转换说明与确认                 |
| `document-detail/`                                                                    | 四范围文档分段查询、详情及可管理范围维护     |
| `workflow/application/`、`tool/`、`knowledge/`                                        | 全屏画布、加载、保存、发布、历史、模板与调试 |
| `trigger/`                                                                            | 触发器列表、任务配置、启停及执行记录         |
| `system/resource-management/application/`、`knowledge/`、`model/`、`tool/`            | 跨工作空间资源管理                           |
| `system/shared-resources/knowledge/`、`model/`、`tool/`                               | System 共享资源管理                          |
| `system/identity/users/`、`groups/`、`roles/`、`workspaces/`                          | 用户、用户组、角色与工作空间管理             |
| `system/identity/resource-authorization/`                                             | 分类资源授权                                 |
| `system/chat-management/users/`、`user-groups/`、`authentication/`、`portal-setting/` | 对话用户、组、认证和门户设置                 |
| `system/settings/theme/`、`authentication/`、`email/`                                 | 外观、登录认证与邮件设置                     |
| `system/operate-logs/`                                                                | 操作日志与清除策略                           |
| `login/`、`login/forgot-password/`                                                    | Admin 登录与找回密码                         |
| `chat/`、`portal/`                                                                    | 单应用与门户对话                             |
| `chat/login/`、`chat/error/`、`error/`                                                | Chat 登录、Chat／Admin 错误页                |
| `details-demo/`                                                                       | 临时执行详情预览                             |

## 资源列表与详情

四类资源的范围定义由路由文档维护，完整 API 选择规则由 API 文档维护。
资源卡片放在基础资源目录 `<resource>-card/`，System 页面复用，不复制展示实现。
卡片只负责展示、选择和操作插槽；页面按场景组合 Action，传入中文 `label`、资源及完整 API。
跨范围 Action 留在基础资源目录，仅 System 使用的 Action 留在对应 System 功能目录。

- 单项移动复用 `MoveToDialog`，具体目录转出后局部移除，“全部”目录保留；批量移动和删除由页面管理。
- 切换文件夹退出批量模式，搜索／刷新清空选择；创建或导入成功保留资料刷新和原有导航。
- 普通 Workspace 详情返回列表时恢复所属 `folderId`；共享知识库返回 `folderId: 'shared'`。
  文件夹地址同步与工作空间切换规则见路由文档。
- `application-detail/context.ts` 提供只读详情、替换和刷新；完整响应局部替换，部分响应重新查询。
  通过 `provideApplicationDetailContext`／`useApplicationDetailContext` 统一提供 `applicationId`、
  `resourceApi`、`listRouteName` 与 `routeParams`，仅支持 Workspace 和 System 资源管理。
  `resourceApi.application / chatUser / overview / access / chatLog / workflow` 按范围选择完整 API，
  不包含 Workspace 共享或 System 共享，不将缺失方法回退到 Workspace。
  切换二级菜单不重复挂载详情容器。
- 创建模型入口接收完整 Model API；创建成功刷新基础资料后通知调用方刷新选项。
- 工具表单按类型放在 `tool-form/`，共用参数及 Python 设置放在 `tool-form/component/`。
  创建和编辑复用同一表单，不把不同类型字段合并成通用表单。
- `ToolCard` 点击工作流进入画布，其他类型调用编辑 Action 的同一表单实例；编辑、启停成功局部更新。
  商店列表由页面加载，卡片和版本更新按钮不重复查询。
- 工具头像由 `MkEditAvatar` 暂存文件，校验后先上传再保存；上传成功后清理暂存文件，避免保存失败后重复上传。
- Python 生成入口由 `CodeGenerate` 选择 Tool／Model API，复用 `GenerateContent`；全屏替换只修改草稿，确认后回写。
- System 模型／工具使用表格，保留既有权限、引用数量删除提示和末页回退；不新增不存在的创建／导入能力。
  工作空间列与选项仅企业版显示，筛选 `workspace_ids` 使用 JSON 数组字符串。
- Workspace 共享知识库只读；System 共享资源页面按自身 API 维护，不组合 Workspace 文件夹移动等操作。

资源授权和关联资源入口按需挂载公共抽屉，关闭动画结束后卸载。授权使用资源数据的
`workspace_id`；关联资源抽屉的查询与工作空间展示规则见组件和 API 文档。

## 详情布局与知识库上下文

智能体发布渠道位于 `application-detail/access/`，支持企业微信智能机器人、企业微信应用、钉钉、
公众号、飞书和 Slack。平台字段与后台指引在功能本地 `platforms.ts` 维护；卡片按配置状态显示
启停开关，保存状态成功后更新显示。配置抽屉按需挂载并在关闭动画后卸载，每次打开重新查询，
保存失败保留草稿。公众号提供认证开关，飞书 Verification Token 可选；回调 URL 只读并支持复制。

`layout/ResourceDetailLayout.vue` 提供侧栏和固定标题栏。子页声明 `ResourceDetailPageProps`，
普通页使用默认标题；`defineExpose({ customHeader: true })` 配合 Teleport 到 `headerTarget`
自定义标题、搜索及操作；`hideHeader: true` 隐藏整个标题栏且优先于自定义标题。
不再嵌套页面布局、创建 Header 注入或增加路由字段。

`knowledge-detail/context.ts` 仅通过 `provideKnowledgeDetailContext` 和
`useKnowledgeDetailContext` 公开详情、更新能力、ID、来源导航及完整 API。
`resourceApi.knowledge / scheduledSync / document / paragraph / image / tags / termbase / problem / chatUser / externalRetrieval` 按当前范围响应式读取，无需 `.value`，
不要在 setup 时解构具体 API。`workflow` 当前仅普通 Workspace 提供，其他范围不回退。
共有查询方法必填，部分范围缺失的方法可选调用；未发请求时不提示成功、不关闭、不刷新或修改快照，loading 正常清理。
不增加查询／维护双入口、接口别名或专属 Context hook，也不以方法存在性新增操作显隐规则。

仅支持部分来源的消费方可传 `useKnowledgeDetailContext({ resourceScopes: [...] })`，
由上下文统一校验并返回来源文档页，保留类型、query 和 hash。未约定接口或返回结构先与用户确认。
基础设置、文档策略、定时同步及转换说明允许 Workspace 共享访问；本地设置可编辑，仅隐藏保存／转换按钮，
提交入口同时阻止共享写入。System 文档、标签与分段 API 已装配，具体服务能力仍需对应部署支持。
知识库全屏 WorkflowView 的加载、保存、模型查询仍直接使用 Workspace API，其他来源仅完成导航，不能视为范围接入完成。

### 简易智能体设置

`application-detail/setting/` 使用可折叠配置表单和调试预览占位双栏布局，仅模型设置和知识库
通过 `:expanded="true"` 默认展开，未绑定更新事件时由组件内部切换状态。通过详情上下文按
Workspace／System 资源管理范围保存、发布，发布前先保存当前配置；草稿独立深拷贝，保存失败
保留输入，保存成功后用返回详情回填。详情返回的模型别名统一回填，空语音模型 ID 提交
`null`，简易设置不提交详情中的画布或只读字段，保留范围外配置。

知识库、智能体、技能和工具复用公共资源选择弹窗，保留未能查询到的关联 ID；智能体排除自身。
技能区域复用 AI 对话节点的 `ResourceSetting`，统一选择、移除及 MCP 来源配置；资源 ID 与回显
快照回写页面草稿，保存时剔除回显快照。详情回填时，有关联智能体 ID 才查询智能体列表，
有工具、Skills 或 MCP ID 才查询工具列表，用于补全名称和图标。长期记忆使用功能本地 `ButtonLongTermSetting`，沿用工作流的轮次、周期和 Cron 交互，
直接选择模型与参数，不提供默认模型选项；打开时若未配置模型，选中首个可用模型，
选项异步返回后同样补选，已有选择不覆盖。简易接口提交具体模型 ID。语音输入直接选择模型，语音播放提供浏览器播放和自定义模型，
不提供默认语音模型选项；启用后显示自动发送／播放，关闭时清空对应模型，播放恢复浏览器方式。输出思考复用工作流的 `ThinkingSetting`，确认时合并思考字段并保留系统和用户提示词。
知识库检索、无引用处理和问题优化由功能本地 `ButtonKnowledgeSetting` 维护，按钮与弹窗封装在同一组件，
弹窗确认只更新页面草稿。模型使用当前范围的共享模型查询和参数接口。系统提示词生成复用
工作流的 `PromptGenerate`，由页面注入 `resourceScope`，使用当前模型与参数生成后回填草稿。

### 创建与设置

四类知识库创建入口集中在 `knowledge/create-knowledge/`：`BaseKnowledgeDialog`、
`WebKnowledgeDrawer`、`LarkKnowledgeDialog`、`WorkflowKnowledgeDialog`。
`KnowledgeBaseForm` 负责名称、描述及 Embedding 选择，内部按范围查询模型；未选择时默认首个可用模型，
刷新不覆盖用户选择。创建浮层接收完整 Knowledge API，工作流创建使用其 `postKnowledgeWorkflow`。

`DocumentStrategyForm` 由 Web 创建、文档上传及策略设置复用；视觉增强仅在启用、切换策略或回填启用配置时
查询对应模型／工具，刷新模型不请求工具。Web 创建两步，策略设置回填独立草稿并单独保存 `doc_strategy`，下次同步生效。
基础设置保留未编辑的来源 `meta` 和顶层上传限制；更换向量模型先确认、保存，再向量化。
向量化失败保留原比较基准以便重试；Workspace 飞书使用专用保存，System 使用通用保存。

定时同步提供设置与日志；查询成功后才允许保存，成功以规范化响应更新草稿和详情。
复用周期及同步方式常量，支持日、周、月、间隔和 Cron，间隔至少 5 分钟；完整 Cron 由后台校验。
日志页按需挂载 `SyncLogTable`，传完整 API，仅展示定时任务，不轮询；跳过执行展示原因。

### 召回测试

`hit-test/` 提供参数／输入与结果两栏，标题位于左栏，右侧结果面板贴合内容区的顶部、底部和右边缘。通过详情上下文选择 Workspace、
System 资源管理或 System 共享 Knowledge API 的 `postKnowledgeHitTest`；Workspace 共享缺少对应接口时
由上下文返回文档页，不回退其他范围。
两栏高度使用内容区布局尺寸，分别通过 `el-scrollbar` 独立滚动；左栏包含标题、参数和输入区，右栏包含本次查询与结果。
默认向量检索、相似度 0.600、TOP K 6；切换全文检索重置相似度为 0，其余模式为 0.6。
文本和图片至少提供一项，空白文本不可提交；仅 BASE 通用知识库支持图片查询，其他类型隐藏图片上传入口并禁止选择、拖拽和粘贴图片。
图片上传不受检索模式限制，已有图片不限制检索模式切换。
图片通过 Admin File API 上传为 120 分钟临时文件，仅提交上传成功的文件引用；数量和单文件大小读取知识库
`file_count_limit`、`file_size_limit` 配置，与图片上传抽屉一致，数量最多 50 张，缺省为 50 张、每张 100MB。
支持 JPG、JPEG、PNG、WEBP、BMP，文件选择、格式校验和提示使用一致的类型配置。
召回测试与对话输入共用 `conversation-panel/core/input-events.ts` 的选择文件、拖拽、粘贴和提交快捷键。
`HitTestInput` 管理文本、图片上传与提交校验，在输入框下方提供整行测试按钮。父页面传入测试请求的加载状态；
按钮与回车通过 `submit` 一次性提交文本和已上传图片，由父页面执行测试。
输入容器接收文件拖入和剪贴板附件，纯文本及混合内容中的文本保留原生粘贴；各入口使用相同的上传禁用条件。
桌面 Enter 提交，Ctrl／Shift／Alt／Meta + Enter 换行，输入法组合期间不提交；移动端 Enter 换行，文本上限 100000 字符。
输入区通过 `ImageUploadCard` 展示图片进度、失败重试和删除，不提供点击预览。上传中或存在失败图片时禁测试，
失败图片可直接重新上传或移除。移除与卸载释放本地预览并取消未完成上传。
测试期间冻结参数与输入；结果使用 `MkSourceCard` 展示分段、得分、文档名称及命中图片，Markdown 只读。
点击结果卡片按需挂载 `ParagraphDialog`，按命中分段的知识库和文档 ID 加载详情，关闭动画后卸载；保存正文后同步当前结果，保留检索得分。
“本次查询”展示成功请求的文本与图片快照，图片位于文本上方，缩略图自动换行并支持预览，不使用横向滚动。
初始与无命中分别展示空态；请求失败由请求层提示，保留输入与已有结果供重试。

### 文档列表与导入

`library/document/index.vue` 管理查询、分页、选择、启停及刷新；Action 管理各自请求和浮层。
`library/image/index.vue` 使用独立列表入口，复用 `document/` 的状态、展示组件及 Action，
查询与操作沿用 Document API；图片列表的查询参数差异见 [API 文档](../api/API_README.md#文档与分段)。
点击图片行通过 `resourceApi.paragraph.getParagraphPage` 查询首个分段，使用 `ParagraphDialog` 展示详情；弹窗按需挂载，关闭动画结束后卸载。
图片上传独立放在 `image/upload-image/`，`ButtonUploadImage` 管理入口与按需挂载，
`UploadImageDrawer` 分为上传图片、图片处理两步，复用 `MkDragUpload` 的多文件图片模式暂存文件；
`ImageProcessingForm` 管理视觉增强策略及模型／工具选项，不展示文档分段与索引设置。
生成预览时按当前策略提交原图，预览直接展示生成接口返回的数据，不单独查询或轮询。
开始导入以 `previewVisible` 区分：已预览提交生成结果的文件 ID，未预览校验处理策略后直接提交上传成功的图片 ID 和当前策略，
不自动请求生成预览；成功通知列表刷新，失败保留文件和策略供重试。
图片上传入口接收 `resourceApi.image`；Workspace 和 System 资源管理提供生成预览及批量添加，
共享范围不回退到 Workspace。
类型统一读取路由 `type`，使用 `KNOWLEDGE_TYPE_KEY`，不逐层传递类型 Prop。
挂载时查询并启动 6 秒轮询，请求结束后安排下一次；静默刷新保留筛选、页码和当前页选择，
操作中推迟轮询，卸载后停止。创建者选项打开或远程搜索时加载，不在页面进入时预查。

- 名称使用 `MkEditName`，最长 128，禁止 `: \ / ? * [ ]`；成功按 ID 更新名称与时间。
- 文件状态、启用、命中处理用 `MkTableFilter single`，标签用 `cascader`；改变条件回第一页并清空选择，保留其他条件。
  状态查询同步更新 `status` 与 `task_type`；布尔 false 保留，“全部”省略条件；标签传叶子 ID 或 `NO_TAG`。
- 字符数使用服务端表头排序，通过 `toOrderBy` 更新独立的 `orderBy`，请求时作为 `order_by` 传入；切换排序回第一页并清空选择，
  取消排序恢复后端默认顺序。搜索、筛选、分页和轮询保留当前排序，导入成功清空搜索及筛选时也保留排序。
- 任务解析及筛选统一在 `document/status.ts`，展示由 `DocumentStatus.vue` 负责；不复用执行记录状态。
  汇总优先级为取消中、执行中、排队中、失败、取消完成、成功；忽略未知和 n，保留取消完成显示成功的既有规则。
- 文档 Action 按 embedding、generate-questions、setting、setting-tags、tokenize、export、sync、migrate 等职责分组，
  通过 `action-dropdown/index.ts` 导出。打开前快照目标，单项和批量使用真实对应接口，共用页面操作 loading。
- 删除和同步先确认；成功清空选择刷新，导出／下载保留选择。启停成功后才回显，不在请求前改变状态。
- 图片列表批量删除和向量化分别向 `DeleteDocumentAction`、`BatchEmbeddingAction` 传入图片资源类型，打开操作时固定所选 ID 与类型；文档列表使用默认文档类型。
- 生成问题复用 `GenerateQuestionsDialog`，向量化与生成可选分段状态范围，分词处理全部状态。
- 单项 Web 设置保留来源 meta，批量隐藏地址／选择器并使用顶层 `allow_download`。
- Web、飞书提供同步；工作流仅 Web 来源文档支持单项同步，本地上传文档不提供；手动同步不写定时日志。
- 批量 More 使用 `hide-when-empty` 判断标准插槽，浮层生命周期遵循公共菜单保留规则。
- Workspace 共享隐藏选择、操作和批量入口，名称只读；标签加号保留禁用展示，不探测 API 方法控制显隐。

通用知识库通过 `MkTable.body-prepend` 组合 `MkQuickCreate`；页面创建请求成功才调用 `close()`，失败保留草稿。
快速创建不插入占位数据，也不计入分页与选择。

通用上传由 `upload-document/` 管理，Web／飞书／工作流导入由 `import-document/` 管理独立 Drawer。
复用 `MkDragUpload` 和 `DocumentStrategyForm`，传完整 Document API；使用成功文件 ID，不二次上传。
文本直接导入提交文件 ID 与策略；生成预览才携带文件 ID 与策略请求 split_by_file_ids，预览可本地编辑／删除，最终创建使用编辑后结果。
`document/components/DocumentImportPreview.vue` 提供文档与图片导入的左右预览布局；
组件统一使用 DocumentSplitResult 的文档列表与分段页面，不按图片类型区分展示。
图片生成结果直接传入预览组件，正文按接口返回的 content 展示，不转换或拼接；图片导入提交原始文件 ID，
预览内本地编辑不会写回图片生成结果。文档分段编辑与删除保留原有行为。
预览编辑复用 `ParagraphForm`、`ParagraphQuestions`，不传已有分段 ID，不即时写入问题关联。
表格／QA 支持模板下载；飞书懒加载仅展开时查子目录，已导入项不可取消，不在前端递归展开文件夹。
工作流导入执行已发布版本，复用知识库调试的 DataSource、KnowledgeBase、Result 三步流程。
本地文件校验上传成功及 `file_id`，远程工具数据源保留其文件／目录协议。
导入成功清空搜索、筛选并回第一页，失败保留文件、选择与策略。

### 标签管理

`library/tags/` 按标签组前端分页，再展开标签值；`MkTable.selectionGroupKey="key"`
联动组内选择，统计与删除按实际标签值数量。普通查询将名称传后端，共享无参数查询后本地筛选。
`CreateTagDialog` 创建多行组合或为 `open(key)` 添加值；`EditTagDialog` 只重命名或编辑单值，
保留完整 id、key、value，不模拟多行保存。名称／值上限 64／128，提交清理可编辑文本并检查重复。
`ButtonImportTags` 内聚 XLS／XLSX 导入及模板下载，失败保留文件。

`AssociatedDocumentDrawer` 从上下文读取 Document API，按已关联／未关联切换，搜索与布尔启用筛选可组合；
切换、分页和搜索清空选择，变更刷新数量，末页为空回退。
文档 `DocumentTags`、标签 Drawer 和批量 Action 各自维护添加弹窗；添加候选仅取前 100 组并本地搜索，
不禁选已关联值，后台去重。创建候选成功重载但不自动选择。删除仅解除文档关联，不删除知识库标签。

### 问题管理

`question/` 使用 `resourceApi.problem`，默认每页 20 条，不提供表头排序，搜索将 content 传给后端。
`ButtonCreateProblem` 内聚创建按钮和多行输入弹窗；快捷创建使用 `MkQuickCreate`，每个问题最多 256 字符。
单项与批量删除直接提交，删除后末页为空时回退到最后有效页；名称编辑复用 `MkEditName`。
点击数据行打开 `ProblemDetailDrawer`，勾选、名称编辑和操作按钮不触发行详情。
详情支持问题名称快捷编辑、关联分段卡片和跨页上一个／下一个；卡片复用 `.mk-paragraph-card` 样式，
点击打开已有 `ParagraphDialog`，悬浮取消关联按钮仅解除当前关联，成功刷新卡片与列表计数。
分段详情关闭后重查关联，保持编辑与解除关联后的数据一致。
单项、批量、详情的“关联分段”入口暂时禁用，待交互确认后接入，不创建关联弹窗或发送关联请求。
Workspace 共享只展示和搜索问题列表，不显示维护入口，也不打开缺少查询接口的问题详情。

## 文档分段

`document-detail/context.ts` 装配四范围完整 Document／Paragraph／Problem API 和返回导航，
无注入时按当前路由创建上下文，供导入预览复用。页面提供上下文；Action 接收选定 Paragraph API，
`paragraph-dialog/` 直接读取上下文，不透传 API。共有查询必填，维护方法按真实差异可选。
Workspace 共享只读，隐藏创建、编辑、排序、关联修改及批量操作；缺少详情接口保留默认标题，不回退。

主区通过 `MkInfiniteScroll` 加载分段，侧栏定位已加载卡片并同步高亮；全选只覆盖已加载数据，追加保留选择。
搜索／新增／删除／迁移通过 `refreshParagraphs()` 回第一页并清理选择；编辑与启停按 ID 局部替换，
不匹配筛选时刷新。不补偿分页偏移或改写服务端总数。

`action-dropdown/move/useParagraphSort.ts` 统一两侧 `useSortable`、位置请求、快照恢复和 loading。
菜单及拖拽共用 `putParagraphPosition`；成功本地同步受影响位置，失败恢复顺序，不重载分页。
普通 DOM 承载排序，不叠加 TransitionGroup；目录链接禁原生拖动但不阻断 Sortable。
拖拽仅覆盖已加载数据，保留原生链接／按钮交互；批量、加载、浮层、确认或位置保存中禁用。
菜单方向类型留在 move 目录，上下移动使用相邻真实位置，置顶为 1，置底以末段位置和总数兜底。

迁移和生成问题各维护独立单项与批量 Action，打开时固定目标，浮层关闭后卸载。
迁移允许同知识库其他文档，排除当前文档；成功刷新分段。生成问题隐藏状态范围，提交后仅清空选择，不重载列表。
批量删除留在页面，确认前快照目标；取消或失败保留选择。更多菜单展开状态只控制操作区显隐，挂载仍由 persistent 管理。

`paragraph-dialog/` 使用 `CreateParagraphDialog` 和 `ParagraphDialog`（详情／编辑），组合
`ParagraphForm`、`ParagraphPreview`、`ParagraphQuestions`。创建可指定插入位置；正文表单支持 Markdown 和知识库图片上传。
`ParagraphDialog` 的 `title` 可自定义详情标题，默认“分段详情”，图片列表传入“图片详情”；编辑模式标题为“编辑”。
图片列表将行数据的 `meta.source_file_id` 通过 `ParagraphDialog.sourceFileId` 传入，预览合并为分段的 `source_file_id`；
仅存在文件 ID 时展示图片，图片与 Markdown 正文共用滚动区域，保存正文后保留图片。
问题区使用远程候选和即时关联／解除，不删除问题本身；无分段 ID 时保存本地问题草稿，随新增提交。
正文保存不提交或回填 `problem_list`，避免覆盖并行关联操作；取消编辑不撤销问题修改。
问题区请求状态独立，不阻止正文保存／关闭；共享模式只展示，不查询可关联候选。
详情查询失败可重试，失败保留草稿；标题最多 256，正文界面最多 100000 字符。

## 工作流页面

三个入口均为 `views/workflow/<resource>/index.vue`，使用 `WorkflowViewLayout`。
View 负责路由、资源与模式、图加载、保存／发布／调试编排；画布公开接口及节点行为见画布文档。
整条页面操作共用一个 loading，最外层 finally 释放，内部保存／加载只返回 Promise。

- 自动保存默认关闭，按 `workflowAutoSave:<resource>:<id>` 独立记录；开启后每 60 秒保存未提交修改。
  加载、保存、发布、历史和退出确认中跳过；成功只更新本次快照，请求期间继续编辑仍算未保存；失败留待重试。
- 保存使用规范化 `getGraphData()`；默认模型与图一起持久化，失败回滚已保存配置并保持抽屉编辑草稿。
- 默认模型抽屉接收完整 Model API；“应用到所有节点”递归修改图，保留自定义配置及禁用功能，不自动提交模型草稿。
- 发布历史入口各自查询版本，共用纯 UI `publish-history/`；第一次预览保存草稿，关闭恢复，恢复版本只回编辑态，后续保存。
  版本缺少默认模型时保留当前配置；更新说明后端支持情况见 API 文档。
- 智能体发布先校验，再打开发布内容表单，提交先保存再发布；失败保留表单。
- 模板中心共享 UI 在 `workflow/components/template-store/`，业务入口查模板，View 确认覆盖、提交并重载详情和保存基准。
  创建模板由资源创建流程负责，取消／失败保留模板中心。
- 调试与导出先保存未提交修改，保存失败不继续；打开历史、模板或默认模型时按原流程关闭调试。
- 智能体复用对话模块 DebugPanel；工具使用 debug Drawer、SSE 和执行详情；知识库保留任务轮询与导入 Action。
  智能体画布按 Workspace／System 资源管理选择详情、保存、发布、模型和历史 API；DebugPanel 尚未按 System 范围适配。
  客户端停止读取不等于服务端停止任务。
- 知识库导出仅工作流 `.kbwf`；导入确认覆盖后直接上传，不先保存旧草稿，成功重载；取消／失败保留图。
  正式导入文档要求已发布；转换使用 Knowledge API，保留已有文档，不能用保存代替转换。
- 返回方法集中在各资源 `navigation.ts`；历史模式先退出预览，编辑态保留保存并退出／直接退出确认。
  当前没有通用路由离开或浏览器关闭守卫。
- 工具、知识库执行记录抽屉按需挂载，关闭后卸载；知识库记录每 6 秒刷新，关闭停止。
  执行时间列声明 `sortable`，独立 `orderBy` 通过 `toOrderBy` 添加 `ett.` 前缀，以 `order` 查询参数传入。
  切换排序回第一页；搜索、筛选、分页与轮询保留排序，重新打开时恢复默认排序。
  当前本地后端两类接口仍固定按执行时间降序，需支持 `order` 后才能实际响应升序请求。

## 其他页面约束

- 首页组件位于 `home/components/`，排行位于 `components/ranking/`。完整 Homepage API 和 workspaceId 由 View 传入。
  智能体筛选只影响趋势；日期复用 MkDateRange，默认过去 7 天；占比使用工作空间同期总量，累计活跃人次为每日人数之和。
  失败不伪装成零。快捷创建复用资源入口，`fitTriggerWidth` 仅显式开启时测量触发器。
- `HomeStatistics` 接收完整的 Workspace Homepage、System Homepage 或 Overview API。
  智能体概览通过 `hideHeader: true` 隐藏详情布局标题栏，保留内容内的监控与排行标题。
  三类场景统一调用 `getMonitoring(workspaceId, range, applicationId)`；全部智能体使用空 ID，
  两类首页不提交智能体筛选，概览传当前智能体 ID。页面直接传入完整 API，不包装接口。
  排行由概览本地 `components/ApplicationRanking.vue` 调用 Overview API，展示用户 Tokens 消耗与提问次数两类 TOP5。
  应用排行复用首页 `RankingCard`，由概览转换展示字段；占比使用当前应用同期完整排行总量。
  概览内暂时隐藏卡片详情入口，不接入排行抽屉、搜索、分页或导出。
- 触发器执行记录的执行时间列使用服务端排序，独立 `orderBy` 经 `toOrderBy` 添加 `ett.` 前缀，
  通过查询参数 `order` 传入。切换排序回第一页；搜索、分页和详情跨页保留排序，重新打开抽屉恢复默认排序。
- 触发器表单共用创建／编辑，保留任务 ID 和参数；资源模式固定单任务，完整输入定义不足时补查详情。
  保存校验全部折叠任务；参数初始化不覆盖已配置值，移除事件引用时恢复自定义默认值。
- 智能体／知识库对话用户页使用双栏布局和当前页授权；智能体从 context 取 Workspace／System 资源管理 ChatUser API，知识库取四范围 API。
  自动授权立即保存，手动保存只提交当前页；请求共用 loading 与 inert，失败保留勾选。
  授权人数取 `authorized_count`，不以分页勾选推算。
- 对话日志筛选、导出使用同组查询；无勾选导出筛选结果，日期清空禁用导出。
  清除策略通过当前范围 ChatLog API 保存、使用弹窗自身 loading；添加知识库固定所选对话 ID，选项使用当前范围 Knowledge／Document API。
  `ChatLogDetailDrawer` 使用现有 `LogConversation` 展示只读历史对话与执行详情，正文查询仍使用 Workspace API；上一条／下一条与跨页由页面管理。
- 外部检索页从 context 读取四范围 ExternalRetrieval API；Workspace 共享只读，禁用开关并阻止提交。
  查询失败展示重新加载入口，不展示默认开关；保存期间使用 loading 与 inert，失败保留已保存配置。
  知识库或资源范围变化时重新查询；示例与地址来自响应，只读展示／复制，不在前端拼接。
- 门户设置已通过 Portal API 持久化，JSON 保存开关、认证及 `cross_domain_list`，FormData 保存名称／Logo。
  成功以完整响应回显，保留现有编辑权限；认证选项来自 LoginSetting，跨域地址按行清理，取消不回写。
- 用户导入、改密、批量角色／配额流程留在各自业务目录；工作空间成员按用户联动角色行选择，
  删除按 `user_relation_id` 去重，不按用户 ID 丢弃角色记录。
- 登录页使用 `formEl.validate` 回调和清晰的 LDAP／本地分支，不额外抽象或改写提交控制流程。
- Chat／Portal 页面以 auth token 为面板 key，token 变化重建并加载用户档案；路由认证见路由文档。
  会话装配在 conversation-panel，列表 Store 不感知 Router；门户复用 chat 装配，保留各智能体最近会话分组。
  没有当前智能体时不查询其信息／会话、禁用输入，分组加载后选首个；无可用智能体显示空态。
  全部智能体与选择抽屉复用卡片，抽屉每次打开重新查询，搜索状态独立。
