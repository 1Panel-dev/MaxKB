/**
 * 前端权限模型 —— 后端 `apps/common/auth` 的 TypeScript 镜像。
 *
 * 对应后端：
 *  - Group / Operate / Role          → common/auth/constants/*
 *  - Permission                      → common/auth/struct/permission.py
 *  - AggregatePermission             → common/auth/struct/aggregate_permission.py
 *
 * 关键约定（必须与后端保持一致，否则前端判定与 `/user/profile` 返回的
 * `permissions` 位图对不上）：
 *  - 每个「组(group)」用一个整数位图存放该组内所有操作(operate)的授权位，
 *    某个操作是否被授权 = `bitmap & (1 << bitIndex)`。
 *  - 非资源权限的 key = Permission.toString()（如 `KNOWLEDGE_DOCUMENT_READ`）。
 *  - 资源级权限的 key = `${group}:w:${workspaceId}:r:${resourceId}`。
 */

/** 权限组：一个组通常对应前端一个菜单。枚举值需与后端 `Group` 的 value 一致。 */
export enum Group {
  USER = 'USER_MANAGEMENT',
  APPLICATION = 'APPLICATION',
  KNOWLEDGE = 'KNOWLEDGE',
  MODEL = 'MODEL',
  TOOL = 'TOOL',
  TRIGGER = 'TRIGGER',
  FOLDER = 'FOLDER',
  DOCUMENT = 'DOCUMENT',
  WORKFLOW = 'WORKFLOW',
  TAG = 'TAG',
  PROBLEM = 'PROBLEM',
  TERMBASE = 'TERMBASE',
  HIT_TEST = 'HIT_TEST',
  OVERVIEW = 'OVERVIEW',
  ACCESS = 'ACCESS',
  CHAT_LOG = 'CHAT_LOG',
  CHAT_USER = 'CHAT_USER',
  KNOWLEDGE_CHAT_USER = 'KNOWLEDGE_CHAT_USER',
  ROLE = 'ROLE',
  WORKSPACE = 'WORKSPACE',
  USER_GROUP = 'USER_GROUP',
  EMAIL_SETTING = 'EMAIL_SETTING',
  LOGIN_AUTH = 'LOGIN_AUTH',
  APPEARANCE_SETTINGS = 'APPEARANCE_SETTINGS',
  DISPLAY_SETTINGS = 'DISPLAY_SETTINGS',
  CHAT_USER_GROUP = 'CHAT_USER_GROUP',
  CHAT_USER_AUTH = 'CHAT_USER_AUTH',
  PORTAL = 'PORTAL',
  OTHER = 'OTHER',
  HOMEPAGE = 'HOMEPAGE',
  OPERATION_LOG = 'OPERATION_LOG',
  RESOURCE_PERMISSION = 'RESOURCE_PERMISSION',
  APPLICATION_RESOURCE_PERMISSION = 'APPLICATION_RESOURCE_PERMISSION',
  KNOWLEDGE_RESOURCE_PERMISSION = 'KNOWLEDGE_RESOURCE_PERMISSION',
  TOOL_RESOURCE_PERMISSION = 'TOOL_RESOURCE_PERMISSION',
  MODEL_RESOURCE_PERMISSION = 'MODEL_RESOURCE_PERMISSION',
  WORKSPACE_ROLE = 'WORKSPACE_ROLE',
  WORKSPACE_WORKSPACE = 'WORKSPACE_WORKSPACE',
  WORKSPACE_USER_GROUP = 'WORKSPACE_USER_GROUP',
  WORKSPACE_RESOURCE_PERMISSION = 'WORKSPACE_RESOURCE_PERMISSION',
  WORKSPACE_CHAT_USER = 'WORKSPACE_CHAT_USER',
  WORKSPACE_CHAT_USER_GROUP = 'WORKSPACE_CHAT_USER_GROUP',
  USER_HOMEPAGE = 'USER_HOMEPAGE',
  USER_APPLICATION = 'USER_APPLICATION',
  USER_KNOWLEDGE = 'USER_KNOWLEDGE',
  USER_MODEL = 'USER_MODEL',
  USER_TOOL = 'USER_TOOL',
  USER_OTHER = 'USER_OTHER',
  SYSTEM_KNOWLEDGE = 'SYSTEM_KNOWLEDGE',
  SYSTEM_MODEL = 'SYSTEM_MODEL',
  SYSTEM_TOOL = 'SYSTEM_TOOL',
  SYSTEM_RES_APPLICATION = 'SYSTEM_RESOURCE_APPLICATION',
  SYSTEM_RES_KNOWLEDGE = 'SYSTEM_RESOURCE_KNOWLEDGE',
  SYSTEM_RES_TOOL = 'SYSTEM_RESOURCE_TOOL',
  SYSTEM_RES_MODEL = 'SYSTEM_RESOURCE_MODEL',
  SYSTEM_DOCUMENT = 'SYSTEM_DOCUMENT',
  SYSTEM_WORKFLOW = 'SYSTEM_WORKFLOW',
  SYSTEM_TAG = 'SYSTEM_TAG',
  SYSTEM_PROBLEM = 'SYSTEM_PROBLEM',
  SYSTEM_TERMBASE = 'SYSTEM_TERMBASE',
  SYSTEM_HIT_TEST = 'SYSTEM_HIT_TEST',
  SYSTEM_CHAT_USER = 'SYSTEM_CHAT_USER',
  SYSTEM_OVERVIEW = 'SYSTEM_OVERVIEW',
  SYSTEM_ACCESS = 'SYSTEM_ACCESS',
  SYSTEM_CHAT_LOG = 'SYSTEM_CHAT_LOG',
  CHAT = 'CHAT',
}

