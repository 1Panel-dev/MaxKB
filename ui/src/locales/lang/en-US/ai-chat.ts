export default {
  noHistory: 'No Chat History',
  createChat: 'New Chat',
  history: 'Chat History',
  only20history: 'Showing only the last 20 chats',
  question_count: 'Questions',
  exportRecords: 'Export Chat History',
  chatId: 'Chat ID',
  userInput: 'User Input',
  quote: 'Quote',
  download: 'Click to Download',
  passwordValidator: {
    title: 'Enter Password to Access',
    errorMessage1: 'Password cannot be empty',
    errorMessage2: 'Incorrect password'
  },
  operation: {
    play: 'Play',
    pause: 'Pause',
    regeneration: 'Regenerate Response',
    like: 'Like',
    cancelLike: 'Unlike',
    oppose: 'Dislike',
    cancelOppose: 'Undo Dislike',
    continue: 'Continue',
    stopChat: 'Stop Response'
  },
  tip: {
    error500Message: 'Sorry, the service is currently under maintenance. Please try again later!',
    errorIdentifyMessage: 'Unable to verify user identity',
    errorLimitMessage: 'Sorry, you have reached the maximum number of questions. Please try again tomorrow!',
    answerMessage: 'Sorry, no relevant content found. Please rephrase your question or provide more details.',
    stopAnswer: 'Response Stopped',
    answerLoading: 'Generating Response...',
    recorderTip: `<p>This feature requires microphone access. Browsers block recording on insecure pages. Solutions:<br/>
1. Enable HTTPS;<br/>
2. If HTTPS is not available, adjust browser security settings. For Chrome:<br/>
(1) Enter chrome://flags/#unsafely-treat-insecure-origin-as-secure in the address bar;<br/>
(2) Add your HTTP site, e.g., http://127.0.0.1:8080.</p>`,
    recorderError: 'Recording Failed',
    confirm: 'Got it',
    requiredMessage: 'Please fill in all required fields',
    inputParamMessage1: 'Please specify a parameter in the URL',
    inputParamMessage2: 'value',
    prologueMessage: 'Sorry, the service is currently under maintenance. Please try again later!'
  },
  inputPlaceholder: {
    speaking: 'Speaking...',
    recorderLoading: 'Transcribing...',
    default: 'Type your question, Ctrl+Enter for a new line'
  },
  uploadFile: {
    label: 'Upload File',
    most: 'Maximum',
    limit: 'files allowed, each up to',
    fileType: 'File Type',
    tipMessage: 'Please select allowed file types in the upload settings',
    limitMessage1: 'You can upload up to',
    limitMessage2: 'files',
    sizeLimit: 'Each file must not exceed',
    imageMessage: 'Please process the image content',
    errorMessage: 'Upload Failed'
  },
  executionDetails: {
    title: 'Execution Details',
    paramOutputTooltip: 'Each document supports previewing up to 500 characters',
    audioFile: 'Audio File',
    searchContent: 'Search Query',
    searchResult: 'Search Results',
    conditionResult: 'Condition Evaluation',
    currentChat: 'Current Chat',
    answer: 'AI Response',
    replyContent: 'Reply Content',
    textContent: 'Text Content',
    input: 'Input',
    output: 'Output',
    rerankerContent: 'Re-ranked Content',
    rerankerResult: 'Re-ranking Results',
    paragraph: 'Segment',
    noSubmit: 'No submission from user',
    errMessage: 'Error Log'
  },
  KnowledgeSource: {
    title: 'Knowledge Source',
    referenceParagraph: 'Cited Segment',
    consume: 'Tokens',
    consumeTime: 'Runtime'
  },
  paragraphSource: {
    title: 'Knowledge Quote',
    question: 'User Question',
    optimizationQuestion: 'Optimized Question'
  }
}
