import { RoleTypeEnum } from '@/enums/system'

export const roleTypeMap: Record<string, string> = {
  [RoleTypeEnum.ADMIN]: '系统管理员',
  [RoleTypeEnum.USER]: '普通用户',
  [RoleTypeEnum.WORKSPACE_MANAGE]: '工作空间管理员',
}

/** 创建自定义角色时可选的继承角色类型（不包含 ADMIN） */
export const createRoleTypeOptions = [
  { label: '普通用户', value: RoleTypeEnum.USER },
  { label: '工作空间管理员', value: RoleTypeEnum.WORKSPACE_MANAGE },
]
