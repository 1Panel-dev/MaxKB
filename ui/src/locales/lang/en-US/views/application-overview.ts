export default {
  title: 'Overview',
  appInfo: {
    header: 'App Information',
    publicAccessLink: 'Public URL',
    openText: 'On',
    closeText: 'Off',
    copyLinkText: 'Copy Link',
    refreshLinkText: 'Refresh Link',
    demo: 'Preview',
    embedInWebsite: 'Get Embed Code',
    accessControl: 'Access Control',
    displaySetting: 'Display Settings',
    apiAccessCredentials: 'API Access Credentials',
    apiKey: 'API Key',
    refreshToken: {
      msgConfirm1: 'Are you sure you want to regenerate the public URL?',
      msgConfirm2:
        'Regenerating the Public URL will affect any existing embedded codes on third-party sites. You will need to update the embed code and re-integrate it into those sites. Proceed with caution!',
      refreshSuccess: 'Successfully Refreshed'
    },
    APIKeyDialog: {
      saveSettings: 'Save Settings',
      msgConfirm1: 'Are you sure you want to delete the API Key',
      msgConfirm2:
        'This action is irreversible. Once deleted, the API Key cannot be recovered. Do you still want to proceed?',
      enabledSuccess: 'Enabled',
      disabledSuccess: 'Disabled'
    },
    EditAvatarDialog: {
      title: 'App Logo',
      customizeUpload: 'Custom Upload',
      upload: 'Upload',
      default: 'Default Logo',
      custom: 'Custom',
      sizeTip:
        'Recommended size: 32×32 pixels. Supports JPG, PNG, and GIF formats. Max size: 10 MB',
      fileSizeExceeded: 'File size exceeds 10 MB',
      uploadImagePrompt: 'Please upload an image'
    },
    EmbedDialog: {
      fullscreenModeTitle: 'Fullscreen Mode',
      copyInstructions: 'Copy the code below to embed',
      floatingModeTitle: 'Floating Mode',
      mobileModeTitle: 'Mobile Mode'
    },
    LimitDialog: {
      dialogTitle: 'Access Restrictions',
      showSourceLabel: 'Show Knowledge Source',
      clientQueryLimitLabel: 'Query Limit per Client',
      authentication: 'Authentication',
      authenticationValue: 'Access Password',
      timesDays: 'queries per day',
      whitelistLabel: 'Allowed Domains',
      whitelistPlaceholder:
        'Enter allowed third-party domains, one per line. For example:\nhttp://127.0.0.1:5678\nhttps://dataease.io'
    },
    SettingAPIKeyDialog: {
      allowCrossDomainLabel: 'Allow Cross-Domain Access',
      crossDomainPlaceholder:
        'Enter allowed cross-domain addresses. If enabled but left blank, no restrictions will apply.\nEnter one per line, e.g.:\nhttp://127.0.0.1:5678\nhttps://dataease.io'
    },
    SettingDisplayDialog: {
      dialogTitle: 'Display Settings',
      languageLabel: 'Language',
      showSourceLabel: 'Show Knowledge Source',
      showExecutionDetail: 'Show Execution Details',
      restoreDefault: 'Restore Default',
      customThemeColor: 'Custom Theme Color',
      headerTitleFontColor: 'Header Title Font Color',
      default: 'Default',
      askUserAvatar: 'User Avatar (Asking)',
      replace: 'Replace',
      display: 'Display',
      imageMessage:
        'Recommended size: 32×32 pixels. Supports JPG, PNG, and GIF formats. Max size: 10 MB',
      AIAvatar: 'AI Avatar',
      floatIcon: 'Floating Icon',
      iconDefaultPosition: 'Default Icon Position',
      iconPosition: {
        left: 'Left',
        right: 'Right',
        bottom: 'Bottom',
        top: 'Top'
      },
      draggablePosition: 'Draggable Position',
      showHistory: 'Show Chat History',
      displayGuide: 'Show Guide Image (Floating Mode)',
      disclaimer: 'Disclaimer',
      disclaimerValue: 'This content is AI-generated and for reference only.'
    }
  },
  monitor: {
    monitoringStatistics: 'Monitoring Statistics',
    customRange: 'Custom Range',
    startDatePlaceholder: 'Start Date',
    endDatePlaceholder: 'End Date',
    pastDayOptions: {
      past7Days: 'Last 7 Days',
      past30Days: 'Last 30 Days',
      past90Days: 'Last 90 Days',
      past183Days: 'Last 6 Months',
      other: 'Custom'
    },
    charts: {
      customerTotal: 'Total Users',
      customerNew: 'New Users',
      queryCount: 'Total Queries',
      tokensTotal: 'Total Tokens Used',
      userSatisfaction: 'User Feedback Metrics',
      approval: 'Like',
      disapproval: 'Dislike'
    }
  }
}
