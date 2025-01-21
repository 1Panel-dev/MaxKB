export default {
  title: 'Knowledge',
  createDataset: 'Create Knowledge',
  general: 'General',
  web: 'Web Site',
  relatedApplications: 'Related App',
  searchBar: {
    placeholder: 'Search by name'
  },
  setting: {
    vectorization: 'Vectorization',
    sync: 'Sync'
  },
  tip: {
    professionalMessage:
      'The community edition supports up to 50 knowledge bases. For more knowledge bases, please upgrade to the professional edition.',
    syncSuccess: 'Sync task sent successfully',
    updateModeMessage:
      'After modifying the knowledge base vector model, you need to vectorize the knowledge base. Do you want to continue saving?'
  },
  delete: {
    confirmTitle: 'Confirm Deletion of Knowledge Base:',
    confirmMessage1: 'This knowledge base is associated with',
    confirmMessage2: 'applications. Deleting it will be irreversible, please proceed with caution.'
  },
  datasetForm: {
    title: {
      info: 'Basic Information'
    },
    form: {
      datasetName: {
        label: 'Knowledge Base Name',
        placeholder: 'Please enter the knowledge base name',
        requiredMessage: 'Please enter the knowledge base name'
      },
      datasetDescription: {
        label: 'Knowledge Base Description',
        placeholder:
          'Describe the content of the knowledge base. A detailed description will help AI understand the content better, improving the accuracy of content retrieval and hit rate.',
        requiredMessage: 'Please enter the knowledge base description'
      },
      EmbeddingModel: {
        label: 'Embedding Model',
        placeholder: 'Please select a Embedding Model',
        requiredMessage: 'Please enter the Embedding model'
      },
      datasetType: {
        label: 'Knowledge Base Type',
        generalInfo: 'Upload local files or manually enter',
        webInfo: 'Sync text data from a Web site'
      },
      source_url: {
        label: 'Web Root URL',
        placeholder: 'Please enter the Web root URL',
        requiredMessage: 'Please enter the Web root URL'
      },
      selector: {
        label: 'Selector',
        placeholder: 'Default is body, can input .classname/#idname/tagname'
      }
    },
  }
}
