export default {
  title: 'Tool',
  internalTitle: 'Internal Tool',
  added: 'Added',
  createTool: 'Create Tool',
  editTool: 'Edit Tool',
  copyTool: 'Copy Tool',
  importTool: 'Import Tool',
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
    searchResult: '{count} search results for'
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
      placeholder: 'Please enter the tool name',
      requiredMessage: 'Please enter the tool name',
    },
    toolDescription: {
      label: 'Description',
      placeholder: 'Please enter a description of the tool',
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
    debug: {
      run: 'Run',
      output: 'Output',
      runResult: 'Run Result',
      runSuccess: 'Successful',
      runFailed: 'Run Failed',
    },
  },
}
