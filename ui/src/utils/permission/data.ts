import { Permission, Role, Edition } from '@/utils/permission/type'
const PermissionConst = {
  USER_READ: new Permission('USER:READ'),
  USER_CREATE: new Permission('USER:CREATE'),
  KNOWLEDGE_READ: new Permission('KNOWLEDGE:READ'),
  APPLICATION_OVERVIEW_READ: new Permission('APPLICATION_OVERVIEW_READ'),
}
const RoleConst = {
  ADMIN: new Role('ADMIN'),
  WORKSPACE_MANAGE: new Role('WORKSPACE_MANAGE'),
  USER: new Role('USER'),
}
const EditionConst = {
  IS_PE: new Edition('X-PACK-PE'),
  IS_EE: new Edition('X-PACK-EE'),
  IS_CE: new Edition('X-PACK-CE'),
}
export { PermissionConst, RoleConst, EditionConst }
