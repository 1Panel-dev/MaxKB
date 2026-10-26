# Router 目录说明

本文档是项目路由规则的唯一依据。新增、删除、移动或修改路由前，应先阅读本文档。

项目包含 Admin 和 Chat 两个独立入口，两者分别创建自己的 Router 实例，不共享路由表。

## 目录职责

- `admin/index.ts`：Router、导航初始化与认证；`types.ts`：RouteMeta；`utils.ts`：导航生成。
- `admin/workspace/modules/`：按业务维护工作空间路由，`workspace/index.ts` 汇总。
- `admin/system/modules/`：System 复用页面；`system/index.ts`：系统导航及汇总。
- `admin/login/`、`admin/workflow/`：无 AppLayout 的登录和全屏画布路由。
- `chat/index.ts`、`chat/routes.ts`：独立认证守卫和单应用／门户路由。

## 路由分类

### Workspace

Workspace 使用 `AppLayout`，左侧导航根据 `scope: 'workspace'` 对应路由的 `children` 自动生成。

Workspace 根地址为 `/admin/workspace/:workspaceId`。`workspaceId` 只以当前路由参数为准。应用根
地址、登录成功和从 System 返回 Workspace 时统一进入 `/admin/workspace/default`；若当前用户
只属于 `workspace_list` 中的部分工作空间且目标 `workspaceId` 不在其中，路由守卫会自动重定向到
其首个可访问工作空间（仅对携带 `workspaceId` 参数的工作空间路由生效）。父路由的 `scope`
会合并到匹配的子路由 `meta` 中。

顶部工作空间切换统一由 `layout/header-workspace-dropdown/index.vue` 处理：选择不同工作空间时，
通过 `router.resolve()` 生成目标地址，再调用 `window.location.assign()` 整页加载，重新初始化
用户资料、权限和页面状态。智能体详情及其子页切换后进入目标工作空间的智能体列表；普通或共享
知识库详情及其子页切换后进入目标工作空间的知识库列表，不携带原详情的资源参数、query 或 hash。
其他页面保留当前路由名称、其他参数、query 和 hash；选择当前工作空间不刷新。
不要改为仅 `router.push()` 或依赖组件 `key` 重建来替代整页加载。

触发器列表地址为 `/admin/workspace/:workspaceId/trigger`，渲染 `views/trigger/index.vue`。

每个业务模块在 `admin/workspace/modules` 中独立维护。模块的列表、创建、详情、编辑等页面默认放在同一个路由文件中；较长的模块可按资源范围拆分。知识库的共享详情维护在 `knowledge-shared.ts`，由 `workspace/index.ts` 与 `knowledgeRoutes` 并列汇总，两个模块共同继承 Workspace 布局；共享详情显式配置资源范围和激活菜单。

### System

System 使用 `AppLayout`，左侧导航根据 `scope: 'system'` 对应路由的 `children` 自动生成。
系统侧栏在进入资源详情页（`resourceDetailRoot`）时默认收起，其他页面默认展开；小屏默认收起。
列表和详情页均保留系统侧栏，并支持手动切换；详情子页之间切换保留当前展开状态。

System 根地址为 `/admin/system`，默认进入首页 `/admin/system/home`。需要复用 Workspace 详情页面时使用独立路由名保留访问来源。System 知识库详情在 `system/index.ts` 的 children 注册，
继承 System 的 AppLayout，在主区展示详情目录和内容区。

对话端管理根地址为 `/admin/system/chat-management`（`system-chat-management`），默认进入
`users`（`system-chat-users`）。子路由还包括 `groups`
（`system-chat-groups`）、`authentication`（`system-chat-authentication`）
和 `portal-setting`（`system-portal-setting`），页面组件统一位于 `views/system/chat-management/`。
门户访问设置渲染 `views/system/chat-management/portal-setting/index.vue`，提供门户访问
配置和右侧界面预览。

