import useLoginStore from './modules/login'
import useUserStore from './modules/user'
import useFolderStore from './modules/folder'
import useThemeStore from './modules/theme'

const useStore = () => ({
  login: useLoginStore(),
  user: useUserStore(),
  folder: useFolderStore(),
  theme: useThemeStore(),
})

export default useStore
