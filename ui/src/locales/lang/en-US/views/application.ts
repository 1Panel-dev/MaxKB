export default {
  title: 'APP',
  createApplication: 'Create Simple APP',
  createWorkFlowApplication: 'Create Workflow APP',
  importApplication: 'Import APP',
  copyApplication: 'Copy APP',
  workflow: 'WORKFLOW',
  simple: 'SIMPLE',
  simplePlaceholder: 'Suitable for beginners to create assistant using form settings',
  workflowPlaceholder:
    'Suitable for advanced users to build complex logic AI assistants using low-code drag-and-drop',
  appTest: 'Debug Preview',
  operation: {
    addModel: 'Add Model',
    toChat: 'Chat',
  },
  delete: {
    confirmTitle: 'Are you sure you want to delete this APP: ',
    confirmMessage:
      'Deleting this APP will no longer provide its services. Please proceed with caution.',
  },
  tip: {
    publishSuccess: 'Published successfully',
    ExportError: 'Export Failed',
    professionalMessage:
      'The Community Edition supports up to 5 APP. If you need more APP, please upgrade to the Professional Edition.',
    saveErrorMessage: 'Saving failed, please check your input or try again later',
    loadingErrorMessage: 'Failed to load configuration, please check your input or try again later',
    noDocPermission: 'No permission to create documents',
  },

  form: {
    appName: {
      label: 'Name',
      placeholder: 'Please enter the APP name',
      requiredMessage: 'APP name is required',
    },
    appDescription: {
      placeholder:
        'Describe the APP scenario and use, e.g.: XXX assistant answering user questions about XXX product usage',
    },
    appType: {
      label: 'Type',
      simplePlaceholder: 'Suitable for beginners to create assistant.',
      workflowPlaceholder: 'Suitable for advanced users to customize the workflow of assistant',
    },
    appTemplate: {
      blankApp: {
        title: 'Blank APP',
      },
      assistantApp: {
        title: 'Knowledge Assistant',
        description: 'Suitable for advanced users to customize the workflow of assistant',
      },
    },
    aiModel: {
      label: 'AI Model',
      placeholder: 'Please select an AI model',
    },
    roleSettings: {
      label: 'System Prompt',
      placeholder:
        'System prompt, you can reference variables in the system: {data} is the segment hit in the knowledge base; {question} is the question asked by the user.',
      tooltip: 'Set the role or instructions for the model to follow',
    },

    prompt: {
      label: 'User Prompt',
      noReferences: '（No references Knowledge）',
      references: ' (References Knowledge)',
      placeholder:
        'User prompt, you can reference variables in the system: {data} is the segment hit in the knowledge base; {question} is the question asked by the user',
      requiredMessage: 'Please enter User prompt',
      tooltip: 'The question or command that the user poses to the model',

      noReferencesTooltip:
        'By adjusting the content of the prompt, you can guide the direction of the large model chat. This prompt will be fixed at the beginning of the context. Variables used: {question} is the question posed by the user.',
      referencesTooltip:
        'By adjusting the content of the prompt, you can guide the direction of the large model chat. This prompt will be fixed at the beginning of the context. Variables used: {data} carries known information from the knowledge; {question} is the question posed by the user.',
      defaultPrompt: `Known information: {data}
        Question: {question}
         Response requirements:
         - Please use concise and professional language to answer the user's question.
         `,
    },
    historyRecord: {
      label: 'Chat History',
    },
    relatedKnowledge: {
      label: 'Related Knowledge',
      placeholder: 'Related knowledge are displayed here',
    },
    multipleRoundsDialogue: 'Multiple Rounds Dialogue',

    prologue: 'Prologue',
    defaultPrologue:
      'Hello, I am XXX Assistant. You can ask me questions about using XXX.\n- What are the main features of XXX?\n- Which LLM does XXX support?\n- What document types does XXX support?',
    problemOptimization: {
      label: 'Questions Optimization',
      tooltip:
        'Optimize the current question based on historical chat to better match knowledge points.',
    },

    voiceInput: {
      label: 'Voice Input',
      placeholder: 'Please select a speech recognition model',
      requiredMessage: 'Please select a speech input model',
      autoSend: 'Automatic Sending',
    },
    voicePlay: {
      label: 'Voice Playback',
      placeholder: 'Please select a speech synthesis model',
      requiredMessage: 'Please select a speech playback model',
      autoPlay: 'Automatic Playback',
      browser: 'Browser Playback (free)',
      tts: 'TTS Model',
      listeningTest: 'Preview',
    },
    reasoningContent: {
      label: 'Output Thinking',
      tooltip:
        "Please set the thinking label based on the model's return, and the content in the middle of the label will be recognized as the thinking process.",
      start: 'Start',
      end: 'End',
    },
    mcp_output_enable: 'Output MCP/Tool Execution Process',
  },
  generateDialog: {
    label: 'Generate',
    generatePrompt: 'Generate Prompt',
    placeholder: 'Please enter the prompt topic',
    title: 'The prompt is displayed here',
    remake: 'Regenerate',
    stop: 'Stop Generating',
    continue: 'Continue Generating',
    replace: 'Replace',
    exit: 'Are you sure you want to exit and discard the AI-generated content?',
    loading: 'Generating...',
  },
  dialog: {
    addKnowledge: 'Add Related Knowledge',
    addKnowledgePlaceholder: 'The selected knowledge must use the same embedding model',
    selectSearchMode: 'Retrieval Mode',
    vectorSearch: 'Vector Search',
    vectorSearchTooltip:
      'Vector search is a retrieval method based on vector distance calculations, suitable for large data volumes in the knowledge.',
    fullTextSearch: 'Full-text Search',
    fullTextSearchTooltip:
      'Full-text search is a retrieval method based on text similarity, suitable for small data volumes in the knowledge.',
    hybridSearch: 'Hybrid Search',
    hybridSearchTooltip:
      'Hybrid search is a retrieval method based on both vector and text similarity, suitable for medium data volumes in the knowledge.',
    similarityThreshold: 'Similarity higher than',
    similarityTooltip: 'The higher the similarity, the stronger the correlation.',
    topReferences: 'Top N Segments',
    maxCharacters: 'Maximum  Characters per Reference',
    noReferencesAction: 'When there are no knowledge references',
    continueQuestioning: 'Continue to ask questions to the Al model',
    provideAnswer: 'Specify Reply Content',
    designated_answer:
      'Hello, I am XXX Assistant. My knowledge only contains information related to XXX products. Please rephrase your question.',
    defaultPrompt1:
      "The content inside the parentheses () represents the user's question. Based on the context, please speculate and complete the user's question ({question}). The requirement is to output a completed question and place it",
    defaultPrompt2: 'tag',
  },
  applicationAccess: {
    title: 'APP Access',
    wecom: 'WeCom',
    wecomTip: 'Create WeCom intelligent APP',
    wecomBot: 'WeCom Bot',
    wecomBotTip: 'Create WeCom intelligent Bot',
    dingtalk: 'DingTalk',
    dingtalkTip: 'Create DingTalk intelligent APP',
    wechat: 'WeChat',
    wechatTip: 'Create WeChat intelligent APP',
    lark: 'Lark',
    larkTip: 'Create Lark intelligent APP',
    setting: 'Setting',
    callback: 'Callback Address',
    callbackTip: 'Please fill in the callback address',
    wecomPlatform: 'WeCom Open Platform',
    wechatPlatform: 'WeChat Open Platform',
    dingtalkPlatform: 'DingTalk Open Platform',
    larkPlatform: 'Lark Open Platform',
    slack: 'Slack',
    slackTip: 'Create Slack intelligent APP',
    wecomSetting: {
      title: 'WeCom Configuration',
      cropId: 'Crop ID',
      cropIdPlaceholder: 'Please enter crop ID',
      agentIdPlaceholder: 'Please enter agent ID',
      secretPlaceholder: 'Please enter secret',
      tokenPlaceholder: 'Please enter token',
      encodingAesKeyPlaceholder: 'Please enter EncodingAESKey',
      authenticationSuccessful: 'Successful',
      urlInfo:
        '-APP management-Self-built-Created APP-Receive messages-Set the "URL" received by the API',
    },
    dingtalkSetting: {
      title: 'DingTalk Configuration',
      clientIdPlaceholder: 'Please enter client ID',
      clientSecretPlaceholder: 'Please enter client secret',
      urlInfo:
        '-On the robot page, set the "Message Receiving Mode" to HTTP mode, and fill in the above URL into the "Message Receiving Address"',
    },
    wechatSetting: {
      title: 'WeChat Configuration',
      appId: 'APP ID',
      appIdPlaceholder: 'Please enter APP ID',
      appSecret: 'APP SECRET',
      appSecretPlaceholder: 'Please enter APP SECRET',
      token: 'TOKEN',
      tokenPlaceholder: 'Please enter TOKEN',
      aesKey: 'Message Encryption Key',
      aesKeyPlaceholder: 'Please enter the message encryption key',
      urlInfo:
        '-Settings and Development-Basic Configuration-"Server Address URL" in server configuration',
    },
    wecomBotSetting: {
      title: 'WeCom Bot Configuration',
      urlInfo: '-Management Tools-Smart Bot-Create Bot-API Mode Create "URL"',
    },
    larkSetting: {
      title: 'Lark Configuration',
      appIdPlaceholder: 'Please enter APP ID',
      appSecretPlaceholder: 'Please enter APP secret',
      verificationTokenPlaceholder: 'Please enter verification token',
      urlInfo:
        '-Events and callbacks - event configuration - configure the "request address" of the subscription method',
    },
    slackSetting: {
      title: 'Slack Configuration',
      signingSecretPlaceholder: 'Please enter signing secret',
      botUserTokenPlaceholder: 'Please enter bot user token',
    },
    copyUrl: 'Copy the link and fill it in',
  },
  hitTest: {
    title: 'Retrieval Testing',
    text: 'Test the hitting effect of the Knowledge based on the given query text.',
    emptyMessage1: 'Retrieval Testing results will show here',
    emptyMessage2: 'No matching sections found',
  },
  publishTime: 'Publish Time',
  publishStatus: 'Publish Status',
}