/**
 * 操作权限。枚举值需与后端 `Operate` 的 value 完全一致 ——
 * 注意后端很多操作的 value 是形如 `READ+EDIT` 的复合串，会直接进入权限 key。
 */
export enum Operate {
  SELF = '',
  READ = 'READ',
  EDIT = 'READ+EDIT',
  CREATE = 'READ+CREATE',
  DELETE = 'READ+DELETE',
  USE = 'USE',
  IMPORT = 'READ+IMPORT',
  EXPORT = 'READ+EXPORT',
  PUBLISH = 'READ+PUBLISH',
  SYNC = 'READ+SYNC',
  GENERATE = 'READ+GENERATE',
  ADD_MEMBER = 'READ+ADD_MEMBER',
  REMOVE_MEMBER = 'READ+REMOVE_MEMBER',
  VECTOR = 'READ+VECTOR',
  MIGRATE = 'READ+MIGRATE',
  RELATE = 'READ+RELATE',
  USER_GROUP = 'READ+USER_GROUP',
  ANNOTATION = 'READ+ANNOTATION',
  CLEAR_POLICY = 'READ+CLEAR_POLICY',
  EMBED = 'READ+EMBED',
  ACCESS = 'READ+ACCESS',
  DISPLAY = 'READ+DISPLAY',
  API_KEY = 'READ+API_KEY',
  PUBLIC_ACCESS = 'READ+PUBLIC_ACCESS',
  Q_WEIXIN = 'READ+Q_WEIXIN',
  FEISHU = 'READ+FEISHU',
  DD = 'READ+DD',
  WEIXIN_PUBLIC_ACCOUNT = 'READ+WEIXIN_PUBLIC_ACCOUNT',
  SLACK = 'READ+SLACK',
  ADD_KNOWLEDGE = 'READ+ADD_KNOWLEDGE',
  TO_CHAT = 'READ+TO_CHAT',
  SETTING = 'READ+SETTING',
  DOWNLOAD = 'READ+DOWNLOAD',
  COPY = 'READ+COPY',
  AUTH = 'READ+AUTH',
  TAG = 'READ+TAG',
  REPLACE = 'READ+REPLACE',
  UPDATE = 'READ+UPDATE',
  RELATE_VIEW = 'READ+RELATE_VIEW',
  RECORD = 'READ+RECORD',
  TRIGGER_READ = 'READ+TRIGGER_READ',
  TRIGGER_EDIT = 'READ+TRIGGER_EDIT',
  TRIGGER_CREATE = 'READ+TRIGGER_CREATE',
  TRIGGER_DELETE = 'READ+TRIGGER_DELETE',
  BATCH_DELETE = 'READ+BATCH_DELETE',
  BATCH_MOVE = 'READ+BATCH_MOVE',
  TOKEN = 'READ+TOKEN',
  TO_WORKSPACE = 'READ+TO_WORKSPACE',
  SET_ROLE = 'READ+SET_ROLE',
  QUOTA_SETTING = 'READ+QUOTA_SETTING',
  ABOUT = 'READ',
  LICENSE = 'READ+UPDATE',
  SWITCH_LANGUAGE = 'READ+EDIT',
  CHANGE_PASSWORD = 'READ+CREATE',
  SYSTEM_API_KEY = 'READ+DELETE',
  PORTAL = 'READ+PORTAL',
  PASSWORD = 'PASSWORD',
  LOCAL = 'LOCAL',
  CAS = 'CAS',
  DINGTALK = 'DINGTALK',
  WECOM = 'WECOM',
  LARK = 'LARK',
  OIDC = 'OIDC',
  LDAP = 'LDAP',
  OAUTH2 = 'OAUTH2',
}

