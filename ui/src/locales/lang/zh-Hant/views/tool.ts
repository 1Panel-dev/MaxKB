export default {
  title: '工具',
  all: '全部',
  createTool: '建立工具',
  editTool: '編輯工具',
  createMcpTool: '建立MCP',
  editMcpTool: '編輯MCP',
  copyTool: '複製工具',
  importTool: '匯入工具',
  settingTool: '設定工具',
  mcpConfig: 'MCP服務配置',
  toolStore: {
    title: '工具商店',
    createFromToolStore: '從工具商店創建',
    internal: '系统内置',
    recommend: '推薦',
    webSearch: '聯網搜索',
    databaseQuery: '數據庫查詢',
    image: '圖像',
    developer: '開發者',
    communication: '通信',
    searchResult: '的搜索結果 {count} 個',
    confirmTip: '是否更新工具：',
    updateStoreToolMessage: '更新工具可能會影響正在使用的資源，請謹慎操作。',
  },
  searchBar: {
    placeholder: '按工具名稱搜尋',
  },
  tip: {
    saveMessage: '當前的更改尚未保存，確認退出嗎？',
  },
  delete: {
    confirmTitle: '是否刪除工具',
    confirmMessage: '刪除後，引用該工具的應用在查詢時會報錯，請謹慎操作。',
  },
  disabled: {
    confirmTitle: '是否停用工具：',
    confirmMessage: '停用後，引用該工具的應用在查詢時會報錯，請謹慎操作。',
  },
  form: {
    toolName: {
      label: '名稱',
      name: '工具名稱',
      placeholder: '請輸入工具名稱',
      requiredMessage: '請輸入工具名稱',
    },
    mcpName: {
      label: '名稱',
      name: 'MCP名稱',
      placeholder: '請輸入MCP名稱',
      requiredMessage: '請輸入MCP名稱',
    },
    toolDescription: {
      label: '描述',
      placeholder: '請輸入工具的描述',
    },
    mcpDescription: {
      label: '描述',
      placeholder: '請輸入MCP的描述',
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
    mcp: {
      title: 'MCP 服務',
      label: 'MCP Server Config',
      placeholder: '請輸入MCP Server配置',
      tip: '僅支援SSE、Streamable HTTP呼叫方式',
      requiredMessage: '請輸入 MCP Server Config',
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
