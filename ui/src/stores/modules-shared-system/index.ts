import useCommonStore from './common'
import useLoginStore from './login'
import useUserStore from './user'
import useFolderStore from './folder'
import useThemeStore from './theme'
import useKnowledgeStore from './knowledge'
import useModelStore from './model'
import usePromptStore from './prompt'
import useProblemStore from './problem'
import useParagraphStore from './paragraph'
import useDocumentStore from './document'

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
})

export default useStore
