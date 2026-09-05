# Router 目录说明

本文档是项目路由规则的唯一依据。新增、删除、移动或修改路由前，应先阅读本文档。

项目包含 Admin 和 Chat 两个独立入口，两者分别创建自己的 Router 实例，不共享路由表。

## 目录结构

```text
src/router/
├── ROUTE_README.md
├── admin/
│   ├── index.ts                 # Admin Router、拦截器、导航目录生成
│   ├── utils.ts                 # 导航目录等公共路由工具
│   ├── types.ts                 # RouteMeta 类型扩展
│   ├── login/
│   │   └── index.ts             # 登录等无框架页面
│   ├── workflow/
│   │   └── index.ts             # Workflow 全屏页面
│   ├── system/
│   │   ├── index.ts             # 系统管理路由汇总
│   │   └── modules/
│   │       ├── application.ts         # System 来源的智能体详情路由
│   │       └── knowledge.ts     # System 来源的知识库详情路由
│   └── workspace/
│       ├── index.ts             # 工作空间模块汇总
│       └── modules/
│           ├── home.ts          # 首页
│           ├── application.ts         # 智能体
│           ├── knowledge.ts     # 知识库
│           ├── tool.ts          # 工具
│           ├── model.ts         # 模型
│           └── trigger.ts       # 触发器
└── chat/
    ├── index.ts                 # Chat Router
    └── routes.ts                # Chat 路由表
```

## 路由分类

### Workspace

Workspace 使用 `AppLayout`，左侧导航根据 `scope: 'workspace'` 对应路由的 `children` 自动生成。

Workspace 根地址为 `/admin/workspace/:workspaceId`。`workspaceId` 只以当前路由参数为准。应用根
地址、登录成功和从 System 返回 Workspace 时统一进入 `/admin/workspace/default`。父路由的
`scope` 会合并到匹配的子路由 `meta` 中。

触发器列表地址为 `/admin/workspace/:workspaceId/trigger`，渲染 `views/trigger/TriggerView.vue`。

每个业务模块在 `admin/workspace/modules` 中独立维护。模块的列表、创建、详情、编辑等页面应放在同一个路由文件中。

### System

System 使用 `AppLayout`，左侧导航根据 `scope: 'system'` 对应路由的 `children` 自动生成。

System 根地址为 `/admin/system`，默认进入首页 `/admin/system/home`。需要复用 Workspace 详情页面时，在 System 路由树中注册独立路由名并复用同一个页面组件，以保留访问来源。

各子路由通过 `meta.resource` 向页面传入对应的后端资源类型。

复用路由按模块放在 `admin/system/modules`，文件名与 `admin/workspace/modules` 保持对应；`system/index.ts` 只负责系统导航路由和模块汇总。

有子目录时直接使用 Vue Router 的 `children`，路由层级就是导航层级，不需要额外的分组字段。

### Login 和 Workflow

Login、Workflow 路由没有挂载 `AppLayout`，因此不会出现在左侧导航中：

- `login`：登录及账户相关独立页面。
- `workflow`：集中维护各业务的全屏画布路由，当前包含智能体和工具工作流，后续知识库等画布
  继续在 `admin/workflow/index.ts` 中注册。
- Workspace 的全屏 Workflow 路由显式设置 `resourceScope: 'workspace'`，使模型创建等资源操作使用 Workspace API。
- Workflow 路由保留当前 Workspace 和资源标识；智能体工作流地址为
  `/workspace/:workspaceId/application/:applicationId/workflow`，工具工作流地址为
  `/workspace/:workspaceId/tool/:toolId/workflow`。两个页面均可从资源操作入口进入，按住 Ctrl 或
  Command 点击时在新标签页打开。

登录页面地址为 `/login`；忘记密码使用独立页面 `/forgot-password`，两者均复用登录布局且不挂载 `AppLayout`。

Admin 使用末尾 catch-all 路由 `not-found` 渲染 `views/error/NotFoundView.vue`。直接访问不存在的
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

Chat 使用独立入口 `src/chat.ts` 和独立 Router，不要把 Chat 路由加入 Admin 路由表。

## RouteMeta 字段

路由扩展字段定义在 `admin/types.ts`：

