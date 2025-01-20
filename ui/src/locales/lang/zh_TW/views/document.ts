export default {
  uploadDocument: '上傳文檔',
  importDocument: '導入文檔',
  syncDocument: '同步文檔',
  selected: '已選',
  items: '項',
  searchBar: {
    placeholder: '按 文檔名稱 搜索'
  },
  setting: {
    migration: '遷移',

    cancelGenerateQuestion: '取消生成問題',
    cancelVectorization: '取消向量化',
    cancelGenerate: '取消生成'
  },
  tip: {
    saveMessage: '當前的更改尚未保存，確認退出嗎?',
    cancelSuccess: '批量取消成功',
    sendMessage: '發送成功',
    vectorizationSuccess: '批量向量化成功',
    nameMessage: '文件名稱不能为空！',
    importMessage: '導入成功',
    migrationSuccess: '遷移成功'
  },
  upload: {
    selectFile: '選擇文件',
    selectFiles: '選擇文件夾',
    uploadMessage: '拖拽文件至此上傳或',
    formats: '支持格式：',
    requiredMessage: '請上傳文件',
    errorMessage1: '請上傳文件',
    errorMessage2: '文件格式不支持',
    errorMessage3: '文件不能为空',
    errorMessage4: '每次最多上傳50個文件',
    template: '模板',
    download: '下載'
  },

  fileType: {
    txt: {
      label: '文本文件',
      tip1: '1、文件上傳前，建議規範文件的分段標識',
      tip2: '2、每次最多上傳 50 個文件，每個文件不超过 100MB'
    },
    table: {
      label: '表格',
      tip1: '1、點擊下載對應模板並完善信息：',
      tip2: '2、第一行必須是列標題，且列標題必須是有意義的術語，表中每條記錄將作為一個分段',
      tip3: '3、上傳的表格文件中每個 sheet 會作為一個文檔，sheet 名稱為文檔名稱',
      tip4: '4、每次最多上傳 50 個文件，每個文件不超过 100MB'
    },
    QA: {
      label: 'QA 問答對',
      tip1: '1、點擊下載對應模板並完善信息',
      tip2: '2、上傳的表格文件中每個 sheet 會作為一個文檔，sheet 名稱為文檔名稱',
      tip3: '3、每次最多上傳 50 個文件，每個文件不超过 100MB'
    }
  },
  setRules: {
    title: {
      setting: '設置分段規則',
      preview: '分段預覽'
    },
    intelligent: {
      label: '智能分段（推薦)',
      text: '不了解如何設置分段規則推薦使用智能分段'
    },
    advanced: {
      label: '高級分段',
      text: '用戶可根據文檔規範自行設置分段標識符、分段長度以及清洗規則'
    },
    patterns: {
      label: '分段標識',
      tooltip: '按照所選符號先後順序做遞歸分割，分割結果超出分段長度將截取至分段長度。',
      placeholder: '請選擇'
    },
    limit: {
      label: '分段長度'
    },
    with_filter: {
      label: '自動清洗',
      text: '去掉重複多餘符號空格、空行、制表符'
    },
    checkedConnect: {
      label: '導入時添加分段標題為關聯問題（適用於標題為問題的問答對）'
    }
  },
  buttons: {
    prev: '上一步',
    next: '下一步',
    import: '開始導入',
    preview: '生成預覽'
  },
  table: {
    name: '文件名稱',
    char_length: '字符數',
    paragraph: '分段',
    all: '全部',
    updateTime: '更新時間'
  },
  fileStatus: {
    label: '文件狀態',
    SUCCESS: '成功',
    FAILURE: '失敗',
    EMBEDDING: '索引中',
    PENDING: '排隊中',
    GENERATE: '生成中',
    SYNC: '同步中',
    REVOKE: '取消中'
  },
  enableStatus: {
    label: '啟用狀態',
    enable: '開啟',
    close: '關閉'
  },
  sync: {
    label: '同步',
    confirmTitle: '確認同步文檔?',
    confirmMessage1: '同步將刪除已有數據重新獲取新數據，請謹慎操作。',
    confirmMessage2: '無法同步，請先去設置文檔 URL地址',
    successMessage: '同步文檔成功'
  },
  delete: {
    confirmTitle1: '是否批量刪除',
    confirmTitle2: '個文檔?',
    confirmMessage: '所選文檔中的分段會跟隨刪除，請謹慎操作。',
    successMessage: '批量刪除成功',
    confirmTitle3: '是否刪除文檔：',
    confirmMessage1: '此文檔下的',
    confirmMessage2: '個分段都會被刪除，請謹慎操作。'
  },
  form: {
    source_url: {
      label: '文檔地址',
      placeholder: '請輸入文檔地址，一行一個，地址不正確文檔會導入失敗。',
      requiredMessage: '請輸入文檔地址'
    },
    selector: {
      label: '選擇器',
      placeholder: '默認為 body，可輸入 .classname/#idname/tagname'
    },
    hit_handling_method: {
      label: '命中處理方式',
      tooltip: '用戶提問時，命中文檔下的分段時按照設置的方式進行處理。'
    },
    similarity: {
      label: '相似度高于',
      placeholder: '直接返回分段内容',
      requiredMessage: '请输入相似度'
    },
    selectVectorization: {
      label: '选择向量化内容',
      error: '向量化未成功的分段',
      all: '全部分段'
    }
  },
  hitHandlingMethod: {
    optimization: '模型優化',
    directly_return: '直接回答'
  },
  generateQuestion: {
    title: '生成問題',
    successMessage: '生成問題成功',
    tip1: '提示詞中的 {data} 為分段內容的佔位符，執行時替換為分段內容並發送給 AI 模型；',
    tip2: 'AI 模型根據分段內容生成相關問題，請將生成的問題放置於 <question></question> 標籤中，系統會自動關聯標籤中的問題；',
    tip3: '生成效果取決於所選模型和提示詞，用戶可自行調整至最佳效果。'
  }
}
