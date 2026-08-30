/**
 * 按钮权限判定助手 —— 业务层（modules/*）只依赖这三个函数。
 *
 * 约定（对应三种场景）：
 *  - can    → 工作空间级、无资源 id（如「新建」）
 *  - canRes → 工作空间级、按资源 id（如「编辑某个应用」）
 *  - canSys → 系统级（系统资源管理 / 共享页），全局判定、无资源 id
 *
 * 复杂/特殊按钮可绕过这里，直接用 core 的 hasPermission + 常量自行组合。
 */

import { hasPermission, buildBasePermission, buildBaseResourcePermission, RoleConstants, Compare } from './core'
import type { Permission } from './core/common'

/** 工作空间级：命中权限位 / 系统管理员 / 该空间管理员 即可。workspaceId 内部取当前路由。 */
export const can = (p: Permission): boolean => hasPermission(buildBasePermission(p))

/** 工作空间资源级：命中该资源权限位 / 系统管理员 / 该空间管理员 即可。 */
export const canRes = (p: Permission, id: string): boolean => hasPermission(buildBaseResourcePermission(p, id))

/** 系统级：命中系统管理员 或 该系统权限位 即可（系统页无 workspace/resource 上下文）。 */
export const canSys = (p: Permission): boolean => hasPermission([RoleConstants.ADMIN, p], Compare.OR)
