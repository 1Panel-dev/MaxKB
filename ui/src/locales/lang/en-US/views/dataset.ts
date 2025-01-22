export default {
  title: 'Knowledge',
  createDataset: 'Create Knowledge',
  general: 'General',
  web: 'Web Site',
  relatedApplications: 'Linked App',
  document_count: 'docs',
  relatedApp_count: 'linked apps',
  searchBar: {
    placeholder: 'Search by name'
  },
  setting: {
    vectorization: 'Vectorization',
    sync: 'Sync'
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 50 knowledge. For more knowledge, please upgrade to the professional edition.',
    syncSuccess: 'Sync task sent successfully',
    updateModeMessage:
      'After modifying the knowledge vector model, you need to vectorize the knowledge. Do you want to continue saving?'
  },
  delete: {
    confirmTitle: 'Confirm deletion of knowledge:',
    confirmMessage1: 'This knowledge is associated with',
    confirmMessage2: 'APP. Deleting it will be irreversible, please proceed with caution.'
  },
  datasetForm: {
    title: {
      info: 'Basic Information'
    },
    form: {
      datasetName: {
        label: 'Knowledge Name',
        placeholder: 'Please enter the knowledge name',
        requiredMessage: 'Please enter the knowledge name'
      },
      datasetDescription: {
        label: 'Knowledge Description',
        placeholder:
          'Describe the content of the knowledge. A detailed description will help AI understand the content better, improving the accuracy of content retrieval and hit rate.',
        requiredMessage: 'Please enter the knowledge description'
      },
      EmbeddingModel: {
        label: 'Embedding Model',
        placeholder: 'Please select a embedding model',
        requiredMessage: 'Please enter the embedding model'
      },
      datasetType: {
        label: 'Knowledge Type',
        generalInfo: 'Upload local documents',
        webInfo: 'Sync text data from a web site'
      },
      source_url: {
        label: 'Web Root URL',
        placeholder: 'Please enter the web root URL',
        requiredMessage: 'Please enter the web root URL'
      },
      selector: {
        label: 'Selector',
        placeholder: 'Default is body, can input .classname/#idname/tagname'
      }
    }
  },
  ResultSuccess: {
    title: 'Knowledge Base Created Successfully',
    paragraph: 'Paragraphs',
    paragraph_count: 'Paragraphs',
    documentList: 'Document List',
    loading: 'Importing',
    buttons: {
      toDataset: 'Return to Knowledge Base List',
      toDocument: 'Go to Document'
    }
  },
  syncWeb: {
    title: 'Sync Knowledge Base',
    syncMethod: 'Sync Method',
    replace: 'Replace Sync',
    replaceText: 'Re-fetch Web site documents, replacing the documents in the local knowledge base',
    complete: 'Full Sync',
    completeText:
      'Delete all documents in the local knowledge base and re-fetch web site documents',
    tip: 'Note: All syncs will delete existing data and re-fetch new data. Please proceed with caution.'
  }
}
