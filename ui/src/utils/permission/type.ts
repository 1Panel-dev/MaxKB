/**
 * 角色对象
 */
export class Role {
  role: string

  constructor(role: string) {
    this.role = role
  }
}
/**
 * 权限对象
 */
export class Permission {
  permission: string

  constructor(permission: string) {
    this.permission = permission
  }
  /**
   * 工作空间权限
   * @param workspace_id 工作空间id
   * @returns 工作空间权限
   */
  getWorkspacePermission(workspace_id: string) {
    return `${this.permission}:/WORKSPACE/${workspace_id}`
  }
  /**
   * 工作空间资源权限
   * @param workspace_id 工作空间id
   * @param resource     资源
   * @param resource_id  资源id
   * @returns  工作空间资源权限
   */
  getWorkspaceResourcePermission(workspace_id: string, resource: string, resource_id: string) {
    return `${this.permission}:/WORKSPACE/${workspace_id}/${resource}/${resource_id}`
  }
}
/**
 * 复杂权限对象
 */
export class ComplexPermission {
  roleList: Array<string>

  permissionList: Array<string>

  compare: 'OR' | 'AND'

  constructor(roleList: Array<string>, permissionList: Array<string>, compare: 'OR' | 'AND') {
    this.roleList = roleList
    this.permissionList = permissionList
    this.compare = compare
  }
}
