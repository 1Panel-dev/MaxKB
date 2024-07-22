export default {
  title: '概览',
  appInfo: {
    header: '应用信息',
    publicAccessLink: '公开访问链接',
    openText: '开',
    closeText: '关',
    copyLinkText: '复制链接',
    refreshLinkText: '刷新链接',
    demo: '演示',
    embedThirdParty: '嵌入第三方',
    accessRestrictions: '访问限制',
    displaySetting: '显示设置',
    apiAccessCredentials: 'API访问凭据',
    apiKey: 'API Key',
    refreshToken: {
      msgConfirm1: '是否重新生成公开访问链接?',
      msgConfirm2:
        '重新生成公开访问链接会影响嵌入第三方脚本变更，需要将新脚本重新嵌入第三方，请谨慎操作！',
      confirm: '确认',
      cancel: '取消',
      refreshSuccess: '刷新成功'
    },
    changeState: {
      enableSuccess: '启用成功',
      disableSuccess: '禁用成功'
    },
    APIKeyDialog: {
      creatApiKey: '创建',
      status: '状态',
      creationDate: '创建日期',
      operations: '操作',
      settings: '设置',
      delete: '删除',
      saveSettings: '保存设置',
      msgConfirm1: '是否删除API Key?',
      msgConfirm2: '删除API Key后将无法恢复，请确认是否删除！',
      confirmDelete: '删除',
      deleteSuccess: '删除成功',
      cancel: '取消',
      enabledSuccess: '已启用',
      disabledSuccess: '已禁用'
    },
    EditAvatarDialog: {
      title: '编辑logo',
      customizeUpload: '自定义上传',
      upload: '上传',
      default: '默认logo',
      custom: '自定义',
      sizeTip: '建议尺寸 32*32，支持 ico、png，大小不超过200KB',
      cancel: '取消',
      save: '保存',
      fileSizeExceeded: '文件大小超过 200KB',
      setSuccess: '设置成功',
      uploadImagePrompt: '请上传一张图片'
    },
    EmbedDialog: {
      embedDialogTitle: '嵌入第三方',
      fullscreenModeTitle: '全屏模式',
      copyInstructions: '复制以下代码进行嵌入',
      floatingModeTitle: '浮窗模式'
    },
    LimitDialog: {
      dialogTitle: '访问限制',
      showSourceLabel: '显示知识来源',
      clientQueryLimitLabel: '每个客户端提问限制',
      timesDays: '次/天',
      whitelistLabel: '白名单',
      whitelistPlaceholder:
        '请输入允许嵌入第三方的源地址，一行一个，如：\nhttp://127.0.0.1:5678\nhttps://dataease.io',
      cancelButtonText: '取消',
      saveButtonText: '保存',
      settingSuccessMessage: '设置成功'
    },
    SettingAPIKeyDialog: {
      dialogTitle: '设置',
      allowCrossDomainLabel: '允许跨域地址',
      crossDomainPlaceholder:
        '请输入允许的跨域地址，开启后不输入跨域地址则不限制。\n跨域地址一行一个，如：\nhttp://127.0.0.1:5678 \nhttps://dataease.io',
      cancelButtonText: '取消',
      saveButtonText: '保存',
      successMessage: '设置成功'
    }
  },
  monitor: {
    monitoringStatistics: '监控统计',
    customRange: '自定义范围',
    startDatePlaceholder: '开始时间',
    endDatePlaceholder: '结束时间',
    pastDayOptions: {
      past7Days: '过去7天',
      past30Days: '过去30天',
      past90Days: '过去90天',
      past183Days: '过去半年',
      other: '自定义'
    },
    charts: {
      customerTotal: '用户总数',
      customerNew: '用户新增数',
      queryCount: '提问次数',
      tokensTotal: 'Tokens 总数',
      userSatisfaction: '用户满意度',
      approval: '赞同',
      disapproval: '反对'
    }
  }
}
