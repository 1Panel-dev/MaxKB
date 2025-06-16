export default {
  title: '工具',
  internalTitle: '內置工具',
  added: '已新增',
  createTool: '建立工具',
  editTool: '編輯工具',
  copyTool: '複製工具',
  importTool: '匯入工具',
  searchBar: {
    placeholder: '按工具名稱搜尋',
  },
  tip: {
    saveMessage: '當前的更改尚未保存，確認退出嗎？',
  },
  delete: {
    confirmTitle: '是否刪除工具：',
    confirmMessage: '刪除後，引用該工具的應用在查詢時會報錯，請謹慎操作。',
  },
  disabled: {
    confirmTitle: '是否停用工具：',
    confirmMessage: '停用後，引用該工具的應用在查詢時會報錯，請謹慎操作。',
  },
  form: {
    toolName: {
      label: '名稱',
      placeholder: '請輸入工具名稱',
      requiredMessage: '請輸入工具名稱',
    },
    toolDescription: {
      label: '描述',
      placeholder: '請輸入工具的描述',
    },
    paramName: {
      label: '參數名',
      placeholder: '請輸入參數名',
      requiredMessage: '請輸入參數名',
    },
    dataType: {
      label: '數據類型',
    },
    source: {
      label: '來源',
      custom: '自定義',
      reference: '引用參數',
    },
    required: {
      label: '是否必填',
    },
    param: {
      paramInfo1: '使用工具時顯示',
      paramInfo2: '使用工具時不顯示',
      code: '工具内容（Python）',
      selectPlaceholder: '請选择參數',
      inputPlaceholder: '請輸入參數值',
    },
    debug: {
      run: '運行',
      output: '輸出',
      runResult: '運行結果',
      runSuccess: '運行成功',
      runFailed: '運行失敗',
    },
  },
}
