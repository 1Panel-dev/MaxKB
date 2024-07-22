export default {
  title: 'Overview',
  appInfo: {
    header: 'Application Info',
    publicAccessLink: 'Public Access Link',
    openText: 'On',
    closeText: 'Off',
    copyLinkText: 'Copy Link',
    refreshLinkText: 'Refresh Link',
    demo: 'Demo',
    embedThirdParty: 'Embed Third Party',
    accessRestrictions: 'Access Restrictions',
    displaySetting: 'Display Setting',
    apiAccessCredentials: 'API Access Credentials',
    apiKey: 'API Key',
    refreshToken: {
      msgConfirm1: 'Do you want to regenerate the public access link?',
      msgConfirm2:
        'Regenerating the public access link will affect third-party embedded scripts changes and will require re-embedding the new script into third-party sites. Please proceed with caution!',
      confirm: 'Confirm',
      cancel: 'Cancel',
      refreshSuccess: 'Refresh Successful'
    },
    changeState: {
      enableSuccess: 'Enable Successful',
      disableSuccess: 'Disable Successful'
    },
    APIKeyDialog: {
      creatApiKey: 'Create',
      status: 'Status',
      creationDate: 'Creation Date',
      operations: 'Operations',
      settings: 'Settings',
      delete: 'Delete',
      saveSettings: 'Save Settings',
      msgConfirm1: 'Are you sure you want to delete the API Key?',
      msgConfirm2:
        'Deleting the API Key cannot be undone. Please confirm if you want to delete it!',
      confirmDelete: 'Delete',
      deleteSuccess: 'Delete Successful',
      cancel: 'Cancel',
      enabledSuccess: 'Enabled',
      disabledSuccess: 'Disabled'
    },
    EditAvatarDialog: {
      title: 'Edit Logo',
      customizeUpload: 'Custom Upload',
      upload: 'Upload',
      default: 'Default Logo',
      custom: 'Custom',
      sizeTip: 'Suggested size 32*32, supports ico, png, size no more than 200KB',
      cancel: 'Cancel',
      save: 'Save',
      fileSizeExceeded: 'File size exceeds 200KB',
      setSuccess: 'Setting Successful',
      uploadImagePrompt: 'Please upload an image'
    },
    EmbedDialog: {
      embedDialogTitle: 'Embed Third Party',
      fullscreenModeTitle: 'Fullscreen Mode',
      copyInstructions: 'Copy the following code to embed',
      floatingModeTitle: 'Floating Mode'
    },
    LimitDialog: {
      dialogTitle: 'Access Restrictions',
      showSourceLabel: 'Show Source',
      clientQueryLimitLabel: 'Each Client Query Limit',
      timesDays: 'Times/Day',
      whitelistLabel: 'Whitelist',
      whitelistPlaceholder:
        'Please enter allowed third-party source addresses, one per line, such as:\nhttp://127.0.0.1:5678\nhttps://dataease.io',
      cancelButtonText: 'Cancel',
      saveButtonText: 'Save',
      settingSuccessMessage: 'Setting Successful'
    },
    SettingAPIKeyDialog: {
      dialogTitle: 'Settings',
      allowCrossDomainLabel: 'Allow Cross-Domain Address',
      crossDomainPlaceholder:
        'Please enter allowed cross-domain addresses, if open without inputting addresses, there are no restrictions.\nCross-domain addresses one per line, such as:\nhttp://127.0.0.1:5678\nhttps://dataease.io',
      cancelButtonText: 'Cancel',
      saveButtonText: 'Save',
      successMessage: 'Setting Successful'
    }
  },
  monitor: {
    monitoringStatistics: 'Monitoring Statistics',
    customRange: 'Custom Range',
    startDatePlaceholder: 'Start Date',
    endDatePlaceholder: 'End Date',
    pastDayOptions: {
      past7Days: 'Past 7 Days',
      past30Days: 'Past 30 Days',
      past90Days: 'Past 90 Days',
      past183Days: 'Past Half Year',
      other: 'Custom'
    },
    charts: {
      customerTotal: 'Total Customers',
      customerNew: 'New Customers',
      queryCount: 'Query Count',
      tokensTotal: 'Total Tokens',
      userSatisfaction: 'User Satisfaction',
      approval: 'Approval',
      disapproval: 'Disapproval'
    }
  }
}
