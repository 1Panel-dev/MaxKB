export default {
  noHistory: '暂无历史记录',
  createChat: '新建对话',
  history: '历史记录',
  only20history: '仅显示最近 20 条对话',
  question_count: '条提问',
  exportRecords: '导出聊天记录',
  chatId: '对话 ID',
  userInput: '用户输入',
  quote: '引用',
  download: '点击下载文件',
  passwordValidator: {
    title: '请输入密码打开链接',
    errorMessage1: '密码不能为空',
    errorMessage2: '密码错误'
  },
  operation: {
    play: '点击播放',
    pause: '停止',
    regeneration: '换个答案',
    like: '赞同',
    cancelLike: '取消赞同',
    oppose: '反对',
    cancelOppose: '取消反对',
    continue: '继续',
    stopChat: '停止回答'
  },

  tip: {
    error500Message: '抱歉，当前正在维护，无法提供服务，请稍后再试！',
    errorIdentifyMessage: '无法识别用户身份',
    errorLimitMessage: '抱歉，您的提问已达到最大限制，请明天再来吧！',
    answerMessage: '抱歉，没有查找到相关内容，请重新描述您的问题或提供更多信息。',
    stopAnswer: '已停止回答',
    answerLoading: '回答中',
    recorderTip: `<p>该功能需要使用麦克风，浏览器禁止不安全页面录音，解决方案如下：<br/>
1、可开启 https 解决；<br/>
2、若无 https 配置则需要修改浏览器安全配置，Chrome 设置如下：<br/>
(1) 地址栏输入chrome://flags/#unsafely-treat-insecure-origin-as-secure；<br/>
(2) 将 http 站点配置在文本框中，例如: http://127.0.0.1:8080。</p>`,
    recorderError: '录音失败',
    confirm: '我知道了',
    requiredMessage: '请填写所有必填字段',
    inputParamMessage1: '请在URL中填写参数',
    inputParamMessage2: '的值',
    prologueMessage: '抱歉，当前正在维护，无法提供服务，请稍后再试！'
  },
  inputPlaceholder: {
    speaking: '说话中',
    recorderLoading: '转文字中',
    default: '请输入问题，Ctrl+Enter 换行'
  },
  uploadFile: {
    label: '上传文件',
    most: '最多',
    limit: '个，每个文件限制',
    fileType: '文件类型',
    tipMessage: '请在文件上传配置中选择文件类型',
    limitMessage1: '最多上传',
    limitMessage2: '个文件',
    sizeLimit: '单个文件大小不能超过',
    imageMessage: '请解析图片内容',
    errorMessage: '上传失败'
  },
  executionDetails: {
    title: '执行详情',
    paramOutputTooltip: '每个文档仅支持预览500字',
    audioFile: '语音文件',
    searchContent: '检索内容',
    searchResult: '检索结果',
    conditionResult: '判断结果',
    currentChat: '本次对话',
    answer: 'AI 回答',
    replyContent: '回复内容',
    textContent: '文本内容',
    input: '输入',
    output: '输出',
    rerankerContent: '重排内容',
    rerankerResult: '重排结果',
    paragraph: '分段',
    noSubmit: '用户未提交',
    errMessage: '错误日志'
  },
  KnowledgeSource: {
    title: '知识来源',
    referenceParagraph: '引用分段',
    consume: '消耗tokens',
    consumeTime: '耗时'
  },
  paragraphSource: {
    title: '知识库引用',
    question: '用户问题',
    optimizationQuestion: '优化后问题'
  }
}
