export default {
  title: '概覽',
  appInfo: {
    header: '應用資訊',
    publicAccessLink: '公開訪問連結',
    openText: '開',
    closeText: '關',
    copyLinkText: '複製連結',
    refreshLinkText: '重新整理連結',
    demo: '示範',
    embedThirdParty: '嵌入第三方',
    accessRestrictions: '訪問限制',
    displaySetting: '顯示設定',
    apiAccessCredentials: 'API 存取憑證',
    apiKey: 'API Key',
    refreshToken: {
      msgConfirm1: '是否重新產生公開訪問連結?',
      msgConfirm2:
        '重新產生公開訪問連結會影響嵌入第三方腳本變更，需要將新腳本重新嵌入第三方，請謹慎操作！',
      refreshSuccess: '重新整理成功'
    },
    APIKeyDialog: {
      saveSettings: '儲存設定',
      msgConfirm1: '是否刪除API Key',
      msgConfirm2: '刪除API Key後將無法恢復，請確認是否刪除？',
      enabledSuccess: '已啟用',
      disabledSuccess: '已停用'
    },
    EditAvatarDialog: {
      title: '應用頭像',
      customizeUpload: '自訂上傳',
      upload: '上傳',
      default: '預設logo',
      custom: '自訂',
      sizeTip: '建議尺寸 32*32，支援 JPG、PNG、GIF，大小不超過 10 MB',
      fileSizeExceeded: '檔案大小超過 10 MB',
      uploadImagePrompt: '請上傳一張圖片'
    },
    EmbedDialog: {
      embedDialogTitle: '嵌入第三方',
      fullscreenModeTitle: '全螢幕模式',
      copyInstructions: '複製以下程式碼進行嵌入',
      floatingModeTitle: '浮窗模式'
    },
    LimitDialog: {
      dialogTitle: '訪問限制',
      showSourceLabel: '顯示知識來源',
      clientQueryLimitLabel: '每個用戶端提問限制',
      timesDays: '次/天',
      authentication: '身份驗證',
      authenticationValue: '驗證密碼',
      whitelistLabel: '白名單',
      whitelistPlaceholder:
        '請輸入允許嵌入第三方的來源位址，一行一個，如：\nhttp://127.0.0.1:5678\nhttps://dataease.io'
    },
    SettingAPIKeyDialog: {
      dialogTitle: '設定',
      allowCrossDomainLabel: '允許跨域位址',
      crossDomainPlaceholder:
        '請輸入允許的跨域位址，開啟後不輸入跨域位址則不限制。\n跨域位址一行一個，如：\nhttp://127.0.0.1:5678 \nhttps://dataease.io',
    },
    SettingDisplayDialog: {
      dialogTitle: '顯示設定',
      showSourceLabel: '顯示知識來源',
      showExecutionDetail: '顯示執行細節',
      restoreDefault: '恢復預設',
      customThemeColor: '自訂主題色',
      headerTitleFontColor: '標頭標題字體顏色',
      default: '預設',
      askUserAvatar: '提問用戶頭像',
      replace: '取代',
      imageMessage: '建議尺寸 32*32，支援 JPG、PNG、GIF，大小不超過 10 MB',
      AIAvatar: 'AI 回覆頭像',
      floatIcon: '浮窗入口圖示',
      iconDefaultPosition: '圖示預設位置',
      iconPosition: {
        left: '左',
        right: '右',
        bottom: '下',
        top: '上'
      },
      draggablePosition: '可拖曳位置',
      showHistory: '顯示歷史紀錄',
      displayGuide: '顯示引導圖(浮窗模式)',
      disclaimer: '免責聲明',
      disclaimerValue: '「以上內容均由 AI 生成，僅供參考和借鏡」'
    }
  },
  monitor: {
    monitoringStatistics: '監控統計',
    customRange: '自訂範圍',
    startDatePlaceholder: '開始時間',
    endDatePlaceholder: '結束時間',
    pastDayOptions: {
      past7Days: '過去7天',
      past30Days: '過去30天',
      past90Days: '過去90天',
      past183Days: '過去半年',
      other: '自訂义'
    },
    charts: {
      customerTotal: '用戶總數',
      customerNew: '用戶新增數',
      queryCount: '提問次數',
      tokensTotal: 'Tokens 總數',
      userSatisfaction: '用戶滿意度',
      approval: '贊同',
      disapproval: '反對'
    }
  }
}
