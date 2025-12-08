export default {
  node: '节点',
  nodeName: '节点名称',
  baseComponent: '基础组件',
  nodeSetting: '节点设置',
  workflow: '工作流',
  searchBar: {
    placeholder: '按名称搜索',
  },
  info: {
    previewVersion: '预览版本：',
    saveTime: '保存时间：',
  },
  setting: {
    restoreVersion: '恢复版本',
    restoreCurrentVersion: '恢复此版本',
    addComponent: '添加组件',
    releaseHistory: '发布历史',
    autoSave: '自动保存',
    latestRelease: '最近发布',
    copyParam: '复制参数',
    debug: '调试',
    exit: '直接退出',
    exitSave: '保存并退出',
  },
  tip: {
    noData: '没有找到相关结果',
    nameMessage: '名字不能为空！',
    onlyRight: '只允许从右边的锚点连出',
    notRecyclable: '不可循环连线',
    onlyLeft: '只允许连接左边的锚点',
    applicationNodeError: '该应用不可用',
    toolNodeError: '该工具不可用',
    repeatedNodeError: '节点名称已存在！',
    cannotCopy: '不能被复制',
    copyError: '已复制节点',
    paramErrorMessage: '参数已存在: ',
    saveMessage: '当前的更改尚未保存，是否保存后退出?',
  },
  delete: {
    confirmTitle: '确定删除该节点？',
    deleteMessage: '节点不允许删除',
  },
  control: {
    zoomOut: '缩小',
    zoomIn: '放大',
    fitView: '适应',
    retract: '收起全部节点',
    extend: '展开全部节点',
    beautify: '一键美化',
  },
  variable: {
    global: '全局变量',
    chat: '会话变量',
    Referencing: '引用变量',
    ReferencingRequired: '引用变量必填',
    ReferencingError: '引用变量错误',
    NoReferencing: '不存在的引用变量',
    placeholder: '请选择变量',
    inputPlaceholder: '请输入变量',
    loop: '循环变量',
  },
  condition: {
    title: '执行条件',
    front: '前置',
    AND: '所有',
    OR: '任一',
    text: '连线节点执行完，执行当前节点',
  },
  validate: {
    startNodeRequired: '开始节点必填',
    startNodeOnly: '开始节点只能有一个',
    baseNodeRequired: '基本信息节点必填',
    baseNodeOnly: '基本信息节点只能有一个',
    notInWorkFlowNode: '未在流程中的节点',
    noNextNode: '不存在的下一个节点',
    nodeUnavailable: '节点不可用',
    needConnect1: '节点的',
    needConnect2: '分支需要连接',
    cannotEndNode: '节点不能当做结束节点',
    loopNodeBreakNodeRequired: '无限循环 必须存在 Break 节点',
  },
  nodes: {
    classify: {
      aiCapability: 'AI能力',
      businessLogic: '业务逻辑',
      other: '其他',
      dataProcessing: '数据处理',
    },
    startNode: {
      label: '开始',
      question: '用户问题',
      currentTime: '当前时间',
    },
    baseNode: {
      label: '基本信息',
      appName: {
        label: '应用名称',
      },
      appDescription: {
        label: '应用描述',
      },
      fileUpload: {
        label: '文件上传',
        tooltip: '开启后，问答页面会显示上传文件的按钮。',
      },
      FileUploadSetting: {
        title: '文件上传设置',
        maxFiles: '单次上传最多文件数',
        fileLimit: '每个文件最大（MB）',
        fileUploadType: {
          label: '上传的文件类型',
          documentText: '需要使用“文档内容提取”节点解析文档内容',
          imageText: '需要使用“视觉模型”节点解析图片内容',
          audioText: '需要使用“语音转文本”节点解析音频内容',
          videoText: '需要使用“视频理解”节点解析视频内容',
          otherText: '需要自行解析该类型文件',
        },
      },
    },
    aiChatNode: {
      label: 'AI 对话',
      text: '与 AI 大模型进行对话',
      answer: 'AI 回答内容',
      returnContent: {
        label: '返回内容',
        tooltip: `关闭后该节点的内容则不输出给用户。
                  如果你想让用户看到该节点的输出内容，请打开开关。`,
      },
      defaultPrompt: '已知信息',
      think: '思考过程',
      historyMessage: '历史聊天记录',
    },
    searchKnowledgeNode: {
      label: '知识库检索',
      text: '关联知识库，查找与问题相关的分段',
      paragraph_list: '检索结果的分段列表',
      is_hit_handling_method_list: '满足直接回答的分段列表',
      result: '检索结果',
      directly_return: '满足直接回答的分段内容',
      searchParam: '检索参数',
      showKnowledge: {
        label: '结果显示在知识来源中',
        requiredMessage: '请设置参数',
      },
      searchQuestion: {
        label: '检索问题',
        placeholder: '请选择检索问题',
        requiredMessage: '请选择检索问题',
      },
    },
    searchDocumentNode: {
      label: '文档标签检索',
      text: '从设定的检索范围中，根据文档标签检索出满足条件的文档',
      selectKnowledge: '检索范围',
      searchSetting: '检索设置',
      custom: '手动',
      customTooltip: '手动设置标签过滤条件',
      auto: '自动',
      autoTooltip: '根据检索问题自动匹配文档标签',
      document_list: '文档列表',
      knowledge_list: '知识库列表',
      result: '检索结果',
      searchParam: '检索参数',
      select_variable: '选择变量',
      valueMessage: `值或变量`,
      showKnowledge: {
        label: '结果显示在知识来源中',
        requiredMessage: '请设置参数',
      },
      searchQuestion: {
        label: '检索问题',
        placeholder: '请选择检索问题',
        requiredMessage: '请选择检索问题',
      },
    },
    questionNode: {
      label: '问题优化',
      text: '根据历史聊天记录优化完善当前问题，更利于匹配知识库分段',
      result: '问题优化结果',
      systemDefault: `# 角色
你是一位问题优化大师，擅长根据上下文精准揣测用户意图，并对用户提出的问题进行优化。

## 技能
### 技能 1: 优化问题
2. 接收用户输入的问题。
3. 依据上下文仔细分析问题含义。
4. 输出优化后的问题。

## 限制:
- 仅返回优化后的问题，不进行额外解释或说明。
- 确保优化后的问题准确反映原始问题意图，不得改变原意。`,
    },
    conditionNode: {
      label: '判断器',
      text: '根据不同条件执行不同的节点',
      branch_name: '分支名称',
      conditions: {
        label: '条件',
        info: '符合以下',
        requiredMessage: '请选择条件',
      },
      valueMessage: '请输入值',
      addCondition: '添加条件',
      addBranch: '添加分支',
    },
    replyNode: {
      label: '指定回复',
      text: '指定回复内容，引用变量会转换为字符串进行输出',
      replyContent: '回复内容',
    },
    rerankerNode: {
      label: '多路召回',
      text: '使用重排模型对多个知识库的检索结果进行二次召回',
      result_list: '重排结果列表',
      result: '重排结果',
      rerankerContent: {
        label: '重排内容',
        requiredMessage: '请选择重排内容',
      },
      higher: '高于',
      ScoreTooltip: 'Score越高相关性越强。',
      max_paragraph_char_number: '最大引用字符数',
      reranker_model: {
        label: '重排模型',
        placeholder: '请选择重排模型',
      },
    },
    formNode: {
      label: '表单收集',
      text: '在问答过程中用于收集用户信息，可以根据收集到表单数据执行后续流程',
      form_content_format1: '你好，请先填写下面表单内容：',
      form_content_format2: '填写后请点击【提交】按钮进行提交。',
      form_data: '表单全部内容',
      formContent: {
        label: '表单输出内容',
        requiredMessage: '请表单输出内容',
        tooltip: '设置执行该节点输出的内容，{ form } 为表单的占位符。',
      },
      formAllContent: '表单全部内容',
      formSetting: '表单配置',
    },
    documentExtractNode: {
      label: '文档内容提取',
      text: '提取文档中的内容',
      content: '文档内容',
    },
    imageUnderstandNode: {
      label: '图片理解',
      text: '识别出图片中的对象、场景等信息回答用户问题',
      answer: 'AI 回答内容',
      model: {
        label: '视觉模型',
        requiredMessage: '请选择视觉模型',
      },
      image: {
        label: '选择图片',
        requiredMessage: '请选择图片',
      },
    },
    variableAggregationNode: {
      label: '变量聚合',
      text: '按聚合策略聚合每组的变量',
      Strategy: '聚合策略',
      placeholder: '返回每组的第一个非空值',
      placeholder1: '返回每组变量的集合',
      group: {
        noneError: '名称不能为空',
        dupError: '名称不能重复',
      },
      addGroup: '添加分组',
      editGroup: '编辑分组',
    },
    variableAssignNode: {
      label: '变量赋值',
      text: '更新全局变量的值',
      assign: '赋值',
    },
    mcpNode: {
      label: 'MCP 调用',
      text: '通过SSE/Streamable HTTP方式执行MCP服务中的工具',
      getToolsSuccess: '获取工具成功',
      getTool: '获取工具',
      toolParam: '工具参数',
      mcpServerTip: '请输入JSON格式的MCP服务器配置',
      mcpToolTip: '请选择工具',
      configLabel: 'MCP Server Config (仅支持SSE/Streamable HTTP调用方式)',
      reference: '引用MCP',
    },
    imageGenerateNode: {
      label: '图片生成',
      text: '根据提供的文本内容生成图片',
      answer: 'AI 回答内容',
      model: {
        label: '图片生成模型',
        requiredMessage: '请选择图片生成模型',
      },
      prompt: {
        label: '提示词(正向)',
        tooltip: '正向提示词，用来描述生成图像中期望包含的元素和视觉特点',
      },
      negative_prompt: {
        label: '提示词(负向)',
        tooltip: '反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。',
        placeholder: '请描述不想生成的图片内容，比如：颜色、血腥内容',
      },
    },
    textToVideoGenerate: {
      label: '文生视频',
      text: '根据提供的文本内容生成视频',
      answer: 'AI 回答内容',
      model: {
        label: '文生视频模型',
        requiredMessage: '请选择文生视频模型',
      },
      prompt: {
        label: '提示词(正向)',
        tooltip: '正向提示词，用来描述生成视频中期望包含的元素和视觉特点',
      },
      negative_prompt: {
        label: '提示词(负向)',
        tooltip: '反向提示词，用来描述不希望在视频中看到的内容，可以对视频进行限制。',
        placeholder: '请描述不想生成的视频内容，比如：颜色、血腥内容',
      },
    },
    videoUnderstandNode: {
      label: '视频理解',
      text: '识别出视频中的对象、场景等信息回答用户问题',
      answer: 'AI 回答内容',
      model: {
        label: '视觉模型',
        requiredMessage: '请选择视觉模型',
      },
      image: {
        label: '选择视频',
        requiredMessage: '请选择视频',
      },
    },
    imageToVideoGenerate: {
      label: '图生视频',
      text: '根据提供的图片生成视频',
      answer: 'AI 回答内容',
      model: {
        label: '图生视频模型',
        requiredMessage: '请选择图生视频模型',
      },
      prompt: {
        label: '提示词(正向)',
        tooltip: '正向提示词，用来描述生成视频中期望包含的元素和视觉特点',
      },
      negative_prompt: {
        label: '提示词(负向)',
        tooltip: '反向提示词，用来描述不希望在视频中看到的内容，可以对视频进行限制。',
        placeholder: '请描述不想生成的视频内容，比如：颜色、血腥内容',
      },
      first_frame: {
        label: '首帧图片',
        requiredMessage: '请选择首帧图片',
      },
      last_frame: {
        label: '尾帧图片',
        requiredMessage: '请选择尾帧图片',
      },
    },
    speechToTextNode: {
      label: '语音转文本',
      text: '将音频通过语音识别模型转换为文本',
      stt_model: {
        label: '语音识别模型',
      },
      audio: {
        label: '选择语音文件',
        placeholder: '请选择语音文件',
      },
    },
    textToSpeechNode: {
      label: '文本转语音',
      text: '将文本通过语音合成模型转换为音频',
      tts_model: {
        label: '语音合成模型',
      },
      content: {
        label: '选择文本内容',
      },
    },
    toolNode: {
      label: '自定义工具',
      text: '通过执行自定义脚本，实现数据处理',
    },
    intentNode: {
      label: '意图识别',
      text: '将用户问题与用户预设的意图分类进行匹配',
      other: '其他',
      error2: '意图重复',
      placeholder: '请选择分类项',
      classify: {
        label: '意图分类',
        placeholder: '请输入',
      },
      input: {
        label: '输入',
      },
    },
    applicationNode: {
      label: '应用节点',
    },
    loopNode: {
      label: '循环节点',
      text: '通过设置循环次数和逻辑，重复执行一系列任务',
      loopType: {
        label: '循环类型',
        requiredMessage: '请选择循环类型',
        arrayLoop: '数组循环',
        numberLoop: '指定次数循环',
        infiniteLoop: '无限循环',
      },
      loopNumber: {
        label: '循环次数',
        requiredMessage: '循环次数必填',
      },
      loopArray: {
        label: '循环数组',
        requiredMessage: '循环数组必填',
        placeholder: '请选择循环数组',
      },
      loopSetting: '循环设置',
      loopDetail: '循环详情',
    },
    loopStartNode: {
      label: '循环开始',
      loopIndex: '下标',
      loopItem: '循环元素',
    },
    loopBodyNode: {
      label: '循环体',
      text: '循环体',
    },
    loopContinueNode: {
      label: 'Continue',
      text: '用于终止当前循环，执行下次循环',
      isContinue: 'Continue',
    },
    loopBreakNode: {
      label: 'Break',
      text: '终止当前循环，跳出循环体',
      isBreak: 'Break',
    },
    variableSplittingNode: {
      label: '变量拆分',
      text: '通过配置JSON Path 表达式，对输入的 JSON 格式变量进行解析和拆分',
      splitVariables: '拆分变量',
      inputVariables: '输入变量',
      addVariables: '添加变量',
      editVariables: '编辑变量',
      variableListPlaceholder: '请添加拆分变量',
      expression: {
        label: '表达式',
        placeholder: '请输入表达式',
        tooltip: '请使用JSON Path 表达式拆分变量，例如：$.store.book',
      },
    },
    parameterExtractionNode: {
      label: '参数提取',
      text: '利用 AI 模型提取结构化参数',
      extractParameters: {
        label: '提取参数',
        variableListPlaceholder: '请添加提取参数',
        parameterType: '参数类型',
      },
    },
  },
  compare: {
    is_null: '为空',
    is_not_null: '不为空',
    contain: '包含',
    not_contain: '不包含',
    eq: '等于',
    ge: '大于等于',
    gt: '大于',
    le: '小于等于',
    lt: '小于',
    len_eq: '长度等于',
    len_ge: '长度大于等于',
    len_gt: '长度大于',
    len_le: '长度小于等于',
    len_lt: '长度小于',
    is_true: '为真',
    is_not_true: '不为真',
  },
  SystemPromptPlaceholder: '系统提示词，可以引用系统中的变量：如',
  UserPromptPlaceholder: '用户提示词，可以引用系统中的变量：如',
}