各子路由通过 `meta.resource` 向页面传入对应的后端资源类型。

复用路由按模块放在 `admin/system/modules`，文件名与 `admin/workspace/modules` 保持对应；`system/index.ts` 只负责系统导航路由和模块汇总。

有子目录时直接使用 Vue Router 的 `children`，路由层级就是导航层级，不需要额外的分组字段。

### Login 和 Workflow

Login、Workflow 路由没有挂载 `AppLayout`，因此不会出现在左侧导航中：

- `login`：登录及账户相关独立页面。
- `workflow`：集中维护各业务的全屏画布路由，当前包含智能体、工具和知识库工作流，后续其他画布
  继续在 `admin/workflow/index.ts` 中注册。
- Workspace 的全屏 Workflow 路由显式设置 `resourceScope: 'workspace'`，使模型创建等资源操作使用 Workspace API。
- Workflow 路由保留当前 Workspace 和资源标识；智能体工作流地址为
  `/workspace/:workspaceId/application/:applicationId/workflow`，工具工作流地址为
  `/workspace/:workspaceId/tool/:toolId/workflow`。两个页面均可从资源操作入口进入，按住 Ctrl 或
  Command 点击时在新标签页打开。知识库工作流路由名为 `workflow-knowledge`，地址为
  `/workspace/:workspaceId/knowledge/:knowledgeId/workflow`。

登录页面地址为 `/login`；忘记密码使用独立页面 `/forgot-password`，两者均复用登录布局且不挂载 `AppLayout`。

Admin 使用末尾 catch-all 路由 `not-found` 渲染 `views/error/index.vue`。直接访问不存在的
页面或 Admin API 返回需要全局处理的 404 时，统一进入该页面。

## Admin 导航拦截器

Admin Router 在 `admin/index.ts` 中统一处理导航初始化：

1. 路由 path 变化时调用 `NProgress.start()`；同一路径只更新 query 或 hash 时不启动顶部进度条。
   导航完成或发生路由错误时调用 `NProgress.done()`；统一关闭 Spinner，视觉样式由
   `styles/nprogress.scss` 维护。
2. `login`、`forgot-password`、`not-found` 为公开路由，不校验登录状态。
3. URL 查询参数包含 `token` 时，先写入 Admin 认证 Store，用于外部认证回跳，然后使用替换
   导航清理地址栏中的 token。
4. 访问非公开路由且没有 token 时跳转到 `login`，并通过 `redirect` 查询参数保留原地址。
5. token 有效但当前用户尚未加载时，统一加载平台基础档案和当前用户；专业版或
   企业版同时加载服务端外观主题，其他版本恢复默认主题，使刷新页面也能恢复版本、用户和
   外观状态。
6. 登录态档案加载失败时清除登录状态并返回登录页。
7. 导航完成后根据 `route.meta.title` 更新浏览器标题。

### Chat

Chat 使用独立入口 `src/chat.ts` 和独立 Router，不要把 Chat 路由加入 Admin 路由表。门户与单应用对话
共用这一个入口，门户部署在 `/chat/portal/` 下。

门户路由统一放在 `/portal` 下并配置 `meta.portal: true`：`portal-home`（`/portal`）、
`portal-login`（`/portal/login`）、`portal-application-list`（`/portal/applications`，全部智能体）、
`portal-application`（`/portal/a/:applicationId`，新建对话）、
`portal-application-chat`（`/portal/a/:applicationId/c/:chatId`），
`portal-home`、`portal-application-list`、`portal-application`、`portal-application-chat` 共用门户对话页 `views/portal/index.vue`，
访问 `portal-home` 时由页面在分组加载后进入第一个智能体的新建对话。`portal-login` 与 `chat-login` 共用 `views/chat/login/index.vue`，页面按 Store
当前认证场景显示门户或应用名称，并使用对应场景登录。不要把门户页面放到 `/login` 等一级路径，否则会与 `/:accessToken/` 冲突。

