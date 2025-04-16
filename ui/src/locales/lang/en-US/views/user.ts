export default {
  title: 'User',
  createUser: 'Create User',
  editUser: 'Edit User',
  setting: {
    updatePwd: 'Change Password'
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 2 users. For more users, please upgrade to the professional edition.',
    updatePwdSuccess: 'User password updated successfully'
  },
  delete: {
    confirmTitle: 'Confirm deletion of user:',
    confirmMessage:
      'Deleting this user will also delete all resources (APP, knowledge, models) created by this user. Please proceed with caution.'
  },
  disabled: {
    confirmTitle: 'Confirm disable function:',
    confirmMessage:
      'Disabling this function will cause errors when APP that reference it are queried. Please proceed with caution.'
  },
  userForm: {
    form: {
      username: {
        label: 'Username',
        placeholder: 'Please enter username',
        requiredMessage: 'Please enter username',
        lengthMessage: 'Length must be between 6 and 20 words'
      },
      nick_name: {
        label: 'Name',
        placeholder: 'Please enter name'
      },
      email: {
        label: 'Email',
        placeholder: 'Please enter email',
        requiredMessage: 'Please enter email'
      },
      phone: {
        label: 'Phone',
        placeholder: 'Please enter phone'
      },
      password: {
        label: 'Login Password',
        placeholder: 'Please enter password',
        requiredMessage: 'Please enter password',
        lengthMessage: 'Length must be between 6 and 20 words'
      },
      new_password: {
        label: 'New Password',
        placeholder: 'Please enter new password',
        requiredMessage: 'Please enter new password'
      },
      re_password: {
        label: 'Confirm Password',
        placeholder: 'Please enter confirm password',
        requiredMessage: 'Please enter confirm password',
        validatorMessage: 'Passwords do not match'
      }
    }
  },
  source: {
    label: 'User Type',
    local: 'System User',
    wecom: 'WeCom',
    lark: 'Lark',
    dingtalk: 'DingTalk'
  }
}
