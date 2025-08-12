export default {
  title: '工具',
  all: '全部',
  createTool: '创建工具',
  editTool: '编辑工具',
  createMcpTool: '创建MCP',
  editMcpTool: '编辑MCP',
  copyTool: '复制工具',
  importTool: '导入工具',
  toolStore: {
    title: '工具商店',
    createFromToolStore: '从工具商店创建',
    internal: '系统内置',
    recommend: '推荐',
    webSearch: '联网搜索',
    databaseQuery: '数据库查询',
    image: '图像',
    developer: '开发者',
    communication: '通信',
    searchResult: '的搜索结果 {count} 个',
  },
  delete: {
    confirmTitle: '是否刪除工具',
    confirmMessage: '删除后，引用了该工具的应用提问时会报错 ，请谨慎操作。',
  },
  disabled: {
    confirmTitle: '是否禁用工具：',
    confirmMessage: '禁用后，引用了该工具的应用提问时会报错 ，请谨慎操作。',
  },
  tip: {
    saveMessage: '当前的更改尚未保存，确认退出吗?',
  },
  form: {
    toolName: {
      label: '名称',
      name: '工具名称',
      placeholder: '请输入工具名称',
      requiredMessage: '请输入工具名称',
    },
    toolDescription: {
      label: '描述',
      placeholder: '请输入工具的描述',
    },
    paramName: {
      label: '参数名',
      placeholder: '请输入参数名',
      requiredMessage: '请输入参数名',
    },
    dataType: {
      label: '数据类型',
    },
    source: {
      label: '来源',
      reference: '引用参数',
    },
    required: {
      label: '是否必填',
    },
    param: {
      paramInfo1: '使用工具时显示',
      paramInfo2: '使用工具时不显示',
      code: '工具内容（Python）',
      selectPlaceholder: '请选择参数',
      inputPlaceholder: '请输入参数值',
    },
    mcp: {
      label: 'MCP Server Config',
      placeholder: '请输入MCP Server配置',
      tip: '仅支持SSE、Streamable HTTP调用方式',
    },
    debug: {
      run: '运行',
      output: '输出',
      runResult: '运行结果',
      runSuccess: '运行成功',
      runFailed: '运行失败',
    },
  },
}
