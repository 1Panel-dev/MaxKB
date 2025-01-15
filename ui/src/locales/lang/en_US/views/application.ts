export default {
  title: 'Applications',
  createApplication: 'Create Application',
  importApplication: 'Import Application',
  copyApplication: 'Copy Application',
  workflow: 'WORKFLOW',
  simple: 'SIMPLE',
  searchBar: {
    placeholder: 'Search by name'
  },

  setting: {
    demo: 'Demo'
  },
  delete: {
    confirmTitle: 'Are you sure you want to delete this application?',
    confirmMessage:
      'Deleting this application will no longer provide its services. Please proceed with caution.'
  },
  tip: {
    ExportError: 'Export Failed',
    professionalMessage:
      'The Community Edition supports up to 5 applications. If you need more applications, please upgrade to the Professional Edition.',
    saveErrorMessage: 'Saving failed, please check your input or try again later',
    loadingErrorMessage: 'Failed to load configuration, please check your input or try again later'
  },

  applicationForm: {
    title: {
      info: 'Application Information',
      apptest: 'Debug Preview',
      copy: 'copy'
    },
    form: {
      appName: {
        label: 'Application Name',
        placeholder: 'Please enter the application name',
        requiredMessage: 'Application name is required'
      },
      appDescription: {
        label: 'Application Description',
        placeholder:
          'Describe the application scenario and use, e.g.: XXX assistant answering user questions about XXX product usage'
      },
      appType: {
        label: 'Please select the application type',
        simplePlaceholder: 'Suitable for beginners to create assistant.',
        workflowPlaceholder: 'Suitable for advanced users to customize the workflow of assistant'
      },
      aiModel: {
        label: 'AI Model',
        placeholder: 'Please select an AI model'
      },
      roleSettings: {
        label: 'Role settings',
        placeholder: 'You are xxx assistant'
      },

      prompt: {
        label: 'Prompt',
        noReferences: '（No references Knowledge）',
        references: ' (References Knowledge)',
        placeholder: 'Please enter prompt',
        requiredMessage: 'Please enter prompt',
        noReferencesTooltip:
          'By adjusting the content of the prompt, you can guide the direction of the large model conversation. This prompt will be fixed at the beginning of the context. Variables used: {question} is the question posed by the user.',
        referencesTooltip:
          'By adjusting the content of the prompt, you can guide the direction of the large model conversation. This prompt will be fixed at the beginning of the context. Variables used: {data} carries known information from the knowledge base; {question} is the question posed by the user.',
        defaultPrompt: `Known information: {data}
          Question: {question}
           Response requirements: 
           - Please use concise and professional language to answer the user's question.
           `
      },
      historyRecord: {
        label: 'Historical chat records'
      },
      relatedKnowledge: {
        label: 'Related Knowledge Base',
        placeholder: 'Associated knowledge bases are displayed here'
      },
      multipleRoundsDialogue: 'Multiple Rounds Dialogue',

      prologue: 'Prologue',
      defaultPrologue:
        'Hello, I am XXX Assistant. You can ask me questions about using XXX.\n- What are the main features of MaxKB?\n- Which large language models does MaxKB support?\n- What document types does MaxKB support?',
      problemOptimization: {
        label: 'Problem Optimization',
        tooltip:
          'Optimize the current question based on historical chat to better match knowledge points.'
      },

      voiceInput: {
        label: 'Voice input',
        placeholder: 'Please select a speech recognition model',
        requiredMessage: 'Please select a speech input model',
        autoSend: 'Automatic sending'
      },
      voicePlay: {
        label: 'Voice playback',
        placeholder: 'Please select a speech synthesis model',
        requiredMessage: 'Please select a speech playback model',
        autoPlay: 'Automatic playback',
        browser: 'Browser playback (free)',
        tts: 'TTS Model',
        listeningTest: 'Preview'
      }
    },
    buttons: {
      publish: 'Save&Publish',
      addModel: 'Add Model'
    },
    dialog: {
      addDataset: 'Add Related Knowledge Base',
      addDatasetPlaceholder: 'The selected knowledge bases must use the same embedding model',
      selected: 'Selected',
      countDataset: 'Knowledge',

      selectSearchMode: 'Search Mode',
      vectorSearch: 'Vector Search',
      vectorSearchTooltip:
        'Vector search is a retrieval method based on vector distance calculations, suitable for large data volumes in the knowledge base.',
      fullTextSearch: 'Full-text Search',
      fullTextSearchTooltip:
        'Full-text search is a retrieval method based on text similarity, suitable for small data volumes in the knowledge base.',
      hybridSearch: 'Hybrid Search',
      hybridSearchTooltip:
        'Hybrid search is a retrieval method based on both vector and text similarity, suitable for medium data volumes in the knowledge base.',
      similarityThreshold: 'Similarity Threshold',
      topReferences: 'Top N References',
      maxCharacters: 'Maximum Characters per Reference',
      noReferencesAction: 'When there are no knowledge base references',
      continueQuestioning: 'Continue Questioning AI Model',
      provideAnswer: 'Provide a Specific Answer',
      designated_answer:
        'Hello, I am XXX Assistant. My knowledge base only contains information related to XXX products. Please rephrase your question.',
      defaultPrompt1:
        "The content inside the parentheses () represents the user's question. Based on the context, please speculate and complete the user's question ({question}). The requirement is to output a completed question and place it",
      defaultPrompt2: 'tag'
    }
  },
  applicationAccess: {
    title: 'Application Access',
    wecom: 'WeCom',
    wecomTip: 'Create WeCom intelligent applications',
    dingtalk: 'DingTalk',
    dingtalkTip: 'Create DingTalk intelligent applications',
    wechat: 'WeChat',
    wechatTip: 'Create WeChat intelligent applications',
    lark: 'Lark',
    larkTip: 'Create Lark intelligent applications',
    setting: 'Setting',
    info: 'Application Information',
    callback: 'Callback Address',
    callbackTip: 'Please fill in the callback address',
    wecomPlatform: 'WeCom Open Platform',
    wechatPlatform: 'WeChat Open Platform',
    dingtalkPlatform: 'DingTalk Open Platform',
    larkPlatform: 'Lark Open Platform',
    wecomSetting: {
      title: 'WeCom Configuration',
      cropId: 'Crop ID',
      cropIdPlaceholder: 'Please enter Crop ID',
      agentIdPlaceholder: 'Please enter Agent ID',
      secretPlaceholder: 'Please enter Secret',
      tokenPlaceholder: 'Please enter Token',
      encodingAesKeyPlaceholder: 'Please enter EncodingAESKey',
      authenticationSuccessful: 'Authentication successful',
      urlInfo:
        '-Application management-Self-built-Created application-Receive messages-Set the "URL" received by the API'
    },
    dingtalkSetting: {
      title: 'DingTalk Configuration',
      clientIdPlaceholder: 'Please enter Client ID',
      clientSecretPlaceholder: 'Please enter Client Secret',
      urlInfo:
        '-On the robot page, set the "Message Receiving Mode" to HTTP mode, and fill in the above URL into the "Message Receiving Address"'
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
        '-Settings and Development-Basic Configuration-"Server Address URL" in Server Configuration'
    },
    larkSetting: {
      title: 'Lark Configuration',
      appIdPlaceholder: 'Please enter App ID',
      appSecretPlaceholder: 'Please enter App Secret',
      verificationTokenPlaceholder: 'Please enter Verification Token',
      urlInfo:
        '-Events and callbacks - event configuration - configure the "request address" of the subscription method'
    },
    copyUrl: 'Copy the link and fill it in'
  },
  hitTest: {
    title: 'Hit testing',
    text: 'Ensure effective response by matching paragraphs to user inquiries.',
    emptyMessage1: 'The matching paragraph is displayed here',
    emptyMessage2: 'No matching sections found'
  }
}
