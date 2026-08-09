# views 目录说明

本文档是页面职责和页面功能代码组织规则的唯一依据。新增、移动、删除页面，改变页面职责，或
调整页面专用代码的位置前，应先阅读并同步更新本文档。

## 放置规则

- `views/<feature>/` 是页面功能边界。路由级页面、该功能专用组件、常量、组合式函数和
  其他业务逻辑应放在同一个功能目录或其子目录中。
- 路由级 Vue 组件使用 `PascalCase` 并以 `View.vue` 结尾，例如 `UserListView.vue`。
- 仅供一个页面使用的代码放在该页面旁边；同一功能下多个页面复用的代码放在它们最近的共同
  功能目录中。
- 页面专用组件放在所属功能的 `components/` 中。不要为了复用一个页面内部实现而提前移动到
  `src/components`。
- 页面类型的归属和复用遵循 `src/api/API_README.md`；API 与页面共用的业务类型从
  `@/api/types` 导入。页面常量可使用 `constants.ts`；其他逻辑文件应按具体职责命名，避免
  `helpers.ts` 等含义模糊的名称。
- 只有代码确实跨多个功能复用时，才按对应专项规则上移到 `src/components`、`src/constants`、
  `src/utils`、`src/stores` 或 `src/api`。
- 页面目录存在多个层级时，目录名应表达业务层级，例如
  `system/identity/groups/UserGroupListView.vue`，不要创建无业务含义的分组目录。
- 页面脚本中的状态、计算属性和处理方法按照同一业务流程集中放置，并使用简短的业务备注划分
  列表查询、批量操作等流程。流程较长的函数应在确认、请求、刷新等关键阶段添加说明，重点解释
  Promise 返回、执行顺序和业务约束，不为含义明确的单行代码逐句添加注释。

参考结构：

```text
src/views/<feature>/
├── FeatureListView.vue       # 路由级列表页面
├── FeatureDetailView.vue     # 路由级详情页面
├── components/               # 仅供该功能使用的组件
├── constants.ts              # 仅供该功能使用的常量
```

不需要为了匹配示例创建空目录；有对应代码时再创建。

## 页面功能登记

| 页面                                               | 功能说明                        |
| -------------------------------------------------- | ------------------------------- |
| `agent/AgentDetailView.vue`                        | 智能体详情页面                  |
| `chat/ChatView.vue`                                | Chat 入口的对话页面             |
| `error/NotFoundView.vue`                           | Admin 未匹配路由和全局 404 页面 |
| `home/HomeView.vue`                                | Workspace 首页                  |
| `knowledge/KnowledgeDetailView.vue`                | 知识库详情页面                  |
| `knowledge/DocumentDetailView.vue`                 | 知识库文档详情页面              |
| `login/LoginView.vue`                              | Admin 登录页面                  |
| `login/ForgotPasswordView.vue`                     | 忘记密码页面                    |
| `system/SystemView.vue`                            | System 模块通用占位页面         |
| `system/identity/groups/UserGroupListView.vue`     | 用户组列表页面                  |
| `system/identity/roles/RoleListView.vue`           | 角色列表页面                    |
| `system/identity/users/UserListView.vue`           | 用户列表页面                    |
| `system/identity/workspaces/WorkspaceListView.vue` | 工作空间列表页面                |
| `system/settings/AppearanceSettingsView.vue`       | 系统外观设置和登录外观预览页面  |
| `workflow/WorkflowView.vue`                        | 工作流编排全屏页面              |

## 备注要求

- 新增路由级页面时，必须在“页面功能登记”中添加一条简洁、明确的功能说明。
- 页面职责改变、文件重命名或目录移动时，必须同步修改登记内容。
- 对职责不直观的页面专用 TypeScript 文件，在文件顶部用一句话说明负责的业务领域和用途。
- 注释说明“为什么”和业务约束，不重复描述能够从文件名、类型或代码直接看出的内容。

## 登录页实现约定

- Element Plus 登录表单通过 `formEl.validate((valid, fields) => {})` 回调处理校验结果。
- LDAP 与本地账号登录保留清晰的条件分支，请求结果使用 `.then().catch()` 处理；未经明确要求，
  不改写为 `try/catch` 或额外抽象登录提交流程。
