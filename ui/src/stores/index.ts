import useCommonStore from './modules/common'
import useLoginStore from './modules/login'
import useUserStore from './modules/user'
import useFolderStore from './modules/folder'
import useThemeStore from './modules/theme'
import useKnowledgeStore from './modules/knowledge'

const useStore = () => ({
  common: useCommonStore(),
  login: useLoginStore(),
  user: useUserStore(),
  folder: useFolderStore(),
  theme: useThemeStore(),
  knowledge: useKnowledgeStore(),
})

export default useStore
