export default {
  title: 'Models',
  provider: 'Provider',
  providerPlaceholder: 'Select Provider',
  addModel: 'Add Model',
  searchBar: {
    placeholder: 'Search by name'
  },
  delete: {
    confirmTitle: 'Delete Model',
    confirmMessage: 'Are you sure you want to delete the model:'
  },
  tip: {
    createSuccessMessage: 'Model created successfully',
    createErrorMessage: 'There are errors in the basic information',
    errorMessage: 'Variable already exists: ',
    emptyMessage1: 'Please select the model type and base model in the basic information first',
    emptyMessage2: 'The selected model does not support parameter settings',
    updateSuccessMessage: 'Model updated successfully',
    saveSuccessMessage: 'Model parameters saved successfully',
    downloadError: 'Download failed',
    noModel: 'Model does not exist in Ollama'
  },
  model: {
    allModel: 'All Models',
    publicModel: 'Public Models',
    privateModel: 'Private Models',
    LLM: 'LLM',
    EMBEDDING: 'Embedding Model',
    RERANKER: 'Rerank',
    STT: 'Speech2Text',
    TTS: 'TTS',
    IMAGE: 'Vision Model',
    TTI: 'Image Generation'
  },
  templateForm: {
    title: {
      baseInfo: 'Basic Information',
      advancedInfo: 'Advanced Settings',
      modelParams: 'Model Parameters',
      editParam: 'Edit Parameter',
      addParam: 'Add Parameter',
      paramSetting: 'Model Parameter Settings',
      apiParamPassing: 'Interface Parameters'
    },
    form: {
      templateName: {
        label: 'Model Name',
        placeholder: 'Set a name for the base model',
        tooltip: 'Custom model name in MaxKB',
        requiredMessage: 'Model name cannot be empty'
      },
      permissionType: {
        label: 'Permission',
        privateDesc: 'Available only to current user',
        publicDesc: 'Available to all users',
        requiredMessage: 'Permission cannot be empty'
      },
      model_type: {
        label: 'Model Type',
        placeholder: 'Select a model type',
        tooltip1:
          'LLM: An inference model for AI chats in the APP.',
        tooltip2:
          'Embedding Model: A model for vectorizing document content in the knowledge.',
        tooltip3: 'Speech2Text: A model used for speech recognition in the APP.',
        tooltip4: 'TTS: A model used for TTS in the APP.',
        tooltip5:
          'Rerank: A model used to reorder candidate segments when using multi-route recall in advanced orchestration APP.',
        tooltip6:
          'Vision Model: A visual model used for image understanding in advanced orchestration APP.',
        tooltip7:
          'Image Generation: A visual model used for image generation in advanced orchestration APP.',
        requiredMessage: 'Model type cannot be empty'
      },
      base_model: {
        label: 'Base Model',
        tooltip:
          'For models not listed, enter the model name and press Enter',
        placeholder: 'Enter the base model name and press Enter to add',
        requiredMessage: 'Base model cannot be empty'
      }
    }
  },
  download: {
    downloading: 'Downloading...',
    cancelDownload: 'Cancel Download'
  }
}