export enum Compare {
  OR = 'OR',
  AND = 'AND',
}

/** 权限工厂调用时可注入的上下文（一般取自路由参数）。 */
export interface PermissionContext {
  workspaceId?: string
  resourceId?: string
}

/** 延迟到判定时刻、结合上下文生成具体 Permission 的工厂。 */
export type PermissionFactory = (ctx?: PermissionContext) => Permission

/** 延迟到判定时刻、结合上下文生成具体 Role 的工厂。 */
export type RoleFactory = (ctx?: PermissionContext) => Role

/**
 * 运行时角色，支持工作空间维度限定，对应后端
 * `common/auth/struct/permission.py` 的 Role dataclass。
 */
export class Role {
  name: string
  workspaceId?: string

  constructor(name: string, workspaceId?: string) {
    this.name = name
    this.workspaceId = workspaceId
  }

  /** 对应后端 `Role.__str__`。 */
  toString(): string {
    return this.workspaceId ? `${this.name}:${this.workspaceId}` : `${this.name}`
  }

  /** 工作空间维度角色工厂，对应后端 `RoleConstants.get_workspace_role`。 */
  getWorkspaceRole(): RoleFactory {
    return (ctx) => new Role(this.name, ctx?.workspaceId)
  }
}

/**
 * 内置角色常量，成员为 Role 实例，对应后端
 * `common/auth/constants/role_constants.py` 的 RoleConstants 枚举。
 */
export const RoleConstants = {
  ADMIN: new Role('ADMIN'),
  WORKSPACE_MANAGE: new Role('WORKSPACE_MANAGE'),
  USER: new Role('USER'),
  EXTENDS_ADMIN: new Role('EXTENDS_ADMIN'),
  EXTENDS_WORKSPACE_MANAGE: new Role('EXTENDS_WORKSPACE_MANAGE'),
  EXTENDS_USER: new Role('EXTENDS_USER'),
} as const

/** 单条权限，对应后端 `common/auth/struct/permission.py` 的 Permission。 */
export class Permission {
  constructor(
    public group: Group,
    public subGroup: Group,
    public operate: Operate,
    public bitIndex: number,
    public workspaceId?: string,
    public resourceId?: string,
    /** 特权标记，对应后端工作空间管理员特权 flag。 */
    public flag?: string,
  ) {}

  /** 该权限在所属组位图中的比特位。 */
  bit(): bigint {
    return 1n << BigInt(this.bitIndex)
  }

  /** 非资源权限 key，对应后端 `Permission.__str__`。 */
  toString(): string {
    const sub = this.subGroup !== this.group ? `_${this.subGroup}` : ''
    const flag = this.flag ? `_${this.flag}` : ''
    return `${this.group}${sub}_${this.operate}${flag}`
  }

  /** 资源级权限 key，对应后端 `Permission.get_resource_permission_key`。 */
  getResourcePermissionKey(): string {
    const workspace = this.workspaceId ? `:w:${this.workspaceId}` : ''
    const resource = this.resourceId ? `:r:${this.resourceId}` : ''
    return `${this.group}${workspace}${resource}`
  }

  /** 判定时使用的最终 key，对应后端 `AggregatePermission._match_permission`。 */
  toPermissionKey(): string {
    return this.resourceId ? this.getResourcePermissionKey() : this.toString()
  }

  /** 基于上下文派生出带 workspace / resource 的权限副本。 */
  withContext(ctx?: PermissionContext): Permission {
    if (!ctx?.workspaceId && !ctx?.resourceId) {
      return this
    }
    return new Permission(this.group, this.subGroup, this.operate, this.bitIndex, ctx?.workspaceId, ctx?.resourceId, this.flag)
  }

  /** 派生带 workspaceId 的工作空间级权限副本，对应后端 `get_workspace_permission`。 */
  newWorkspacePermission(workspaceId?: string): Permission {
    return new Permission(this.group, this.subGroup, this.operate, this.bitIndex, workspaceId)
  }

  /** 派生带 workspaceId + resourceId 的资源级权限副本。 */
  newResourcePermission(workspaceId?: string, resourceId?: string): Permission {
    return new Permission(this.group, this.subGroup, this.operate, this.bitIndex, workspaceId, resourceId)
  }

  // —— 工厂：对应后端 PermissionConstants 上的 get_workspace_*_permission ——

  /** 仅工作空间维度（无资源 id），对应 `get_workspace_permission`。 */
  getWorkspacePermission(): PermissionFactory {
    return (ctx) => new Permission(this.group, this.subGroup, this.operate, this.bitIndex, ctx?.workspaceId)
  }

