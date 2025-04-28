import { Permission } from '@/utils/permission/type'
const PermissionConst = {
  USER_READ: new Permission('USER:READ'),
  USER_CREATE: new Permission('USER:CREATE'),
  KNOWLEDGE_READ: new Permission('KNOWLEDGE:READ'),
}
export default PermissionConst
