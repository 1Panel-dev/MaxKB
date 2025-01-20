export default {
  title: 'User Management',
  createUser: 'Create User',
  editUser: 'Edit User',
  setting: {
    updatePwd: 'Update User Password'
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 2 users. For more users, please upgrade to the professional edition.',
    updatePwdSuccess: 'User password updated successfully'
  },
  delete: {
    confirmTitle: 'Confirm Deletion of User:',
    confirmMessage:
      'Deleting this user will also delete all resources (applications, knowledge bases, models) created by this user. Please proceed with caution.'
  },
  disabled: {
    confirmTitle: 'Confirm Disable Function:',
    confirmMessage:
      'Disabling this function will cause errors when applications that reference it are queried. Please proceed with caution.'
  },
  userForm: {
    form: {
      username: {
        label: 'Username',
        placeholder: 'Please enter username',
        requiredMessage: 'Please enter username',
        lengthMessage: 'Length must be between 6 and 20 characters'
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
        label: 'Phone Number',
        placeholder: 'Please enter phone number'
      },
      password: {
        label: 'Login Password',
        placeholder: 'Please enter password',
        requiredMessage: 'Please enter password',
        lengthMessage: 'Length must be between 6 and 20 characters'
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
    wecom: 'WeCom (Enterprise WeChat)',
    lark: 'Lark (Feishu)',
    dingtalk: 'DingTalk'
  }
}
