export default {
  applicationList: {
    title: 'Applications',
    searchBar: {
      placeholder: 'Search by name'
    },
    card: {
      createApplication: 'Create Application',
      overview: 'Overview',
      demo: 'Demo',
      setting: 'Settings',
      delete: {
        tooltip: 'Delete',
        confirmTitle: 'Are you sure you want to delete this application?',
        confirmMessage:
          'Deleting this application will no longer provide its services. Please proceed with caution.',
        confirmButton: 'Delete',
        cancelButton: 'Cancel',
        successMessage: 'Successfully deleted'
      }
    },
    tooltips: {
      demo: 'Demo',
      setting: 'Settings',
      delete: 'Delete'
    }
  },
  applicationForm: {
    title: {
      create: 'Create Application',
      edit: 'Edit Settings',
      info: 'Application Information'
    },
    form: {
      appName: {
        label: 'Application Name',
        placeholder: 'Please enter the application name',
        requiredMessage: 'Application name is required'
      },
      appDescription: {
        label: 'Application Description',
        placeholder:
          'Describe the application scenario and use, e.g.: MaxKB assistant answering user questions about MaxKB product usage'
      },
      aiModel: {
        label: 'AI Model',
        placeholder: 'Please select an AI model',
        unavailable: '(Unavailable)'
      },
      prompt: {
        label: 'Prompt',
        placeholder: 'Please enter prompt',
        tooltip:
          'By adjusting the content of the prompt, you can guide the direction of the large model conversation. This prompt will be fixed at the beginning of the context. Variables used: {data} carries known information from the knowledge base; {question} is the question posed by the user.'
      },
      multipleRoundsDialogue: 'Multiple Rounds Dialogue',
      relatedKnowledgeBase: 'Related Knowledge Base',
      relatedKnowledgeBaseWhere: 'Associated knowledge bases are displayed here',
      prologue: 'Prologue',
      problemOptimization: {
        label: 'Problem Optimization',
        tooltip:
          'Optimize the current question based on historical chat to better match knowledge points.'
      },
      addModel: 'Add Model',
      paramSetting: 'Parameter Settings',
      add: 'Add',
      apptest: 'Debug Preview'
    },
    buttons: {
      confirm: 'Confirm',
      cancel: 'Cancel',
      create: 'Create',
      createSuccess: 'Create Success',
      save: 'Save',
      saveSuccess: 'Save Success'
    },
    dialogues: {
      addDataset: 'Add Related Knowledge Base',
      removeDataset: 'Remove Knowledge Base',
      paramSettings: 'Parameter Settings',
      refresh: 'Refresh',
      selectSearchMode: 'Search Mode',
      vectorSearch: 'Vector Search',
      vectorSearchTooltip:
        'Vector search is a retrieval method based on vector distance calculations, suitable for large data volumes in the knowledge base.',
      fullTextSearch: 'Full-text Search',
      fullTextSearchTooltip:
        'Full-text search is a retrieval method based on text similarity, suitable for small data volumes in the knowledge base.',
      hybridSearch: 'Hybrid Search',
      hybridSearchTooltip:
        'Hybrid search is a retrieval method based on both vector and text similarity, suitable for medium data volumes in the knowledge base.',
      similarityThreshold: 'Similarity Threshold',
      topReferences: 'Top N References',
      maxCharacters: 'Maximum Characters per Reference',
      noReferencesAction: 'When there are no knowledge base references',
      continueQuestioning: 'Continue Questioning AI Model',
      provideAnswer: 'Provide a Specific Answer',
      prompt: 'Prompt',
      promptPlaceholder: 'Please enter a prompt',
      concent: 'Content',
      concentPlaceholder: 'Please enter content',
      designated_answer:
        'Hello, I am MaxKB Assistant. My knowledge base only contains information related to MaxKB products. Please rephrase your question.'
    }
  },
  prompt: {
    defaultPrompt:
      'Known information:\n{data}\nResponse requirements:\n- Please use concise and professional language to answer the user\'s question.\n- If you do not know the answer, reply, "No relevant information was found in the knowledge base; it is recommended to consult technical support or refer to the official documentation for operations."\n- Avoid mentioning that your knowledge is obtained from known information.\n- Ensure the answer is consistent with the information described in the known data.\n- Please use Markdown syntax to optimize the format of the answer.\n- Directly return any images, link addresses, and script languages found in the known information.\n- Please respond in the same language as the question.\nQuestion:\n{question}',
    defaultPrologue:
      'Hello, I am MaxKB Assistant. You can ask me questions about using MaxKB.\n- What are the main features of MaxKB?\n- Which large language models does MaxKB support?\n- What document types does MaxKB support?'
  }
}