  /** 工作空间 + 资源维度，对应 `get_workspace_{knowledge,application,...}_permission`。 */
  getWorkspaceResourcePermission(): PermissionFactory {
    return (ctx) => new Permission(this.group, this.subGroup, this.operate, this.bitIndex, ctx?.workspaceId, ctx?.resourceId)
  }

  /** 工作空间管理员特权，对应 `get_workspace_permission_workspace_manage_role`。 */
  getWorkspaceManageFlagPermission(): PermissionFactory {
    return (ctx) => new Permission(this.group, this.subGroup, this.operate, this.bitIndex, ctx?.workspaceId, undefined, RoleConstants.WORKSPACE_MANAGE.name)
  }
}

export interface AggregatePermissionOptions {
  permissionCalls?: PermissionFactory[]
  permissionConstants?: Permission[]
  aggregatePermissions?: AggregatePermission[]
  roles?: Array<Role | RoleFactory>
  compare?: Compare
}

/** 组合权限，对应后端 `AggregatePermission`，支持 OR/AND 与嵌套、短路求值。 */
export class AggregatePermission {
  permissionCalls: PermissionFactory[]
  permissionConstants: Permission[]
  aggregatePermissions: AggregatePermission[]
  roles: Array<Role | RoleFactory>
  compare: Compare

  constructor(options: AggregatePermissionOptions = {}) {
    this.permissionCalls = options.permissionCalls ?? []
    this.permissionConstants = options.permissionConstants ?? []
    this.aggregatePermissions = options.aggregatePermissions ?? []
    this.roles = options.roles ?? []
    this.compare = options.compare ?? Compare.OR
  }

  static builder(): AggregatePermissionBuilder {
    return new AggregatePermissionBuilder()
  }

  hasPermission(userRoles: Set<string>, userPermissions: Map<string, bigint>, ctx?: PermissionContext): boolean {
    // 无任何约束 => 放行（对应后端五集合全空的判断）
    if (this.permissionCalls.length === 0 && this.permissionConstants.length === 0 && this.aggregatePermissions.length === 0 && this.roles.length === 0) {
      return true
    }

    const isAnd = this.compare === Compare.AND

    const evaluate = (hit: boolean): boolean | undefined => {
      if (hit && !isAnd) return true // OR：命中其一即通过
      if (!hit && isAnd) return false // AND：缺一即失败
      return undefined // 继续下一项
    }

    for (const call of this.permissionCalls) {
      const r = evaluate(this.checkPermission(call(ctx), userPermissions))
      if (r !== undefined) return r
    }
    for (const permission of this.permissionConstants) {
      const r = evaluate(this.checkPermission(permission.withContext(ctx), userPermissions))
      if (r !== undefined) return r
    }
    for (const role of this.roles) {
      const resolved = typeof role === 'function' ? role(ctx) : role
      const r = evaluate(this.checkRole(resolved, userRoles))
      if (r !== undefined) return r
    }
    for (const aggregate of this.aggregatePermissions) {
      const r = evaluate(aggregate.hasPermission(userRoles, userPermissions, ctx))
      if (r !== undefined) return r
    }

    // AND 全部通过 => true；OR 一个都没命中 => false
    return isAnd
  }

  private checkRole(role: Role, userRoles: Set<string>): boolean {
    if (userRoles.size === 0) return false
    return userRoles.has(role.toString())
  }

  private checkPermission(permission: Permission, userPermissions: Map<string, bigint>): boolean {
    const key = permission.toPermissionKey()
    const raw = userPermissions.get(key)
    if (raw == null) return false
    return (raw & permission.bit()) !== 0n
  }
}

export class AggregatePermissionBuilder {
  private _permissionCalls: PermissionFactory[] = []
  private _permissionConstants: Permission[] = []
  private _aggregatePermissions: AggregatePermission[] = []
  private _roles: Array<Role | RoleFactory> = []
  private _compare: Compare = Compare.OR

  compare(compare: Compare): this {
    this._compare = compare
    return this
  }

  addPermission(permission: PermissionFactory | Permission | AggregatePermission): this {
    if (permission instanceof AggregatePermission) {
      this._aggregatePermissions.push(permission)
    } else if (typeof permission === 'function') {
      this._permissionCalls.push(permission)
    } else {
      this._permissionConstants.push(permission)
    }
    return this
  }

  addRole(role: Role | RoleFactory): this {
    this._roles.push(role)
    return this
  }

  build(): AggregatePermission {
    return new AggregatePermission({
      permissionCalls: this._permissionCalls,
      permissionConstants: this._permissionConstants,
      aggregatePermissions: this._aggregatePermissions,
      roles: this._roles,
      compare: this._compare,
    })
  }
}