单应用对话路由以 `/:accessToken/` 开头，兼容 v2 对话地址：`chat-home`（`/:accessToken/`）、
`chat-home-detail`（`/:accessToken/c/:chatId`）和 `chat-login`（`/:accessToken/login`）。
静态段 `/portal` 优先于动态参数匹配；后端生成的 accessToken 为 16 位十六进制字符串，不会等于 `portal`。

根路径 `/` 重定向到 `portal-home`；匹配不到的地址由末尾 catch-all 路由 `chat-not-found` 渲染
`views/chat/error/index.vue`，保留原地址。Router base 优先读取 `window.MaxKB.prefix`（后端按 `CHAT_PATH`
替换），再回退到 `VITE_BASE_PATH`。

认证场景（scope）由路由决定：门户路由为 `PORTAL_AUTH_SCOPE`，单应用路由为其 accessToken。
Chat 导航守卫（`chat/index.ts`）：

1. `/portal` 下未定义的子路径会被单应用路由匹配为 `accessToken = 'portal'`，重定向到 `portal-home`。
2. 获取目标场景的认证前置配置（`AuthProfile`），与当前场景相同时复用。accessToken 无效、应用已停用或门户
   未开放导致获取失败时，进入 `chat-not-found` 并保留原地址；匿名认证失败时同样处理。
3. 判断时只读取目标场景在本地存储中的 token，不切换 Store 的当前场景。
4. 进入登录页或已有 token 时，调用 `auth.activate()` 切换当前场景后放行。
5. `enable_auth` 为 false 时获取匿名 token，切换当前场景后放行。匿名认证与登录都携带该场景本地保存的
   token，后端据此沿用同一对话用户。401 时 token 只在 Store 中清除并标记为失效，本地存储保留以便
   重新认证时携带；退出登录才从本地存储删除。
6. 否则跳转到对应登录页（`portal-login` 或 `chat-login`），并通过 `redirect` 查询参数保留原地址。

当前场景只在放行前切换，请求层直接读取 `auth.token`，导航未完成时不会带上目标场景的 token。

接口返回 401（`/auth/` 认证接口除外）时，请求层调用 `reauthenticate()`：将当前场景的 token 标记为失效（Store 中清除，本地存储保留），并以
`force: true` 重新导航到当前地址，由守卫重新匿名认证或跳转登录页。同一时间只处理一次。

## RouteMeta 字段

路由扩展字段定义在 `admin/types.ts`：

| 字段                 | 类型                                                                        | 说明                                                                      |
| -------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `scope`              | `'workspace' \| 'system'`                                                   | 标记生成哪一套框架导航，只配置在布局根路由上                              |
| `resourceScope`      | `'workspace' \| 'workspace-shared' \| 'system-resource' \| 'system-shared'` | 标记页面使用的资源范围，由对应资源父路由配置并向下继承                    |
| `activeIcon`         | `string`                                                                    | 菜单激活状态的 iconfont Symbol ID                                         |
| `activeMenu`         | `string`                                                                    | 进入子页面时需要保持激活的侧栏菜单标识（Workspace 为名称，System 为路径） |
| `resourceDetailRoot` | `boolean`                                                                   | 标记资源详情根，详情容器和独立文档分段页配置，用于目录与工作空间切换      |
| `detailActiveMenu`   | `string`                                                                    | 更深层详情页面需要保持激活的二级菜单路由名称                              |
| `title`              | `string`                                                                    | 页面标题，同时作为导航名称                                                |
| `icon`               | `string`                                                                    | iconfont Symbol ID，子目录通常可以不配置                                  |
| `order`              | `number`                                                                    | 同级导航排序，数字越小越靠前                                              |
| `hidden`             | `boolean`                                                                   | 设置为 `true` 时不显示在导航中                                            |
| `detailMenuVisible`  | `(params) => boolean`                                                       | 按业务类型过滤详情菜单，不用于权限                                        |
| `canAccess`          | `(params) => boolean`                                                       | 工作流返回详情时的访问判断                                                |
| `resource`           | `ResourceAuthorizationType`                                                 | 系统资源授权页面当前管理的后端资源类型                                    |

