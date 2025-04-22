export default {
  node: '節點',
  nodeName: '節點名稱',
  baseComponent: '基礎組件',
  nodeSetting: '節點設置',
  workflow: '工作流',
  searchBar: {
    placeholder: '按名稱搜索'
  },
  info: {
    previewVersion: '預覽版本：',
    saveTime: '保存時間：'
  },
  setting: {
    restoreVersion: '恢復版本',
    restoreCurrentVersion: '恢復此版本',
    addComponent: '添加組件',
    public: '發布',
    releaseHistory: '發布歷史',
    autoSave: '自動保存',
    latestRelease: '最近發布',
    copyParam: '複製參數',
    debug: '調試',
    exit: '直接退出',
    exitSave: '保存並退出'
  },
  tip: {
    publicSuccess: '發布成功',
    noData: '沒有找到相關結果',
    nameMessage: '名字不能為空！',
    onlyRight: '只允許從右邊的錨點連出',
    notRecyclable: '不可循環連線',
    onlyLeft: '只允許連接左邊的錨點',
    applicationNodeError: '該應用不可用',
    functionNodeError: '該函數不可用',
    repeatedNodeError: '節點名稱已存在！',
    cannotCopy: '不能被複製',
    copyError: '已複製節點',
    paramErrorMessage: '參數已存在: ',
    saveMessage: '當前修改未保存，是否保存後退出？'
  },
  delete: {
    confirmTitle: '確定刪除該節點？',
    deleteMessage: '節點不允許刪除'
  },
  control: {
    zoomOut: '縮小',
    zoomIn: '放大',
    fitView: '適應',
    retract: '收起全部節點',
    extend: '展開全部節點',
    beautify: '一鍵美化'
  },
  variable: {
    label: '變量',
    global: '全局變量',
    Referencing: '引用變量',
    ReferencingRequired: '引用變量必填',
    ReferencingError: '引用變量錯誤',
    NoReferencing: '不存在的引用變量',
    placeholder: '請選擇變量'
  },
  condition: {
    title: '執行條件',
    front: '前置',
    AND: '所有',
    OR: '任一',
    text: '連線節點執行完，執行當前節點'
  },
  validate: {
    startNodeRequired: '開始節點必填',
    startNodeOnly: '開始節點只能有一個',
    baseNodeRequired: '基本信息節點必填',
    baseNodeOnly: '基本信息節點只能有一個',
    notInWorkFlowNode: '未在流程中的節點',
    noNextNode: '不存在的下一個節點',
    nodeUnavailable: '節點不可用',
    needConnect1: '節點的',
    needConnect2: '分支需要連接',
    cannotEndNode: '節點不能當做結束節點'
  },
  nodes: {
    startNode: {
      label: '開始',
      question: '用戶問題',
      currentTime: '當前時間'
    },
    baseNode: {
      label: '基本信息',
      appName: {
        label: '應用名稱'
      },
      appDescription: {
        label: '應用描述'
      },
      fileUpload: {
        label: '文件上傳',
        tooltip: '開啟後，問答頁面會顯示上傳文件的按鈕。'
      },
      FileUploadSetting: {
        title: '文件上傳設置',
        maxFiles: '單次上傳最多文件數',
        fileLimit: '每個文件最大（MB）',
        fileUploadType: {
          label: '上傳的文件類型',
          documentText: '需要使用「文檔內容提取」節點解析文檔內容',
          imageText: '需要使用「圖片理解」節點解析圖片內容',
          audioText: '需要使用「語音轉文本」節點解析音頻內容',
          otherText: '需要自行解析該類型文件'
        }
      }
    },
    aiChatNode: {
      label: 'AI 對話',
      text: '與 AI 大模型進行對話',
      answer: 'AI 回答內容',
      returnContent: {
        label: '返回內容',
        tooltip: `關閉後該節點的內容則不輸出給用戶。
                  如果你想讓用戶看到該節點的輸出內容，請打開開關。`
      },
      defaultPrompt: '已知信息',
      think: '思考過程'
    },
    searchDatasetNode: {
      label: '知識庫檢索',
      text: '關聯知識庫，查找與問題相關的分段',
      paragraph_list: '檢索結果的分段列表',
      is_hit_handling_method_list: '滿足直接回答的分段列表',
      result: '檢索結果',
      directly_return: '滿足直接回答的分段內容',
      searchParam: '檢索參數',
      searchQuestion: {
        label: '檢索問題',
        placeholder: '請選擇檢索問題',
        requiredMessage: '請選擇檢索問題'
      }
    },
    questionNode: {
      label: '問題優化',
      text: '根據歷史聊天記錄優化完善當前問題，更利於匹配知識庫分段',
      result: '問題優化結果',
      defaultPrompt1: `根據上下文優化和完善用戶問題：`,
      defaultPrompt2: `請輸出一個優化後的問題。`,
      systemDefault: '你是一個問題優化大師'
    },
    conditionNode: {
      label: '判斷器',
      text: '根據不同條件執行不同的節點',
      branch_name: '分支名稱',
      conditions: {
        label: '條件',
        info: '符合以下',
        requiredMessage: '請選擇條件'
      },
      valueMessage: '請輸入值',
      addCondition: '添加條件',
      addBranch: '添加分支'
    },
    replyNode: {
      label: '指定回覆',
      text: '指定回覆內容，引用變量會轉換為字符串進行輸出',
      content: '內容',
      replyContent: {
        label: '回覆內容',
        custom: '自定義',
        reference: '引用變量'
      }
    },
    rerankerNode: {
      label: '多路召回',
      text: '使用重排模型對多個知識庫的檢索結果進行二次召回',
      result_list: '重排結果列表',
      result: '重排結果',
      rerankerContent: {
        label: '重排內容',
        requiredMessage: '請選擇重排內容'
      },
      higher: '高於',
      ScoreTooltip: 'Score越高相關性越強。',
      max_paragraph_char_number: '最大引用字符數',
      reranker_model: {
        label: '重排模型',
        placeholder: '請選擇重排模型'
      }
    },
    formNode: {
      label: '表單收集',
      text: '在問答過程中用於收集用戶信息，可以根據收集到表單數據執行後續流程',
      form_content_format1: '你好，請先填寫下面表單內容：',
      form_content_format2: '填寫後請點擊【提交】按鈕進行提交。',
      form_data: '表單全部內容',
      formContent: {
        label: '表單輸出內容',
        requiredMessage: '請表單輸出內容',
        tooltip: '設置執行該節點輸出的內容，{ form } 為表單的佔位符。'
      },
      formAllContent: '表單全部內容',
      formSetting: '表單配置'
    },
    documentExtractNode: {
      label: '文檔內容提取',
      text: '提取文檔中的內容',
      content: '文檔內容'
    },
    imageUnderstandNode: {
      label: '圖片理解',
      text: '識別出圖片中的物件、場景等信息回答用戶問題',
      answer: 'AI 回答內容',
      model: {
        label: '圖片理解模型',
        requiredMessage: '請選擇圖片理解模型'
      },
      image: {
        label: '選擇圖片',
        requiredMessage: '請選擇圖片'
      }
    },
    variableAssignNode: {
      label: '變數賦值',
      text: '更新全域變數的值',
      assign: '賦值'
    },
    mcpNode: {
      label: 'MCP 調用',
      text: '透過SSE方式執行MCP服務中的工具',
      getToolsSuccess: '獲取工具成功',
      getTool: '獲取工具',
      tool: '工具',
      toolParam: '工具變數',
      mcpServerTip: '請輸入JSON格式的MCP服務器配置',
      mcpToolTip: '請選擇工具',
      configLabel: 'MCP Server Config (僅支持SSE調用方式)'
    },
    imageGenerateNode: {
      label: '圖片生成',
      text: '根據提供的文本內容生成圖片',
      answer: 'AI 回答內容',
      model: {
        label: '圖片生成模型',
        requiredMessage: '請選擇圖片生成模型'
      },
      prompt: {
        label: '提示詞(正向)',
        tooltip: '正向提示詞，用來描述生成圖像中期望包含的元素和視覺特點'
      },
      negative_prompt: {
        label: '提示詞(負向)',
        tooltip: '反向提示詞，用來描述不希望在畫面中看到的內容，可以對畫面進行限制。',
        placeholder: '請描述不想生成的圖片內容，比如：顏色、血腥內容'
      }
    },
    speechToTextNode: {
      label: '語音轉文本',
      text: '將音頻通過語音識別模型轉換為文本',
      stt_model: {
        label: '語音識別模型'
      },
      audio: {
        label: '選擇語音文件',
        placeholder: '請選擇語音文件'
      }
    },
    textToSpeechNode: {
      label: '文本轉語音',
      text: '將文本通過語音合成模型轉換為音頻',
      tts_model: {
        label: '語音合成模型'
      },
      content: {
        label: '選擇文本內容'
      }
    },
    functionNode: {
      label: '自定義函數',
      text: '通過執行自定義腳本，實現數據處理'
    },
    applicationNode: {
      label: '應用節點'
    }
  },
  compare: {
    is_null: '為空',
    is_not_null: '不為空',
    contain: '包含',
    not_contain: '不包含',
    eq: '等於',
    ge: '大於等於',
    gt: '大於',
    le: '小於等於',
    lt: '小於',
    len_eq: '長度等於',
    len_ge: '長度大於等於',
    len_gt: '長度大於',
    len_le: '長度小於等於',
    len_lt: '長度小於',
    is_true: '為真',
    is_not_true: '不為真'
  },
  FileUploadSetting: {}
}