| 字段               | 类型                                                  | 说明                                                   |
| ------------------ | ----------------------------------------------------- | ------------------------------------------------------ |
| `scope`            | `'workspace' \| 'system'`                             | 标记生成哪一套框架导航，只配置在布局根路由上           |
| `resourceScope`    | `'workspace' \| 'system-resource' \| 'system-shared'` | 标记页面使用的资源范围，由对应资源父路由配置并向下继承 |
| `activeIcon`       | `string`                                              | 菜单激活状态的 iconfont Symbol ID                      |
| `activeMenu`       | `string`                                              | 进入子页面时需要保持激活的侧栏菜单路径                 |
| `detailActiveMenu` | `string`                                              | 更深层详情页面需要保持激活的二级菜单路由名称           |
| `title`            | `string`                                              | 页面标题，同时作为导航名称                             |
| `icon`             | `string`                                              | iconfont Symbol ID，子目录通常可以不配置               |
| `order`            | `number`                                              | 同级导航排序，数字越小越靠前                           |
| `hidden`           | `boolean`                                             | 设置为 `true` 时不显示在导航中                         |
| `resource`         | `ResourceAuthorizationType`                           | 系统资源授权页面当前管理的后端资源类型                 |

## 导航生成

`admin/utils.ts` 中的 `getChildRouteList(scope)` 会：

1. 根据 `scope` 找到 Workspace 或 System 根路由。
2. 读取根路由的 `children`。
3. 使用路由 `name` 作为导航项标识，并根据 `title`、`icon`、`activeIcon` 和 `order` 生成导航项。
4. 递归读取 `children` 生成子目录。
5. 排除没有名称、没有标题或设置了 `hidden: true` 的路由。

`WorkspaceSidebar` 和 `SystemSidebar` 分别调用该方法，不需要在页面组件中维护菜单数组。

资源详情页面统一使用 `ResourceDetailLayout`。`admin/utils.ts` 中的
`getMatchedChildRouteList(route)` 根据当前匹配路由找到所属详情父路由，并复用与
`getChildRouteList(scope)` 相同的过滤、排序和菜单字段转换逻辑生成二级导航。详情子路由通过
`title`、`icon`、`activeIcon` 和 `order` 配置二级菜单；更深层页面通过
`detailActiveMenu` 指定需要保持激活的二级菜单路由名称，不配置 `parentPath` 或 `parentName`。
`ResourceDetailLayout` 切换二级菜单时保留当前 query；详情容器返回列表时按业务来源状态透传或
重新生成 query。

路由导航图标统一使用 `src/assets/iconfont.js` 中的完整 Symbol ID 字符串，并由
`MkIcon` 的 `name` 属性渲染。需要在菜单激活后切换图标时，通过 `activeIcon` 配置激活状态
的 Symbol ID；未配置时继续使用 `icon`。Router 目录禁止导入或传入 Element Plus 图标组件。

System 侧栏默认使用当前页面的 `route.path` 匹配菜单激活项。Workspace 地址包含动态
`workspaceId`，其侧栏使用路由名称匹配；详情、创建和编辑等子页面需要继续高亮所属一级菜单
时，在一级父路由中把该菜单的路由名称配置为 `activeMenu`，由 Vue Router 合并到所有后代
路由的 `meta`。个别子页面需要激活其他菜单时，可在子路由中覆盖 `activeMenu`。Workspace
侧栏跳转必须携带当前路由的 `workspaceId`，不要拼接或写死工作空间路径。

## Scope 来源判断

Layout 对 Workspace、System 模式的判断统一维护在 `src/layout/utils.ts`：

```ts
import { isSystem, isWorkspace } from '@/layout/utils'
```

`scope` 来自 Vue Router 合并后的路由 `meta`。Workspace、System 子页面会分别继承根路由的 `workspace`、`system`。

`getChildRouteList` 属于公共路由工具，继续维护在 `admin/utils.ts`；仅供 Layout 使用的模式判断不要放入 Router。

路由对象是响应式的，不要在 setup 顶层解构 `route.meta.scope`，否则切换路由后 Scope 不会更新。需要响应路由变化时，应在 `computed` 中读取：

```ts
const route = useRoute()
const mode = computed(() => route.meta.scope ?? 'workspace')
```

## 资源范围判断

`application`、`knowledge`、`model`、`tool` 是需要跨资源范围维护的四类特殊资源。
`resourceScope` 只用于区分这四类资源在 Workspace、System 资源管理和 System 共享资源中的接口与
展示差异，不作为所有业务页面的通用模式字段。Workspace 在布局根路由配置 `workspace`；System
的“资源管理”和“共享资源”分别在对应父路由配置 `system-resource`、`system-shared`，子路由通过
Vue Router 的 meta 合并自动继承。

业务页面和组件统一使用 `src/utils/resource-context.ts` 中的 `isWorkspaceResource()`、
`isSystemResource()` 和 `isSystemSharedResource()` 判断当前资源范围，不根据 path 或路由名称重复
判断。非资源页面不配置 `resourceScope`。

