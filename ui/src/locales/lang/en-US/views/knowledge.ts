export default {
  title: 'Knowledge',
  relatedApplications: 'Linked Agent',
  document_count: 'docs',
  relatedApp_count: 'linked agents',
  setting: {
    vectorization: 'Vectorization',
    sync: 'Sync',
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 50 knowledge. For more knowledge, please upgrade to the professional edition.',
    syncSuccess: 'Sync task sent successfully',
    updateModeMessage:
      'After modifying the knowledge vector model, you need to vectorize the knowledge. Do you want to continue saving?',
  },
  delete: {
    confirmTitle: 'Confirm deletion of knowledge:',
    confirmMessage1: 'This knowledge is related with',
    confirmMessage2: 'agent. Deleting it will be irreversible, please proceed with caution.',
    resourceCountMessage: 'This knowledge is associated with {count} resources, and will be unavailable after deletion. Please proceed with caution.',
  },
  knowledgeType: {
    label: 'Type',
    generalKnowledge: 'General Knowledge',
    webKnowledge: 'Web Knowledge',
    larkKnowledge: 'Lark Knowledge',
    workflowKnowledge: 'Workflow Knowledge',
    yuqueKnowledge: 'Yuque Knowledge',
    generalInfo: 'Upload local documents',
    webInfo: 'Sync text data from a web site',
    larkInfo: 'Build knowledge through Lark documents',
    yuqueInfo: 'Build knowledge through Yuque documents',
    createGeneralKnowledge: 'Create General Knowledge',
    createWebKnowledge: 'Create Web Knowledge',
    createLarkKnowledge: 'Create Lark Knowledge',
    createYuqueKnowledge: 'Create Yuque Knowledge',
    createWorkflowKnowledge: 'Create Workflow Knowledge',
    workflowInfo: 'Building a knowledge base through custom workflow methods',
  },
  form: {
    knowledgeName: {
      label: 'Name',
      placeholder: 'Please enter the knowledge name',
      requiredMessage: 'Please enter the knowledge name',
    },
    knowledgeDescription: {
      label: 'Description',
      placeholder:
        'Describe the content of the knowledge. A detailed description will help AI understand the content better, improving the accuracy of content retrieval and hit rate.',
      requiredMessage: 'Please enter the knowledge description',
    },
    EmbeddingModel: {
      label: 'Embedding Model',
      placeholder: 'Please select a embedding model',
      requiredMessage: 'Please select the embedding model',
    },

    source_url: {
      label: 'Web Root URL',
      placeholder: 'Please enter the web root URL',
      requiredMessage: 'Please enter the web root URL',
    },
    selector: {
      label: 'Selector',
      placeholder: 'Default is body, can input .classname/#idname/tagname',
    },
    file_count_limit: {
      label: 'Maximum number of files uploaded at once',
    },
    file_size_limit: {
      label: 'Maximum size of each document(MB)',
      placeholder: 'Suggest based on server configuration, otherwise may cause service shutdown',
    },
    appTemplate: {
      blank: {
        title: 'Blank Creation',
      },
      basic: {
        title: 'Basic Template',
        description: 'Supports basic workflow templates for local files, Lark documents, and web site data sources',
      },
    },
  },

  ResultSuccess: {
    title: 'Knowledge Created Successfully',
    paragraph: 'Segments',
    paragraph_count: 'Segments',
    documentList: 'Document List',
    loading: 'Importing',
    buttons: {
      toKnowledge: 'Return to Knowledge List',
      toDocument: 'Go to Document',
    },
  },
  syncWeb: {
    title: 'Sync Knowledge',
    syncMethod: 'Sync Method',
    replace: 'Replace Sync',
    replaceText: 'Re-fetch Web site documents, replacing the documents in the local knowledge',
    complete: 'Full Sync',
    completeText: 'Delete all documents in the local knowledge and re-fetch web site documents',
    tip: 'Note: All syncs will delete existing data and re-fetch new data. Please proceed with caution.',
  },
}
