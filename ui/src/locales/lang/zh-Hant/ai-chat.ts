export default {
  noHistory: '暫無歷史記錄',
  createChat: '新建對話',
  history: '歷史記錄',
  only20history: '僅顯示最近 20 條對話',
  question_count: '條提問',
  exportRecords: '導出聊天記錄',
  chatId: '對話 ID',
  userInput: '用戶輸入',
  quote: '引用',
  download: '點擊下載文件',
  passwordValidator: {
    title: '請輸入密碼打開連結',
    errorMessage1: '密碼不能為空',
    errorMessage2: '密碼錯誤'
  },
  operation: {
    play: '點擊播放',
    pause: '停止',
    regeneration: '換個答案',
    like: '贊同',
    cancelLike: '取消贊同',
    oppose: '反對',
    cancelOppose: '取消反對',
    continue: '繼續',
    stopChat: '停止回答'
  },
  tip: {
    error500Message: '抱歉，當前正在維護，無法提供服務，請稍後再試！',
    errorIdentifyMessage: '無法識別用戶身份',
    errorLimitMessage: '抱歉，您的提問已達最大限制，請明天再來吧！',
    answerMessage: '抱歉，沒有查找到相關內容，請重新描述您的問題或提供更多資訊。',
    stopAnswer: '已停止回答',
    answerLoading: '回答中',
    recorderTip: `<p>該功能需要使用麥克風，瀏覽器禁止不安全頁面錄音，解決方案如下：<br/>
1、可開啟 https 解決；<br/>
2、若無 https 配置則需要修改瀏覽器安全配置，Chrome 設定如下：<br/>
(1) 地址欄輸入 chrome://flags/#unsafely-treat-insecure-origin-as-secure；<br/>
(2) 將 http 站點配置在文字框中，例如: http://127.0.0.1:8080。</p>`,
    recorderError: '錄音失敗',
    confirm: '我知道了',
    requiredMessage: '請填寫所有必填欄位',
    inputParamMessage1: '請在 URL 中填寫參數',
    inputParamMessage2: '的值',
    prologueMessage: '抱歉，當前正在維護，無法提供服務，請稍後再試！'
  },
  inputPlaceholder: {
    speaking: '說話中',
    recorderLoading: '轉文字中',
    default: '請輸入問題，Ctrl+Enter 換行'
  },
  uploadFile: {
    label: '上傳文件',
    most: '最多',
    limit: '個，每個文件限制',
    fileType: '文件類型',
    tipMessage: '請在文件上傳配置中選擇文件類型',
    limitMessage1: '最多上傳',
    limitMessage2: '個文件',
    sizeLimit: '單個文件大小不能超過',
    imageMessage: '請解析圖片內容',
    errorMessage: '上傳失敗'
  },
  executionDetails: {
    title: '執行詳細',
    paramOutputTooltip: '每個文件僅支持預覽 500 字',
    audioFile: '語音文件',
    searchContent: '檢索內容',
    searchResult: '檢索結果',
    conditionResult: '判斷結果',
    currentChat: '本次對話',
    answer: 'AI 回答',
    replyContent: '回覆內容',
    textContent: '文本內容',
    input: '輸入',
    output: '輸出',
    rerankerContent: '重排內容',
    rerankerResult: '重排結果',
    paragraph: '段落',
    noSubmit: '用戶未提交',
    errMessage: '錯誤日誌'
  },
  KnowledgeSource: {
    title: '知識來源',
    referenceParagraph: '引用段落',
    consume: '消耗tokens',
    consumeTime: '耗時'
  },
  paragraphSource: {
    title: '知識庫引用',
    question: '用戶問題',
    optimizationQuestion: '優化後問題'
  }
}
