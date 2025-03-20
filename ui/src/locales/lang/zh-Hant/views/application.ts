export default {
  title: '應用',
  createApplication: '建立應用',
  importApplication: '匯入應用',
  copyApplication: '複製應用',
  workflow: '進階編排',
  simple: '簡單配置',
  searchBar: {
    placeholder: '按名稱搜尋'
  },
  setting: {
    demo: '示範'
  },
  delete: {
    confirmTitle: '是否刪除應用：',
    confirmMessage: '刪除後該應用將不再提供服務，請謹慎操作。'
  },
  tip: {
    ExportError: '匯出失敗',
    professionalMessage: '社群版最多支援 5 個應用，如需擁有更多應用，請升級為專業版。',
    saveErrorMessage: '儲存失敗，請檢查輸入或稍後再試',
    loadingErrorMessage: '載入配置失敗，請檢查輸入或稍後再試'
  },
  applicationForm: {
    title: {
      appTest: '調試預覽',
      copy: '副本'
    },
    form: {
      appName: {
        label: '名稱',
        placeholder: '請輸入應用名稱',
        requiredMessage: '請輸入應用名稱'
      },
      appDescription: {
        label: '描述',
        placeholder: '描述該應用的應用場景及用途，如：XXX 小助手回答用戶提出的 XXX 產品使用問題'
      },
      appType: {
        label: '類型',
        simplePlaceholder: '適合新手建立小助手',
        workflowPlaceholder: '適合高階用戶自訂小助手的工作流程'
      },
      appTemplate: {
        blankApp: '空白應用',
        assistantApp: '知識庫問答助手'
      },
      aiModel: {
        label: 'AI 模型',
        placeholder: '請選擇 AI 模型'
      },
      roleSettings: {
        label: '角色設定',
        placeholder: '你是 xxx 小助手'
      },
      prompt: {
        label: '提示詞',
        noReferences: ' (無引用知識庫)',
        references: ' (引用知識庫)',
        placeholder: '請輸入提示詞',
        requiredMessage: '請輸入提示詞',
        tooltip: '透過調整提示詞內容，可以引導大模型對話方向，該提示詞會被固定在上下文的開頭。',

        noReferencesTooltip:
          '透過調整提示詞內容，可以引導大模型對話方向，該提示詞會被固定在上下文的開頭。可以使用變數：{question} 是用戶提出問題的佔位符。',
        referencesTooltip:
          '透過調整提示詞內容，可以引導大模型對話方向，該提示詞會被固定在上下文的開頭。可以使用變數：{data} 是引用知識庫中分段的佔位符；{question} 是用戶提出問題的佔位符。',
        defaultPrompt: `已知資訊：{data}
用戶問題：{question}
回答要求：
 - 請使用中文回答用戶問題`
      },
      historyRecord: {
        label: '歷史對話紀錄'
      },
      relatedKnowledge: {
        label: '關聯知識庫',
        placeholder: '關聯的知識庫展示在這裡'
      },
      multipleRoundsDialogue: '多輪對話',

      prologue: '開場白',
      defaultPrologue:
        '您好，我是 XXX 小助手，您可以向我提出 XXX 使用問題。\n- XXX 主要功能有什麼？\n- XXX 如何收費？\n- 需要轉人工服務',

      problemOptimization: {
        label: '問題優化',
        tooltip: '根據歷史對話優化完善當前問題，更利於匹配知識點。'
      },
      voiceInput: {
        label: '語音輸入',
        placeholder: '請選擇語音辨識模型',
        requiredMessage: '請選擇語音輸入模型',
        autoSend: '自動發送'
      },
      voicePlay: {
        label: '語音播放',
        placeholder: '請選擇語音合成模型',
        requiredMessage: '請選擇語音播放模型',
        autoPlay: '自動播放',
        browser: '瀏覽器播放(免費)',
        tts: 'TTS模型',
        listeningTest: '試聽'
      },
      reasoningContent: {
        label: '輸出思考',
        tooltip: '請根據模型返回的思考標簽設置，標簽中間的內容將會認定爲思考過程',
        start: '開始',
        end: '結束'
      }
    },
    buttons: {
      publish: '儲存並發佈',
      addModel: '新增模型'
    },

    dialog: {
      addDataset: '新增關聯知識庫',
      addDatasetPlaceholder: '所選知識庫必須使用相同的 Embedding 模型',
      selected: '已選',
      countDataset: '個知識庫',

      selectSearchMode: '檢索模式',
      vectorSearch: '向量檢索',
      vectorSearchTooltip: '向量檢索是一種基於向量相似度的檢索方式，適用於知識庫中的大數據量場景。',
      fullTextSearch: '全文檢索',
      fullTextSearchTooltip:
        '全文檢索是一種基於文本相似度的檢索方式，適用於知識庫中的小數據量場景。',
      hybridSearch: '混合檢索',
      hybridSearchTooltip:
        '混合檢索是一種基於向量和文本相似度的檢索方式，適用於知識庫中的中等數據量場景。',
      similarityThreshold: '相似度高於',
      similarityTooltip: '相似度越高相關性越強。',
      topReferences: '引用分段數 TOP',
      maxCharacters: '最多引用字元數',
      noReferencesAction: '無引用知識庫分段時',
      continueQuestioning: '繼續向 AI 模型提問',
      provideAnswer: '指定回答內容',
      designated_answer:
        '你好，我是 XXX 小助手，我的知識庫只包含了 XXX 產品相關知識，請重新描述您的問題。',
      defaultPrompt1:
        '()裡面是用戶問題,根據上下文回答揣測用戶問題({question}) 要求: 輸出一個補全問題,並且放在',
      defaultPrompt2: '標籤中'
    }
  },
  applicationAccess: {
    title: '應用接入',
    wecom: '企業微信應用',
    wecomTip: '打造企業微信智慧應用',
    dingtalk: '釘釘應用',
    dingtalkTip: '打造釘釘智慧應用',
    wechat: '公眾號',
    wechatTip: '打造公眾號智慧應用',
    lark: '飛書應用',
    larkTip: '打造飛書智慧應用',
    slack: 'Slack',
    slackTip: '打造 Slack 智慧應用',
    setting: '配置',
    callback: '回呼位址',
    callbackTip: '請輸入回呼位址',
    wecomPlatform: '企業微信後台',
    wechatPlatform: '微信公众平台',
    dingtalkPlatform: '釘釘開放平台',
    larkPlatform: '飛書開放平台',
    wecomSetting: {
      title: '企業微信應用配置',
      cropId: '企業 ID',
      cropIdPlaceholder: '請輸入企業 ID',
      agentIdPlaceholder: '請輸入Agent ID',
      secretPlaceholder: '請輸入Secret',
      tokenPlaceholder: '請輸入Token',
      encodingAesKeyPlaceholder: '請輸入EncodingAESKey',
      authenticationSuccessful: '認證成功',
      urlInfo: '-應用管理-自建-建立的應用-接收消息-設定 API 接收的 "URL" 中'
    },
    dingtalkSetting: {
      title: '釘釘應用配置',
      clientIdPlaceholder: '請輸入Client ID',
      clientSecretPlaceholder: '請輸入Client Secret',
      urlInfo: '-機器人頁面，設定 "消息接收模式" 為 HTTP模式 ，並把上面URL填寫到"消息接收位址"中'
    },
    wechatSetting: {
      title: '公眾號應用配置',
      appId: '開發者ID (APP ID)',
      appIdPlaceholder: '請輸入開發者ID (APP ID)',
      appSecret: '開發者密鑰 (APP SECRET)',
      appSecretPlaceholder: '請輸入開發者密鑰 (APP SECRET)',
      token: '權杖 (TOKEN)',
      tokenPlaceholder: '請輸入權杖 (TOKEN)',
      aesKey: '消息加解密密鑰',
      aesKeyPlaceholder: '請輸入消息加解密密鑰',
      urlInfo: '-設定與開發-基本配置-伺服器配置的 "伺服器位址URL" 中'
    },
    larkSetting: {
      title: '飛書應用配置',
      appIdPlaceholder: '請輸入App ID',
      appSecretPlaceholder: '請輸入App Secret',
      verificationTokenPlaceholder: '請輸入Verification Token',
      urlInfo: '-事件與回呼-事件配置-配置訂閱方式的 "請求位址" 中',
      folderTokenPlaceholder: '請輸入Folder Token'
    },
    slackSetting: {
      title: 'Slack 應用配置',
      signingSecretPlaceholder: '請輸入 Signing Secret',
      botUserTokenPlaceholder: '請輸入 Bot User Token'
    },
    copyUrl: '複製連結填入到'
  },
  hitTest: {
    title: '命中測試',
    text: '針對用戶提問調試段落匹配情況，保障回答效果。',
    emptyMessage1: '命中的段落顯示在這裡',
    emptyMessage2: '沒有命中的分段'
  }
}
