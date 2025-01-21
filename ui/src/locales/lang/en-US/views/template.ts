export default {
  title: 'Model Settings',
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
    LLM: 'Large Language Model',
    EMBEDDING: 'Embedding Model',
    RERANKER: 'Reranker Model',
    STT: 'Speech-to-Text',
    TTS: 'Text-to-Speech',
    IMAGE: 'Image Understanding',
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
      apiParamPassing: 'API Parameter Passing'
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
        privateDesc: 'Only the current user can use',
        publicDesc: 'All users can use, but cannot be edited',
        requiredMessage: 'Permission cannot be empty'
      },
      model_type: {
        label: 'Model Type',
        placeholder: 'Select a model type',
        tooltip1:
          'Large Language Model: An inference model for AI conversations in the application.',
        tooltip2:
          'Embedding Model: A model for vectorizing document content in the knowledge base.',
        tooltip3: 'Speech-to-Text: A model used for speech recognition in the application.',
        tooltip4: 'Text-to-Speech: A model used for text-to-speech in the application.',
        tooltip5:
          'Reranker Model: A model used to reorder candidate segments when using multi-route recall in advanced orchestration applications.',
        tooltip6:
          'Image Understanding: A visual model used for image understanding in advanced orchestration applications.',
        tooltip7:
          'Image Generation: A visual model used for image generation in advanced orchestration applications.',
        requiredMessage: 'Model type cannot be empty'
      },
      base_model: {
        label: 'Base Model',
        tooltip:
          'For models not listed in the list, enter the model name directly and press Enter to add',
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
