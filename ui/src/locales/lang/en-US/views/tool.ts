export default {
  title: 'Tool',
  all: 'All',
  createTool: 'Create Tool',
  editTool: 'Edit Tool',
  createMcpTool: 'Create MCP',
  editMcpTool: 'Edit MCP',
  copyTool: 'Copy Tool',
  importTool: 'Import Tool',
  settingTool: 'Set Tool',
  mcpConfig: 'MCP Service Config',
  toolStore: {
    title: 'Tool Store',
    createFromToolStore: 'Create from Tool Store',
    internal: 'Built in system',
    recommend: 'Recommended',
    webSearch: 'Web Search',
    databaseQuery: 'Database Query',
    image: 'Image',
    developer: 'Developer',
    communication: 'Communication',
    searchResult: '{count} search results for',
    confirmTip: 'Are you sure to update tool: ',
    updateStoreToolMessage: 'Updating tools may affect resources in use, so proceed with caution.',
  },
  searchBar: {
    placeholder: 'Search by tool name',
  },
  tip: {
    saveMessage: 'Unsaved changes will be lost. Are you sure you want to exit?',
  },
  delete: {
    confirmTitle: 'Confirm deletion of tool:',
    confirmMessage:
      'Deleting this tool will cause errors in APP that reference it when they are queried. Please proceed with caution.',
  },
  disabled: {
    confirmTitle: 'Confirm disable tool:',
    confirmMessage:
      'Disabling this tool will cause errors in APP that reference it when they are queried. Please proceed with caution.',
  },

  form: {
    toolName: {
      label: 'Name',
      name: 'Tool Name',
      placeholder: 'Please enter the tool name',
      requiredMessage: 'Please enter the tool name',
    },
    mcpName: {
      label: 'Name',
      name: 'MCP Name',
      placeholder: 'Please enter the MCP name',
      requiredMessage: 'Please enter the MCP name',
    },
    toolDescription: {
      label: 'Description',
      placeholder: 'Please enter a description of the tool',
    },
    mcpDescription: {
      label: 'Description',
      placeholder: 'Please enter a description of the MCP',
    },
    paramName: {
      label: 'Parameter Name',
      placeholder: 'Please enter the parameter name',
      requiredMessage: 'Please enter the parameter name',
    },
    dataType: {
      label: 'Data Type',
    },
    source: {
      label: 'Source',
      reference: 'Reference Parameter',
    },
    required: {
      label: 'Required',
    },
    param: {
      paramInfo1: 'Displayed when using the tool',
      paramInfo2: 'Not displayed when using the tool',
      code: 'Content (Python)',
      selectPlaceholder: 'Please select parameter',
      inputPlaceholder: 'Please enter parameter values',
    },
    mcp: {
      title: 'MCP Service',
      label: 'MCP Server Config',
      placeholder: 'Please enter MCP Server config',
      tip: 'Only supports SSE and Streamable HTTP calling methods',
      requiredMessage: 'Please enter MCP Server Config',
    },
    debug: {
      run: 'Run',
      output: 'Output',
      runResult: 'Run Result',
      runSuccess: 'Successful',
      runFailed: 'Run Failed',
    },
  },
}
