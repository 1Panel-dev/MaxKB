export default {
  title: '对话用户',
  syncUsers: '导入用户',
  syncUsersTip: '仅导入新增用户',
  setUserGroups: '设置用户组',
  knowledgeTitleTip: '该配置需要关联的智能体开启对话用户登录认证后才会生效',
  applicationTitleTip: '该配置需要智能体开启登录认证后生效',
  autoAuthorization: '自动授权',
  authorization: '授权',
  batchDeleteUser: '是否删除选中的 {count} 个用户？',
  settingMethod: '设置方式',
  append: '追加',
  group: {
    title: '用户组',
    requiredMessage: '请选择用户组',
    name: '用户组名称',
    usernameOrName: '用户名/姓名',
    delete: {
      confirmTitle: '是否删除用户组：',
      confirmMessage: '删除后，该用户组下的成员将全部移除，请谨慎操作！',
    },
    batchDeleteMember: '是否移除选中的 {count} 个成员？',
  },
  syncMessage: {
    title: '成功同步 {count} 个用户',
    usernameExist: '以下用户名已存在：',
    nicknameExist: '以下姓名已存在：',
  },
}
