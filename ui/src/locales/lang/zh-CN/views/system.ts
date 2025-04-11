export default {
  title: '系统管理',
  subTitle: '系统设置',
  test: '测试连接',
  testSuccess: '测试连接成功',
  testFailed: '测试连接失败',
  password: '密码',
  authentication: {
    title: '登录认证',
    ldap: {
      title: 'LDAP',
      address: 'LDAP 地址',
      serverPlaceholder: '请输入LDAP 地址',
      bindDN: '绑定DN',
      bindDNPlaceholder: '请输入绑定 DN',
      ou: '用户OU',
      ouPlaceholder: '请输入用户 OU',
      ldap_filter: '用户过滤器',
      ldap_filterPlaceholder: '请输入用户过滤器',
      ldap_mapping: 'LDAP 属性映射',
      ldap_mappingPlaceholder: '请输入 LDAP 属性映射',
      enableAuthentication: '启用 LDAP 认证'
    },
    cas: {
      title: 'CAS',
      ldpUri: 'ldpUri',
      ldpUriPlaceholder: '请输入ldpUri',
      validateUrl: '验证地址',
      validateUrlPlaceholder: '请输入验证地址',
      redirectUrl: '回调地址',
      redirectUrlPlaceholder: '请输入回调地址',
      enableAuthentication: '启用 CAS 认证'
    },
    oidc: {
      title: 'OIDC',
      authEndpoint: '授权端地址',
      authEndpointPlaceholder: '请输入授权端地址',
      tokenEndpoint: 'Token端地址',
      tokenEndpointPlaceholder: '请输入 Token 端地址',
      userInfoEndpoint: '用户信息端地址',
      userInfoEndpointPlaceholder: '请输入用户信息端地址',
      scopePlaceholder: '请输入连接范围',
      clientId: '客户端 ID',
      clientIdPlaceholder: '请输入客户端 ID',
      clientSecret: '客户端密钥',
      clientSecretPlaceholder: '请输入客户端密钥',
      logoutEndpoint: '注销端地址',
      logoutEndpointPlaceholder: '请输入注销端地址',
      redirectUrl: '回调地址',
      redirectUrlPlaceholder: '请输入回调地址',
      enableAuthentication: '启用 OIDC 认证'
    },

    oauth2: {
      title: 'OAuth2',
      authEndpoint: '授权端地址',
      authEndpointPlaceholder: '请输入授权端地址',
      tokenEndpoint: 'Token 端地址',
      tokenEndpointPlaceholder: '请输入 Token 端地址',
      userInfoEndpoint: '用户信息端地址',
      userInfoEndpointPlaceholder: '请输入用户信息端地址',
      scope: '连接范围',
      scopePlaceholder: '请输入连接范围',
      clientId: '客户端 ID',
      clientIdPlaceholder: '请输入客户端 ID',
      clientSecret: '客户端密钥',
      clientSecretPlaceholder: '请输入客户端密钥',
      redirectUrl: '回调地址',
      redirectUrlPlaceholder: '请输入回调地址',
      filedMapping: '字段映射',
      filedMappingPlaceholder: '请输入字段映射',
      enableAuthentication: '启用 OAuth2 认证'
    },
    scanTheQRCode: {
      title: '扫码登录',
      wecom: '企业微信',
      dingtalk: '钉钉',
      lark: '飞书',
      effective: '有效',
      alreadyTurnedOn: '已开启',
      notEnabled: '未开启',
      validate: '校验',
      validateSuccess: '校验成功',
      validateFailed: '校验失败',
      validateFailedTip: '请填写所有必填项并确保格式正确',
      appKeyPlaceholder: '请输入 App Key',
      appSecretPlaceholder: '请输入 App Secret',
      corpIdPlaceholder: '请输入 Corp Id',
      agentIdPlaceholder: '请输入 Agent Id',
      callbackWarning: '请输入有效的 URL 地址',
      larkQrCode: '飞书扫码登录',
      dingtalkQrCode: '钉钉扫码登录',
      setting: '设置',
      access: '接入'
    }
  },
  theme: {
    title: '外观设置',
    platformDisplayTheme: '平台显示主题',
    customTheme: '自定义主题',
    platformLoginSettings: '平台登录设置',
    custom: '自定义',
    pagePreview: '页面预览',
    default: '默认',
    restoreDefaults: '恢复默认',
    orange: '活力橙',
    green: '松石绿',
    purple: '神秘紫',
    red: '胭脂红',
    loginBackground: '登录背景图',
    loginLogo: '登录 Logo',
    websiteLogo: '网站 Logo',
    replacePicture: '替换图片',
    websiteLogoTip: '顶部网站显示的 Logo，建议尺寸 48*48，支持 JPG、PNG、GIF，大小不超过 10MB',
    loginLogoTip: '登录页面右侧 Logo，建议尺寸 204*52，支持 JPG、PNG、GIF，大小不超过 10 MB',
    loginBackgroundTip:
      '左侧背景图，矢量图建议尺寸 576*900，位图建议尺寸 1152*1800；支持 JPG、PNG、GIF，大小不超过 10 MB',
    websiteName: '网站名称',
    websiteNamePlaceholder: '请输入网站名称',
    websiteNameTip: '显示在网页 Tab 的平台名称',
    websiteSlogan: '欢迎语',
    websiteSloganPlaceholder: '请输入欢迎语',
    websiteSloganTip: '产品 Logo 下的欢迎语',
    defaultSlogan: '欢迎使用 MaxKB 智能知识库问答系统',
    logoDefaultTip: '默认为 MaxKB 登录界面，支持自定义设置',
    defaultTip: '默认为 MaxKB 平台界面，支持自定义设置',
    platformSetting: '平台设置',
    showUserManual: '显示用户手册',
    showForum: '显示论坛求助',
    showProject: '显示项目地址',
    urlPlaceholder: '请输入 URL 地址',
    abandonUpdate: '放弃更新',
    saveAndApply: '保存并应用',
    fileMessageError: '文件大小超过 10M',
    saveSuccess: '外观设置成功'
  },
  email: {
    title: '邮箱设置',
    smtpHost: 'SMTP Host',
    smtpHostPlaceholder: '请输入 SMTP Host',
    smtpPort: 'SMTP Port',
    smtpPortPlaceholder: '请输入 SMTP Port',
    smtpUser: 'SMTP 账户',
    smtpUserPlaceholder: '请输入 SMTP 账户',
    sendEmail: '发件人邮箱',
    sendEmailPlaceholder: '请输入发件人邮箱',
    smtpPassword: '发件人密码',
    smtpPasswordPlaceholder: '请输入发件人密码',
    enableSSL: '启用 SSL（如果 SMTP 端口是 465，通常需要启用 SSL）',
    enableTLS: '启用 TLS（如果 SMTP 端口是 587，通常需要启用 TLS）'
  }
}
