export default {
  title: '模型設定',
  provider: '供應商',
  providerPlaceholder: '選擇供應商',
  addModel: '新增模型',
  searchBar: {
    placeholder: '按名稱搜尋'
  },
  delete: {
    confirmTitle: '刪除模型',
    confirmMessage: '是否刪除模型：'
  },
  tip: {
    createSuccessMessage: '創建模型成功',
    createErrorMessage: '基礎資訊有填寫錯誤',
    errorMessage: '變數已存在: ',
    emptyMessage1: '請先選擇基礎資訊的模型類型和基礎模型',
    emptyMessage2: '所選模型不支援參數設定',
    updateSuccessMessage: '修改模型成功',
    saveSuccessMessage: '模型參數儲存成功',
    downloadError: '下載失敗',
    noModel: '模型在Ollama不存在'
  },
  model: {
    allModel: '全部模型',
    publicModel: '公有模型',
    privateModel: '私有模型',
    LLM: '大語言模型',
    EMBEDDING: '向量模型',
    RERANKER: '重排模型',
    STT: '語音辨識',
    TTS: '語音合成',
    IMAGE: '圖片理解',
    TTI: '圖片生成'
  },
  templateForm: {
    title: {
      baseInfo: '基礎資訊',
      advancedInfo: '進階設定',
      modelParams: '模型參數',
      editParam: '編輯參數',
      addParam: '新增參數',
      paramSetting: '模型參數設定',
      apiParamPassing: '接口傳參'
    },
    form: {
      templateName: {
        label: '模型名稱',
        placeholder: '請給基礎模型設定一個名稱',
        tooltip: 'MaxKB 中自訂的模型名稱',
        requiredMessage: '模型名稱不能為空'
      },
      permissionType: {
        label: '權限',
        privateDesc: '僅當前使用者使用',
        publicDesc: '所有使用者都可使用',
        requiredMessage: '權限不能為空'
      },
      model_type: {
        label: '模型類型',
        placeholder: '請選擇模型類型',
        tooltip1: '大語言模型：在應用中與AI對話的推理模型。',
        tooltip2: '向量模型：在知識庫中對文件內容進行向量化化的模型。',
        tooltip3: '語音辨識：在應用中開啟語音辨識後用於語音轉文字的模型。',
        tooltip4: '語音合成：在應用中開啟語音播放後用於文字轉語音的模型。',
        tooltip5: '重排模型：在高階編排應用中使用多路召回時，對候選分段進行重新排序的模型。',
        tooltip6: '圖片理解：在高階編排應用中用於圖片理解的視覺模型。',
        tooltip7: '圖片生成：在高階編排應用中用於圖片生成的視覺模型。',
        requiredMessage: '模型類型不能為空'
      },
      base_model: {
        label: '基礎模型',
        tooltip: '列表中未列出的模型，直接輸入模型名稱，按 Enter 即可新增',
        placeholder: '自訂輸入基礎模型後按 Enter 即可',
        requiredMessage: '基礎模型不能為空'
      }
    }
  },
  download: {
    downloading: '正在下載中',
    cancelDownload: '取消下載'
  }
}
