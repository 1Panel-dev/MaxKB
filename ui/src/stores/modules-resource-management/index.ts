import useCommonStore from './common'
import useLoginStore from './login'
import useFolderStore from './folder'
import useKnowledgeStore from './knowledge'
import useModelStore from './model'
import usePromptStore from './prompt'
import useProblemStore from './problem'
import useParagraphStore from './paragraph'
import useDocumentStore from './document'

const useStore = () => ({
  common: useCommonStore(),
  login: useLoginStore(),
  folder: useFolderStore(),
  knowledge: useKnowledgeStore(),
  model: useModelStore(),
  prompt: usePromptStore(),
  problem: useProblemStore(),
  paragraph: useParagraphStore(),
  document: useDocumentStore(),
})

export default useStore
