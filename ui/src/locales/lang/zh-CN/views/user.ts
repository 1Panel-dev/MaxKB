export default {
  title: '用户管理',
  createUser: '创建用户',
  editUser: '编辑用户',
  setting: {
    updatePwd: '修改用户密码'
  },
  tip: {
    professionalMessage: '社区版最多支持 2 个用户，如需拥有更多用户，请升级为专业版。',
    updatePwdSuccess: '修改用户密码成功'
  },
  delete: {
    confirmTitle: '是否删除用户：',
    confirmMessage: '删除用户，该用户创建的资源（应用、知识库、模型）都会删除，请谨慎操作。'
  },
  disabled: {
    confirmTitle: '是否禁用函数：',
    confirmMessage: '禁用后，引用了该函数的应用提问时会报错 ，请谨慎操作。'
  },
  userForm: {
    form: {
      username: {
        label: '用户名',
        placeholder: '请输入用户名',
        requiredMessage: '请输入用户名',
        lengthMessage: '长度在 6 到 20 个字符'
      },
      nick_name: {
        label: '姓名',
        placeholder: '请输入姓名'
      },
      email: {
        label: '邮箱',
        placeholder: '请输入邮箱',
        requiredMessage: '请输入邮箱',
        validatorEmail: '请输入有效邮箱格式！',
      },
      phone: {
        label: '手机号',
        placeholder: '请输入手机号'
      },
      password: {
        label: '登录密码',
        placeholder: '请输入密码',
        requiredMessage: '请输入密码',
        lengthMessage: '长度在 6 到 20 个字符'
      },
      new_password: {
        label: '新密码',
        placeholder: '请输入新密码',
        requiredMessage: '请输入新密码',
      },
      re_password: {
        label: '确认密码',
        placeholder: '请输入确认密码',
        requiredMessage: '请输入确认密码',
        validatorMessage: '密码不一致',
      }
    }
  },
  source: {
    label: '用户类型',
    local: '系统用户',
    wecom: '企业微信',
    lark: '飞书',
    dingtalk: '钉钉'
  }
}
