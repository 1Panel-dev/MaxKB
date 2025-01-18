import type { result } from 'lodash'

export default {
  node: '节点',
  baseComponent: '基础组件',
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
    copyParam: '复制参数'
  },
  tip: {
    publicSuccess: '发布成功',
    noData: '没有找到相关结果',
    nameMessage: '名字不能为空！',
    onlyRight: '只允许从右边的锚点连出',
    notRecyclable: '不可循环连线',
    onlylest: '只允许连接左边的锚点',
    applicationNodeError: '该应用不可用',
    functionNodeError: '该函数不可用',
    repeatedNodeError: '节点名称已存在！',
    cannotCopy: '不能被复制',
    copyError: '已复制节点'
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
    global: '全局变量',
    Referencing: '引用变量',
    ReferencingRequired: '引用变量必填',
    ReferencingError: '引用变量错误',
    NoReferencing: '不存在的引用变量'
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
      label: '基本信息'
    },
    aiChatNode: {
      label: 'AI 对话',
      text: '与 AI 大模型进行对话',
      answer: 'AI 回答内容'
    },
    searchDatasetNode: {
      label: '知识库检索',
      text: '关联知识库，查找与问题相关的分段',
      paragraph_list: '检索结果的分段列表',
      is_hit_handling_method_list: '满足直接回答的分段列表',
      result: '检索结果',
      directly_return: '满足直接回答的分段内容'
    },
    questionNode: {
      label: '问题优化',
      text: '根据历史聊天记录优化完善当前问题，更利于匹配知识库分段',
      result: '问题优化结果'
    },
    conditionNode: {
      label: '判断器',
      text: '根据不同条件执行不同的节点',
      branch_name: '分支名称'
    },
    replyNode: {
      label: '指定回复',
      text: '指定回复内容，引用变量会转换为字符串进行输出',
      content: '内容'
    },
    rerankerNode: {
      label: '多路召回',
      text: '使用重排模型对多个知识库的检索结果进行二次召回',
      result_list: '重排结果列表',
      result: '重排结果'
    },
    formNode: {
      label: '表单收集',
      text: '在问答过程中用于收集用户信息，可以根据收集到表单数据执行后续流程',
      form_content_format: `你好，请先填写下面表单内容：
{{form}}
填写后请点击【提交】按钮进行提交。`,
      form_data: '表单全部内容'
    },
    documentExtractNode: {
      label: '文档内容提取',
      text: '提取文档中的内容',
      content: '文档内容'
    },
    imageUnderstandNode: {
      label: '图片理解',
      text: '识别出图片中的对象、场景等信息回答用户问题',
      answer: 'AI 回答内容'
    },
    imageGenerateNode: {
      label: '图片生成',
      text: '根据提供的文本内容生成图片',
      answer: 'AI 回答内容',
      image: '图片'
    },
    speechToTextNode: {
      label: '语音转文本',
      text: '将音频通过语音识别模型转换为文本'
    },
    textToSpeechNode: {
      label: '文本转语音',
      text: '将文本通过语音合成模型转换为音频'
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
    len_lt: '长度小于'
  }
}
