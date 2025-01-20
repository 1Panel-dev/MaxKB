export default {
  uploadDocument: 'Upload Document',
  importDocument: 'Import Document',
  syncDocument: 'Sync Document',
  selected: 'Selected',
  items: 'Items',
  searchBar: {
    placeholder: 'Search by Document Name'
  },
  setting: {
    migration: 'Migration',
    cancelGenerateQuestion: 'Cancel Generating Questions',
    cancelVectorization: 'Cancel Vectorization',
    cancelGenerate: 'Cancel Generation'
  },
  tip: {
    saveMessage: 'Current changes have not been saved. Confirm exit?',
    cancelSuccess: 'Batch cancellation successful',
    sendMessage: 'Sent successfully',
    vectorizationSuccess: 'Batch vectorization successful',
    nameMessage: 'File name cannot be empty!',
    importMessage: 'Import successful',
    migrationSuccess: 'Migration successful'
  },
  upload: {
    selectFile: 'Select File',
    selectFiles: 'Select Folder',
    uploadMessage: 'Drag and drop files here to upload or',
    formats: 'Supported formats:',
    requiredMessage: 'Please upload a file',
    errorMessage1: 'Please upload a file',
    errorMessage2: 'Unsupported file format',
    errorMessage3: 'File cannot be empty',
    errorMessage4: 'Up to 50 files can be uploaded at once',
    template: 'Template',
    download: 'Download'
  },

  fileType: {
    txt: {
      label: 'Text File',
      tip1: '1. It is recommended to standardize the paragraph markers in the file before uploading.',
      tip2: '2. Up to 50 files can be uploaded at once, with each file not exceeding 100MB'
    },
    table: {
      label: 'Table',
      tip1: '1. Click to download the corresponding template and complete the information:',
      tip2: '2. The first row must be column headers, and the column headers must be meaningful terms. Each record in the table will be treated as a segment.',
      tip3: '3. Each sheet in the uploaded spreadsheet file will be treated as a document, with the sheet name as the document name.',
      tip4: '4. Up to 50 files can be uploaded at once, with each file not exceeding 100MB'
    },
    QA: {
      label: 'QA Pairs',
      tip1: '1. Click to download the corresponding template and complete the information.',
      tip2: '2. Each sheet in the uploaded spreadsheet file will be treated as a document, with the sheet name as the document name.',
      tip3: '3. Up to 50 files can be uploaded at once, with each file not exceeding 100MB'
    }
  },
  setRules: {
    title: {
      setting: 'Set Segment Rules',
      preview: 'Segment Preview'
    },
    intelligent: {
      label: 'Intelligent Segmentation (Recommended)',
      text: 'If you are unsure how to set segmentation rules, it is recommended to use intelligent segmentation.'
    },
    advanced: {
      label: 'Advanced Segmentation',
      text: 'Users can customize segmentation delimiters, segment length, and cleaning rules based on document standards.'
    },
    patterns: {
      label: 'Segment Delimiters',
      tooltip:
        'Recursively split according to the selected symbols in order. If the split result exceeds the segment length, it will be truncated to the segment length.',
      placeholder: 'Please select'
    },
    limit: {
      label: 'Segment Length'
    },
    with_filter: {
      label: 'Auto Clean',
      text: 'Remove duplicate extra symbols, spaces, blank lines, and tab characters.'
    },
    checkedConnect: {
      label:
        'Add Segment Titles as Associated Questions During Import (Applicable for QA Pairs where Titles are Questions)'
    }
  },
  buttons: {
    prev: 'Previous',
    next: 'Next',
    import: 'Start Import',
    preview: 'Generate Preview'
  },
  table: {
    name: 'File Name',
    char_length: 'Character',
    paragraph: 'Segment',
    all: 'All',
    updateTime: 'Update Time'
  },
  fileStatus: {
    label: 'File Status',
    SUCCESS: 'Success',
    FAILURE: 'Failure',
    EMBEDDING: 'Indexing',
    PENDING: 'Queued',
    GENERATE: 'Generating',
    SYNC: 'Syncing',
    REVOKE: 'Cancelling'
  },
  enableStatus: {
    label: 'Status',
    enable: 'Enabled',
    close: 'Disabled'
  },
  sync: {
    label: 'Sync',
    confirmTitle: 'Confirm Sync Document?',
    confirmMessage1:
      'Syncing will delete existing data and retrieve new data. Please proceed with caution.',
    confirmMessage2: 'Cannot sync, please set the document URL first.',
    successMessage: 'Document synced successfully'
  },
  delete: {
    confirmTitle1: 'Confirm Batch Deletion of',
    confirmTitle2: 'Documents?',
    confirmMessage:
      'Segments within the selected documents will also be deleted. Please proceed with caution.',
    successMessage: 'Batch deletion successful',
    confirmTitle3: 'Confirm Deleting Document:',
    confirmMessage1:
      'All segments under this document will be deleted. Please proceed with caution.'
  },
  form: {
    source_url: {
      label: 'Document URL',
      placeholder: 'Enter document URLs, one per line. Incorrect URLs will cause import failure.',
      requiredMessage: 'Please enter a document URL'
    },
    selector: {
      label: 'Selector',
      placeholder: 'Default is body, you can input .classname/#idname/tagname'
    },
    hit_handling_method: {
      label: 'Hit Handling Method',
      tooltip: 'When user asks a question, handle matched segments according to the set method.'
    },
    similarity: {
      label: 'Similarity Higher Than',
      placeholder: 'Directly return segment content',
      requiredMessage: 'Please enter similarity value'
    },
    selectVectorization: {
      label: 'Select Vectorization Content',
      error: 'Segments that failed vectorization',
      all: 'All Segments'
    }
  },
  hitHandlingMethod: {
    optimization: 'Model optimization',
    directly_return: 'Direct answer'
  },
  generateQuestion: {
    title: 'Generate Questions',
    successMessage: 'Question generation successful',
    tip1: 'The {data} in the prompt is a placeholder for segmented content, which is replaced by the segmented content when executed and sent to the AI model;',
    tip2: 'The AI model generates relevant questions based on the segmented content. Please place the generated questions within the <question></question> tags, and the system will automatically associate the questions within these tags;',
    tip3: 'The generation effect depends on the selected model and prompt. Users can adjust to achieve the best effect.'
  }
}
