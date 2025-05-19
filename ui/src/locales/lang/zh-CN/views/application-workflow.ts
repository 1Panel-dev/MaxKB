export default {
  node: '节点',
  nodeName: '节点名称',
  baseComponent: '基础组件',
  nodeSetting: '节点设置',
  workflow: '工作流',
  searchBar: {
    placeholder: '按名称搜索'
  },
  info: {
    previewVersion: '预览版本：',
    saveTime: '保存时间：'
  },
  setting: {
    restoreVersion: '恢复版本',
    restoreCurrentVersion: '恢复此版本',
    addComponent: '添加组件',
    public: '发布',
    releaseHistory: '发布历史',
    autoSave: '自动保存',
    latestRelease: '最近发布',
    copyParam: '复制参数',
    debug: '调试',
    exit: '直接退出',
    exitSave: '保存并退出'
  },
  tip: {
    publicSuccess: '发布成功',
    noData: '没有找到相关结果',
    nameMessage: '名字不能为空！',
    onlyRight: '只允许从右边的锚点连出',
    notRecyclable: '不可循环连线',
    onlyLeft: '只允许连接左边的锚点',
    applicationNodeError: '该应用不可用',
    functionNodeError: '该函数不可用',
    repeatedNodeError: '节点名称已存在！',
    cannotCopy: '不能被复制',
    copyError: '已复制节点',
    paramErrorMessage: '参数已存在: ',
    saveMessage: '当前的更改尚未保存，是否保存后退出?'
  },
  delete: {
    confirmTitle: '确定删除该节点？',
    deleteMessage: '节点不允许删除'
  },
  control: {
    zoomOut: '缩小',
    zoomIn: '放大',
    fitView: '适应',
    retract: '收起全部节点',
    extend: '展开全部节点',
    beautify: '一键美化'
  },
  variable: {
    label: '变量',
    global: '全局变量',
    Referencing: '引用变量',
    ReferencingRequired: '引用变量必填',
    ReferencingError: '引用变量错误',
    NoReferencing: '不存在的引用变量',
    placeholder: '请选择变量'
  },
  condition: {
    title: '执行条件',
    front: '前置',
    AND: '所有',
    OR: '任一',
    text: '连线节点执行完，执行当前节点'
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
    cannotEndNode: '节点不能当做结束节点'
  },
  nodes: {
    startNode: {
      label: '开始',
      question: '用户问题',
      currentTime: '当前时间'
    },
    baseNode: {
      label: '基本信息',
      appName: {
        label: '应用名称'
      },
      appDescription: {
        label: '应用描述'
      },
      fileUpload: {
        label: '文件上传',
        tooltip: '开启后，问答页面会显示上传文件的按钮。'
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
          otherText: '需要自行解析该类型文件'
        },
        
      }
    },
    aiChatNode: {
      label: 'AI 对话',
      text: '与 AI 大模型进行对话',
      answer: 'AI 回答内容',
      returnContent: {
        label: '返回内容',
        tooltip: `关闭后该节点的内容则不输出给用户。
                  如果你想让用户看到该节点的输出内容，请打开开关。`
      },
      defaultPrompt: '已知信息',
      think: '思考过程'
    },
    searchDatasetNode: {
      label: '知识库检索',
      text: '关联知识库，查找与问题相关的分段',
      paragraph_list: '检索结果的分段列表',
      is_hit_handling_method_list: '满足直接回答的分段列表',
      result: '检索结果',
      directly_return: '满足直接回答的分段内容',
      searchParam: '检索参数',
      searchQuestion: {
        label: '检索问题',
        placeholder: '请选择检索问题',
        requiredMessage: '请选择检索问题'
      }
    },
    questionNode: {
      label: '问题优化',
      text: '根据历史聊天记录优化完善当前问题，更利于匹配知识库分段',
      result: '问题优化结果',
      defaultPrompt1: `根据上下文优化和完善用户问题`,
      defaultPrompt2: `请输出一个优化后的问题。`,
      systemDefault: '你是一个问题优化大师'
    },
    conditionNode: {
      label: '判断器',
      text: '根据不同条件执行不同的节点',
      branch_name: '分支名称',
      conditions: {
        label: '条件',
        info: '符合以下',
        requiredMessage: '请选择条件'
      },
      valueMessage: '请输入值',
      addCondition: '添加条件',
      addBranch: '添加分支'
    },
    replyNode: {
      label: '指定回复',
      text: '指定回复内容，引用变量会转换为字符串进行输出',
      content: '内容',
      replyContent: {
        label: '回复内容',
        custom: '自定义',
        reference: '引用变量'
      }
    },
    rerankerNode: {
      label: '多路召回',
      text: '使用重排模型对多个知识库的检索结果进行二次召回',
      result_list: '重排结果列表',
      result: '重排结果',
      rerankerContent: {
        label: '重排内容',
        requiredMessage: '请选择重排内容'
      },
      higher: '高于',
      ScoreTooltip: 'Score越高相关性越强。',
      max_paragraph_char_number: '最大引用字符数',
      reranker_model: {
        label: '重排模型',
        placeholder: '请选择重排模型'
      }
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
        tooltip: '设置执行该节点输出的内容，{ form } 为表单的占位符。'
      },
      formAllContent: '表单全部内容',
      formSetting: '表单配置'
    },
    documentExtractNode: {
      label: '文档内容提取',
      text: '提取文档中的内容',
      content: '文档内容'
    },
    imageUnderstandNode: {
      label: '图片理解',
      text: '识别出图片中的对象、场景等信息回答用户问题',
      answer: 'AI 回答内容',
      model: {
        label: '视觉模型',
        requiredMessage: '请选择视觉模型'
      },
      image: {
        label: '选择图片',
        requiredMessage: '请选择图片'
      }
    },
    variableAssignNode: {
      label: '变量赋值',
      text: '更新全局变量的值',
      assign: '赋值'
    },
    mcpNode: {
      label: 'MCP 调用',
      text: '通过SSE方式执行MCP服务中的工具',
      getToolsSuccess: '获取工具成功',
      getTool: '获取工具',
      tool: '工具',
      toolParam: '工具参数',
      mcpServerTip: '请输入JSON格式的MCP服务器配置',
      mcpToolTip: '请选择工具',
      configLabel: 'MCP Server Config (仅支持SSE调用方式)'
    },
    imageGenerateNode: {
      label: '图片生成',
      text: '根据提供的文本内容生成图片',
      answer: 'AI 回答内容',
      model: {
        label: '图片生成模型',
        requiredMessage: '请选择图片生成模型'
      },
      prompt: {
        label: '提示词(正向)',
        tooltip: '正向提示词，用来描述生成图像中期望包含的元素和视觉特点'
      },
      negative_prompt: {
        label: '提示词(负向)',
        tooltip: '反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。',
        placeholder: '请描述不想生成的图片内容，比如：颜色、血腥内容'
      }
    },
    speechToTextNode: {
      label: '语音转文本',
      text: '将音频通过语音识别模型转换为文本',
      stt_model: {
        label: '语音识别模型'
      },
      audio: {
        label: '选择语音文件',
        placeholder: '请选择语音文件'
      }
    },
    textToSpeechNode: {
      label: '文本转语音',
      text: '将文本通过语音合成模型转换为音频',
      tts_model: {
        label: '语音识别模型'
      },
      content: {
        label: '选择文本内容'
      }
    },
    functionNode: {
      label: '自定义函数',
      text: '通过执行自定义脚本，实现数据处理'
    },
    applicationNode: {
      label: '应用节点'
    }
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
    is_not_true: '不为真'
  },
  FileUploadSetting: {}
}