Workspace 和 System 资源知识库的详情子路由使用现有 `meta.permission` 访问判断；二级菜单应用相同判断并隐藏空分组。
Workspace 根据目标路由中的 workspaceId、knowledgeId 判断权限，权限回退保留目标参数、query 和 hash。
`detailMenuVisible` 继续只处理知识库类型。进入详情时优先选择有查看权限的子页，缺少文档权限时不会固定落到文档页。

## 导航生成

`admin/utils.ts` 中的 `getChildRouteList(scope)` 会：

1. 根据 `scope` 找到 Workspace 或 System 根路由。
2. 读取根路由的 `children`。
3. 使用路由 `name` 作为导航项标识，并根据 `title`、`icon`、`activeIcon` 和 `order` 生成导航项。
4. 递归读取 `children` 生成子目录。
5. 排除没有名称、没有标题或设置了 `hidden: true` 的路由。

一级业务入口即使只有隐藏的列表、详情子路由也保留；隐藏空分组仅适用于详情目录，避免移除知识库、智能体等入口。

`WorkspaceSidebar` 和 `SystemSidebar` 分别调用该方法，不需要在页面组件中维护菜单数组。

资源详情页面统一使用 `ResourceDetailLayout`。`admin/utils.ts` 中的
`getMatchedChildRouteList(route)` 从 `route.matched` 的记录自身 meta 中查找 `resourceDetailRoot: true`，定位详情父路由，并复用与
`getChildRouteList(scope)` 相同的过滤、排序和菜单字段转换逻辑生成二级导航。详情菜单支持一级入口与二级折叠分组混排，分组直接使用路由 `children`。详情子路由通过
`title`、`icon`、`activeIcon` 和 `order` 配置二级菜单；更深层页面通过
`detailActiveMenu` 指定需要保持激活的二级菜单路由名称，不配置 `parentPath` 或 `parentName`。
`ResourceDetailLayout` 切换二级菜单时保留当前 query；详情容器返回列表时按业务来源状态透传或
重新生成 query。

路由导航图标统一使用 `src/assets/iconfont.js` 中的完整 Symbol ID 字符串，并由
`MkIcon` 的 `name` 属性渲染。需要在菜单激活后切换图标时，通过 `activeIcon` 配置激活状态
的 Symbol ID；未配置时继续使用 `icon`。Router 目录禁止导入或传入 Element Plus 图标组件。

System 侧栏优先使用 `route.meta.activeMenu`，未配置时使用当前页面的 `route.path` 匹配菜单激活项。
资源授权父路由配置 `activeMenu: '/system/identity/authorization'`，各资源类型子页面继承该配置，
直接访问或刷新时保持“资源授权”菜单激活。Workspace 地址包含动态
`workspaceId`，其侧栏使用路由名称匹配；详情、创建和编辑等子页面需要继续高亮所属一级菜单
时，在一级父路由中把该菜单的路由名称配置为 `activeMenu`，由 Vue Router 合并到所有后代
路由的 `meta`。个别子页面需要激活其他菜单时，可在子路由中覆盖 `activeMenu`。Workspace
侧栏跳转必须携带当前路由的 `workspaceId`，不要拼接或写死工作空间路径。

## Scope 来源判断

Layout 对 Workspace、System 模式的判断统一维护在 `src/layout/utils.ts`：

`scope` 来自 Vue Router 合并后的路由 `meta`。Workspace、System 子页面会分别继承根路由的 `workspace`、`system`。

`getChildRouteList` 属于公共路由工具，继续维护在 `admin/utils.ts`；仅供 Layout 使用的模式判断不要放入 Router。

路由对象是响应式的，不要在 setup 顶层解构 `route.meta.scope`，否则切换路由后 Scope 不会更新。需要响应路由变化时，应在 `computed` 中读取：

