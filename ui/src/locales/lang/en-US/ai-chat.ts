export default {
  noHistory: 'No History',
  createChat: 'New Chat',
  history: 'Chat History',
  only20history: 'Only showing the last 20 chats',
  question_count: 'Questions',
  exportRecords: 'Export Chat Records',
  chatId: 'Chat ID',
  userInput: 'User Input',
  quote: 'Quote',
  download: 'Click to Download File',
  passwordValidator: {
    title: 'Enter password to open the link',
    errorMessage1: 'Password cannot be empty',
    errorMessage2: 'Incorrect password'
  },
  operation: {
    play: 'Click to Play',
    pause: 'Stop',
    regeneration: 'Re-answer',
    like: 'Agree',
    cancelLike: 'Cancel Agree',
    oppose: 'Disagree',
    cancelOppose: 'Cancel Disagree',
    continue: 'Continue',
    stopChat: 'Stop Output'
  },
  tip: {
    error500Message: 'Sorry, the service is currently under maintenance. Please try again later!',
    errorIdentifyMessage: 'Unable to identify user',
    errorLimitMessage:
      'Sorry, you have reached the maximum number of questions. Please try again tomorrow!',
    answerMessage:
      'Sorry, no relevant content was found. Please rephrase your question or provide more information.',
    stopAnswer: 'Output stopped',
    answerLoading: 'Thinking',
    recorderTip: `<p>This feature requires the use of a microphone. Browsers prohibit recording on insecure pages. Solutions are as follows:<br/>
1. Enable HTTPS to resolve;<br/>
2. If there is no HTTPS configuration, modify the browser security settings. Chrome settings as follows:<br/>
(1) Enter chrome://flags/#unsafely-treat-insecure-origin-as-secure in the address bar;<br/>
(2) Add the HTTP site to the text box, e.g., http://127.0.0.1:8080.</p>`,
    recorderError: 'Recording failed',
    confirm: 'I understand',
    requiredMessage: 'Please fill in all required fields',
    inputParamMessage1: 'Please enter parameters in the URL',
    inputParamMessage2: 'value',
    prologueMessage: 'Sorry, the service is currently under maintenance. Please try again later!'
  },
  inputPlaceholder: {
    speaking: 'Speaking',
    recorderLoading: 'Transcribing',
    default: 'Enter your question, Ctrl+Enter for new line, Enter to send'
  },
  uploadFile: {
    label: 'Upload File',
    most: 'Up to',
    limit: 'files, each file limited to',
    fileType: 'File Type',
    tipMessage: 'Please select file types in the file upload configuration',
    limitMessage1: 'Up to',
    limitMessage2: 'files',
    sizeLimit: 'Each file size cannot exceed',
    imageMessage: 'Please parse the image content',
    errorMessage: 'Upload failed'
  },
  executionDetails: {
    title: 'Execution Details',
    paramInput: 'Parameter Input',
    paramOutput: 'Parameter Output',
    paramOutputTooltip: 'Each document supports preview of up to 500 words',
    audioFile: 'Audio File',
    searchContent: 'Search Content',
    searchResult: 'Search Results',
    conditionResult: 'Condition Result',
    currentChat: 'Current Chat',
    answer: 'AI Response',
    replyContent: 'Reply Content',
    textContent: 'Text Content',
    input: 'Input',
    output: 'Output',
    rerankerContent: 'Reranked Content',
    rerankerResult: 'Reranked Results',
    paragraph: 'Segment',
    noSubmit: 'User did not submit',
    errMessage: 'Error Log'
  },
  KnowledgeSource: {
    title: 'Knowledge Source',
    referenceParagraph: 'Quote',
    consume: 'Tokens',
    consumeTime: 'Time'
  },
  paragraphSource: {
    title: 'Knowledge Reference',
    question: 'User Question',
    optimizationQuestion: 'Optimized Question'
  }
}
