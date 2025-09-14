export default {
  title: 'Chat Users',
  syncUsers: 'Sync Users',
  syncUsersTip: 'Only sync newly added users',
  setUserGroups: 'Configure User Groups',
  knowledgeTitleTip:
    'This configuration will only take effect after enabling chat user login authentication in the associated application',
  applicationTitleTip:
    'This configuration requires login authentication to be enabled in the application',
  autoAuthorization: 'Auto Authorization',
  authorization: 'Authorization',
  batchDeleteUser: 'Delete selected {count} users?',
  settingMethod: 'Configuration Method',
  append: 'Append',
  group: {
    title: 'User Groups',
    name: 'User Group Name',
    requiredMessage: 'Please select user group',
    usernameOrName: 'Username/Name',
    delete: {
      confirmTitle: 'Confirm to delete user group:',
      confirmMessage:
        'All members in this group will be removed after deletion. Proceed with caution!',
    },
    batchDeleteMember: 'Remove selected {count} members?',
  },
  syncMessage: {
    title: 'Successfully synced {count} users',
    usernameExist: 'The following usernames already exist:',
    nicknameExist: 'The following nicknames already exist:',
  },
}