`resourceScope` 负责表达当前路由语义，页面据此决定展示和选用哪个业务 API；卡片、Action、
Drawer、Dialog 不根据 path、路由名称或 Scope 自行维护 API 映射。

## 业务路由层级

Workspace 页面：

```text
/admin/workspace/:workspaceId/tools
/admin/workspace/:workspaceId/model

/admin/workspace/:workspaceId/tool/:toolId/workflow

/admin/workspace/:workspaceId/application
/admin/workspace/:workspaceId/application/:applicationId/workflow
/admin/workspace/:workspaceId/application/:applicationId/:type/overview
/admin/workspace/:workspaceId/application/:applicationId/:type/setting

/admin/workspace/:workspaceId/knowledge
/admin/workspace/:workspaceId/knowledge/:knowledgeId
/admin/workspace/:workspaceId/knowledge/:knowledgeId/document/:documentId
```

智能体详情路由的 `type` 来自当前 `ApplicationDetail.type`；卡片概览和简易智能体设置等详情入口
必须与 `applicationId` 一并传入该参数。高级智能体设置继续进入独立的 Workflow 路由。
智能体详情返回列表时，根据 `ApplicationDetail.folder` 通过可选的 `folderId` query 标记所属文件夹；
列表中的 `FolderTree` 初始化时读取该 query 并恢复选中项。用户在列表中切换文件夹时不写入新的
文件夹 ID，只清除已有的 `folderId`；进入详情时也不继续携带该 query。`folderId` 不作为详情 path
参数。

System 复用页面（仅替换根前缀）：

```text
/admin/system/application/:applicationId
/admin/system/application/:applicationId/edit

/admin/system/knowledge/:knowledgeId
/admin/system/knowledge/:knowledgeId/document/:documentId
```

两套详情路由使用不同的路由名称并复用相同页面组件。除 `/workspace`、`/system` 根前缀外，后续模块路径保持一致。

System 共享资源页面：

```text
/admin/system/share/knowledge
/admin/system/share/models
/admin/system/share/tools
```

共享资源路由是 System 导航的一部分，继续在 `admin/system/index.ts` 的 `share` 子路由中维护。
已实现的共享资源页面放在 `views/system/shared-resources/`，由页面处理 System 范围的查询和操作，
可按需复用 Workspace 对应资源的卡片等展示组件。

## 一级导航示例

```ts
{
  path: 'settings',
  name: 'system-settings',
  component: () => import('@/views/system/SystemView.vue'),
  meta: {
    title: '系统设置',
    icon: 'icon_setting_outlined',
    order: 60,
  },
}
```

## 子目录示例

```ts
{
  path: 'identity',
  name: 'system-identity',
  redirect: { name: 'system-users' },
  meta: {
    title: '身份与权限',
    icon: 'icon_user_outlined',
    order: 10,
  },
  children: [
    {
      path: 'users',
      name: 'system-users',
      component: () => import('@/views/system/identity/users/UserListView.vue'),
      meta: {
        title: '用户管理',
        order: 10,
      },
    },
  ],
}
```

对应地址为 `/admin/system/identity/users`。

## 不显示在导航中的页面

详情、创建、编辑等页面仍可以放在对应模块的路由树中，通过 `hidden` 隐藏：

```ts
{
  path: 'users/:id/edit',
  name: 'system-user-edit',
  component: () => import('@/views/system/UserEditView.vue'),
  meta: {
    title: '编辑用户',
    hidden: true,
  },
}
```

使用 `ResourceDetailLayout` 的详情路由只在详情父路由配置 `hidden: true`；需要显示在二级导航中的
直接子路由继续配置 `title`、`icon` 和 `order`，不要再配置 `hidden: true`。一级导航生成时会排除
整个详情父路由，详情布局则读取该父路由的直接子路由生成自己的二级导航。

## 新增路由约定

- 每条路由必须使用全局唯一的 `name`。
- 导航页面配置 `title` 和 `order`。
- 详情、创建、编辑页面配置 `hidden: true`。
- 有真实层级关系时使用 `children`，不要自行增加菜单分组字段。
- Workspace 新模块需要在 `workspace/index.ts` 中汇总。
- System 复用 Workspace 页面时，在 `system/modules` 中创建对应模块文件并由 `system/index.ts` 汇总。
- Login、Workflow 等全屏页面不要挂载 `AppLayout`。
- Admin 与 Chat 路由不要相互引用。
- 每次新增、删除、移动或修改路由时，必须同步更新本文件。
