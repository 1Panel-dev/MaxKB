import useStore from '@/stores'
import { useRoute } from 'vue-router'
export type PF = () => Role | string | Permission | ComplexPermission
export type CRF = () => Role | string
export type CPF = () => Permission | string
/**
 * 角色对象
 */
export class Role {
  role: string

  constructor(role: string) {
    this.role = role
  }

  getWorkspaceRole = () => {
    const { user } = useStore()
    return new Role(`${this.role}:/WORKSPACE/${user.getWorkspaceId()}`)
  }
  getWorkspaceRoleString = () => {
    const { user } = useStore()
    return `${this.role}:/WORKSPACE/${user.getWorkspaceId()}`
  }
  toString() {
    return this.role
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
  getWorkspacePermission = () => {
    const { user } = useStore()
    return `${this.permission}:/WORKSPACE/${user.getWorkspaceId()}`
  }
  /**
   * 自定义工作空间管理员权限
   * @returns
   */
  getWorkspacePermissionWorkspaceManageRole = () => {
    const { user } = useStore()
    return `${this.permission}:/WORKSPACE/${user.getWorkspaceId()}:ROLE/WORKSPACE_MANAGE`
  }
  /**
   * 工作空间资源权限
   * @param workspace_id 工作空间id
   * @param resource     资源
   * @param resource_id  资源id
   * @returns  工作空间资源权限
   */
  getWorkspaceResourcePermission = (resource: string, resource_id: string) => {
    const { user } = useStore()
    return `${this.permission}:/WORKSPACE/${user.getWorkspaceId()}/${resource}/${resource_id}`
  }
  /**
   *
   * @param resource_id 资源id
   * @returns 工作空间下知识库资源权限
   */
  getKnowledgeWorkspaceResourcePermission = (resource_id: string) => {
    return this.getWorkspaceResourcePermission('KNOWLEDGE', resource_id)
  }
  getTest=()=>{
    const route=useRoute()
    debugger
    console.log(route)
    return ""
  }
  /**
   *
   * @param resource_id  资源id
   * @returns 工作空间下应用资源权限
   */
  getApplicationWorkspaceResourcePermission = (resource_id: string) => {
    return this.getWorkspaceResourcePermission('APPLICATION', resource_id)
  }
  /**
   * 
   * @param resource_id 资源id
   * @returns 工作空间下模型资源权限
   */
  getModelWorkspaceResourcePermission = (resource_id: string) => {
    return this.getWorkspaceResourcePermission('MODEL', resource_id)
  }
  /**
   * 
   * @param resource_id 
   * @returns 工作空间下工具资源权限
   */
  getToolWorkspaceResourcePermission = (resource_id: string) => {
    return this.getWorkspaceResourcePermission('TOOL', resource_id)
  }

  toString() {
    return this.permission
  }
}

/**
 * 复杂权限对象
 */
export class ComplexPermission {
  roleList: Array<string | Role | CRF>

  permissionList: Array<string | Permission | CPF>

  editionList: Array<string | Edition>

  compare: 'OR' | 'AND'

  constructor(
    roleList: Array<string | Role | CRF>,
    permissionList: Array<string | Permission | CPF>,
    editionList: Array<string | Edition>,
    compare: 'OR' | 'AND',
  ) {
    this.roleList = roleList
    this.permissionList = permissionList
    this.editionList = editionList
    this.compare = compare
  }
}
/**
 * 版本
 */
export class Edition {
  edition: string
  constructor(edition: string) {
    this.edition = edition
  }
  toString() {
    return this.edition
  }
}
