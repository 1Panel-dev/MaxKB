import useCommonStore from './modules/common'
import useLoginStore from './modules/login'
import useUserStore from './modules/user'
import useFolderStore from './modules/folder'
import useThemeStore from './modules/theme'
import useKnowledgeStore from './modules/knowledge'
import useModelStore from './modules/model'
import usePromptStore from './modules/prompt'
import useApplicationStore from './modules/application'
import useChatUserStore from './modules/chat-user'
import useToolStore from './modules/tool'
const useStore = () => ({
  common: useCommonStore(),
  login: useLoginStore(),
  user: useUserStore(),
  folder: useFolderStore(),
  theme: useThemeStore(),
  knowledge: useKnowledgeStore(),
  model: useModelStore(),
  prompt: usePromptStore(),
  application: useApplicationStore(),
  chatUser: useChatUserStore(),
  tool: useToolStore(),
})

export default useStore
