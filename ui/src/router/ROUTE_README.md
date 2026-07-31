# Router 目录说明

本文档是项目路由规则的唯一依据。新增、删除、移动或修改路由前，应先阅读本文档。

项目包含 Admin 和 Chat 两个独立入口，两者分别创建自己的 Router 实例，不共享路由表。

## 目录结构

```text
src/router/
├── ROUTE_README.md
├── admin/
│   ├── index.ts                 # Admin Router、拦截器、导航目录生成
│   ├── utils.ts                 # Scope、导航目录等公共路由工具
│   ├── types.ts                 # RouteMeta 类型扩展
│   ├── login/
│   │   └── index.ts             # 登录等无框架页面
│   ├── workflow/
│   │   └── index.ts             # Workflow 全屏页面
│   ├── system/
│   │   ├── index.ts             # 系统管理路由汇总
│   │   └── modules/
│   │       ├── agent.ts         # System 来源的智能体详情路由
│   │       └── knowledge.ts     # System 来源的知识库详情路由
│   └── workspace/
│       ├── index.ts             # 工作空间模块汇总
│       └── modules/
│           ├── home.ts          # 首页
│           ├── agent.ts         # 智能体
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

Workspace 根地址为 `/admin/workspace`。父路由的 `scope` 会合并到匹配的子路由 `meta` 中。

每个业务模块在 `admin/workspace/modules` 中独立维护。模块的列表、创建、详情、编辑等页面应放在同一个路由文件中。

### System

System 使用 `AppLayout`，左侧导航根据 `scope: 'system'` 对应路由的 `children` 自动生成。

System 根地址为 `/admin/system`。需要复用 Workspace 详情页面时，在 System 路由树中注册独立路由名并复用同一个页面组件，以保留访问来源。

系统外观设置页面地址为 `/admin/system/settings/appearance`，使用
`views/system/settings/AppearanceSettingsView.vue`，并复用 `views/login/components`
中的登录外观组件进行实时主题预览。

复用路由按模块放在 `admin/system/modules`，文件名与 `admin/workspace/modules` 保持对应；`system/index.ts` 只负责系统导航路由和模块汇总。

有子目录时直接使用 Vue Router 的 `children`，路由层级就是导航层级，不需要额外的分组字段。

### Login 和 Workflow

Login、Workflow 路由没有挂载 `AppLayout`，因此不会出现在左侧导航中：

- `login`：登录及账户相关独立页面。
- `workflow`：工作流编排等全屏页面。

登录页面地址为 `/login`；忘记密码使用独立页面 `/forgot-password`，两者均复用登录布局且不挂载 `AppLayout`。

### Chat

Chat 使用独立入口 `src/chat.ts` 和独立 Router，不要把 Chat 路由加入 Admin 路由表。

## RouteMeta 字段

路由扩展字段定义在 `admin/types.ts`：

| 字段         | 类型                      | 说明                                         |
| ------------ | ------------------------- | -------------------------------------------- |
| `scope`      | `'workspace' \| 'system'` | 标记生成哪一套框架导航，只配置在布局根路由上 |
| `activeIcon` | `string`                  | 菜单激活状态的 iconfont Symbol ID            |
| `activeMenu` | `string`                  | 进入子页面时需要保持激活的侧栏菜单路径       |
| `title`      | `string`                  | 页面标题，同时作为导航名称                   |
| `icon`       | `string`                  | iconfont Symbol ID，子目录通常可以不配置     |
| `order`      | `number`                  | 同级导航排序，数字越小越靠前                 |
| `hidden`     | `boolean`                 | 设置为 `true` 时不显示在导航中               |

## 导航生成

`admin/utils.ts` 中的 `getChildRouteList(scope)` 会：

1. 根据 `scope` 找到 Workspace 或 System 根路由。
2. 读取根路由的 `children`。
3. 使用路由 `name` 作为导航项标识，并根据 `title`、`icon`、`activeIcon` 和 `order` 生成导航项。
4. 递归读取 `children` 生成子目录。
5. 排除没有名称、没有标题或设置了 `hidden: true` 的路由。

`WorkspaceSidebar` 和 `SystemSidebar` 分别调用该方法，不需要在页面组件中维护菜单数组。

路由导航图标统一使用 `src/assets/iconfont.js` 中的完整 Symbol ID 字符串，并由
`MkIcon` 的 `name` 属性渲染。需要在菜单激活后切换图标时，通过 `activeIcon` 配置激活状态
的 Symbol ID；未配置时继续使用 `icon`。Router 目录禁止导入或传入 Element Plus 图标组件。

侧栏默认使用当前页面的 `route.path` 匹配菜单激活项。详情、创建和编辑等子页面需要继续高亮
所属一级菜单时，在一级父路由中配置该菜单的绝对路径 `activeMenu`，由 Vue Router 合并到
所有后代路由的 `meta`。侧栏统一使用 `route.meta.activeMenu ?? route.path` 进行匹配，不在
组件中截取 URL 或回溯路由层级。个别子页面需要激活其他菜单时，可在子路由中覆盖
`activeMenu`。

## Scope 来源判断

页面不要重复判断 `route.meta.scope`，统一使用 `admin/utils.ts`：

```ts
import { isSystem, isWorkspace } from '@/router/admin/utils'
```

`scope` 来自 Vue Router 合并后的路由 `meta`。Workspace、System 子页面会分别继承根路由的 `workspace`、`system`。

`getRouteScope`、`useRouteScope` 和 `getChildRouteList` 都属于公共路由工具，统一维护在 `admin/utils.ts`，并通过 `@/router/admin` 对外导出。

路由对象是响应式的，不要在 setup 顶层解构 `route.meta.scope`，否则切换路由后 Scope 不会更新。需要响应路由变化时，应在 `computed` 中读取：

```ts
const route = useRoute()
const mode = computed(() => route.meta.scope ?? 'workspace')
```

## Agent 和 Knowledge 路由层级

Workspace 页面：

```text
/admin/workspace/agent
/admin/workspace/agent/:agentId
/admin/workspace/agent/:agentId/edit

/admin/workspace/knowledge
/admin/workspace/knowledge/:knowledgeId
/admin/workspace/knowledge/:knowledgeId/document/:documentId
```

System 复用页面（仅替换根前缀）：

```text
/admin/system/agent/:agentId
/admin/system/agent/:agentId/edit

/admin/system/knowledge/:knowledgeId
/admin/system/knowledge/:knowledgeId/document/:documentId
```

两套详情路由使用不同的路由名称并复用相同页面组件。除 `/workspace`、`/system` 根前缀外，后续模块路径保持一致。页面通过 `isSystem`、`isWorkspace` 处理返回地址、权限和操作差异。

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
