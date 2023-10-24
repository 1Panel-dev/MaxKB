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
