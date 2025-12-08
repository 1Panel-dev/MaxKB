export default {
  uploadDocument: 'Upload Document',
  importDocument: 'Import Document',
  syncDocument: 'Sync Document',
  items: 'Items',
  migrateDocument: 'Migrate to',
  searchBar: {
    placeholder: 'Search by document name',
  },
  setting: {
    migration: 'Move',
    cancelGenerateQuestion: 'Cancel Generating Questions',
    cancelVectorization: 'Cancel Vectorization',
    cancelGenerate: 'Cancel Generation',
    export: 'Export to',
    download: 'Download',
    replace: 'Replace',
  },

  tip: {
    saveMessage: 'Current changes have not been saved. Confirm exit?',
    cancelSuccess: 'Successful',
    sendMessage: 'Successful',
    vectorizationSuccess: 'Successful',
    nameMessage: 'Document name cannot be empty!',
    importMessage: 'Successful',
    migrationSuccess: 'Successful',
    fileLimitCountTip1: 'Maximum upload per time',
    fileLimitCountTip2: 'files',
    fileLimitSizeTip1: 'each file must not exceed',
  },
  upload: {
    selectFile: 'Select File',
    selectFiles: 'Select Folder',
    uploadMessage: 'Drag and drop files here to upload or',
    formats: 'Supported formats:',
    requiredMessage: 'Please upload a file',
    errorMessage1: 'The file size exceeds 100mb',
    errorMessage2: 'Unsupported file format',
    errorMessage3: 'File cannot be empty',
    errorMessage4: 'Up to 50 files can be uploaded at once',
    template: 'Template',
    download: 'Download',
  },

  fileType: {
    txt: {
      label: 'Text File',
      tip1: '1. It is recommended to standardize the segment markers in the file before uploading.',
      tip2: '2. Up to 50 files can be uploaded at once, with each file not exceeding 100MB.',
    },
    table: {
      label: 'Table',
      tip1: '1. Click to download the corresponding template and complete the information:',
      tip2: '2. The first row must be column headers, and the column headers must be meaningful terms. Each record in the table will be treated as a segment.',
      tip3: '3. Each sheet in the uploaded spreadsheet file will be treated as a document, with the sheet name as the document name.',
      tip4: '4. Up to 50 files can be uploaded at once, with each file not exceeding 100MB.',
    },
    QA: {
      label: 'QA Pairs',
      tip1: '1. Click to download the corresponding template and complete the information:',
      tip2: '2. Each sheet in the uploaded spreadsheet file will be treated as a document, with the sheet name as the document name.',
      tip3: '3. Up to 50 files can be uploaded at once, with each file not exceeding 100MB.',
    },
  },
  setRules: {
    title: {
      setting: 'Set Segment Rules',
      preview: 'Preview',
    },
    intelligent: {
      label: 'Automatic Segmentation (Recommended)',
      text: 'If you are unsure how to set segmentation rules, it is recommended to use automatic segmentation.',
    },
    advanced: {
      label: 'Advanced Segmentation',
      text: 'Users can customize segmentation delimiters, segment length, and cleaning rules based on document standards.',
    },
    patterns: {
      label: 'Segment Delimiters',
      tooltip:
        'Recursively split according to the selected symbols in order. If the split result exceeds the segment length, it will be truncated to the segment length.',
      placeholder: 'Please select',
    },
    limit: {
      label: 'Segment Length',
    },
    with_filter: {
      label: 'Auto Clean',
      text: 'Remove duplicate extra symbols, spaces, blank lines, and tab words.',
    },
    checkedConnect: {
      label: 'Add "Related Questions" section for question-based QA pairs during import.',
    },
  },
  buttons: {
    prev: 'Previous',
    next: 'Next',
    import: 'Start Import',
    preview: 'Apply',
  },
  tag: {
    label: 'Tag Management',
    key: 'Tag',
    value: 'Value',
    addTag: 'Add Tag',
    setting: 'Tag Settings',
    create: 'Create Tag',
    createValue: 'Create Tag Value',
    edit: 'Edit Tag',
    editValue: 'Edit Tag Value',
    deleteConfirm: 'Confirm delete tag: ',
    deleteTip:
      'After deletion, resources using this tag will have the tag removed. Please proceed with caution!',
    requiredMessage1: 'Please enter a tag',
    requiredMessage2: 'Please enter a value',
    requiredMessage3: 'Please enter a tag or value',
  },
  table: {
    name: 'Document Name',
    char_length: 'Character',
    paragraph: 'Segment',
    all: 'All',
    updateTime: 'Update Time',
  },
  fileStatus: {
    label: 'File Status',
    SUCCESS: 'Success',
    FAILURE: 'Failure',
    EMBEDDING: 'Indexing',
    PENDING: 'Queuing',
    GENERATE: 'Generating',
    SYNC: 'Syncing',
    REVOKE: 'Cancelling',
    finish: 'Finish',
  },
  enableStatus: {
    label: 'Status',
    enable: 'Enabled',
    close: 'Disabled',
  },
  sync: {
    label: 'Sync',
    confirmTitle: 'Confirm sync document?',
    confirmMessage1:
      'Syncing will delete existing data and retrieve new data. Please proceed with caution.',
    confirmMessage2: 'Cannot sync, please set the document URL first.',
    successMessage: 'Successful',
  },
  delete: {
    confirmTitle1: 'Confirm batch deletion of',
    confirmTitle2: 'documents?',
    confirmMessage:
      'Segments within the selected documents will also be deleted. Please proceed with caution.',
    successMessage: 'Successful',
    confirmTitle3: 'Confirm deleting document:',
    confirmMessage1: 'Under this document',
    confirmMessage2: 'All segments will be deleted, please operate with caution. ',
  },
  form: {
    source_url: {
      label: 'Document URL',
      placeholder: 'Enter document URL, one per line. Incorrect URL will cause import failure.',
      requiredMessage: 'Please enter a document URL',
    },
    selector: {
      label: 'Selector',
      placeholder: 'Default is body, you can input .classname/#idname/tagname',
    },
    hit_handling_method: {
      label: 'Retrieve-Respond',
      tooltip: 'When user asks a question, handle matched segments according to the set method.',
    },
    similarity: {
      label: 'Similarity Higher Than',
      placeholder: 'Directly return segment content',
      requiredMessage: 'Please enter similarity value',
    },
    allow_download: {
      label: 'Allow download in knowledge base source',
    },
  },
  hitHandlingMethod: {
    optimization: 'Model optimization',
    directly_return: 'Respond directly',
  },
  movePosition: {
    title: 'Move position',
    moveUp: 'Move up',
    moveDown: 'Move down',
  },
  generateQuestion: {
    title: 'Generate Questions',
    successMessage: 'Successful',
    tip1: 'The {data} in the prompt is a placeholder for segmented content, which is replaced by the segmented content when executed and sent to the AI model;',
    tip2: 'The AI model generates relevant questions based on the segmented content. Please place the generated questions within the',
    tip3: 'tags, and the system will automatically relate the questions within these tags;',
    tip4: 'The generation effect depends on the selected model and prompt. Users can adjust to achieve the best effect.',
    prompt1:
      'Content: {data}\n \n Please summarize the above and generate 5 questions based on the summary. \nAnswer requirements: \n - Please output only questions; \n - Please place each question in',
    prompt2: 'tag.',
  },
  feishu: {
    selectDocument: 'Select Document',
    tip1: 'Only documents and tables are supported. Documents will be segmented based on titles, and tables will be converted to Markdown format before segmentation.',
    tip2: 'Before importing the document, it is recommended to standardize the document segmentation markers.',
    allCheck: 'Select All',
  },
}
