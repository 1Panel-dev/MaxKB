import useCommonStore from './modules/common'
import useLoginStore from './modules/login'
import useUserStore from './modules/user'
import useFolderStore from './modules/folder'
import useThemeStore from './modules/theme'
import useKnowledgeStore from './modules/knowledge'
import useModelStore from './modules/model'
import usePromptStore from './modules/prompt'
import useProblemStore from './modules/problem'
import useParagraphStore from './modules/paragraph'
import useDocumentStore from './modules/document'
import useApplicationStore from './modules/application'
import useChatLogStore from './modules/chat-log'
const useStore = () => ({
  common: useCommonStore(),
  login: useLoginStore(),
  user: useUserStore(),
  folder: useFolderStore(),
  theme: useThemeStore(),
  knowledge: useKnowledgeStore(),
  model: useModelStore(),
  prompt: usePromptStore(),
  problem: useProblemStore(),
  paragraph: useParagraphStore(),
  document: useDocumentStore(),
  application: useApplicationStore(),
  chatLog: useChatLogStore(),
})

export default useStore
