export default {
  title: '应用',
  createApplication: '创建应用',
  importApplication: '导入应用',
  copyApplication: '复制应用',
  workflow: '高级编排',
  simple: '简单配置',
  searchBar: {
    placeholder: '按名称搜索'
  },
  setting: {
    demo: '演示'
  },
  delete: {
    confirmTitle: '是否删除应用：',
    confirmMessage: '删除后该应用将不再提供服务，请谨慎操作。'
  },
  tip: {
    ExportError: '导出失败',
    professionalMessage: '社区版最多支持 5 个应用，如需拥有更多应用，请升级为专业版。',
    saveErrorMessage: '保存失败，请检查输入或稍后再试',
    loadingErrorMessage: '加载配置失败，请检查输入或稍后再试'
  },
  applicationForm: {
    title: {
      appTest: '调试预览',
      copy: '副本'
    },
    form: {
      appName: {
        label: '名称',
        placeholder: '请输入应用名称',
        requiredMessage: '请输入应用名称'
      },
      appDescription: {
        label: '描述',
        placeholder: '描述该应用的应用场景及用途，如：XXX 小助手回答用户提出的 XXX 产品使用问题'
      },
      appType: {
        label: '类型',
        simplePlaceholder: '适合新手创建小助手',
        workflowPlaceholder: '适合高级用户自定义小助手的工作流'
      },
      appTemplate: {
        blankApp: '空白应用',
        assistantApp: '知识库问答助手'
      },
      aiModel: {
        label: 'AI 模型',
        placeholder: '请选择 AI 模型'
      },
      roleSettings: {
        label: '系统角色',
        placeholder: '你是 xxx 小助手'
      },
      prompt: {
        label: '提示词',
        noReferences: ' (无引用知识库)',
        references: ' (引用知识库)',
        placeholder: '请输入提示词',
        requiredMessage: '请输入提示词',
        tooltip:
          '通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头，可以使用变量。',
        noReferencesTooltip:
          '通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。可以使用变量：{question} 是用户提出问题的占位符。',
        referencesTooltip:
          '通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。可以使用变量：{data} 是引用知识库中分段的占位符；{question} 是用户提出问题的占位符。',
        defaultPrompt: `已知信息：{data}
用户问题：{question}
回答要求：
 - 请使用中文回答用户问题`
      },
      historyRecord: {
        label: '历史聊天记录'
      },
      relatedKnowledge: {
        label: '关联知识库',
        placeholder: '关联的知识库展示在这里'
      },
      multipleRoundsDialogue: '多轮对话',

      prologue: '开场白',
      defaultPrologue:
        '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务',

      problemOptimization: {
        label: '问题优化',
        tooltip: '根据历史聊天优化完善当前问题，更利于匹配知识点。'
      },
      voiceInput: {
        label: '语音输入',
        placeholder: '请选择语音识别模型',
        requiredMessage: '请选择语音输入模型',
        autoSend: '自动发送'
      },
      voicePlay: {
        label: '语音播放',
        placeholder: '请选择语音合成模型',
        requiredMessage: '请选择语音播放模型',
        autoPlay: '自动播放',
        browser: '浏览器播放(免费)',
        tts: 'TTS模型',
        listeningTest: '试听'
      },
      reasoningContent: {
        label: '输出思考',
        tooltip: '请根据模型返回的思考标签设置，标签中间的内容将会认定为思考过程',
        start: '开始',
        end: '结束'
      }
    },
    buttons: {
      publish: '保存并发布',

      addModel: '添加模型'
    },

    dialog: {
      addDataset: '添加关联知识库',
      addDatasetPlaceholder: '所选知识库必须使用相同的 Embedding 模型',
      selected: '已选',
      countDataset: '个知识库',

      selectSearchMode: '检索模式',
      vectorSearch: '向量检索',
      vectorSearchTooltip: '向量检索是一种基于向量相似度的检索方式，适用于知识库中的大数据量场景。',
      fullTextSearch: '全文检索',
      fullTextSearchTooltip:
        '全文检索是一种基于文本相似度的检索方式，适用于知识库中的小数据量场景。',
      hybridSearch: '混合检索',
      hybridSearchTooltip:
        '混合检索是一种基于向量和文本相似度的检索方式，适用于知识库中的中等数据量场景。',
      similarityThreshold: '相似度高于',
      similarityTooltip: '相似度越高相关性越强。',
      topReferences: '引用分段数 TOP',
      maxCharacters: '最多引用字符数',
      noReferencesAction: '无引用知识库分段时',
      continueQuestioning: '继续向 AI 模型提问',
      provideAnswer: '指定回答内容',
      designated_answer:
        '你好，我是 XXX 小助手，我的知识库只包含了 XXX 产品相关知识，请重新描述您的问题。',
      defaultPrompt1:
        '()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在',
      defaultPrompt2: '标签中'
    }
  },
  applicationAccess: {
    title: '应用接入',
    wecom: '企业微信应用',
    wecomTip: '打造企业微信智能应用',
    dingtalk: '钉钉应用',
    dingtalkTip: '打造钉钉智能应用',
    wechat: '公众号',
    wechatTip: '打造公众号智能应用',
    lark: '飞书应用',
    larkTip: '打造飞书智能应用',
    slack: 'Slack',
    slackTip: '打造 Slack 智能应用',
    setting: '配置',
    callback: '回调地址',
    callbackTip: '请输入回调地址',
    wecomPlatform: '企业微信后台',
    wechatPlatform: '微信公众平台',
    dingtalkPlatform: '钉钉开放平台',
    larkPlatform: '飞书开放平台',
    wecomSetting: {
      title: '企业微信应用配置',
      cropId: '企业 ID',
      cropIdPlaceholder: '请输入企业 ID',
      agentIdPlaceholder: '请输入Agent ID',
      secretPlaceholder: '请输入Secret',
      tokenPlaceholder: '请输入Token',
      encodingAesKeyPlaceholder: '请输入EncodingAESKey',
      authenticationSuccessful: '认证成功',
      urlInfo: '-应用管理-自建-创建的应用-接收消息-设置 API 接收的 "URL" 中'
    },
    dingtalkSetting: {
      title: '钉钉应用配置',
      clientIdPlaceholder: '请输入Client ID',
      clientSecretPlaceholder: '请输入Client Secret',
      urlInfo: '-机器人页面，设置 "消息接收模式" 为 HTTP模式 ，并把上面URL填写到"消息接收地址"中'
    },
    wechatSetting: {
      title: '公众号应用配置',
      appId: '开发者ID (APP ID)',
      appIdPlaceholder: '请输入开发者ID (APP ID)',
      appSecret: '开发者密钥 (APP SECRET)',
      appSecretPlaceholder: '请输入开发者密钥 (APP SECRET)',
      token: '令牌 (TOKEN)',
      tokenPlaceholder: '请输入令牌 (TOKEN)',
      aesKey: '消息加解密密钥',
      aesKeyPlaceholder: '请输入消息加解密密钥',
      urlInfo: '-设置与开发-基本配置-服务器配置的 "服务器地址URL" 中'
    },
    larkSetting: {
      title: '飞书应用配置',
      appIdPlaceholder: '请输入App ID',
      appSecretPlaceholder: '请输入App Secret',
      verificationTokenPlaceholder: '请输入Verification Token',
      urlInfo: '-事件与回调-事件配置-配置订阅方式的 "请求地址" 中',
      folderTokenPlaceholder: '请输入Folder Token'
    },
    slackSetting: {
      title: 'Slack 应用配置',
      signingSecretPlaceholder: '请输入 Signing Secret',
      botUserTokenPlaceholder: '请输入 Bot User Token'
    },
    copyUrl: '复制链接填入到'
  },
  hitTest: {
    title: '命中测试',
    text: '针对用户提问调试段落匹配情况，保障回答效果。',
    emptyMessage1: '命中段落显示在这里',
    emptyMessage2: '没有命中的分段'
  }
}