## 资源范围判断

`application`、`knowledge`、`model`、`tool` 是需要跨资源范围维护的四类特殊资源。
`resourceScope` 只用于区分这四类资源在 Workspace 普通资源、Workspace 共享资源、System 资源管理和 System 共享资源中的接口与
展示差异，不作为所有业务页面的通用模式字段。Workspace 在布局根路由配置 `workspace`；System
的“资源管理”和“共享资源”分别在对应父路由配置 `system-resource`、`system-shared`，子路由通过
Vue Router 的 meta 合并自动继承。Workspace 共享详情父路由覆盖为 `workspace-shared`，布局 `scope` 仍为 `workspace`。

业务页面和组件统一使用 `src/utils/resource-context.ts` 中的 `isWorkspaceResource()`、
`isWorkspaceSharedResource()`、`isSystemResource()` 和 `isSystemSharedResource()` 判断当前资源范围，不根据 path 或路由名称重复
判断。非资源页面不配置 `resourceScope`。

`resourceScope` 负责表达当前路由语义，页面据此决定展示和选用哪个业务 API；卡片、Action、
Drawer、Dialog 通常不根据 path、路由名称或 Scope 自行维护 API 映射。
资源授权抽屉 `ResourceAuthorizationDrawer` 例外：由抽屉入口通过 `isSystemResource()`
选择 System 资源管理或 Workspace 用户授权接口，再传给标签子组件。

## 新增与维护

- 路由 name 全局唯一；导航页配置 title、order；详情／创建／编辑父页使用 hidden。
  详情二级菜单需要展示的子页保留 title、icon、order，不再隐藏。
- 层级直接用 children，不增加菜单分组字段。新增 Workspace 模块由 workspace/index.ts 汇总；
  System 复用路由按模块汇总。Admin 和 Chat 不相互引用。
- View 路径、功能登记见 [VIEW_README.md](../views/VIEW_README.md)，不在本文登记业务交互。
- 路由变化更新所属配置及本文的导航规则，不复制完整路由树或记录迁移过程。

## 资源详情与工作流导航

### 知识库

四种来源独立维护 children，不使用共享子路由生成函数；复用相同 View，菜单顺序和类型条件一致。
以下路径相对 Admin base，普通 Workspace 和 System 资源管理详情优先进入有查看权限的页面，共享详情默认进入 `/document`。

| 来源            | 详情路径                                                      | 详情父路由名                        | 全屏工作流名                          |
| --------------- | ------------------------------------------------------------- | ----------------------------------- | ------------------------------------- |
| Workspace       | `/workspace/:workspaceId/knowledge/:knowledgeId/:type`        | `workspace-knowledge-detail`        | `workflow-knowledge`                  |
| Workspace 共享  | `/workspace/:workspaceId/shared/knowledge/:knowledgeId/:type` | `workspace-shared-knowledge-detail` | `workspace-shared-workflow-knowledge` |
| System 资源管理 | `/system/resource/knowledge/:knowledgeId/:type`               | `system-resource-knowledge-detail`  | `system-resource-workflow-knowledge`  |
| System 共享     | `/system/shared/knowledge/:knowledgeId/:type`                 | `system-shared-knowledge-detail`    | `system-shared-workflow-knowledge`    |

`type` 由 KNOWLEDGE_TYPE_MAP 转为 BASE／WEB／LARK／WORKFLOW，地址不使用数字枚举；
创建、卡片、设置及返回详情均传 knowledgeId 和字符串类型。全屏工作流不含 type，路径在各来源
知识库 ID 后追加 `/workflow`。System 地址不携带 workspaceId，shared 使用统一前缀，不保留 share 别名。

详情父页配置 hidden、resourceDetailRoot；hidden 仅影响导航菜单，详情页仍保留 AppLayout 的
应用侧栏、头部和详情目录。
Workspace 共享覆盖 resourceScope，保留 Workspace scope 及知识库 activeMenu。

