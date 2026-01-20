export default {
  title: '用户管理',
  createUser: '创建用户',
  editUser: '编辑用户',
  roleSetting: '角色设置',
  addRole: '添加角色',
  setting: {
    updatePwd: '修改用户密码',
  },
  tip: {
    professionalMessage: '社区版最多支持 2 个用户，如需拥有更多用户，请升级为专业版。',
    updatePwdSuccess: '修改用户密码成功',
  },
  delete: {
    confirmTitle: '是否删除用户：',
    confirmMessage: '删除用户，该用户创建的资源（智能体、知识库、模型）不会删除，请谨慎操作。',
  },
  disabled: {
    confirmTitle: '是否禁用工具：',
    confirmMessage: '禁用后，引用了该工具的智能体提问时会报错 ，请谨慎操作。',
  },
  userForm: {
    nick_name: {
      label: '姓名',
      placeholder: '请输入姓名',
      lengthMessage: '长度在 1 到 20 个字符',
    },

    phone: {
      label: '手机号',
      placeholder: '请输入手机号',
      invalidMessage: '手机号格式不正确',
    },
  },
  source: {
    label: '用户来源',
    local: '系统用户',
    localCreate: '本地创建',
    wecom: '企业微信',
    lark: '飞书',
    dingtalk: '钉钉',
  },
  settingRole: '设置角色',
}
