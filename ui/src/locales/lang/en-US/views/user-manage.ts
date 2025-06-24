export default {
  title: 'User',
  createUser: 'Create User',
  editUser: 'Edit User',
  roleSetting: 'Role Setting',
  addRole: 'Add role',
  setting: {
    updatePwd: 'Change Password',
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 2 users. For more users, please upgrade to the professional edition.',
    updatePwdSuccess: 'User password updated successfully',
  },
  delete: {
    confirmTitle: 'Confirm deletion of user:',
    confirmMessage:
      'Deleting this user will also delete all resources (APP, knowledge, models) created by this user. Please proceed with caution.',
  },
  disabled: {
    confirmTitle: 'Confirm disable tool:',
    confirmMessage:
      'Disabling this tool will cause errors when APP that reference it are queried. Please proceed with caution.',
  },
  userForm: {
    nick_name: {
      label: 'Name',
      placeholder: 'Please enter name',
      lengthMessage: 'Length must be between 2 and 20 characters',
    },
    phone: {
      label: 'Phone',
      placeholder: 'Please enter phone',
    },
  },
  source: {
    label: 'User Source',
    local: 'System User',
    wecom: 'WeCom',
    lark: 'Lark',
    dingtalk: 'DingTalk',
  },
}
