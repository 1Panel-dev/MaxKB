export default {
  node: 'Node',
  baseComponent: 'Basic',
  nodeSetting: 'Node Settings',
  workflow: 'Workflow',
  searchBar: {
    placeholder: 'Search by name'
  },
  info: {
    previewVersion: 'Preview Version:',
    saveTime: 'Last Saved:'
  },
  setting: {
    restoreVersion: 'Restore Previous Version"',
    restoreCurrentVersion: 'Restore to This Version',
    addComponent: 'Add',
    public: 'Publish',
    releaseHistory: 'Release History',
    autoSave: 'Auto Save',
    latestRelease: 'Latest Release',
    copyParam: 'Copy Parameters',
    debug: 'Run'
  },
  tip: {
    publicSuccess: 'Published successfully',
    noData: 'No related results found',
    nameMessage: 'Name cannot be empty!',
    onlyRight: 'Connections can only be made from the right anchor',
    notRecyclable: 'Loop connections are not allowed',
    onlyLeft: 'Connections can only be made to the left anchor',
    applicationNodeError: 'This application is unavailable',
    functionNodeError: 'This function node is unavailable',
    repeatedNodeError: 'A node with this name already exists',
    cannotCopy: 'Cannot be copied',
    copyError: 'Node already copied',
    paramErrorMessage: 'Parameter already exists: '
  },
  delete: {
    confirmTitle: 'Confirm to delete this node?',
    deleteMessage: 'This node cannot be deleted'
  },
  control: {
    zoomOut: 'Zoom Out',
    zoomIn: 'Zoom In',
    fitView: 'Fit to Screen',
    retract: 'Collapse All',
    extend: 'Expand All',
    beautify: 'Auto-Arrange'
  },
  variable: {
    label: 'Variable',
    global: 'Global Variable',
    Referencing: 'Referenced Variable',
    ReferencingRequired: 'Referenced variable is required',
    ReferencingError: 'Invalid referenced variable',
    NoReferencing: 'Referenced variable does not exist',
    placeholder: 'Please select a variable'
  },
  condition: {
    title: 'Execution Condition',
    front: 'Precondition',
    AND: 'All',
    OR: 'Any',
    text: 'After the connected node is executed, execute the current node'
  },
  validate: {
    startNodeRequired: 'Start node is required',
    startNodeOnly: 'Only one start node is allowed',
    baseNodeRequired: 'Base information node is required',
    baseNodeOnly: 'Only one base information node is allowed',
    notInWorkFlowNode: 'Node not in workflow',
    noNextNode: 'Next node does not exist',
    nodeUnavailable: 'Node unavailable',
    needConnect1: 'The branch of the node needs to be connected',
    cannotEndNode: 'This node cannot be used as an end node'
  },
  nodes: {
    startNode: {
      label: 'Start',
      question: 'User Question',
      currentTime: 'Current Time'
    },
    baseNode: {
      label: 'Base Information',
      appName: {
        label: 'App Name'
      },
      appDescription: {
        label: 'App Description'
      },
      fileUpload: {
        label: 'File Upload',
        tooltip: 'When enabled, the Q&A page will display a file upload button.'
      },
      FileUploadSetting: {
        title: 'File Upload Settings',
        maxFiles: 'Maximum number of files per upload',
        fileLimit: 'Maximum size per file (MB)',
        fileUploadType: {
          label: 'File types allowed for upload',
          documentText: 'Requires "Document Content Extraction" node to parse document content',
          imageText: 'Requires "Image Understanding" node to parse image content',
          audioText: 'Requires "Speech-to-Text" node to parse audio content'
        }
      }
    },
    aiChatNode: {
      label: 'AI Chat',
      text: 'Chat with an AI model',
      answer: 'AI Content',
      returnContent: {
        label: 'Return Content',
        tooltip: `If turned off, the content of this node will not be output to the user.
                  If you want the user to see the output of this node, please turn on the switch.`
      },
      defaultPrompt: 'Known Information',
      think: 'Thinking Process'
    },
    searchDatasetNode: {
      label: 'Knowledge Retrieval',
      text: 'Allows you to query text content related to user questions from the Knowledge',
      paragraph_list: 'List of retrieved segments',
      is_hit_handling_method_list: 'List of segments that meet direct response criteria',
      result: 'Search Result',
      directly_return: 'Content of segments that meet direct response criteria',
      searchParam: 'Retrieval Parameters',
      searchQuestion: {
        label: 'Question',
        placeholder: 'Please select a search question',
        requiredMessage: 'Please select a search question'
      }
    },
    questionNode: {
      label: 'Question Optimization',
      text: 'Optimize and improve the current question based on historical chat records to better match knowledge segments',
      result: 'Optimized Question Result',
      defaultPrompt1: `Optimize and improve the user's question based on context:`,
      defaultPrompt2: `Please output an optimized question.`,
      systemDefault: 'You are a question optimization expert'
    },
    conditionNode: {
      label: 'Conditional Branch',
      text: 'Trigger different nodes based on conditions',
      branch_name: 'Branch Name',
      conditions: {
        label: 'Conditions',
        info: 'Meets the following',
        requiredMessage: 'Please select conditions'
      },
      valueMessage: 'Please enter a value',
      addCondition: 'Add Condition',
      addBranch: 'Add Branch'
    },
    replyNode: {
      label: 'Specified Reply',
      text: 'Specify reply content, referenced variables will be converted to strings for output',
      content: 'Content',
      replyContent: {
        label: 'Reply Content',
        custom: 'Custom',
        reference: 'Reference Variable'
      }
    },
    rerankerNode: {
      label: 'Multi-path Recall',
      text: 'Use a re-ranking model to refine retrieval results from multiple knowledge sources',
      result_list: 'Re-ranked Results List',
      result: 'Re-ranking Result',
      rerankerContent: {
        label: 'Re-ranking Content',
        requiredMessage: 'Please select re-ranking content'
      },
      higher: 'Higher',
      ScoreTooltip: 'The higher the Score, the stronger the relevance.',
      max_paragraph_char_number: 'Maximum Character',
      reranker_model: {
        label: 'Rerank',
        placeholder: 'Please select a rerank'
      }
    },
    formNode: {
      label: 'Form Input',
      text: 'Collect user input during Q&A and use it in subsequent processes',
      form_content_format1: 'Hello, please fill out the form below:',
      form_content_format2: 'Click the [Submit] button after filling it out.',
      form_data: 'All Form Content',
      formContent: {
        label: 'Form Output Content',
        requiredMessage:
          'Please set the output content of this node, { form } is a placeholder for the form.',
        tooltip: 'Define the output content of this node. { form } is a placeholder for the form'
      },
      formAllContent: 'All Form Content',
      formSetting: 'Form Configuration'
    },
    documentExtractNode: {
      label: 'Document Content Extraction',
      text: 'Extract content from documents',
      content: 'Document Content'
    },
    imageUnderstandNode: {
      label: 'Image Understanding',
      text: 'Analyze images to identify objects, scenes, and provide answers',
      answer: 'AI Content',
      model: {
        label: 'Vision Model',
        requiredMessage: 'Please select a vision model'
      },
      image: {
        label: 'Select Image',
        requiredMessage: 'Please select an image'
      }
    },
    variableAssignNode: {
      label: 'Variable Assign',
      text: 'Update the value of the global variable',
      assign: 'Set Value'
    },
    imageGenerateNode: {
      label: 'Image Generation',
      text: 'Generate images based on provided text content',
      answer: 'AI Content',
      model: {
        label: 'Image Generation Model',
        requiredMessage: 'Please select an image generation model'
      },
      prompt: {
        label: 'Positive Prompt',
        tooltip: 'Describe elements and visual features you want in the generated image'
      },
      negative_prompt: {
        label: 'Negative Prompt',
        tooltip: 'Describe elements you want to exclude from the generated image',
        placeholder:
          'Please describe content you do not want to generate, such as color, bloody content'
      }
    },
    speechToTextNode: {
      label: 'Speech2Text',
      text: 'Convert audio to text through speech recognition model',
      stt_model: {
        label: 'Speech Recognition Model'
      },
      audio: {
        label: 'Select Audio File',
        placeholder: 'Please select an audio file'
      }
    },
    textToSpeechNode: {
      label: 'TTS',
      text: 'Convert text to audio through speech synthesis model',
      tts_model: {
        label: 'Speech Synthesis Model'
      },
      content: {
        label: 'Select Text Content'
      }
    },
    functionNode: {
      label: 'Custom Function',
      text: 'Execute custom scripts to achieve data processing'
    },
    applicationNode: {
      label: 'APP Node'
    }
  },
  compare: {
    is_null: 'Is null',
    is_not_null: 'Is not null',
    contain: 'Contains',
    not_contain: 'Does not contain',
    eq: 'Equal to',
    ge: 'Greater than or equal to',
    gt: 'Greater than',
    le: 'Less than or equal to',
    lt: 'Less than',
    len_eq: 'Length equal to',
    len_ge: 'Length greater than or equal to',
    len_gt: 'Length greater than',
    len_le: 'Length less than or equal to',
    len_lt: 'Length less than'
  },
  FileUploadSetting: {}
}