| 菜单       | 路径与条件                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------------- |
| 资料库     | 空 path 分组；document、image、tag；仅 BASE 显示图片                                                                  |
| 工作流     | workflow-entry；WORKFLOW 类型 beforeEnter 重定向对应全屏画布，其他类型显示转换页                                      |
| 检索优化   | retrieval/hit-test、retrieval/question、retrieval/dictionary                                                          |
| 授权与集成 | integration/chat-user、integration/external-retrieval                                                                 |
| 设置       | BASE 单独 setting；WEB 分组含 setting/base、document-strategy、scheduled-sync；LARK／WORKFLOW 含 base、scheduled-sync |

分组不挂 View，直接访问重定向首个子页，保留参数、query、hash。
设置只用 detailMenuVisible 控制菜单类型，不添加类型访问守卫。资料库 View 的目录是 library/tags，URL 仍为 tag。

分段地址在各来源详情后追加 `/document/:documentId`，路由名为 `<resourceScope>-knowledge-paragraph`。
与详情容器同级挂载，使用自身分段目录；配置 hidden 和 resourceDetailRoot，返回对应文档列表并保留 query。
全屏画布直接访问时检查真实知识库类型，非工作流返回转换页；返回导航集中在 workflow/knowledge/navigation.ts。
菜单与路由存在不代表该范围全部 API 已支持，真实接口边界见 API 文档。

### 智能体

Workspace 详情父路由为 workspace-application-detail-layout，详情参数包含 applicationId 与 ApplicationDetail.type。
System 资源管理详情为 `/system/resource/application/:applicationId/:type`，父路由名为
`system-resource-application-detail-layout`，默认进入 `system-resource-application-overview`。
配置集中在 `admin/system/modules/application-system-resource.ts`，由 System 路由汇总接入。
两种范围独立维护 children，复用 `application-detail` 页面；System 保留系统侧栏，不携带 workspaceId，
不提供 Workspace 共享或 System 共享的智能体详情。System 列表点击名称进入详情。
菜单为概览、设置、发布渠道、对话用户、对话日志；SIMPLE 的 setting 与高级 workflow-entry 互斥显示。
发布渠道使用 access 路径、workspace-application-access 路由名，对应 application-detail/access 页面。
高级设置重定向 workflow-application，保留 workspaceId、applicationId 和 query。
System 高级设置重定向 `system-resource-workflow-application`，地址为
`/system/resource/application/:applicationId/workflow`，保留 applicationId 和 query。
对话日志保留 operation-log 路径和 workspace-application-operation-log 名称。

workflow/application/navigation.ts 按详情子路由 order 查找首个有名称、标题、未隐藏且 canAccess 允许的页面。
未配置 canAccess 默认允许；它仅用于返回导航，不替代守卫或后端鉴权。
概览使用 overviewRead，简易设置要求 SIMPLE 与编辑权限，高级设置 canAccess 为 false，避免返回画布。
无可访问详情时返回对应列表，不在导航函数硬编码子页分支。

### 工具

Workspace 工作流为 `/workspace/:workspaceId/tool/:toolId/workflow`；System 两种入口为
`/system/resource/tool/:toolId/workflow` 和 `/system/shared/tool/:toolId/workflow`，
名称分别 system-resource-workflow-tool、system-shared-workflow-tool，统一复用 ToolWorkflowView。
工具／模型范围由各路由的 resourceScope 传递；System 不传路由工作空间。
返回导航集中在 workflow/tool/navigation.ts，Workspace 带可选 folderId，System 返回各自工具列表。

### 文件夹恢复

详情返回列表用资源 folder 写入 folderId query；FolderTree 初始化恢复，切换文件夹只清除旧 query，
不写新的文件夹 ID，进入详情不携带它。Workspace 共享知识库返回 folderId: shared。
该参数不进入详情 path。
